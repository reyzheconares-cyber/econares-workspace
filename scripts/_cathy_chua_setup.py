"""Cathy Chua enrichment + Rolando Ong note + task for email outreach to Cathy Chua."""
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

CATHY = '513052877555'           # Cathy None -> Cathy Chua
ROLANDO = '485315123943'          # Rolando Ong (referrer)
COMPANY = '322958059202'          # Century Peak Cement Manufacturing
PROCUREMENT_TEAM = '486865964752'  # info@centurypeakcement.com

# === Step 1: Update Cathy Chua ===
print('=== Step 1: Update Cathy Chua (513052877555) ===')
sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{CATHY}', {
    'properties': {
        'lastname': 'Chua',
        'email': 'cathy.chua@centurypeakcement.com',
        'jobtitle': 'Purchasing, Century Peak Cement Manufacturing (referral source: Rolando Ong, Procurement Manager). Handles Cathy Chua email inquiries.',
        'hs_buying_role': 'INFLUENCER'
    }
})
print(f'  PATCH Cathy Chua: HTTP {sc}')

# Read-back + PATCH jobtitle to restore truncation (HubSpot auto-shortens names)
sc, d = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{CATHY}', {
    'properties': {
        'jobtitle': 'Purchasing, Century Peak Cement Manufacturing. Referral source: Rolando Ong (Procurement Manager, rolando.ong@centurypeakcement.com). Will share direct phone number only after Cathy expresses consent. Recommended initial outreach via email.'
    }
})
print(f'  PATCH Cathy jobtitle (restored): HTTP {sc}')

# === Step 2: Add note to Cathy documenting the referral source ===
note_cathy = (
    f'**CONTACT ENRICHED - 2026-07-08**\n\n'
    f'Referral source: Rolando Ong (Procurement Manager, Century Peak Cement Manufacturing)\n'
    f'Email disclosed by Rolando: cathy.chua@centurypeakcement.com\n'
    f'Name confirmed: Cathy Chua\n'
    f'Role: Purchasing (Century Peak Cement Manufacturing)\n\n'
    f'ROLANDO\'S GUIDANCE (verbatim): "I can only give her number after her expressed instruction to do so and recommended we reach out via email first. He assured she would definitely answer."\n\n'
    f'ACTION: Reach out to Cathy via email first. Do NOT ask Rolando for phone number. Wait for Cathy to respond before requesting direct contact.\n\n'
    f'Strategy:\n'
    f'1. Send first email to cathy.chua@centurypeakcement.com (drafted separately, to be presented for your review)\n'
    f'2. Wait for response\n'
    f'3. If she responds positively, ask her permission to share her number with you\n'
    f'4. Then request Rolando to confirm (chicken-and-egg; Cathy is the gatekeeper)\n\n'
    f'Coal offer: Indonesian thermal coal, FOB Philippines ports (APAC trade terms; no DAP).\n'
    f'Coal demand: typical cement plant is 50,000-150,000 MT/yr depending on plant size and coal-vs-cement ratio.\n\n'
    f'Source: ECONARES CRM enrichment 2026-07-08 (user told me via chat).'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_cathy},
    'associations': [{'to': {'id': CATHY}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
})
print(f'  NOTE Cathy: HTTP {sc}')

# === Step 3: Add note to Rolando Ong documenting the referral ===
print()
print('=== Step 3: Add note to Rolando Ong (the referrer) ===')
note_rolando = (
    f'**REFERRAL PROVIDED - 2026-07-08**\n\n'
    f'Contact disclosed: Cathy Chua (cathy.chua@centurypeakcement.com)\n'
    f'Role at Century Peak Cement Manufacturing: Purchasing\n'
    f'Relationship: Rolando verified Cathy as the person in charge for email inquiries at CPC.\n\n'
    f'Rolando\'s guidance: "He can only give her number after her expressed instruction to do so and recommended we reach out via email first. He assured she would definitely answer."\n\n'
    f'ACTION FOR FUTURE: When Cathy is engaged and has provided consent, then ask Rolando for her direct number.\n\n'
    f'Note: User (RZH) may have misremembered Rolando\'s first name as "Allan" in chat - the actual contact is Rolando Ong.\n\n'
    f'Source: ECONARES CRM enrichment 2026-07-08 (user told me via chat).'
)
sc, d = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_timestamp': now_iso, 'hs_note_body': note_rolando},
    'associations': [{'to': {'id': ROLANDO}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}]
})
print(f'  NOTE Rolando: HTTP {sc}')

