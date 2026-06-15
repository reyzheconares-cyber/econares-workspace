#!/usr/bin/env python3
"""Step-by-step HubSpot CRM optimization: Pre-flight for Deals and Target Accounts."""
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

# 1. Check existing deals for naming convention
print("=== CURRENT DEALS ===")
code, body = http('GET', 'https://api.hubapi.com/crm/v3/objects/deals?properties=dealname,dealstage,hs_lastmodifieddate')
if code == 200:
    deals = body.get('results', [])
    for d in deals:
        print(f"  {d['id']} | {d['properties'].get('dealname')} | Stage: {d['properties'].get('dealstage')}")
else:
    print(f"Failed to fetch deals: {code} {body}")

# 2. Check hs_target_account property on Companies
print("\n=== COMPANY PROPERTY: hs_target_account ===")
code, body = http('GET', 'https://api.hubapi.com/crm/v3/properties/companies/hs_target_account')
if code == 200:
    print(f"  Property exists! Type: {body.get('type')}")
else:
    print(f"  Property check failed: {code} {body}")

# 3. Pull top companies to mark as Target Accounts
print("\n=== TOP COMPANIES BY ASSOCIATED DEALS/CONTACTS ===")
code, body = http('GET', 'https://api.hubapi.com/crm/v3/objects/companies?properties=name,hs_target_account&limit=10')
if code == 200:
    for c in body.get('results', []):
        print(f"  {c['id']} | {c['properties'].get('name')} | Target Account: {c['properties'].get('hs_target_account')}")
