"""Initialize and launch nine local HTTP services without replacing existing data.

Usage: python run.py [--service users] [--port-offset 0]
First run writes a local administrator credential to runtime/bootstrap.json.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import threading
import time
from werkzeug.security import generate_password_hash
from security_backend.core import ADMIN,Context,Database,SERVICES,Settings,now

ROOT=Path(__file__).resolve().parent

def prepare():
    runtime=ROOT/'runtime'
    runtime.mkdir(exist_ok=True)
    key_file=runtime/'service.secret'
    if not key_file.exists():key_file.write_text(secrets.token_urlsafe(48),encoding='utf-8')
    os.environ.setdefault('SERVICE_KEY',key_file.read_text().strip())
    os.environ.setdefault('SECURITY_DB',str(runtime/'security.db'))
    db=Database(os.environ['SECURITY_DB'])
    db.initialize()
    with db.transaction() as conn:
        if not conn.execute('SELECT 1 FROM users LIMIT 1').fetchone():
            password=os.environ.get('BOOTSTRAP_PASSWORD') or 'Ak!'+secrets.token_urlsafe(18)+'7z'
            from security_backend.identity import validate_password
            validate_password(password)
            conn.execute('INSERT INTO users(full_name,username,email,password_hash,department,role,account_status,created_at) VALUES(?,?,?,?,?,?,?,?)',
                ('Abdulrahman Kobeissi','admin','admin@example.test',generate_password_hash(password,method='scrypt'),'Security',ADMIN,'Active',now()))
            (runtime/'bootstrap.json').write_text(json.dumps({'login':'admin','password':password},indent=2),encoding='utf-8')
            print('Created first administrator. Local credentials: runtime/bootstrap.json',flush=True)
    return Settings.from_env()

def deliver(settings,stop):
    contexts=[Context(s,settings) for s in SERVICES]
    while not stop.is_set():
        for ctx in contexts:
            if stop.is_set():return
            try:ctx.events.flush()
            except Exception as exc:print(f'Event delivery error ({ctx.service}): {exc}',file=sys.stderr,flush=True)
        stop.wait(0.5)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--service',choices=SERVICES)
    parser.add_argument('--port-offset',type=int,default=int(os.environ.get('PORT_OFFSET','0')))
    args=parser.parse_args()
    os.environ['PORT_OFFSET']=str(args.port_offset)
    settings=prepare()
    if args.service:
        from security_backend.app import create_app
        create_app(args.service,settings).run(host='127.0.0.1',port=SERVICES[args.service]+args.port_offset,threaded=True,debug=False,use_reloader=False)
        return
    children=[]
    stop=threading.Event()
    def shutdown(*_):stop.set()
    signal.signal(signal.SIGINT,shutdown)
    signal.signal(signal.SIGTERM,shutdown)
    try:
        for service in SERVICES:
            log=(ROOT/'runtime'/f'{service}.log').open('a',encoding='utf-8')
            proc=subprocess.Popen([sys.executable,str(ROOT/'run.py'),'--service',service,'--port-offset',str(args.port_offset)],cwd=ROOT,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            children.append((proc,log))
        worker=threading.Thread(target=deliver,args=(settings,stop),daemon=True)
        worker.start()
        print('Nine services running on 127.0.0.1 ports '+', '.join(str(p+args.port_offset) for p in SERVICES.values()),flush=True)
        print('Press Ctrl+C to stop. Existing database is preserved.',flush=True)
        while not stop.wait(1):
            if any(proc.poll() is not None for proc,_ in children):
                raise RuntimeError('A service exited. Read runtime/*.log; no database was replaced.')
    finally:
        stop.set()
        for proc,log in children:
            if proc.poll() is None:proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill()
            log.close()

if __name__=='__main__':main()
