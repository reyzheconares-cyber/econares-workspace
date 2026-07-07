"""Find correct task association type IDs and create the task properly."""
import json, urllib.request, datetime

ENV_PATH = r'C:\Users\reyma\.hermes\.env'
T = None
with open(ENV_PATH, 'r', encoding='utf-8') as f:
    for line in f:
        if line.lstrip().startswith('HUBSPOT_ACCESS_TOKEN='):
            T = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

BASE = 'https://api.hubapi.com'

def http(method, url, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=15) as resp:
            return resp.status, (json.loads(resp.read().decode()) if resp.length else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, e.read().decode()[:300]

# === Use the HubSpot default association API to read the task schema associations ===
# Tasks are object type 0-46. Let me check what association types are available.
print('=== Get task schema with default associations ===')
# v1 API for object definition
sc, d = http('GET', f'{BASE}/crm/v3/schemas/tasks')
print(f'  HTTP {sc}')
if sc == 200:
    assocs = d.get('associations', [])
    print(f'  Task default associations: {assocs}')
    for a in assocs:
        if isinstance(a, dict):
            print(f'    {a.get("name")}: from type {a.get("fromObjectTypeId")} -> to {a.get("toObjectTypeId")} type {a.get("id")}')

# Also look at the v1 /v1 or v2 schemas endpoint
print()
sc, d = http('GET', f'{BASE}/crm/v2/schemas/tasks')
print(f'v2 schema HTTP {sc}')
if sc == 200 and isinstance(d, dict):
    for a in d.get('associations', []) or []:
        print(f'  {a}')

# === Try with the v1 default association (PUT with specific type IDs known to work) ===
# According to HubSpot's standard task association types:
# - 212 = task->contact
# - 214 = task->deal
# - 216 = task->company (this worked for deals; maybe contact/company need different)
# Actually, 216 worked for task->deal not task->company.
# Standard task engagement types:
# - 202 = note->contact
# - 214 = note->deal
# - 190 = note->company (we just used this)
# For TASK: 212=contact, 214=deal, 83=company? But "0-27 expected: 0-18" said 0-83 expects 0-18 (note) not 0-46 (task)
# So task->company is a DIFFERENT type, like 191 or similar

CANONICAL = '329640754913'
DEAL_BASE = '331864002293'
DEAL_EXPANSION = '331885143770'
CONTACT_EMAIL = '509350081224'

# === Try the v3 default association (PUT) with various type IDs ===
print()
print('=== Try task->company with various type IDs ===')
TASK_NEW = None
sc, d = http('POST', f'{BASE}/crm/v3/objects/tasks', {
    'properties': {
        'hs_task_subject': 'Call FDCUI landline +63285751600',
        'hs_task_body': 'Test',
        'hs_task_status': 'NOT_STARTED',
        'hs_timestamp': '2026-07-08T06:56:32Z'
    }
})
if sc in (200, 201):
    TASK_NEW = d.get('id') if isinstance(d, dict) else None
    print(f'  Created new test task: {TASK_NEW}')

if TASK_NEW:
    # Try various type IDs for task->company
    for type_id in [84, 191, 192, 193, 279, 280, 281, 282, 283, 284]:
        sc, d = http('PUT', f'{BASE}/crm/v3/objects/tasks/{TASK_NEW}/associations/companies/{CANONICAL}/{type_id}', body={})
        if sc in (200, 201, 204):
            print(f'  task->company type {type_id}: HTTP {sc} SUCCESS')
            break
        else:
            err = d.get('message', str(d)[:80]) if isinstance(d, dict) else str(d)[:80]
            print(f'  type {type_id}: {sc} - {err[:80]}')
    # Verify
    sc, d = http('GET', f'{BASE}/crm/v3/objects/tasks/{TASK_NEW}/associations/companies')
    print(f'  Final company assocs: {d.get("results",[])}')

    print()
    print('=== Try task->contact with various type IDs ===')
    for type_id in [88, 212, 213, 279, 280, 281, 282, 283, 284]:
        sc, d = http('PUT', f'{BASE}/crm/v3/objects/tasks/{TASK_NEW}/associations/contacts/{CONTACT_EMAIL}/{type_id}', body={})
        if sc in (200, 201, 204):
            print(f'  task->contact type {type_id}: HTTP {sc} SUCCESS')
            break
        else:
            err = d.get('message', str(d)[:80]) if isinstance(d, dict) else str(d)[:80]
            print(f'  type {type_id}: {sc} - {err[:80]}')
    sc, d = http('GET', f'{BASE}/crm/v3/objects/tasks/{TASK_NEW}/associations/contacts')
    print(f'  Final contact assocs: {d.get("results",[])}')

    # Cleanup test task
    sc, d = http('DELETE', f'{BASE}/crm/v3/objects/tasks/{TASK_NEW}')
    print(f'\\nDeleted test task {TASK_NEW}: HTTP {sc}')

print()
print('=== Done ===')