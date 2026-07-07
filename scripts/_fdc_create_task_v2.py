"""Create the FDC task with proper associations - using v4 default API for new task."""
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

tomorrow_iso = (datetime.datetime.utcnow() + datetime.timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%S.000Z')

CANONICAL = '329640754913'
DEAL_BASE = '331864002293'
DEAL_EXPANSION = '331885143770'
CONTACT_EMAIL = '509350081224'

# === Find RZH owner ID ===
print('=== Find RZH owner ID ===')
sc, d = http('GET', f'{BASE}/crm/v3/owners')
rzh_owner_id = None
if sc == 200:
    for o in d.get('results', []):
        if o.get('email', '').lower() == 'rzh24.econares@gmail.com':
            rzh_owner_id = o.get('id')
            break
print(f'  RZH owner: {rzh_owner_id}')

# === Create task via v3 POST (with v4-style association list) ===
# Per the API error earlier, "expected: 0-46" means task from-type is 0-46.
# So the correct format is: associations list with from-type 0-46 to various to-types.

print()
print('=== Create task with v3 POST + full associations list ===')

# Build the v4-style association spec: from type 0-46 (Task) to others
# But the API says the "from" object type in the POST is the new object being created
# which is 0-27 (Note type?) for engagement POSTs.
# Actually - 0-27 might be a different object. The error said "expected: 0-18. For definition 0-83"
# That means type 83 expects from-type 0-18. Different types have different from-types.

# Let me try a simpler approach: POST a task, then iteratively add associations.
print('--- Create task (no assoc) ---')
body = {
    'properties': {
        'hs_task_subject': 'Call FDCUI landline +63285751600 to reach procurement/Mr. Roderick Fernandez - log outcome',
        'hs_task_body': (
            'Email channel to fdcui.com.ph has been failing since 2026-06-29 (server 45.79.222.138 timeouts). '
            'Landline +63285751600 is the only working contact channel.\n\n'
            'Call and log outcome:\n'
            '- Did you reach Mr. Roderick Fernandez?\n'
            '- Willing to discuss FDC Misamis coal supply?\n'
            '- Alternate email provided?\n'
            '- Alternate procurement contact at FDCUI Taguig?\n\n'
            'Update deals 331864002293 + 331885143770 with outcome.'
        ),
        'hs_task_status': 'NOT_STARTED',
        'hs_task_priority': 'HIGH',
        'hs_timestamp': tomorrow_iso
    }
}
if rzh_owner_id:
    body['properties']['hubspot_owner_id'] = rzh_owner_id

sc, d = http('POST', f'{BASE}/crm/v3/objects/tasks', body)
print(f'  HTTP {sc}')
print(f'  Response: {d}')

# Get the task ID from the URL
# Even if response is empty, we can find it
import re
# Actually search for the task in the result. Wait - let me check the Location header
# Easier: just list recent tasks and find the newest one
import time
time.sleep(2)  # small wait for indexing
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_task_subject', 'operator': 'CONTAINS_TOKEN', 'value': 'FDCUI landline +63285751600'}]}], 'properties': ['hs_task_subject','hs_object_id','hs_timestamp','hs_task_status'], 'limit': 10, 'sorts': [{'propertyName': 'hs_timestamp', 'direction': 'DESCENDING'}]}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/tasks/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
print(f'\\n=== Task search results: {d.get("total",0)} ===')
TASK_ID = None
for t in d.get('results',[]):
    p = t['properties']
    subj = p.get('hs_task_subject','')
    if 'log outcome' in subj:
        TASK_ID = t['id']
        print(f'  Found target task: {TASK_ID} | due={p.get("hs_timestamp")}')
        break

if not TASK_ID:
    print('ERROR: Could not find the task. Trying with date range...')
    # List ALL recent tasks
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_timestamp', 'operator': 'GTE', 'value': str(int(time.time()*1000) - 600000)}]}], 'properties': ['hs_task_subject','hs_object_id','hs_timestamp','hs_task_status'], 'limit': 10, 'sorts': [{'propertyName': 'hs_timestamp', 'direction': 'DESCENDING'}]}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/tasks/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read().decode())
    print(f'  Recent tasks (last 10 min): {d.get("total",0)}')
    for t in d.get('results',[]):
        p = t['properties']
        print(f'    {t["id"]}: {p.get("hs_task_subject","")[:70]} | due={p.get("hs_timestamp","")}')

if TASK_ID:
    # === Try various type IDs for task->company ===
    print()
    print('=== Add task->company association ===')
    for type_id in [83, 84, 191, 192, 280, 281, 282, 13, 14, 65, 71]:
        sc, d = http('PUT', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/companies/{CANONICAL}/{type_id}', body={})
        if sc in (200, 201, 204):
            print(f'  type {type_id}: HTTP {sc} SUCCESS')
            break
        # Show only non-"wrong from-type" errors
        elif isinstance(d, dict) and 'expected: 0-46' in d.get('message', ''):
            pass
        elif isinstance(d, dict) and 'for associations' in d.get('message', ''):
            pass
        else:
            err = d.get('message', str(d)[:60]) if isinstance(d, dict) else str(d)[:60]
            print(f'  type {type_id}: {sc} - {err}')

    # === Try various type IDs for task->contact ===
    print()
    print('=== Add task->contact association ===')
    for type_id in [87, 88, 212, 213, 280, 281, 282, 14, 15, 65, 71]:
        sc, d = http('PUT', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/contacts/{CONTACT_EMAIL}/{type_id}', body={})
        if sc in (200, 201, 204):
            print(f'  type {type_id}: HTTP {sc} SUCCESS')
            break
        elif isinstance(d, dict) and 'expected: 0-46' in d.get('message', ''):
            pass
        elif isinstance(d, dict) and 'for associations' in d.get('message', ''):
            pass
        else:
            err = d.get('message', str(d)[:60]) if isinstance(d, dict) else str(d)[:60]
            print(f'  type {type_id}: {sc} - {err}')

    # === Add task->deal associations (known to work with 216) ===
    print()
    print('=== Add task->deal associations ===')
    for did in [DEAL_BASE, DEAL_EXPANSION]:
        sc, d = http('PUT', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/deals/{did}/216', body={})
        print(f'  task->deal {did} (216): HTTP {sc}')

# === Final verification ===
print()
print('=== Final task state ===')
if TASK_ID:
    for label in ['companies', 'contacts', 'deals']:
        sc, d = http('GET', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/{label}')
        results = d.get('results', []) if isinstance(d, dict) else []
        print(f'  {label}: {len(results)} associations')
        for r in results:
            print(f'    {r}')

print()
print(f'=== Task ID: {TASK_ID} ===')