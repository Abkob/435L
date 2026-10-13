"""Identity service: password hashing, expiring opaque sessions and role control."""
from datetime import datetime, timedelta, timezone
import re
import secrets
from flask import g, request
from werkzeug.security import check_password_hash, generate_password_hash
from .core import *

def validate_profile(data, partial=False):
    for key in ('full_name', 'department'):
        text_field(data, key, optional=partial)
    if 'email' in data or not partial:
        text_field(data, 'email', 254)
        data['email'] = data['email'].lower()
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', data['email']):
            raise ApiError('Invalid email format')

def validate_password(password):
    if not isinstance(password, str) or not 12 <= len(password) <= 128 or not re.search('[A-Z]', password) or not re.search('[a-z]', password) or not re.search('[0-9]', password) or not re.search(r'[^\w\s]', password):
        raise ApiError('Password must be 12 to 128 characters and include uppercase, lowercase, digit and symbol')

def register(app, ctx):
    repo = Repository('users')
    route = lambda path, **kw: app.route(PREFIX + path, **kw)

    @route('/users/register', methods=['POST'])
    def create_user():
        data = body(('full_name','username','email','password','department','role','account_status'), ('full_name','username','email','password','department','role'))
        validate_profile(data)
        text_field(data, 'username', 40)
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{2,39}', data['username']):
            raise ApiError('Username must start with a letter and contain 3 to 40 letters, digits, dots, underscores or hyphens')
        enum_field(data, 'role', ROLES)
        validate_password(data['password'])
        data.setdefault('account_status', 'Active')
        enum_field(data, 'account_status', ('Active','Inactive','Suspended'))
        actor = None
        if request.headers.get('Authorization'):
            g.user = authenticate(ctx)
            actor = g.user['id']
            if g.user['role'] not in (ADMIN, EMPLOYEE):
                raise ApiError('Your role cannot register users', 403)
        if (not getattr(g, 'user', None) or g.user['role'] != ADMIN) and (data['role'] != EMPLOYEE or data['account_status'] != 'Active'):
            raise ApiError('Self-registration can only create an active Regular Employee/User', 403)
        data['password_hash'] = generate_password_hash(data.pop('password'), method='scrypt')
        data['created_at'] = now()
        with ctx.db.transaction() as conn:
            user = repo.insert(conn, data)
            ctx.events.audit(conn, 'user.created', f'Created account {user["username"]}', actor or user['id'])
            ctx.events.notify(conn, user['id'], 'Account created', 'Your account is ready.', 'System Notification', 'Low')
        return ok(public_user(user), 201)

    @route('/users/login', methods=['POST'])
    def login():
        data = body(('login','password'), ('login','password'))
        text_field(data, 'login', 254)
        text_field(data, 'password', 128)
        since = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
        address = request.remote_addr or 'unknown'
        normalized = data['login'].lower()
        with ctx.db.transaction() as conn:
            recent = conn.execute('SELECT COUNT(*) FROM login_attempts WHERE login=? AND address=? AND created_at>?', (normalized, address, since)).fetchone()[0]
            if recent >= 5:
                raise ApiError('Too many unsuccessful attempts; try again after 15 minutes', 429)
            row = conn.execute('SELECT * FROM users WHERE (username=? OR email=?) AND deleted_at IS NULL', (normalized, normalized)).fetchone()
            user = dict(row) if row else None
        valid = bool(user and check_password_hash(user['password_hash'], data['password']) and user['account_status'] == 'Active')
        with ctx.db.transaction() as conn:
            if not valid:
                conn.execute('INSERT INTO login_attempts(login,address,created_at) VALUES(?,?,?)', (normalized, address, now()))
                ctx.events.audit(conn, 'login.failed', 'Unsuccessful authentication', user['id'] if user else None, 'Warning')
            else:
                # Re-read under the write lock to prevent a suspension racing login.
                fresh = repo.get(conn, user['id'])
                if fresh['account_status'] != 'Active':
                    raise ApiError('Invalid credentials or inactive account', 401)
                token = secrets.token_urlsafe(36)
                expires = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
                conn.execute('INSERT INTO sessions(token_hash,user_id,expires_at,created_at) VALUES(?,?,?,?)', (token_digest(token), user['id'], expires, now()))
                user = repo.update(conn, user['id'], {'last_login_at': now()})
                conn.execute('DELETE FROM login_attempts WHERE login=? AND address=?', (normalized, address))
                ctx.events.audit(conn, 'login.succeeded', 'User authenticated', user['id'])
        if not valid:
            g.auth_event_recorded = True
            raise ApiError('Invalid credentials or inactive account', 401)
        return ok(dict(token=token, token_type='Bearer', expires_at=expires, user=public_user(user)))

    @route('/users/logout', methods=['POST'])
    @protected(ctx, *ROLES)
    def logout():
        with ctx.db.transaction() as conn:
            conn.execute('DELETE FROM sessions WHERE token_hash=?', (token_digest(request.headers['Authorization'][7:]),))
            ctx.record(conn, 'user.logout', g.user['id'])
        return ok({'message':'Session revoked'})

    @route('/users', methods=['GET'])
    @protected(ctx, ADMIN, AUDITOR)
    def users():
        with ctx.db.transaction() as conn:
            rows = repo.search(conn, {}, {}, 'deleted_at IS NULL')
        return ok([public_user(r) for r in rows])

    @route('/users/<username>', methods=['GET'])
    @protected(ctx, ADMIN, AUDITOR, EMPLOYEE)
    def user_by_username(username):
        if g.user['role'] == EMPLOYEE and username.lower() != g.user['username'].lower():
            raise ApiError('You can only access your own profile', 403)
        with ctx.db.transaction() as conn:
            row = conn.execute('SELECT * FROM users WHERE username=? AND deleted_at IS NULL', (username,)).fetchone()
            if row is None:
                raise ApiError('User not found', 404)
        return ok(public_user(dict(row)))

    @route('/users/<int:user_id>', methods=['PUT'])
    @protected(ctx, ADMIN, EMPLOYEE)
    def update_user(user_id):
        if g.user['role'] == EMPLOYEE and user_id != g.user['id']:
            raise ApiError('You can only update your own profile', 403)
        data = body(('full_name','email','department'))
        validate_profile(data, True)
        with ctx.db.transaction() as conn:
            user = repo.update(conn, user_id, data)
            ctx.record(conn, 'user.updated', user_id)
        return ok(public_user(user))

    def preserve_admin(conn, user, role=None, status=None):
        if user['role'] == ADMIN and (role not in (None, ADMIN) or status not in (None, 'Active')):
            count = conn.execute('SELECT COUNT(*) FROM users WHERE role=? AND account_status=? AND deleted_at IS NULL', (ADMIN,'Active')).fetchone()[0]
            if count <= 1:
                raise ApiError('Cannot remove the last active administrator', 409)

    @route('/users/<int:user_id>', methods=['DELETE'])
    @protected(ctx, ADMIN)
    def delete_user(user_id):
        if user_id == g.user['id']:
            raise ApiError('Cannot delete your own administrator account', 409)
        with ctx.db.transaction() as conn:
            user = repo.get(conn, user_id)
            preserve_admin(conn, user, status='Inactive')
            # Tombstone preserves ownership and immutable historic audit records.
            conn.execute('UPDATE users SET account_status=?,deleted_at=? WHERE id=?', ('Inactive',now(),user_id))
            conn.execute('DELETE FROM sessions WHERE user_id=?', (user_id,))
            ctx.record(conn, 'user.deleted', user_id)
        return ok({'id':user_id, 'deleted':True})

    @route('/users/<int:user_id>/role', methods=['PUT','DELETE'])
    @protected(ctx, ADMIN)
    def role(user_id):
        data = {'role':EMPLOYEE} if request.method == 'DELETE' else body(('role',), ('role',))
        enum_field(data, 'role', ROLES)
        with ctx.db.transaction() as conn:
            user = repo.get(conn, user_id)
            preserve_admin(conn, user, role=data['role'])
            user = repo.update(conn, user_id, data)
            conn.execute('DELETE FROM sessions WHERE user_id=?', (user_id,))
            ctx.record(conn, 'role.changed', user_id)
        return ok(public_user(user))

    @route('/users/<int:user_id>/status', methods=['PUT'])
    @protected(ctx, ADMIN)
    def account_status(user_id):
        data = body(('account_status',), ('account_status',))
        enum_field(data, 'account_status', ('Active','Inactive','Suspended'))
        with ctx.db.transaction() as conn:
            user = repo.get(conn, user_id)
            preserve_admin(conn, user, status=data['account_status'])
            user = repo.update(conn, user_id, data)
            conn.execute('DELETE FROM sessions WHERE user_id=?', (user_id,))
            ctx.record(conn, 'user.status_changed', user_id)
        return ok(public_user(user))

    @route('/users/permissions', methods=['GET'])
    @protected(ctx, ADMIN, AUDITOR)
    def permissions():
        return ok({ADMIN:'Platform administration and all services', ANALYST:'Assigned investigations, related assets, threat and vulnerability review, own notifications and playbook actions', EMPLOYEE:'Own profile, incident reporting and own notifications', AUDITOR:'Read-only inspection and report generation'})

    @route('/internal/introspect', methods=['GET'])
    @internal(ctx)
    def introspect():
        return ok(authenticate(ctx))

    @route('/internal/users/<int:user_id>', methods=['GET'])
    @internal(ctx)
    def internal_user(user_id):
        with ctx.db.transaction() as conn:
            user = repo.get(conn, user_id)
        return ok(public_user(user))
