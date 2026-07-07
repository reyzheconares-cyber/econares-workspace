"""Retry FDC cleanup - fix company note type + task creation."""
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

# === Retry company note with correct association type ===
print('=== Retry: Company-level note (type 202 not 210) ===')
company_note = (
    f'**EMAIL DELIVERY BOUNCE SUMMARY - {today}**\n\n'
    f'ECONARES has experienced repeated email delivery failures to recipients on the fdcui.com.ph domain '
    f'since initial outreach began.\n\n'
    f'**Affected recipients:**\n'
    f'- roderick.fernandez@fdcui.com.ph (Roderick Fernandez, Procurement Contact, FDCUI Taguig)\n\n'
    f'**Failure mode:**\n'
    f'Recipient server at IP 45.79.222.138 has been intermittently timing out since initial outreach. '
    f'Specific timestamps (UTC):\n'
    f'- 2026-06-29 22:39: First send - server timeout\n'
    f'- 2026-07-01 00:51: Bounce notification (no DNS error, just timeout)\n'
    f'- 2026-07-06 16:38 PHT (08:38 UTC): Retry attempt - server still unreachable\n\n'
    f'**Status:**\n'
    f'Email channel effectively DOWN. Switch to phone outreach. Landline on file: +63285751600.\n'
    f'If phone also unreachable, find alternate procurement contact at FDCUI Taguig HQ.\n\n'
    f'**Source IP:** 45.79.222.138 (hosted infrastructure - common with PEPOI which shares the same IP range)\n\n'
    f'Source: ECONARES CRM cleanup 2026-07-06.'
)
# Notes-to-company uses associationTypeId 202 (not 210)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': company_note},
    'associations': [{'to': {'id': CANONICAL}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
})
print(f'NOTE company (type 202): HTTP {sc}')
if sc not in (200, 201):
    print(f'  Error: {d}')

# === Retry task with simpler payload ===
print()
print('=== Retry: Task with correct types ===')

# Find RZH owner ID
sc, d = http('GET', f'{BASE}/crm/v3/owners')
rzh_owner_id = None
if sc == 200:
    for o in d.get('results', []):
        if o.get('email', '').lower() == 'rzh24.econares@gmail.com':
            rzh_owner_id = o.get('id')
            break
print(f'  RZH owner ID: {rzh_owner_id}')

# Build task - single association first
task_body = {
    'properties': {
        'hs_task_subject': 'Call FDCUI landline +63285751600 to reach procurement/Mr. Roderick Fernandez - log outcome',
        'hs_task_body': (
            'Email channel to fdcui.com.ph has been failing since 2026-06-29 (server 45.79.222.138 timeouts). '
            'Landline +63285751600 is the only working contact channel. Call and log outcome:\n\n'
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
}
if rzh_owner_id:
    task_body['properties']['hubspot_owner_id'] = rzh_owner_id

# Single association first
task_body['associations'] = [{'to': {'id': CANONICAL}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
sc, d = http('POST', f'{BASE}/crm/v3/objects/tasks', task_body)
print(f'TASK (single assoc to company): HTTP {sc}')
if sc not in (200, 201):
    print(f'  Error: {d}')

# If single assoc worked, add the other associations via the default association endpoint
if sc in (200, 201):
    task_id = d.get('id')
    print(f'  Task ID: {task_id}')
    # Default task association endpoint
    for target_id, target_type in [
        (DEAL_BASE, 214),
        (DEAL_EXPANSION, 214),
        (CONTACT_EMAIL, 202)
    ]:
        sc2, d2 = http('PUT', f'{BASE}/crm/v3/objects/tasks/{task_id}/associations/{target_id}/{target_type}', body={'associationCategory': 'HUBSPOT_DEFINED'})
        print(f'  Add association to {target_id} (type {target_type}): HTTP {sc2}')
        if sc2 not in (200, 201):
            print(f'    Error: {d2}')

print()
print('=== Done ===')