#!/usr/bin/env python3
"""Fill Jeffren Argame's company from his email domain (smgp.sanmiguel.com.ph = San Miguel Global Power)."""
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


CID = '489728100061'
# Email domain smgp.sanmiguel.com.ph -> San Miguel Global Power
# Multiple sources confirm: email domain + LinkedIn profile (Supply Chain Manager at SMC Global Power Holdings Corp.)
COMPANY = 'San Miguel Global Power Holdings Corp.'

# Pre-write check
code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{CID}?properties=company,email')
p = body.get('properties', {})
print(f"Pre-write check: HTTP {code}")
print(f"  company: '{p.get('company', '')}'")
print(f"  email: '{p.get('email', '')}'")

pre = p.get('company', '')
if pre and pre != '':
    print(f"\n[KYC BLOCK] company not empty - skip")
else:
    code, body = http('PATCH', f'https://api.hubapi.com/crm/v3/objects/contacts/{CID}',
                      {"properties": {"company": COMPANY}})
    print(f"\nPATCH result: HTTP {code}")
    if code in (200, 201):
        print(f"  wrote company: {COMPANY}")
    else:
        print(f"  FAIL: {body}")

    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{CID}?properties=company,email,firstname,lastname')
    if code == 200:
        p = body.get('properties', {})
        print(f"\nVerify read-back:")
        print(f"  name: {p.get('firstname', '')} {p.get('lastname', '')}")
        print(f"  company: '{p.get('company', '')}'")
        print(f"  email: '{p.get('email', '')}'")
        actual = p.get('company', '')
        print(f"\n  RESULT: {'OK' if actual == COMPANY else 'MISMATCH'}")
        print(f"  SOURCE: email domain smgp.sanmiguel.com.ph + LinkedIn profile cross-confirm")
