# Sprint 1 security incident backend

**Abdulrahman Kobeissi · Software Tools Lab · Fall 2026–2027**

Nine independently running Flask REST services implement incident reporting,
investigation, assets, threat intelligence, vulnerabilities, notifications,
playbooks, identity and audit reporting. The deliverable is backend-only.

Repository: https://github.com/Abkob/Abdulrahman-Kobeissi-435L

Current report: [AUB-styled LaTeX PDF](Sprint1-Report-AUB.pdf).

## Run locally

Requires Python 3.12 or later. From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

On macOS/Linux substitute `.venv/bin/python` for the Windows interpreter path.
Open a second terminal for testing. Keep the first terminal running; Ctrl+C
stops its nine child services. Existing database contents are reused.

First launch creates `runtime/security.db`, a random internal service key and
an administrator account. Read `runtime/bootstrap.json` locally for its login
and password. These files are deliberately excluded from Git and the ZIP.
Do not upload them. A new checkout generates its own credentials.

Use `--port-offset 100` if the default ports are in use. A single service can be
started with `python run.py --service users`; its audit outbox still retries.
Start the other required services before exercising cross-service operations.

| Service | Port | Resource prefix |
| --- | ---: | --- |
| Identity | 5101 | `/Abdulrahman-Kobeissi/users` |
| Assets | 5102 | `/Abdulrahman-Kobeissi/assets` |
| Incidents | 5103 | `/Abdulrahman-Kobeissi/incidents` |
| Threat intelligence | 5104 | `/Abdulrahman-Kobeissi/threats` |
| Audit logs | 5105 | `/Abdulrahman-Kobeissi/logs` |
| Reports | 5106 | `/Abdulrahman-Kobeissi/reports` |
| Vulnerabilities | 5107 | `/Abdulrahman-Kobeissi/vulnerabilities` |
| Notifications | 5108 | `/Abdulrahman-Kobeissi/notifications` |
| Playbooks and actions | 5109 | `/Abdulrahman-Kobeissi/playbooks`, `/Abdulrahman-Kobeissi/actions` |

Every service exposes `/Abdulrahman-Kobeissi/health` and
`/Abdulrahman-Kobeissi/openapi.json`. Health includes pending and failed event
delivery counts. The supervisor reports a child process failure visibly.

## Postman

1. Import both JSON files in `postman/`.
2. Select **Sprint 1 Local — Abdulrahman Kobeissi**.
3. Set the environment's local `admin_password` to the value from
   `runtime/bootstrap.json`. `admin_login` defaults to `admin`.
4. In Postman web, select the running **Desktop Agent**, which can reach
   `127.0.0.1`. The Cloud Agent cannot reach these local services.
5. Run all requests in their numbered order. The collection creates a unique
   prefix for each run, stores generated IDs and tokens, and tests both expected
   successes and expected rejections. Do not reorder lifecycle requests.
6. Open a request's saved example to inspect its recorded response. Those
   examples came from actual HTTP executions; passwords/tokens are redacted.

The complete collection has 173 requests and 364 assertions. A 400, 401, 403,
404 or 409 response is a passing result when that request deliberately tests
invalid input or permissions. Run results must be judged by assertions.

Reproducible command-line run after installing Node.js and Newman:

```powershell
npx --yes newman@6.2.3 run postman/Sprint1.postman_collection.json -e postman/Sprint1.postman_environment.json --env-var "admin_password=YOUR_LOCAL_PASSWORD"
```

