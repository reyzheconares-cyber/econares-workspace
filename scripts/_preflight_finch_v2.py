#!/usr/bin/env python3
"""Check the 3 'duplicate' contacts and the canonical in detail, plus see if canonical already has buying_role set."""
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


# Canonical
print("=== CANONICAL ED FINCH (500247103197) ===\n")
code, body = http('GET', 'https://api.hubapi.com/crm/v3/objects/contacts/500247103197?properties=firstname,lastname,email,company,jobtitle,phone,lifecyclestage,hs_lead_status,hs_buying_role,hs_linkedin_url,createdate,lastmodifieddate')
if code == 200:
    p = body.get('properties', {})
    for k, v in p.items():
        if v:
            print(f"  {k}: {v}")

# Deals/companies associated with canonical
print("\n--- Canonical associations ---")
for kind in ('deals', 'companies'):
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/500247103197/associations/{kind}')
    if code == 200:
        ids = [a['id'] for a in body.get('results', [])]
        print(f"  {kind}: {ids}")

# Duplicates
print("\n=== 3 DUPLICATE CONTACTS ===\n")
for cid in ['488052007614', '488078159596', '488085684984']:
    print(f"--- {cid} ---")
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}?properties=firstname,lastname,email,company,jobtitle,phone,lifecyclestage,hs_lead_status,hs_buying_role,hs_linkedin_url,createdate,lastmodifieddate')
    if code == 200:
        p = body.get('properties', {})
        for k, v in p.items():
            if v is not None:
                if k == 'firstname' or k == 'lastname':
                    if v and v != 'None':
                        print(f"  {k}: {v}")
                else:
                    print(f"  {k}: {v}")
    for kind in ('deals', 'companies'):
        code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}/associations/{kind}')
        if code == 200:
            ids = [a['id'] for a in body.get('results', [])]
            if ids:
                print(f"  {kind}: {ids}")
    print()
