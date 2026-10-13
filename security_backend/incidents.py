"""Incident lifecycle with server-derived reporter and assignment checks."""
from flask import g, request
from .core import *

FLOW = Lifecycle(('Open','Under Investigation','Mitigated','Resolved','Closed'))

def register(app, ctx):
    repo = Repository('incidents')
    route = lambda path, **kw: app.route(PREFIX + path, **kw)

    def access(incident):
        role = g.user['role']
        if role == EMPLOYEE and incident['reporter_id'] != g.user['id']:
            raise ApiError('You can only view incidents you reported',403)
        if role == ANALYST and incident['assigned_analyst_id'] != g.user['id']:
            raise ApiError('Incident is not assigned to you',403)

    @route('/incidents', methods=['POST'])
    @protected(ctx, ADMIN, EMPLOYEE)
    def create():
        data = body(('title','description','category','severity','asset_id','reporter_id'),('title','description','category','severity','asset_id'))
        for key in ('title','description','category'):
            text_field(data,key,4000 if key=='description' else 200)
        enum_field(data,'severity',SEVERITIES)
        integer_field(data,'asset_id',nullable=True)
        if data['asset_id'] is not None:
            ctx.asset(data['asset_id'])
        integer_field(data,'reporter_id',optional=True)
        if 'reporter_id' in data and data['reporter_id'] != g.user['id']:
            raise ApiError('Reporter must match the authenticated user',403)
        data.update(reporter_id=g.user['id'],status='Open',created_at=now())
        with ctx.db.transaction() as conn:
            row = repo.insert(conn,data)
            ctx.record(conn,'incident.created',row['id'])
            ctx.events.notify(conn,g.user['id'],'Incident reported',f'Incident {row["id"]} is Open.','Security Alert',row['severity'])
        return ok(row,201)

    @route('/incidents', methods=['GET'])
    @protected(ctx,*ROLES)
    def all_incidents():
        extra, args = '', ()
        if g.user['role'] == ANALYST:
            extra,args = 'assigned_analyst_id=?',(g.user['id'],)
        elif g.user['role'] == EMPLOYEE:
            extra,args = 'reporter_id=?',(g.user['id'],)
        with ctx.db.transaction() as conn:
            rows = repo.search(conn,request.args,{k:(k,False) for k in ('severity','status','asset_id')},extra,args)
        return ok(rows)

    @route('/incidents/<int:incident_id>', methods=['GET'])
    @protected(ctx,*ROLES)
    def one(incident_id):
        with ctx.db.transaction() as conn:
            row = repo.get(conn,incident_id)
            access(row)
            # Employees can track their reports; confidential investigation notes are staff-only.
            if g.user['role'] != EMPLOYEE:
                row['notes'] = [dict(r) for r in conn.execute('SELECT * FROM investigation_notes WHERE incident_id=? ORDER BY id',(incident_id,))]
        return ok(row)

    @route('/incidents/<int:incident_id>/assign', methods=['PUT'])
    @protected(ctx,ADMIN)
    def assign(incident_id):
        data = body(('analyst_id',),('analyst_id',))
        integer_field(data,'analyst_id')
        analyst = ctx.user(data['analyst_id'])
        if analyst['role'] != ANALYST or analyst['account_status'] != 'Active':
            raise ApiError('Assigned user must be an active Security Analyst')
        with ctx.db.transaction() as conn:
            row = repo.get(conn,incident_id)
            if row['status'] == 'Closed':
                raise ApiError('Cannot reassign a closed incident',409)
            row = repo.update(conn,incident_id,{'assigned_analyst_id':data['analyst_id']})
            ctx.record(conn,'incident.assigned',incident_id)
            ctx.events.notify(conn,data['analyst_id'],'Incident assigned',f'Investigate incident {incident_id}: {row["title"]}','Incident Assignment',row['severity'])
        return ok(row)

    @route('/incidents/<int:incident_id>/status', methods=['PUT'])
    @protected(ctx,ADMIN,ANALYST)
    def status(incident_id):
        data = body(('status',),('status',))
        with ctx.db.transaction() as conn:
            row = repo.get(conn,incident_id)
            access(row)
            FLOW.validate(row['status'],data['status'])
            if not row['assigned_analyst_id']:
                raise ApiError('Assign an analyst before beginning investigation',409)
            if data['status']=='Resolved' and row['status']!='Resolved':
                data['resolution_date']=now()
            row = repo.update(conn,incident_id,data)
            ctx.record(conn,'incident.status_changed',incident_id)
        return ok(row)

    @route('/incidents/<int:incident_id>/notes', methods=['POST'])
    @protected(ctx,ADMIN,ANALYST)
    def notes(incident_id):
        data = body(('content',),('content',))
        text_field(data,'content',4000)
        with ctx.db.transaction() as conn:
            row = repo.get(conn,incident_id)
            access(row)
            if row['status']=='Closed':
                raise ApiError('Closed incidents cannot receive new notes',409)
            note = Repository('investigation_notes').insert(conn,dict(incident_id=incident_id,analyst_id=g.user['id'],content=data['content'],created_at=now()))
            ctx.record(conn,'incident.note_added',incident_id)
        return ok(note,201)
