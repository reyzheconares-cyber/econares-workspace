import json, urllib.request, datetime
ENV = r'C:\Users\reyma\.hermes\.env'
T = next(line.split('=',1)[1].strip().strip('"').strip("'") for line in open(ENV) if line.lstrip().startswith('HUBSPOT_ACCESS_TOKEN'))

def http(method, url, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, e.read().decode()[:400]

BASE='https://api.hubapi.com'
HNPCL_ID='331693873869'
parent_desc = ('Hinduja Group of Companies - UK-India family-owned conglomerate founded 1914. Forbes 2024 net worth ~$22B; '
               'UK Rich List #1 family. Chairman India: Ashok Hinduja; Europe: Prakash Hinduja; Shom Hinduja leads renewables. '
               'Sectors: Ashok Leyland, banking, power (HNPCL), renewables, IT, media, healthcare. ECONARES angle: monitoring parent only; '
               'coal opportunity is via HNPCL 1,040 MW Visakhapatnam power plant.')
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {'properties': {
    'name':'Hinduja Group of Companies',
    'domain':'hindujagroup.com',
    'industry':'INVESTMENT_MANAGEMENT',
    'phone':'+44 20 7389 8000',
    'address':'123 Victoria Street, London SW1E 6DE, United Kingdom (Hinduja Group HQ)',
    'city':'London',
    'country':'United Kingdom',
    'website':'https://www.hindujagroup.com',
    'hs_target_account':'tier_2',
    'numberofemployees':200000,
    'description':parent_desc
}})
print(f"CREATE Hinduja parent: {sc} | {r.get('id') if sc in (200,201) else r.get('message','')[:250]}")
PARENT_ID = r.get('id') if sc in (200,201) else None
if PARENT_ID:
    sc2, r2 = http('GET', f'{BASE}/crm/v3/objects/companies/{PARENT_ID}?properties=name')
    actual = r2.get('properties',{}).get('name') if sc2==200 else None
    if actual != 'Hinduja Group of Companies':
        print(f'  name auto-truncated: {actual} - restoring')
        sc3, _ = http('PATCH', f'{BASE}/crm/v3/objects/companies/{PARENT_ID}', {'properties': {'name':'Hinduja Group of Companies'}})
        print('  PATCH name:', sc3)
    note_body = '<p><strong>Hinduja parent supplemental CRM note:</strong> Parent record created after valid HubSpot industry correction (INVESTMENT_MANAGEMENT; CONGLOMERATE invalid). HNPCL record already created as tier_1 utilities/coal-power target. ECONARES angle remains HNPCL supplemental Indonesian thermal coal for blending/peak demand via Vizag port; parent is monitoring only.</p>'
    ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
    scn, nr = http('POST', f'{BASE}/crm/v3/objects/notes', {'properties': {'hs_note_body': note_body, 'hs_timestamp': ts}})
    print(f"CREATE supplemental note: {scn} | {nr.get('id') if scn in (200,201) else nr.get('message','')[:200]}")
    if scn in (200,201):
        note_id = nr['id']
        for oid in [PARENT_ID, HNPCL_ID]:
            sca, _ = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/companies/{oid}/note_to_company', {})
            print(f'  note assoc to {oid}: {sca}')

print('\n=== FINAL VERIFY COMPANIES ===')
for label, oid in [('Hinduja Group', PARENT_ID), ('HNPCL', HNPCL_ID)]:
    if not oid:
        continue
    scv, co = http('GET', f'{BASE}/crm/v3/objects/companies/{oid}?properties=name,industry,phone,address,city,state,country,website,hs_target_account,numberofemployees,description')
    print(f'--- {label} ({oid}) status {scv} ---')
    p=co.get('properties',{})
    for k in ['name','industry','phone','address','city','state','country','website','hs_target_account','numberofemployees']:
        print(f'  {k}: {p.get(k)}')
    desc=p.get('description') or ''
    print(f'  description: {len(desc)} chars - {desc[:120]}...')

print('\n=== FINAL VERIFY CONTACTS DIRECT ===')
for cid in ['512552966848','512577861344','512623458016']:
    scc, c = http('GET', f'{BASE}/crm/v3/objects/contacts/{cid}?properties=firstname,lastname,associatedcompanyid,hs_buying_role,hs_lead_status,jobtitle,hs_linkedin_url')
    p=c.get('properties',{})
    print(f"  {cid}: {p.get('firstname')} {p.get('lastname')} | co:{p.get('associatedcompanyid')} | role:{p.get('hs_buying_role')} | status:{p.get('hs_lead_status')}")
    print(f"    linkedin: {p.get('hs_linkedin_url')}")
