"""FDC Misamis cleanup: merge 3 companies into 1, reassign contacts, update deals, add notes, create task."""
import json, urllib.request, datetime

ENV = r'C:\Users\reyma\.hermes\.env'
with open(ENV, 'r', encoding='utf-8') as f:
    T = None
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

CANONICAL = '329640754913'    # FDC Misamis Power Corporation
EXPANSION = '329322443499'    # FDC Misamis 6x135 MW Expansion (to be deleted)
THIRD     = '330861127367'    # FDC Misamis (to be deleted, has phone + email)

CONTACT_EXPANSION = '506636552925'  # Roderick Fernandez (Expansion) - to reassign
CONTACT_EMAIL     = '509350081224'  # Roderick (with email) - to reassign
CONTACT_CANONICAL = '506450586331'  # Roderick Fernandez (already on canonical) - keep

DEAL_BASE      = '331864002293'  # FDC Misamis - Coal - 500k MT/yr Villanueva
DEAL_EXPANSION = '331885143770'  # FDC Misamis Expansion - Coal - Forward Demand 1.5-2M MT/yr
DEALSTAGE      = '3410654913'     # 20% stage

DEAL_NOTE_BUYING_SIGNALS = 'Buying Signals: 405 MW baseload, expansion planning 6x135 MW (probable 60–70%).'
DEAL_NOTE_STRATEGIC = 'Strategic Notes: Email delivery repeatedly failing to roderick.fernandez@fdcui.com.ph (fdcui.com.ph 45.79.222.138 timed out Jun29–Jul7). Landline +63285751600 on file. Treat current outreach as stalled until voice contact confirmed.'
DEAL_NOTE_OUTREACH = 'Outreach Strategy: Immediate phone call to landline; if unreachable, find alternate procurement contact at FDCUI Taguig; do NOT send further emails until server issue resolved.'

DEAL_NOTE_TEXT = f'{DEAL_NOTE_BUYING_SIGNALS}\n\n{DEAL_NOTE_STRATEGIC}\n\n{DEAL_NOTE_OUTREACH}'

# === Step 1: Reassign both contacts to the canonical company ===
print('=== Step 1: Reassign contacts to canonical ===')

# Contact 506636552925 (was on EXPANSION)
sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{CONTACT_EXPANSION}', {
    'properties': {
        'associatedcompanyid': CANONICAL,
        'jobtitle': 'Procurement Contact, FDCUI Taguig (FDC Misamis site + 6x135 MW Expansion)'
    }
})
print(f'PATCH contact {CONTACT_EXPANSION} (was on Expansion): HTTP {sc}')

# Contact 509350081224 (was on THIRD) - this one has the email
# User wants: "Set primary contact: roderick.fernandez@fdcui.com.ph (keep email on file but mark as delivery-failed)."
# So: keep the email, but mark as delivery-failed
sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{CONTACT_EMAIL}', {
    'properties': {
        'associatedcompanyid': CANONICAL,
        'jobtitle': 'Procurement Contact, FDCUI Taguig (email delivery-failed 2026-07-06)',
        'hs_lead_status': 'UNQUALIFIED'  # delivery-failed = disqualify for now
    }
})
print(f'PATCH contact {CONTACT_EMAIL} (was on 3rd, marked delivery-failed): HTTP {sc}')

# Add a note to contact 509350081224 explaining the status
note_email = (
    f'**EMAIL DELIVERY FAILED - 2026-07-06**\n\n'
    f'Email roderick.fernandez@fdcui.com.ph is KEPT on file but marked delivery-failed.\n\n'
    f'Bounce history:\n'
    f'- 2026-06-29 22:39 UTC: Initial send to roderick.fernandez@fdcui.com.ph — server timeout at IP 45.79.222.138\n'
    f'- 2026-07-01 00:51 UTC: Same bounce (re-tried)\n'
    f'- 2026-07-06 16:38 PHT: Retry attempted, server still unreachable\n\n'
    f'Decision: Pause email outreach to this address. Try landline +63285751600 instead. '
    f'If landline also unreachable, find alternate procurement contact at FDCUI Taguig HQ.\n\n'
    f'Source: ECONARES CRM cleanup 2026-07-06.'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_email},
    'associations': [{'to': {'id': CONTACT_EMAIL}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
})
print(f'NOTE contact {CONTACT_EMAIL}: HTTP {sc}')

# === Step 2: Delete the 2 merged-into companies ===
print()
print('=== Step 2: Delete merged-into companies ===')
for cid in [EXPANSION, THIRD]:
    print(f'\\nDeleting company {cid}...')
    sc, d = http('DELETE', f'{BASE}/crm/v3/objects/companies/{cid}')
    print(f'  DELETE: HTTP {sc}')
    if sc == 204:
        print(f'  DELETED')
    else:
        print(f'  Warn: {d}')

