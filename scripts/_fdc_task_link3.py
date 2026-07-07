"""Try task associations with different v3 default formats."""
import json, urllib.request

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

# Try v4 default associations (object type in URL, no type id)
print('=== Try v4 default associations API ===')
for obj_type in ['companies', 'contacts', 'deals']:
    for type_id in [None, 83, 84, 87, 88, 216]:
        if type_id is None:
            # v4 without type id
            url = f'{BASE}/crm/v4/objects/tasks/{TASK_ID}/associations/{obj_type}/'
            sc, d = http('POST', url, body={'toObjectId': CANONICAL if obj_type == 'companies' else (CONTACT_EMAIL if obj_type == 'contacts' else '331864002293')})
        else:
            url = f'{BASE}/crm/v4/objects/tasks/{TASK_ID}/associations/{obj_type}/{type_id}'
            sc, d = http('PUT', url, body={'toObjectId': CANONICAL if obj_type == 'companies' else (CONTACT_EMAIL if obj_type == 'contacts' else '331864002293')})
        if sc in (200, 201, 204):
            print(f'  {obj_type} (type {type_id}): HTTP {sc} - SUCCESS')
            break
        else:
            err = d.get('message', str(d)[:120]) if isinstance(d, dict) else str(d)[:120]
            print(f'  {obj_type} (type {type_id}): HTTP {sc} - {err}')

# Try also the v3 task update with full associations array
print()
print('=== Try PATCH task with full associations array ===')
for attempt in [
    # Attempt 1: standard v3 with type IDs
    {
        'associations': {
            'companies': [83],
            'contacts': [87],
        }
    },
    # Attempt 2: v3 default pattern with array
    {
        'associations': {
            'companyIds': [CANONICAL],
            'contactIds': [CONTACT_EMAIL],
        }
    },
]:
    sc, d = http('PATCH', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}', body=attempt)
    print(f'  PATCH with {list(attempt.keys())}: HTTP {sc}')
    if isinstance(d, dict):
        msg = d.get('message', str(d)[:200])
        print(f'    {msg[:150]}')
    if sc == 200:
        break

# Final verification
print()
print('=== Final task associations ===')
for label in ['companies', 'contacts', 'deals']:
    sc, d = http('GET', f'{BASE}/crm/v3/objects/tasks/{TASK_ID}/associations/{label}')
    results = d.get('results', []) if isinstance(d, dict) else []
    print(f'  {label}: {len(results)} associations')
    for r in results:
        print(f'    {r}')

print()
print('=== Done ===')