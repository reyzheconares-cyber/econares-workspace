#!/usr/bin/env python3
"""HubSpot API smoke test — verifies HUBSPOT_ACCESS_TOKEN can:
  1. Read the portal info
  2. List tasks filtered by the [Gmail prefix (same query the real sync uses)
  3. Fetch the SPC Power company record (sanity)

Exits non-zero on any failure. Does not write to HubSpot.
"""
import json
import os
import sys
import urllib.request
import urllib.error

HERMES_ENV = os.path.expanduser('~/.hermes/.env')

def load_token():
    with open(HERMES_ENV) as f:
        for line in f:
            s = line.lstrip()
            if s.startswith('export '):
                s = s[len('export '):]
            if s.startswith('HUBSPOT_ACCESS_TOKEN'):
                tok = s.split('=', 1)[1].strip().strip('"').strip("'")
                if tok:
                    return tok
    return None

def http(method, url, token, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    data = None
    if body is not None:
        data = json.dumps(body).encode('utf-8')
    try:
        with urllib.request.urlopen(req, data=data, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode('utf-8', errors='replace')[:400]
        return e.code, {'http_error': body_text}

def main():
    token = load_token()
    if not token:
        print('FAIL: HUBSPOT_ACCESS_TOKEN not found in', HERMES_ENV)
        sys.exit(2)
    print(f'Token loaded: {token[:15]}... ({len(token)} chars)')

    # 1. Portal info
    code, body = http('GET', 'https://api.hubapi.com/account-info/v3/details', token)
    print(f'[1/3] GET /account-info/v3/details  HTTP {code}')
    if code == 200:
        print(f'      portalId={body.get("portalId")}  accountType={body.get("accountType")}  companyCurrency={body.get("companyCurrency")}')
    else:
        print('      FAIL:', body)
        sys.exit(1)

    # 2. List [Gmail tasks (proves scope + the exact search the real sync does)
    search = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "hs_task_subject",
                "operator": "CONTAINS_TOKEN",
                "value": "[Gmail"
            }]
        }],
        "properties": ["hs_task_subject", "hs_task_status", "hs_createdate"],
        "limit": 10
    }
    code, body = http('POST', 'https://api.hubapi.com/crm/v3/objects/tasks/search', token, search)
    print(f'[2/3] POST /crm/v3/objects/tasks/search ([Gmail filter)  HTTP {code}')
    if code == 200:
        results = body.get('results', [])
        print(f'      {len(results)} existing [Gmail*] tasks (total in portal: {body.get("total", "?")})')
        for t in results[:5]:
            print(f'        - {t.get("id")} | {t.get("properties",{}).get("hs_task_subject","")[:60]}')
    else:
        print('      FAIL:', body)
        sys.exit(1)

    # 3. Fetch SPC Power (sanity check on the company we know exists)
    code, body = http('GET', 'https://api.hubapi.com/crm/v3/objects/companies/325115776729?properties=name,domain,industry', token)
    print(f'[3/3] GET /crm/v3/objects/companies/325115776729 (SPC Power)  HTTP {code}')
    if code == 200:
        props = body.get('properties', {})
        print(f'      name={props.get("name")}  domain={props.get("domain")}  industry={props.get("industry")}')
    else:
        print('      FAIL:', body)
        sys.exit(1)

    print()
    print('SMOKE_TEST_PASSED — token + scopes are good for the gmail_starred_hubspot_sync.py use case')

if __name__ == '__main__':
    main()
