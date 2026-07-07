"""Try alternative association type IDs for task -> company and task -> contact."""
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

TASK_ID = '381415880383'
CANONICAL = '329640754913'
CONTACT_EMAIL = '509350081224'

# === Try task -> company with various type IDs ===
# Known default types for task:
# 83 = task->company
# 84 = ?
# 279 = ?
# 280 = ?
# 65 = engagement->company?

# Try the v4 default associations endpoint (different syntax)
print('=== Try various type IDs for task->company ===')
for type_id in [83, 84, 279, 280, 65, 13, 14, 71]:
    sc, d = http('PUT', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/companies/{CANONICAL}/{type_id}', body={})
    print(f'  Type {type_id}: HTTP {sc}')
    if sc in (200, 201, 204):
        print(f'  SUCCESS')
        break

print()
print('=== Verify task->company ===')
sc, d = http('GET', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/companies')
print(f'  GET: HTTP {sc} | {d}')

# === Try task -> contact with various type IDs ===
print()
print('=== Try various type IDs for task->contact ===')
for type_id in [87, 88, 202, 203, 14, 15, 71, 65]:
    sc, d = http('PUT', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/contacts/{CONTACT_EMAIL}/{type_id}', body={})
    print(f'  Type {type_id}: HTTP {sc}')
    if sc in (200, 201, 204):
        print(f'  SUCCESS')
        break

print()
print('=== Verify task->contact ===')
sc, d = http('GET', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/contacts')
print(f'  GET: HTTP {sc} | {d}')

# === Also recheck task with all 3 association types using the v3 default endpoint ===
print()
print('=== Final task state ===')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_object_id', 'operator': 'EQ', 'value': TASK_ID}]}], 'properties': ['hs_task_subject','hs_task_status','hs_object_id'], 'limit': 5}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/tasks/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
for t in d.get('results',[]):
    print(f'  Task {t["id"]}: {t["properties"].get("hs_task_subject","")}')

# Get all association types on the task
print()
for label in ['companies', 'contacts', 'deals']:
    sc, d = http('GET', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/{label}')
    results = d.get('results', []) if isinstance(d, dict) else []
    print(f'  {label}: {len(results)} | IDs: {results}')

print()
print('=== Done ===')