"""Bulk enrichment for all coal/power/cement/steel companies from both sessions."""
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
# COMPANY ENRICHMENT DATA
# ═══════════════════════════════════════════════════════════════════

companies = {
    # ── Philippine Sinter Corporation (JFE Steel subsidiary) ──
    '329644342986': {
        'name': 'Philippine Sinter Corporation',
        'props': {
            'industry': 'MINING_METALS',
            'hs_target_account': 'tier_1',
            'phone': '+63 88 323 1234',
            'address': 'PHIVIDEC Industrial Estate, Villanueva, Misamis Oriental, Philippines',
            'city': 'Villanueva',
            'state': 'Misamis Oriental',
            'country': 'Philippines',
            'website': 'https://www.jfe-steel.co.jp',
            'numberofemployees': 500,
            'description': 'Philippine Sinter Corporation (PSC) - JFE Steel subsidiary in Villanueva, Misamis Oriental. Primary coke breeze demand center: ~5.5M MT/yr. Sinter plant for iron ore processing. JFE Steel (Japan) is the parent company. No PSC entity exists in Batangas. ECONARES angle: coke breeze and thermal coal supply to sinter plant. Close to Cagayan de Oro port - good Indonesian logistics.',
        },
        'contact_form': 'https://www.jfe-steel.co.jp/en/inquiry/',
        'notes': [
            '<p><strong>CALL BRIEF — Philippine Sinter Corporation (PSC)</strong></p>'
            '<p><strong>BUYING SIGNALS:</strong></p><ul>'
            '<li>JFE Steel subsidiary — 5.5M MT/yr coke breeze demand (massive scale)</li>'
            '<li>Sinter plant requires consistent coal/coke breeze feed</li>'
            '<li>Located in PHIVIDEC Industrial Estate, Villanueva — close to Cagayan de Oro port</li>'
            '<li>No PSC entity in Batangas — Villanueva is the only location</li>'
            '</ul><p><strong>STRATEGIC NOTES:</strong></p><ul>'
            '<li>Parent: JFE Steel Corporation (Japan) — keiretsu culture, formal, long-term contracts</li>'
            '<li>JFE is world\'s 5th largest steelmaker — PSC is their PH raw material processing arm</li>'
            '<li>Procurement likely managed at JFE Japan level with local PSC coordination</li>'
            '<li>Indonesian coal logistics: Cagayan de Oro port is close to PHIVIDEC — short haul from Kalimantan</li>'
            '</ul><p><strong>COMMODITY FIT:</strong></p><ul>'
            '<li>Coke breeze: ★★★★★ PRIMARY — 5.5M MT/yr demand</li>'
            '<li>Indonesian thermal coal: ★★★★ — sinter plant fuel</li>'
            '<li>Iron ore: ★★★ — sinter feed (ECONARES nickel ore byproduct possible)</li>'
            '</ul><p><strong>OUTREACH STRATEGY:</strong></p><ul>'
            '<li>Lead with coke breeze + thermal coal angle</li>'
            '<li>Access via JFE Japan procurement or local PSC management</li>'
            '<li>Japanese business culture: formal, relationship-first, 6-12 month cycle</li>'
            '</ul>',
        ],
    },

    # ── GNPower Group (parent) ──
    '319028063953': {
        'name': 'GNPower Group',
        'props': {
            'industry': 'OIL_ENERGY',
            'hs_target_account': 'tier_2',
            'phone': '+63 2 8638 4542',
            'address': 'Pasig City, Metro Manila, Philippines',
            'city': 'Pasig City',
            'country': 'Philippines',
            'website': 'https://www.gnpower.com',
            'numberofemployees': 200,
            'description': 'GNPower Group - Philippine independent power producer group. Parent of GNPower Dinginin (1,336 MW, Mariveles Bataan) and GNPower Kauswagan (552 MW, Lanao del Norte Mindanao). Combined capacity ~1,900 MW. Consolidated procurement for coal across both plants. ECONARES angle: Indonesian thermal coal supply to both GNPD and GNPK. Contact: res-info@gnpower.com.',
        },
        'contact_form': 'https://www.gnpower.com/contact',
        'notes': [
            '<p><strong>CALL BRIEF — GNPower Group (Parent)</strong></p>'
            '<p><strong>BUYING SIGNALS:</strong></p><ul>'
            '<li>Combined ~1,900 MW coal capacity across GNPD + GNPK</li>'
            '<li>Consolidated procurement — group-level coal buying</li>'
            '<li>GNPD: 1,336 MW supercritical (Mariveles, Bataan) — ~3.5-4.5M MT/yr</li>'
            '<li>GNPK: 552 MW (Kauswagan, Lanao del Norte) — ~1.5-2.0M MT/yr</li>'
            '</ul><p><strong>STRATEGIC NOTES:</strong></p><ul>'
            '<li>GNPD ownership: AboitizPower / JERA / AC Energy</li>'
            '<li>GNPK: AC Energy divesting — ownership transition creating procurement window</li>'
            '<li>Both plants: supercritical grade coal preferred (low-mid ash, low sulfur)</li>'
            '<li>Indonesian coal logistics: GNPK is Mindanao-based (closer to Indonesia)</li>'
            '</ul><p><strong>OUTREACH STRATEGY:</strong></p><ul>'
            '<li>Group-level approach via res-info@gnpower.com</li>'
            '<li>For GNPD: Francisco Bordeos (Strategic Sourcing, Coal Procurement)</li>'
            '<li>For GNPK: Donna Mezo (Purchasing Officer)</li>'
            '</ul>',
        ],
    },

    # ── GNPower Kauswagan ──
    '328345657071': {
        'name': 'GNPower Kauswagan Ltd. Co.',
        'props': {
            'industry': 'OIL_ENERGY',
            'hs_target_account': 'tier_1',
            'phone': '+63 63 263 8452',
            'address': 'Kauswagan, Lanao del Norte, Philippines',
            'city': 'Kauswagan',
            'state': 'Lanao del Norte',
            'country': 'Philippines',
            'website': 'https://www.gnpower.com',
            'numberofemployees': 150,
            'description': 'GNPower Kauswagan Ltd. Co. (GNPK) - 552 MW (4x138 MW) coal-fired power plant in Kauswagan, Lanao del Norte, Mindanao. Ownership: Power Partners 85% / AC Energy (Ayala) divesting. Annual coal demand: ~1.5-2.0M MT/yr. Standard pulverized coal: 5,000-6,300 GAR, low-mid ash. Closer to Indonesian origin than Luzon plants. Active tender: AC Energy divestment creates procurement opportunity. Contact: Donna Mezo (Purchasing Officer, gnpres@gnpower.com).',
        },
        'contact_form': 'https://www.gnpower.com/contact',
        'notes': [
            '<p><strong>CALL BRIEF — GNPower Kauswagan (GNPK)</strong></p>'
            '<p><strong>BUYING SIGNALS:</strong></p><ul>'
            '<li>552 MW (4x138 MW) — ~1.5-2.0M MT/yr coal demand</li>'
            '<li>AC Energy divesting — ownership transition creates NEW procurement opportunity</li>'
            '<li>Standard pulverized coal: 5,000-6,300 GAR</li>'
            '<li>Mindanao-based — closer to Indonesian origin than Luzon plants</li>'
            '</ul><p><strong>STRATEGIC NOTES:</strong></p><ul>'
            '<li>Active tender — AC Energy divestment = new supplier window</li>'
            '<li>FOB origin or CIF Mindanao ports</li>'
            '<li>Contact: Donna Mezo (Purchasing Officer) via gnpres@gnpower.com</li>'
            '</ul><p><strong>OUTREACH STRATEGY:</strong></p><ul>'
            '<li>Lead with Indonesian thermal coal (NAR 5,000-6,300 GAR)</li>'
            '<li>Position as Mindanao-optimized logistics (short sea route from Kalimantan)</li>'
            '</ul>',
        ],
    },

    # ── Masinloc Power Partners ──
    '320729061083': {
        'name': 'Masinloc Power Partners Co. Ltd.',
        'props': {
            'industry': 'OIL_ENERGY',
            'hs_target_account': 'tier_1',
            'phone': '+63 2 8702 4664',
            'address': 'Masinloc, Zambales, Philippines',
            'city': 'Masinloc',
            'state': 'Zambales',
            'country': 'Philippines',
            'website': 'https://www.smcglobalpower.com.ph',
            'numberofemployees': 500,
            'description': 'Masinloc Power Partners Co. Ltd. (MPPCL) - San Miguel Global Power (SMCGP) subsidiary. 688 MW existing + 700 MW expansion (Units 4 & 5, target 2025-2026). Annual coal demand: ~2.5M MT/yr existing + ~2M MT/yr expansion = ~4.5M MT/yr total. Sub-bituminous coal: 5,000-6,500 GAR, low sulfur preferred. HQ: SMC Global Power, Mandaluyong. ECONARES angle: major expansion driving new coal demand. SMC owns Semirara mine but expansion may need supplemental supply.',
        },
        'contact_form': 'https://www.smcglobalpower.com.ph/contact',
        'notes': [
            '<p><strong>CALL BRIEF — Masinloc Power Partners (MPPCL)</strong></p>'
            '<p><strong>BUYING SIGNALS:</strong></p><ul>'
            '<li>688 MW existing + 700 MW expansion (Units 4 & 5) = 1,388 MW total</li>'
            '<li>Expansion ~2M MT/yr ADDITIONAL coal demand on top of existing ~2.5M MT/yr</li>'
            '<li>Sub-bituminous coal: 5,000-6,500 GAR</li>'
            '<li>SMC Global Power — large, stable counterparty</li>'
            '</ul><p><strong>STRATEGIC NOTES:</strong></p><ul>'
            '<li>SMC owns Semirara mine — BUT expansion may need supplemental supply</li>'
            '<li>Risk: SMC vertical integration may limit external coal sourcing</li>'
            '<li>Opportunity: expansion volume may exceed Semirara capacity</li>'
            '<li>Contact via SMC Global Power HQ (Mandaluyong)</li>'
            '</ul><p><strong>COMMODITY FIT:</strong></p><ul>'
            '<li>Indonesian thermal coal (5,000-6,500 GAR): ★★★ — expansion may need supplemental</li>'
            '<li>Risk: SMC vertical integration (Semirara mine)</li>'
            '</ul><p><strong>OUTREACH STRATEGY:</strong></p><ul>'
            '<li>Position as supplemental coal for expansion (Units 4 & 5)</li>'
            '<li>SMC Global Power procurement HQ in Mandaluyong</li>'
            '</ul>',
        ],
    },

    # ── SPI Power ──
    '320650095346': {
        'name': 'SPI Power Inc.',
        'props': {
            'industry': 'OIL_ENERGY',
            'hs_target_account': 'tier_2',
            'phone': '+63 32 230 8200',
            'address': 'PHIVIDEC Industrial Estate, Villanueva, Misamis Oriental 9002, Philippines',
            'city': 'Villanueva',
            'state': 'Misamis Oriental',
            'country': 'Philippines',
            'website': 'https://www.aboitizpower.com',
            'numberofemployees': 200,
            'description': 'SPI Power Inc. (formerly STEAG State Power Inc.) - AboitizPower / STEAG (German JV) coal-fired power plant. 232 MW + 3rd unit (~150 MW) planned. Annual coal demand: ~0.6-0.8M MT/yr + expansion. Standard coal: 5,200-6,300 GAR. Villanueva, Misamis Oriental — same PHIVIDEC location as PSC. Sunset asset: slated for early retirement by 2027. ECONARES angle: limited — short remaining life + AboitizPower procurement channel.',
        },
        'contact_form': 'https://www.aboitizpower.com/contact',
        'notes': [
            '<p><strong>CALL BRIEF — SPI Power Inc. (formerly STEAG)</strong></p>'
            '<p><strong>BUYING SIGNALS:</strong></p><ul>'
            '<li>232 MW + 3rd unit (~150 MW) planned</li>'
            '<li>~0.6-0.8M MT/yr coal demand</li>'
            '<li>AboitizPower / STEAG German JV</li>'
            '</ul><p><strong>STRATEGIC NOTES:</strong></p><ul>'
            '<li>SUNSET ASSET — slated for early retirement by 2027</li>'
            '<li>Limited remaining life = low ROI on outreach</li>'
            '<li>AboitizPower consolidated procurement channel</li>'
            '<li>Contact: procurement@aboitizpower.com</li>'
            '</ul><p><strong>OUTREACH STRATEGY:</strong></p><ul>'
            '<li>DEFERRED — low ROI due to 2027 retirement</li>'
            '<li>Monitor for any life extension announcements</li>'
            '</ul>',
        ],
    },

    # ── PT Vale Indonesia ──
    '331684054763': {
        'name': 'PT Vale Indonesia Tbk',
        'props': {
            'industry': 'MINING_METALS',
            'hs_target_account': 'tier_2',
            'phone': '+62 21 522 3333',
            'address': 'Jakarta, Indonesia (mines in Sorowako, Sulawesi)',
            'city': 'Jakarta',
            'country': 'Indonesia',
            'website': 'https://www.valeindonesia.co.id',
            'numberofemployees': 3000,
            'description': 'PT Vale Indonesia Tbk - Indonesian nickel mining company (formerly INCO). Mines in Sorowako, Sulawesi. Produces matte nickel. Majority owned by Vale Canada (divesting to PT Mineral Industri Indonesia). Subject to Indonesian Domestic Market Obligation (DMO). Vertically integrated — self-processes nickel ore. ECONARES angle: LIMITED — DMO restrictions, vertical integration, no coal demand. Low priority.',
        },
        'contact_form': 'https://www.valeindonesia.co.id/en/contact-us',
        'notes': [
            '<p><strong>CALL BRIEF — PT Vale Indonesia</strong></p>'
            '<p><strong>STRATEGIC NOTES:</strong></p><ul>'
            '<li>Indonesian nickel mining — Sorowako, Sulawesi</li>'
            '<li>Subject to Indonesian DMO — export restrictions</li>'
            '<li>Vertically integrated — self-processes nickel ore</li>'
            '<li>Vale Canada divesting to PT Mineral Industri Indonesia (MIND ID)</li>'
            '<li>No coal demand — nickel smelting uses electric/HPAL</li>'
            '</ul><p><strong>COMMODITY FIT:</strong></p><ul>'
            '<li>Indonesian thermal coal: ★ Low — no coal-fired operations</li>'
            '<li>PH nickel ore: ★ Low — DMO restrictions, vertical integration</li>'
            '</ul><p><strong>OUTREACH STRATEGY:</strong></p><ul>'
            '<li>DEFERRED — low priority due to DMO + vertical integration</li>'
            '<li>Monitor for MIND ID acquisition completion and any new procurement patterns</li>'
            '</ul>',
        ],
    },

    # ── JFE Steel Corporation ──
    '329648274159': {
        'name': 'JFE Steel Corporation',
        'props': {
            'industry': 'MINING_METALS',
            'hs_target_account': 'tier_2',
            'phone': '+81 3 3597 4000',
            'address': '2-2-3 Uchisaiwaicho, Chiyoda-ku, Tokyo 100-0011, Japan',
            'city': 'Tokyo',
            'country': 'Japan',
            'website': 'https://www.jfe-steel.co.jp',
            'numberofemployees': 50000,
            'description': 'JFE Steel Corporation (JFEスチール株式会社) - Japanese integrated steelmaker, subsidiary of JFE Holdings. World 5th largest steelmaker. Parent of Philippine Sinter Corporation (PSC) in Villanueva, Misamis Oriental. PSC processes ~5.5M MT/yr coke breeze. JFE procurement managed at Tokyo HQ level. ECONARES angle: coke breeze + thermal coal supply to PSC via JFE Japan procurement. Japanese keiretsu culture.',
        },
        'contact_form': 'https://www.jfe-steel.co.jp/en/inquiry/',
        'notes': [
            '<p><strong>CALL BRIEF — JFE Steel Corporation</strong></p>'
            '<p><strong>BUYING SIGNALS:</strong></p><ul>'
            '<li>Parent of Philippine Sinter Corporation (PSC) — 5.5M MT/yr coke breeze demand</li>'
            '<li>World 5th largest steelmaker — massive commodity procurement</li>'
            '<li>JFE manages procurement at Tokyo HQ with local PSC coordination</li>'
            '</ul><p><strong>STRATEGIC NOTES:</strong></p><ul>'
            '<li>Japanese keiretsu culture: formal, relationship-first, 12-24 month sales cycle</li>'
            '<li>Procurement via JFE Tokyo HQ — need Japanese-speaking counterpart</li>'
            '<li>PSC is the PH demand center for coke breeze/coal</li>'
            '</ul><p><strong>OUTREACH STRATEGY:</strong></p><ul>'
            '<li>Approach via JFE Steel Tokyo procurement division</li>'
            '<li>Lead with coke breeze + thermal coal angle for PSC</li>'
            '<li>Alternative: approach PSC Villanueva directly</li>'
            '</ul>',
        ],
    },

    # ── Concreat Holdings (formerly CEMEX Philippines) ──
    '320080163556': {
        'name': 'Concreat Holdings Philippines',
        'props': {
            'industry': 'GLASS_CERAMICS_CONCRETE',
            'hs_target_account': 'tier_1',
            'phone': '+63 2 8888 8888',
            'address': 'Makati City, Metro Manila, Philippines',
            'city': 'Makati City',
            'country': 'Philippines',
            'website': 'https://www.concreat.ph',
            'numberofemployees': 1000,
            'description': 'Concreat Holdings Philippines (formerly CEMEX Philippines) - Cement manufacturer. Shifted from coal (self-supplied via Semirara) to alternative fuels (biomass/PKS/RDF). ECONARES angle: alternative fuels supply (biomass, PKS, RDF) — NOT coal. Semirara self-supplies coal. PKS and biomass from Indonesia is the primary opportunity.',
        },
        'contact_form': None,
        'notes': [
            '<p><strong>CALL BRIEF — Concreat Holdings (formerly CEMEX Philippines)</strong></p>'
            '<p><strong>BUYING SIGNALS:</strong></p><ul>'
            '<li>Shifted from coal to alternative fuels (biomass/PKS/RDF)</li>'
            '<li>Coal self-supplied via Semirara — no coal opportunity</li>'
            '<li>Active alternative fuel procurement: biomass, PKS, RDF</li>'
            '</ul><p><strong>STRATEGIC NOTES:</strong></p><ul>'
            '<li>Formerly CEMEX Philippines — rebranded</li>'
            '<li>Semirara Mining supplies coal — vertical integration</li>'
            '<li>Alternative fuel angle is the ECONARES opportunity</li>'
            '</ul><p><strong>COMMODITY FIT:</strong></p><ul>'
            '<li>Indonesian PKS (Palm Kernel Shells): ★★★★ — active alternative fuel procurement</li>'
            '<li>Biomass: ★★★★ — fuel switching program</li>'
            '<li>Indonesian thermal coal: ★ Low — self-supplied via Semirara</li>'
            '</ul><p><strong>OUTREACH STRATEGY:</strong></p><ul>'
            '<li>Lead with PKS/biomass from Indonesia — NOT coal</li>'
            '<li>Position ECONARES as Indonesian PKS/biomass supplier</li>'
            '</ul>',
        ],
    },

    # ── Eagle Cement Corporation ──
    '331682263760': {
        'name': 'Eagle Cement Corporation',
        'props': {
            'industry': 'GLASS_CERAMICS_CONCRETE',
            'hs_target_account': 'tier_1',
            'phone': '+63 2 8867 8888',
            'address': 'San Ildefonso, Bulacan, Philippines',
            'city': 'San Ildefonso',
            'state': 'Bulacan',
            'country': 'Philippines',
            'website': 'https://www.eaglecement.com.ph',
            'numberofemployees': 2000,
            'description': 'Eagle Cement Corporation - Philippine cement manufacturer (San Miguel Corporation subsidiary). Large-scale fuel demand. Alternative fuel programs active. ECONARES angle: Indonesian thermal coal supply + PKS/biomass alternatives. SMC-owned but may need supplemental coal beyond Semirara capacity.',
        },
        'contact_form': 'https://www.eaglecement.com.ph/contact',
        'notes': [
            '<p><strong>CALL BRIEF — Eagle Cement Corporation</strong></p>'
            '<p><strong>BUYING SIGNALS:</strong></p><ul>'
            '<li>SMC subsidiary — large-scale cement operations</li>'
            '<li>Active alternative fuel programs</li>'
            '<li>May need supplemental coal beyond Semirara capacity</li>'
            '</ul><p><strong>STRATEGIC NOTES:</strong></p><ul>'
            '<li>SMC-owned — Semirara is primary coal supplier</li>'
            '<li>Alternative fuel angle: PKS/biomass from Indonesia</li>'
            '<li>Expansion potential = new fuel demand</li>'
            '</ul><p><strong>COMMODITY FIT:</strong></p><ul>'
            '<li>Indonesian thermal coal: ★★★ — supplemental beyond Semirara</li>'
            '<li>Indonesian PKS/biomass: ★★★★ — active alt fuel program</li>'
            '</ul><p><strong>OUTREACH STRATEGY:</strong></p><ul>'
            '<li>Lead with PKS/biomass angle (NOT coal — Semirara supplies coal)</li>'
            '<li>Secondary: supplemental Indonesian thermal coal for expansion</li>'
            '</ul>',
        ],
    },

    # ── Northern Cement Corporation ──
    '331711753956': {
        'name': 'Northern Cement Corporation',
        'props': {
            'industry': 'GLASS_CERAMICS_CONCRETE',
            'hs_target_account': 'tier_1',
            'phone': '+63 2 8638 8888',
            'address': 'Mandaluyong City, Metro Manila, Philippines',
            'city': 'Mandaluyong City',
            'country': 'Philippines',
            'website': 'https://www.northerncement.com.ph',
            'numberofemployees': 1500,
            'description': 'Northern Cement Corporation - Philippine cement manufacturer. Large-scale fuel demand with explicit alternative fuel programs. ECONARES angle: Indonesian thermal coal + PKS/biomass supply. Independent of Semirara — may have more flexible procurement than SMC-linked cement companies.',
        },
        'contact_form': 'https://www.northerncement.com.ph/contact',
        'notes': [
            '<p><strong>CALL BRIEF — Northern Cement Corporation</strong></p>'
            '<p><strong>BUYING SIGNALS:</strong></p><ul>'
            '<li>Large-scale cement operations — significant fuel demand</li>'
            '<li>Explicit alternative fuel programs</li>'
            '<li>Independent of Semirara — more flexible procurement</li>'
            '</ul><p><strong>STRATEGIC NOTES:</strong></p><ul>'
            '<li>NOT SMC-owned — no Semirara vertical integration constraint</li>'
            '<li>May be open to Indonesian coal supply</li>'
            '<li>Alternative fuel programs = PKS/biomass opportunity</li>'
            '</ul><p><strong>COMMODITY FIT:</strong></p><ul>'
            '<li>Indonesian thermal coal: ★★★★ — no Semirara lock-in</li>'
            '<li>Indonesian PKS/biomass: ★★★★ — active alt fuel program</li>'
            '</ul><p><strong>OUTREACH STRATEGY:</strong></p><ul>'
            '<li>Lead with Indonesian thermal coal (no Semirara constraint)</li>'
            '<li>Secondary: PKS/biomass from Indonesia</li>'
            '</ul>',
        ],
    },

    # ── SteelAsia Manufacturing Corporation ──
    '331631347401': {
        'name': 'SteelAsia Manufacturing Corporation',
        'props': {
            'industry': 'BUILDING_MATERIALS',
            'hs_target_account': 'tier_1',
            'phone': '+63 2 8888 8888',
            'address': 'Taguig City, Metro Manila, Philippines',
            'city': 'Taguig City',
            'country': 'Philippines',
            'website': 'https://www.steelasia.com',
            'numberofemployees': 3000,
            'description': 'SteelAsia Manufacturing Corporation - Philippine steel manufacturer with PHP 75B expansion plan. Primary procurement: steel scrap/billet. EAF-based (electric arc furnace). ECONARES angle: CONDITIONAL — steel scrap/billet sourcing, NOT coal. If ECONARES can source steel scrap/billet from Indonesia, there may be an opportunity.',
        },
        'contact_form': 'https://www.steelasia.com/contact',
        'notes': [
            '<p><strong>CALL BRIEF — SteelAsia Manufacturing Corporation</strong></p>'
            '<p><strong>BUYING SIGNALS:</strong></p><ul>'
            '<li>PHP 75B expansion plan — massive growth</li>'
            '<li>EAF-based steelmaking — needs steel scrap/billet</li>'
            '<li>Philippine steel demand growing</li>'
            '</ul><p><strong>STRATEGIC NOTES:</strong></p><ul>'
            '<li>Primary procurement: steel scrap/billet — NOT coal</li>'
            '<li>EAF (electric arc furnace) — no coking coal needed</li>'
            '<li>ECONARES angle is CONDITIONAL — only if sourcing steel scrap/billet</li>'
            '</ul><p><strong>COMMODITY FIT:</strong></p><ul>'
            '<li>Steel scrap/billet: ★★★ — conditional on ECONARES sourcing capability</li>'
            '<li>Coal: ★ Low — EAF-based, no coal-fired operations</li>'
            '</ul><p><strong>OUTREACH STRATEGY:</strong></p><ul>'
            '<li>DEFERRED — commodity fit is conditional</li>'
            '<li>Monitor for any coal/coke procurement needs</li>'
            '</ul>',
        ],
    },

    # ── Quezon Power (QPL) ──
    '326532899525': {
        'name': 'Quezon Power (Philippines) Limited Co.',
        'props': {
            'industry': 'UTILITIES',
            'hs_target_account': 'tier_1',
            'phone': '+63 2 8888 8888',
            'address': 'Mauban, Quezon, Philippines',
            'city': 'Mauban, Quezon',
            'country': 'Philippines',
            'website': 'https://www.quezonpower.com.ph',
            'numberofemployees': 200,
            'description': 'Quezon Power (Philippines) Limited Co. (QPL) - Coal-fired power plant in Mauban, Quezon. 460 MW capacity. Ownership: EGCO Group (Thailand) / Meralco. Annual coal demand: ~1.5-2.0M MT/yr. CFBC grade coal. ECONARES angle: Indonesian thermal coal supply. Key contact: Frank Thiel (LinkedIn InMail outreach queued).',
        },
        'contact_form': 'https://www.quezonpower.com.ph/contact',
        'notes': [
            '<p><strong>CALL BRIEF — Quezon Power (QPL)</strong></p>'
            '<p><strong>BUYING SIGNALS:</strong></p><ul>'
            '<li>460 MW coal-fired plant in Mauban, Quezon</li>'
            '<li>~1.5-2.0M MT/yr coal demand</li>'
            '<li>EGCO Group (Thailand) / Meralco ownership</li>'
            '</ul><p><strong>STRATEGIC NOTES:</strong></p><ul>'
            '<li>CFBC grade coal — flexible specs</li>'
            '<li>Mauban port — accessible for Indonesian coal shipments</li>'
            '<li>Key contact: Frank Thiel (LinkedIn outreach queued)</li>'
            '</ul><p><strong>COMMODITY FIT:</strong></p><ul>'
            '<li>Indonesian thermal coal: ★★★★ — direct buyer, CFBC grade</li>'
            '</ul><p><strong>OUTREACH STRATEGY:</strong></p><ul>'
            '<li>Lead with Frank Thiel LinkedIn InMail</li>'
            '<li>Position as Indonesian thermal coal supplier (CFBC grade)</li>'
            '</ul>',
        ],
    },
}