# === Step 3: Update both deals to dealstage 3410654913 (20%) with the note ===
print()
print('=== Step 3: Update deals to dealstage 3410654913 + add deal notes ===')
for did, deal_label in [(DEAL_BASE, '500k MT/yr Villanueva'), (DEAL_EXPANSION, 'Expansion 1.5-2M MT/yr')]:
    print(f'\\nDeal {did} ({deal_label}):')
    # Update dealstage
    sc, d = http('PATCH', f'{BASE}/crm/v3/objects/deals/{did}', {
        'properties': {
            'dealstage': DEALSTAGE
        }
    })
    print(f'  PATCH dealstage: HTTP {sc}')
    # Add a note with the 3 sections
    sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
        'properties': {'hs_timestamp': now_iso, 'hs_note_body': DEAL_NOTE_TEXT},
        'associations': [{'to': {'id': did}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 214}]}]
    })
    note_id = d.get('id', '?') if isinstance(d, dict) else '?'
    print(f'  NOTE deal: HTTP {sc} | id={note_id}')

# === Step 4: Add a company-level note on the canonical with bounce summary ===
print()
print('=== Step 4: Company-level bounce summary note ===')
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
    f'**Source IP:** 45.79.222.138 (hosted infrastructure — common with PEPOI which shares the same IP range)\n\n'
    f'Source: ECONARES CRM cleanup 2026-07-06.'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': company_note},
    'associations': [{'to': {'id': CANONICAL}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 210}]}]
})
print(f'NOTE company bounce summary: HTTP {sc}')

# === Step 5: Create task assigned to RZH: call FDCUI landline ===
print()
print('=== Step 5: Create call task ===')
# Find RZH's user ID
sc, d = http('GET', f'{BASE}/crm/v3/owners')
rzh_owner_id = None
if sc == 200:
    for o in d.get('results', []):
        if o.get('email', '').lower() == 'rzh24.econares@gmail.com':
            rzh_owner_id = o.get('id')
            print(f'  RZH owner ID: {rzh_owner_id}')
            break

task_body = {
    'properties': {
        'hs_task_subject': 'Call FDCUI landline +63285751600 to reach procurement/Mr. Roderick Fernandez — log outcome',
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
    print(f'  Task assigned to RZH (owner {rzh_owner_id})')
task_body['associations'] = [
    {'to': {'id': CANONICAL}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 210}]},
    {'to': {'id': DEAL_BASE}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 214}]},
    {'to': {'id': DEAL_EXPANSION}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 214}]},
    {'to': {'id': CONTACT_EMAIL}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}
]
sc, d = http('POST', f'{BASE}/crm/v3/objects/tasks', task_body)
task_id = d.get('id', '?') if isinstance(d, dict) else '?'
print(f'TASK created: HTTP {sc} | id={task_id} | due {tomorrow_iso}')

# === Step 6: Verify final state ===
print()
print('=== Step 6: Verify final state ===')

# Verify only 1 FDC company remains
for q in ['FDC Misamis', 'FDC Utilities', 'FDCUI']:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'name', 'operator': 'CONTAINS_TOKEN', 'value': q}]}], 'properties': ['name','hs_object_id','num_associated_contacts'], 'limit': 10}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/companies/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read().decode())
    if d.get('total',0) > 0:
        for c in d.get('results',[]):
            p = c['properties']
            print(f'  Co {c["id"]}: {p.get("name","")} | contacts={p.get("num_associated_contacts","")}')

# Verify deal stages
print()
for did in [DEAL_BASE, DEAL_EXPANSION]:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_object_id', 'operator': 'EQ', 'value': did}]}], 'properties': ['dealname','dealstage','hs_object_id'], 'limit': 5}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/deals/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read().decode())
    for c in d.get('results',[]):
        p = c['properties']
        print(f'  Deal {c["id"]}: {p.get("dealname","")} | stage={p.get("dealstage","")}')

# Verify the 2 deleted companies are gone
print()
for cid in [EXPANSION, THIRD]:
    sc, d = http('GET', f'{BASE}/crm/v3/objects/companies/{cid}')
    print(f'  Company {cid}: HTTP {sc}', '(expected 404)')

# Verify both Roderick contacts now on canonical
print()
for cid in [CONTACT_CANONICAL, CONTACT_EXPANSION, CONTACT_EMAIL]:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_object_id', 'operator': 'EQ', 'value': cid}]}], 'properties': ['firstname','lastname','email','jobtitle','associatedcompanyid','hs_lead_status'], 'limit': 5}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read().decode())
    for c in d.get('results',[]):
        p = c['properties']
        name = f'{p.get("firstname","")} {p.get("lastname","")}'.strip()
        print(f'  Contact {c["id"]}: {name} | email={p.get("email","")} | co={p.get("associatedcompanyid","")} | status={p.get("hs_lead_status","")}')

print()
print('=== Done ===')