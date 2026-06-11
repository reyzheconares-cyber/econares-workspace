#!/usr/bin/env python3
"""Build the research brief CSV + MD summary. Save to canonical ECONARES workspace."""
import json
import csv
import re
import os
from datetime import datetime
from collections import defaultdict

scored = json.load(open(r'C:\Users\reyma\AppData\Local\Temp\research_brief_full.json'))
xlsx = json.load(open(r'C:\Users\reyma\AppData\Local\Temp\xlsx_contacts.json'))

# Build xlsx company intel for context
xlsx_by_company = defaultdict(list)
for c in xlsx:
    co = (c.get('company') or '').strip()
    if co:
        xlsx_by_company[co.lower()].append(c)


def safe(s):
    return (s or '').strip()


def norm(s):
    s = (s or '').lower()
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


# Build CSV: one row per real-named lead
CSV_PATH = r'C:\Users\reyma\Documents\ECONARES_WORKSPACE\contact_research_brief_2026-06-11.csv'
MD_PATH = r'C:\Users\reyma\Documents\ECONARES_WORKSPACE\contact_research_brief_2026-06-11.md'

# Add context from XLSX for the company (if any)
def company_context(co):
    co_n = norm(co)
    matches = []
    for k, v in xlsx_by_company.items():
        if co_n == k or co_n[:8] == k[:8]:
            matches.extend(v)
    if not matches:
        return None
    # Take the highest-intel match
    def s(c):
        try:
            return int(c.get('intel_score') or 0)
        except Exception:
            return 0
    best = max(matches, key=s)
    return {
        'xlsx_company': best.get('company'),
        'xlsx_industry': best.get('industry'),
        'xlsx_region': best.get('region'),
        'xlsx_country': best.get('country'),
        'xlsx_intel': best.get('intel_score'),
        'xlsx_website': best.get('website'),
        'xlsx_logistics': best.get('logistics'),
        'xlsx_phone': best.get('phone'),
    }


with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow([
        'priority_rank', 'priority_score', 'hub_id',
        'name', 'email', 'phone', 'jobtitle', 'company',
        'lifecycle', 'lead_status', 'buying_role',
        'lastmodified', 'createdate',
        'has_personal_email', 'corporate_domain',
        'xlsx_company_match', 'xlsx_intel_score', 'xlsx_industry', 'xlsx_region', 'xlsx_country', 'xlsx_website', 'xlsx_logistics', 'xlsx_phone',
        'research_action', 'notes'
    ])
    for i, lead in enumerate(scored, 1):
        ctx = company_context(lead.get('company', '')) or {}
        em = safe(lead.get('email', ''))
        is_personal = bool(em) and em.split('@')[0].lower() not in (
            'info', 'contact', 'sales', 'admin', 'enquiries', 'enquiry', 'procurement', 'inquiry', 'inquiries'
        ) and not em.split('@')[0].lower().startswith('noreply')
        dom = em.split('@')[-1].lower() if '@' in em else ''
        is_corporate = bool(dom) and not any(d in dom for d in ('gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'))

        # determine research action
        actions = []
        if not lead.get('phone'):
            actions.append('find_phone')
        jt = (lead.get('jobtitle') or '').lower()
        if not lead.get('jobtitle') or jt in ('procurement', 'sales', 'trading', 'general info', 'marketing'):
            actions.append('verify_title')
        if not lead.get('linkedin'):
            actions.append('find_linkedin')
        if not lead.get('buying_role') and lead.get('lifecycle') in ('opportunity', 'salesqualifiedlead'):
            actions.append('assign_buying_role')
        if not ctx:
            actions.append('verify_company_in_xlsx_or_industry_db')

        w.writerow([
            i, lead.get('priority_score', 0), lead.get('id', ''),
            lead.get('name', ''), em, lead.get('phone', ''), lead.get('jobtitle', ''), lead.get('company', ''),
            lead.get('lifecycle', ''), lead.get('lead_status', ''), lead.get('buying_role', ''),
            lead.get('modified', ''), lead.get('createdate', ''),
            'Y' if is_personal else 'N',
            'Y' if is_corporate else 'N',
            ctx.get('xlsx_company', ''), ctx.get('xlsx_intel', ''), ctx.get('xlsx_industry', ''),
            ctx.get('xlsx_region', ''), ctx.get('xlsx_country', ''), ctx.get('xlsx_website', ''),
            ctx.get('xlsx_logistics', ''), ctx.get('xlsx_phone', ''),
            '; '.join(actions),
            ''
        ])

