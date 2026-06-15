#!/usr/bin/env python3
"""REVERT John Rey Hisoler's hs_linkedin_url to original KYC-compliant value."""
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


CID = '464524351190'
ORIGINAL = 'https://www.linkedin.com/in/john-rey-hisoler-9199b934'

code, body = http('PATCH', f'https://api.hubapi.com/crm/v3/objects/contacts/{CID}',
                  {"properties": {"hs_linkedin_url": ORIGINAL}})
print(f"REVERT PATCH: HTTP {code}")
if code in (200, 201):
    print(f"  reverted to: {ORIGINAL}")
else:
    print(f"  FAIL: {body}")

# Verify
code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{CID}?properties=hs_linkedin_url')
print(f"\nFinal value: '{body.get('properties', {}).get('hs_linkedin_url', '')}'")
