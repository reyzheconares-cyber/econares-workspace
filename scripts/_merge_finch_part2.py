#!/usr/bin/env python3
"""Merge remaining duplicates into the NEW canonical Ed Finch record."""
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

NEW_CANONICAL = '501895526098'
REMAINING_DUPS = ['488078159596', '488085684984']

print(f"=== MERGING REMAINING INTO NEW CANONICAL ({NEW_CANONICAL}) ===\n")
for dup in REMAINING_DUPS:
    payload = {
        "primaryObjectId": NEW_CANONICAL,
        "objectIdToMerge": dup
    }
    code, body = http('POST', 'https://api.hubapi.com/crm/v3/objects/contacts/merge', payload)
    if code in (200, 201, 204):
        print(f"  Merged {dup} into {NEW_CANONICAL}  OK")
        NEW_CANONICAL = body.get('id', NEW_CANONICAL) # Update canonical if it shifts again
    else:
        print(f"  FAIL merging {dup}: HTTP {code} {body}")

print(f"\n=== VERIFY FINAL CANONICAL ({NEW_CANONICAL}) ===")
code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{NEW_CANONICAL}?properties=email,hs_additional_emails')
if code == 200:
    p = body.get('properties', {})
    print(f"  Primary email: {p.get('email')}")
    print(f"  Additional emails: {p.get('hs_additional_emails')}")
