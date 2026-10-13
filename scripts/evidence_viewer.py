"""Read-only localhost database viewer for genuine schema and record screenshots.

This is a development evidence utility, not a product frontend. It performs
fresh read-only SQLite queries and omits sessions and credential values.
"""
from contextlib import closing
from datetime import datetime,timezone
from html import escape
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import sqlite3
from urllib.parse import urlsplit,parse_qs

ROOT=Path(__file__).resolve().parents[1]
FIELDS={
 'users':['id','full_name','username','role','account_status','password_hash'],
 'assets':['id','name','ip_address','owner_id','criticality','status'],
 'incidents':['id','title','severity','reporter_id','asset_id','assigned_analyst_id','status','resolution_date'],
 'investigation_notes':['id','incident_id','analyst_id','content','created_at'],
 'threats':['id','threat_type','value','severity','source'],
 'logs':['id','user_id','action','severity','related_service','created_at'],
 'vulnerabilities':['id','title','cve','cvss','severity','asset_id','status'],
 'notifications':['id','user_id','title','notification_type','status','read_date'],
 'playbooks':['id','name','incident_category','severity','created_by','deleted_at'],
 'response_actions':['id','playbook_id','description','step_number','status','assigned_user_id','completion_date'],
 'action_history':['id','action_id','actor_id','old_status','new_status','created_at'],
 'asset_history':['id','asset_id','actor_id','operation','created_at'],
 'outbox':['id','source','target','attempts','delivered_at','last_error']}

def table(headers,rows):
    return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+escape(str(h))+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape('NULL' if v is None else str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params=parse_qs(urlsplit(self.path).query)
        name=params.get('table',['assets'])[0]
        view=params.get('view',['records'])[0]
        if name not in FIELDS and view!='schema':self.send_error(404);return
        with closing(sqlite3.connect(f'{(ROOT/"runtime/security.db").as_uri()}?mode=ro',uri=True)) as conn:
            if view=='schema':
                title='Database schema'
                query="SELECT name FROM sqlite_master WHERE type='table'; PRAGMA table_info(table); PRAGMA foreign_key_list(table);"
                rows=[]
                for (t,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
                    cols=conn.execute('PRAGMA table_info('+t+')').fetchall()
                    fks=conn.execute('PRAGMA foreign_key_list('+t+')').fetchall()
                    rows.append([t,', '.join(c[1] for c in cols if c[5]),'; '.join(f'{r[3]} → {r[2]}.{r[4]}' for r in fks) or 'None',len(cols)])
                content=table(['Table','Primary key','Foreign keys','Fields'],rows)
                note='All 15 tables in the running implementation. Logical asset_history.asset_id intentionally retains deleted asset history.'
            else:
                title=name.replace('_',' ').title()+' records'
                fields=FIELDS[name]
                query='SELECT '+', '.join(fields)+' FROM '+name+' ORDER BY rowid DESC LIMIT 8;'
                rows=[list(r) for r in conn.execute(query)]
                if name=='users':
                    for row in rows:row[-1]=row[-1].split('$')[0]+'$[hash redacted]'
                content=table(fields,rows)
                count=conn.execute('SELECT COUNT(*) FROM '+name).fetchone()[0]
                note=f'Showing the latest {len(rows)} of {count} stored records. Timestamps are UTC. Secret values are redacted.'
            integrity=conn.execute('PRAGMA integrity_check').fetchone()[0]
            fk_count=len(conn.execute('PRAGMA foreign_key_check').fetchall())
        nav=''.join(f'<a href="/?table={t}">{t.replace("_"," ")}</a>' for t in FIELDS)
        html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Database evidence — Abdulrahman Kobeissi</title><style>
        *{box-sizing:border-box}body{font:15px/1.45 Segoe UI,Arial,sans-serif;color:#17222c;margin:0;background:#fff}main{max-width:1240px;margin:auto;padding:32px}h1{font-size:25px;margin:5px 0 8px}p{margin:8px 0 15px}.eyebrow{font-size:13px;color:#536272}nav{display:flex;flex-wrap:wrap;gap:5px 18px;border-top:1px solid #d9dfe4;margin-top:25px;padding-top:14px}a{color:#3c5367;padding:8px 0;min-height:40px}a:focus-visible{outline:2px solid #365b83;outline-offset:4px}pre{background:#f5f7f9;padding:13px;white-space:pre-wrap;font:12px/1.5 Consolas,monospace;border:1px solid #d9dfe4}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;vertical-align:top;border:1px solid #d9dfe4;padding:11px 9px;overflow-wrap:anywhere;max-width:240px}th{background:#eaf0f5;color:#142331}tr:nth-child(even){background:#fafbfc}.checks{font-size:13px;color:#3d5550}@media(max-width:600px){main{padding:18px}h1{font-size:22px}nav{gap:2px 12px}th,td{min-width:95px;padding:9px;font-size:12px}.eyebrow{font-size:12px}}
        </style><main>'''
        html+=f'<div class="eyebrow">SOFTWARE TOOLS LAB · SPRINT 1 · ABDULRAHMAN KOBEISSI</div><h1>{title}</h1><p>Live read-only query of <strong>runtime/security.db</strong> · {datetime.now(timezone.utc).isoformat(timespec="seconds")}</p><pre>{escape(query)}</pre>'+content+f'<p>{note}</p><p class="checks">Database integrity: {integrity} · Foreign-key violations: {fk_count} · Source: this local implementation</p><nav><a href="/?view=schema">Schema</a>'+nav+'</nav></main></html>'
        payload=html.encode('utf-8')
        self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(payload)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(payload)

if __name__=='__main__':
    print('Read-only evidence viewer: http://127.0.0.1:5190',flush=True)
    ThreadingHTTPServer(('127.0.0.1',5190),Handler).serve_forever()
