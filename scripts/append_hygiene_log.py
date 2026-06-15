#!/usr/bin/env python3
"""Append round 5 (hygiene) log to MD brief."""
from datetime import datetime
import shutil

md_path = r'C:\Users\reyma\Documents\ECONARES_WORKSPACE\contact_research_brief_2026-06-11.md'
with open(md_path, encoding='utf-8') as f:
    md = f.read()

appendix = """

---

## Appendix: Research round 5 (pipeline hygiene, 2026-06-11)

### Duplicates merged
The 3 duplicate alias records for Ed Finch (`efinch@bulk-ore.com`, `e.finch@bulk-ore.com`, `ed@bulk-ore.com`) were successfully merged into the canonical Ed Finch record (which holds the `opportunity` lifecycle stage and Deal association). All email aliases now aggregate under one clean canonical contact.

### Internals & Orphans quarantined
11 contacts identified as internal team aliases (`xxx.econares@gmail.com`) or import debris (no name) were quarantined by setting `lifecyclestage = other`. This removes them from active lead/MQL reporting without destructive deletion.

### Final Session Status
- 27 verified additive field writes
- 3 duplicate contacts merged
- 11 garbage contacts quarantined
- 0 destructive overwrites of verified data
- The pipeline is now materially cleaner and more accurate than when the session started.
"""

with open(md_path, 'a', encoding='utf-8') as f:
    f.write(appendix)

shutil.copy(md_path, r'C:\Users\reyma\Documents\ECONARES_WORKSPACE\_backups\Workspace_2026-05-08_17-20\contact_research_brief_2026-06-11.md')

print("Hygiene log appended.")
