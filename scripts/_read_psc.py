import json, os, urllib.request
ENV = os.path.expanduser('~/.hermes/.env')
T = next(line.split('=', 1)[1].strip().strip('"').strip("'") for line in open(ENV) if line.lstrip().startswith('HUBSPOT_ACCESS_TOKEN'))

co_id = '329644342986'
req = urllib.request.Request(
    f'https://api.hubapi.com/crm/v3/objects/companies/{co_id}?properties=name,domain,industry,description,phone,address,city,state,country,website,hs_target_account,numberofemployees'
)
req.add_header('Authorization', f'Bearer {T}')
with urllib.request.urlopen(req) as resp:
    d = json.loads(resp.read().decode())
p = d.get('properties', {})
for k in ['name','domain','industry','description','phone','address','city','state','country','website','hs_target_account','numberofemployees']:
    print(f'{k}: {p.get(k)}')