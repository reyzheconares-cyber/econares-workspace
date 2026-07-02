"""Enrich all HubSpot entries from session companies:
1. POSCO Holdings (331643911869)
2. POSCO International (331643910896)
3. Nippon Steel (331636777655)
4. SMM parent (331687676658)
5. SMMPH (322924743370)
6. Hinduja Group (331702785747)
7. HNPCL (331693873869)
+ 11 contacts enrichment
"""
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
            return e.code, e.read().decode()[:400]

BASE = 'https://api.hubapi.com'
ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

# ═══════════════════════════════════════════════════════════════════
# COMPANY ENRICHMENTS — sales notes, strategic notes, contact forms
# ═══════════════════════════════════════════════════════════════════

companies = {
    # ── POSCO Holdings ──
    '331643911869': {
        'name': 'POSCO Holdings',
        'notes_to_write': [
            {
                'title': 'POSCO Holdings — Sales & Strategic Notes (Call Brief)',
                'body': (
                    '<p><strong>CALL BRIEF — POSCO Holdings (KRX: 005490)</strong></p>'
                    '<p><strong>BUYING SIGNALS:</strong></p>'
                    '<ul>'
                    '<li>POSCO Future M JV with MC Group (NPSI) producing MHP in Philippines — MC Group acquiring ~200M tons PH nickel ore by 2026</li>'
                    '<li>POSCO Future M targets 1M MT/yr cathode materials by 2030</li>'
                    '<li>POSCO-Huayou JV (China) — cathode + precursor; existing ECONARES CRM contact</li>'
                    '<li>POSCO International trading arm handles spot/opportunity deals</li>'
                    '<li>Krakatau POSCO (Indonesia) — 3M MT/yr integrated steel mill</li>'
                    '</ul>'
                    '<p><strong>STRATEGIC NOTES:</strong></p>'
                    '<ul>'
                    '<li>World\'s 5th largest steelmaker; 17.2 MT/yr crude steel</li>'
                    '<li>$15B U.S. Steel acquisition closed Jun 2025 — management bandwidth absorbed</li>'
                    '<li>100% imported iron ore + coking coal (Australia 60.5%, Brazil 28.2%)</li>'
                    '<li>Procurement strategy: vertical integration (buys mine stakes, not from traders)</li>'
                    '<li>Korean business culture: formal, relationship-first, 6–12 month sales cycle</li>'
                    '<li>RMI-compliant supply chain messaging required</li>'
                    '</ul>'
                    '<p><strong>COMMODITY FIT:</strong></p>'
                    '<ul>'
                    '<li>PH nickel ore (1.5–2.0% Ni): ★★★★★ PRIMARY — MC Group/NPSI acquiring 200M tons by 2026</li>'
                    '<li>MHP blend material: ★★★★ — POSCO Future M direct consumer</li>'
                    '<li>Indonesian thermal coal: ★★★ — Indonesia ~20% of coking coal sourcing</li>'
                    '</ul>'
                    '<p><strong>OUTREACH STRATEGY:</strong></p>'
                    '<ul>'
                    '<li>Lead with PH nickel ore angle via POSCO Future M / NPSI JV</li>'
                    '<li>Secondary: Indonesian thermal coal via POSCO International trading arm</li>'
                    '<li>Tertiary: Krakatau POSCO (Indonesia) coal angle</li>'
                    '<li>Contact: Jungeun (Christine) Yi — Sr Procurement Manager (raw materials desk, Seoul)</li>'
                    '</ul>'
                ),
            },
        ],
        'contact_form': 'https://www.posco.co.kr/homepage/eng/contactUs/contactUs.do',
    },

    # ── POSCO International ──
    '331643910896': {
        'name': 'POSCO International',
        'notes_to_write': [
            {
                'title': 'POSCO International — Sales & Strategic Notes (Call Brief)',
                'body': (
                    '<p><strong>CALL BRIEF — POSCO International (Trading Arm)</strong></p>'
                    '<p><strong>BUYING SIGNALS:</strong></p>'
                    '<ul>'
                    '<li>Newly appointed President: Lee Kye-in (ex-Daewoo International head of energy/steel)</li>'
                    '<li>Handles global trading: steel, energy, grain, REE</li>'
                    '<li>Trading arm for spot/opportunity deals — entry point for ECONARES</li>'
                    '</ul>'
                    '<p><strong>STRATEGIC NOTES:</strong></p>'
                    '<ul>'
                    '<li>Trading arm of POSCO Holdings — handles non-core procurement and spot deals</li>'
                    '<li>Lee Kye-in brings Daewoo International energy/steel trading expertise</li>'
                    '<li>New leadership = new procurement patterns — entry window open</li>'
                    '<li>Korean business culture: formal, relationship-first</li>'
                    '</ul>'
                    '<p><strong>COMMODITY FIT:</strong></p>'
                    '<ul>'
                    '<li>Indonesian thermal coal: ★★★ — spot/opportunity trading</li>'
                    '<li>PH nickel ore: ★★★ — trading arm may handle spot cargoes</li>'
                    '</ul>'
                    '<p><strong>OUTREACH STRATEGY:</strong></p>'
                    '<ul>'
                    '<li>Position as ECONARES\'s spot/trading counterpart at POSCO Group</li>'
                    '<li>Lead with Indonesian thermal coal + PH nickel ore spot availability</li>'
                    '<li>Contact via POSCO International Seoul HQ</li>'
                    '</ul>'
                ),
            },
        ],
        'contact_form': 'https://www.poscointl.com/en/contact/contactUs.do',
    },

    # ── Nippon Steel ──
    '331636777655': {
        'name': 'Nippon Steel Corporation',
        'notes_to_write': [
            {
                'title': 'Nippon Steel Corporation — Sales & Strategic Notes (Call Brief)',
                'body': (
                    '<p><strong>CALL BRIEF — Nippon Steel Corporation (TSE: 5401)</strong></p>'
                    '<p><strong>BUYING SIGNALS:</strong></p>'
                    '<ul>'
                    '<li>$15B U.S. Steel acquisition closed Jun 2025 — global expansion</li>'
                    '<li>Actively hunting coking coal + iron ore mine stakes (Reuters Nov 2023)</li>'
                    '<li>Indonesia ~20% of coking coal sourcing — non-Australian alternative</li>'
                    '<li>Target 100 MT/yr global capacity by mid-2030s</li>'
                    '</ul>'
                    '<p><strong>STRATEGIC NOTES:</strong></p>'
                    '<ul>'
                    '<li>World\'s 4th–5th largest steelmaker; 82 MT/yr crude steel</li>'
                    '<li>100% imported iron ore + coking coal (Australia 60.5% + 56.5%)</li>'
                    '<li>Vertical integration strategy — buys mine stakes, not from traders</li>'
                    '<li>Japanese keiretsu culture: 12–24 month sales cycle, formal</li>'
                    '<li>Management bandwidth absorbed by US Steel integration</li>'
                    '<li>No PH/Indonesia operations = lower priority for ECONARES</li>'
                    '</ul>'
                    '<p><strong>COMMODITY FIT:</strong></p>'
                    '<ul>'
                    '<li>Indonesian thermal coal (NAR 4,200–6,200 GAR): ★★★ — non-Australian alternative</li>'
                    '<li>Coking coal: ★★ — strong existing supplier relationships (BHP, Rio Tinto)</li>'
                    '<li>PH nickel ore: ★★ — no PH/Indonesia operations</li>'
                    '</ul>'
                    '<p><strong>OUTREACH STRATEGY:</strong></p>'
                    '<ul>'
                    '<li>Position as non-Australian coal alternative (Indonesian thermal coal)</li>'
                    '<li>Wait for US Steel integration to settle (6–12 months)</li>'
                    '<li>Primary sourcing is from mines, not traders — break-in is hard</li>'
                    '<li>Monitor only — no active outreach recommended now</li>'
                    '</ul>'
                ),
            },
        ],
        'contact_form': 'https://www.nipponsteel.com/en/inquiry/',
    },

    # ── SMM parent ──
    '331687676658': {
        'name': 'Sumitomo Metal Mining Co., Ltd.',
        'notes_to_write': [
            {
                'title': 'SMM (Parent) — Sales & Strategic Notes (Call Brief)',
                'body': (
                    '<p><strong>CALL BRIEF — Sumitomo Metal Mining Co., Ltd. (TSE: 5713)</strong></p>'
                    '<p><strong>BUYING SIGNALS:</strong></p>'
                    '<ul>'
                    '<li>CBNC (Coral Bay, Palawan, 100% SMM) — 24,000 MT/yr Ni + 2,500 MT/yr Co; active HPAL plant</li>'
                    '<li>THPAL (Taganito, Surigao del Norte, 60% SMM) — 30,000–36,000 MT/yr Ni; world\'s largest HPAL</li>'
                    '<li>Combined PH capacity: ~60,000 MT/yr Ni + 2,500 MT/yr Co</li>'
                    '<li>Long-term target: 150,000 MT/yr nickel (currently 82,000 MT/yr)</li>'
                    '<li>NCA cathode for Panasonic/Tesla: 60,000 MT/yr → 84,000 MT/yr by 2025</li>'
                    '</ul>'
                    '<p><strong>STRATEGIC NOTES:</strong></p>'
                    '<ul>'
                    '<li>VERTICALLY INTEGRATED — self-supplies primary ore from own mines</li>'
                    '<li>May need supplemental PH ore for blending (Mg:Si ratio critical for HPAL)</li>'
                    '<li>3 verified procurement contacts at SMMPH Manila (TJ Villaluna primary)</li>'
                    '<li>Japanese keiretsu culture: formal, 6–12 month sales cycle</li>'
                    '<li>Both CBNC + THPAL received PMIEA 2021 awards — compliance messaging</li>'
                    '</ul>'
                    '<p><strong>COMMODITY FIT:</strong></p>'
                    '<ul>'
                    '<li>PH saprolite/limonite nickel ore: ★★★★ STRONG — CBNC + THPAL HPAL plants need consistent feed</li>'
                    '<li>MHP blend material: ★★★★ — HPAL processing needs precise Mg:Si ratio</li>'
                    '<li>Cobalt-copper concentrate: ★★★ — CBNC produces cobalt as byproduct</li>'
                    '<li>Indonesian thermal coal: ★★ — HPAL uses autoclaves (electric), not coal-fired</li>'
                    '</ul>'
                    '<p><strong>OUTREACH STRATEGY:</strong></p>'
                    '<ul>'
                    '<li>Lead with TJ Villaluna (Procurement Sr Sup) at SMMPH Manila</li>'
                    '<li>Cover both CBNC Palawan + THPAL Surigao del Norte plants</li>'
                    '<li>HPAL feed quality specs strict — align with their Mg:Si requirements</li>'
                    '<li>Japanese business culture: formal, relationship-first</li>'
                    '</ul>'
                ),
            },
        ],
        'contact_form': 'https://www.smm.co.jp/en/inquiry/',
    },

    # ── SMMPH ──
    '322924743370': {
        'name': 'Sumitomo Metal Mining Philippine Holdings Corp',
        'notes_to_write': [
            {
                'title': 'SMMPH — Sales & Strategic Notes (Call Brief)',
                'body': (
                    '<p><strong>CALL BRIEF — SMMPH (Regional HQ, Manila)</strong></p>'
                    '<p><strong>BUYING SIGNALS:</strong></p>'
                    '<ul>'
                    '<li>Coordinates 2 active HPAL nickel plants: CBNC (Palawan) + THPAL (Surigao del Norte)</li>'
                    '<li>Combined PH capacity: ~60,000 MT/yr Ni + 2,500 MT/yr Co</li>'
                    '<li>3 verified procurement/logistics contacts in Manila</li>'
                    '<li>SMM parent target: 150,000 MT/yr Ni — expansion needs new sourcing</li>'
                    '</ul>'
                    '<p><strong>STRATEGIC NOTES:</strong></p>'
                    '<ul>'
                    '<li>Regional HQ for SMM nickel business in PH — all procurement flows through here</li>'
                    '<li>Parent: Sumitomo Metal Mining Co., Ltd. (TSE: 5713)</li>'
                    '<li>Established 2010, inaugurated Feb 2011; 51–200 employees</li>'
                    '<li>PMIEA 2021 awards for both CBNC + THPAL — compliance messaging</li>'
                    '<li>Access via SMMPH Manila regional HQ procurement team</li>'
                    '</ul>'
                    '<p><strong>OUTREACH STRATEGY:</strong></p>'
                    '<ul>'
                    '<li>Lead with TJ Villaluna (Procurement Senior Supervisor)</li>'
                    '<li>Secondary: Ma. Cristina Magbanua (Logistics) + Kristel Ann Galvez (Procurement)</li>'
                    '<li>Position ECONARES as PH nickel ore supplier for HPAL feed blending</li>'
                    '</ul>'
                ),
            },
        ],
        'contact_form': 'https://www.smm.co.jp/en/inquiry/',
    },

    # ── Hinduja Group ──
    '331702785747': {
        'name': 'Hinduja Group of Companies',
        'notes_to_write': [
            {
                'title': 'Hinduja Group — Sales & Strategic Notes (Call Brief)',
                'body': (
                    '<p><strong>CALL BRIEF — Hinduja Group (Monitoring Only)</strong></p>'
                    '<p><strong>STRATEGIC NOTES:</strong></p>'
                    '<ul>'
                    '<li>UK-India family conglomerate; $22B Forbes 2024; UK Rich List #1</li>'
                    '<li>Chairman India: Ashok Hinduja (post-Gopichand death late 2025)</li>'
                    '<li>Sectors: Ashok Leyland, banking, power (HNPCL), renewables, IT, media</li>'
                    '<li>Coal interest via HNPCL (1,040 MW Visakhapatnam) — monitoring parent only</li>'
                    '<li>Hinduja Group leadership transition + GOCL acquisition of HNPCL = M&A window</li>'
                    '</ul>'
                    '<p><strong>OUTREACH STRATEGY:</strong></p>'
                    '<ul>'
                    '<li>Monitor only — no active outreach to parent</li>'
                    '<li>Coal angle is via HNPCL subsidiary (separate record)</li>'
                    '<li>Wait for GOCL acquisition to settle (6–12 months)</li>'
                    '</ul>'
                ),
            },
        ],
        'contact_form': 'https://www.hindujagroup.com/contact-us',
    },

    # ── HNPCL ──
    '331693873869': {
        'name': 'Hinduja National Power Corporation Limited',
        'notes_to_write': [
            {
                'title': 'HNPCL — Sales & Strategic Notes (Call Brief)',
                'body': (
                    '<p><strong>CALL BRIEF — HNPCL (1,040 MW Coal Power Plant, Visakhapatnam)</strong></p>'
                    '<p><strong>BUYING SIGNALS:</strong></p>'
                    '<ul>'
                    '<li>1,040 MW (2 × 520/540 MW) coal-fired thermal power plant</li>'
                    '<li>COD: April 30, 2016 — 25-year PPA with AP discoms (cost-plus)</li>'
                    '<li>~5M MT/yr coal demand — significant scale</li>'
                    '<li>GOCL acquisition pending — M&A transition window</li>'
                    '<li>Future Hinduja target: 10,000 MW (~$10B investment over 10 years)</li>'
                    '</ul>'
                    '<p><strong>STRATEGIC NOTES:</strong></p>'
                    '<ul>'
                    '<li>Primary coal source: Talcher coalfields (~600 km) — domestic India (Coal India)</li>'
                    '<li>Imported coal opportunity: supplemental for blending/peak demand only</li>'
                    '<li>CARE rated: Rs 800 crore FY25 infusion; Rs 6,600 crore group support</li>'
                    '<li>Vizag port is major Indian coal import hub — logistics angle</li>'
                    '<li>Indian business culture: formal, relationship-first, Hindi/English bilingual</li>'
                    '<li>Hinduja Group restructuring (post-Gopichand) = new leadership, new procurement</li>'
                    '</ul>'
                    '<p><strong>COMMODITY FIT:</strong></p>'
                    '<ul>'
                    '<li>Indonesian thermal coal: ★★★ — supplemental for blending/peak demand</li>'
                    '<li>Coking coal: ★ Low — not a steelmaker</li>'
                    '<li>Nickel ore / mineral ores: ❌ N/A — power generation only</li>'
                    '</ul>'
                    '<p><strong>OUTREACH STRATEGY:</strong></p>'
                    '<ul>'
                    '<li>Lead with Shiva Prasad Danturi (Sr Manager, Procurement/Contracts/Warehouse)</li>'
                    '<li>Position as supplemental imported coal for blending/peak demand</li>'
                    '<li>Vizag port logistics angle — direct Indonesian coal shipment</li>'
                    '<li>Wait for GOCL acquisition to settle before active outreach</li>'
                    '</ul>'
                ),
            },
        ],
        'contact_form': 'https://www.hindujanationalpower.com/contact',
    },
}

