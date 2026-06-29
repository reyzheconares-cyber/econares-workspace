#!/usr/bin/env python3
"""
ECONARES — HubSpot Stale Lead Automator (v2)

Industry best-practice refactor of the original (Jun 15 2026):

  [x] Uses hs_last_sales_activity_date (the actual sales-engagement signal),
      NOT hs_lastmodifieddate (any CRM write counts and produces false positives).
  [x] Dry-run by default. Pass --apply to actually mutate. Never bulk-mutate
      the CRM without a logged preview step.
  [x] Probes portal enums FIRST and refuses to run if the downgrade target
      status isn't valid in this portal (original script blindly PATCHed
      'NURTURE' which doesn't exist here — would have silently 400'd).
  [x] Excludes contacts currently in OPEN_DEAL, CONNECTED, or ATTEMPTED_TO_CONTACT
      — those are engagement signals, not staleness.
  [x] Excludes contacts whose IDs appear on any open Deal in the pipeline
      (loads Deal associations before deciding).
  [x] Logs every proposed change as a CSV before --apply runs, so the run
      is auditable / reversible.
  [x] Acceptable window: 90 days default (overridable with --days).

CLI:
  python hubspot_stale_leads.py                # dry-run preview, default 90d
  python hubspot_stale_leads.py --days 60      # 60-day window
  python hubspot_stale_leads.py --days 90 --apply   # actually downgrade
  python hubspot_stale_leads.py --apply --yes      # skip interactive confirm
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

ENV = os.path.expanduser('~/.hermes/.env')


def _token() -> str:
    with open(ENV) as f:
        for line in f:
            if line.lstrip().startswith('HUBSPOT_ACCESS_TOKEN'):
                return line.split('=', 1)[1].strip().strip('"').strip("'")
    raise SystemExit('HUBSPOT_ACCESS_TOKEN not found in ~/.hermes/.env')


T = _token()
BASE = 'https://api.hubapi.com'


def http(method: str, url: str, body=None):
    """Wrapper that returns (status, json|str). Handles 204 No Content."""
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as r:
            raw = r.read().decode()
            if not raw.strip():
                return r.status, {}
            try:
                return r.status, json.loads(raw)
            except json.JSONDecodeError:
                return r.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw


def probe_enums() -> tuple[set[str], set[str]]:
    """Return ({valid_hs_lead_status_values}, {valid_lifecyclestage_values})."""
    c, body = http('GET', f'{BASE}/crm/v3/properties/contacts/hs_lead_status')
    if c != 200:
        raise SystemExit(f'Cannot probe hs_lead_status: HTTP {c} {str(body)[:200]}')
    lead_status = {o['value'] for o in body.get('options', [])}

    c2, body2 = http('GET', f'{BASE}/crm/v3/properties/contacts/lifecyclestage')
    if c2 != 200:
        lifecycle = set()
    else:
        lifecycle = {o['value'] for o in body2.get('options', [])}
    return lead_status, lifecycle


def fetch_stale_contacts(days: int) -> list[dict]:
    """Find contacts with no sales activity in `days` days, eligible for downgrade."""
    cutoff_ms = int((time.time() - days * 86400) * 1000)
    cutoff_iso = (
        datetime.fromtimestamp(cutoff_ms / 1000, tz=timezone.utc)
        .strftime('%Y-%m-%dT%H:%M:%S.000Z')
    )
    # NOTE: hs_last_sales_activity_date is labeled "old" in the portal — it's
    # deprecated. Newer portals use notes_last_updated / engagements. For now
    # this still returns valid data; if it ever returns 0 hits across all
    # contacts the portal has migrated and we need to switch.
    query = {
        'filterGroups': [
            {
                'filters': [
                    {'propertyName': 'hs_lead_status',
                     'operator': 'EQ', 'value': 'OPEN'},
                    {'propertyName': 'hs_last_sales_activity_date',
                     'operator': 'LT', 'value': cutoff_iso},
                ],
            },
            {
                'filters': [
                    {'propertyName': 'hs_lead_status',
                     'operator': 'EQ', 'value': 'IN_PROGRESS'},
                    {'propertyName': 'hs_last_sales_activity_date',
                     'operator': 'LT', 'value': cutoff_iso},
                ],
            },
        ],
        'properties': [
            'hs_lead_status', 'hs_last_sales_activity_date', 'firstname',
            'lastname', 'lifecyclestage', 'hs_buying_role',
        ],
        'limit': 100,
    }
    c, body = http(
        'POST', f'{BASE}/crm/v3/objects/contacts/search', query,
    )
    if c != 200:
        raise SystemExit(
            f'Search failed: HTTP {c}\n{json.dumps(body, indent=2)[:600]}'
        )
    return body.get('results', [])


def fetch_open_deal_contact_ids() -> set[str]:
    """Return IDs of contacts associated to any non-closed Deal in the pipeline."""
    contact_ids: set[str] = set()
    after = None
    while True:
        body_q = {
            'filterGroups': [{
                'filters': [{
                    'propertyName': 'dealstage',
                    'operator': 'NEQ',
                    'value': 'closedlost',
                }],
            }],
            'properties': ['dealstage'],
            'limit': 100,
        }
        if after:
            body_q['after'] = after
        c, body = http(
            'POST', f'{BASE}/crm/v3/objects/deals/search', body_q,
        )
        if c != 200:
            break
        for d in body.get('results', []):
            did = d['id']
            # HubSpot v4 associations: GET /crm/v4/objects/deals/{id}/associations/contacts
            _, assoc = http(
                'GET',
                f'{BASE}/crm/v4/objects/deals/{did}/associations/contacts',
            )
            for r in assoc.get('results', []):
                contact_ids.add(str(r.get('toObjectId') or r.get('id')))
        paging = body.get('paging', {}).get('next', {})
        after = paging.get('after')
        if not after:
            break
    return contact_ids


def is_protected_status(current_status: str) -> bool:
    """Contacts with these statuses should NEVER be auto-downgraded."""
    return current_status in {'OPEN_DEAL', 'CONNECTED', 'ATTEMPTED_TO_CONTACT'}


def preview(stale, protected_ids, target_status):
    rows = []
    for c in stale:
        cid = c['id']
        if cid in protected_ids:
            reason = 'contact has open deal(s)'
        elif is_protected_status(c['properties'].get('hs_lead_status', '')):
            reason = "lead status is engagement-positive"
        else:
            reason = ''
        rows.append({
            'contact_id': cid,
            'name': f"{c['properties'].get('firstname','')} {c['properties'].get('lastname','')}".strip(),
            'current_status': c['properties'].get('hs_lead_status', ''),
            'last_activity': c['properties'].get('hs_last_sales_activity_date', ''),
            'protected': 'YES' if reason else 'no',
            'reason': reason,
            'new_status': target_status,
        })
    return rows


def write_preview_csv(rows, path):
    cols = [
        'contact_id', 'name', 'current_status', 'last_activity',
        'protected', 'reason', 'new_status',
    ]
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return path


def apply(rows, target_status, log_path):
    """Apply the downgrade for rows that are not protected. Append to log."""
    applied = 0
    skipped = 0
    ts = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with open(log_path, 'a', newline='', encoding='utf-8') as logf:
        log = csv.writer(logf)
        for r in rows:
            if r['protected'] == 'YES':
                skipped += 1
                continue
            c, body = http(
                'PATCH',
                f'{BASE}/crm/v3/objects/contacts/{r["contact_id"]}',
                {'properties': {'hs_lead_status': target_status}},
            )
            ok = (c == 200)
            log.writerow([
                ts, r['contact_id'], r['name'],
                r['current_status'], target_status, c,
                'OK' if ok else json.dumps(body)[:200],
            ])
            if ok:
                applied += 1
            else:
                skipped += 1
    return applied, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=int, default=90)
    ap.add_argument('--apply', action='store_true',
                    help='Actually downgrade (default is dry-run preview)')
    ap.add_argument('--yes', action='store_true',
                    help='Skip interactive yes/no confirmation when --apply')
    ap.add_argument('--target', type=str, default='UNQUALIFIED',
                    help='Target hs_lead_status (default UNQUALIFIED per enum)')
    ap.add_argument('--out', type=str, default=None,
                    help='Preview CSV path (default tmp)')
    args = ap.parse_args()

    # === Step 0: probe portal enums FIRST ===
    print(f'[PROBE] Validating portal enums for hs_lead_status target "{args.target}" ...')
    lead_status_values, _ = probe_enums()
    if args.target not in lead_status_values:
        raise SystemExit(
            f'\nFATAL: "{args.target}" is not a valid hs_lead_status in this portal.\n'
            f'Valid options: {sorted(lead_status_values)}\n'
            f'Pass --target <one_of_those> to proceed.'
        )
    print(f'[PROBE] OK. {len(lead_status_values)} enum values present.')

    # === Step 1: find stale candidates ===
    print(f'[SCAN] Searching contacts with no sales activity in {args.days} days ...')
    stale = fetch_stale_contacts(args.days)
    print(f'[SCAN] {len(stale)} candidates match OPEN/IN_PROGRESS + inactive > {args.days}d')

    # === Step 2: find protected contacts (have open deals) ===
    print('[SCAN] Loading contacts associated to any open deal ...')
    protected = fetch_open_deal_contact_ids()
    print(f'[SCAN] {len(protected)} contact(s) are protected by open deals')

    # === Step 3: build preview ===
    rows = preview(stale, protected, args.target)
    out_path = args.out or os.path.join(
        os.path.expanduser('~/.hermes/scripts/logs'),
        f'stale_preview_{int(time.time())}.csv',
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_preview_csv(rows, out_path)
    applyable = [r for r in rows if r['protected'] != 'YES']
    print(f'\n[PREVIEW] {len(applyable)} contact(s) WOULD be downgraded '
          f'→ {args.target}')
    print(f'[PREVIEW] {len(rows) - len(applyable)} protected (skipped)')
    print(f'[PREVIEW] CSV: {out_path}')
    for r in rows[:20]:
        flag = '[PROTECTED]' if r['protected'] == 'YES' else '[OK]'
        print(f'  {flag} {r["name"]!s:40s}  '
              f'{r["current_status"]!s:18s} → {r["new_status"]!s:14s}  '
              f'last={r["last_activity"]!s:24s}')
    if len(rows) > 20:
        print(f'  ... ({len(rows) - 20} more in CSV)')

    if not args.apply:
        print('\n[DRY-RUN] No changes made. Re-run with --apply to commit.')
        return 0

    if not applyable:
        print('\n[APPLY] Nothing to apply; all candidates are protected.')
        return 0

    if not args.yes:
        resp = input(
            f'\nAbout to downgrade {len(applyable)} contact(s). Continue? [y/N] '
        ).strip().lower()
        if resp != 'y':
            print('[APPLY] Aborted by user.')
            return 1

    log_path = os.path.join(
        os.path.expanduser('~/.hermes/scripts/logs'),
        'stale_apply_log.csv',
    )
    applied, skipped = apply(applyable, args.target, log_path)
    print(f'\n[APPLY] {applied} downgraded, {skipped} skipped/failed. '
          f'Audit log: {log_path}')
    return 0 if applied > 0 or skipped == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