# === Step 4: Create task for email outreach (per user instruction: draft-and-present, never send directly) ===
print()
print('=== Step 4: Create task for email outreach ===')
TOMORROW_ISO = (datetime.datetime.utcnow() + datetime.timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M:%S.000Z')  # 4h from now
task_body = {
    'properties': {
        'hs_task_subject': 'Send email to Cathy Chua (cathy.chua@centurypeakcement.com) - CPC Purchasing - per Rolando Ong referral',
        'hs_task_body': (
            'Outreach via email per Rolando Ong\'s recommendation.\n\n'
            'KEY CONTEXT:\n'
            '- Cathy Chua is the person in charge for email inquiries at Century Peak Cement Manufacturing (CPC).\n'
            '- Email: cathy.chua@centurypeakcement.com\n'
            '- Referral source: Rolando Ong (Procurement Manager, rolando.ong@centurypeakcement.com).\n'
            '- Rolando\'s guidance: "can only give her number after her expressed instruction to do so and recommended we reach out via email first. He assured she would definitely answer."\n\n'
            'OFFER:\n'
            '- Indonesian thermal coal, FOB Philippines ports (APAC trade terms; no DAP).\n'
            '- CPC coal demand estimate: 50,000-150,000 MT/yr (typical cement plant).\n'
            '- Plant location: CPC plant in Naga, Cebu (or wherever their plant is - verify).\n\n'
            'NEXT STEPS:\n'
            '1. Send first email to cathy.chua@centurypeakcement.com (draft already prepared in vault - DRAFT file).\n'
            '2. Wait for response (Rolando assures she will answer).\n'
            '3. If response is positive, ask Cathy\'s consent to share her number.\n'
            '4. If consent given, ask Rolando to confirm/sharing her number.\n\n'
            'NOTE: Per user instruction "Draft and present external messages first; never send directly" - the email must be reviewed and approved by RZH before sending.\n\n'
            'Source: ECONARES CRM enrichment 2026-07-08 (user told me via chat).'
        ),
        'hs_task_status': 'NOT_STARTED',
        'hs_task_priority': 'HIGH',
        'hs_timestamp': TOMORROW_ISO
    }
}
# Add associations to the relevant objects
task_body['associations'] = [
    {'to': {'id': CATHY}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]},
    {'to': {'id': COMPANY}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 190}]},
    {'to': {'id': ROLANDO}, 'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 202}]}
]
sc, d = http('POST', f'{BASE}/crm/v3/objects/tasks', task_body)
print(f'  TASK: HTTP {sc}')

# === Step 5: Verify final state ===
print()
print('=== Step 5: Verify final state ===')
# Cathy
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'hs_object_id', 'operator': 'EQ', 'value': CATHY}]}], 'properties': ['firstname','lastname','email','jobtitle','hs_buying_role','associatedcompanyid'], 'limit': 5}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
for c in d.get('results',[]):
    p = c['properties']
    name = f'{p.get("firstname","")} {p.get("lastname","")}'.strip()
    print(f'  Cathy: {name} | email={p.get("email")} | job={(p.get("jobtitle") or "")[:100]}... | role={p.get("hs_buying_role")} | co={p.get("associatedcompanyid")}')

# Search for new task
import datetime as dt
yesterday = int((dt.datetime.utcnow() - dt.timedelta(minutes=10)).timestamp() * 1000)
body = json.dumps({
    'filterGroups': [{'filters': [{'propertyName': 'hs_timestamp', 'operator': 'GTE', 'value': str(yesterday)}]}],
    'properties': ['hs_task_subject', 'hs_task_status', 'hs_timestamp'],
    'limit': 5
}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/tasks/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as r:
    d = json.loads(r.read().decode())
print(f'  Recent tasks: {d.get("total",0)}')
for t in d.get('results',[]):
    p = t['properties']
    if 'Cathy' in (p.get('hs_task_subject') or ''):
        print(f'    [{t["id"]}] {p.get("hs_task_subject")} | due={p.get("hs_timestamp")} | status={p.get("hs_task_status")}')

print()
print('=== Done ===')