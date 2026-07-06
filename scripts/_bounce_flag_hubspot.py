"""Flag bounced email contacts in HubSpot with notes explaining the bounce.
Sets hs_lead_status = UNQUALIFIED + adds engagement note per contact.
Verified from himalaya Gmail bounce analysis on 2026-07-06.
"""
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
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, e.read().decode()[:300]

today = datetime.date.today().isoformat()
now_iso = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

# All 5 bounced contacts verified in HubSpot from prior step
flag_targets = [
    {
        'contact_id': '509286368975',
        'name': 'Walter (W.) Laptew @ PEPOI',
        'email': 'w.laptew@pepoi.com.ph',
        'bounce_type': 'Server timeout (recipient server unreachable at 45.79.222.138)',
        'recovery': 'Retry in 24-48h or find alternate contact',
    },
    {
        'contact_id': '509286368974',
        'name': 'Walter Laptew',
        'email': 'walter.laptew@qpl.com.ph',
        'bounce_type': 'Address not found (550 No Such User Here)',
        'recovery': 'Verify email or use LinkedIn for Walter Laptew @ QPL',
    },
    {
        'contact_id': '475095398099',
        'name': 'Ernest Ursal',
        'email': 'ernest.ursal@kepcospc.com',
        'bounce_type': 'Address not found (550 5.1.1 - mailbox does not exist)',
        'recovery': 'Account does not exist - verify spelling or switch to LinkedIn',
    },
    {
        'contact_id': '512124164814',
        'name': 'Rochelle Alabanza',
        'email': 'rochellaa@gnpd.ph',
        'bounce_type': 'Address not found (550 5.1.1 - mailbox does not exist)',
        'recovery': 'Account does not exist - try GNPD general procurement email',
    },
    {
        'contact_id': '509350081224',
        'name': 'Roderick Fernandez',
        'email': 'roderick.fernandez@fdcui.com.ph',
        'bounce_type': 'Server timeout (recipient server unreachable at 45.79.222.138)',
        'recovery': 'Retry in 24-48h or switch to LinkedIn InMail',
    },
]

print('=== Flagging bounced contacts in HubSpot ===')
print(f'Targets: {len(flag_targets)}')
print()

results = []
for target in flag_targets:
    cid = target['contact_id']
    name = target['name']
    email = target['email']
    
    # Step 1: PATCH hs_lead_status = UNQUALIFIED
    sc1, d1 = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{cid}', {
        'properties': {'hs_lead_status': 'UNQUALIFIED'}
    })
    
    # Step 2: Add engagement note (associates to the contact)
    note_body = (
        f'**EMAIL BOUNCED - {today}**\n\n'
        f'Recipient: {name} <{email}>\n'
        f'Bounce type: {target["bounce_type"]}\n\n'
        f'Source: Himalaya IMAP bounce analysis of ECONARES Gmail inbox (rzh24.econares@gmail.com).\n\n'
        f'**Recovery action:** {target["recovery"]}\n\n'
        f'Flagged UNQUALIFIED to prevent repeat send until verified via alternate channel '
        f'(LinkedIn, contact form, or verified alternate email).'
    )
    sc2, d2 = http('POST', f'{BASE}/crm/v3/objects/notes', {
        'properties': {
            'hs_timestamp': now_iso,
            'hs_note_body': note_body,
        },
        'associations': [
            {'to': {'id': cid}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}
        ]
    })
    
    note_id = d2.get('id', '?') if isinstance(d2, dict) else '?'
    print(f'  [{sc1}/{sc2}] {cid} ({name[:30]:30s}) note={note_id}')
    if sc1 != 200:
        print(f'    PATCH warn: {d1}')
    if sc2 not in (200, 201):
        print(f'    NOTE warn: {d2}')
    results.append((cid, sc1, sc2))

print()
print('=== Summary ===')
success = sum(1 for _, s1, s2 in results if s1 == 200 and s2 in (200, 201))
print(f'Successfully flagged: {success}/{len(flag_targets)} contacts')
print()
print('NOTE: wlaptew@qpl.com.ph (without "er.") was NOT FOUND in HubSpot - skipped, no record to flag.')
