"""Asset ownership, scoped analyst access and retained change history."""
from flask import g, request
from .core import *

ASSET_TYPES = ('Server','Workstation','Database','Application','Network Device','Cloud Resource')

def register(app, ctx):
    repo = Repository('assets')
    route = lambda path, **kw: app.route(PREFIX + path, **kw)
    fields = ('name','asset_type','ip_address','operating_system','department','owner_id','location','criticality','status')
    filters = {k:(k,k in ('name','department')) for k in ('name','asset_type','ip_address','department','criticality')}

    def validate(data, partial=False):
        for key in ('name','department'):
            text_field(data, key, optional=partial)
        for key in ('operating_system','location'):
            if key in data and (not isinstance(data[key], str) or len(data[key]) > 200):
                raise ApiError(f'{key} must be a string up to 200 characters')
        for key, choices in (('asset_type',ASSET_TYPES),('criticality',SEVERITIES),('status',('Active','Inactive','Under Maintenance'))):
            enum_field(data,key,choices,partial)
        integer_field(data,'owner_id',partial)
        if 'ip_address' in data:
            ip_field(data,'ip_address')
        if 'owner_id' in data:
            owner = ctx.user(data['owner_id'])
            if owner['account_status'] != 'Active':
                raise ApiError('Owner must be an active user')

    def history(conn, before, after, operation):
        asset_id = (before or after)['id']
        conn.execute('INSERT INTO asset_history(asset_id,actor_id,operation,before_json,after_json,created_at) VALUES(?,?,?,?,?,?)',
                     (asset_id,g.user['id'],operation,json.dumps(before) if before else None,json.dumps(after) if after else None,now()))
        ctx.record(conn, 'asset.'+operation, asset_id)

    def related(conn, asset_id):
        if g.user['role'] == ANALYST and not conn.execute('SELECT 1 FROM incidents WHERE asset_id=? AND assigned_analyst_id=?', (asset_id,g.user['id'])).fetchone():
            raise ApiError('Asset is not related to your assigned incidents',403)

    @route('/assets', methods=['POST'])
    @protected(ctx, ADMIN)
    def create():
        data = body(fields, ('name','asset_type','ip_address','department','owner_id','criticality'))
        data.setdefault('status','Active')
        validate(data)
        data['created_at'] = now()
        with ctx.db.transaction() as conn:
            asset = repo.insert(conn,data)
            history(conn,None,asset,'created')
        return ok(asset,201)

    @route('/assets/<int:asset_id>', methods=['PUT'])
    @protected(ctx, ADMIN)
    def update(asset_id):
        data = body(fields)
        validate(data,True)
        with ctx.db.transaction() as conn:
            before = repo.get(conn,asset_id)
            after = repo.update(conn,asset_id,data)
            history(conn,before,after,'updated')
        return ok(after)

    @route('/assets/<int:asset_id>', methods=['DELETE'])
    @protected(ctx, ADMIN)
    def delete(asset_id):
        with ctx.db.transaction() as conn:
            before = repo.get(conn,asset_id)
            conn.execute('DELETE FROM assets WHERE id=?',(asset_id,))
            history(conn,before,None,'deleted')
        return ok({'id':asset_id,'deleted':True})

    @route('/assets', methods=['GET'])
    @protected(ctx, ADMIN, AUDITOR)
    def all_assets():
        with ctx.db.transaction() as conn:
            rows = repo.search(conn,request.args,filters)
        return ok(rows)

    @route('/assets/search', methods=['GET'])
    @protected(ctx, ADMIN, AUDITOR, ANALYST)
    def search():
        extra = 'id IN (SELECT asset_id FROM incidents WHERE assigned_analyst_id=?)' if g.user['role']==ANALYST else ''
        args = (g.user['id'],) if extra else ()
        with ctx.db.transaction() as conn:
            rows = repo.search(conn,request.args,filters,extra,args)
        return ok(rows)

    @route('/assets/<int:asset_id>', methods=['GET'])
    @protected(ctx, ADMIN, AUDITOR, ANALYST)
    def one(asset_id):
        with ctx.db.transaction() as conn:
            row = repo.get(conn,asset_id)
            related(conn,asset_id)
            row['incident_ids'] = [r[0] for r in conn.execute('SELECT id FROM incidents WHERE asset_id=?',(asset_id,))]
            row['vulnerability_ids'] = [r[0] for r in conn.execute('SELECT id FROM vulnerabilities WHERE asset_id=?',(asset_id,))]
        return ok(row)

    @route('/assets/<int:asset_id>/history', methods=['GET'])
    @protected(ctx, ADMIN, AUDITOR)
    def asset_history(asset_id):
        with ctx.db.transaction() as conn:
            rows = [dict(r) for r in conn.execute('SELECT * FROM asset_history WHERE asset_id=? ORDER BY id',(asset_id,))]
        if not rows:
            raise ApiError('Asset history not found',404)
        return ok(rows)

    @route('/internal/assets/<int:asset_id>', methods=['GET'])
    @internal(ctx)
    def internal_asset(asset_id):
        with ctx.db.transaction() as conn:
            row = repo.get(conn,asset_id)
        return ok(row)
