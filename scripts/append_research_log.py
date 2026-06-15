#!/usr/bin/env python3
"""Append round 4 log."""
from datetime import datetime
import shutil

md_path = r'C:\Users\reyma\Documents\ECONARES_WORKSPACE\contact_research_brief_2026-06-11.md'
with open(md_path, encoding='utf-8') as f:
    md = f.read()

appendix = """

---

## Appendix: Research round 4 (2026-06-11)

### Round 4: company-fill batch via email domain (KYC: blank-only)

Scanned all 174 HubSpot contacts for the pattern: blank `company` + non-generic email domain. Found 15 candidates. Pre-flight confirmed all 15 truly blank before any write. All 15 written, all 15 verified by read-back.

| Contact | Email domain | Filled company | Source |
|---|---|---|---|
| Rey Floresca | republiccement.com | Republic Cement | email domain |
| Rande Almarinez | republiccement.com | Republic Cement | email domain |
| Mark Dimal | republiccement.com | Republic Cement | email domain |
| Basal Contact | primary.com.ph | Primary Structures | email domain |
| Procurement Team | centurypeakcement.com | Century Peak Cement Manufacturing | email domain |
| San Carlos Bioenergy | scbi.ph | San Carlos Bioenergy | email domain |
| Donna Mezo | gnpk.com.ph | GNPower Kauswagan | email domain |
| EDC Procurement | energy.com.ph | First Gen (Energy Development Corporation) | email domain |
| Cleah Trinilla | rhi.com.ph | Republic Hydraulic Industries | email domain |
| SMC Corporate Secretary | sanmiguel.com.ph | San Miguel Corporation | email domain |
| Rosalie | zkjck.com | Fujian Yunding Mining (Zhongke Jinhe) | email domain |
| Justin Werner | nickelindustries.com | Nickel Industries | email domain |
| Fanfan Zhao | nickelindustries.com | Nickel Industries | email domain |
| Vijay Nair | nickelindustries.com | Nickel Industries | email domain |
| Tony Green | nickelindustries.com | Nickel Industries | email domain |

### KYC: pre-flight check
All 15 contacts had `company='None'` (truly blank) in the pre-flight response. The PATCH payload only contained `company`. The PATCH HTTP 200 for all 15. The post-flight read-back confirmed the exact expected value for all 15 (15/15 OK).

### CRM data quality findings on this batch
- **6 of 15 are role-name contacts**, not real people: Basal Contact, Procurement Team, San Carlos Bioenergy, EDC Procurement, SMC Corporate Secretary, and Donna Mezo. The audit classified these as role-name earlier. Filled company is still correct (they are at those companies, just not specific people). They should be flagged for quarantine consideration.
- **Rosalie** is a partial name (no last name). Email domain maps to Fujian Yunding Mining, but the contact is incomplete.
- The 4 Republic Cement contacts (Rey, Rande, Mark) and Rosalie (mapped to Fujian Yunding Mining via zkjck.com) are all members of deals that already exist in the pipeline.

### Net result this round
- **15 verified writes** (all `company` field, all blank->filled, all KYC safe)
- 0 destructive overwrites
- 6 role-name contacts re-confirmed for quarantine

### Updated session grand totals
- 3 destination_port writes (turn 1)
- 5 LinkedIn URL writes (round 1: Dave; round 2: Rose, Albarr, Qi Sun; round 3: Rachelle, Jeffren)
- 2 phone writes (round-up: Chen Bin, Feifei Liu)
- 17 company writes (round 3: Jeffren, Mark Tagle; round 4: 15 batch)
- = **27 verified additive writes this session**, 0 destructive overwrites
- 4 CRM data quality findings flagged across rounds
- 6 role-name contacts re-confirmed for quarantine
"""

with open(md_path, 'a', encoding='utf-8') as f:
    f.write(appendix)

shutil.copy(md_path, r'C:\Users\reyma\Documents\ECONARES_WORKSPACE\_backups\Workspace_2026-05-08_17-20\contact_research_brief_2026-06-11.md')

print(f"Round 4 log appended. Total chars: {len(md) + len(appendix)}")
