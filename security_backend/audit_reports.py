"""Immutable audit log API and reports collected through other services' APIs."""
from collections import Counter
from flask import g, request
from .core import *

def register_logs(app,ctx):
    repo=Repository('logs')
    route=lambda path,**kw:app.route(PREFIX+path,**kw)
    fields=('user_id','action','description','severity','related_service')

    def validate(data):
        integer_field(data,'user_id',nullable=True)
        text_field(data,'action',100)
        text_field(data,'description',4000)
        enum_field(data,'severity',('Information','Warning','Error','Critical'))
        enum_field(data,'related_service',tuple(SERVICES))

    @route('/logs',methods=['POST'])
    @protected(ctx,ADMIN)
    def create():
        data=body(fields,fields)
        validate(data)
        if data['user_id'] is not None:ctx.user(data['user_id'])
        data['created_at']=now()
        with ctx.db.transaction() as conn:
            row=repo.insert(conn,data)
            ctx.record(conn,'log.created',row['id'])
        return ok(row,201)

    @route('/logs',methods=['GET'])
    @protected(ctx,ADMIN,AUDITOR)
    def all_logs():
        with ctx.db.transaction() as conn:
            rows=repo.search(conn,{}, {})
        return ok(rows)

    @route('/logs/<int:record_id>',methods=['GET'])
    @protected(ctx,ADMIN,AUDITOR,ANALYST)
    def one(record_id):
        with ctx.db.transaction() as conn:row=repo.get(conn,record_id)
        return ok(row)

    @route('/logs/search',methods=['GET'])
    @protected(ctx,ADMIN,AUDITOR,ANALYST)
    def search():
        filters={k:(k,False) for k in ('user_id','action','severity','related_service')}
        filters['date']=('substr(created_at,1,10)',False)
        if 'date' in request.args:
            try:datetime.strptime(request.args['date'],'%Y-%m-%d')
            except ValueError:raise ApiError('date must use YYYY-MM-DD')
        with ctx.db.transaction() as conn:rows=repo.search(conn,request.args,filters)
        return ok(rows)

    @route('/logs/user/<int:user_id>',methods=['GET'])
    @protected(ctx,ADMIN,AUDITOR)
    def user_logs(user_id):
        # A deleted user remains a valid historical audit subject.
        with ctx.db.transaction() as conn:
            if not conn.execute('SELECT 1 FROM users WHERE id=?',(user_id,)).fetchone():raise ApiError('User not found',404)
            rows=repo.search(conn,{}, {},'user_id=?',(user_id,))
        return ok(rows)

    @route('/logs/<int:record_id>',methods=['DELETE'])
    @protected(ctx,ADMIN)
    def delete(record_id):
        with ctx.db.transaction() as conn:
            repo.get(conn,record_id)
            conn.execute('DELETE FROM logs WHERE id=?',(record_id,))
            ctx.record(conn,'log.deleted',record_id)
        return ok({'id':record_id,'deleted':True})

    @route('/internal/events',methods=['POST'])
    @internal(ctx)
    def events():
        data=body((*fields,'created_at','event_id'),(*fields,'created_at','event_id'))
        validate(data)
        text_field(data,'created_at',100)
        text_field(data,'event_id',100)
        with ctx.db.transaction() as conn:
            existing=conn.execute('SELECT * FROM logs WHERE event_id=?',(data['event_id'],)).fetchone()
            row=dict(existing) if existing else repo.insert(conn,data)
        return ok(row)

def register_reports(app,ctx):
    def fetch(service):
        return ctx.client.call(service,'/'+service,bearer=request.headers['Authorization'])

    def grouped(rows,key):
        return dict(sorted(Counter(row[key] for row in rows).items()))

    @app.get(PREFIX+'/reports/<report_type>')
    @protected(ctx,ADMIN,AUDITOR)
    def report(report_type):
        if report_type=='summary':
            sources={service:fetch(service) for service in ('users','assets','incidents','threats','logs','vulnerabilities')}
            result={service:len(rows) for service,rows in sources.items()}
            result.update(open_incidents=sum(r['status'] not in ('Resolved','Closed') for r in sources['incidents']),critical_threats=sum(r['severity']=='Critical' for r in sources['threats']),recent_activities=sources['logs'][-5:])
        elif report_type in ('incidents','assets','threats','vulnerabilities'):
            rows=fetch(report_type)
            result={'total':len(rows)}
            if report_type=='assets':
                result.update(critical_assets=sum(r['criticality']=='Critical' for r in rows),by_type=grouped(rows,'asset_type'))
            else:
                result['by_severity']=grouped(rows,'severity')
                if report_type in ('incidents','vulnerabilities'):result['by_status']=grouped(rows,'status')
                if report_type=='threats':result.update(by_type=grouped(rows,'threat_type'),recent_added=rows[-5:])
                if report_type=='vulnerabilities':result['critical_vulnerabilities']=sum(r['severity']=='Critical' for r in rows)
        elif report_type=='activity':
            rows=fetch('logs')
            counts=Counter(r['action'] for r in rows)
            result=dict(total_activities=len(rows),login_attempts=counts['login.succeeded']+counts['login.failed'],failed_login_attempts=counts['login.failed'],most_performed_actions=[{'action':k,'count':v} for k,v in counts.most_common(10)])
        else:raise ApiError('Report not found',404)
        result['generated_at']=now()
        result['source']='Service HTTP APIs'
        return ok(result)

def register(app,ctx):
    (register_logs if ctx.service=='logs' else register_reports)(app,ctx)