To avoid placing a password in shell history, use a private environment file
inside `runtime/` and pass its path with `-e`. The provided Python verifier
creates that private runner input automatically. Never commit it.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/verify_http.py
.\.venv\Scripts\python.exe scripts/build_api_docs.py
```

Unit tests use temporary databases. The HTTP verifier uses the running local
lab instance, adds uniquely named demo records and never resets a database.
The fictional IPs, domains, CVEs and incidents are controlled test fixtures,
not claims about real malicious infrastructure or discovered vulnerabilities.

`evidence/` contains actual sanitized HTTP captures, Newman results, database
schema and record exports, test results and screenshots. Raw runtime secrets
and password hashes are omitted. The OpenAPI file and `docs/API_REFERENCE.md`
document all 60 business API operations, including the 54 required operations.

## Design and security decisions

- Nine HTTP processes share one SQLite database for a manageable Sprint 1
  deployment and real foreign-key enforcement. This is a shared-database
  service architecture, not nine isolated databases. Service code owns its
  writes; identity checks, entity validation, reports, audit delivery and alert
  delivery use HTTP APIs. Some local relationship reads use the shared schema.
- `Database` encapsulates transactions; `Repository` reuses data access;
  `CatalogService` uses inheritance and specialized validation;
  `Lifecycle` validates ordered transitions; `ServiceClient` and `EventBus`
  encapsulate integration and retry behavior.
- Passwords use Werkzeug scrypt. Opaque one-hour session tokens are stored as
  SHA-256 digests. Logout, role changes and account status changes revoke
  sessions. Public registration cannot create privileged accounts.
- Every protected request verifies the current active account, role and
  resource scope. Analysts see assigned incidents and related assets;
  employees see their own reports and notifications. Auditor operations do not
  mutate business records. Audit traces of rejected operations are still kept.
- Incident and vulnerability state changes advance one step at a time.
  Playbook actions must execute in order; action history survives deletion.
- User deletion creates an inactive tombstone, preserving foreign keys and
  historic audit information. Playbook deletion also preserves execution
  history. API retrieval excludes these deleted records.
- Database uniqueness rejects duplicate usernames, email addresses, normalized
  threat indicators and playbook steps. Bound SQL values prevent injection.
- Business writes and outgoing events commit together. HTTP consumers deduplicate
  event IDs. Failed delivery remains in the outbox, retries, and appears in
  health responses; source responses also expose `X-Pending-Events`.
- A report fails with 503 if a required service cannot be reached. It never
  silently replaces missing data with zero. Cross-service report reads are not
  one atomic database snapshot, so totals can change during concurrent writes.
- The handout's general role description and detailed service tables differ in
  a few places. Read-only auditor threat search is retained; analysts may read
  specific audit logs and search logs as the audit-service table allows.
  Employee/analyst incident lists are scoped to their own/assigned records.

This localhost teaching deployment uses Flask's development server. Public
deployment would require production WSGI hosting, TLS, per-service credentials,
secret management, pagination and operational monitoring. No production cloud
database has been created, replaced or modified.

## Backups

The nine-service supervisor creates a verified backup on startup and hourly
while it runs. `runtime/backup-status.json` records success or the failure reason;
failures also appear in the supervisor output. Backups stay private and local.

Create a verified local recovery copy without changing the source:

```powershell
.\.venv\Scripts\python.exe scripts/backup.py runtime/security.db runtime/backups/manual-2026-10-13.db
```

The script uses SQLite's backup API, checks integrity and foreign keys, records
table counts and a SHA-256 manifest, and refuses to overwrite an existing
backup. To restore, stop the services, keep another verified copy of the current
database, then restore the chosen backup as a separate runtime database. Set
`SECURITY_DB` to its path when starting. GitHub protects source code and sanitized
evidence; it does **not** protect live application data or runtime credentials.

## Solo attribution and course requirements

All implementation and report sections belong to Abdulrahman Kobeissi's solo
project. No teammate contributions or meeting attendance are claimed.
The supplied handout requests teams of three and includes CREATES attendance;
solo eligibility and the actual coaching session must be handled with the
course staff. The report discloses the use of OpenAI Codex for implementation,
test generation, documentation and report preparation. The handout prohibits
submitting a complete AI-generated solution as the student's own work; this
package requires the student's review, understanding and instructor-approved
use before submission. Nothing has been submitted to Moodle.

## References

- Supplied course brief, `Final Project Fall 2026-2027-Sprint 1.docx`.
- Earlier local Lab 1, Lab 3, Lab 4 and Lab 5 materials for Flask, OOP,
  SQLite, documentation, Postman and Git workflow conventions.
- Flask documentation: https://flask.palletsprojects.com/en/stable/quickstart/
- Python sqlite3 documentation: https://docs.python.org/3/library/sqlite3.html
- Werkzeug security helpers: https://werkzeug.palletsprojects.com/en/stable/utils/
- Postman Collection Runner: https://learning.postman.com/docs/tests-and-scripts/running-collections/intro-to-collection-runs/
