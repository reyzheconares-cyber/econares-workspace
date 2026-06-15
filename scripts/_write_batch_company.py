#!/usr/bin/env python3
"""Write company for 15 blank-company contacts in batch (KYC: only fill if truly blank).
Sources are the contacts' own email domains - 1st-party signal of their employer."""
import json
import os
import urllib.request
import urllib.error
import time

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


candidates = json.load(open(r'C:/Users/reyma/AppData/Local/Temp/blank_company_candidates.json'))

print("=== STEP 1: Verify all are truly blank before any write ===\n")
for c in candidates:
    cid = c['id']
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}?properties=company')
    p = body.get('properties', {})
    cur = p.get('company', '')
    flag = 'BLANK' if not cur or cur == '' else f'NON-BLANK:{cur}'
    print(f"  {cid}  {c['name'][:30]:<30}  company='{cur}'  [{flag}]")

print("\n=== STEP 2: PATCH (only the ones still blank) ===\n")
written = []
skipped = []
for c in candidates:
    cid = c['id']
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}?properties=company')
    p = body.get('properties', {})
    cur = (p.get('company') or '').strip()
    if cur and cur != '':
        skipped.append((cid, c['name'], f"pre-write check: company='{cur}'"))
        continue

    code, body = http('PATCH', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}',
                      {"properties": {"company": c['suggested']}})
    if code in (200, 201):
        written.append((cid, c['name'], c['suggested'], c['domain']))
        print(f"  {cid}  {c['name'][:30]:<30}  {c['domain']:<35}  ->  {c['suggested']}")
    else:
        print(f"  {cid}  FAIL: {code} {body}")

print(f"\n  WROTE: {len(written)}")
print(f"  SKIPPED: {len(skipped)}")

print("\n=== STEP 3: Verify by read-back ===\n")
ok = 0
for cid, nm, company, dom in written:
    code, body = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}?properties=company')
    if code == 200:
        actual = (body.get('properties', {}).get('company') or '')
        if actual == company:
            ok += 1
        else:
            print(f"  MISMATCH {cid}: expected '{company}', got '{actual}'")
print(f"  {ok}/{len(written)} verified OK")
