"""Notifications: per-user scope, read tracking and idempotent internal delivery."""
from flask import g, request
from .core import *

TYPES=('Incident Assignment','Security Alert','System Notification','Threat Alert','Vulnerability Alert')

def register(app,ctx):
    repo=Repository('notifications')
    route=lambda path,**kw:app.route(PREFIX+path,**kw)
    fields=('user_id','title','message','notification_type','severity')

    def validate(data):
        integer_field(data,'user_id')
        text_field(data,'title')
        text_field(data,'message',4000)
        enum_field(data,'notification_type',TYPES)
        enum_field(data,'severity',SEVERITIES)

    def scope(user_id):
        if g.user['role'] not in (ADMIN,AUDITOR) and user_id!=g.user['id']:
            raise ApiError('You can only access your own notifications',403)

    @route('/notifications',methods=['POST'])
    @protected(ctx,ADMIN)
    def create():
        data=body(fields,fields)
        validate(data)
        ctx.user(data['user_id'])
        data.update(status='Unread',created_at=now())
        with ctx.db.transaction() as conn:
            row=repo.insert(conn,data)
            ctx.record(conn,'notification.created',row['id'])
        return ok(row,201)

    @route('/notifications/user/<int:user_id>',methods=['GET'])
    @protected(ctx,*ROLES)
    def for_user(user_id):
        scope(user_id)
        ctx.user(user_id)
        with ctx.db.transaction() as conn:
            rows=repo.search(conn,{}, {},'user_id=?',(user_id,))
        return ok(rows)

    @route('/notifications/<int:record_id>',methods=['GET'])
    @protected(ctx,*ROLES)
    def one(record_id):
        with ctx.db.transaction() as conn:
            row=repo.get(conn,record_id)
            scope(row['user_id'])
        return ok(row)

    @route('/notifications/<int:record_id>/read',methods=['PUT'])
    @protected(ctx,ADMIN,ANALYST,EMPLOYEE)
    def read(record_id):
        with ctx.db.transaction() as conn:
            row=repo.get(conn,record_id)
            scope(row['user_id'])
            if row['status']=='Unread':
                row=repo.update(conn,record_id,{'status':'Read','read_date':now()})
                ctx.record(conn,'notification.read',record_id)
        return ok(row)

    @route('/notifications/search',methods=['GET'])
    @protected(ctx,ADMIN,ANALYST,AUDITOR)
    def search():
        extra,args=('user_id=?',(g.user['id'],)) if g.user['role']==ANALYST else ('',())
        with ctx.db.transaction() as conn:
            rows=repo.search(conn,request.args,{k:(k,False) for k in ('user_id','notification_type','severity','status')},extra,args)
        return ok(rows)

    @route('/notifications/<int:record_id>',methods=['DELETE'])
    @protected(ctx,ADMIN)
    def delete(record_id):
        with ctx.db.transaction() as conn:
            repo.get(conn,record_id)
            conn.execute('DELETE FROM notifications WHERE id=?',(record_id,))
            ctx.record(conn,'notification.deleted',record_id)
        return ok({'id':record_id,'deleted':True})

    @route('/internal/events',methods=['POST'])
    @internal(ctx)
    def event():
        data=body((*fields,'event_id','created_at'),(*fields,'event_id','created_at'))
        validate(data)
        text_field(data,'event_id',100)
        text_field(data,'created_at',100)
        data['status']='Unread'
        with ctx.db.transaction() as conn:
            existing=conn.execute('SELECT * FROM notifications WHERE event_id=?',(data['event_id'],)).fetchone()
            row=dict(existing) if existing else repo.insert(conn,data)
        return ok(row)
