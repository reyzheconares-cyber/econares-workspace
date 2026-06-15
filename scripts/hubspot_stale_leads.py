import json, os, urllib.request, time
ENV = os.path.expanduser('~/.hermes/.env')
T = next(line.split('=', 1)[1].strip().strip('"').strip("'") for line in open(ENV) if line.lstrip().startswith('HUBSPOT_ACCESS_TOKEN'))
def http(method, url, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(body).encode() if body else None
    try:
        with urllib.request.urlopen(req, data=data) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

cutoff = int((time.time() - (90 * 86400)) * 1000)
query = {
    "filterGroups": [{
        "filters": [
            {"propertyName": "hs_lead_status", "operator": "IN", "values": ["OPEN", "IN_PROGRESS"]},
            {"propertyName": "hs_lastmodifieddate", "operator": "LT", "value": str(cutoff)}
        ]
    }],
    "properties": ["hs_lead_status", "firstname", "lastname"]
}
c, body = http('POST', 'https://api.hubapi.com/crm/v3/objects/contacts/search', query)
stale = body.get('results', [])
for sc in stale:
    http('PATCH', f'https://api.hubapi.com/crm/v3/objects/contacts/{sc["id"]}', {"properties": {"hs_lead_status": "NURTURE"}})
    print(f"[STALE LEAD] Downgraded {sc['id']} to NURTURE (no activity > 90 days)")
if not stale:
    print("[STALE LEAD] No stale leads found to downgrade.")
