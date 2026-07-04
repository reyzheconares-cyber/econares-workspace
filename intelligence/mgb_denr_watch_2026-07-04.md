MGB/DENR COMPLIANCE WATCH — 2026-07-04

OVERVIEW

ECONARES is a Cebu-based PH commodity supplier trading nickel ore, copper ore, coal (Indonesian origin for Asian offtakers, PH-origin for PH miners), diesel, PKS, woodchips, and CPO. Two PH government bodies are central to our compliance + lead-gen monitoring:

- MGB (Mines and Geosciences Bureau) — under DENR, manages mining tenements, issues exploration permits, mineral agreements, and FTAAs. Maintains a public tenement database.
- DENR (Dept of Environment and Natural Resources) — issues Administrative Orders (AOs), Environmental Compliance Certificates (ECCs), suspension orders, and oversees export policy.

Why this watch matters for ECONARES:
1. Lead generation: MGB issues new mining permits → we know who's mining → we can approach with supply offers
2. Compliance: new AOs or policy changes can shift our deal terms
3. Competitive intel: miner suspensions or expansions = market signal

KEY 2026 DEVELOPMENTS (from web research)

1. DENR AO 2026-23 (2026): Amending ECC processing guidelines for projects in Boracay Island. Boracay-specific but signals tightening of ECC rules.
2. DENR AO 2026-04 (Jan 21, 2026): New regulation establishing administrative fines for environmental violations.
3. PH Nickel Ore Export Ban STATUS: Conflicting signals — Senate passed a bill Feb 3, 2025 to ban unprocessed nickel ore exports by 2030 (mirroring Indonesia's 2020 policy). The ban provision was LATER REMOVED in the mineral bill (per Argus, July 2025). PNIA supported the removal. STATUS: No active ban as of mid-2026, but legislative risk remains. WATCH.
4. MGB Q1 2026 production data: Metal production +28.6% YoY to ₱82.78B, driven by nickel ore, mixed nickel-cobalt sulfide, scandium oxalate. POSITIVE for ECONARES (more nickel supply available).
5. MGB suspension order (Feb 5, 2026): Woggle Corporation in Dupax del Norte — exploration permit suspended for "force majeure" under the Mining Act. Other suspensions may follow.
6. Nickel Asia Corporation: 50-60% of PH nickel production per MGB data. THE key player to monitor.
7. MGB Q4 2025 mineral industry statistics: Released ~Feb 2026.

DATA SOURCES — RANKED BY VIABILITY

| # | Source | URL | Method | Reliability | Cost |
|---|--------|-----|--------|-------------|------|
| 1 | MGB Public Portal (tenement DB) | http://databaseportal.mgb.gov.ph | Manual + scraper | 5/5 (official) | Free |
| 2 | MGB Facebook Page | facebook.com/denrmgbofficial | blogwatcher | 4/5 (active) | Free |
| 3 | DENR Press Releases | denr.gov.ph (UA-blocked, use web_search) | web_search | 5/5 (official) | Free |
| 4 | MGB Regional Facebook Pages | e.g., car.mgb.gov.ph | Manual | 4/5 (regional) | Free |
| 5 | Business Inquirer Mining | business.inquirer.net | blogwatcher | 4/5 (business press) | Free |
| 6 | Argus Media | argusmedia.com | Subscription | 5/5 (specialist) | Paid |
| 7 | Inquirer / Reuters / Bloomberg | web search | web_search | 4/5 (general press) | Free |
| 8 | Philippine Nickel Industry Association (PNIA) | [search for official site] | Manual | 3/5 (industry) | Free |
| 9 | ICLG Mining Philippines | iclg.com/practice-areas | Manual | 4/5 (legal reference) | Free |
| 10 | Chambers Mining 2026 | practiceguides.chambers.com | Manual | 4/5 (legal reference) | Free |

RECOMMENDED CONFIG

```yaml
# /home/mauiclaw/.config/econares/mgb_denr_watch.yaml
# ECONARES MGB/DENR compliance + lead-gen watch

watch:
  name: mgb_denr_compliance
  owner: 164168266  # RZH HubSpot owner ID
  version: 1.0
  created: 2026-07-04

sources:
  - name: mgb_facebook
    url: https://www.facebook.com/denrmgbofficial/
    type: blogwatcher
    refresh: weekly
    priority: high

  - name: denr_news_search
    type: web_search
    queries:
      - "MGB Philippines mining permit 2026"
      - "DENR environmental compliance order 2026"
      - "Philippines nickel mining export ban 2026"
      - "Mines and Geosciences Bureau press release"
      - "DENR Philippines mining policy 2026"
    refresh: weekly
    priority: high

  - name: business_inquirer_mining
    url: https://business.inquirer.net/tag/mining
    type: blogwatcher
    refresh: daily
    priority: medium

  - name: chambers_mining_ph
    url: https://practiceguides.chambers.com/practice-guides/mining-2026/philippines/trends-and-developments
    type: manual
    refresh: monthly
    priority: low

  - name: mgb_tenement_portal
    url: http://databaseportal.mgb.gov.ph
    type: manual
    refresh: monthly
    priority: high  # for new permit discovery
    notes: Use search filter: type=EP,status=Approved for new exploration permits

keywords:
  always_alert:
    - "nickel export ban"
    - "MGB suspension order"
    - "DENR mining moratorium"
    - "FDI mining restriction"
    - "MFTAA"
  suppress:
    - "boracay"  # Boracay-specific noise
    - "small-scale mining"  # Low relevance to ECONARES
    - "gold"  # Out of scope

output:
  destination: ~/ECONARES_WORKSPACE/intelligence/compliance/
  filename_pattern: mgb_denr_{YYYY-MM-DD}.md
  telegram_delivery: true
  telegram_chat: 707620807  # RZH personal
  format: ALL CAPS headers + bullets (no markdown)

schedule:
  # Run weekly on Monday 7 AM PHT — before the 8 AM outreach batch
  cron: "0 7 * * MON"
  timezone: Asia/Manila
  agent: subagent-leaf
  model: inherit
  workdir: /home/mauiclaw/ECONARES_WORKSPACE
  enabled_toolsets: [web, file]
  max_runtime_seconds: 240  # Conservative; web_search has been timing out at 300s
```

ROLL-OUT PLAN

Phase 1 (manual, NOW)
- RZH checks MGB Facebook + Business Inquirer mining tag weekly (5 min)
- Forward any high-signal items to the ECONARES team
- Track in a personal spreadsheet: date, signal, impact, action

Phase 2 (semi-automated, Q3 2026)
- blogwatcher-cli on MGB Facebook + Business Inquirer mining tag
- web_search cron on the 5 high-priority queries
- Daily digest to Telegram (only "always_alert" keywords)

Phase 3 (fully automated, Q4 2026)
- Tavily-powered deep-dive on high-signal items
- Auto-link to HubSpot companies (when MGB issues a permit to a company, create HubSpot company record + draft outreach)
- Weekly compliance report to ECONARES CEO Eleizer Eleguin

GOTCHAS (INDUSTRY BEST-PRACTICES)

1. UA-BLOCKED: Direct HTTP to mgb.gov.ph and denr.gov.ph returns 403. MUST use web_search or browser. Don't try curl.
2. RSS feeds unavailable: Neither MGB nor DENR publishes RSS. Workarounds: blogwatcher on Facebook, web_search on Google.
3. News lag: Government press releases often surface on Facebook days before official channels. Monitor MGB Facebook as a leading indicator.
4. Verification: A press release ≠ an actual policy change. Always check the DENR AO number + publication date + implementing rules before acting.
5. Export policy volatility: The PH nickel export ban has been proposed, removed, and re-proposed multiple times in 2025-2026. Track this as a legislative signal, not a fait accompli.
6. Filinvest Group / FDC Misamis / PSC / SRPI: These are our BUYERS' parent companies or related entities. If MGB/DENR action hits them, it affects our deal pipeline.
7. Coordinate with stale-deal detector: Cross-reference MGB/DENR news against our open deals. If a buyer's parent gets a suspension order, escalate the deal review.

SAMPLE ALERT FORMAT

---
MGB/DENR ALERT — 2026-XX-XX
Headline: [DENR issues new ECC processing guidelines for mining]
Source: DENR AO 2026-XX, Business Inquirer
Signal: New administrative order (high signal — official publication)
Impact on ECONARES: [HIGH/MEDIUM/LOW] — explain
Affected deals: [list any open deals that might be affected]
Action: [review spec docs / no action / escalate / adjust deal terms]
Time-sensitive: [yes/no — if yes, why]
---

KEY WEB RESEARCH SOURCES (verified 2026-07-04)

- business.inquirer.net/593346 — MGB Q1 2026 production data (+28.6% YoY)
- business.inquirer.net/150093 — FDC Misamis coal plant contractor selection (background)
- argusmedia.com/en/news-and-insights/latest-market-news/2698099 — PH axes planned nickel export ban
- enviliance.com/regions/southeast-asia/ph/report_16446 — DENR AO 2026-04 (Jan 21, 2026)
- eia.emb.gov.ph?page_id=392 — DENR AO 2026-23 (Boracay ECC amendments)
- practiceguides.chambers.com/practice-guides/mining-2026/philippines — legal reference
- iclg.com/practice-areas/mining-laws-and-regulations/philippines — legal reference
- facebook.com/denrmgbofficial — MGB official Facebook (active, monitor)
- gem.wiki/Misamis_Oriental_power_station — FDC Misamis plant tracker
- gem.wiki/Zamboanga_power_station — SRPI plant tracker
- jfe-steel.co.jp/en/research/report/013/pdf/013-04.pdf — PSC history (JFE subsidiary)

RECOMMENDED CRON SCHEDULE

- Mondays 7:00 AM PHT: weekly compliance digest (precedes 8 AM outreach batch)
- Daily 6:00 AM PHT: MGB Facebook blogwatcher (low-cost, low-signal)
- Monthly 1st of month: MGB tenement portal check (manual, new permit discovery)

TOP 1-LINE TAKEAWAY FOR RZH

The PH nickel export ban is a 2026 legislative risk, not yet a ban. MGB production is up 28.6% — bullish for ECONARES nickel supply. Start with manual monitoring of MGB Facebook + Business Inquirer mining tag (Phase 1), graduate to blogwatcher + web_search cron in Q3 2026.
