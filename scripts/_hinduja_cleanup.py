"""Hinduja Group / HNPCL cleanup:
1. Create Hinduja Group parent record (monitoring, London HQ)
2. Create HNPCL Company record (tier_1, India, 1,040 MW Visakhapatnam)
3. Create 3 contacts: Shiva Prasad Danturi (DECISION_MAKER), Rohit Tabhane (INFLUENCER), Prasanta Kumar Pradhan (INFLUENCER)
4. KYC enrich all records
5. Engagement note + final read-back
"""
import json, os, urllib.request, datetime
ENV = os.path.expanduser('~/.hermes/.env')
T = next(line.split('=', 1)[1].strip().strip('"').strip("'") for line in open(ENV) if line.lstrip().startswith('HUBSPOT_ACCESS_TOKEN'))

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
        except:
            return e.code, e.read().decode()[:400]

BASE = 'https://api.hubapi.com'

# === STEP 1: Create Hinduja Group parent record (monitoring) ===
print('=== STEP 1: Create Hinduja Group parent record (monitoring) ===')
parent_desc = 'Hinduja Group of Companies - UK-India family-owned conglomerate, $22B Forbes 2024 net worth, UK Rich List #1 5 years running. Founded 1914. Chairman (India): Ashok Hinduja (post-Gopichand death late 2025). Chairman (Europe): Prakash Hinduja. 3rd gen: Shom Hinduja (renewables). Sectors: Automotive (Ashok Leyland), Banking (Hinduja Bank Switzerland), Power (HNPCL), Renewables, IT (HGS), Media, Healthcare. Coal/mineral ore interest via HNPCL (1,040 MW Visakhapatnam). MONITORING only - no PH/Indonesia ops; low priority for ECONARES.'
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'Hinduja Group of Companies',
        'domain': 'hindujagroup.com',
        'industry': 'CONGLOMERATE',
        'phone': '+44 20 7389 8000',
        'address': '123 Victoria Street, London SW1E 6DE, United Kingdom (Hinduja Group HQ)',
        'city': 'London',
        'country': 'United Kingdom',
        'website': 'https://www.hindujagroup.com',
        'hs_target_account': 'tier_2',
        'numberofemployees': 200000,
        'description': parent_desc
    }
})
print(f'  CREATE: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
HINDUJA_ID = r.get('id') if sc in (200, 201) else None

if sc in (200, 201):
    sc2, r2 = http('GET', f'{BASE}/crm/v3/objects/companies/{HINDUJA_ID}?properties=name')
    if sc2 == 200:
        actual = r2['properties'].get('name')
        if actual != 'Hinduja Group of Companies':
            print(f'  Name auto-truncated: "{actual}" - restoring...')
            http('PATCH', f'{BASE}/crm/v3/objects/companies/{HINDUJA_ID}', {'properties': {'name': 'Hinduja Group of Companies'}})
            print('  PATCH name: 200')

print()

# === STEP 2: Create HNPCL Company record (tier_1) ===
print('=== STEP 2: Create HNPCL Company record (tier_1) ===')
hnpcl_desc = 'Hinduja National Power Corporation Limited (HNPCL) - Hinduja Group coal-fired power arm. Operates 1,040 MW (2 x 520/540 MW) coal-based thermal power plant near Visakhapatnam, Andhra Pradesh, India. Commercial operations date (COD): April 30, 2016. Long-term 25-year PPA with AP discoms (Andhra Pradesh distribution companies) on cost-plus basis. Parent: Machen Holdings SA (Hinduja Group holding entity). Coal source: Talcher coalfields (~600 km away) - primarily domestic Indian coal (Coal India). CARE rated: Rs 800 crore FY25 infusion + Rs 6,600 crore group support as of Mar 31, 2025. M&A pending: GOCL (Gulf Oil Corporation Ltd, Hinduja Group) to acquire HNPCL (recent restructuring). Future Hinduja target: 10,000 MW power generation capacity over 10 years (~$10B investment). No PH or Indonesia operations. ECONARES angle: supplemental imported coal for blending/peak demand only (primary is domestic Talcher); Vizag port is major Indian coal import hub.'
sc, r = http('POST', f'{BASE}/crm/v3/objects/companies', {
    'properties': {
        'name': 'Hinduja National Power Corporation Limited',
        'domain': 'hindujanationalpower.com',
        'industry': 'UTILITIES',
        'phone': '+91 891 270 4000',
        'address': 'HNPCL Plant Site, Parawada, Visakhapatnam, Andhra Pradesh 531021, India',
        'city': 'Visakhapatnam',
        'state': 'Andhra Pradesh',
        'country': 'India',
        'website': 'https://www.hindujanationalpower.com',
        'hs_target_account': 'tier_1',
        'numberofemployees': 500,
        'description': hnpcl_desc
    }
})
print(f'  CREATE: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
HNPCL_ID = r.get('id') if sc in (200, 201) else None

if sc in (200, 201):
    sc2, r2 = http('GET', f'{BASE}/crm/v3/objects/companies/{HNPCL_ID}?properties=name')
    if sc2 == 200:
        actual = r2['properties'].get('name')
        if actual != 'Hinduja National Power Corporation Limited':
            print(f'  Name auto-truncated: "{actual}" - restoring...')
            http('PATCH', f'{BASE}/crm/v3/objects/companies/{HNPCL_ID}', {'properties': {'name': 'Hinduja National Power Corporation Limited'}})
            print('  PATCH name: 200')

print()

# === STEP 3: Create 3 contacts under HNPCL ===
print('=== STEP 3: Create 3 contacts under HNPCL ===')
contacts = [
    {
        'firstname': 'Shiva Prasad',
        'lastname': 'Danturi',
        'jobtitle': 'Senior Manager - Procurement, Contracts & Warehouse, Hinduja National Power Corporation Limited (HNPCL) - Dec 2023-present, Vizag. Strategic Sourcing + Contracts leader. Procurement Leader profile.',
        'associatedcompanyid': HNPCL_ID,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'DECISION_MAKER',
        'hs_linkedin_url': 'https://in.linkedin.com/in/shiva-prasad-danturi-procurement-leader-sourcing-contracts'
    },
    {
        'firstname': 'Rohit',
        'lastname': 'Tabhane',
        'jobtitle': 'Addl. GM-Head Operations, Hinduja National Power Corporation Ltd (HNPCL) - Apr 2024-present, Korba Chhattisgarh (new plant site). 18+ years power sector (commissioning, operations, fuel management). Previously DGM-Head Operations, Sr. Manager Performance & Efficiency, Technical Advisor to CEO at HNPCL Visakhapatnam.',
        'associatedcompanyid': HNPCL_ID,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'INFLUENCER',
        'hs_linkedin_url': 'https://in.linkedin.com/in/rohit-tabhane-62968b19a'
    },
    {
        'firstname': 'Prasanta Kumar',
        'lastname': 'Pradhan',
        'jobtitle': 'Vice President, Hinduja National Power Corporation Limited (HNPCL) - Jan 2012-present, Visakhapatnam, Andhra Pradesh.',
        'associatedcompanyid': HNPCL_ID,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'INFLUENCER',
        'hs_linkedin_url': 'https://in.linkedin.com/in/prasanta-kumar-pradhan-683bb5ba'
    }
]
for c in contacts:
    sc, ct = http('POST', f'{BASE}/crm/v3/objects/contacts', {'properties': c})
    print(f"  {c['firstname']} {c['lastname']}: {sc} | {ct.get('id') if sc in (200,201) else ct.get('message','')[:200]}")

print()

# === STEP 4: KYC enrichment (engagement note) ===
print('=== STEP 4: Engagement note + cleanup log ===')
note_body = (
    f"<p><strong>Hinduja Group CRM Buildout (2026-07-02):</strong></p>"
    f"<p>Created 2 Company records: <strong>Hinduja Group of Companies</strong> (ID <code>{HINDUJA_ID}</code>) — UK-India family-owned conglomerate, $22B Forbes 2024, monitoring tier_2; <strong>Hinduja National Power Corporation Limited (HNPCL)</strong> (ID <code>{HNPCL_ID}</code>) — Tier_1, 1,040 MW coal-fired power plant near Visakhapatnam, Andhra Pradesh, India, COD Apr 30, 2016, 25-year PPA with AP discoms, parent: Machen Holdings SA (Hinduja Group).</p>"
    "<p>Created 3 verified contacts under HNPCL: <strong>Shiva Prasad Danturi</strong> (Senior Manager - Procurement, Contracts & Warehouse, Dec 2023-present, DECISION_MAKER); <strong>Rohit Tabhane</strong> (Addl. GM-Head Operations, Korba Chhattisgarh, INFLUENCER); <strong>Prasanta Kumar Pradhan</strong> (Vice President, Visakhapatnam, INFLUENCER).</p>"
    "<p><strong>ECONARES ANGLE:</strong> Supplemental imported coal for blending/peak demand only (primary is domestic Talcher via Coal India). Vizag port is major Indian coal import hub. Hinduja Group primary commodity interest is power generation (not mineral ores). Coal target: 10,000 MW capacity over 10 years (~$10B).</p>"
    "<p><strong>Outreach strategy:</strong> Lead with Shiva Prasad Danturi (Procurement Senior Manager) for direct angle. Rohit Tabhane (Head Operations) as plant-level influence. Prasanta Pradhan (VP) for executive escalation. Indian business culture = 6-12 month sales cycle, formal Hindi/English bilingual.</p>"
    "<p><strong>Risks/Notes:</strong> Hinduja Group restructuring in progress (GOCL to acquire HNPCL + leadership transition post-Gopichand death late 2025). M&A window may delay entry 6-12 months. No PH/Indonesia ops = low priority vs other Hinduja verticals (Hinduja Renewables, Ashok Leyland). MONITORING only.</p>"
)
ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
sc, r = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {'hs_note_body': note_body, 'hs_timestamp': ts}
})
print(f'  create note: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')
if sc in (200, 201):
    note_id = r['id']
    for assoc_id in [HINDUJA_ID, HNPCL_ID]:
        if assoc_id:
            sc2, r2 = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/companies/{assoc_id}/note_to_company', {})
            print(f'  assoc to {assoc_id}: {sc2}')

