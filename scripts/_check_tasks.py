"""Check HubSpot tasks due today."""
import json, urllib.request, datetime

ENV = r'C:\Users\reyma\.hermes\.env'
with open(ENV, 'r', encoding='utf-8') as f:
    T = None
    for line in f:
        if line.lstrip().startswith('HUBSPOT_ACCESS_TOKEN='):
            T = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

BASE = 'https://api.hubapi.com'

def http(method, url, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {T}')
    req.add_header('Content-Type', 'application/json')
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=15) as resp:
            return resp.status, (json.loads(resp.read().decode()) if resp.length else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, e.read().decode()[:300]

today = datetime.date.today()
today_start_ms = int(datetime.datetime(today.year, today.month, today.day, tzinfo=datetime.timezone.utc).timestamp() * 1000)
tomorrow_start_ms = today_start_ms + 86400000

body = {
    "filterGroups": [{
        "filters": [
            {
                "propertyName": "hs_timestamp",
                "operator": "GTE",
                "value": str(today_start_ms)
            },
            {
                "propertyName": "hs_timestamp",
                "operator": "LT",
                "value": str(tomorrow_start_ms)
            }
        ]
    }],
    "properties": ["hs_timestamp", "hs_task_subject", "hs_task_status", "hs_task_priority"],
    "limit": 50,
    "sorts": [{"propertyName": "hs_timestamp", "direction": "ASCENDING"}]
}

sc, d = http('POST', f'{BASE}/crm/v3/objects/tasks/search', body)
print(f"Tasks due today: {d.get('total', 0)}")
for t in d.get('results', []):
    p = t['properties']
    ts = p.get('hs_timestamp', '')
    subj = p.get('hs_task_subject', '')[:70]
    status = p.get('hs_task_status', 'NOT_STARTED')
    print(f"  [{status[:15]:15s}] {ts} | {subj}")