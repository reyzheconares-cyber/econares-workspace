"""Create the final FDC call task with proper associations."""
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

# === Step 1: Create the task (no associations) ===
print('=== Create task (no assoc) ===')
sc, d = http('POST', f'{BASE}/crm/v3/objects/tasks', {
    'properties': {
        'hs_task_subject': 'Call FDCUI landline +63285751600 to reach procurement/Mr. Roderick Fernandez - log outcome',
        'hs_task_body': (
            'Email channel to fdcui.com.ph has been failing since 2026-06-29 (server 45.79.222.138 timeouts). '
            'Landline +63285751600 is the only working contact channel.\n\n'
            'Call and log outcome:\n'
            '- Did you reach Mr. Roderick Fernandez (Procurement Contact, FDCUI Taguig)?\n'
            '- Was he willing to discuss FDC Misamis coal supply (500k MT/yr Villanueva + 1.5-2M MT/yr Expansion)?\n'
            '- Did he provide a working alternate email?\n'
            '- If no answer, is there an alternate procurement contact at FDCUI Taguig?\n\n'
            'Update HubSpot deals 331864002293 + 331885143770 with outcome.'
        ),
        'hs_task_status': 'NOT_STARTED',
        'hs_task_priority': 'HIGH',
        'hs_timestamp': tomorrow_iso
    }
})
print(f'  Create: HTTP {sc}')
# Task created with empty response - find it by subject
if sc in (200, 201):
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_task_subject', 'operator': 'CONTAINS_TOKEN', 'value': 'FDCUI landline'}]}], 'properties': ['hs_task_subject','hs_object_id','hs_timestamp','hs_task_status'], 'limit': 5}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/tasks/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read().decode())
    if d.get('total', 0) > 0:
        TASK_ID = d['results'][0]['id']
        print(f'  Task ID (newest): {TASK_ID}')
    else:
        print('  ERROR: Task not found after creation!')
        exit(1)
else:
    print(f'  Error: {d}')
    exit(1)

# === Step 2: Add associations using the PUT endpoint with various type IDs ===
# For task->deal, 216 worked previously. Let me find the right types for company+contact.

# Test type IDs for task->company (per HubSpot docs, common types: 83, 191, 192, 280, 281)
# For task->contact: 87, 88, 212, 213, 280

print()
print('=== Add task associations ===')

# Try task->deal first (known to work with 216)
for did in [DEAL_BASE, DEAL_EXPANSION]:
    sc, d = http('PUT', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/deals/{did}/216', body={})
    print(f'  task->deal {did} (216): HTTP {sc}')

# Try task->company with multiple type IDs
for type_id in [83, 84, 191, 192, 279, 280, 281, 282, 13, 14, 65, 71]:
    sc, d = http('PUT', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/companies/{CANONICAL}/{type_id}', body={})
    err_msg = d.get('message', '') if isinstance(d, dict) else str(d)
    if sc in (200, 201, 204):
        print(f'  task->company type {type_id}: HTTP {sc} SUCCESS')
        # Verify
        sc2, d2 = http('GET', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/companies')
        if d2.get('results', []):
            res = d2.get('results')
            print(f'    Verified: {res}')
        break
    elif 'expected: 0-46' in err_msg or 'for associations' in err_msg:
        # Wrong from-type for this type id, skip
        pass
    else:
        print(f'  task->company type {type_id}: {sc} - {err_msg[:80]}')

# Try task->contact with multiple type IDs
for type_id in [87, 88, 212, 213, 280, 281, 282, 14, 15, 65, 71]:
    sc, d = http('PUT', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/contacts/{CONTACT_EMAIL}/{type_id}', body={})
    err_msg = d.get('message', '') if isinstance(d, dict) else str(d)
    if sc in (200, 201, 204):
        print(f'  task->contact type {type_id}: HTTP {sc} SUCCESS')
        sc2, d2 = http('GET', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/contacts')
        if d2.get('results', []):
            res = d2.get('results')
            print(f'    Verified: {res}')
        break
    elif 'expected: 0-46' in err_msg or 'for associations' in err_msg:
        pass
    else:
        print(f'  task->contact type {type_id}: {sc} - {err_msg[:80]}')

# === Final verification ===
print()
print('=== Final task state ===')
for label in ['companies', 'contacts', 'deals']:
    sc, d = http('GET', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/{label}')
    results = d.get('results', []) if isinstance(d, dict) else []
    print(f'  {label}: {len(results)} associations')
    for r in results:
        print(f'    {r}')

print()
print('=== Done ===')
print(f'Task ID: {TASK_ID}')