# ═══════════════════════════════════════════════════════════════════
# CONTACT ENRICHMENTS — LinkedIn URLs, sales notes
# ═══════════════════════════════════════════════════════════════════

contacts = {
    # POSCO contacts
    '512570728144': {
        'name': 'Jungeun (Christine) Yi',
        'props': {
            'hs_linkedin_url': 'https://www.linkedin.com/in/jungeun-christine-yi-58b1a224',
        },
        'note': (
            '<p><strong>CONTACT BRIEF — Jungeun (Christine) Yi</strong></p>'
            '<ul>'
            '<li><strong>Role:</strong> Senior Procurement Manager, POSCO (Seoul)</li>'
            '<li><strong>Desk:</strong> Raw Materials Procurement — iron ore, coal, nickel</li>'
            '<li><strong>Tenure:</strong> 10+ years at POSCO (since ~2014)</li>'
            '<li><strong>LinkedIn:</strong> 500+ connections; Seoul Metropolitan Area</li>'
            '<li><strong>Priority:</strong> PRIMARY — direct match for ECONARES commodity supply</li>'
            '<li><strong>Approach:</strong> Lead with PH nickel ore angle (POSCO Future M / NPSI JV); secondary: Indonesian thermal coal</li>'
            '<li><strong>Culture:</strong> Korean — formal, relationship-first, 6–12 month sales cycle</li>'
            '</ul>'
        ),
    },
    '512592224999': {
        'name': 'Seonyeob (Sydney) Chu',
        'props': {
            'hs_linkedin_url': 'https://www.linkedin.com/in/seonyeob-sydney-chu-185514126',
        },
        'note': (
            '<p><strong>CONTACT BRIEF — Seonyeob (Sydney) Chu</strong></p>'
            '<ul>'
            '<li><strong>Role:</strong> Senior Procurement Manager, POSCO (since 2009)</li>'
            '<li><strong>Certification:</strong> CPSM (Certified Professional in Supply Management)</li>'
            '<li><strong>Education:</strong> MBA 2017</li>'
            '<li><strong>Previous:</strong> Samsung (2004–2009)</li>'
            '<li><strong>LinkedIn:</strong> 500+ connections</li>'
            '<li><strong>Priority:</strong> SECONDARY — alternate procurement contact</li>'
            '<li><strong>Approach:</strong> Same angle as Jungeun Yi; use as backup if primary unresponsive</li>'
            '</ul>'
        ),
    },

    # SMM / SMMPH contacts
    '512632772344': {
        'name': 'TJ Villaluna',
        'props': {
            'hs_linkedin_url': 'https://ph.linkedin.com/in/tjvillaluna',
        },
        'note': (
            '<p><strong>CONTACT BRIEF — TJ Villaluna, MBA</strong></p>'
            '<ul>'
            '<li><strong>Role:</strong> Procurement Senior Supervisor, SMMPH (Manila)</li>'
            '<li><strong>Education:</strong> Ateneo Graduate School of Business — MBA Strategic Management (ongoing)</li>'
            '<li><strong>LinkedIn:</strong> 500+ connections, 1,700+ followers</li>'
            '<li><strong>Priority:</strong> PRIMARY — direct match for ECONARES PH nickel ore supply</li>'
            '<li><strong>Approach:</strong> Lead with PH nickel ore supply to CBNC + THPAL HPAL plants; HPAL feed Mg:Si ratio specs</li>'
            '<li><strong>Location:</strong> Metro Manila — accessible for face-to-face meeting</li>'
            '</ul>'
        ),
    },
    '512586545851': {
        'name': 'Ma. Cristina Magbanua',
        'props': {
            'hs_linkedin_url': 'https://ph.linkedin.com/in/ma-cristina-magbanua-60581152',
        },
        'note': (
            '<p><strong>CONTACT BRIEF — Ma. Cristina Magbanua</strong></p>'
            '<ul>'
            '<li><strong>Role:</strong> Logistics Supervisor, SMMPH Manila (Apr 2020–present)</li>'
            '<li><strong>Experience:</strong> 11+ years in mining logistics</li>'
            '<li><strong>Education:</strong> Jose Rizal University (2005–2009)</li>'
            '<li><strong>Priority:</strong> SECONDARY — logistics angle for PH-Indonesia shipping</li>'
            '<li><strong>Approach:</strong> Use for logistics/shipping discussions; coordinate with TJ Villaluna for procurement</li>'
            '</ul>'
        ),
    },
    '512734492386': {
        'name': 'Kristel Ann Galvez',
        'props': {
            'hs_linkedin_url': 'https://ph.linkedin.com/in/kristel-ann-galvez',
        },
        'note': (
            '<p><strong>CONTACT BRIEF — Kristel Ann Galvez</strong></p>'
            '<ul>'
            '<li><strong>Role:</strong> Procurement | Logistics, SMMPH (11+ years)</li>'
            '<li><strong>Experience:</strong> Procurement, Logistics, Supply Chain</li>'
            '<li><strong>Priority:</strong> TERTIARY — alternate procurement contact</li>'
            '<li><strong>Approach:</strong> Backup if TJ Villaluna unresponsive; same PH nickel ore angle</li>'
            '</ul>'
        ),
    },

    # Nippon Steel contacts
    '512552966848': {
        'name': 'Shiva Prasad Danturi',
        'props': {},
        'note': (
            '<p><strong>CONTACT BRIEF — Shiva Prasad Danturi</strong></p>'
            '<ul>'
            '<li><strong>Role:</strong> Senior Manager, Procurement / Contracts / Warehouse, HNPCL (Dec 2023–present)</li>'
            '<li><strong>Location:</strong> Visakhapatnam, Andhra Pradesh</li>'
            '<li><strong>Profile:</strong> Procurement Leader | Strategic Sourcing</li>'
            '<li><strong>Priority:</strong> PRIMARY — direct match for HNPCL coal procurement</li>'
            '<li><strong>Approach:</strong> Position as supplemental Indonesian thermal coal for blending/peak demand; Vizag port logistics angle</li>'
            '</ul>'
        ),
    },
    '512577861344': {
        'name': 'Rohit Tabhane',
        'props': {},
        'note': (
            '<p><strong>CONTACT BRIEF — Rohit Tabhane</strong></p>'
            '<ul>'
            '<li><strong>Role:</strong> Addl. GM-Head Operations, HNPCL (Apr 2024–present, Korba Chhattisgarh)</li>'
            '<li><strong>Experience:</strong> 18+ years power sector (commissioning, operations, fuel management)</li>'
            '<li><strong>Previous Roles:</strong> DGM-Head Operations; Sr. Manager Performance & Efficiency; Technical Advisor to CEO at HNPCL Visakhapatnam</li>'
            '<li><strong>Priority:</strong> SECONDARY — plant-level influence; fuel management experience</li>'
            '<li><strong>Approach:</strong> Use for operational/technical discussions; coordinate with Shiva Prasad for procurement</li>'
            '</ul>'
        ),
    },
    '512623458016': {
        'name': 'Prasanta Kumar Pradhan',
        'props': {},
        'note': (
            '<p><strong>CONTACT BRIEF — Prasanta Kumar Pradhan</strong></p>'
            '<ul>'
            '<li><strong>Role:</strong> Vice President, HNPCL (Jan 2012–present, Visakhapatnam)</li>'
            '<li><strong>Experience:</strong> 14+ years at HNPCL</li>'
            '<li><strong>Priority:</strong> TERTIARY — executive escalation contact</li>'
            '<li><strong>Approach:</strong> Use for executive-level discussions after initial procurement engagement with Shiva Prasad</li>'
            '</ul>'
        ),
    },
}