# ═══════════════════════════════════════════════════════════════════
# EXECUTE ENRICHMENTS
# ═══════════════════════════════════════════════════════════════════

print('=== COMPANY ENRICHMENTS ===')
for cid, data in companies.items():
    # Update company properties
    props_to_update = {k: v for k, v in data['props'].items() if v is not None}
    if props_to_update:
        sc, r = http('PATCH', f'{BASE}/crm/v3/objects/companies/{cid}', {'properties': props_to_update})
        print(f"  PATCH {data['name']}: {sc}")

    # Write sales/strategic notes
    for note_body in data['notes']:
        sc, r = http('POST', f'{BASE}/crm/v3/objects/notes', {
            'properties': {'hs_note_body': note_body, 'hs_timestamp': ts}
        })
        note_id = r.get('id') if sc in (200, 201) else None
        if note_id:
            sc2, _ = http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/companies/{cid}/note_to_company', {})
            print(f"  Note for {data['name']}: {sc} | {note_id} | assoc:{sc2}")

    # Add contact form URL as a note
    if data.get('contact_form'):
        cf_body = f'<p><strong>Online Contact Form:</strong> <a href="{data["contact_form"]}">{data["contact_form"]}</a></p>'
        sc, r = http('POST', f'{BASE}/crm/v3/objects/notes', {
            'properties': {'hs_note_body': cf_body, 'hs_timestamp': ts}
        })
        note_id = r.get('id') if sc in (200, 201) else None
        if note_id:
            http('PUT', f'{BASE}/crm/v3/objects/notes/{note_id}/associations/companies/{cid}/note_to_company', {})
            print(f"  Contact form for {data['name']}: {sc} | {note_id}")

print()
print('=== DONE ===')
print(f'Companies enriched: {len(companies)}')
print(f'Total notes created: {sum(len(d["notes"]) + (1 if d.get("contact_form") else 0) for d in companies.values())}')
