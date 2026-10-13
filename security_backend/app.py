"""Application factory; creates one independently runnable Flask service."""
import importlib
import sqlite3
import uuid
from flask import Flask,g,jsonify,request
from werkzeug.exceptions import HTTPException
from .core import *

MODULES={'users':'identity','assets':'assets','incidents':'incidents','threats':'catalogs','logs':'audit_reports','reports':'audit_reports','vulnerabilities':'catalogs','notifications':'notifications','playbooks':'playbooks'}

def create_app(service,settings=None):
    if service not in SERVICES:raise ValueError('Unknown service')
    settings=settings or Settings.from_env()
    app=Flask(service,static_folder=None)
    app.config.update(MAX_CONTENT_LENGTH=64*1024,JSON_SORT_KEYS=False)
    ctx=Context(service,settings)
    app.extensions['security_context']=ctx
    importlib.import_module('.'+MODULES[service],__package__).register(app,ctx)

    @app.before_request
    def identify_request():
        g.request_id=str(uuid.uuid4())

    @app.after_request
    def headers(response):
        response.headers['X-Request-ID']=g.get('request_id','')
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        # Delivery is asynchronous. Status is exposed by /health; run.py retries.
        with ctx.db.transaction() as conn:
            pending=conn.execute('SELECT COUNT(*) FROM outbox WHERE source=? AND delivered_at IS NULL',(service,)).fetchone()[0]
        response.headers['X-Pending-Events']=str(pending)
        return response

    @app.errorhandler(ApiError)
    def api_error(error):
        if error.status in (401,403,429) and not g.get('auth_event_recorded'):
            with ctx.db.transaction() as conn:
                ctx.events.audit(conn,'access.denied',f'{request.method} {request.path}: {error.message}',g.get('user',{}).get('id'),'Warning')
        return jsonify(status='error',message=error.message,request_id=g.get('request_id')),error.status

    @app.errorhandler(sqlite3.IntegrityError)
    def integrity(error):
        message='Record conflicts with an existing record or a database constraint'
        if 'UNIQUE' in str(error):message='A record with this unique username, email, indicator or step already exists'
        if 'FOREIGN KEY' in str(error):message='Record is referenced by another entity or a referenced record does not exist'
        return api_error(ApiError(message,409))

    @app.errorhandler(HTTPException)
    def http_error(error):return api_error(ApiError(error.description,error.code))

    @app.errorhandler(Exception)
    def unexpected(error):
        app.logger.exception('Unhandled error for request %s',g.get('request_id'))
        return api_error(ApiError('An internal error occurred; use the request ID when reporting it',500))

    @app.get(PREFIX+'/health')
    def health():
        with ctx.db.transaction() as conn:
            pending=conn.execute('SELECT COUNT(*) FROM outbox WHERE source=? AND delivered_at IS NULL',(service,)).fetchone()[0]
            failed=conn.execute('SELECT COUNT(*) FROM outbox WHERE source=? AND delivered_at IS NULL AND attempts>0',(service,)).fetchone()[0]
        return ok(dict(service=service,database='available',pending_events=pending,failed_deliveries=failed,delivery_status='retrying' if failed else 'healthy'))

    @app.get(PREFIX+'/openapi.json')
    def spec():
        path=Path(__file__).resolve().parents[1]/'docs'/'openapi.json'
        if not path.exists():raise ApiError('Generate API documentation with scripts/build_api_docs.py',503)
        document=json.loads(path.read_text(encoding='utf-8'))
        document['paths']={k:v for k,v in document['paths'].items() if any(isinstance(op,dict) and op.get('tags')==[service] for op in v.values())}
        document['servers']=[{'url':f'http://127.0.0.1:{SERVICES[service]+settings.port_offset}'}]
        return jsonify(document)
    return app
