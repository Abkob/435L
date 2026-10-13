"""Shared persistence, validation, authentication and durable service messaging.

Every SQL value is bound. Identifiers come only from programmer-owned constants.
An outbox is committed with each business write, then delivered over HTTP.
"""
from contextlib import contextmanager, closing
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
import hashlib
import hmac
import ipaddress
import json
import os
import re
import sqlite3
import uuid

import requests
from flask import g, jsonify, request

PREFIX = '/Abdulrahman-Kobeissi'
ADMIN, ANALYST, EMPLOYEE, AUDITOR = ('Security Administrator', 'Security Analyst', 'Regular Employee/User', 'Auditor')
ROLES = (ADMIN, ANALYST, EMPLOYEE, AUDITOR)
SEVERITIES = ('Low', 'Medium', 'High', 'Critical')
SERVICES = dict(zip(('users', 'assets', 'incidents', 'threats', 'logs', 'reports', 'vulnerabilities', 'notifications', 'playbooks'), range(5101, 5110)))

def now():
    """UTC ISO timestamp with microseconds for deterministic ordering."""
    return datetime.now(timezone.utc).isoformat()

class ApiError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message, self.status = message, status

@dataclass(frozen=True)
class Settings:
    database: str
    internal_key: str
    port_offset: int = 0

    @classmethod
    def from_env(cls):
        key = os.environ.get('SERVICE_KEY', '')
        if len(key) < 32:
            raise RuntimeError('SERVICE_KEY must contain at least 32 characters; use run.py for automatic local configuration')
        return cls(os.environ.get('SECURITY_DB', 'runtime/security.db'), key, int(os.environ.get('PORT_OFFSET', '0')))

    def url(self, service, path):
        return f'http://127.0.0.1:{SERVICES[service] + self.port_offset}{PREFIX}{path}'

class Database:
    """Encapsulates a connection per transaction and enables foreign keys."""
    def __init__(self, path):
        self.path = str(path)

    @contextmanager
    def transaction(self):
        conn = sqlite3.connect(self.path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('PRAGMA busy_timeout=15000')
        try:
            # Serialize read-modify-write decisions as well as the writes themselves.
            conn.execute('BEGIN IMMEDIATE')
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self):
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute('PRAGMA journal_mode=WAL')
            conn.executescript(Path(__file__).with_name('schema.sql').read_text())

class Repository:
    """Reusable data access; subclasses and services own the business rules."""
    def __init__(self, table):
        self.table = table

    def get(self, conn, record_id):
        row = conn.execute(f'SELECT * FROM {self.table} WHERE id=?', (record_id,)).fetchone()
        if row is None or ('deleted_at' in row.keys() and row['deleted_at']):
            raise ApiError(f'{self.table} record not found', 404)
        return dict(row)

    def insert(self, conn, values):
        keys = list(values)
        cur = conn.execute(f"INSERT INTO {self.table} ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})", tuple(values.values()))
        return self.get(conn, cur.lastrowid)

    def update(self, conn, record_id, values):
        self.get(conn, record_id)
        if values:
            conn.execute(f"UPDATE {self.table} SET {','.join(k+'=?' for k in values)} WHERE id=?", (*values.values(), record_id))
        return self.get(conn, record_id)

    def search(self, conn, filters, allowed, extra='', args=()):
        unknown = set(filters) - set(allowed)
        if unknown:
            raise ApiError('Unsupported filters: ' + ', '.join(sorted(unknown)))
        clauses, values = [], list(args)
        if extra:
            clauses.append(extra)
        for key, value in filters.items():
            column, partial = allowed[key]
            if partial:
                value = value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
                clauses.append(f"{column} LIKE ? ESCAPE '\\'")
                values.append('%' + value + '%')
            else:
                clauses.append(f'{column}=?')
                values.append(value)
        query = f'SELECT * FROM {self.table}' + (' WHERE ' + ' AND '.join(clauses) if clauses else '') + ' ORDER BY id'
        return [dict(row) for row in conn.execute(query, values)]

@dataclass(frozen=True)
class Lifecycle:
    """One reusable state machine for incident, vulnerability and action flows."""
    states: tuple

    def validate(self, current, target):
        if target not in self.states:
            raise ApiError('Invalid status')
        if current == target:
            return
        if self.states.index(target) != self.states.index(current) + 1:
            raise ApiError(f'Invalid transition from {current} to {target}', 409)

class ServiceClient:
    """Explicit timeout and visible failures for service-to-service HTTP calls."""
    def __init__(self, settings):
        self.settings = settings

    def call(self, service, path, method='GET', payload=None, bearer=None):
        headers = {'X-Service-Key': self.settings.internal_key}
        if bearer:
            headers['Authorization'] = bearer
        try:
            response = requests.request(method, self.settings.url(service, path), json=payload, headers=headers, timeout=4)
        except requests.RequestException as exc:
            raise ApiError(f'{service} service unavailable', 503) from exc
        try:
            body = response.json()
        except ValueError as exc:
            raise ApiError(f'{service} returned an invalid response', 502) from exc
        if not response.ok:
            raise ApiError(body.get('message', f'{service} request failed'), response.status_code)
        return body['data']

