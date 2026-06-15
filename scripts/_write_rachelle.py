#!/usr/bin/env python3
"""Write Rachelle Vinas's LinkedIn URL."""
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


CID = '484496948954'
URL = 'https://ph.linkedin.com/in/rachellevi%C3%B1as'

# Pre-write check
code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{CID}?properties=hs_linkedin_url,jobtitle,company,email,phone')
p = body.get('properties', {})
print(f"Pre-write check: HTTP {code}")
for k, v in p.items():
    if v:
        print(f"  {k}: {v}")

pre = p.get('hs_linkedin_url', '')
if pre and pre != '':
    print(f"\n[KYC BLOCK] hs_linkedin_url not empty - skip")
else:
    code, body = http('PATCH', f'https://api.hubapi.com/crm/v3/objects/contacts/{CID}',
                      {"properties": {"hs_linkedin_url": URL}})
    print(f"\nPATCH result: HTTP {code}")
    if code in (200, 201):
        print(f"  wrote: {URL}")
    else:
        print(f"  FAIL: {body}")

    # Read-back
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{CID}?properties=firstname,lastname,hs_linkedin_url,jobtitle,company,phone')
    if code == 200:
        p = body.get('properties', {})
        print(f"\nVerify read-back:")
        print(f"  name: {p.get('firstname', '')} {p.get('lastname', '')}")
        print(f"  hs_linkedin_url: '{p.get('hs_linkedin_url', '')}'")
        print(f"  jobtitle: {p.get('jobtitle', '')}")
        print(f"  company: {p.get('company', '')}")
        actual = p.get('hs_linkedin_url', '')
        print(f"\n  RESULT: {'OK' if actual == URL else 'MISMATCH'}")
        print(f"  NOTE: LinkedIn shows current employer = Tokyu Tobishima Megawide JV, not Aboitiz Construction. FLAGGED for user review.")
