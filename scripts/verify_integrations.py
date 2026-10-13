"""Validate live report totals, empty results, persistence and backup evidence."""
from contextlib import closing
from datetime import datetime,timezone
import json
from pathlib import Path
import secrets
import sqlite3
import sys
import time
import requests
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from security_backend.core import SERVICES,PREFIX
from scripts.backup import backup
from scripts.verify_http import redact

def main():
    bootstrap=json.loads((ROOT/'runtime/bootstrap.json').read_text())
    session=requests.Session()
    login=session.post(f'http://127.0.0.1:5101{PREFIX}/users/login',json=bootstrap,timeout=15)
    login.raise_for_status()
    session.headers['Authorization']='Bearer '+login.json()['data']['token']
    captures=[]
    def call(service,method,path,payload=None,expected=200):
        url=f'http://127.0.0.1:{SERVICES[service]}{PREFIX}{path}'
        response=session.request(method,url,json=payload,timeout=15)
        assert response.status_code==expected,(path,response.status_code,response.text)
        data=response.json()
        captures.append(dict(service=service,method=method,url=url,request_body=redact(payload),status=expected,response=redact(data)))
        return data['data'] if expected<400 else data
    identifier='empty'+secrets.token_hex(5)
    user=call('users','POST','/users/register',dict(full_name='Empty Results Test Account',username=identifier,email=identifier+'@example.test',password='DemoPassword!2026',department='Lab',role='Regular Employee/User'),201)
    # Account creation is logged against its administrator actor, so this new
    # account has no user activities until it authenticates or performs an action.
    empty_logs=call('logs','GET',f'/logs/user/{user["id"]}')
    assert empty_logs==[]
    time.sleep(1)
    notices=call('notifications','GET',f'/notifications/user/{user["id"]}')
    for notice in notices:call('notifications','DELETE',f'/notifications/{notice["id"]}')
    assert call('notifications','GET',f'/notifications/user/{user["id"]}')==[]
    call('assets','GET',"/assets/search?name=%27%20OR%201%3D1--")
    deadline=time.monotonic()+30
    while time.monotonic()<deadline:
        with closing(sqlite3.connect(ROOT/'runtime/security.db')) as conn:
            if conn.execute('SELECT COUNT(*) FROM outbox WHERE delivered_at IS NULL').fetchone()[0]==0:break
        time.sleep(.2)
    else:raise AssertionError('Pending messages remain')
    comparisons={}
    for table in ('assets','incidents','threats','vulnerabilities'):
        report=call('reports','GET','/reports/'+table)
        with closing(sqlite3.connect(ROOT/'runtime/security.db')) as conn:
            count=conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            assert report['total']==count
            field='asset_type' if table=='assets' else 'severity'
            grouped=dict(conn.execute(f'SELECT {field},COUNT(*) FROM {table} GROUP BY {field}').fetchall())
            assert report['by_type' if table=='assets' else 'by_severity']==grouped
            if table in ('incidents','vulnerabilities'):
                by_status=dict(conn.execute(f'SELECT status,COUNT(*) FROM {table} GROUP BY status').fetchall())
                assert report['by_status']==by_status
        comparisons[table]=dict(api_total=report['total'],database_total=count,groups_match=True)
    activity=call('reports','GET','/reports/activity')
    summary=call('reports','GET','/reports/summary')
    with closing(sqlite3.connect(ROOT/'runtime/security.db')) as conn:
        counts=dict(conn.execute('SELECT action,COUNT(*) FROM logs GROUP BY action').fetchall())
        assert activity['total_activities']==sum(counts.values())
        assert activity['failed_login_attempts']==counts.get('login.failed',0)
        assert activity['login_attempts']==counts.get('login.failed',0)+counts.get('login.succeeded',0)
        for table in ('users','assets','incidents','threats','logs','vulnerabilities'):
            condition=' WHERE deleted_at IS NULL' if table=='users' else ''
            assert summary[table]==conn.execute(f'SELECT COUNT(*) FROM {table}'+condition).fetchone()[0]
        assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert not conn.execute('PRAGMA foreign_key_check').fetchall()
        automatic_events={r[0] for r in conn.execute('SELECT DISTINCT action FROM logs')}
        assert {'login.succeeded','login.failed','user.created','user.deleted','role.changed','access.denied','incident.assigned'} <= automatic_events
        conn.row_factory=sqlite3.Row
        tables=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        snapshot={table:[redact(dict(r)) for r in conn.execute('SELECT * FROM '+table+' ORDER BY rowid')] for table in tables if table not in ('sessions','login_attempts')}
    evidence=ROOT/'evidence'
    (evidence/'database-records.json').write_text(json.dumps(snapshot,indent=2),encoding='utf-8')
    manifest=backup(ROOT/'runtime/security.db',ROOT/'runtime/backups'/('verified-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.db'))
    status=dict(checked_at=datetime.now(timezone.utc).isoformat(),report_comparisons=comparisons,activity_report_matches=True,summary_report_matches=True,integrity_check='ok',foreign_key_violations=0,outbox_pending=0,empty_notifications_verified=True,empty_logs_verified=True,automatic_events=sorted(automatic_events),backup=manifest,captures=captures)
    (evidence/'integration-checks.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    # Supplemental Postman examples retain the actual empty-result and report requests.
    items=[]
    for n,capture in enumerate(captures,1):
        req={'method':capture['method'],'url':capture['url'],'description':'Abdulrahman Kobeissi. Actual supplemental integration verification. Use the main collection for a fresh repeatable run. These concrete-ID requests inspect the recorded lab run.','auth':{'type':'bearer','bearer':[{'key':'token','value':'{{admin_token}}','type':'string'}]}}
        if capture['request_body'] is not None:req['body']={'mode':'raw','raw':json.dumps(capture['request_body'],indent=2)}
        items.append({'name':f'S{n:02} {capture["method"]} {capture["url"].split(PREFIX)[1]}','request':req,'response':[{'name':f'Actual {capture["status"]} supplemental verification','originalRequest':req,'status':'OK','code':capture['status'],'header':[{'key':'Content-Type','value':'application/json'}],'body':json.dumps(capture['response'],indent=2),'_postman_previewlanguage':'json'}]})
    collection={'info':{'name':'Sprint 1 supplemental evidence — Abdulrahman Kobeissi','schema':'https://schema.getpostman.com/json/collection/v2.1.0/collection.json','description':'Actual saved requests and responses from database reconciliation and empty-result tests. Concrete IDs are historical evidence; run the main collection for reproduction.'},'item':items}
    (ROOT/'postman/Supplemental-evidence.postman_collection.json').write_text(json.dumps(collection,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in status.items() if k not in ('captures','automatic_events')},indent=2))

if __name__=='__main__':main()
