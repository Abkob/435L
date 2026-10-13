"""Security and persistence tests using a disposable database, never live data."""
import json
from contextlib import closing
from pathlib import Path
import secrets
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from werkzeug.security import generate_password_hash,check_password_hash
from security_backend.app import create_app
from security_backend.core import *
from scripts.backup import backup

class InvariantTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/'test.db'
        self.settings=Settings(str(self.path),secrets.token_urlsafe(36),300)
        self.db=Database(self.path)
        self.db.initialize()
        self.apps={s:create_app(s,self.settings) for s in SERVICES}
        self.clients={s:app.test_client() for s,app in self.apps.items()}
        with self.db.transaction() as c:
            for username,role in [('admin',ADMIN),('analyst',ANALYST),('employee',EMPLOYEE),('auditor',AUDITOR),('other',EMPLOYEE)]:
                c.execute('INSERT INTO users(full_name,username,email,password_hash,department,role,account_status,created_at) VALUES(?,?,?,?,?,?,?,?)',(username,username,username+'@example.test',generate_password_hash('TestPassword!2026',method='scrypt'),'Lab',role,'Active',now()))
        def local_call(client,service,path,method='GET',payload=None,bearer=None):
            headers={'X-Service-Key':self.settings.internal_key}
            if bearer:headers['Authorization']=bearer
            response=self.clients[service].open(PREFIX+path,method=method,json=payload,headers=headers)
            data=response.get_json()
            if response.status_code>=400:raise ApiError(data['message'],response.status_code)
            return data['data']
        self.network=patch.object(ServiceClient,'call',local_call)
        self.network.start()
        self.tokens={}
        for username in ('admin','analyst','employee','auditor','other'):
            response=self.clients['users'].post(PREFIX+'/users/login',json={'login':username,'password':'TestPassword!2026'})
            self.tokens[username]=response.json['data']['token']

    def tearDown(self):
        self.network.stop()
        self.temp.cleanup()

    def req(self,service,method,path,role='admin',data=None):
        return self.clients[service].open(PREFIX+path,method=method,json=data,headers={'Authorization':'Bearer '+self.tokens[role]} if role else {})

    def asset(self):
        return self.req('assets','POST','/assets',data={'name':'Server','asset_type':'Server','ip_address':'192.0.2.1','department':'Lab','owner_id':3,'criticality':'High'}).json['data']

    def drain(self):
        for _ in range(3):
            for app in self.apps.values():app.extensions['security_context'].events.flush()

    def test_passwords_and_tokens_are_hashed(self):
        with self.db.transaction() as c:
            password=c.execute('SELECT password_hash FROM users WHERE id=1').fetchone()[0]
            tokens=[r[0] for r in c.execute('SELECT token_hash FROM sessions')]
        self.assertTrue(password.startswith('scrypt:'))
        self.assertTrue(check_password_hash(password,'TestPassword!2026'))
        self.assertNotIn(self.tokens['admin'],tokens)
        self.assertIn(token_digest(self.tokens['admin']),tokens)
        self.assertNotIn('password_hash',self.req('users','GET','/users').get_data(as_text=True))

    def test_sql_injection_is_a_literal_search_value(self):
        self.asset()
        response=self.req('assets','GET',"/assets/search?name=%27%20OR%201%3D1--")
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json['data'],[])
        self.assertEqual(len(self.req('assets','GET','/assets').json['data']),1)

    def test_foreign_keys_protect_referenced_asset(self):
        asset=self.asset()
        self.req('incidents','POST','/incidents','employee',{'title':'Test','description':'Example','category':'Phishing','severity':'High','asset_id':asset['id']})
        self.assertEqual(self.req('assets','DELETE',f'/assets/{asset["id"]}').status_code,409)

    def test_audit_rows_are_immutable_in_database(self):
        self.drain()
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.transaction() as c:c.execute("UPDATE logs SET description='tampered'")

    def test_denied_access_is_automatically_logged(self):
        self.assertEqual(self.req('assets','GET','/assets','employee').status_code,403)
        self.drain()
        with self.db.transaction() as c:
            row=c.execute("SELECT * FROM logs WHERE action='access.denied' AND user_id=3").fetchone()
        self.assertIsNotNone(row)

    def test_outbox_retries_and_deduplicates(self):
        ctx=self.apps['assets'].extensions['security_context']
        with self.db.transaction() as c:ctx.events.audit(c,'retry.test','Preserve this',1)
        with patch.object(ServiceClient,'call',side_effect=ApiError('Service down',503)):ctx.events.flush()
        with self.db.transaction() as c:row=dict(c.execute("SELECT * FROM outbox WHERE source='assets'").fetchone())
        self.assertIsNone(row['delivered_at'])
        self.assertEqual(row['attempts'],1)
        ctx.events.flush()
        ctx.client.call('logs','/internal/events','POST',json.loads(row['payload']))
        with self.db.transaction() as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM logs WHERE event_id=?',(row['id'],)).fetchone()[0],1)
            self.assertIsNotNone(c.execute('SELECT delivered_at FROM outbox WHERE id=?',(row['id'],)).fetchone()[0])

    def test_notification_read_is_idempotent_and_scoped(self):
        record=self.req('notifications','POST','/notifications',data={'user_id':3,'title':'Test','message':'Message','notification_type':'Security Alert','severity':'High'}).json['data']
        path=f'/notifications/{record["id"]}'
        self.assertEqual(self.req('notifications','GET',path,'other').status_code,403)
        first=self.req('notifications','PUT',path+'/read','employee').json['data']['read_date']
        second=self.req('notifications','PUT',path+'/read','employee').json['data']['read_date']
        self.assertEqual(first,second)
        self.assertEqual(self.req('notifications','PUT',path+'/read','auditor').status_code,403)

    def test_empty_notifications_and_logs_are_arrays(self):
        self.assertEqual(self.req('notifications','GET','/notifications/user/5','other').json['data'],[])
        # Existing account with no logged activity before its queued login reaches audit service.
        self.assertEqual(self.req('logs','GET','/logs/user/5').json['data'],[])

    def test_incident_notes_and_analyst_scope(self):
        asset=self.asset()
        incident=self.req('incidents','POST','/incidents','employee',{'title':'Test','description':'Example','category':'Phishing','severity':'High','asset_id':asset['id']}).json['data']
        path=f'/incidents/{incident["id"]}'
        self.assertEqual(self.req('incidents','GET',path,'analyst').status_code,403)
        self.req('incidents','PUT',path+'/assign',data={'analyst_id':2})
        self.assertEqual(self.req('assets','GET',f'/assets/{asset["id"]}','analyst').status_code,200)
        self.req('incidents','POST',path+'/notes','analyst',{'content':'Confidential investigation note'})
        self.assertEqual(len(self.req('incidents','GET',path,'analyst').json['data']['notes']),1)
        self.assertNotIn('notes',self.req('incidents','GET',path,'employee').json['data'])
        self.assertEqual(self.req('incidents','GET',path,'other').status_code,403)

    def test_all_lifecycle_edges(self):
        flow=Lifecycle(('Open','Under Investigation','Mitigated','Resolved','Closed'))
        for i,current in enumerate(flow.states):
            for j,target in enumerate(flow.states):
                if j in (i,i+1):flow.validate(current,target)
                else:
                    with self.assertRaises(ApiError):flow.validate(current,target)

    def test_playbook_history_survives_deletion(self):
        book=self.req('playbooks','POST','/playbooks',data={'name':'Response','description':'Test','incident_category':'Phishing','severity':'High'}).json['data']
        action=self.req('playbooks','POST',f'/playbooks/{book["id"]}/actions','analyst',{'description':'Isolate','step_number':1,'assigned_user_id':2}).json['data']
        self.req('playbooks','PUT',f'/actions/{action["id"]}/status','analyst',{'status':'In Progress'})
        self.req('playbooks','DELETE',f'/playbooks/{book["id"]}')
        self.assertEqual(self.req('playbooks','GET',f'/playbooks/{book["id"]}').status_code,404)
        with self.db.transaction() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM action_history').fetchone()[0],2)

    def test_report_uses_http_client_and_matches_records(self):
        self.asset()
        ctx=self.apps['reports'].extensions['security_context']
        with patch.object(ctx.client,'call',wraps=ctx.client.call) as calls:
            report=self.req('reports','GET','/reports/assets','auditor')
            self.assertEqual(report.json['data']['total'],1)
            self.assertEqual(report.json['data']['by_type'],{'Server':1})
            self.assertTrue(any(c.args[:2]==('assets','/assets') for c in calls.call_args_list))

    def test_missing_report_dependency_fails_visibly(self):
        ctx=self.apps['reports'].extensions['security_context']
        actual=ctx.client.call
        def failure(service,*args,**kwargs):
            if service=='assets':raise ApiError('assets service unavailable',503)
            return actual(service,*args,**kwargs)
        with patch.object(ctx.client,'call',side_effect=failure):
            response=self.req('reports','GET','/reports/assets','auditor')
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json['status'],'error')

    def test_role_change_and_suspension_revoke_sessions(self):
        self.req('users','PUT','/users/3/role',data={'role':AUDITOR})
        self.assertEqual(self.req('users','GET','/users','employee').status_code,401)
        self.req('users','PUT','/users/2/status',data={'account_status':'Suspended'})
        self.assertEqual(self.req('threats','GET','/threats','analyst').status_code,401)

    def test_last_administrator_is_protected(self):
        self.assertEqual(self.req('users','DELETE','/users/1/role').status_code,409)
        self.assertEqual(self.req('users','PUT','/users/1/status',data={'account_status':'Suspended'}).status_code,409)

    def test_empty_malformed_and_unknown_input(self):
        self.assertEqual(self.req('assets','POST','/assets',data={}).status_code,400)
        response=self.clients['assets'].post(PREFIX+'/assets',data='{',content_type='application/json',headers={'Authorization':'Bearer '+self.tokens['admin']})
        self.assertEqual(response.status_code,400)
        self.assertEqual(self.req('users','PUT','/users/3','employee',{'role':ADMIN}).status_code,400)
        self.assertEqual(self.req('assets','GET','/assets/search?unknown=1').status_code,400)

    def test_session_expiry_and_internal_authentication(self):
        with self.db.transaction() as c:c.execute('UPDATE sessions SET expires_at=? WHERE user_id=3',('2000-01-01T00:00:00+00:00',))
        self.assertEqual(self.req('users','GET','/users/employee','employee').status_code,401)
        self.assertEqual(self.clients['users'].get(PREFIX+'/internal/users/1').status_code,401)

    def test_backup_is_restorable_and_cannot_overwrite(self):
        self.asset()
        destination=Path(self.temp.name)/'backup.db'
        result=backup(self.path,destination)
        self.assertEqual(result['integrity_check'],'ok')
        self.assertEqual(result['table_counts']['assets'],1)
        with closing(sqlite3.connect(destination)) as conn:self.assertEqual(conn.execute('SELECT name FROM assets').fetchone()[0],'Server')
        with self.assertRaises(FileExistsError):backup(self.path,destination)

if __name__=='__main__':unittest.main()
