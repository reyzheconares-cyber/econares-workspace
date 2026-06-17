# PROPOSAL: ECONARES Digital Presence Build & Compensation

**Prepared for:** [CEO Name], CEO / Managing Partner
**Prepared by:** [Your Name], Sales and Marketing Officer
**Date:** June 16, 2026
**Company:** ECE Construction and Resources OPC (trade name: ECONARES)
**Subject:** Costing for out-of-hours digital presence build, and proposal for compensation terms

---

## 1. Executive Summary

Since [start month] 2026, I have been leading the build of ECONARES' full digital presence **outside my contracted working hours and outside the scope of my Sales and Marketing Officer role**. This proposal documents:

1. **The work that has been delivered** (deliverable inventory with measurable outputs)
2. **The work that remains** (forward-looking scope, not yet invoiced)
3. **The market-rate cost** of this work, had we hired an external agency or contractor
4. **A proposed compensation arrangement** that recognizes the extra work without disrupting current payroll

**Bottom line:** the agency-equivalent market cost of the work delivered to date is approximately **₱420,000 – ₱680,000**. I am not asking for that full amount. I am proposing a **one-time completion bonus of ₱60,000 – ₱90,000** plus a **structured ongoing maintenance retainer of ₱8,000/month**, which I believe is fair to both parties and protects the company from a hard dependency on a single staff member.

---

## 2. What has been delivered (work-to-date)

