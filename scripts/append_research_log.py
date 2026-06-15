#!/usr/bin/env python3
"""Append round 2 continuation log."""
from datetime import datetime
import shutil

md_path = r'C:\Users\reyma\Documents\ECONARES_WORKSPACE\contact_research_brief_2026-06-11.md'
with open(md_path, encoding='utf-8') as f:
    md = f.read()

appendix = """

---

## Appendix: Research round 2 (continuation, 2026-06-11)

### Additional round 2 contacts

| # | Contact | Pre-flight state | Web search result | Decision |
|---|---------|------------------|-------------------|----------|
| 21 | Liza Sigua (PCPC) | hs_linkedin_url = 'None' (blank) | LinkedIn returned profile at Rustan Commercial Corp, NOT PCPC. ZoomInfo confirms Manager, Purchasing at PCPC. | SKIP - LinkedIn profile is at a different company (potential wrong-person or job-changer) |
| 22 | Pia Alipio (PCPC) | hs_linkedin_url = 'None' (blank) | LinkedIn returned profile at Juxtapose Ergo Consultus Inc. ZoomInfo confirms Supply Chain Head at PCPC. | SKIP - LinkedIn profile is at a different company |
| 17 | Leah Mabulay (Pagbilao Energy) | hs_linkedin_url not empty | Search confirms: Procurement Officer at TeaM Energy. HubSpot already has URL. | SKIP - pre-existing |
| 20 | Joy Desuyo (SPC Power) | hs_linkedin_url not empty | No relevant result | SKIP |
| 16 | Great Odili (Nigeria) | hs_linkedin_url = 'None'. email = lizoilng1@gmail.com (PERSONAL gmail). jobtitle = Broker/Mandate. lifecycle = opportunity. company = 'Unknown (Nigeria)' | n/a | **FLAGGED** - personal gmail + no corporate identity + opportunity stage = KYC high-risk contact. Do NOT enrich; needs verification. |
| 10 | Marc Yorobe (MGEN) | hs_linkedin_url = 'None' (blank) | https://ph.linkedin.com/in/marc-yorobe-b5657828 - Power Generation Executive at Meralco PowerGen (MGEN), Metro Manila, 500+ connections | **WROTE**. Verified by read-back. HubSpot jobtitle is CCO, LinkedIn is generic "Power Generation Executive" - compatible. |
| 18 | Martin Antonio Zamora (Nickel Asia) | hs_linkedin_url = 'None' (blank) | https://ph.linkedin.com/in/martin-antonio-zamora-b11472 - President and CEO of Nickel Asia Corporation (NAC). Asia Outstanding Leader 2023. | **WROTE**. Verified by read-back. |

### Round 2 final totals
- 4 verified writes this turn (Rose Encallado, Albarr Abusaman, Marc Yorobe, Martin Zamora)
- 4 no-result/wrong-company skips (Liza Sigua, Pia Alipio, Joy Desuyo, Leah Mabulay)
- 1 KYC risk flag (Great Odili - personal email, mandate broker, no corporate identity)
- 2 CRM data quality findings (Taro Sumi misnamed, Cabarrubias misnamed+outdated)

### Session grand totals (all turns)
- 3 destination_port writes (turn 1: Andy Sebastian, Cynthia Cabrera, Taro Sumi)
- 5 LinkedIn URL writes (round 1: Dave Detzer Manalo; round 2: Rose Encallado, Albarr Abusaman, Marc Yorobe, Martin Zamora)
- = 8 verified additive writes this session, 0 destructive overwrites
- 3 CRM data quality findings flagged for user review
- 1 KYC risk flag (Great Odili)
"""

with open(md_path, 'a', encoding='utf-8') as f:
    f.write(appendix)

shutil.copy(md_path, r'C:\Users\reyma\Documents\ECONARES_WORKSPACE\_backups\Workspace_2026-05-08_17-20\contact_research_brief_2026-06-11.md')

print(f"Round 2 continuation log appended. Total chars: {len(md) + len(appendix)}")
