#!/usr/bin/env python3
"""Merge 3 bulk-ore.com duplicate aliases into the canonical Ed Finch record.
Industry best practice: merge alias records into the canonical so engagement history aggregates.
"""
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

CANONICAL = '500247103197'
DUPLICATES = ['488052007614', '488078159596', '488085684984']

print(f"=== MERGING 3 ALIASES INTO CANONICAL ED FINCH ({CANONICAL}) ===\n")
for dup in DUPLICATES:
    payload = {
        "primaryObjectId": CANONICAL,
        "objectIdToMerge": dup
    }
    code, body = http('POST', 'https://api.hubapi.com/crm/v3/objects/contacts/merge', payload)
    if code in (200, 201, 204):
        print(f"  Merged {dup} into {CANONICAL}  OK")
    else:
        print(f"  FAIL merging {dup}: HTTP {code} {body}")

print("\n=== VERIFY CANONICAL AFTER MERGE ===")
code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{CANONICAL}?properties=email,hs_additional_emails')
if code == 200:
    p = body.get('properties', {})
    print(f"  Primary email: {p.get('email')}")
    print(f"  Additional emails: {p.get('hs_additional_emails')}")