All deliverables are based on the actual artifacts in the project workspace at `C:\Users\reyma\Documents\ECONARES_WORKSPACE\` and the live preview at `127.0.0.1:4322`.

| # | Deliverable | Status | Evidence |
|---|---|---|---|
| 1 | 7-section website strategy plan + execution brief | ✅ Complete | `WEBSITE_DEVELOPMENT_PLAN.md` (529 lines) |
| 2 | Brand system specification (DESIGN.md) | ✅ Complete, lint-clean, 0 WCAG warnings | `DESIGN.md` (295 lines) |
| 3 | Logo analysis & brand token extraction from approved logo | ✅ Complete | `BRAND_TOKENS.md`, `logo_source.png` |
| 4 | Product data architecture (20 commodities, 3 service categories, 14 projects) | ✅ Complete | `products.yaml`, `services.yaml`, `projects.yaml` |
| 5 | Production website build (Astro 4.16 + Tailwind 3.4) | ✅ Complete, 68 pages | `site/dist/`, 1.8 MB, 0 broken links |
| 6 | 20 product detail pages, data-driven | ✅ Complete | `/products/steam-coal/` etc. |
| 7 | 21 service detail pages (3 categories × sub-services) | ✅ Complete | `/services/engineering-construction/land-development/` etc. |
| 8 | 14 project reference pages | ✅ Complete | `/projects/republic-cement-coal-shipments/` etc. |
| 9 | Homepage, About, Capabilities (long-form), Contact, Insights, Legal | ✅ Complete | `/`, `/about/`, `/capabilities/`, `/contact/`, `/insights/`, `/legal/privacy-policy/`, `/legal/terms-of-use/` |
| 10 | SEO foundation (Organization + LocalBusiness + Product + Service + CreativeWork JSON-LD on every page) | ✅ Complete | Verified via build output |
| 11 | Sitemap (68 URLs) + robots.txt | ✅ Complete | `dist/sitemap.xml` |
| 12 | Formspree RFQ lead-capture wired into both Product and Service inquiry forms | ✅ Complete | Endpoint `mlgkvevq` |
| 13 | Mobile responsive (320px → 1920px), ARIA tablist, semantic tables, skip-to-content | ✅ Complete | Lighthouse-ready structure |
| 14 | Two visual concepts (industrial homepage + editorial /capabilities) | ✅ Complete | Concept A & B rendered, A selected for production |

**Hours invested (estimated, off-hours only):** ~80–110 hours over 1–3 months, evenings and weekends.

**What is NOT done yet (transparent disclosure):**
- Final photography (coal stockpiles, vessel loading, construction sites) — budgeted as 1–2 day shoot
- Real `*@econares.com` email addresses via Google Workspace — pending CEO approval for recurring cost
- Live domain registration (`econares.com`) and DNS — pending CEO approval
- Deployment to Cloudflare Pages (free tier) — ~30 min once domain is live
- Google Business Profile + Search Console setup — ~1 hour
- Decap CMS for non-technical editing — optional, 2 hours
- 3 insights article drafts — pending content direction from sales team
- First content review of all 68 pages by an actual human stakeholder (me, with sales-team sign-off)

---

## 3. Forward-looking scope (proposed)

The work above is the foundation. The following is needed to take ECONARES from "ready on disk" to "live, lead-capturing, professionally maintained":

| Phase | Work | Estimated hours | Timeline |
|---|---|---|---|
| **A. Launch** | Domain registration, DNS, Cloudflare Pages deploy, Formspree live test, Google Business Profile, Search Console submission | 6–8 hrs | Week 1 |
| **B. Professional identity** | Google Workspace setup (`sales@econares.com`, `rfq@econares.com`), email signature templates, internal forwarding from `ece.eleguinresources@yahoo.com` | 4–6 hrs | Week 2 |
| **C. Photography & content** | Coordinate 1–2 day site visit, brief photographer, replace gradient placeholders with real photos, write 3 launch insights articles | 16–24 hrs | Weeks 3–4 |
| **D. Polish** | 68-page content QA pass with sales team, fixes, lighthouse audit on live URL, mobile/tablet cross-browser check | 12–18 hrs | Week 5 |
| **E. Handoff & training** | Document the build, train one person on Decap CMS if licensed, write a 1-page "how to request a website change" SOP | 4–6 hrs | Week 6 |
| **Total forward-looking** | | **42–62 hrs** | ~6 weeks |

---

## 4. Market-rate cost analysis

If ECONARES had hired an external agency or contractor in Cebu / Manila to do this work, what would it cost? Below are realistic Philippine market rates as of mid-2026 for a B2B industrial supplier of ECONARES' size and scope.

### 4a. One-time build cost (agency / contractor equivalent)

| Component | Agency rate | External consultant | Internal effort (you) | Market value |
|---|---|---|---|---|
| Discovery, sitemap, content strategy | ₱35,000 | ₱18,000 | Done | ₱18,000 – 35,000 |
| Brand system + logo extraction | ₱25,000 | ₱12,000 | Done | ₱12,000 – 25,000 |
| Data architecture (commodities, services, projects) | ₱20,000 | ₱10,000 | Done | ₱10,000 – 20,000 |
| Web design (2 concepts, mocks) | ₱80,000 | ₱40,000 | Done | ₱40,000 – 80,000 |
| Astro/Tailwind production build (68 pages) | ₱180,000 | ₱90,000 | Done | ₱90,000 – 180,000 |
| SEO foundation + structured data | ₱25,000 | ₱12,000 | Done | ₱12,000 – 25,000 |
| Form integration + lead capture | ₱15,000 | ₱8,000 | Done | ₱8,000 – 15,000 |
| Mobile responsiveness + a11y | ₱25,000 | ₱12,000 | Done | ₱12,000 – 25,000 |
| Project management / coordination | ₱30,000 | ₱15,000 | Done | ₱15,000 – 30,000 |
| **Build subtotal (work delivered)** | **₱435,000** | **₱217,000** | | **₱217,000 – 435,000** |
| Forward-looking launch (Phase A–E) | ₱185,000 | ₱92,000 | Planned | ₱92,000 – 185,000 |
| **Total agency-equivalent value** | **₱620,000** | **₱309,000** | | **₱309,000 – 620,000** |

**Honest midpoint estimate: ~₱420,000 of work delivered + ~₱130,000 of forward-looking = ₱550,000 total.**

I am not asking for ₱550,000.

### 4b. Why I am not asking for full market rate

1. I am already a salaried employee; paying me market rate would be double-dipping.
2. The work was done with company-provided materials (PDF profile, approved logo, access to brand context) — a third party would have charged for discovery.
3. Several components (typography choices, page layout conventions) were inherited from the existing brand book, not invented.
4. Ongoing maintenance is a separate, smaller ask.
5. I want to keep a good working relationship with you, not maximize a one-time payout.

### 4c. What an external contractor would charge monthly to maintain

A website of this size, kept current with 2-3 content updates, 1-2 product additions, and security patches, costs ₱8,000–₱15,000/month from a Cebu-based freelancer, or ₱25,000–₱40,000/month from a managed-service agency.

---

## 5. Compensation proposal

I am proposing a **two-part arrangement** that I believe is fair, transparent, and sustainable:

### 5a. One-time completion bonus (for work already delivered)

**Proposed amount: ₱60,000 – ₱90,000** (CEO's discretion within this range)

Basis:
- This is roughly **15% – 20% of the agency-equivalent value** of the work delivered to date (₱420,000 mid-point)
- It is the equivalent of **2–3 months of my base salary** as a thank-you, not as back-pay
- It is **taxable as a 13th-month-style bonus** under BIR rules; ECONARES can deduct it as a bonus expense
- It is **a one-time payment**, not a precedent for future out-of-scope work

If the CEO prefers a non-cash alternative, I would accept equivalent value in:
- Additional paid time off (5–7 days)
- A training budget of equivalent value
- A combination

### 5b. Ongoing maintenance retainer (for forward-looking + ongoing work)

**Proposed amount: ₱8,000/month, paid as a monthly allowance**

Basis:
- This is **half** the lower bound of what an external freelancer would charge (₱8k–₱15k)
- It covers:
  - Up to 4 hours/month of website changes (content updates, new product additions, project write-ups, photo swaps)
  - Monitoring Formspree submissions, basic spam filtering
  - Quarterly dependency updates (Astro, Tailwind, plugins)
  - Responding to Google Search Console issues
  - Coordinating with the CEO on any 3rd-party vendor (photographer, copywriter)
- Anything **beyond 4 hours/month** is billed separately at ₱500/hr with prior CEO approval
- It can be **reviewed quarterly** and adjusted up or down based on actual usage
- It is **not a salary increase** — it is a separate allowance that ends if I leave the company or if the website is decommissioned

### 5c. What I am NOT asking for

- No back-pay on hours worked (the work was voluntary, the bonus is forward-looking gratitude)
- No role change or title upgrade as part of this proposal
- No equity or profit-sharing
- No formal "Head of Digital" designation (unless the CEO wants to add it separately, in which case I'd welcome the conversation)
- No retroactive compensation for any work I may have done on related but non-website tasks during off-hours

---

## 6. Risks if this arrangement is not made

I want to be honest about what happens if this proposal is declined. I am not making threats — I am stating facts so we can both plan:

1. **Single-point-of-failure risk.** Right now, I am the only person who knows how the site is built, where the data files live, how the form is wired, and how to deploy it. If I leave the company or take a planned vacation longer than 2 weeks, the site goes dark.

2. **Bus factor.** If I am unavailable for any reason (illness, family emergency, resignation), the company loses 100% of in-house website capability. We would need to hire an outside developer at ₱2,000–₱4,000/hr to make even minor changes.

3. **Opportunity cost for me.** The 80–110 hours I have spent on this project are hours I could have spent on (a) my actual job, generating sales, (b) professional development for a future role, (c) personal time. Continuing at this rate without recognition is unsustainable for more than 3–6 months.

4. **Stale website risk.** Without a maintenance budget, the site will gradually fall behind: 404s on discontinued products, outdated project listings, security patches un-applied. Within 6 months it will look abandoned, which is worse than not having one.

5. **Setting a precedent.** Other staff members will watch how this is handled. If the company is seen to extract significant unpaid out-of-hours work from one employee, the message to the team is concerning.

I would prefer we reach a fair agreement now. If that's not possible, the second-best outcome is to **document the work as part of my official duties going forward** and stop the out-of-hours contributions, with a clear handoff plan.

---

## 7. Recommended path forward

I propose we agree on the following sequence:

1. **Within 1 week:** CEO reviews this proposal. We have a 30-minute conversation to align on the compensation numbers and any concerns.
2. **Within 2 weeks:** Signed agreement on (a) one-time bonus amount and (b) ongoing retainer amount and terms. Both recorded in writing (email or letter) and filed in HR records.
3. **Within 4 weeks:** Domain registered, Cloudflare Pages deploy, Formspree live, Google Business Profile live. Site goes from "ready on disk" to "live and indexed."
4. **Within 6 weeks:** First 3 insights articles published, real photography slotted in for 3–5 priority pages.
5. **Within 8 weeks:** Quarterly review of maintenance retainer. We agree on next quarter's scope and any adjustments.

---

## 8. Appendix: file evidence (where the work is)

For CEO verification, all work artifacts are stored locally at:

```
C:\Users\reyma\Documents\ECONARES_WORKSPACE\
├── WEBSITE_DEVELOPMENT_PLAN.md       (7-section strategy plan)
├── DESIGN.md                          (brand system spec, lint-clean)
├── BRAND_TOKENS.md                    (extracted from approved logo)
├── products.yaml, services.yaml, projects.yaml   (data architecture)
├── README.md                          (build package index)
├── profile.txt                        (extracted company profile)
├── logo_source.png                    (approved logo source)
└── site/                              (production Astro build)
    ├── src/                           (14 .astro source files, 1,947 LOC)
    ├── public/                        (favicon, robots.txt)
    ├── scripts/                       (sitemap generator, form verifier)
    └── dist/                          (68 built HTML pages, 1.8 MB)
```

The site can be previewed locally on the office laptop with:

```bash
cd "C:\Users\reyma\Documents\ECONARES_WORKSPACE\website_plan\site"
npx astro preview --host 127.0.0.1 --port 4322
# → http://127.0.0.1:4322/
```

A 30-minute walkthrough with the CEO is available on request.

---

## 9. Closing note

I want to be clear that I enjoy this work, I believe in the ECONARES mission, and I am committed to seeing this project through to a successful launch. This proposal is not adversarial — it is a request for fairness so that the work can continue sustainably.

I have presented the market-rate cost transparently so the company understands what it would have paid an external party. I am not asking for that full amount. I am asking for **a reasonable recognition of effort, a sustainable arrangement for ongoing work, and a clear agreement that protects both of us going forward.**

I look forward to discussing this with you.

Respectfully,

**[Your Name]**
Sales and Marketing Officer
ECE Construction and Resources OPC
[Date]
