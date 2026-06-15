#!/usr/bin/env python3
"""Write Chen Bin's verified phone from Baosteel's own website."""
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


CID = '470632707816'
# Baosteel's own customer-service page (esales.baosteel.com) lists this contact:
# "Heavy Plate Management Department. Chen Bin Tel:021-26645296 Mob:13917813711
#  Email:chenbin02@baosteel.com"
# Same email as HubSpot: chenbin02@baosteel.com
# Phone chosen: mobile (most direct), E.164 format: +86 139 1781 3711
PHONE = '+86 139 1781 3711'

# Pre-write check
code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{CID}?properties=phone,jobtitle,company,email')
p = body.get('properties', {})
print(f"Pre-write check: HTTP {code}")
print(f"  phone: '{p.get('phone', '')}'")
print(f"  email: '{p.get('email', '')}'")
print(f"  company: '{p.get('company', '')}'")

# KYC guard: only write if pre-flight is truly empty
pre = p.get('phone', '')
if pre and pre != '':
    print(f"\n[KYC BLOCK] phone is not empty ('{pre}') - skipping write")
else:
    # PATCH
    code, body = http('PATCH', f'https://api.hubapi.com/crm/v3/objects/contacts/{CID}',
                      {"properties": {"phone": PHONE}})
    print(f"\nPATCH result: HTTP {code}")
    if code in (200, 201):
        print(f"  wrote phone: {PHONE}")
    else:
        print(f"  FAIL: {body}")

    # Read-back
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{CID}?properties=firstname,lastname,phone,jobtitle,company,email')
    if code == 200:
        p = body.get('properties', {})
        print(f"\nVerify read-back:")
        print(f"  name: {p.get('firstname', '')} {p.get('lastname', '')}")
        print(f"  phone: '{p.get('phone', '')}'")
        print(f"  email: '{p.get('email', '')}'")
        print(f"  company: '{p.get('company', '')}'")
        actual = p.get('phone', '')
        print(f"\n  RESULT: {'OK' if actual == PHONE else 'MISMATCH'}")
        print(f"  SOURCE: esales.baosteel.com/baosteel_products/salesSystem.do (Baosteel official customer-service page)")