# ═══════════════════════════════════════════════════════════════════
# EXECUTE ENRICHMENTS
# ═══════════════════════════════════════════════════════════════════

print('=== COMPANY ENRICHMENTS ===')
for cid, data in companies.items():
    # Write sales/strategic notes
    for note_data in data['notes_to_write']:
        sc, r = http('POST', f'{BASE}/crm/v3/objects/notes', {
            'properties': {
                'hs_note_body': note_data['body'],
                'hs_timestamp': ts,
            }
        })
        note_id = r.get('id') if sc in (200, 201) else None
        print(f"  Note '{note_data['title'][:40]}...' for {data['name']}: {sc} | {note_id}")
        if note_id:
            sc2, _ = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/companies/{cid}/note_to_company', {})
            print(f"    assoc to {cid}: {sc2}")

    # Add contact form URL as a note
    if data.get('contact_form'):
        cf_body = f'<p><strong>Online Contact Form:</strong> <a href="{data["contact_form"]}">{data["contact_form"]}</a></p>'
        sc, r = http('POST', f'{BASE}/crm/v3/objects/notes', {
            'properties': {
                'hs_note_body': cf_body,
                'hs_timestamp': ts,
            }
        })
        note_id = r.get('id') if sc in (200, 201) else None
        print(f"  Contact form note for {data['name']}: {sc} | {note_id}")
        if note_id:
            sc2, _ = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/companies/{cid}/note_to_company', {})
            print(f"    assoc to {cid}: {sc2}")

    # Also add contact form as note to the company's description (append)
    # Actually, let's add it as a separate note — cleaner

print()
print('=== CONTACT ENRICHMENTS ===')
for contact_id, data in contacts.items():
    # Update LinkedIn URL if missing
    if data['props']:
        sc, r = http('PATCH', f'{BASE}/crm/v3/objects/contacts/{contact_id}', {'properties': data['props']})
        print(f"  PATCH {data['name']}: {sc}")

    # Write contact brief note
    sc, r = http('POST', f'{BASE}/crm/v3/objects/notes', {
        'properties': {
            'hs_note_body': data['note'],
            'hs_timestamp': ts,
        }
    })
    note_id = r.get('id') if sc in (200, 201) else None
    print(f"  Note for {data['name']}: {sc} | {note_id}")
    if note_id:
        sc2, _ = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/contacts/{contact_id}/note_to_contact', {})
        print(f"    assoc to contact {contact_id}: {sc2}")

print()
print('=== DONE ===')
print(f'Companies enriched: {len(companies)}')
print(f'Contacts enriched: {len(contacts)}')
print(f'Total notes created: {sum(len(d["notes_to_write"]) for d in companies.values()) + len(companies) + len(contacts)}')
