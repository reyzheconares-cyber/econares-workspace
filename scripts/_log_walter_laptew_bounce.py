"""Log 2026-07-08 soft-bounce to walter.laptew@pepoi.com.ph + cleanup both Laptew contacts."""
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

WALTER_FULL = '514454579940'   # walter.laptew@pepoi.com.ph
WALTER_SHORT = '509286368975'  # w.laptew@pepoi.com.ph
PEPOI_COMPANY = '330875977444'

# === Step 1: Add soft-bounce note to BOTH Waltew contacts ===
print('=== Step 1: Add soft-bounce note to both Waltew contacts ===')
note_both = (
    f'**SOFT-BOUNCE (DELAY) - 2026-07-08 ~13:00 PHT (05:00 UTC)**\n\n'
    f'Channel: Gmail SMTP retry notification\n'
    f'Recipient: walter.laptew@pepoi.com.ph (and the alternate form w.laptew@pepoi.com.ph - same person)\n'
    f'Status: Delivery incomplete. Gmail will retry for 46 more hours. Will be notified if delivery fails permanently.\n\n'
    f'This is the SAME server IP (45.79.222.138) and same problem as the FDCUI bounces:\n'
    f'- Both PEPOI and FDCUI use shared infrastructure at 45.79.222.138\n'
    f'- 4 FDCUI bounces + 1 PEPOI bounce within 24 hours suggests a regional email-server outage in the PH\n'
    f'- Since 2026-06-29 (FDCUI first bounce) and 2026-06-30 (PEPOI first bounce), email channel to pepoi.com.ph is effectively DOWN\n\n'
    f'ACTION: Pause email outreach to pepoi.com.ph. Switch to landline. PEPOI contact number not yet confirmed in HubSpot - obtain via alternate route.\n\n'
    f'Source: ECONARES CRM tracking 2026-07-08.'
)
for cid, name in [(WALTER_FULL, 'walter.laptew'), (WALTER_SHORT, 'w.laptew')]:
    sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
        'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_both},
        'associations': [{'to': {'id': cid}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
    })
    print(f'  NOTE {name} ({cid}): HTTP {sc}')

# === Step 2: Flag both contacts as UNQUALIFIED ===
print()
print('=== Step 2: Flag both contacts UNQUALIFIED ===')
for cid, name in [(WALTER_FULL, 'walter.laptew'), (WALTER_SHORT, 'w.laptew')]:
    sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{cid}', {
        'properties': {'hs_lead_status': 'UNQUALIFIED'}
    })
    print(f'  PATCH {name} status=UNQUALIFIED: HTTP {sc}')

# === Step 3: Add company-level note to PEPOI ===
print()
print('=== Step 3: Add company-level note to PEPOI (330875977444) ===')
note_company = (
    f'**PEPOI EMAIL CHANNEL DOWN - 2026-07-08**\n\n'
    f'Server: pepoi.com.ph 45.79.222.138 - same shared infrastructure as FDCUI (45.79.222.138)\n'
    f'Affected: walter.laptew@pepoi.com.ph (and alternate w.laptew@pepoi.com.ph)\n'
    f'Bounce history:\n'
    f'- 2026-06-30: Initial hard bounce (timeout at 45.79.222.138)\n'
    f'- 2026-07-01: 2 hard bounces (delay + failure)\n'
    f'- 2026-07-08 ~13:00 PHT: Soft-bounce delay (Gmail retry 46h)\n\n'
    f'Both Waltew contacts marked UNQUALIFIED. Email channel paused.\n'
    f'Next step: obtain PEPOI contact number via alternate channel (LinkedIn / company website / referral).\n\n'
    f'Source: ECONARES CRM tracking 2026-07-08.'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_company},
    'associations': [{'to': {'id': PEPOI_COMPANY}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 190}]}]
})
print(f'  NOTE PEPOI company: HTTP {sc}')

# === Step 4: Verify final state ===
print()
print('=== Step 4: Verify final state ===')
for cid, name in [(WALTER_FULL, 'walter.laptew'), (WALTER_SHORT, 'w.laptew')]:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_object_id', 'operator': 'EQ', 'value': cid}]}], 'properties': ['firstname','lastname','email','hs_lead_status','hs_object_id'], 'limit': 5}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read().decode())
    for c in d.get('results',[]):
        p = c['properties']
        name_actual = f'{p.get("firstname","")} {p.get("lastname","")}'.strip()
        print(f'  Contact {c["id"]} ({name}): {name_actual} | email={p.get("email")} | status={p.get("hs_lead_status")}')

print()
print('=== Done ===')