"""Threat and vulnerability services share CRUD plumbing and specialize validation."""
import re
from flask import g, request
from .core import *

THREAT_TYPES = ('IP Address','Domain','File Hash','Malware Signature','Other Indicators')
VULNERABILITY_FLOW = Lifecycle(('Open','Under Investigation','In Progress','Resolved','Closed'))

class CatalogService:
    """Base class: authorization, persistence and events are reused by both catalogs."""
    table = ''
    create_fields = ()
    update_fields = ()
    search_fields = ()
    update_roles = (ADMIN,)

    def __init__(self, ctx):
        self.ctx, self.repo = ctx, Repository(self.table)

    def validate(self, data, partial=False):
        raise NotImplementedError

    def before_update(self, current, data):
        pass

    def register(self, app):
        ctx, repo = self.ctx, self.repo
        route = lambda path, **kw: app.route(PREFIX+'/'+self.table+path, **kw)

        @route('',methods=['POST'])
        @protected(ctx,ADMIN)
        def create():
            data=body(self.create_fields,self.create_fields)
            self.validate(data)
            data['created_at']=now()
            if self.table=='vulnerabilities':
                data['status']='Open'
            with ctx.db.transaction() as conn:
                row=repo.insert(conn,data)
                ctx.record(conn,self.table+'.created',row['id'])
                if row['severity'] in ('High','Critical'):
                    alert_type='Threat Alert' if self.table=='threats' else 'Vulnerability Alert'
                    ctx.events.notify(conn,g.user['id'],alert_type,f'{self.table} record {row["id"]} requires review.',alert_type,row['severity'])
            return ok(row,201)

        @route('',methods=['GET'])
        @protected(ctx,ADMIN,ANALYST,AUDITOR)
        def all_records():
            with ctx.db.transaction() as conn:
                rows=repo.search(conn,request.args,{key:(key,key in ('value','source')) for key in self.search_fields})
            return ok(rows)

        @route('/search',methods=['GET'])
        @protected(ctx,ADMIN,ANALYST,AUDITOR)
        def search():
            return all_records.__wrapped__()

        @route('/<int:record_id>',methods=['GET'])
        @protected(ctx,ADMIN,ANALYST,AUDITOR)
        def one(record_id):
            with ctx.db.transaction() as conn:
                row=repo.get(conn,record_id)
            return ok(row)

        @route('/<int:record_id>',methods=['PUT'])
        @protected(ctx,*self.update_roles)
        def update(record_id):
            data=body(self.update_fields)
            self.validate(data,True)
            with ctx.db.transaction() as conn:
                current=repo.get(conn,record_id)
                self.before_update(current,data)
                row=repo.update(conn,record_id,data)
                ctx.record(conn,self.table+'.updated',record_id)
            return ok(row)

        @route('/<int:record_id>',methods=['DELETE'])
        @protected(ctx,ADMIN)
        def delete(record_id):
            with ctx.db.transaction() as conn:
                repo.get(conn,record_id)
                conn.execute(f'DELETE FROM {self.table} WHERE id=?',(record_id,))
                ctx.record(conn,self.table+'.deleted',record_id)
            return ok({'id':record_id,'deleted':True})

class ThreatService(CatalogService):
    table='threats'
    create_fields=('threat_type','value','description','severity','source')
    update_fields=('description','severity','source')
    search_fields=('threat_type','value','severity','source')

    def validate(self,data,partial=False):
        for key in ('description','source'):
            text_field(data,key,4000 if key=='description' else 200,partial)
        enum_field(data,'severity',SEVERITIES,partial)
        if partial:
            return
        enum_field(data,'threat_type',THREAT_TYPES)
        text_field(data,'value',500)
        kind=data['threat_type']
        if kind=='IP Address':
            ip_field(data,'value')
        elif kind=='Domain':
            value=data['value'].lower().rstrip('.')
            if len(value)>253 or not re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}',value):
                raise ApiError('Invalid domain indicator')
            data['value']=value
        elif kind=='File Hash':
            if len(data['value']) not in (32,40,64) or not re.fullmatch('[a-fA-F0-9]+',data['value']):
                raise ApiError('Hash must be hexadecimal MD5, SHA1 or SHA256')
            data['value']=data['value'].lower()

class VulnerabilityService(CatalogService):
    table='vulnerabilities'
    create_fields=('title','description','cve','cvss','severity','asset_id','discovery_source')
    update_fields=('description','severity','status','cvss','resolution_date')
    search_fields=('cve','severity','asset_id','status')
    update_roles=(ADMIN,ANALYST)

    def validate(self,data,partial=False):
        for key in ('title','description','discovery_source'):
            text_field(data,key,4000 if key=='description' else 200,partial)
        enum_field(data,'severity',SEVERITIES,partial)
        if 'cvss' in data or not partial:
            score=data.get('cvss')
            if type(score) not in (int,float) or not 0<=score<=10:
                raise ApiError('cvss must be a number from 0 to 10')
        if not partial:
            text_field(data,'cve',30)
            data['cve']=data['cve'].upper()
            if not re.fullmatch(r'CVE-\d{4}-\d{4,}',data['cve']):
                raise ApiError('Invalid CVE identifier')
            integer_field(data,'asset_id')
            self.ctx.asset(data['asset_id'])
        if 'status' in data:
            enum_field(data,'status',VULNERABILITY_FLOW.states)
        if 'resolution_date' in data:
            try:
                timestamp=datetime.fromisoformat(data['resolution_date'])
                if timestamp.tzinfo is None or timestamp>datetime.now(timezone.utc):
                    raise ValueError
            except (ValueError,TypeError):
                raise ApiError('resolution_date must be an ISO timestamp with timezone, not in the future')

    def before_update(self,current,data):
        target=data.get('status',current['status'])
        VULNERABILITY_FLOW.validate(current['status'],target)
        if 'resolution_date' in data and target not in ('Resolved','Closed'):
            raise ApiError('Resolution date requires Resolved or Closed status')
        if 'resolution_date' in data and datetime.fromisoformat(data['resolution_date'])<datetime.fromisoformat(current['created_at']):
            raise ApiError('Resolution date cannot predate discovery')
        if target=='Resolved' and current['status']!='Resolved':
            data.setdefault('resolution_date',now())

def register(app,ctx):
    (ThreatService(ctx) if ctx.service=='threats' else VulnerabilityService(ctx)).register(app)
