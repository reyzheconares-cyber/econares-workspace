import json, os, urllib.request

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

# 1. Update Deal Names & Map Buying Center
c, body = http('GET', 'https://api.hubapi.com/crm/v3/objects/deals?properties=dealname,destination_port,material_needed,monthly_volume_requirement&associations=companies,contacts')
deals = body.get('results', [])

for d in deals:
    did = d['id']
    props = d.get('properties', {})
    old_name = props.get('dealname', '')
    port = props.get('destination_port') or 'TBD Port'
    mat = props.get('material_needed') or 'Commodity'
    vol = props.get('monthly_volume_requirement') or 'TBD Vol'
    
    comp_assoc = d.get('associations', {}).get('companies', {}).get('results', [])
    if comp_assoc:
        cid = comp_assoc[0]['id']
        c2, cbody = http('GET', f'https://api.hubapi.com/crm/v3/objects/companies/{cid}?properties=name')
        cname = cbody.get('properties', {}).get('name', 'Unknown')
        
        new_name = f"{cname} - {mat} - {vol} {port}"
        if old_name != new_name:
            http('PATCH', f'https://api.hubapi.com/crm/v3/objects/deals/{did}', {"properties": {"dealname": new_name}})
            print(f"[NAMING] Renamed Deal: '{old_name}' -> '{new_name}'")
            
        c3, cont_body = http('GET', f'https://api.hubapi.com/crm/v3/objects/companies/{cid}/associations/contacts')
        contact_ids = [c['id'] for c in cont_body.get('results', [])]
        
        for cont_id in contact_ids:
            http('PUT', f'https://api.hubapi.com/crm/v4/objects/deals/{did}/associations/default/contacts/{cont_id}')
        print(f"[ABM] Associated {len(contact_ids)} buying center contacts to deal '{new_name}'")
        
        for cont_id in contact_ids:
            c4, get_cont = http('GET', f'https://api.hubapi.com/crm/v3/objects/contacts/{cont_id}?properties=hs_buying_role,jobtitle')
            c_props = get_cont.get('properties', {})
            if not c_props.get('hs_buying_role'):
                title = str(c_props.get('jobtitle') or '').lower()
                role = ''
                if 'vp' in title or 'director' in title or 'head' in title: role = 'EXECUTIVE_SPONSOR'
                elif 'procurement' in title or 'purchasing' in title: role = 'DECISION_MAKER'
                elif 'manager' in title: role = 'INFLUENCER'
                
                if role:
                    http('PATCH', f'https://api.hubapi.com/crm/v3/objects/contacts/{cont_id}', {"properties": {"hs_buying_role": role}})
                    print(f"  -> Assigned role '{role}' to contact {cont_id} ({title})")
