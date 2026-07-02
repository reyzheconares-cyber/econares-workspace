"""
Tsingshan fix - simpler version
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

# Industry enum check
print('=== Industry enum check ===')
sc, r = http('GET', f'{BASE}/crm/v3/properties/companies/industry')
if sc == 200:
    all_vals = [v.get('value') for v in r.get('options', [])]
    print(f'  Total options: {len(all_vals)}')
    print(f'  Metal-related: {[v for v in all_vals if "METAL" in v or "STEEL" in v or "IRON" in v]}')
    print(f'  Mfg-related: {[v for v in all_vals if "MFG" in v]}')
    print(f'  Industry-related: {[v for v in all_vals if "INDUST" in v or "AUTOMAT" in v or "MACHIN" in v]}')

print()
print('=== Contact audit: search by lastname ===')
for ln, fn in [('Li', 'Rhea'), ('Stephanie', 'Juliet'), ('Lin', 'Samuel')]:
    body = json.dumps({'filterGroups': [{'filters': [{'propertyName': 'lastname', 'operator': 'EQ', 'value': ln}]}], 'properties': ['firstname','lastname','email','jobtitle','associatedcompanyid','hs_buying_role']}).encode()
    req = urllib.request.Request(f'{BASE}/crm/v3/objects/contacts/search', data=body, method='POST')
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read().decode())
    print(f'  {fn} {ln}: {d.get("total",0)} matches')
    for c in d.get('results', []):
        p2 = c['properties']
        print(f"    ID:{c['id']} | {p2.get('firstname')} {p2.get('lastname')} | co:{p2.get('associatedcompanyid')} | role:{p2.get('hs_buying_role')}")