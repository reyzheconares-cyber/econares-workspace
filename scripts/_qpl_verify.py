"""
Verification: confirm both new contacts (Chaiwut + Davie) actually exist and are linked to canonical QPL.
Also fix Walter Laptew's missing role/status.
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
        try: return e.code, json.loads(e.read().decode())
        except: return e.code, e.read().decode()[:300]

BASE = 'https://api.hubapi.com'

# Fix Walter Laptew role + status
sc, r = http('PATCH', f'{BASE}/crm/v3/objects/contacts/509286368974', {
    'properties': {
        'hs_buying_role': 'INFLUENCER',
        'hs_lead_status': 'NEW'
    }
})
print(f'PATCH Walter Laptew: {sc}')

# Read-back both new contacts
for cid in ['512132585157', '512244792034']:
    sc, ct = http('GET', f'{BASE}/crm/v3/objects/contacts/{cid}?properties=firstname,lastname,jobtitle,hs_buying_role,hs_linkedin_url,associatedcompanyid,hs_lead_status,lifecyclestage')
    if sc == 200:
        p = ct.get('properties', {})
        print(f"\n  ID:{cid}")
        for k in ['firstname','lastname','jobtitle','hs_buying_role','hs_linkedin_url','associatedcompanyid','hs_lead_status','lifecyclestage']:
            print(f'    {k}: {p.get(k)}')

# Final count: contacts at QPL
body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'associatedcompanyid', 'operator': 'EQ', 'value': '326532899525'}]}], 'properties': ['firstname','lastname','jobtitle','hs_buying_role']}).encode()
req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
req.add_header('Authorization', f'Bearer {T}')
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as resp:
    d = json.loads(resp.read().decode())
print(f'\nFinal contacts at QPL (canonical): {d.get("total",0)}')
for c in d.get('results', []):
    p2 = c['properties']
    print(f"  ID:{c['id']} | {p2.get('firstname')} {p2.get('lastname')} | {p2.get('jobtitle')} | role:{p2.get('hs_buying_role')}")