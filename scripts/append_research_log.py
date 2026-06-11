#!/usr/bin/env python3
"""Append research round 1 log to the MD brief."""
from datetime import datetime
import shutil

md_path = r'C:\Users\reyma\Documents\ECONARES_WORKSPACE\contact_research_brief_2026-06-11.md'
with open(md_path, encoding='utf-8') as f:
    md = f.read()

appendix = """

---

## Appendix: Research round 1 (2026-06-11)

External research pass on the top 5 priority contacts. Method: web_search for "name" "company" LinkedIn for each.

### Verdict per contact

| # | Contact | LinkedIn search result | Decision |
|---|---------|------------------------|----------|
| 1 | Andy Sebastian (MGen-GBP) | Profile found, title=Fuel Manager | SKIP write - HubSpot already had hs_linkedin_url (verified: linkedin.com/in/andy-sebastian-1b09b421). KYC: don't overwrite verified data. |
| 2 | Cynthia Cabrera (Holcim PH) | Profile found, title=Procurement Manager | SKIP write - HubSpot already had hs_linkedin_url (verified: linkedin.com/in/cynthia-cabrera-b168bb132). NOTE: LinkedIn shows Procurement Manager; HubSpot shows Procurement Lead. Not overwriting title (ECONARES may have reason). |
| 3 | Rose Calba (Solaris) | No real LinkedIn match | SKIP - no verified source |
| 4 | Tina Chen (Fujian Yunding) | 2 candidates, both wrong industry (Stone / Oready) | SKIP - no verified source for her actual company |
| 5 | Dave Detzer C. Manalo (Sem-Calaca) | Profile found + cross-confirmed on semiraramining.com/our_organization/content/Management_Team | WROTE hs_linkedin_url=https://ph.linkedin.com/in/dave-detzer-manalo-80327728 (HubSpot was blank). Verified by read-back. |

### Net result this round
- 1 verified write (Dave Detzer Manalo - new LinkedIn URL)
- 0 destructive overwrites (Andy & Cynthia reverted when audit detected the pre-existing values)
- 2 contacts need different research (Rose Calba, Tina Chen) - their emails do not surface LinkedIn profiles; try direct company directory lookups

### Next research direction
- For Rose Calba: try solaris.com.ph staff page, or industry conference speaker lists
- For Tina Chen: try Fujian Yunding Mining Co. website, or Chinese-language LinkedIn search
- For the rest of the top 20: same web_search pattern, with pre-check that hs_linkedin_url is empty before writing
"""

with open(md_path, 'a', encoding='utf-8') as f:
    f.write(appendix)

shutil.copy(md_path, r'C:\Users\reyma\Documents\ECONARES_WORKSPACE\_backups\Workspace_2026-05-08_17-20\contact_research_brief_2026-06-11.md')

print(f"Appendix appended. Total chars: {len(md) + len(appendix)}")