print(f"CSV saved: {CSV_PATH}")
print(f"Rows: {len(scored)}")

# MD summary
top_20 = scored[:20]

# Counters
with_email = sum(1 for l in scored if l.get('email'))
with_phone = sum(1 for l in scored if l.get('phone'))
with_lifecycle_opp = sum(1 for l in scored if l.get('lifecycle') in ('opportunity', 'salesqualifiedlead', 'marketingqualifiedlead'))
in_xlsx_company = sum(1 for l in scored if company_context(l.get('company', '')))

md = []
md.append("# ECONARES - HubSpot Contact Research Brief")
md.append("**Generated:** " + datetime.now().strftime('%Y-%m-%d %H:%M'))
md.append("**Source:** HubSpot (176 contacts) + ECONARES master XLSX (392 contacts)")
md.append("**Author:** ECONARES audit pipeline")
md.append("")
md.append("---")
md.append("")
md.append("## What this is")
md.append("")
md.append("The audit-first enrichment pass for the standing goal *enrich our HubSpot contacts that we have not connected yet, per industry best practices* revealed that **96 real-named HubSpot contacts have no XLSX row** - they cannot be enriched by the master tracker, and the KYC integrity rule blocks fabricating data for them. They need external research (LinkedIn, company sites, industry databases, direct outreach verification).")
md.append("")
md.append("This brief ranks all 96 contacts by enrichment priority and lists the specific research action needed for each.")
md.append("")
md.append("---")
md.append("")
md.append("## Pipeline summary")
md.append("")
md.append("- **Total HubSpot contacts:** 176")
md.append("- **Fully enriched (10/10 core fields):** 0")
md.append("- **Total XLSX contacts:** 392")
md.append("- **High-confidence XLSX matches surviving KYC filter:** 0 (all 5 candidates blocked - see audit report)")
md.append("- **Additive writes this session:** 3 (destination_port for Andy Sebastian, Cynthia Cabrera, Taro Sumi - all verified)")
md.append(f"- **Real-named leads without XLSX match:** **{len(scored)}** <- this brief covers them")
md.append("- **Role-name contacts (deferred, separate decision needed):** 27")
md.append("- **ECONARES-internal aliases (deferred, separate decision needed):** 8")
md.append("- **Ed Finch / bulk-ore duplicates (deferred):** 4")
md.append("- **No-name orphans (deferred, separate decision needed):** 7")
md.append("")
md.append("---")
md.append("")
md.append("## How the priority score works")
md.append("")
md.append("Each lead is scored on:")
md.append("- +30 for lifecycle=opportunity (real revenue/pipeline contact)")
md.append("- +25 for lifecycle=salesqualifiedlead")
md.append("- +20 for lifecycle=marketingqualifiedlead")
md.append("- +10 if has a personal (non-role) email")
md.append("- +5 if has a corporate-domain email")
md.append("- +5 if lead_status is OPEN or IN_PROGRESS")
md.append("- +20 if their company is in XLSX with intel_score=100")
md.append("- +10 if buying_role already set (active deal context)")
md.append("- +3 if recently modified in HubSpot")
md.append("")
md.append("**Higher score = higher priority for research effort.**")
md.append("")
md.append("---")
md.append("")
md.append("## Top 20 research targets")
md.append("")
md.append("| # | Score | Name | Company | Lifecycle | Email | Research actions |")
md.append("|---|------:|------|---------|-----------|-------|------------------|")

for i, lead in enumerate(top_20, 1):
    nm = safe(lead.get('name', ''))[:30]
    co = safe(lead.get('company', ''))[:30]
    em = safe(lead.get('email', ''))[:35]
    lc = safe(lead.get('lifecycle', ''))[:22]
    s = lead.get('priority_score', 0)
    actions = []
    if not lead.get('phone'):
        actions.append('find_phone')
    jt = (lead.get('jobtitle') or '').lower()
    if not lead.get('jobtitle') or jt in ('procurement', 'sales', 'trading', 'general info', 'marketing'):
        actions.append('verify_title')
    if not lead.get('linkedin'):
        actions.append('find_linkedin')
    if not lead.get('buying_role') and lead.get('lifecycle') in ('opportunity', 'salesqualifiedlead'):
        actions.append('assign_buying_role')
    if not company_context(lead.get('company', '')):
        actions.append('verify_company')
    md.append(f"| {i} | {s} | {nm} | {co} | {lc} | {em} | {'; '.join(actions) or 'verify phone + title + linkedin'} |")