class EventBus:
    """At-least-once HTTP delivery with event IDs for receiver deduplication."""
    def __init__(self, db, client, service):
        self.db, self.client, self.service = db, client, service

    def queue(self, conn, target, payload):
        event_id = str(uuid.uuid4())
        payload = dict(payload, event_id=event_id, created_at=now())
        conn.execute('INSERT INTO outbox(id,source,target,payload,created_at) VALUES(?,?,?,?,?)',
                     (event_id, self.service, target, json.dumps(payload), now()))

    def audit(self, conn, action, description, user_id=None, severity='Information'):
        self.queue(conn, 'logs', dict(user_id=user_id, action=action, description=description, severity=severity, related_service=self.service))

    def notify(self, conn, user_id, title, message, notification_type, severity='Medium'):
        self.queue(conn, 'notifications', dict(user_id=user_id, title=title, message=message, notification_type=notification_type, severity=severity))

    def flush(self):
        with self.db.transaction() as conn:
            rows = [dict(r) for r in conn.execute('SELECT * FROM outbox WHERE source=? AND delivered_at IS NULL ORDER BY created_at LIMIT 50', (self.service,))]
        for row in rows:
            error = None
            try:
                self.client.call(row['target'], '/internal/events', 'POST', json.loads(row['payload']))
            except ApiError as exc:
                error = exc.message
            with self.db.transaction() as conn:
                conn.execute('UPDATE outbox SET attempts=attempts+1,last_error=?,delivered_at=? WHERE id=?', (error, None if error else now(), row['id']))

def body(allowed, required=()):
    if not request.is_json:
        raise ApiError('Content-Type must be application/json', 415)
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        raise ApiError('A nonempty JSON object is required')
    if set(data) - set(allowed):
        raise ApiError('Unknown or read-only fields: ' + ', '.join(sorted(set(data) - set(allowed))))
    for field in required:
        if field not in data:
            raise ApiError(f'{field} is required')
    return data

def text_field(data, key, maximum=200, optional=False):
    if key not in data and optional:
        return
    value = data.get(key)
    if not isinstance(value, str) or not value.strip() or len(value) > maximum or any(ord(c) < 32 and c not in '\n\t' for c in value):
        raise ApiError(f'{key} must be a nonempty string of at most {maximum} characters')
    data[key] = value.strip()

def enum_field(data, key, choices, optional=False):
    if key not in data and optional:
        return
    if data.get(key) not in choices:
        raise ApiError(f'{key} must be one of: ' + ', '.join(choices))

def integer_field(data, key, optional=False, nullable=False):
    if key not in data and optional:
        return
    value = data.get(key)
    if value is None and nullable:
        return
    if type(value) is not int or value <= 0:
        raise ApiError(f'{key} must be a positive integer')

def ip_field(data, key):
    try:
        data[key] = str(ipaddress.ip_address(data.get(key)))
    except (ValueError, TypeError):
        raise ApiError(f'{key} must be a valid IP address')

def public_user(user):
    return {k: v for k, v in user.items() if k not in ('password_hash', 'deleted_at')}

def ok(data, code=200):
    return jsonify(status='success', data=data), code

def token_digest(token):
    return hashlib.sha256(token.encode()).hexdigest()

def authenticate(ctx):
    bearer = request.headers.get('Authorization', '')
    if not bearer.startswith('Bearer ') or len(bearer) < 20:
        raise ApiError('A valid bearer token is required', 401)
    if ctx.service == 'users':
        with ctx.db.transaction() as conn:
            row = conn.execute('SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires_at>? AND u.account_status=? AND u.deleted_at IS NULL',
                               (token_digest(bearer[7:]), now(), 'Active')).fetchone()
            if row is None:
                raise ApiError('Invalid, expired or revoked session', 401)
            return public_user(dict(row))
    return ctx.client.call('users', '/internal/introspect', bearer=bearer)

def protected(ctx, *roles):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            g.user = authenticate(ctx)
            if g.user['role'] not in roles:
                raise ApiError('Your role does not permit this operation', 403)
            return fn(*args, **kwargs)
        return wrapped
    return decorator

def internal(ctx):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not hmac.compare_digest(request.headers.get('X-Service-Key', ''), ctx.settings.internal_key):
                raise ApiError('Invalid service credentials', 401)
            return fn(*args, **kwargs)
        return wrapped
    return decorator

class Context:
    def __init__(self, service, settings):
        self.service, self.settings = service, settings
        self.db = Database(settings.database)
        self.client = ServiceClient(settings)
        self.events = EventBus(self.db, self.client, service)

    def user(self, user_id):
        return self.client.call('users', f'/internal/users/{user_id}')

    def asset(self, asset_id):
        return self.client.call('assets', f'/internal/assets/{asset_id}')

    def record(self, conn, action, record_id):
        self.events.audit(conn, action, f'{action}: record {record_id}', g.user['id'])
