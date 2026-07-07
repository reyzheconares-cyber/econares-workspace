"""Final retry: FDC company note + task creation with correct object type associations."""
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
today = datetime.date.today().isoformat()
tomorrow_iso = (datetime.datetime.utcnow() + datetime.timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%S.000Z')

CANONICAL = '329640754913'
DEAL_BASE      = '331864002293'
DEAL_EXPANSION = '331885143770'
CONTACT_EMAIL  = '509350081224'

# === Company note via default association API ===
# The standard v3 notes API expects associations in form:
# associations: [{"to": {"id": X}, "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": Y}]}]
# Where Y for notes-to-company is 190 (HubSpot's default for notes->company, not 202 which is for notes->contact)

# Actually let me check what type works. Try 190 first.
print('=== Try company note with various association types ===')
company_note = (
    f'**EMAIL DELIVERY BOUNCE SUMMARY - {today}**\n\n'
    f'ECONARES has experienced repeated email delivery failures to recipients on the fdcui.com.ph domain.\n\n'
    f'**Affected:** roderick.fernandez@fdcui.com.ph (Roderick Fernandez, Procurement Contact, FDCUI Taguig)\n\n'
    f'**Failure mode:** Recipient server at IP 45.79.222.138 timing out.\n'
    f'Timestamps: 2026-06-29 22:39 UTC, 2026-07-01 00:51 UTC, 2026-07-06 08:38 UTC.\n\n'
    f'**Status:** Email channel DOWN. Switch to phone outreach. Landline: +63285751600.\n'
    f'Source: ECONARES CRM cleanup 2026-07-06.'
)

# Try the default associations endpoint to create note + link to company
note_body = {
    'properties': {
        'hs_timestamp': now_iso,
        'hs_note_body': company_note
    }
}
# Add association to company
note_body['associations'] = []

# The v4 associationTypeId for notes-to-companies is 190
# But let me try without any explicit type first
for assoc_type in [190, 214, 197, 279]:
    sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
        **note_body,
        'associations': [{'to': {'id': CANONICAL}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': assoc_type}]}]
    })
    print(f'  Try assocTypeId={assoc_type}: HTTP {sc}')
    if sc in (200, 201):
        nid = d.get('id') if isinstance(d, dict) else d
        print(f'  SUCCESS: {nid}')
        break
    else:
        # print short error
        if isinstance(d, dict):
            err = d.get('message', str(d)[:200])
            print(f'  Error: {err}')

# If none worked, try the default-association endpoint (PUT) for note-to-company
# We need a note ID first - create without association, then add via PUT
print()
print('=== Fallback: create note first, then associate via PUT ===')
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', note_body)
print(f'Create note (no assoc): HTTP {sc}')
if sc in (200, 201):
    note_id = d.get('id') if isinstance(d, dict) else None
    print(f'  Note ID: {note_id}')
    if note_id:
        # PUT the association - try various types
        for assoc_type in [190, 197, 279, 214]:
            sc2, d2 = http('PUT', f'{BASE}/crm/v4/objects/notes/{note_id}/associations/companies/{CANONICAL}/{assoc_type}', body={})
            print(f'  v4 PUT assoc to company (type {assoc_type}): HTTP {sc2}')
            if sc2 in (200, 201, 204):
                print(f'  SUCCESS')
                break
else:
    print(f'  Error: {d}')

# === Task creation ===
print()
print('=== Task creation (retry) ===')
# Find RZH owner ID
sc, d = http('GET', f'{BASE}/crm/v3/owners')
rzh_owner_id = None
if sc == 200:
    for o in d.get('results', []):
        if o.get('email', '').lower() == 'rzh24.econares@gmail.com':
            rzh_owner_id = o.get('id')
            break
print(f'  RZH owner ID: {rzh_owner_id}')

# Build task - try without owner first, then with owner
task_props = {
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
if rzh_owner_id:
    task_props['hubspot_owner_id'] = rzh_owner_id

# Task with NO associations
sc, d = http('POST', f'{BASE}/crm/v3/objects/tasks', {'properties': task_props})
print(f'Task (no assoc): HTTP {sc}')
if sc in (200, 201):
    task_id = d.get('id') if isinstance(d, dict) else None
    print(f'  Task ID: {task_id}')

    # Now add associations via PUT (v4)
    for target_id, target_type_id, label in [
        (CANONICAL, 83, 'company'),    # task-to-company
        (DEAL_BASE, 216, 'deal1'),
        (DEAL_EXPANSION, 216, 'deal2'),
        (CONTACT_EMAIL, 87, 'contact')   # task-to-contact
    ]:
        sc2, d2 = http('PUT', f'{BASE}/crm/v4/objects/tasks/{task_id}/associations/{label}s/{target_id}/{target_type_id}', body={})
        print(f'  v4 PUT assoc to {label} {target_id} (type {target_type_id}): HTTP {sc2}')
else:
    print(f'  Error: {d}')

print()
print('=== Done ===')