md.append("")
md.append("---")
md.append("")
md.append("## Aggregate stats for the 96 leads")
md.append("")
md.append(f"- **With email:** {with_email} / 96 ({100*with_email//96}%)")
md.append(f"- **With phone:** {with_phone} / 96 ({100*with_phone//96}%)")
md.append(f"- **Advanced lifecycle (Opp/SQL/MQL):** {with_lifecycle_opp} / 96 ({100*with_lifecycle_opp//96}%)")
md.append(f"- **Company confirmed in XLSX:** {in_xlsx_company} / 96 ({100*in_xlsx_company//96}%)")
md.append("")
md.append("---")
md.append("")
md.append("## KYC integrity constraints applied")
md.append("")
md.append("Per ECONARES policy: *Never fabricate placeholder data to hit fill targets. Leave empty + mark TBD if unverified. Verified parent routing (Aboitiz/MGEN/SMC/FGEN/EDC) is the only legitimate bulk-fill path.*")
md.append("")
md.append("Concretely, this brief:")
md.append("- Reports only data that exists in HubSpot or XLSX - no inferred values")
md.append("- Does **not** populate destination_port, material_needed, or other ECONARES custom fields for any of these 96 contacts (XLSX has no row for them, so there is no source of truth)")
md.append("- Does **not** assign buying_role to contacts that have no associated Deal or Target Account")
md.append("- Does **not** mark any contact as customer or opportunity without supporting HubSpot lifecycle evidence")
md.append("")
md.append("---")
md.append("")
md.append("## Next-step options (pick one)")
md.append("")
md.append("1. **External research sweep** on the top 10-20 contacts. I can run a batch web search (LinkedIn + company site + industry database) and return verified phone, title, LinkedIn URL, and any new company context. **Cost:** time + web search tokens. **Output:** patchable enrichment payloads with sources.")
md.append("2. **Direct outreach attempt** to the top 5 highest-priority contacts (Rachel Castillo, Allan Saquilayan, Andy Sebastian, Cynthia Cabrera, Rose Calba). Skip the research and just verify via email reply. **Cost:** risk of looking unprepared. **Output:** if they reply, we have verified data.")
md.append("3. **XLSX cleanup first** - fix the ~20 placeholder phone numbers, ~10 third-party-domain emails, and 5 mismatched company rows in the master tracker. **Cost:** ~1 hour of careful work. **Output:** the XLSX becomes a real enrichment source for the next pass.")
md.append("")
md.append("My recommendation: **option 1** (external research sweep on the top 10) is the highest-ROI move. It actually fills the gaps without violating KYC, and the deliverables are re-usable for the broader pipeline.")
md.append("")
md.append("---")
md.append("")
md.append("## Files in this brief")
md.append("")
md.append("- `contact_research_brief_2026-06-11.csv` - full ranked list, 96 rows, ready for import to Notion/Airtable/spreadsheet workflow")
md.append("- `contact_research_brief_2026-06-11.md` - this human-readable summary")
md.append("- `audit_artifacts/` (scripts dir) - supporting JSON: hub_all_contacts.json, hub_gaps_v2.json, matches.json, unmatched.json, xlsx_contacts.json, research_brief_full.json")
md.append("")
md.append("---")
md.append("")
md.append(f"*Brief regenerated automatically each session. Last build: {datetime.now().isoformat(timespec='minutes')}*")

with open(MD_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))

print(f"MD saved: {MD_PATH}")
print(f"  size: {os.path.getsize(MD_PATH)} bytes")

# List all artifacts produced
print("\n=== ARTIFACTS ===")
for p in [CSV_PATH, MD_PATH]:
    if os.path.exists(p):
        print(f"  {p}  ({os.path.getsize(p)} bytes)")
    else:
        print(f"  MISSING: {p}")
