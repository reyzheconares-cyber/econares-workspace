#!/usr/bin/env python3
"""
hubspot_token_health.py — Daily health check for the HUBSPOT_ACCESS_TOKEN.

Exits 0 if the token is valid and has the required scopes.
Exits 1 if the token is missing, invalid, or missing required scopes.
Exits 2 if HubSpot API is unreachable (transient — retry).

Logs to stdout AND to ~/ECONARES_WORKSPACE/logs/hubspot_health.log.

Usage:
  python hubspot_token_health.py            # check now
  python hubspot_token_health.py --quiet    # only log on FAIL
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERMES_ENV = Path(os.path.expanduser('~/.hermes/.env'))
LOG_FILE = Path(os.path.expanduser('~/ECONARES_WORKSPACE/logs/hubspot_health.log'))

REQUIRED_SCOPES = [
    'crm.objects.contacts',
    'crm.objects.companies',
    'crm.objects.deals',
    'crm.objects.tasks',
]


def load_token():
    if not HERMES_ENV.is_file():
        return None
    for line in HERMES_ENV.read_text(encoding='utf-8').splitlines():
        s = line.lstrip()
        if s.startswith('export '):
            s = s[len('export '):]
        if s.startswith('HUBSPOT_ACCESS_TOKEN'):
            tok = s.split('=', 1)[1].strip().strip('"').strip("'")
            if tok:
                return tok
    return None


def http_get(url, token):
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.status, json.loads(r.read().decode('utf-8'))


def log(msg, quiet, force=False):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    if not quiet or force:
        print(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    token = load_token()
    if not token:
        log('FAIL: HUBSPOT_ACCESS_TOKEN missing from ~/.hermes/.env', args.quiet, force=True)
        sys.exit(1)
    log(f'Token loaded ({len(token)} chars)', args.quiet)

    try:
        code, info = http_get('https://api.hubapi.com/account-info/v3/details', token)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            log('FAIL: token rejected (401 Unauthorized) — regenerate the Private App token', args.quiet, force=True)
            sys.exit(1)
        log(f'FAIL: HTTP {e.code} from HubSpot: {e.read().decode("utf-8", errors="replace")[:200]}', args.quiet, force=True)
        sys.exit(1)
    except Exception as e:
        log(f'FAIL: transient network error: {e}', args.quiet, force=True)
        sys.exit(2)

    if code != 200:
        log(f'FAIL: /account-info returned HTTP {code}', args.quiet, force=True)
        sys.exit(1)
    log(f'Portal: {info.get("portalId")}  Account type: {info.get("accountType")}', args.quiet)

    # Check that we can read each required object type
    for obj in ['contacts', 'companies', 'deals', 'tasks']:
        url = f'https://api.hubapi.com/crm/v3/objects/{obj}?limit=1'
        try:
            code, body = http_get(url, token)
            if code == 200:
                log(f'  {obj}: OK (read access)', args.quiet)
            elif code == 403:
                log(f'  {obj}: SCOPE MISSING (403 Forbidden) — add crm.objects.{obj}.read in Private App scopes', args.quiet, force=True)
                sys.exit(1)
            else:
                log(f'  {obj}: HTTP {code} — {body}', args.quiet, force=True)
                sys.exit(1)
        except urllib.error.HTTPError as e:
            if e.code == 403:
                log(f'  {obj}: SCOPE MISSING (403)', args.quiet, force=True)
                sys.exit(1)
            raise

    log('OK: token + all 4 object scopes healthy', args.quiet)
    sys.exit(0)


if __name__ == '__main__':
    main()
