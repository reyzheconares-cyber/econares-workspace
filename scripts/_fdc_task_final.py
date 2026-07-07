"""Create final task with proper associations + delete the orphaned ones."""
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

# === Delete the orphaned task 381415880383 (has 0 company/contact associations) ===
TASK_OLD = '381415880383'
print('=== Delete old task (no company/contact associations) ===')
sc, d = http('DELETE', f'{BASE}/crm/v3/objects/tasks/{TASK_OLD}')
print(f'  DELETE: HTTP {sc}')

# === Create new task with proper associations at creation time ===
# Use the v3 default endpoint which accepts associations in the POST body
print()
print('=== Create new task with associations ===')
tomorrow_iso = (datetime.datetime.utcnow() + datetime.timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
now_iso = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

CANONICAL = '329640754913'
DEAL_BASE = '331864002293'
DEAL_EXPANSION = '331885143770'
CONTACT_EMAIL = '509350081224'

# Try the v4 POST with proper body format (v4 wants a list of association specs)
print()
print('--- Attempt 1: v4 with full list body ---')
url = f'{BASE}/crm/v4/objects/tasks'
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
    },
    'associations': [
        # Company association
        {'from': {'id': 'PLACEHOLDER_TASK_ID', 'type': '0-46'}, 'to': {'id': CANONICAL, 'type': '0-2'}, 'associationTypeId': 83},
        # Deal associations
        {'from': {'id': 'PLACEHOLDER_TASK_ID', 'type': '0-46'}, 'to': {'id': DEAL_BASE, 'type': '0-3'}, 'associationTypeId': 216},
        {'from': {'id': 'PLACEHOLDER_TASK_ID', 'type': '0-46'}, 'to': {'id': DEAL_EXPANSION, 'type': '0-3'}, 'associationTypeId': 216},
        # Contact association
        {'from': {'id': 'PLACEHOLDER_TASK_ID', 'type': '0-46'}, 'to': {'id': CONTACT_EMAIL, 'type': '0-1'}, 'associationTypeId': 87},
    ]
}
# Replace placeholder
body['associations'] = [
    {'to': {'id': t}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': tid}]}
    for t, tid in [(CANONICAL, 83), (DEAL_BASE, 216), (DEAL_EXPANSION, 216), (CONTACT_EMAIL, 87)]
]
sc, d = http('POST', f'{BASE}/crm/v3/objects/tasks', body)
print(f'  v3 POST with full associations: HTTP {sc}')
if isinstance(d, dict):
    if sc in (200, 201):
        new_task_id = d.get('id', '?')
        print(f'  Created task ID: {new_task_id}')
    else:
        msg = d.get('message', str(d)[:200])
        print(f'  Error: {msg}')

# === If still failed, fall back to incremental association approach ===
# Try default PUT for the missing 2 associations (company + contact) using the v3 default endpoint
# with the standard type IDs that worked for deals
if sc not in (200, 201):
    # Task was created without associations
    new_task_id = d.get('id') if isinstance(d, dict) else None
    print(f'\\nTask was created as {new_task_id} without associations. Adding incrementally...')
    if new_task_id:
        # For task->company, the working type is 83 (already worked for deals? No, it failed for company+contact)
        # Let me try the v3 default endpoint with the standard pattern
        for target_id, target_label, type_id in [
            (CANONICAL, 'companies', 279),  # try 279 for task->company
            (CANONICAL, 'companies', 65),   # try 65
            (CONTACT_EMAIL, 'contacts', 202),  # try 202 for task->contact
            (CONTACT_EMAIL, 'contacts', 203),
        ]:
            sc, d = http('PUT', f'{BASE}/crm/v3/objects/tasks/{new_task_id}/associations/{target_label}/{target_id}/{type_id}', body={})
            print(f'  Type {type_id}: HTTP {sc}')
            if sc in (200, 201, 204):
                break

# === Verify final state ===
print()
print('=== Final task state ===')
if sc in (200, 201):
    new_task_id = d.get('id') if isinstance(d, dict) else None
    if new_task_id:
        for label in ['companies', 'contacts', 'deals']:
            sc, d = http('GET', f'{BASE}/crm/v3/objects/tasks/{new_task_id}/associations/{label}')
            results = d.get('results', []) if isinstance(d, dict) else []
            print(f'  {label}: {len(results)} associations')

print()
print('=== Done ===')