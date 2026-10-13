"""Create and verify a consistent SQLite backup; never overwrite a backup."""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
from datetime import datetime,timezone

def backup(source,destination):
    source,destination=Path(source).resolve(),Path(destination).resolve()
    if not source.is_file():raise FileNotFoundError(source)
    if destination.exists():raise FileExistsError('Choose a new backup path')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(f'{source.as_uri()}?mode=ro',uri=True)) as src,closing(sqlite3.connect(destination)) as dst:
        src.backup(dst)
        assert dst.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert not dst.execute('PRAGMA foreign_key_check').fetchall()
        counts={r[0]:dst.execute('SELECT COUNT(*) FROM "'+r[0]+'"').fetchone()[0] for r in dst.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    manifest=dict(created_at=datetime.now(timezone.utc).isoformat(),sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),integrity_check='ok',foreign_key_violations=0,table_counts=counts)
    destination.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source')
    p.add_argument('destination')
    a=p.parse_args()
    print(json.dumps(backup(a.source,a.destination),indent=2))
