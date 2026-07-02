"""Tsingshan KYC enrich v3 - keep MINING_METALS, add all other fields, audit orphans."""
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

# PATCH with all fields except industry
print('=== STEP 1: KYC enrich Tsingshan (keeping MINING_METALS) ===')
desc = (
    "Tsingshan Holding Group (青山控股集团) - Chinese private conglomerate. "
    "WORLD'S LARGEST stainless steel producer + WORLD'S LARGEST nickel producer (since 2022). "
    "Founded 1988 by Xiang Guangda in Wenzhou, Zhejiang. "
    "Annual revenue $56B+ USD. 110,000+ employees. "
    "Indonesia Morowali Industrial Park (IMIP) = 2,000+ hectares, world's largest nickel industrial park; "
    "vertical integration: mining to Ni-Cr-Fe smelting to stainless steel to hot/cold rolling. "
    "POSCO JV announced Sep 2025 (2M MT stainless). "
    "Antam invested $102M (2024). "
    "2021-2022 LME nickel crisis: Tsingshan lost $1B shorting nickel; later disbanded futures team. "
    "CONTEXT: Indonesian smelters (including Tsingshan) are NOW importing Philippine nickel ore - "
    "51.3% YoY import growth in 2025 (15.84M MT). "
    "ECONARES angle: PH saprolite/limonite nickel ore supply to IMIP."
)
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/{CANONICAL}', {
    'properties': {
        'name': 'Tsingshan Holding Group',
        'domain': 'tssgroup.com.cn',
        'phone': '+86 0577 8206-1300',
        'address': 'Tsingshan Building, Wenzhou, Zhejiang Province, China',
        'city': 'Wenzhou',
        'state': 'Zhejiang',
        'country': 'China',
        'website': 'https://www.tssgroup.com.cn',
        'hs_target_account': 'tier_1',
        'numberofemployees': 110000,
        'description': desc
    }
})
print(f'  PATCH: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')

print()
print('=== STEP 2: Audit orphan contacts on canonical ===')
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'associatedcompanyid', 'operator': 'EQ', 'value': CANONICAL}]}], 'properties': ['firstname','lastname','email','jobtitle','hs_buying_role','lifecycle']}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as resp:
    d = json.loads(resp.read().decode())
print(f'  Contacts on canonical: {d.get("total",0)}')
for c in d.get('results', []):
    p2 = c['properties']
    print(f"    ID:{c['id']} | name={p2.get('firstname')!r} {p2.get('lastname')!r} | jobtitle={p2.get('jobtitle')!r} | role={p2.get('hs_buying_role')!r} | lifecycle={p2.get('lifecycle')!r}")
