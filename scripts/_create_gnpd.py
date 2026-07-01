import json, os, urllib.request
ENV = os.path.expanduser('~/.hermes/.env')
T = next(line.split('=', 1)[1].strip().strip('"').strip("'") for line in open(ENV) if line.lstrip().startswith('HUBSPOT_ACCESS_TOKEN'))

def http(method, url, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except:
            return e.code, e.read().decode()[:400]

base = 'https://api.hubapi.com'

# STEP 1 — Create Company record
co_props = {
    'name': 'GNPower Dinginin Ltd. Co.',
    'domain': 'gnpd.ph',
    'industry': 'UTILITIES',
    'description': '1,336 MW supercritical coal-fired power plant (2x668 MW) in Mariveles, Bataan. Joint venture of AboitizPower (Therma Power) 50% + AC Energy Holdings (Ayala) 50%. Combined with sister plant GMEC: 1,968 MW total = largest single-site coal complex in Philippines. Long-term Indonesian coal off-take (~3.5-4M MT/yr). 30 distribution utility customers + 2 RES. Plant site: Sitio Dinginin, Brgy. Alas Asin, Mariveles, Bataan 2105. HQ: Unit 1905 Orient Square Bldg, Pasig City 1605.',
    'phone': '+63286384575',
    'address': 'Sitio Dinginin, Barangay Alas Asin, Mariveles, Bataan 2105',
    'city': 'Mariveles',
    'state': 'Bataan',
    'country': 'Philippines',
    'website': 'https://gnpd.ph',
    'numberofemployees': 250,
    'hs_target_account': 'tier_1'
}
sc, co = http('POST', f'{base}/crm/v3/objects/companies', {'properties': co_props})
print('=== COMPANY CREATE ===')
print('status:', sc)
if sc in (200, 201):
    co_id = co['id']
    print('company_id:', co_id)
else:
    print(co)
    raise SystemExit

# STEP 2 — Create 4 contacts (verified fields only — no inferred emails)
contacts = [
    {
        'firstname': 'Rochelle',
        'lastname': 'Alabanza',
        'jobtitle': 'Strategic Sourcing and Procurement Operations Manager',
        'associatedcompanyid': co_id,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'CHAMPION',
        'hs_linkedin_url': 'https://ph.linkedin.com/in/rochelle-alabanza-b16a08194',
        'source': 'LinkedIn (verified Mar 2024-present)'
    },
    {
        'firstname': 'Alfredo',
        'lastname': 'Cortez',
        'jobtitle': 'Procurement Operation Specialist',
        'associatedcompanyid': co_id,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'INFLUENCER',
        'hs_linkedin_url': 'https://ph.linkedin.com/in/alfredo-jr-cortez-8230b970',
        'source': 'LinkedIn (verified Jan 2024-present)'
    },
    {
        'firstname': 'Helen',
        'lastname': 'Aruta',
        'jobtitle': 'Supervisor, Procurement Operational',
        'associatedcompanyid': co_id,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'INFLUENCER',
        'source': 'ZoomInfo (verified, email masked)'
    },
    {
        'firstname': 'Claudine',
        'lastname': 'Alingal',
        'jobtitle': 'Chief Operating Officer',
        'associatedcompanyid': co_id,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'DECISION_MAKER',
        'source': 'RocketReach management roster'
    }
]

created_contacts = []
for c in contacts:
    src = c.pop('source')
    sc2, ct = http('POST', f'{base}/crm/v3/objects/contacts', {'properties': c})
    print(f'\n=== CONTACT: {c["firstname"]} {c["lastname"]} ({c["jobtitle"]}) ===')
    print('source:', src)
    print('status:', sc2)
    if sc2 in (200, 201):
        print('contact_id:', ct['id'])
        created_contacts.append({'id': ct['id'], 'name': f'{c["firstname"]} {c["lastname"]}', 'role': c['jobtitle']})
    else:
        print(ct)

# Final summary
print('\n\n=== SUMMARY ===')
print(f'Company: GNPower Dinginin Ltd. Co. (ID: {co_id})')
print(f'Contacts created: {len(created_contacts)}')
for c in created_contacts:
    print(f'  - {c["name"]} | {c["role"]} (ID: {c["id"]})')
print('\nEmails: NOT written (KYC safe — pattern not individually verified)')
print('Manual email lookup via: (a) LinkedIn InMail, (b) GNPD switchboard +63286384575, (c) GMEC peer intro via Leah Mabulay (Pagbilao)')