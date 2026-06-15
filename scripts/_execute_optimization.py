#!/usr/bin/env python3
"""Execute Step 1 (Deal Naming) and Step 2 (Target Accounts)."""
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

print("=== STEP 1: STANDARDIZE DEAL NAMING ===")
# Fetch all deals and their associated companies
code, body = http('GET', 'https://api.hubapi.com/crm/v3/objects/deals?properties=dealname&associations=companies')
deals = body.get('results', [])
target_companies = set()

for d in deals:
    did = d['id']
    old_name = d['properties'].get('dealname', '')
    
    # Get associated company name
    companies = d.get('associations', {}).get('companies', {}).get('results', [])
    company_name = "Unknown Company"
    if companies:
        cid = companies[0]['id']
        target_companies.add(cid) # Save for Step 2
        ccode, cbody = http('GET', f'https://api.hubapi.com/crm/v3/objects/companies/{cid}?properties=name')
        if ccode == 200:
            company_name = cbody.get('properties', {}).get('name', 'Unknown Company')
            
    # Clean up the name format: [Company Name] - [Details]
    new_name = old_name
    details = old_name
    
    # Extract details by removing the company name if it exists in the deal name
    if "—" in details:
        parts = details.split("—")
        details = parts[0].strip() if company_name.lower() in parts[1].lower() else parts[1].strip()
    elif "-" in details:
        parts = details.split("-")
        details = parts[0].strip() if company_name.lower() in parts[1].lower() else parts[1].strip()
        
    # Standardize
    if "Supply" not in details and "Pilot" not in details and "Buyer" not in details:
        details += " Supply"
        
    if not old_name.startswith(f"{company_name} -"):
        new_name = f"{company_name} - {details.replace(company_name, '').strip(' -—')}"
        
        # Patch the deal
        pcode, pbody = http('PATCH', f'https://api.hubapi.com/crm/v3/objects/deals/{did}', {"properties": {"dealname": new_name}})
        if pcode in (200, 201):
            print(f"  [RENAMED] {old_name}  ->  {new_name}")
        else:
            print(f"  [FAIL] {old_name}: {pbody}")
    else:
        print(f"  [OK] {old_name} (already standardized)")

print("\n=== STEP 2: TAG TARGET ACCOUNTS ===")
for cid in target_companies:
    pcode, pbody = http('PATCH', f'https://api.hubapi.com/crm/v3/objects/companies/{cid}', {"properties": {"hs_target_account": "true"}})
    if pcode in (200, 201):
        name = pbody.get('properties', {}).get('name', cid)
        print(f"  [TAGGED] {name} (ID: {cid}) is now a Target Account")
    else:
        print(f"  [FAIL] Company {cid}: {pbody}")
