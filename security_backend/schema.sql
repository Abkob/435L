PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, full_name TEXT NOT NULL, username TEXT NOT NULL COLLATE NOCASE UNIQUE,
 email TEXT NOT NULL COLLATE NOCASE UNIQUE, password_hash TEXT NOT NULL, department TEXT NOT NULL,
 role TEXT NOT NULL CHECK(role IN ('Security Administrator','Security Analyst','Regular Employee/User','Auditor')),
 account_status TEXT NOT NULL DEFAULT 'Active' CHECK(account_status IN ('Active','Inactive','Suspended')),
 created_at TEXT NOT NULL, last_login_at TEXT, deleted_at TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
 token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), expires_at TEXT NOT NULL,
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS login_attempts (
 id INTEGER PRIMARY KEY, login TEXT NOT NULL, address TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assets (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, asset_type TEXT NOT NULL,
 ip_address TEXT NOT NULL, operating_system TEXT NOT NULL DEFAULT '', department TEXT NOT NULL,
 owner_id INTEGER NOT NULL REFERENCES users(id), location TEXT NOT NULL DEFAULT '',
 criticality TEXT NOT NULL CHECK(criticality IN ('Low','Medium','High','Critical')),
 status TEXT NOT NULL CHECK(status IN ('Active','Inactive','Under Maintenance')), created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS asset_history (
 id INTEGER PRIMARY KEY, asset_id INTEGER NOT NULL, actor_id INTEGER REFERENCES users(id),
 operation TEXT NOT NULL, before_json TEXT, after_json TEXT, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS incidents (
 id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL, category TEXT NOT NULL,
 severity TEXT NOT NULL CHECK(severity IN ('Low','Medium','High','Critical')),
 reporter_id INTEGER NOT NULL REFERENCES users(id), asset_id INTEGER REFERENCES assets(id) ON DELETE RESTRICT,
 assigned_analyst_id INTEGER REFERENCES users(id),
 status TEXT NOT NULL CHECK(status IN ('Open','Under Investigation','Mitigated','Resolved','Closed')),
 created_at TEXT NOT NULL, resolution_date TEXT
);
CREATE TABLE IF NOT EXISTS investigation_notes (
 id INTEGER PRIMARY KEY, incident_id INTEGER NOT NULL REFERENCES incidents(id),
 analyst_id INTEGER NOT NULL REFERENCES users(id), content TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS threats (
 id INTEGER PRIMARY KEY, threat_type TEXT NOT NULL, value TEXT NOT NULL,
 description TEXT NOT NULL, severity TEXT NOT NULL CHECK(severity IN ('Low','Medium','High','Critical')),
 source TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(threat_type,value)
);
CREATE TABLE IF NOT EXISTS logs (
 id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id), action TEXT NOT NULL,
 description TEXT NOT NULL, severity TEXT NOT NULL CHECK(severity IN ('Information','Warning','Error','Critical')),
 related_service TEXT NOT NULL, created_at TEXT NOT NULL, event_id TEXT UNIQUE
);
CREATE TRIGGER IF NOT EXISTS logs_immutable BEFORE UPDATE ON logs
 BEGIN SELECT RAISE(ABORT, 'Audit logs are immutable'); END;
CREATE TABLE IF NOT EXISTS vulnerabilities (
 id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL, cve TEXT NOT NULL,
 cvss REAL NOT NULL CHECK(cvss BETWEEN 0 AND 10),
 severity TEXT NOT NULL CHECK(severity IN ('Low','Medium','High','Critical')),
 asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE RESTRICT, discovery_source TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('Open','Under Investigation','In Progress','Resolved','Closed')),
 created_at TEXT NOT NULL, resolution_date TEXT
);
CREATE TABLE IF NOT EXISTS notifications (
 id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), title TEXT NOT NULL,
 message TEXT NOT NULL, notification_type TEXT NOT NULL, severity TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('Unread','Read')), created_at TEXT NOT NULL, read_date TEXT,
 event_id TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS playbooks (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL, incident_category TEXT NOT NULL,
 severity TEXT NOT NULL CHECK(severity IN ('Low','Medium','High','Critical')),
 created_by INTEGER NOT NULL REFERENCES users(id), created_at TEXT NOT NULL, deleted_at TEXT
);
CREATE TABLE IF NOT EXISTS response_actions (
 id INTEGER PRIMARY KEY, playbook_id INTEGER NOT NULL REFERENCES playbooks(id), description TEXT NOT NULL,
 step_number INTEGER NOT NULL CHECK(step_number>0),
 status TEXT NOT NULL CHECK(status IN ('Pending','In Progress','Completed')),
 assigned_user_id INTEGER REFERENCES users(id), completion_date TEXT, UNIQUE(playbook_id,step_number)
);
CREATE TABLE IF NOT EXISTS action_history (
 id INTEGER PRIMARY KEY, action_id INTEGER NOT NULL REFERENCES response_actions(id),
 actor_id INTEGER NOT NULL REFERENCES users(id), old_status TEXT, new_status TEXT NOT NULL,
 assigned_user_id INTEGER REFERENCES users(id), created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS outbox (
 id TEXT PRIMARY KEY, source TEXT NOT NULL, target TEXT NOT NULL, payload TEXT NOT NULL,
 created_at TEXT NOT NULL, delivered_at TEXT, attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT
);
CREATE INDEX IF NOT EXISTS idx_incident_assignee ON incidents(assigned_analyst_id);
CREATE INDEX IF NOT EXISTS idx_incident_reporter ON incidents(reporter_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_logs_user ON logs(user_id);
CREATE INDEX IF NOT EXISTS idx_vulnerability_asset ON vulnerabilities(asset_id);
CREATE INDEX IF NOT EXISTS idx_outbox_pending ON outbox(source,delivered_at);
