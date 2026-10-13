"""Execute the complete scenario suite against nine REAL running HTTP services.

Creates a portable Postman collection with descriptions, tests and captured examples.
Passwords and bearer tokens are excluded from published evidence and environments.
"""
from dataclasses import asdict
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import secrets
import sqlite3
import sys
import time
import uuid
import requests

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.scenarios import scenarios
from security_backend.core import PREFIX,SERVICES

def lookup(value,path):
    for key in path.split('.'):value=value[int(key)] if isinstance(value,list) else value[key]
    return value

def resolve(value,variables):
    if isinstance(value,dict):return {k:resolve(v,variables) for k,v in value.items()}
    if isinstance(value,list):return [resolve(v,variables) for v in value]
    if isinstance(value,str):
        exact=re.fullmatch(r'\{\{(\w+)\}\}',value)
        if exact:return variables[exact[1]]
        return re.sub(r'\{\{(\w+)\}\}',lambda m:str(variables[m[1]]),value)
    return value

def redact(value):
    if isinstance(value,dict):return {k:('[REDACTED]' if k in ('token','password','password_hash','token_hash') else redact(v)) for k,v in value.items()}
    if isinstance(value,list):return [redact(v) for v in value]
    return value

def wait_events():
    deadline=time.monotonic()+30
    while time.monotonic()<deadline:
        with sqlite3.connect(ROOT/'runtime/security.db') as conn:
            if conn.execute('SELECT COUNT(*) FROM outbox WHERE delivered_at IS NULL').fetchone()[0]==0:return
        time.sleep(.1)
    raise AssertionError('Durable events did not finish delivery within 30 seconds')

