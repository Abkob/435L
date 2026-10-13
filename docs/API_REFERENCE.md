# API reference

Responsible student: Abdulrahman Kobeissi.

All examples below come from the live HTTP verification. Passwords and tokens are redacted. Request and response fields are JSON; protected calls require `Authorization: Bearer <token>`. List endpoints return arrays, single-resource endpoints return objects, both wrapped in `{ "status": "success", "data": ... }`. Error envelopes include `status`, `message` and `request_id`.

## POST /Abdulrahman-Kobeissi/users/register

Register an account.

Service: users; base URL: http://127.0.0.1:5101.

Owner: Abdulrahman Kobeissi. Public registration is restricted to active employees; login verifies credentials.

Request fields: full_name, username, email, password, department, role.
Required fields: full_name, username, email, password, department, role.

```json
{
  "full_name": "Demo Analyst",
  "username": "r1791896720766f_analyst",
  "email": "r1791896720766f_analyst@example.test",
  "password": "[REDACTED]",
  "department": "Security",
  "role": "Security Analyst"
}
```

HTTP 201: Record created.

```json
{
  "data": {
    "account_status": "Active",
    "created_at": "2026-10-13T13:05:23.479865+00:00",
    "department": "Security",
    "email": "r1791896720766f_analyst@example.test",
    "full_name": "Demo Analyst",
    "id": 2,
    "last_login_at": null,
    "role": "Security Analyst",
    "username": "r1791896720766f_analyst"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## POST /Abdulrahman-Kobeissi/users/login

Administrator login.

Service: users; base URL: http://127.0.0.1:5101.

Owner: Abdulrahman Kobeissi. Public registration is restricted to active employees; login verifies credentials.

Request fields: login, password.
Required fields: login, password.

```json
{
  "login": "admin",
  "password": "[REDACTED]"
}
```

HTTP 200: Successful read or update.

```json
{
  "data": {
    "expires_at": "2026-10-13T14:05:21.785131+00:00",
    "token": "[REDACTED]",
    "token_type": "Bearer",
    "user": {
      "account_status": "Active",
      "created_at": "2026-10-13T13:01:10.347584+00:00",
      "department": "Security",
      "email": "admin@example.test",
      "full_name": "Abdulrahman Kobeissi",
      "id": 1,
      "last_login_at": "2026-10-13T13:05:21.786131+00:00",
      "role": "Security Administrator",
      "username": "admin"
    }
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 429: Login rate limit.

HTTP 503: Required service unavailable.

## POST /Abdulrahman-Kobeissi/users/logout

Employee logout.

Service: users; base URL: http://127.0.0.1:5101.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Regular Employee/User, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": {
    "message": "Session revoked"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/users

List users.

Service: users; base URL: http://127.0.0.1:5101.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "account_status": "Active",
      "created_at": "2026-10-13T13:01:10.347584+00:00",
      "department": "Security",
      "email": "admin@example.test",
      "full_name": "Abdulrahman Kobeissi",
      "id": 1,
      "last_login_at": "2026-10-13T13:05:21.786131+00:00",
      "role": "Security Administrator",
      "username": "admin"
    },
    {
      "account_status": "Active",
      "created_at": "2026-10-13T13:05:23.479865+00:00",
      "department": "Security",
      "email": "r1791896720766f_analyst@example.test",
      "full_name": "Demo Analyst",
      "id": 2,
      "last_login_at": "2026-10-13T13:05:24.280001+00:00",
      "role": "Security Analyst",
      "username": "r1791896720766f_analyst"
    },
    {
      "account_status": "Active",
      "created_at": "2026-10-13T13:05:25.102120+00:00",
      "department": "IT",
      "email": "r1791896720766f_employee@example.test",
      "full_name": "Demo Employee Updated",
      "id": 3,
      "last_login_at": "2026-10-13T13:05:25.939455+00:00",
      "role": "Regular Employee/User",
      "username": "r1791896720766f_employee"
    },
    {
      "account_status": "Active",
      "created_at": "2026-10-13T13:05:26.731688+00:00",
      "department": "Operations",
      "email": "r1791896720766f_auditor@example.test",
      "full_name": "Demo Auditor",
      "id": 4,
      "last_login_at": "2026-10-13T13:05:27.649768+00:00",
      "role": "Auditor",
      "username": "r1791896720766f_auditor"
    },
    {
      "account_status": "Active",
      "created_at": "2026-10-13T13:05:28.537120+00:00",
      "department": "Operations",
      "email": "r1791896720766f_other@example.test",
      "full_name": "Demo Other",
      "id": 5,
      "last_login_at": "2026-10-13T13:05:29.354724+00:00",
      "role": "Regular Employee/User",
      "username": "r1791896720766f_other"
    },
    {
      "account_status": "Active",
      "created_at": "2026-10-13T13:05:30.223006+00:00",
      "department": "Operations",
      "email": "r1791896720766f_spare@example.test",
      "full_name": "Demo Spare",
      "id": 6,
      "last_login_at": "2026-10-13T13:05:31.015713+00:00",
      "role": "Regular Employee/User",
      "username": "r1791896720766f_spare"
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/users/{username}

Retrieve own profile.

Service: users; base URL: http://127.0.0.1:5101.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor, Regular Employee/User.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| username | path | True | Username to retrieve |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "account_status": "Active",
    "created_at": "2026-10-13T13:05:25.102120+00:00",
    "department": "IT",
    "email": "r1791896720766f_employee@example.test",
    "full_name": "Demo Employee Updated",
    "id": 3,
    "last_login_at": "2026-10-13T13:05:25.939455+00:00",
    "role": "Regular Employee/User",
    "username": "r1791896720766f_employee"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## PUT /Abdulrahman-Kobeissi/users/{user_id}

Update own profile.

Service: users; base URL: http://127.0.0.1:5101.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Regular Employee/User.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| user_id | path | True | Positive record identifier |

Request fields: full_name, department, email.
Required fields: at least one permitted update field.

```json
{
  "full_name": "Demo Employee Updated",
  "department": "IT"
}
```

HTTP 200: Successful read or update.

```json
{
  "data": {
    "account_status": "Active",
    "created_at": "2026-10-13T13:05:25.102120+00:00",
    "department": "IT",
    "email": "r1791896720766f_employee@example.test",
    "full_name": "Demo Employee Updated",
    "id": 3,
    "last_login_at": "2026-10-13T13:05:25.939455+00:00",
    "role": "Regular Employee/User",
    "username": "r1791896720766f_employee"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## DELETE /Abdulrahman-Kobeissi/users/{user_id}

Delete spare account.

Service: users; base URL: http://127.0.0.1:5101.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| user_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "deleted": true,
    "id": 6
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## DELETE /Abdulrahman-Kobeissi/users/{user_id}/role

Remove elevated role.

Service: users; base URL: http://127.0.0.1:5101.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| user_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "account_status": "Active",
    "created_at": "2026-10-13T13:05:30.223006+00:00",
    "department": "Operations",
    "email": "r1791896720766f_spare@example.test",
    "full_name": "Demo Spare",
    "id": 6,
    "last_login_at": "2026-10-13T13:05:31.015713+00:00",
    "role": "Regular Employee/User",
    "username": "r1791896720766f_spare"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## PUT /Abdulrahman-Kobeissi/users/{user_id}/role

Assign Auditor role.

Service: users; base URL: http://127.0.0.1:5101.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| user_id | path | True | Positive record identifier |

Request fields: role.
Required fields: role.

```json
{
  "role": "Auditor"
}
```

HTTP 200: Successful read or update.

```json
{
  "data": {
    "account_status": "Active",
    "created_at": "2026-10-13T13:05:30.223006+00:00",
    "department": "Operations",
    "email": "r1791896720766f_spare@example.test",
    "full_name": "Demo Spare",
    "id": 6,
    "last_login_at": "2026-10-13T13:05:31.015713+00:00",
    "role": "Auditor",
    "username": "r1791896720766f_spare"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## PUT /Abdulrahman-Kobeissi/users/{user_id}/status

Suspend account.

Service: users; base URL: http://127.0.0.1:5101.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| user_id | path | True | Positive record identifier |

Request fields: account_status.
Required fields: account_status.

```json
{
  "account_status": "Suspended"
}
```

HTTP 200: Successful read or update.

```json
{
  "data": {
    "account_status": "Suspended",
    "created_at": "2026-10-13T13:05:30.223006+00:00",
    "department": "Operations",
    "email": "r1791896720766f_spare@example.test",
    "full_name": "Demo Spare",
    "id": 6,
    "last_login_at": "2026-10-13T13:05:31.015713+00:00",
    "role": "Regular Employee/User",
    "username": "r1791896720766f_spare"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/users/permissions

Role and permission catalog.

Service: users; base URL: http://127.0.0.1:5101.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": {
    "Auditor": "Read-only inspection and report generation",
    "Regular Employee/User": "Own profile, incident reporting and own notifications",
    "Security Administrator": "Platform administration and all services",
    "Security Analyst": "Assigned investigations, related assets, threat and vulnerability review, own notifications and playbook actions"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## POST /Abdulrahman-Kobeissi/assets

Create server.

Service: assets; base URL: http://127.0.0.1:5102.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

Request fields: name, asset_type, ip_address, department, owner_id, criticality, operating_system, location, status.
Required fields: name, asset_type, ip_address, department, owner_id, criticality.

```json
{
  "name": "r1791896720766f Server",
  "asset_type": "Server",
  "ip_address": "192.0.2.11",
  "department": "IT",
  "owner_id": 3,
  "criticality": "Critical",
  "operating_system": "Linux",
  "location": "Lab",
  "status": "Active"
}
```

HTTP 201: Record created.

```json
{
  "data": {
    "asset_type": "Server",
    "created_at": "2026-10-13T13:05:34.505479+00:00",
    "criticality": "Critical",
    "department": "IT",
    "id": 1,
    "ip_address": "192.0.2.11",
    "location": "Lab",
    "name": "r1791896720766f Server",
    "operating_system": "Linux",
    "owner_id": 3,
    "status": "Active"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## PUT /Abdulrahman-Kobeissi/assets/{asset_id}

Update asset.

Service: assets; base URL: http://127.0.0.1:5102.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| asset_id | path | True | Positive record identifier |

Request fields: name, status, asset_type, ip_address, operating_system, department, owner_id, location, criticality.
Required fields: at least one permitted update field.

```json
{
  "name": "r1791896720766f Protected Server",
  "status": "Under Maintenance"
}
```

HTTP 200: Successful read or update.

```json
{
  "data": {
    "asset_type": "Server",
    "created_at": "2026-10-13T13:05:34.505479+00:00",
    "criticality": "Critical",
    "department": "IT",
    "id": 1,
    "ip_address": "192.0.2.11",
    "location": "Lab",
    "name": "r1791896720766f Protected Server",
    "operating_system": "Linux",
    "owner_id": 3,
    "status": "Under Maintenance"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## DELETE /Abdulrahman-Kobeissi/assets/{asset_id}

Delete unreferenced asset.

Service: assets; base URL: http://127.0.0.1:5102.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| asset_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "deleted": true,
    "id": 3
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/assets

List assets.

Service: assets; base URL: http://127.0.0.1:5102.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "asset_type": "Server",
      "created_at": "2026-10-13T13:05:34.505479+00:00",
      "criticality": "Critical",
      "department": "IT",
      "id": 1,
      "ip_address": "192.0.2.11",
      "location": "Lab",
      "name": "r1791896720766f Protected Server",
      "operating_system": "Linux",
      "owner_id": 3,
      "status": "Under Maintenance"
    },
    {
      "asset_type": "Workstation",
      "created_at": "2026-10-13T13:05:34.636097+00:00",
      "criticality": "Medium",
      "department": "IT",
      "id": 2,
      "ip_address": "192.0.2.12",
      "location": "Lab",
      "name": "r1791896720766f Workstation",
      "operating_system": "Linux",
      "owner_id": 3,
      "status": "Active"
    },
    {
      "asset_type": "Application",
      "created_at": "2026-10-13T13:05:34.719666+00:00",
      "criticality": "Low",
      "department": "IT",
      "id": 3,
      "ip_address": "192.0.2.13",
      "location": "Lab",
      "name": "r1791896720766f Application",
      "operating_system": "Linux",
      "owner_id": 3,
      "status": "Active"
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/assets/search

Search assets by name.

Service: assets; base URL: http://127.0.0.1:5102.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor, Security Analyst.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| name | query | False | Name. |
| asset_type | query | False | Asset type. |
| ip_address | query | False | Ip address. |
| department | query | False | Department. |
| criticality | query | False | Criticality. |

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "asset_type": "Server",
      "created_at": "2026-10-13T13:05:34.505479+00:00",
      "criticality": "Critical",
      "department": "IT",
      "id": 1,
      "ip_address": "192.0.2.11",
      "location": "Lab",
      "name": "r1791896720766f Protected Server",
      "operating_system": "Linux",
      "owner_id": 3,
      "status": "Under Maintenance"
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/assets/{asset_id}

Asset before update.

Service: assets; base URL: http://127.0.0.1:5102.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor, Security Analyst.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| asset_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "asset_type": "Server",
    "created_at": "2026-10-13T13:05:34.505479+00:00",
    "criticality": "Critical",
    "department": "IT",
    "id": 1,
    "incident_ids": [],
    "ip_address": "192.0.2.11",
    "location": "Lab",
    "name": "r1791896720766f Server",
    "operating_system": "Linux",
    "owner_id": 3,
    "status": "Active",
    "vulnerability_ids": []
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/assets/{asset_id}/history

Asset change history.

Service: assets; base URL: http://127.0.0.1:5102.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| asset_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "actor_id": 1,
      "after_json": "{\"id\": 1, \"name\": \"r1791896720766f Server\", \"asset_type\": \"Server\", \"ip_address\": \"192.0.2.11\", \"operating_system\": \"Linux\", \"department\": \"IT\", \"owner_id\": 3, \"location\": \"Lab\", \"criticality\": \"Critical\", \"status\": \"Active\", \"created_at\": \"2026-10-13T13:05:34.505479+00:00\"}",
      "asset_id": 1,
      "before_json": null,
      "created_at": "2026-10-13T13:05:34.522485+00:00",
      "id": 1,
      "operation": "created"
    },
    {
      "actor_id": 1,
      "after_json": "{\"id\": 1, \"name\": \"r1791896720766f Protected Server\", \"asset_type\": \"Server\", \"ip_address\": \"192.0.2.11\", \"operating_system\": \"Linux\", \"department\": \"IT\", \"owner_id\": 3, \"location\": \"Lab\", \"criticality\": \"Critical\", \"status\": \"Under Maintenance\", \"created_at\": \"2026-10-13T13:05:34.505479+00:00\"}",
      "asset_id": 1,
      "before_json": "{\"id\": 1, \"name\": \"r1791896720766f Server\", \"asset_type\": \"Server\", \"ip_address\": \"192.0.2.11\", \"operating_system\": \"Linux\", \"department\": \"IT\", \"owner_id\": 3, \"location\": \"Lab\", \"criticality\": \"Critical\", \"status\": \"Active\", \"created_at\": \"2026-10-13T13:05:34.505479+00:00\"}",
      "created_at": "2026-10-13T13:05:34.845813+00:00",
      "id": 4,
      "operation": "updated"
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## POST /Abdulrahman-Kobeissi/incidents

Report low incident.

Service: incidents; base URL: http://127.0.0.1:5103.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Regular Employee/User.

Request fields: title, description, category, severity, asset_id, reporter_id.
Required fields: title, description, category, severity, asset_id.

```json
{
  "title": "Low lab incident",
  "description": "Fictional controlled lab event for workflow verification.",
  "category": "Phishing",
  "severity": "Low",
  "asset_id": 1,
  "reporter_id": 3
}
```

HTTP 201: Record created.

```json
{
  "data": {
    "asset_id": 1,
    "assigned_analyst_id": null,
    "category": "Phishing",
    "created_at": "2026-10-13T13:05:35.535538+00:00",
    "description": "Fictional controlled lab event for workflow verification.",
    "id": 1,
    "reporter_id": 3,
    "resolution_date": null,
    "severity": "Low",
    "status": "Open",
    "title": "Low lab incident"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/incidents

List all incidents.

Service: incidents; base URL: http://127.0.0.1:5103.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Regular Employee/User, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "asset_id": 1,
      "assigned_analyst_id": null,
      "category": "Phishing",
      "created_at": "2026-10-13T13:05:35.535538+00:00",
      "description": "Fictional controlled lab event for workflow verification.",
      "id": 1,
      "reporter_id": 3,
      "resolution_date": null,
      "severity": "Low",
      "status": "Open",
      "title": "Low lab incident"
    },
    {
      "asset_id": 1,
      "assigned_analyst_id": null,
      "category": "Phishing",
      "created_at": "2026-10-13T13:05:35.623574+00:00",
      "description": "Fictional controlled lab event for workflow verification.",
      "id": 2,
      "reporter_id": 3,
      "resolution_date": null,
      "severity": "Medium",
      "status": "Open",
      "title": "Medium lab incident"
    },
    {
      "asset_id": 1,
      "assigned_analyst_id": null,
      "category": "Phishing",
      "created_at": "2026-10-13T13:05:35.690111+00:00",
      "description": "Fictional controlled lab event for workflow verification.",
      "id": 3,
      "reporter_id": 3,
      "resolution_date": null,
      "severity": "High",
      "status": "Open",
      "title": "High lab incident"
    },
    {
      "asset_id": 1,
      "assigned_analyst_id": null,
      "category": "Phishing",
      "created_at": "2026-10-13T13:05:35.814366+00:00",
      "description": "Fictional controlled lab event for workflow verification.",
      "id": 4,
      "reporter_id": 3,
      "resolution_date": null,
      "severity": "Critical",
      "status": "Open",
      "title": "Critical lab incident"
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/incidents/{incident_id}

Retrieve incident with notes.

Service: incidents; base URL: http://127.0.0.1:5103.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Regular Employee/User, Auditor.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| incident_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "asset_id": 1,
    "assigned_analyst_id": 2,
    "category": "Phishing",
    "created_at": "2026-10-13T13:05:35.535538+00:00",
    "description": "Fictional controlled lab event for workflow verification.",
    "id": 1,
    "notes": [
      {
        "analyst_id": 2,
        "content": "Reviewed the lab message headers and isolated the affected test account.",
        "created_at": "2026-10-13T13:05:36.688336+00:00",
        "id": 1,
        "incident_id": 1
      }
    ],
    "reporter_id": 3,
    "resolution_date": null,
    "severity": "Low",
    "status": "Open",
    "title": "Low lab incident"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## PUT /Abdulrahman-Kobeissi/incidents/{incident_id}/assign

Assign analyst.

Service: incidents; base URL: http://127.0.0.1:5103.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| incident_id | path | True | Positive record identifier |

Request fields: analyst_id.
Required fields: analyst_id.

```json
{
  "analyst_id": 2
}
```

HTTP 200: Successful read or update.

```json
{
  "data": {
    "asset_id": 1,
    "assigned_analyst_id": 2,
    "category": "Phishing",
    "created_at": "2026-10-13T13:05:35.535538+00:00",
    "description": "Fictional controlled lab event for workflow verification.",
    "id": 1,
    "reporter_id": 3,
    "resolution_date": null,
    "severity": "Low",
    "status": "Open",
    "title": "Low lab incident"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## PUT /Abdulrahman-Kobeissi/incidents/{incident_id}/status

Incident becomes Under Investigation.

Service: incidents; base URL: http://127.0.0.1:5103.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| incident_id | path | True | Positive record identifier |

Request fields: status.
Required fields: status.

```json
{
  "status": "Under Investigation"
}
```

HTTP 200: Successful read or update.

```json
{
  "data": {
    "asset_id": 1,
    "assigned_analyst_id": 2,
    "category": "Phishing",
    "created_at": "2026-10-13T13:05:35.535538+00:00",
    "description": "Fictional controlled lab event for workflow verification.",
    "id": 1,
    "reporter_id": 3,
    "resolution_date": null,
    "severity": "Low",
    "status": "Under Investigation",
    "title": "Low lab incident"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## POST /Abdulrahman-Kobeissi/incidents/{incident_id}/notes

Investigation note.

Service: incidents; base URL: http://127.0.0.1:5103.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| incident_id | path | True | Positive record identifier |

Request fields: content.
Required fields: content.

```json
{
  "content": "Reviewed the lab message headers and isolated the affected test account."
}
```

HTTP 201: Record created.

```json
{
  "data": {
    "analyst_id": 2,
    "content": "Reviewed the lab message headers and isolated the affected test account.",
    "created_at": "2026-10-13T13:05:36.688336+00:00",
    "id": 1,
    "incident_id": 1
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## POST /Abdulrahman-Kobeissi/threats

Create IP Address indicator.

Service: threats; base URL: http://127.0.0.1:5104.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

Request fields: threat_type, value, description, severity, source.
Required fields: threat_type, value, description, severity, source.

```json
{
  "threat_type": "IP Address",
  "value": "198.18.147.64",
  "description": "Fictional test indicator; not external threat intelligence.",
  "severity": "High",
  "source": "Local lab"
}
```

HTTP 201: Record created.

```json
{
  "data": {
    "created_at": "2026-10-13T13:05:37.433214+00:00",
    "description": "Fictional test indicator; not external threat intelligence.",
    "id": 1,
    "severity": "High",
    "source": "Local lab",
    "threat_type": "IP Address",
    "value": "198.18.147.64"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/threats

List threat indicators.

Service: threats; base URL: http://127.0.0.1:5104.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "created_at": "2026-10-13T13:05:37.433214+00:00",
      "description": "Fictional test indicator; not external threat intelligence.",
      "id": 1,
      "severity": "High",
      "source": "Local lab",
      "threat_type": "IP Address",
      "value": "198.18.147.64"
    },
    {
      "created_at": "2026-10-13T13:05:37.499042+00:00",
      "description": "Fictional test indicator; not external threat intelligence.",
      "id": 2,
      "severity": "Medium",
      "source": "Local lab",
      "threat_type": "Domain",
      "value": "r1791896720766f.example.test"
    },
    {
      "created_at": "2026-10-13T13:05:37.558370+00:00",
      "description": "Fictional test indicator; not external threat intelligence.",
      "id": 3,
      "severity": "Critical",
      "source": "Local lab",
      "threat_type": "File Hash",
      "value": "e559a91630a369db323fa89a75bbcdc5b881206806cffae82ac632a37360c15d"
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/threats/search

Search threats by threat_type.

Service: threats; base URL: http://127.0.0.1:5104.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Auditor.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| threat_type | query | False | Threat type. |
| value | query | False | Indicator value; type-specific IP, domain or hexadecimal hash validation. |
| severity | query | False | Severity. |
| source | query | False | Source. |

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "created_at": "2026-10-13T13:05:37.499042+00:00",
      "description": "Fictional test indicator; not external threat intelligence.",
      "id": 2,
      "severity": "Medium",
      "source": "Local lab",
      "threat_type": "Domain",
      "value": "r1791896720766f.example.test"
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/threats/{record_id}

Threat before update.

Service: threats; base URL: http://127.0.0.1:5104.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Auditor.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| record_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "created_at": "2026-10-13T13:05:37.433214+00:00",
    "description": "Fictional test indicator; not external threat intelligence.",
    "id": 1,
    "severity": "High",
    "source": "Local lab",
    "threat_type": "IP Address",
    "value": "198.18.147.64"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## PUT /Abdulrahman-Kobeissi/threats/{record_id}

Update threat information.

Service: threats; base URL: http://127.0.0.1:5104.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| record_id | path | True | Positive record identifier |

Request fields: severity, description, source.
Required fields: at least one permitted update field.

```json
{
  "severity": "Critical",
  "description": "Escalated lab indicator",
  "source": "Lab review"
}
```

HTTP 200: Successful read or update.

```json
{
  "data": {
    "created_at": "2026-10-13T13:05:37.433214+00:00",
    "description": "Escalated lab indicator",
    "id": 1,
    "severity": "Critical",
    "source": "Lab review",
    "threat_type": "IP Address",
    "value": "198.18.147.64"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## DELETE /Abdulrahman-Kobeissi/threats/{record_id}

Delete threat.

Service: threats; base URL: http://127.0.0.1:5104.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| record_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "deleted": true,
    "id": 3
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## POST /Abdulrahman-Kobeissi/logs

Create manual audit log 1.

Service: logs; base URL: http://127.0.0.1:5105.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

Request fields: user_id, action, description, severity, related_service.
Required fields: user_id, action, description, severity, related_service.

```json
{
  "user_id": 1,
  "action": "lab.review",
  "description": "Manual verification event",
  "severity": "Information",
  "related_service": "logs"
}
```

HTTP 201: Record created.

```json
{
  "data": {
    "action": "lab.review",
    "created_at": "2026-10-13T13:05:44.357044+00:00",
    "description": "Manual verification event",
    "event_id": null,
    "id": 78,
    "related_service": "logs",
    "severity": "Information",
    "user_id": 1
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/logs

List automatic and manual logs.

Service: logs; base URL: http://127.0.0.1:5105.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "action": "login.succeeded",
      "created_at": "2026-10-13T13:05:21.786131+00:00",
      "description": "User authenticated",
      "event_id": "4b5eb803-89c3-4b5f-b8a8-09d87190f83d",
      "id": 1,
      "related_service": "users",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "login.failed",
      "created_at": "2026-10-13T13:05:22.628338+00:00",
      "description": "Unsuccessful authentication",
      "event_id": "48930507-ec37-40c2-bb61-01a83a1fffaa",
      "id": 2,
      "related_service": "users",
      "severity": "Warning",
      "user_id": 1
    },
    {
      "action": "user.created",
      "created_at": "2026-10-13T13:05:23.482844+00:00",
      "description": "Created account r1791896720766f_analyst",
      "event_id": "0b6c4568-6be3-4407-93b6-8f2a5b2c5a2f",
      "id": 3,
      "related_service": "users",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "login.succeeded",
      "created_at": "2026-10-13T13:05:24.280001+00:00",
      "description": "User authenticated",
      "event_id": "16480150-bf77-4656-84ed-8948ad287c72",
      "id": 4,
      "related_service": "users",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "user.created",
      "created_at": "2026-10-13T13:05:25.105630+00:00",
      "description": "Created account r1791896720766f_employee",
      "event_id": "c2e858c0-f3e0-4df9-8ba8-45769e3aacb1",
      "id": 5,
      "related_service": "users",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "login.succeeded",
      "created_at": "2026-10-13T13:05:25.939455+00:00",
      "description": "User authenticated",
      "event_id": "7e946266-24f0-441c-aac2-ac3cccbcb515",
      "id": 6,
      "related_service": "users",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "user.created",
      "created_at": "2026-10-13T13:05:26.735688+00:00",
      "description": "Created account r1791896720766f_auditor",
      "event_id": "65b840ab-66df-4ef2-98a1-a08cc088e416",
      "id": 7,
      "related_service": "users",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "login.succeeded",
      "created_at": "2026-10-13T13:05:27.649768+00:00",
      "description": "User authenticated",
      "event_id": "8d9721ab-726c-4d0c-ac8a-bcc07188f922",
      "id": 8,
      "related_service": "users",
      "severity": "Information",
      "user_id": 4
    },
    {
      "action": "user.created",
      "created_at": "2026-10-13T13:05:28.540121+00:00",
      "description": "Created account r1791896720766f_other",
      "event_id": "cd251649-4b9d-4fa7-a638-e25574d1cba7",
      "id": 9,
      "related_service": "users",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "login.succeeded",
      "created_at": "2026-10-13T13:05:29.354724+00:00",
      "description": "User authenticated",
      "event_id": "dfc1675d-68ed-49bb-aede-6d2728f2a9d2",
      "id": 10,
      "related_service": "users",
      "severity": "Information",
      "user_id": 5
    },
    {
      "action": "user.created",
      "created_at": "2026-10-13T13:05:30.226007+00:00",
      "description": "Created account r1791896720766f_spare",
      "event_id": "120bfe84-da9c-4e30-8b53-ac77e9e6d8a3",
      "id": 11,
      "related_service": "users",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "login.succeeded",
      "created_at": "2026-10-13T13:05:31.015713+00:00",
      "description": "User authenticated",
      "event_id": "c68fa220-c71c-45e5-a5b6-0abe74ef3f16",
      "id": 12,
      "related_service": "users",
      "severity": "Information",
      "user_id": 6
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:31.985463+00:00",
      "description": "POST /Abdulrahman-Kobeissi/users/register: Self-registration can only create an active Regular Employee/User",
      "event_id": "22b1f2e0-7721-4def-abd7-8792e5758b47",
      "id": 13,
      "related_service": "users",
      "severity": "Warning",
      "user_id": null
    },
    {
      "action": "user.updated",
      "created_at": "2026-10-13T13:05:32.133073+00:00",
      "description": "user.updated: record 3",
      "event_id": "f1b0c6e8-7190-48f4-aa5d-42ca7a4a369f",
      "id": 14,
      "related_service": "users",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:32.194048+00:00",
      "description": "GET /Abdulrahman-Kobeissi/users/r1791896720766f_employee: You can only access your own profile",
      "event_id": "ebd0acef-d483-4867-b2b1-3ae8b7f380fd",
      "id": 15,
      "related_service": "users",
      "severity": "Warning",
      "user_id": 5
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:32.331706+00:00",
      "description": "GET /Abdulrahman-Kobeissi/users: Your role does not permit this operation",
      "event_id": "98a632d1-1a14-47e4-a6bd-80ac8e784ac7",
      "id": 16,
      "related_service": "users",
      "severity": "Warning",
      "user_id": 2
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:32.379378+00:00",
      "description": "GET /Abdulrahman-Kobeissi/users: A valid bearer token is required",
      "event_id": "cf3a2af9-d757-4a77-b6e9-463891021b79",
      "id": 17,
      "related_service": "users",
      "severity": "Warning",
      "user_id": null
    },
    {
      "action": "role.changed",
      "created_at": "2026-10-13T13:05:32.422257+00:00",
      "description": "role.changed: record 6",
      "event_id": "0b34f740-d325-472a-8313-c480590268a7",
      "id": 18,
      "related_service": "users",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:32.478311+00:00",
      "description": "GET /Abdulrahman-Kobeissi/users: Invalid, expired or revoked session",
      "event_id": "a5255016-6000-46e1-9133-e23ca04570ab",
      "id": 19,
      "related_service": "users",
      "severity": "Warning",
      "user_id": null
    },
    {
      "action": "role.changed",
      "created_at": "2026-10-13T13:05:32.513139+00:00",
      "description": "role.changed: record 6",
      "event_id": "3dce0f78-e8ab-4bee-b3af-0c261e2e2685",
      "id": 20,
      "related_service": "users",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "user.status_changed",
      "created_at": "2026-10-13T13:05:32.555279+00:00",
      "description": "user.status_changed: record 6",
      "event_id": "60249a1d-c29d-4454-aad0-8139f95e932b",
      "id": 21,
      "related_service": "users",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "login.failed",
      "created_at": "2026-10-13T13:05:33.390758+00:00",
      "description": "Unsuccessful authentication",
      "event_id": "e7b6528c-e524-48b7-b12e-1c94f1598a0b",
      "id": 22,
      "related_service": "users",
      "severity": "Warning",
      "user_id": 6
    },
    {
      "action": "user.status_changed",
      "created_at": "2026-10-13T13:05:33.419283+00:00",
      "description": "user.status_changed: record 6",
      "event_id": "5ef3461a-41a5-479b-94b9-d9a14c4c303b",
      "id": 23,
      "related_service": "users",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "login.failed",
      "created_at": "2026-10-13T13:05:34.226098+00:00",
      "description": "Unsuccessful authentication",
      "event_id": "3f6cbcf2-03bd-48a2-95f3-a105a6d8377c",
      "id": 24,
      "related_service": "users",
      "severity": "Warning",
      "user_id": 6
    },
    {
      "action": "user.status_changed",
      "created_at": "2026-10-13T13:05:34.267181+00:00",
      "description": "user.status_changed: record 6",
      "event_id": "bdbcb0b2-3ecd-40a8-924d-29c7c43ef1e8",
      "id": 25,
      "related_service": "users",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:34.323696+00:00",
      "description": "DELETE /Abdulrahman-Kobeissi/users/6: Your role does not permit this operation",
      "event_id": "b50e4636-bddc-4945-843d-9cb7b536ea8d",
      "id": 26,
      "related_service": "users",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "user.deleted",
      "created_at": "2026-10-13T13:05:34.353241+00:00",
      "description": "user.deleted: record 6",
      "event_id": "bd890687-fa49-4b9f-a8e5-3fec0fb5e86c",
      "id": 27,
      "related_service": "users",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "asset.created",
      "created_at": "2026-10-13T13:05:34.522485+00:00",
      "description": "asset.created: record 1",
      "event_id": "bf1e0268-56de-45b3-b5d4-d872c99c4b20",
      "id": 28,
      "related_service": "assets",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "asset.created",
      "created_at": "2026-10-13T13:05:34.639098+00:00",
      "description": "asset.created: record 2",
      "event_id": "575691af-ffe9-41c4-9785-538fed3cfd1f",
      "id": 29,
      "related_service": "assets",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "asset.created",
      "created_at": "2026-10-13T13:05:34.735206+00:00",
      "description": "asset.created: record 3",
      "event_id": "a5c2e4a1-92d7-4f9b-a2ac-24d704ad948c",
      "id": 30,
      "related_service": "assets",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "asset.updated",
      "created_at": "2026-10-13T13:05:34.845813+00:00",
      "description": "asset.updated: record 1",
      "event_id": "8ccae3de-22c1-4647-9807-14f92a0170db",
      "id": 31,
      "related_service": "assets",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:35.267279+00:00",
      "description": "DELETE /Abdulrahman-Kobeissi/assets/3: Your role does not permit this operation",
      "event_id": "f7916c0f-e30c-4b30-8140-6071d377529a",
      "id": 32,
      "related_service": "assets",
      "severity": "Warning",
      "user_id": 2
    },
    {
      "action": "asset.deleted",
      "created_at": "2026-10-13T13:05:35.334352+00:00",
      "description": "asset.deleted: record 3",
      "event_id": "886b303b-ba23-4810-b694-1456b2d2ef80",
      "id": 33,
      "related_service": "assets",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "incident.created",
      "created_at": "2026-10-13T13:05:35.539501+00:00",
      "description": "incident.created: record 1",
      "event_id": "e68d188c-1c56-40cf-84cc-ce7e488da26c",
      "id": 34,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "incident.created",
      "created_at": "2026-10-13T13:05:35.625573+00:00",
      "description": "incident.created: record 2",
      "event_id": "fe15b318-f33c-4bb3-915f-b332e77414e9",
      "id": 35,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:35.446433+00:00",
      "description": "GET /Abdulrahman-Kobeissi/assets: Your role does not permit this operation",
      "event_id": "f23e2161-30e1-4ca0-a6bb-386389ba5a4a",
      "id": 36,
      "related_service": "assets",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:36.475139+00:00",
      "description": "GET /Abdulrahman-Kobeissi/assets/2: Asset is not related to your assigned incidents",
      "event_id": "36c801d2-1adb-4f98-930d-92e9da48b4eb",
      "id": 37,
      "related_service": "assets",
      "severity": "Warning",
      "user_id": 2
    },
    {
      "action": "incident.created",
      "created_at": "2026-10-13T13:05:35.693113+00:00",
      "description": "incident.created: record 3",
      "event_id": "68631eab-598b-431a-957d-fd20f990c055",
      "id": 38,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "incident.created",
      "created_at": "2026-10-13T13:05:35.818372+00:00",
      "description": "incident.created: record 4",
      "event_id": "8de64d2a-fb17-4c11-87e4-57d77e213424",
      "id": 39,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:35.981833+00:00",
      "description": "GET /Abdulrahman-Kobeissi/incidents/1: You can only view incidents you reported",
      "event_id": "cee4327f-cb4b-4c2f-ad4c-d76f7584eb1a",
      "id": 40,
      "related_service": "incidents",
      "severity": "Warning",
      "user_id": 5
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:36.034865+00:00",
      "description": "GET /Abdulrahman-Kobeissi/incidents/1: Incident is not assigned to you",
      "event_id": "8953ec7a-d19f-49bd-8a36-4f27552c91e3",
      "id": 41,
      "related_service": "incidents",
      "severity": "Warning",
      "user_id": 2
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:36.127425+00:00",
      "description": "PUT /Abdulrahman-Kobeissi/incidents/1/assign: Your role does not permit this operation",
      "event_id": "5f488df8-2d4a-4425-8184-a83aca6cb840",
      "id": 42,
      "related_service": "incidents",
      "severity": "Warning",
      "user_id": 2
    },
    {
      "action": "incident.assigned",
      "created_at": "2026-10-13T13:05:36.301158+00:00",
      "description": "incident.assigned: record 1",
      "event_id": "add1af83-a1ca-4060-9868-0689e39e1d9f",
      "id": 43,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "incident.note_added",
      "created_at": "2026-10-13T13:05:36.688336+00:00",
      "description": "incident.note_added: record 1",
      "event_id": "e47a8f4c-0693-4c82-a563-02e8c1b99d51",
      "id": 44,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "incident.status_changed",
      "created_at": "2026-10-13T13:05:36.831616+00:00",
      "description": "incident.status_changed: record 1",
      "event_id": "396d4f57-653f-4b0e-a564-9464659a5060",
      "id": 45,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "incident.status_changed",
      "created_at": "2026-10-13T13:05:36.958613+00:00",
      "description": "incident.status_changed: record 1",
      "event_id": "dec79da5-3d60-4f33-a626-7a67c7b06f2a",
      "id": 46,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "incident.status_changed",
      "created_at": "2026-10-13T13:05:37.066078+00:00",
      "description": "incident.status_changed: record 1",
      "event_id": "b1511f85-c302-4279-879f-cd1265421213",
      "id": 47,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "incident.status_changed",
      "created_at": "2026-10-13T13:05:37.175272+00:00",
      "description": "incident.status_changed: record 1",
      "event_id": "93c7bec9-0d76-4057-a103-47dee9507a08",
      "id": 48,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:37.275608+00:00",
      "description": "PUT /Abdulrahman-Kobeissi/incidents/2/status: Your role does not permit this operation",
      "event_id": "4634e8f0-1bab-48b3-8227-3e589596423f",
      "id": 49,
      "related_service": "incidents",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "threats.created",
      "created_at": "2026-10-13T13:05:37.437727+00:00",
      "description": "threats.created: record 1",
      "event_id": "1247eedf-1f27-4c9a-bdfc-3933f0317f1a",
      "id": 50,
      "related_service": "threats",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "threats.created",
      "created_at": "2026-10-13T13:05:37.502131+00:00",
      "description": "threats.created: record 2",
      "event_id": "d82c2ae5-37bf-48be-a5e2-940bece09dac",
      "id": 51,
      "related_service": "threats",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "threats.created",
      "created_at": "2026-10-13T13:05:37.561882+00:00",
      "description": "threats.created: record 3",
      "event_id": "efd283cf-d958-4ffc-be61-05611edf250a",
      "id": 52,
      "related_service": "threats",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "threats.updated",
      "created_at": "2026-10-13T13:05:37.859060+00:00",
      "description": "threats.updated: record 1",
      "event_id": "6b9c2d95-55db-457f-a8ed-bc601d6af60b",
      "id": 53,
      "related_service": "threats",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:38.471409+00:00",
      "description": "DELETE /Abdulrahman-Kobeissi/threats/3: Your role does not permit this operation",
      "event_id": "fe884bdb-9a59-479e-9e45-9c0e263d7cac",
      "id": 54,
      "related_service": "threats",
      "severity": "Warning",
      "user_id": 2
    },
    {
      "action": "threats.deleted",
      "created_at": "2026-10-13T13:05:38.545588+00:00",
      "description": "threats.deleted: record 3",
      "event_id": "48b72154-1611-4f12-831e-5614803716aa",
      "id": 55,
      "related_service": "threats",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:38.599648+00:00",
      "description": "GET /Abdulrahman-Kobeissi/threats: Your role does not permit this operation",
      "event_id": "0c6548dd-77d3-4463-862c-5a632f01a763",
      "id": 56,
      "related_service": "threats",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "vulnerabilities.created",
      "created_at": "2026-10-13T13:05:38.672544+00:00",
      "description": "vulnerabilities.created: record 1",
      "event_id": "ad82b6ee-2fb0-47b5-93f7-561ed2d500d1",
      "id": 57,
      "related_service": "vulnerabilities",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "vulnerabilities.created",
      "created_at": "2026-10-13T13:05:38.765622+00:00",
      "description": "vulnerabilities.created: record 2",
      "event_id": "d47f6714-6475-4a69-bc42-4a65bcbfce4d",
      "id": 58,
      "related_service": "vulnerabilities",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "vulnerabilities.created",
      "created_at": "2026-10-13T13:05:38.862164+00:00",
      "description": "vulnerabilities.created: record 3",
      "event_id": "82d3b698-9dce-49ba-b276-0e14ef1abc6f",
      "id": 59,
      "related_service": "vulnerabilities",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "vulnerabilities.updated",
      "created_at": "2026-10-13T13:05:38.959248+00:00",
      "description": "vulnerabilities.updated: record 1",
      "event_id": "86712b4a-5b7e-488b-a09e-f7b5829a508a",
      "id": 60,
      "related_service": "vulnerabilities",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "vulnerabilities.updated",
      "created_at": "2026-10-13T13:05:39.070339+00:00",
      "description": "vulnerabilities.updated: record 1",
      "event_id": "5ed9979e-501b-4a53-8327-4488e5645825",
      "id": 61,
      "related_service": "vulnerabilities",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "vulnerabilities.updated",
      "created_at": "2026-10-13T13:05:39.165869+00:00",
      "description": "vulnerabilities.updated: record 1",
      "event_id": "320646e2-8006-4a36-a27d-58aa50eee554",
      "id": 62,
      "related_service": "vulnerabilities",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "vulnerabilities.updated",
      "created_at": "2026-10-13T13:05:39.263537+00:00",
      "description": "vulnerabilities.updated: record 1",
      "event_id": "9bcca9ed-4567-4b63-8f56-cfb4d95799b4",
      "id": 63,
      "related_service": "vulnerabilities",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "vulnerabilities.updated",
      "created_at": "2026-10-13T13:05:39.398226+00:00",
      "description": "vulnerabilities.updated: record 1",
      "event_id": "1272caa9-2445-4156-8962-63809dbc31b4",
      "id": 64,
      "related_service": "vulnerabilities",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:39.934290+00:00",
      "description": "DELETE /Abdulrahman-Kobeissi/vulnerabilities/3: Your role does not permit this operation",
      "event_id": "eb0968c4-92ec-4201-aedd-321a9e05d7f6",
      "id": 65,
      "related_service": "vulnerabilities",
      "severity": "Warning",
      "user_id": 2
    },
    {
      "action": "vulnerabilities.deleted",
      "created_at": "2026-10-13T13:05:39.987858+00:00",
      "description": "vulnerabilities.deleted: record 3",
      "event_id": "d8c9a655-77a9-43f3-938d-650d9b323413",
      "id": 66,
      "related_service": "vulnerabilities",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "notification.created",
      "created_at": "2026-10-13T13:05:40.052896+00:00",
      "description": "notification.created: record 15",
      "event_id": "36c681ad-5b4d-41c8-8860-b375fd53617b",
      "id": 67,
      "related_service": "notifications",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "notification.created",
      "created_at": "2026-10-13T13:05:40.147541+00:00",
      "description": "notification.created: record 16",
      "event_id": "5b9c6fd6-99af-4157-9b52-7c6eb44875ba",
      "id": 68,
      "related_service": "notifications",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "notification.read",
      "created_at": "2026-10-13T13:05:40.956007+00:00",
      "description": "notification.read: record 15",
      "event_id": "ee9a0b23-bc8b-485d-9b84-7f33bd93da33",
      "id": 69,
      "related_service": "notifications",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:41.394939+00:00",
      "description": "GET /Abdulrahman-Kobeissi/notifications/15: You can only access your own notifications",
      "event_id": "08437bbb-a4e3-48ee-97aa-46cd4faec53d",
      "id": 70,
      "related_service": "notifications",
      "severity": "Warning",
      "user_id": 5
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:42.252470+00:00",
      "description": "PUT /Abdulrahman-Kobeissi/notifications/15/read: Your role does not permit this operation",
      "event_id": "67dd7a13-145b-4d08-808a-b3a75858805f",
      "id": 71,
      "related_service": "notifications",
      "severity": "Warning",
      "user_id": 4
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:42.326035+00:00",
      "description": "DELETE /Abdulrahman-Kobeissi/notifications/16: Your role does not permit this operation",
      "event_id": "b260cf2b-423f-4aad-b35f-74c82051dcee",
      "id": 72,
      "related_service": "notifications",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "notification.deleted",
      "created_at": "2026-10-13T13:05:42.632037+00:00",
      "description": "notification.deleted: record 16",
      "event_id": "c09388c7-63f1-4733-b78f-b1f2f8dc9e15",
      "id": 73,
      "related_service": "notifications",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "playbook.created",
      "created_at": "2026-10-13T13:05:43.353803+00:00",
      "description": "playbook.created: record 1",
      "event_id": "f1c3c953-0f11-4cd9-b5c3-981d71c664bb",
      "id": 74,
      "related_service": "playbooks",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "playbook.created",
      "created_at": "2026-10-13T13:05:43.428394+00:00",
      "description": "playbook.created: record 2",
      "event_id": "72e7cb44-909a-4518-9b34-52e0a6851f43",
      "id": 75,
      "related_service": "playbooks",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "action.created",
      "created_at": "2026-10-13T13:05:43.565080+00:00",
      "description": "action.created: record 1",
      "event_id": "df17d6db-3cf4-4547-aa81-53c5ae483010",
      "id": 76,
      "related_service": "playbooks",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "action.created",
      "created_at": "2026-10-13T13:05:43.691680+00:00",
      "description": "action.created: record 2",
      "event_id": "5cb2220d-0d79-45ed-b123-30c2256323d5",
      "id": 77,
      "related_service": "playbooks",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "lab.review",
      "created_at": "2026-10-13T13:05:44.357044+00:00",
      "description": "Manual verification event",
      "event_id": null,
      "id": 78,
      "related_service": "logs",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "log.created",
      "created_at": "2026-10-13T13:05:44.363046+00:00",
      "description": "log.created: record 78",
      "event_id": "de79e9e5-38d5-4e0f-90c0-ed9536f1477f",
      "id": 79,
      "related_service": "logs",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "action.status_changed",
      "created_at": "2026-10-13T13:05:43.871353+00:00",
      "description": "action.status_changed: record 1",
      "event_id": "b758072a-67b3-410e-b711-03cb112caa1e",
      "id": 80,
      "related_service": "playbooks",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "action.status_changed",
      "created_at": "2026-10-13T13:05:43.955378+00:00",
      "description": "action.status_changed: record 1",
      "event_id": "81d22e05-ffe2-477f-90ab-d04397e32dbc",
      "id": 81,
      "related_service": "playbooks",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "action.status_changed",
      "created_at": "2026-10-13T13:05:44.021522+00:00",
      "description": "action.status_changed: record 2",
      "event_id": "36d3485f-ce39-4854-bb2d-8f2398400f40",
      "id": 82,
      "related_service": "playbooks",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "action.status_changed",
      "created_at": "2026-10-13T13:05:44.092196+00:00",
      "description": "action.status_changed: record 2",
      "event_id": "94139df1-697a-4740-86f5-c484c6edcda4",
      "id": 83,
      "related_service": "playbooks",
      "severity": "Information",
      "user_id": 2
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:44.229333+00:00",
      "description": "DELETE /Abdulrahman-Kobeissi/playbooks/2: Your role does not permit this operation",
      "event_id": "a688958e-94b7-4624-9c95-2fbbf8c4f6cb",
      "id": 84,
      "related_service": "playbooks",
      "severity": "Warning",
      "user_id": 2
    },
    {
      "action": "playbook.deleted",
      "created_at": "2026-10-13T13:05:44.265902+00:00",
      "description": "playbook.deleted: record 2",
      "event_id": "bdc99953-700a-46ae-a1e1-4a4b27b0da4f",
      "id": 85,
      "related_service": "playbooks",
      "severity": "Information",
      "user_id": 1
    },
    {
      "action": "lab.review",
      "created_at": "2026-10-13T13:05:44.995827+00:00",
      "description": "Manual verification event",
      "event_id": null,
      "id": 86,
      "related_service": "logs",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "log.created",
      "created_at": "2026-10-13T13:05:44.999817+00:00",
      "description": "log.created: record 86",
      "event_id": "6e877cc6-f3b9-4c04-ae69-b17e6c045b11",
      "id": 87,
      "related_service": "logs",
      "severity": "Information",
      "user_id": 1
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/logs/{record_id}

Retrieve audit record.

Service: logs; base URL: http://127.0.0.1:5105.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor, Security Analyst.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| record_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "action": "lab.review",
    "created_at": "2026-10-13T13:05:44.357044+00:00",
    "description": "Manual verification event",
    "event_id": null,
    "id": 78,
    "related_service": "logs",
    "severity": "Information",
    "user_id": 1
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/logs/search

Search logs by user_id.

Service: logs; base URL: http://127.0.0.1:5105.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor, Security Analyst.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| user_id | query | False | User id. |
| date | query | False | Date. |
| action | query | False | Action. |
| severity | query | False | Severity. |
| related_service | query | False | Related service. |

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "action": "login.succeeded",
      "created_at": "2026-10-13T13:05:25.939455+00:00",
      "description": "User authenticated",
      "event_id": "7e946266-24f0-441c-aac2-ac3cccbcb515",
      "id": 6,
      "related_service": "users",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "user.updated",
      "created_at": "2026-10-13T13:05:32.133073+00:00",
      "description": "user.updated: record 3",
      "event_id": "f1b0c6e8-7190-48f4-aa5d-42ca7a4a369f",
      "id": 14,
      "related_service": "users",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:34.323696+00:00",
      "description": "DELETE /Abdulrahman-Kobeissi/users/6: Your role does not permit this operation",
      "event_id": "b50e4636-bddc-4945-843d-9cb7b536ea8d",
      "id": 26,
      "related_service": "users",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "incident.created",
      "created_at": "2026-10-13T13:05:35.539501+00:00",
      "description": "incident.created: record 1",
      "event_id": "e68d188c-1c56-40cf-84cc-ce7e488da26c",
      "id": 34,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "incident.created",
      "created_at": "2026-10-13T13:05:35.625573+00:00",
      "description": "incident.created: record 2",
      "event_id": "fe15b318-f33c-4bb3-915f-b332e77414e9",
      "id": 35,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:35.446433+00:00",
      "description": "GET /Abdulrahman-Kobeissi/assets: Your role does not permit this operation",
      "event_id": "f23e2161-30e1-4ca0-a6bb-386389ba5a4a",
      "id": 36,
      "related_service": "assets",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "incident.created",
      "created_at": "2026-10-13T13:05:35.693113+00:00",
      "description": "incident.created: record 3",
      "event_id": "68631eab-598b-431a-957d-fd20f990c055",
      "id": 38,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "incident.created",
      "created_at": "2026-10-13T13:05:35.818372+00:00",
      "description": "incident.created: record 4",
      "event_id": "8de64d2a-fb17-4c11-87e4-57d77e213424",
      "id": 39,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:37.275608+00:00",
      "description": "PUT /Abdulrahman-Kobeissi/incidents/2/status: Your role does not permit this operation",
      "event_id": "4634e8f0-1bab-48b3-8227-3e589596423f",
      "id": 49,
      "related_service": "incidents",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:38.599648+00:00",
      "description": "GET /Abdulrahman-Kobeissi/threats: Your role does not permit this operation",
      "event_id": "0c6548dd-77d3-4463-862c-5a632f01a763",
      "id": 56,
      "related_service": "threats",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "notification.read",
      "created_at": "2026-10-13T13:05:40.956007+00:00",
      "description": "notification.read: record 15",
      "event_id": "ee9a0b23-bc8b-485d-9b84-7f33bd93da33",
      "id": 69,
      "related_service": "notifications",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:42.326035+00:00",
      "description": "DELETE /Abdulrahman-Kobeissi/notifications/16: Your role does not permit this operation",
      "event_id": "b260cf2b-423f-4aad-b35f-74c82051dcee",
      "id": 72,
      "related_service": "notifications",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "lab.review",
      "created_at": "2026-10-13T13:05:44.995827+00:00",
      "description": "Manual verification event",
      "event_id": null,
      "id": 86,
      "related_service": "logs",
      "severity": "Information",
      "user_id": 3
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/logs/user/{user_id}

Logs by user.

Service: logs; base URL: http://127.0.0.1:5105.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| user_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "action": "login.succeeded",
      "created_at": "2026-10-13T13:05:25.939455+00:00",
      "description": "User authenticated",
      "event_id": "7e946266-24f0-441c-aac2-ac3cccbcb515",
      "id": 6,
      "related_service": "users",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "user.updated",
      "created_at": "2026-10-13T13:05:32.133073+00:00",
      "description": "user.updated: record 3",
      "event_id": "f1b0c6e8-7190-48f4-aa5d-42ca7a4a369f",
      "id": 14,
      "related_service": "users",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:34.323696+00:00",
      "description": "DELETE /Abdulrahman-Kobeissi/users/6: Your role does not permit this operation",
      "event_id": "b50e4636-bddc-4945-843d-9cb7b536ea8d",
      "id": 26,
      "related_service": "users",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "incident.created",
      "created_at": "2026-10-13T13:05:35.539501+00:00",
      "description": "incident.created: record 1",
      "event_id": "e68d188c-1c56-40cf-84cc-ce7e488da26c",
      "id": 34,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "incident.created",
      "created_at": "2026-10-13T13:05:35.625573+00:00",
      "description": "incident.created: record 2",
      "event_id": "fe15b318-f33c-4bb3-915f-b332e77414e9",
      "id": 35,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:35.446433+00:00",
      "description": "GET /Abdulrahman-Kobeissi/assets: Your role does not permit this operation",
      "event_id": "f23e2161-30e1-4ca0-a6bb-386389ba5a4a",
      "id": 36,
      "related_service": "assets",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "incident.created",
      "created_at": "2026-10-13T13:05:35.693113+00:00",
      "description": "incident.created: record 3",
      "event_id": "68631eab-598b-431a-957d-fd20f990c055",
      "id": 38,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "incident.created",
      "created_at": "2026-10-13T13:05:35.818372+00:00",
      "description": "incident.created: record 4",
      "event_id": "8de64d2a-fb17-4c11-87e4-57d77e213424",
      "id": 39,
      "related_service": "incidents",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:37.275608+00:00",
      "description": "PUT /Abdulrahman-Kobeissi/incidents/2/status: Your role does not permit this operation",
      "event_id": "4634e8f0-1bab-48b3-8227-3e589596423f",
      "id": 49,
      "related_service": "incidents",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:38.599648+00:00",
      "description": "GET /Abdulrahman-Kobeissi/threats: Your role does not permit this operation",
      "event_id": "0c6548dd-77d3-4463-862c-5a632f01a763",
      "id": 56,
      "related_service": "threats",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "notification.read",
      "created_at": "2026-10-13T13:05:40.956007+00:00",
      "description": "notification.read: record 15",
      "event_id": "ee9a0b23-bc8b-485d-9b84-7f33bd93da33",
      "id": 69,
      "related_service": "notifications",
      "severity": "Information",
      "user_id": 3
    },
    {
      "action": "access.denied",
      "created_at": "2026-10-13T13:05:42.326035+00:00",
      "description": "DELETE /Abdulrahman-Kobeissi/notifications/16: Your role does not permit this operation",
      "event_id": "b260cf2b-423f-4aad-b35f-74c82051dcee",
      "id": 72,
      "related_service": "notifications",
      "severity": "Warning",
      "user_id": 3
    },
    {
      "action": "lab.review",
      "created_at": "2026-10-13T13:05:44.995827+00:00",
      "description": "Manual verification event",
      "event_id": null,
      "id": 86,
      "related_service": "logs",
      "severity": "Information",
      "user_id": 3
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## DELETE /Abdulrahman-Kobeissi/logs/{record_id}

Delete manual audit log.

Service: logs; base URL: http://127.0.0.1:5105.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| record_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "deleted": true,
    "id": 86
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/reports/summary

Generate summary report.

Service: reports; base URL: http://127.0.0.1:5106.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": {
    "assets": 2,
    "critical_threats": 1,
    "generated_at": "2026-10-13T13:05:47.674532+00:00",
    "incidents": 4,
    "logs": 88,
    "open_incidents": 3,
    "recent_activities": [
      {
        "action": "access.denied",
        "created_at": "2026-10-13T13:05:44.229333+00:00",
        "description": "DELETE /Abdulrahman-Kobeissi/playbooks/2: Your role does not permit this operation",
        "event_id": "a688958e-94b7-4624-9c95-2fbbf8c4f6cb",
        "id": 84,
        "related_service": "playbooks",
        "severity": "Warning",
        "user_id": 2
      },
      {
        "action": "playbook.deleted",
        "created_at": "2026-10-13T13:05:44.265902+00:00",
        "description": "playbook.deleted: record 2",
        "event_id": "bdc99953-700a-46ae-a1e1-4a4b27b0da4f",
        "id": 85,
        "related_service": "playbooks",
        "severity": "Information",
        "user_id": 1
      },
      {
        "action": "log.created",
        "created_at": "2026-10-13T13:05:44.999817+00:00",
        "description": "log.created: record 86",
        "event_id": "6e877cc6-f3b9-4c04-ae69-b17e6c045b11",
        "id": 87,
        "related_service": "logs",
        "severity": "Information",
        "user_id": 1
      },
      {
        "action": "access.denied",
        "created_at": "2026-10-13T13:05:46.095550+00:00",
        "description": "DELETE /Abdulrahman-Kobeissi/logs/86: Your role does not permit this operation",
        "event_id": "1764abce-18d7-4264-9756-b36dd160d879",
        "id": 88,
        "related_service": "logs",
        "severity": "Warning",
        "user_id": 2
      },
      {
        "action": "log.deleted",
        "created_at": "2026-10-13T13:05:46.675741+00:00",
        "description": "log.deleted: record 86",
        "event_id": "cffdef56-beb3-4784-9ff8-c6ca86420dff",
        "id": 89,
        "related_service": "logs",
        "severity": "Information",
        "user_id": 1
      }
    ],
    "source": "Service HTTP APIs",
    "threats": 2,
    "users": 5,
    "vulnerabilities": 2
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/reports/incidents

Generate incidents report.

Service: reports; base URL: http://127.0.0.1:5106.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": {
    "by_severity": {
      "Critical": 1,
      "High": 1,
      "Low": 1,
      "Medium": 1
    },
    "by_status": {
      "Closed": 1,
      "Open": 3
    },
    "generated_at": "2026-10-13T13:05:47.778284+00:00",
    "source": "Service HTTP APIs",
    "total": 4
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/reports/assets

Generate assets report.

Service: reports; base URL: http://127.0.0.1:5106.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": {
    "by_type": {
      "Server": 1,
      "Workstation": 1
    },
    "critical_assets": 1,
    "generated_at": "2026-10-13T13:05:47.891250+00:00",
    "source": "Service HTTP APIs",
    "total": 2
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/reports/threats

Generate threats report.

Service: reports; base URL: http://127.0.0.1:5106.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": {
    "by_severity": {
      "Critical": 1,
      "Medium": 1
    },
    "by_type": {
      "Domain": 1,
      "IP Address": 1
    },
    "generated_at": "2026-10-13T13:05:47.970471+00:00",
    "recent_added": [
      {
        "created_at": "2026-10-13T13:05:37.433214+00:00",
        "description": "Escalated lab indicator",
        "id": 1,
        "severity": "Critical",
        "source": "Lab review",
        "threat_type": "IP Address",
        "value": "198.18.147.64"
      },
      {
        "created_at": "2026-10-13T13:05:37.499042+00:00",
        "description": "Fictional test indicator; not external threat intelligence.",
        "id": 2,
        "severity": "Medium",
        "source": "Local lab",
        "threat_type": "Domain",
        "value": "r1791896720766f.example.test"
      }
    ],
    "source": "Service HTTP APIs",
    "total": 2
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/reports/vulnerabilities

Generate vulnerabilities report.

Service: reports; base URL: http://127.0.0.1:5106.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": {
    "by_severity": {
      "Critical": 1,
      "High": 1
    },
    "by_status": {
      "Closed": 1,
      "Open": 1
    },
    "critical_vulnerabilities": 1,
    "generated_at": "2026-10-13T13:05:48.103233+00:00",
    "source": "Service HTTP APIs",
    "total": 2
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/reports/activity

Generate activity report.

Service: reports; base URL: http://127.0.0.1:5106.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": {
    "failed_login_attempts": 3,
    "generated_at": "2026-10-13T13:05:48.199799+00:00",
    "login_attempts": 9,
    "most_performed_actions": [
      {
        "action": "access.denied",
        "count": 21
      },
      {
        "action": "login.succeeded",
        "count": 6
      },
      {
        "action": "user.created",
        "count": 5
      },
      {
        "action": "vulnerabilities.updated",
        "count": 5
      },
      {
        "action": "incident.created",
        "count": 4
      },
      {
        "action": "incident.status_changed",
        "count": 4
      },
      {
        "action": "action.status_changed",
        "count": 4
      },
      {
        "action": "login.failed",
        "count": 3
      },
      {
        "action": "user.status_changed",
        "count": 3
      },
      {
        "action": "asset.created",
        "count": 3
      }
    ],
    "source": "Service HTTP APIs",
    "total_activities": 88
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## POST /Abdulrahman-Kobeissi/vulnerabilities

Create critical vulnerability.

Service: vulnerabilities; base URL: http://127.0.0.1:5107.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

Request fields: title, description, cve, cvss, severity, asset_id, discovery_source.
Required fields: title, description, cve, cvss, severity, asset_id, discovery_source.

```json
{
  "title": "Critical lab vulnerability",
  "description": "Fictional record for API verification; identifier is a format example.",
  "cve": "CVE-2026-99001",
  "cvss": 9.8,
  "severity": "Critical",
  "asset_id": 1,
  "discovery_source": "Local test scanner"
}
```

HTTP 201: Record created.

```json
{
  "data": {
    "asset_id": 1,
    "created_at": "2026-10-13T13:05:38.669540+00:00",
    "cve": "CVE-2026-99001",
    "cvss": 9.8,
    "description": "Fictional record for API verification; identifier is a format example.",
    "discovery_source": "Local test scanner",
    "id": 1,
    "resolution_date": null,
    "severity": "Critical",
    "status": "Open",
    "title": "Critical lab vulnerability"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/vulnerabilities

List vulnerabilities.

Service: vulnerabilities; base URL: http://127.0.0.1:5107.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "asset_id": 1,
      "created_at": "2026-10-13T13:05:38.669540+00:00",
      "cve": "CVE-2026-99001",
      "cvss": 9.8,
      "description": "Fictional record for API verification; identifier is a format example.",
      "discovery_source": "Local test scanner",
      "id": 1,
      "resolution_date": null,
      "severity": "Critical",
      "status": "Open",
      "title": "Critical lab vulnerability"
    },
    {
      "asset_id": 1,
      "created_at": "2026-10-13T13:05:38.762622+00:00",
      "cve": "CVE-2026-99002",
      "cvss": 8.1,
      "description": "Fictional record for API verification; identifier is a format example.",
      "discovery_source": "Local test scanner",
      "id": 2,
      "resolution_date": null,
      "severity": "High",
      "status": "Open",
      "title": "High lab vulnerability"
    },
    {
      "asset_id": 1,
      "created_at": "2026-10-13T13:05:38.859179+00:00",
      "cve": "CVE-2026-99003",
      "cvss": 2.0,
      "description": "Fictional record for API verification; identifier is a format example.",
      "discovery_source": "Local test scanner",
      "id": 3,
      "resolution_date": null,
      "severity": "Low",
      "status": "Open",
      "title": "Low lab vulnerability"
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/vulnerabilities/search

Search vulnerabilities by cve.

Service: vulnerabilities; base URL: http://127.0.0.1:5107.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Auditor.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| cve | query | False | CVE-YYYY-NNNN or longer numeric suffix; format is validated, external CVE existence is not. |
| severity | query | False | Severity. |
| asset_id | query | False | Existing affected asset ID. Incident reports may use null when the asset is unknown. |
| status | query | False | Validated lifecycle or resource status; see workflow documentation. |

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "asset_id": 1,
      "created_at": "2026-10-13T13:05:38.669540+00:00",
      "cve": "CVE-2026-99001",
      "cvss": 9.1,
      "description": "Remediation verified in controlled lab",
      "discovery_source": "Local test scanner",
      "id": 1,
      "resolution_date": "2026-10-13T13:05:39.262537+00:00",
      "severity": "Critical",
      "status": "Closed",
      "title": "Critical lab vulnerability"
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/vulnerabilities/{record_id}

Vulnerability before update.

Service: vulnerabilities; base URL: http://127.0.0.1:5107.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Auditor.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| record_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "asset_id": 1,
    "created_at": "2026-10-13T13:05:38.669540+00:00",
    "cve": "CVE-2026-99001",
    "cvss": 9.8,
    "description": "Fictional record for API verification; identifier is a format example.",
    "discovery_source": "Local test scanner",
    "id": 1,
    "resolution_date": null,
    "severity": "Critical",
    "status": "Open",
    "title": "Critical lab vulnerability"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## PUT /Abdulrahman-Kobeissi/vulnerabilities/{record_id}

Update vulnerability details.

Service: vulnerabilities; base URL: http://127.0.0.1:5107.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| record_id | path | True | Positive record identifier |

Request fields: description, cvss, status, severity, resolution_date.
Required fields: at least one permitted update field.

```json
{
  "description": "Remediation verified in controlled lab",
  "cvss": 9.1
}
```

HTTP 200: Successful read or update.

```json
{
  "data": {
    "asset_id": 1,
    "created_at": "2026-10-13T13:05:38.669540+00:00",
    "cve": "CVE-2026-99001",
    "cvss": 9.1,
    "description": "Remediation verified in controlled lab",
    "discovery_source": "Local test scanner",
    "id": 1,
    "resolution_date": null,
    "severity": "Critical",
    "status": "Open",
    "title": "Critical lab vulnerability"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## DELETE /Abdulrahman-Kobeissi/vulnerabilities/{record_id}

Delete vulnerability.

Service: vulnerabilities; base URL: http://127.0.0.1:5107.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| record_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "deleted": true,
    "id": 3
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## POST /Abdulrahman-Kobeissi/notifications

Create security alert.

Service: notifications; base URL: http://127.0.0.1:5108.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

Request fields: user_id, title, message, notification_type, severity.
Required fields: user_id, title, message, notification_type, severity.

```json
{
  "user_id": 3,
  "title": "Security Alert example",
  "message": "Controlled local demonstration",
  "notification_type": "Security Alert",
  "severity": "Medium"
}
```

HTTP 201: Record created.

```json
{
  "data": {
    "created_at": "2026-10-13T13:05:40.049379+00:00",
    "event_id": null,
    "id": 15,
    "message": "Controlled local demonstration",
    "notification_type": "Security Alert",
    "read_date": null,
    "severity": "Medium",
    "status": "Unread",
    "title": "Security Alert example",
    "user_id": 3
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/notifications/user/{user_id}

Employee personal notifications.

Service: notifications; base URL: http://127.0.0.1:5108.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Regular Employee/User, Auditor.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| user_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "created_at": "2026-10-13T13:05:25.105630+00:00",
      "event_id": "2658b725-f3bd-4d15-9380-22e901f8f007",
      "id": 2,
      "message": "Your account is ready.",
      "notification_type": "System Notification",
      "read_date": null,
      "severity": "Low",
      "status": "Unread",
      "title": "Account created",
      "user_id": 3
    },
    {
      "created_at": "2026-10-13T13:05:35.539501+00:00",
      "event_id": "464847ba-3d87-404c-ab64-717b08e4dd5d",
      "id": 6,
      "message": "Incident 1 is Open.",
      "notification_type": "Security Alert",
      "read_date": null,
      "severity": "Low",
      "status": "Unread",
      "title": "Incident reported",
      "user_id": 3
    },
    {
      "created_at": "2026-10-13T13:05:35.626572+00:00",
      "event_id": "4123adbd-2058-4280-897b-7938bc0ef72f",
      "id": 7,
      "message": "Incident 2 is Open.",
      "notification_type": "Security Alert",
      "read_date": null,
      "severity": "Medium",
      "status": "Unread",
      "title": "Incident reported",
      "user_id": 3
    },
    {
      "created_at": "2026-10-13T13:05:35.694112+00:00",
      "event_id": "e250e15e-6348-4963-b40d-fca9e8d75a1a",
      "id": 8,
      "message": "Incident 3 is Open.",
      "notification_type": "Security Alert",
      "read_date": null,
      "severity": "High",
      "status": "Unread",
      "title": "Incident reported",
      "user_id": 3
    },
    {
      "created_at": "2026-10-13T13:05:35.819369+00:00",
      "event_id": "71ecc9a2-a6ec-4e0c-b1f8-2a309180e317",
      "id": 9,
      "message": "Incident 4 is Open.",
      "notification_type": "Security Alert",
      "read_date": null,
      "severity": "Critical",
      "status": "Unread",
      "title": "Incident reported",
      "user_id": 3
    },
    {
      "created_at": "2026-10-13T13:05:40.049379+00:00",
      "event_id": null,
      "id": 15,
      "message": "Controlled local demonstration",
      "notification_type": "Security Alert",
      "read_date": null,
      "severity": "Medium",
      "status": "Unread",
      "title": "Security Alert example",
      "user_id": 3
    },
    {
      "created_at": "2026-10-13T13:05:40.144518+00:00",
      "event_id": null,
      "id": 16,
      "message": "Controlled local demonstration",
      "notification_type": "System Notification",
      "read_date": null,
      "severity": "Medium",
      "status": "Unread",
      "title": "System Notification example",
      "user_id": 3
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/notifications/{record_id}

Notification before read.

Service: notifications; base URL: http://127.0.0.1:5108.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Regular Employee/User, Auditor.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| record_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "created_at": "2026-10-13T13:05:40.049379+00:00",
    "event_id": null,
    "id": 15,
    "message": "Controlled local demonstration",
    "notification_type": "Security Alert",
    "read_date": null,
    "severity": "Medium",
    "status": "Unread",
    "title": "Security Alert example",
    "user_id": 3
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## PUT /Abdulrahman-Kobeissi/notifications/{record_id}/read

Mark notification read.

Service: notifications; base URL: http://127.0.0.1:5108.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Regular Employee/User.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| record_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "created_at": "2026-10-13T13:05:40.049379+00:00",
    "event_id": null,
    "id": 15,
    "message": "Controlled local demonstration",
    "notification_type": "Security Alert",
    "read_date": "2026-10-13T13:05:40.955010+00:00",
    "severity": "Medium",
    "status": "Read",
    "title": "Security Alert example",
    "user_id": 3
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/notifications/search

Search notifications by user_id.

Service: notifications; base URL: http://127.0.0.1:5108.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Auditor.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| user_id | query | False | User id. |
| notification_type | query | False | Notification type. |
| severity | query | False | Severity. |
| status | query | False | Validated lifecycle or resource status; see workflow documentation. |

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "created_at": "2026-10-13T13:05:25.105630+00:00",
      "event_id": "2658b725-f3bd-4d15-9380-22e901f8f007",
      "id": 2,
      "message": "Your account is ready.",
      "notification_type": "System Notification",
      "read_date": null,
      "severity": "Low",
      "status": "Unread",
      "title": "Account created",
      "user_id": 3
    },
    {
      "created_at": "2026-10-13T13:05:35.539501+00:00",
      "event_id": "464847ba-3d87-404c-ab64-717b08e4dd5d",
      "id": 6,
      "message": "Incident 1 is Open.",
      "notification_type": "Security Alert",
      "read_date": null,
      "severity": "Low",
      "status": "Unread",
      "title": "Incident reported",
      "user_id": 3
    },
    {
      "created_at": "2026-10-13T13:05:35.626572+00:00",
      "event_id": "4123adbd-2058-4280-897b-7938bc0ef72f",
      "id": 7,
      "message": "Incident 2 is Open.",
      "notification_type": "Security Alert",
      "read_date": null,
      "severity": "Medium",
      "status": "Unread",
      "title": "Incident reported",
      "user_id": 3
    },
    {
      "created_at": "2026-10-13T13:05:35.694112+00:00",
      "event_id": "e250e15e-6348-4963-b40d-fca9e8d75a1a",
      "id": 8,
      "message": "Incident 3 is Open.",
      "notification_type": "Security Alert",
      "read_date": null,
      "severity": "High",
      "status": "Unread",
      "title": "Incident reported",
      "user_id": 3
    },
    {
      "created_at": "2026-10-13T13:05:35.819369+00:00",
      "event_id": "71ecc9a2-a6ec-4e0c-b1f8-2a309180e317",
      "id": 9,
      "message": "Incident 4 is Open.",
      "notification_type": "Security Alert",
      "read_date": null,
      "severity": "Critical",
      "status": "Unread",
      "title": "Incident reported",
      "user_id": 3
    },
    {
      "created_at": "2026-10-13T13:05:40.049379+00:00",
      "event_id": null,
      "id": 15,
      "message": "Controlled local demonstration",
      "notification_type": "Security Alert",
      "read_date": "2026-10-13T13:05:40.955010+00:00",
      "severity": "Medium",
      "status": "Read",
      "title": "Security Alert example",
      "user_id": 3
    },
    {
      "created_at": "2026-10-13T13:05:40.144518+00:00",
      "event_id": null,
      "id": 16,
      "message": "Controlled local demonstration",
      "notification_type": "System Notification",
      "read_date": null,
      "severity": "Medium",
      "status": "Unread",
      "title": "System Notification example",
      "user_id": 3
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## DELETE /Abdulrahman-Kobeissi/notifications/{record_id}

Delete notification.

Service: notifications; base URL: http://127.0.0.1:5108.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| record_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "deleted": true,
    "id": 16
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## POST /Abdulrahman-Kobeissi/playbooks

Create response playbook 1.

Service: playbooks; base URL: http://127.0.0.1:5109.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

Request fields: name, description, incident_category, severity.
Required fields: name, description, incident_category, severity.

```json
{
  "name": "r1791896720766f Phishing response 1",
  "description": "Controlled lab response procedure",
  "incident_category": "Phishing",
  "severity": "High"
}
```

HTTP 201: Record created.

```json
{
  "data": {
    "created_at": "2026-10-13T13:05:43.348801+00:00",
    "created_by": 1,
    "deleted_at": null,
    "description": "Controlled lab response procedure",
    "id": 1,
    "incident_category": "Phishing",
    "name": "r1791896720766f Phishing response 1",
    "severity": "High"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/playbooks

List playbooks.

Service: playbooks; base URL: http://127.0.0.1:5109.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Auditor.

HTTP 200: Successful read or update.

```json
{
  "data": [
    {
      "created_at": "2026-10-13T13:05:43.348801+00:00",
      "created_by": 1,
      "deleted_at": null,
      "description": "Controlled lab response procedure",
      "id": 1,
      "incident_category": "Phishing",
      "name": "r1791896720766f Phishing response 1",
      "severity": "High"
    },
    {
      "created_at": "2026-10-13T13:05:43.424394+00:00",
      "created_by": 1,
      "deleted_at": null,
      "description": "Controlled lab response procedure",
      "id": 2,
      "incident_category": "Phishing",
      "name": "r1791896720766f Phishing response 2",
      "severity": "High"
    }
  ],
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## GET /Abdulrahman-Kobeissi/playbooks/{book_id}

Playbook with ordered actions and history.

Service: playbooks; base URL: http://127.0.0.1:5109.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst, Auditor.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| book_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "actions": [
      {
        "assigned_user_id": 2,
        "completion_date": "2026-10-13T13:05:43.955378+00:00",
        "description": "Isolate test account",
        "history": [
          {
            "action_id": 1,
            "actor_id": 2,
            "assigned_user_id": 2,
            "created_at": "2026-10-13T13:05:43.565080+00:00",
            "id": 1,
            "new_status": "Pending",
            "old_status": null
          },
          {
            "action_id": 1,
            "actor_id": 2,
            "assigned_user_id": 2,
            "created_at": "2026-10-13T13:05:43.871353+00:00",
            "id": 3,
            "new_status": "In Progress",
            "old_status": "Pending"
          },
          {
            "action_id": 1,
            "actor_id": 2,
            "assigned_user_id": 2,
            "created_at": "2026-10-13T13:05:43.955378+00:00",
            "id": 4,
            "new_status": "Completed",
            "old_status": "In Progress"
          }
        ],
        "id": 1,
        "playbook_id": 1,
        "status": "Completed",
        "step_number": 1
      },
      {
        "assigned_user_id": 2,
        "completion_date": "2026-10-13T13:05:44.092196+00:00",
        "description": "Verify recovery",
        "history": [
          {
            "action_id": 2,
            "actor_id": 2,
            "assigned_user_id": 2,
            "created_at": "2026-10-13T13:05:43.691680+00:00",
            "id": 2,
            "new_status": "Pending",
            "old_status": null
          },
          {
            "action_id": 2,
            "actor_id": 2,
            "assigned_user_id": 2,
            "created_at": "2026-10-13T13:05:44.021522+00:00",
            "id": 5,
            "new_status": "In Progress",
            "old_status": "Pending"
          },
          {
            "action_id": 2,
            "actor_id": 2,
            "assigned_user_id": 2,
            "created_at": "2026-10-13T13:05:44.092196+00:00",
            "id": 6,
            "new_status": "Completed",
            "old_status": "In Progress"
          }
        ],
        "id": 2,
        "playbook_id": 1,
        "status": "Completed",
        "step_number": 2
      }
    ],
    "created_at": "2026-10-13T13:05:43.348801+00:00",
    "created_by": 1,
    "deleted_at": null,
    "description": "Controlled lab response procedure",
    "id": 1,
    "incident_category": "Phishing",
    "name": "r1791896720766f Phishing response 1",
    "severity": "High"
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.

## POST /Abdulrahman-Kobeissi/playbooks/{book_id}/actions

Add ordered action 1.

Service: playbooks; base URL: http://127.0.0.1:5109.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| book_id | path | True | Positive record identifier |

Request fields: description, step_number, assigned_user_id.
Required fields: description, step_number.

```json
{
  "description": "Isolate test account",
  "step_number": 1,
  "assigned_user_id": 2
}
```

HTTP 201: Record created.

```json
{
  "data": {
    "assigned_user_id": 2,
    "completion_date": null,
    "description": "Isolate test account",
    "id": 1,
    "playbook_id": 1,
    "status": "Pending",
    "step_number": 1
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## PUT /Abdulrahman-Kobeissi/actions/{action_id}/status

Action 1 becomes In Progress.

Service: playbooks; base URL: http://127.0.0.1:5109.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator, Security Analyst.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| action_id | path | True | Positive record identifier |

Request fields: status, assigned_user_id.
Required fields: status.

```json
{
  "status": "In Progress"
}
```

HTTP 200: Successful read or update.

```json
{
  "data": {
    "assigned_user_id": 2,
    "completion_date": null,
    "description": "Isolate test account",
    "id": 1,
    "playbook_id": 1,
    "status": "In Progress",
    "step_number": 1
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 415: JSON Content-Type required.

HTTP 503: Required service unavailable.

## DELETE /Abdulrahman-Kobeissi/playbooks/{book_id}

Delete unused playbook.

Service: playbooks; base URL: http://127.0.0.1:5109.

Owner: Abdulrahman Kobeissi. Allowed roles: Security Administrator.

| Parameter | Location | Required | Description |
| --- | --- | --- | --- |
| book_id | path | True | Positive record identifier |

HTTP 200: Successful read or update.

```json
{
  "data": {
    "deleted": true,
    "history_retained": true,
    "id": 2
  },
  "status": "success"
}
```

HTTP 400: Invalid input.

HTTP 401: Missing, invalid, expired or revoked token.

HTTP 403: Role or ownership denied.

HTTP 404: Record not found.

HTTP 409: Uniqueness, relationship or workflow conflict.

HTTP 503: Required service unavailable.
