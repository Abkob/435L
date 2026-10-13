"""Ordered response actions and permanent execution history."""
from flask import g
from .core import *

ACTION_FLOW=Lifecycle(('Pending','In Progress','Completed'))

def register(app,ctx):
    books,actions=Repository('playbooks'),Repository('response_actions')
    route=lambda path,**kw:app.route(PREFIX+path,**kw)

    @route('/playbooks',methods=['POST'])
    @protected(ctx,ADMIN)
    def create():
        fields=('name','description','incident_category','severity')
        data=body(fields,fields)
        for key in fields[:-1]:text_field(data,key,4000 if key=='description' else 200)
        enum_field(data,'severity',SEVERITIES)
        data.update(created_by=g.user['id'],created_at=now())
        with ctx.db.transaction() as conn:
            row=books.insert(conn,data)
            ctx.record(conn,'playbook.created',row['id'])
        return ok(row,201)

    @route('/playbooks',methods=['GET'])
    @protected(ctx,ADMIN,ANALYST,AUDITOR)
    def all_books():
        with ctx.db.transaction() as conn:
            rows=books.search(conn,{}, {},'deleted_at IS NULL')
        return ok(rows)

    @route('/playbooks/<int:book_id>',methods=['GET'])
    @protected(ctx,ADMIN,ANALYST,AUDITOR)
    def one(book_id):
        with ctx.db.transaction() as conn:
            row=books.get(conn,book_id)
            row['actions']=[dict(r) for r in conn.execute('SELECT * FROM response_actions WHERE playbook_id=? ORDER BY step_number',(book_id,))]
            for action in row['actions']:
                action['history']=[dict(r) for r in conn.execute('SELECT * FROM action_history WHERE action_id=? ORDER BY id',(action['id'],))]
        return ok(row)

    @route('/playbooks/<int:book_id>/actions',methods=['POST'])
    @protected(ctx,ADMIN,ANALYST)
    def add_action(book_id):
        data=body(('description','step_number','assigned_user_id'),('description','step_number'))
        text_field(data,'description',4000)
        integer_field(data,'step_number')
        integer_field(data,'assigned_user_id',True,True)
        if data.get('assigned_user_id'):
            user=ctx.user(data['assigned_user_id'])
            if user['role'] not in (ADMIN,ANALYST) or user['account_status']!='Active':
                raise ApiError('Action assignee must be an active analyst or administrator')
        data.update(playbook_id=book_id,status='Pending')
        with ctx.db.transaction() as conn:
            books.get(conn,book_id)
            last=conn.execute('SELECT COALESCE(MAX(step_number),0) FROM response_actions WHERE playbook_id=?',(book_id,)).fetchone()[0]
            if data['step_number']!=last+1:
                raise ApiError(f'Next step_number must be {last+1}',409)
            row=actions.insert(conn,data)
            conn.execute('INSERT INTO action_history(action_id,actor_id,new_status,assigned_user_id,created_at) VALUES(?,?,?,?,?)',(row['id'],g.user['id'],'Pending',row['assigned_user_id'],now()))
            ctx.record(conn,'action.created',row['id'])
        return ok(row,201)

    @route('/actions/<int:action_id>/status',methods=['PUT'])
    @protected(ctx,ADMIN,ANALYST)
    def action_status(action_id):
        data=body(('status','assigned_user_id'),('status',))
        enum_field(data,'status',ACTION_FLOW.states)
        integer_field(data,'assigned_user_id',True)
        if data.get('assigned_user_id'):
            assignee=ctx.user(data['assigned_user_id'])
            if assignee['role'] not in (ADMIN,ANALYST) or assignee['account_status']!='Active':
                raise ApiError('Action assignee must be an active analyst or administrator')
        with ctx.db.transaction() as conn:
            row=actions.get(conn,action_id)
            books.get(conn,row['playbook_id'])
            if g.user['role']==ANALYST and (row['assigned_user_id'] not in (None,g.user['id']) or data.get('assigned_user_id',g.user['id'])!=g.user['id']):
                raise ApiError('Analysts may only claim or update their own actions',403)
            ACTION_FLOW.validate(row['status'],data['status'])
            if row['status']=='Completed' and data.get('assigned_user_id',row['assigned_user_id'])!=row['assigned_user_id']:
                raise ApiError('Completed actions cannot be reassigned',409)
            if data['status']!='Pending':
                earlier=conn.execute('SELECT 1 FROM response_actions WHERE playbook_id=? AND step_number<? AND status!=?',(row['playbook_id'],row['step_number'],'Completed')).fetchone()
                if earlier:raise ApiError('Complete earlier response steps first',409)
                data.setdefault('assigned_user_id',row['assigned_user_id'] or g.user['id'])
            if data['status']=='Completed' and row['status']!='Completed':data['completion_date']=now()
            after=actions.update(conn,action_id,data)
            conn.execute('INSERT INTO action_history(action_id,actor_id,old_status,new_status,assigned_user_id,created_at) VALUES(?,?,?,?,?,?)',(action_id,g.user['id'],row['status'],after['status'],after['assigned_user_id'],now()))
            ctx.record(conn,'action.status_changed',action_id)
        return ok(after)

    @route('/playbooks/<int:book_id>',methods=['DELETE'])
    @protected(ctx,ADMIN)
    def delete(book_id):
        with ctx.db.transaction() as conn:
            books.get(conn,book_id)
            conn.execute('UPDATE playbooks SET deleted_at=? WHERE id=?',(now(),book_id))
            ctx.record(conn,'playbook.deleted',book_id)
        return ok({'id':book_id,'deleted':True,'history_retained':True})