def main():
    bootstrap=json.loads((ROOT/'runtime/bootstrap.json').read_text())
    random_int=secrets.randbelow(60000)+1
    variables={'admin_login':bootstrap['login'],'admin_password':bootstrap['password'],'run_id':'r'+str(int(time.time()))+secrets.token_hex(2),'indicator_ip':f'198.18.{random_int//256}.{random_int%256}','indicator_hash':secrets.token_hex(32),'today':datetime.now(timezone.utc).date().isoformat()}
    items,records,failures=[],[],[]
    for index,s in enumerate(scenarios(),1):
        url=f'http://127.0.0.1:{SERVICES[s.service]}{PREFIX}'+resolve(s.path,variables)
        payload=resolve(s.body,variables)
        headers={'Content-Type':'application/json'}
        if s.role:headers['Authorization']='Bearer '+variables[s.role+'_token']
        start=time.monotonic()
        response=requests.request(s.method,url,json=payload,headers=headers,timeout=15)
        elapsed=round((time.monotonic()-start)*1000,2)
        data=response.json()
        checks=[('HTTP status',response.status_code==s.expected),('Response envelope',data.get('status')==('success' if s.expected<400 else 'error'))]
        if response.status_code==s.expected and s.expected<400:
            for variable,path in s.save.items():variables[variable]=lookup(data['data'],path)
            for path,expected in s.checks:checks.append((path,lookup(data['data'],path)==expected))
        passed=all(v for _,v in checks)
        if not passed:failures.append({'index':index,'name':s.name,'expected':s.expected,'actual':response.status_code,'body':redact(data)})
        print(f'{index:03} {"PASS" if passed else "FAIL"} {response.status_code} {s.service}: {s.name}',flush=True)
        record={'index':index,'name':s.name,'service':s.service,'method':s.method,'url':url,'request_body':redact(payload),'response_status':response.status_code,'response_body':redact(data),'elapsed_ms':elapsed,'checks':checks,'captured_at':datetime.now(timezone.utc).isoformat()}
        records.append(record)
        raw_url='{{'+s.service+'_url}}'+PREFIX+s.path
        request={'method':s.method,'header':[{'key':'Content-Type','value':'application/json'}],'url':raw_url,'description':f'Abdulrahman Kobeissi — {s.name}. Runs against the {s.service} service. Role: {s.role or "public"}. Expected HTTP {s.expected}. '+('JSON request fields: '+', '.join(s.body)+'. ' if s.body else '')+'Success uses {status: success, data: object or array}; errors use {status: error, message, request_id}. Errors include 400 validation, 401 authentication, 403 permissions, 404 missing record, 409 conflict and 503 unavailable dependency. Saved example was captured from the running implementation; secrets are redacted.'}
        request['auth']={'type':'bearer','bearer':[{'key':'token','value':'{{'+s.role+'_token}}','type':'string'}]} if s.role else {'type':'noauth'}
        if s.body:
            raw=json.dumps(s.body,indent=2)
            for key in variables:
                if key.endswith('_id') and key!='run_id':raw=raw.replace('"{{'+key+'}}"','{{'+key+'}}')
            request['body']={'mode':'raw','raw':raw,'options':{'raw':{'language':'json'}}}
        tests=[f'pm.test("HTTP {s.expected}", () => pm.response.to.have.status({s.expected}));','const body = pm.response.json();',f'pm.test("Consistent response envelope", () => pm.expect(body.status).to.eql("{"success" if s.expected<400 else "error"}"));']
        if s.expected<400:
            for variable,path in s.save.items():tests.append(f'if (pm.response.code === {s.expected}) pm.environment.set("{variable}", body.data.{path});')
            for path,expected in s.checks:tests.append(f'pm.test("{path}", () => pm.expect(body.data.{path}).to.eql({json.dumps(expected)}));')
        saved_request=dict(request,url=url)
        if payload is not None:saved_request['body']={'mode':'raw','raw':json.dumps(redact(payload),indent=2),'options':{'raw':{'language':'json'}}}
        example={'name':f'Actual HTTP {response.status_code} — {s.name}','originalRequest':saved_request,'status':response.reason,'code':response.status_code,'header':[{'key':'Content-Type','value':'application/json'}],'body':json.dumps(redact(data),indent=2),'_postman_previewlanguage':'json'}
        item={'id':str(uuid.uuid4()),'name':f'{index:03} {s.name}','request':request,'event':[{'listen':'test','script':{'type':'text/javascript','exec':tests}}],'response':[example]}
        items.append(item)
        if not passed:break
        # Wait only where a later check inspects asynchronously generated events.
        if s.service in ('logs','reports') or 'notification' in s.name.lower():wait_events()
    wait_events()
    evidence=ROOT/'evidence'
    evidence.mkdir(exist_ok=True)
    (evidence/'http-results.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    summary=dict(requests=len(records),assertions=sum(len(r['checks']) for r in records),passed=sum(all(v for _,v in r['checks']) for r in records),failures=failures,run_id=variables['run_id'],transport='Real HTTP requests to nine independent local services')
    (evidence/'http-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    if failures:raise SystemExit(json.dumps(failures,indent=2))
    prerequest=['if (pm.info.requestName.startsWith("001 ")) {','  const suffix = Date.now().toString() + Math.floor(Math.random()*9999);','  pm.environment.set("run_id", "r" + suffix);','  const n = Math.floor(Math.random()*60000)+1;','  pm.environment.set("indicator_ip", "198.18."+Math.floor(n/256)+"."+(n%256));','  pm.environment.set("indicator_hash", require("crypto-js").SHA256(suffix).toString());','  pm.environment.set("today", new Date().toISOString().slice(0,10));','}']
    collection={'info':{'name':'Sprint 1 — Abdulrahman Kobeissi','_postman_id':str(uuid.uuid4()),'schema':'https://schema.getpostman.com/json/collection/v2.1.0/collection.json','description':'Complete nine-service Sprint 1 backend. Run requests in order against local lab data. Creates a unique run prefix and never resets a database. Set admin_login and admin_password from runtime/bootstrap.json. Includes successful and deliberately rejected calls, saved actual responses and per-request assertions. Owner: Abdulrahman Kobeissi.'},'item':items,'event':[{'listen':'prerequest','script':{'type':'text/javascript','exec':prerequest}}]}
    (ROOT/'postman/Sprint1.postman_collection.json').write_text(json.dumps(collection,indent=2),encoding='utf-8')
    values=[{'key':s+'_url','value':f'http://127.0.0.1:{port}','enabled':True} for s,port in SERVICES.items()]
    values += [{'key':'admin_login','value':'admin','enabled':True},{'key':'admin_password','value':'','type':'secret','enabled':True}]
    environment={'id':str(uuid.uuid4()),'name':'Sprint 1 Local — Abdulrahman Kobeissi','values':values,'_postman_variable_scope':'environment'}
    (ROOT/'postman/Sprint1.postman_environment.json').write_text(json.dumps(environment,indent=2),encoding='utf-8')
    private_environment=dict(environment,values=values+[{'key':k,'value':v,'enabled':True,'type':'secret' if 'token' in k or 'password' in k else 'default'} for k,v in variables.items() if k!='admin_login'])
    # Private runner input never enters Git or the submission archive.
    (ROOT/'runtime/postman.private.json').write_text(json.dumps(private_environment,indent=2),encoding='utf-8')
    (ROOT/'runtime/verification-variables.json').write_text(json.dumps(variables,indent=2),encoding='utf-8')
    with sqlite3.connect(ROOT/'runtime/security.db') as conn:
        conn.row_factory=sqlite3.Row
        tables=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        snapshot={table:[redact(dict(r)) for r in conn.execute('SELECT * FROM '+table+' ORDER BY rowid')] for table in tables if table not in ('sessions','login_attempts')}
        schema={table:{'columns':[dict(r) for r in conn.execute('PRAGMA table_info('+table+')')],'foreign_keys':[dict(r) for r in conn.execute('PRAGMA foreign_key_list('+table+')')]} for table in tables}
    (evidence/'database-records.json').write_text(json.dumps(snapshot,indent=2),encoding='utf-8')
    (evidence/'database-schema.json').write_text(json.dumps(schema,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
