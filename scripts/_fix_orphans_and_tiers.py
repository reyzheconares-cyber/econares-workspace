#!/usr/bin/env python3
"""Fix orphaned deals and properly tag Tier 1 Target Accounts."""
import json
import os
import urllib.request
import urllib.error

ENV = os.path.expanduser('~/.hermes/.env')

def tok():
    with open(ENV) as f:
        for line in f:
            s = line.lstrip()
            if s.startswith('export '):
                s = s[7:]
            if s.startswith('HUBSPOT_ACCESS_TOKEN'):
                return s.split('=', 1)[1].strip().strip('"').strip("'")
    return None

T = tok()

def http(m, u, b=None):
    r = urllib.request.Request(u, method=m)
    r.add_header('Authorization', f'Bearer {T}')
    r.add_header('Content-Type', 'application/json')
    d = json.dumps(b).encode() if b is not None else None
    try:
        with urllib.request.urlopen(r, data=d, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return e.code, {'err': e.read().decode()[:500]}

# 1. Fetch all companies to map names to IDs
print("=== MAPPING COMPANIES ===")
code, body = http('GET', 'https://api.hubapi.com/crm/v3/objects/companies?limit=100&properties=name')
company_map = {}
if code == 200:
    for c in body.get('results', []):
        name = str(c['properties'].get('name') or '').lower()
        company_map[name] = c['id']

# Manual overrides for tricky names
overrides = {
    'mgen': next((id for n, id in company_map.items() if 'mgen' in n), None),
    'holcim': next((id for n, id in company_map.items() if 'holcim' in n), None),
    'yunding': next((id for n, id in company_map.items() if 'yunding' in n), None)
}

# 2. Fix Orphan Deals
print("\n=== FIXING ORPHAN DEALS ===")
code, body = http('GET', 'https://api.hubapi.com/crm/v3/objects/deals?properties=dealname&associations=companies')
deals = body.get('results', [])
target_company_ids = set()

for d in deals:
    did = d['id']
    name = d['properties'].get('dealname', '')
    companies = d.get('associations', {}).get('companies', {}).get('results', [])
    
    cid_to_link = None
    if not companies:
        name_lower = name.lower()
        if 'mgen' in name_lower: cid_to_link = overrides['mgen']
        elif 'holcim' in name_lower: cid_to_link = overrides['holcim']
        elif 'yunding' in name_lower: cid_to_link = overrides['yunding']
        
        if cid_to_link:
            # Associate Deal to Company (v4 API is safer per earlier tests)
            acode, abody = http('PUT', f'https://api.hubapi.com/crm/v4/objects/deals/{did}/associations/default/companies/{cid_to_link}')
            if acode == 200:
                print(f"  [LINKED] Deal '{name}' to Company ID {cid_to_link}")
                target_company_ids.add(cid_to_link)
            else:
                print(f"  [FAIL LINK] {name}: {abody}")
        else:
            print(f"  [ORPHAN UNRESOLVED] Deal '{name}' - no matching company found.")
    else:
        target_company_ids.add(companies[0]['id'])

# 3. Tag Target Accounts as tier_1
print("\n=== TAGGING TIER 1 TARGET ACCOUNTS ===")
for cid in target_company_ids:
    pcode, pbody = http('PATCH', f'https://api.hubapi.com/crm/v3/objects/companies/{cid}', {"properties": {"hs_target_account": "tier_1"}})
    if pcode in (200, 201):
        cname = pbody.get('properties', {}).get('name', cid)
        print(f"  [SUCCESS] {cname} is now a Tier 1 Target Account")
    else:
        print(f"  [FAIL] {cid}: {pbody}")