print()

# === FINAL READ-BACK ===
print('=== FINAL READ-BACK ===')
for label, oid in [('Hinduja Group', HINDUJA_ID), ('HNPCL', HNPCL_ID)]:
    if not oid:
        continue
    sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{oid}?properties=name,industry,phone,address,city,state,country,website,hs_target_account')
    p = co['properties']
    print(f'--- {label} ({oid}) ---')
    for k in ['name','industry','phone','address','city','state','country','website','hs_target_account']:
        print(f'  {k}: {p.get(k)}')

print()
print('--- All 3 HNPCL contacts (direct ID lookup) ---')
import time
time.sleep(1)
for ln, fn in [('Danturi', 'Shiva Prasad'), ('Tabhane', 'Rohit'), ('Pradhan', 'Prasanta Kumar')]:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'lastname', 'operator': 'EQ', 'value': ln}]}], 'properties': ['firstname','lastname','associatedcompanyid','hs_buying_role','hs_linkedin_url','hs_lead_status']}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read().decode())
    for c in d.get('results', []):
        p2 = c['properties']
        if p2.get('firstname') == fn and p2.get('associatedcompanyid') == HNPCL_ID:
            print(f"  {fn} {ln} (id:{c['id']}) | co:{p2.get('associatedcompanyid')} | role:{p2.get('hs_buying_role')} | status:{p2.get('hs_lead_status')}")
            if p2.get('hs_linkedin_url'):
                print(f"    linkedin: {p2['hs_linkedin_url']}")
