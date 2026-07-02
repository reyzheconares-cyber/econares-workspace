"""
Tsingshan cleanup:
1. Audit complete — canonical = 317279658732 (most recent, has fields, correct domain)
2. Delete 4 duplicates: 318019375841, 318036019913, 318037146341, 322003687158
3. KYC enrich canonical: address, city, state, country=China, industry=MANUFACTURING, description, tier_1
4. Create 3 contacts: Rhea Li (DECISION_MAKER), Juliet Stephanie (INFLUENCER), Samuel Lin (INFLUENCER)
"""
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
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except:
            return e.code, e.read().decode()[:400]

BASE = 'https://api.hubapi.com'
CANONICAL = '317279658732'
DUPLICATES = ['318019375841', '318036019913', '318037146341', '322003687158']

# === STEP 1: Delete 4 duplicates ===
print('=== STEP 1: Delete 4 duplicate Tsingshan records ===')
for dup in DUPLICATES:
    sc, r = http('DELETE', f'{BASE}/crm/v3/objects/companies/{dup}')
    print(f'  DELETE {dup}: {sc}')

print()

# === STEP 2: KYC enrich canonical record ===
print('=== STEP 2: KYC enrich canonical (317279658732) ===')
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/{CANONICAL}', {
    'properties': {
        'name': 'Tsingshan Holding Group',
        'domain': 'tssgroup.com.cn',
        'industry': 'MANUFACTURING',
        'phone': '+86 0577 8206-1300',
        'address': 'Tsingshan Building, Wenzhou, Zhejiang Province, China',
        'city': 'Wenzhou',
        'state': 'Zhejiang',
        'country': 'China',
        'website': 'https://www.tssgroup.com.cn',
        'hs_target_account': 'tier_1',
        'numberofemployees': 110000,
        'description': 'Tsingshan Holding Group (青山控股集团) — Chinese private conglomerate. WORLD\'S LARGEST stainless steel producer + WORLD\'S LARGEST nickel producer (since 2022). Founded 1988 by Xiang Guangda in Wenzhou, Zhejiang. Annual revenue $56B+ USD. 110,000+ employees. Indonesia Morowali Industrial Park (IMIP) = 2,000+ hectares, world\'s largest nickel industrial park; vertical integration: mining → Ni-Cr-Fe smelting → stainless steel → hot/cold rolling. POSCO JV announced Sep 2025 (2M MT stainless). Antam invested $102M (2024). 2021-2022 LME nickel crisis: Tsingshan lost $1B shorting nickel; later disbanded futures team. CONTEXT: Indonesian smelters (including Tsingshan) are NOW importing Philippine nickel ore — 51.3% YoY import growth in 2025 (15.84M MT). ECONARES angle: PH saprolite/limonite nickel ore supply to IMIP.'
    }
})
print(f'  PATCH canonical: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')

print()

# === STEP 3: Create 3 contacts ===
print('=== STEP 3: Create 3 contacts ===')
contacts = [
    {
        'firstname': 'Rhea',
        'lastname': 'Li',
        'jobtitle': 'Procurement at Board of Directors, Tsingshan Steel (Sep 2015-present) — handles Nickel Cathodes, Nickel Briquette, Ferro-nickel',
        'associatedcompanyid': CANONICAL,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'DECISION_MAKER',
        'hs_linkedin_url': 'https://cn.linkedin.com/in/rhea-li-b470b5102'
    },
    {
        'firstname': 'Juliet',
        'lastname': 'Stephanie',
        'jobtitle': 'Purchasing Administrator, Tsingshan Holding Group (Aug 2019-present, Indonesia operations)',
        'associatedcompanyid': CANONICAL,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'INFLUENCER',
        'hs_linkedin_url': 'https://sg.linkedin.com/in/juliet-stephanie-6877b17b'
    },
    {
        'firstname': 'Samuel',
        'lastname': 'Lin',
        'jobtitle': 'Stainless Steel Department (Mobile: +86 186-6554-0448, Tel: 0086-757-8206-1300, email: linguojia@tshint.com) — VERIFIED EMAIL',
        'associatedcompanyid': CANONICAL,
        'hs_lead_status': 'NEW',
        'lifecyclestage': 'lead',
        'hs_buying_role': 'INFLUENCER'
    }
]
for c in contacts:
    sc, ct = http('POST', f'{BASE}/crm/v3/objects/contacts', {'properties': c})
    print(f"  {c['firstname']} {c['lastname']}: {sc} | {ct.get('id') if sc in (200,201) else ct.get('message','')[:200]}")

print()

# === STEP 4: Final read-back ===
print('=== STEP 4: Read-back verification ===')
sc, co = http('GET', f'{BASE}/crm/v3/objects/companies/{CANONICAL}?properties=name,industry,phone,address,city,state,country,website,hs_target_account')
p = co['properties']
for k in ['name','industry','phone','address','city','state','country','website','hs_target_account']:
    print(f'  {k}: {p.get(k)}')

print()
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'associatedcompanyid', 'operator': 'EQ', 'value': CANONICAL}]}], 'properties': ['firstname','lastname','jobtitle','hs_buying_role']}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as resp:
    d = json.loads(resp.read().decode())
print(f'Contacts at canonical: {d.get("total",0)}')
for c in d.get('results', []):
    p2 = c['properties']
    print(f"  {p2.get('firstname')} {p2.get('lastname')} | {p2.get('jobtitle')} | role:{p2.get('hs_buying_role')}")