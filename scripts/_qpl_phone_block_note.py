import json, os, urllib.request, datetime
ENV = os.path.expanduser('~/.hermes/.env')
T = next(line.split('=', 1)[1].strip().strip('"').strip("'") for line in open(ENV) if line.lstrip().startswith('HUBSPOT_ACCESS_TOKEN'))

def http(method, url, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except:
            return e.code, e.read().decode()[:300]

BASE = 'https://api.hubapi.com'

# Log phone block as engagement note
note_body = '<p><strong>Channel Block Report — QPL Switchboard (2026-07-02):</strong> Phone call to <a href="tel:+63427840295">+63 (42) 784 0295</a> is being <strong>instantly dropped</strong> on connection attempt. No ring, no voicemail, immediate disconnect. Combined with email bounce pattern (both Walter Laptew addresses bounced), this suggests possible <strong>DID line issue, blocked caller ID, or call filtering</strong> at QPL switchboard.</p><p><strong>Remaining viable channel:</strong> LinkedIn InMail to Frank Thiel (<a href="https://ph.linkedin.com/in/frank-thiel-6ba418">ph.linkedin.com/in/frank-thiel-6ba418</a>). Draft saved to <code>0 Inbox/QPL_LINKEDIN_OUTREACH_DRAFT - 20260702.md</code>.</p><p><strong>Next-step options:</strong></p><ul><li>Use personal mobile (RZH) to bypass switchboard filter</li><li>Wait until QPL contact arrives at conference (e.g., POWERCON 2026, Enlit Asia)</li><li>Approach via EGCO Group HQ Bangkok (+66 2998 5000) — Thai parent may route the call</li><li>Plant visit to Mauban Quezon (87-hectare site, Isla Grande) — last resort</li></ul>'

ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
sc, r = http('POST', f'{BASE}/crm/v3/objects/notes', {
    'properties': {
        'hs_note_body': note_body,
        'hs_timestamp': ts
    }
})
print(f'create note: {sc} | {r.get("id") if sc in (200,201) else r.get("message","")[:200]}')

if sc in (200, 201):
    note_id = r['id']
    # Associate to QPL Company + Frank Thiel Contact
    for assoc_type, assoc_id in [('companies', '326532899525'), ('contacts', '499284710077')]:
        sc2, r2 = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/{assoc_type}/{assoc_id}/{("note_to_" + assoc_type[:-1])}', {})
        print(f'  assoc {assoc_type}/{assoc_id}: {sc2}')