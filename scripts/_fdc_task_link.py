"""Find and link the just-created task to FDC entities."""
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

now_iso = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

# === Find the just-created task (subject = call FDCUI) ===
print('=== Find the task ===')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_task_subject', 'operator': 'CONTAINS_TOKEN', 'value': 'FDCUI landline'}]}], 'properties': ['hs_task_subject','hs_task_status','hs_timestamp','hs_object_id'], 'limit': 5}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/tasks/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
print(f'Tasks found: {d.get("total",0)}')
for t in d.get('results',[]):
    p = t['properties']
    print(f'  {t["id"]}: {p.get("hs_task_subject","")} | due={p.get("hs_timestamp","")} | status={p.get("hs_task_status","")}')

# Get the task ID
task_id = d.get('results',[{}])[0].get('id') if d.get('results') else None
if not task_id:
    print('No task found!')
    exit(1)

# === Add associations via v3 default endpoint ===
# The default associations API for tasks: PUT /crm/v3/objects/tasks/{taskId}/associations/{toObjectType}/{toObjectId}/{associationType}
# For tasks -> company: 0-2 -> use type 83
# For tasks -> contact: 0-1 -> use type 87
# For tasks -> deal: 0-3 -> use type 216

CANONICAL = '329640754913'
DEAL_BASE = '331864002293'
DEAL_EXPANSION = '331885143770'
CONTACT_EMAIL = '509350081224'

associations_to_add = [
    (CANONICAL, 'company', 83),  # task -> company
    (DEAL_BASE, 'deal', 216),    # task -> deal
    (DEAL_EXPANSION, 'deal', 216),
    (CONTACT_EMAIL, 'contact', 87),  # task -> contact
]

print()
print('=== Add task associations ===')
for target_id, target_type_label, type_id in associations_to_add:
    # Map label to HubSpot object type ID
    obj_type_map = {'company': '0-2', 'contact': '0-1', 'deal': '0-3', 'task': '0-46'}
    obj_type = obj_type_map.get(target_type_label, '0-2')
    url = f'{BASE}/crm/v3/objects/tasks/{task_id}/associations/{target_type_label}/{target_id}/{type_id}'
    sc, d = http('PUT', url, body={})
    print(f'  PUT {target_type_label} {target_id} (type {type_id}): HTTP {sc}')

# === Also verify the task state ===
print()
print('=== Task state after associations ===')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_task_subject', 'operator': 'CONTAINS_TOKEN', 'value': 'FDCUI landline'}]}], 'properties': ['hs_task_subject','hs_task_status','hs_timestamp','hs_object_id','hs_buying_role','hubspot_owner_id'], 'limit': 5}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/tasks/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
for t in d.get('results',[]):
    p = t['properties']
    print(f'  {t["id"]}: {p.get("hs_task_subject","")} | due={p.get("hs_timestamp","")} | status={p.get("hs_task_status","")} | owner={p.get("hubspot_owner_id","")}')

# Get task associations via the v3 default associations endpoint
print()
print('=== Task associations (via v3 GET) ===')
sc, d = http('GET', f'{BASE}/crm/v3/objects/tasks/{task_id}/associations/companies')
print(f'  GET task->companies: HTTP {sc} | {d}')

print()
print('=== Done ===')