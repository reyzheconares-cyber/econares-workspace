# LIVE DEMO PRACTICE SCRIPT
## ECONARES B2B WEBSITE — CEO + STAFF PRESENTATION REHEARSAL

**DATE OF PRESENTATION:** 2026-07-08
**PREPARATION DATE:** 2026-07-07
**DEMO URL:** https://econares-website.vercel.app
**LOCAL FALLBACK:** http://127.0.0.1:4323/ (if Vercel is down)
**TARGET DURATION:** 12-15 MINUTES (slides allow 15 min, build in 3 min buffer)
**PRESENTER:** SALES AND MARKETING OFFICER

---

# 0. PRE-PRESENTATION CHECKLIST (15 MIN BEFORE)

DO THESE BEFORE THE CEO WALKS IN:

- [ ] **VERIFY VERCEL IS UP:** open https://econares-website.vercel.app in your browser. If it's down, use local: http://127.0.0.1:4323/
- [ ] **HARD-RELOAD THE BROWSER** (Ctrl+Shift+R) to clear cache and get latest version
- [ ] **OPEN IN INCOGNITO/PRIVATE WINDOW** to avoid any cached credentials
- [ ] **CLOSE OTHER TABS** so you don't accidentally show the wrong window
- [ ] **TURN OFF NOTIFICATIONS** (Slack, email, chat) so nothing pops up
- [ ] **HAVE A PHONE READY** as backup in case the projector fails
- [ ] **HAVE THE PRESENTATION DOCS OPEN** in another tab (presentation/01_WEBSITE_RATIONALE.md and 02_COMPENSATION_CASE.md)
- [ ] **TEST THE RFQ FORM** by filling it out with your own email — confirm it arrives in your inbox (Formspree free tier has a 50-submission/month limit, do NOT spam)
- [ ] **HAVE WATER** nearby, not just coffee

---

# 1. THE 15-MINUTE DEMO SCRIPT

## 1.1 OPENING (60 SECONDS)

**SAY:**

> "Good morning, [CEO name]. Thank you for the time. I've been working on a comprehensive digital presence for ECONARES over the past [N] months, and I want to walk you through what's live today, what it will do for the business, and — separately, toward the end — what I'd like to discuss about the work and a fair arrangement going forward.
>
> The site is live right now at econares-website.vercel.app. Let me show you."

**ACTION:** Type the URL in the address bar. Hit Enter. Wait 2 seconds for the page to load.

**WATCH FOR:** Page loads in under 2 seconds. If it takes longer, that's a network problem at the venue, not a code problem.

---

## 1.2 HOMEPAGE — 5 MINUTES (THE MOST IMPORTANT PART)

### MINUTE 1: HERO AND CREDENTIALS (45 SECONDS)

**SAY:**

> "This is the homepage. The headline reads 'Industrial Fuels, Minerals & Construction — From One Philippine Partner.' The word 'Construction' is in red — our brand color — to draw the eye.
>
> Below the hero, you can see the credentials strip: SEC-registered, DTI-registered 2015, DTI-registered 2019, PCAB-licensed, 15+ years in Philippine heavy industry.
>
> These are the legal and licensing facts a procurement officer looks for FIRST when pre-qualifying a supplier."

**ACTION:** Slowly scroll down to the credentials strip, then back up.

**IF ASKED "Why the rotating images?":**
> "Those are placeholder gradient backgrounds. The four labels — Coal Stockpile, Vessel Loading, Construction Site, Aggregates Yard — correspond to actual site photos from Republic Cement, Carrascal, Mandani Bay, and Century Peak. Real photography is on the post-launch roadmap. Right now the slots are reserving the design real estate."

### MINUTE 2: WHAT WE SUPPLY (45 SECONDS)

**SAY:**

> "Below that, three division cards map directly to our three legal entities:
> - Industrial Fuels → ECE Resources
> - Minerals → ECE Resources
> - Construction → ECE Construction Services
>
> A prospect can land on this page and immediately understand: 'This is one company that does all three things, and I only need to call one number.' That's the integrated supply-and-build model we keep talking about. It's now visible to a prospect before they ever pick up the phone."

**ACTION:** Hover over each card to show the hover effect (subtle border color change, shadow appears).

### MINUTE 3: FEATURED COMMODITIES (45 SECONDS)

**SAY:**

> "This is the new section — Featured commodities in stock. We have 20 commodities in active supply. I'm showing 8 here: 4 fuels, 4 minerals. Each tile is a real product link.
>
> When we do the photography shoot in [planned date], these tiles will show actual product photos. For now they're rendering the AI-generated product photos — which look professional but are placeholders, clearly labeled as such."

**ACTION:** Click on "STEAM COAL" tile.

**WAIT FOR PAGE LOAD.** 1-2 seconds.

### MINUTE 4: PRODUCT DETAIL PAGE (60 SECONDS)

**SAY (on the Steam Coal page):**

> "This is a single product page. Notice:
> 1. The breadcrumb — Home > Products > Industrial Fuels > Steam Coal
> 2. The spec table — NCV (Net Calorific Value), Moisture, Ash, Volatile Matter, Sulfur, Size — these are the actual values from our current contracts
> 3. Logistics — packaging, MOQ of 5,000 MT, lead time
> 4. Primary applications — cement kilns, sugar mills, biomass power
> 5. Quality assurance — pre-shipment analysis, sieve testing, COA
> 6. Related products at the bottom — the customer doesn't have to navigate back to find a related commodity"

**ACTION:** Scroll down through each section. Point at the spec table. Point at the related products.

**IF ASKED "How do we update the specs?":**
> "It's a single YAML file. I edit one value, rebuild, deploy. About 3 minutes end-to-end. That's the data-driven architecture."

### MINUTE 5: BACK TO HOMEPAGE → CONTACT (45 SECONDS)

**SAY:**

> "Let me jump to the most important page for business: Contact."

**ACTION:** Click CONTACT in top nav.

> "Two RFQ forms — one for products, one for services. Look at the commodity dropdown — every single one of our 20 commodities is listed, in two groups: Industrial Fuels and Minerals. The customer picks what they want, fills in their tonnage, delivery location, and message, and submits.
>
> Below the form, four sales officer cards — Minerals, Fuels, Construction, Marine. Each one has a direct email link. A procurement officer can find the right person in 10 seconds."

**ACTION:** Click on the SERVICE tab to show the tab switcher works.

> "Notice the tab switching — same data-driven pattern, the service type dropdown has all 21 sub-services grouped by category. Procurement officers don't have to navigate to a different page to send a service RFQ."

**IF ASKED "Where do RFQs go?":**
> "They go to our Formspree endpoint, which forwards to a configurable email address. Right now it's wired to send to the sales team. After the CEO signs off, I can wire it to a `sales@econares.com` address once we have Google Workspace set up. That's in the post-launch roadmap."

---

## 1.3 PRODUCTS CATALOG (2 MINUTES)

**ACTION:** Click PRODUCTS in nav. Page loads.

**SAY:**

> "Full catalog. 4 industrial fuels at the top, 16 minerals below. All 20 clickable."

**ACTION:** Click on "Nickel Ore" card.

**SAY:**

> "Same page template, different data. Each product has its own spec sheet, logistics, applications, QA, and related products. The CEO can verify: 'Yes, this is a real supplier with 20 commodities, technical specs, and quality assurance process.' That alone pre-qualifies ECONARES for major cement, sugar, and power procurement."

**ACTION:** Click back, then click on Marine Sand.

> "Marine sand — used for ready-mix concrete and reclamation. ASTM C33 compliance mentioned in the description. That's the kind of detail a procurement officer looks for."

---

## 1.4 PROJECTS (2 MINUTES)

**ACTION:** Click PROJECTS in nav. Page loads.

**SAY:**

> "14 reference projects. Six of them are the 'hero' projects — Republic Cement, Century Peak, Carrascal Nickel, TBC Port, ALS Deep Well, Mandani Bay. These are the names a prospect would recognize.
>
> Republic Cement — coal shipments, ongoing. That's an active account.
> Carrascal Nickel — shipside loading at Surigao del Sur. That's the integrated supply-and-build model in action: we ship the fuel AND load the ore.
> TBC Port — marine/port project, recent. That's our construction arm.
> Mandani Bay — mixed-use real estate, recent. That's another construction arm project."

**ACTION:** Click on Republic Cement project card.

**SAY:**

> "Each project has its own page. Client, scope, year, status, location. This is the kind of social proof that closes deals."

---

## 1.5 CAPABILITIES (2 MINUTES)

**ACTION:** Click CAPABILITIES in nav. Page loads.

**SAY:**

> "This is the long-form capabilities statement. Notice the design is completely different — this is the 'concept B' editorial style I designed. Parchment canvas, serif typography, manifesto + numbered chapters.
>
> Why two designs? Because procurement officers and the CEO evaluate ECONARES differently:
> - The homepage is for first-time visitors who need to understand what we do in 8 seconds
> - The capabilities page is for serious prospects who want to read the full statement
>
> This is the same company, two facets."

**ACTION:** Scroll slowly through the chapters. Point at the 4 numbered chapters (Industrial Fuels, Minerals, Construction & Engineering, Reference Projects).

**IF ASKED "How long did this take to build?":**
> "About 1-3 months of evenings and weekends. I'll discuss that specifically when we get to the compensation case later in the presentation."

---

## 1.6 THE RFQ FORM (LIVE TEST) (1 MINUTE)

**ACTION:** Click CONTACT in nav. Page loads. Click "RFQ — SERVICE" tab.

**SAY:**

> "Let me do a live test of the form. I'm going to fill this out as if I were a procurement officer at a sugar mill looking for a Marine Sand supplier."

**ACTION:** Quick fill (use dummy data):
- Name: "Juan Dela Cruz"
- Company: "Victorias Milling Company"
- Email: YOUR OWN EMAIL
- Phone: "+63 917 555 1234"
- Service type: "Marine Sand Supply" (or similar)
- Project location: "Victorias, Negros Occidental"
- Estimated value: "₱15,000,000"
- Message: "Looking for 50,000 MT of marine sand for Q1 2027 expansion. ASTM C33 compliance required."

**ACTION:** Click "Send Service RFQ" button.

> "And it submits. The RFQ arrives in the inbox I configured. Let me check my email..."

**ACTION:** Open your email, show the RFQ email (if it's arrived by now — may take 30 seconds).

> "Real lead capture. The CEO can verify: this is a working business tool, not a brochure site."

---

## 1.7 CLOSING THE DEMO (30 SECONDS)

**SAY:**

> "That's the live site. 68 pages, 20 commodities, 24 services, 14 projects, all live. Mobile-responsive, fast, accessible. Ready to rank on Google once we submit to Search Console.
>
> Let me move to the second part of the presentation: the work behind the build, and a fair arrangement going forward."

**ACTION:** Switch to the slides (presentation/03_SLIDES.md) or the rationale doc.

---

# 2. ANTICIPATED CEO QUESTIONS + ANSWERS

THESE ARE THE 10 QUESTIONS THE CEO IS MOST LIKELY TO ASK, IN ORDER OF PROBABILITY. KNOW THE ANSWERS.

## Q1: "WHO BUILT THIS?"

> "I did, over the past 1-3 months, in my personal time outside working hours. I used Astro 4.16, Tailwind CSS, Formspree, Vercel, GitHub, and a MiniMax AI image generation API for the 20 product photos."

## Q2: "HOW MUCH DID THIS COST?"

> "Market rate for an external agency would be ₱420,000 to ₱680,000. A freelance contractor would be ₱309,000 to ₱465,000. I am proposing a one-time bonus of ₱60,000 to ₱90,000 plus an ₱8,000/month maintenance retainer. That's roughly 15-20% of the agency-equivalent value, and less than half of what a freelancer would charge."

## Q3: "CAN YOU SHOW ME THE GITHUB REPO?"

> "Yes — github.com/reyzheconares-cyber/econares-website. It's private. I can give you access right now, or add you as a collaborator after this meeting."

## Q4: "WHAT HAPPENS IF YOU LEAVE THE COMPANY?"

> "Right now, the site becomes a single-point-of-failure risk. I am the only one who knows how it's built, how to deploy it, how to update the data files, and how the Formspree form is wired. The proposed ₱8,000/month maintenance retainer ensures I'm available long-term. If I do leave, I will document everything and hand off to whoever takes over, and the data files are simple enough that any web developer can maintain them."

## Q5: "WHY IS THE EMAIL STILL YAHOO?"

> "Great question, and one of the things I want to fix in the post-launch roadmap. The Yahoo email is unprofessional for B2B procurement. I propose we set up Google Workspace — about ₱250/month — and migrate to `sales@econares.com` and `rfq@econares.com`. That's a 2-3 day task. The site is already coded to make the email change a one-line config update."

## Q6: "WHEN CAN WE GO LIVE ON ECONARES.COM?"

> "The site is ready for the production domain. The full migration takes about 1 week:
> 1. Register the domain or use existing (Namecheap, Cloudflare)
> 2. Set up DNS (Cloudflare + Namecheap guide ready)
> 3. Deploy to Cloudflare Pages (1 day)
> 4. Test the live site (1 day)
> 5. Submit to Google Search Console + Google Business Profile (1 day)
>
> I have the deployment guide ready. The demo URL you just saw is the same code that will go to econares.com."

## Q7: "WHAT'S THE NEXT STEP?"

> "Three things in priority order:
> 1. **Photography shoot** at the Cebu yard — 1-2 days, gives us real product photos and project photos
> 2. **Three launch articles** for the Insights section — I draft, you review, we publish
> 3. **Domain migration** to econares.com with Google Workspace
>
> All three can run in parallel over the next 2-4 weeks."

## Q8: "CAN THE COMPETITORS SEE THIS?"

> "Yes, anyone can see it. The site is public. That's the point — it's a marketing tool. The data shown (commodity specs, project references, capabilities) is already public information or information we want competitors to know about. The competitive advantage is execution — our relationships with Republic Cement, our access to marine sand sources, our shipside loading capability at Carrascal. The website gets us found; the relationships close deals."

## Q9: "WHAT IF WE NEED TO UPDATE SOMETHING URGENTLY?"

> "Right now, you call me. With the proposed maintenance retainer, you have a guaranteed 4 hours/month of my time for changes. Anything urgent is prioritized. The site is data-driven — most updates are 5-minute YAML edits."

## Q10: "CAN I GET INVOLVED IN UPDATING THE CONTENT?"

> "Yes, two options:
> 1. **Direct YAML editing** — I can teach you or any staff member to edit the data files directly. It's structured like a spreadsheet.
> 2. **Decap CMS** — I can set up a web-based admin panel where you log in, edit a form, click save, and the site updates. Takes about 2 hours to set up. Recommended once we're past launch."

---

# 3. THE TRANSITION TO COMPENSATION

AFTER THE DEMO + Q&A, TRANSITION TO SLIDES 11-18 (THE COMPENSATION CASE).

USE THIS TRANSITION:

> "I'd like to shift to the second part of the conversation: the work that went into this build, and a fair arrangement going forward. I'll keep this short — five minutes — and then I'd like to hear your thoughts."

**ACTION:** Open presentation/02_COMPENSATION_CASE.md or presentation/03_SLIDES.md (slides 11-18).

**THEN WALK THROUGH:**
1. Slide 12: What was delivered (15 items, all complete)
2. Slide 13: Effort invested (~80-110 hours, evenings, weekends)
3. Slide 14: Market-rate cost analysis (₱420K-₱680K agency, ₱309K-₱465K contractor)
4. Slide 15: What I am asking (₱60K-₱90K + ₱8K/month)
5. Slide 16: Why this is fair (35% of market value)
6. Slide 17: Risks if not agreed
7. Slide 18: Recommended path forward

**KEY TALKING POINTS:**
- "I am NOT asking for the full market rate."
- "I am asking for 15-20% of what an agency would charge."
- "The maintenance retainer is HALF of what a freelancer would charge."
- "This is sustainable for me, fair to the company, and protects us from bus factor."

---

# 4. HANDLING TENSION (IF THE CEO PUSHES BACK)

THE CEO MAY:
- QUESTION THE AMOUNTS
- WANT TO NEGOTIATE LOWER
- WANT TO DELAY THE DECISION
- WANT TO BRING IN AN OUTSIDE VENDOR

**DO NOT ARGUE.** PRESENT FACTS AND DEFER.

## IF ASKED "CAN WE DO THIS FOR LESS?":

> "I'm open to discussion. The numbers I proposed are based on a 35% discount to the market rate, plus half the freelancer rate for ongoing maintenance. If you have a different number in mind, I'd like to hear it. I would prefer to reach a fair agreement than to delay the decision."

## IF ASKED "CAN WE DELAY THIS DECISION?":

> "We can, but I'd note that the longer the website runs without a maintenance agreement, the more it will fall behind. Updates won't happen, security patches will lapse, and the site will gradually feel abandoned. The proposed ₱8,000/month retainer is the minimum needed to keep the site healthy."

## IF ASKED "CAN WE HIRE AN EXTERNAL VENDOR INSTEAD?":

> "We can, and the deployment guides are ready. The market rate for a freelancer would be ₱8,000-₱15,000/month for maintenance, or ₱2,000-₱4,000/hour for changes. The proposed retainer is at the lower end of that range. The advantage of using me is institutional knowledge — I know the codebase, the data files, and the business context. The disadvantage of using me is bus factor. Both are real; I'll let you decide."

## IF THE CEO SAYS NOTHING:

> "I'd like to give you time to think about this. I'll send you the rationale document and the compensation case after the meeting. If you'd like to discuss further, my contact information is in the documents. Thank you for the time today."

---

# 5. TIMING CHECKLIST (USE A WATCH)

| SEGMENT | TARGET | MAX |
|---|---|---|
| OPENING | 1 MIN | 1.5 MIN |
| HOMEPAGE (HERO + CREDENTIALS + DIVISIONS) | 2 MIN | 3 MIN |
| PRODUCT DETAIL (STEAM COAL) | 1.5 MIN | 2 MIN |
| CONTACT (RFQ FORM TEST) | 1.5 MIN | 2 MIN |
| PRODUCTS CATALOG | 1.5 MIN | 2 MIN |
| PROJECTS | 1.5 MIN | 2 MIN |
| CAPABILITIES | 1.5 MIN | 2 MIN |
| CLOSING THE DEMO | 0.5 MIN | 1 MIN |
| Q&A (CEO QUESTIONS) | 3 MIN | 5 MIN |
| TRANSITION + COMPENSATION | 5 MIN | 7 MIN |
| **TOTAL** | **15 MIN** | **20 MIN** |

**IF YOU'RE RUNNING OVER 15 MIN:**
- SKIP THE CAPABILITIES WALKTHROUGH (just point to the link, say "long-form statement, also live")
- SKIP THE PROJECTS DETAIL PAGE (just show the index, don't click in)
- SHORTEN Q&A TO 2 MIN

**IF YOU HAVE LESS THAN 15 MIN TOTAL:**
- DO HOMEPAGE → PRODUCT DETAIL → CONTACT (5 MIN)
- SKIP EVERYTHING ELSE
- JUMP STRAIGHT TO SLIDES

---

# 6. CLOSING THE MEETING

WHEN YOU WRAP UP, SAY:

> "Thank you for the time. The site is live at econares-website.vercel.app, ready for review. I have the rationale document and the compensation case ready to share. I'll send them to you after this meeting for review. I'd appreciate your feedback within the week so we can move forward.
>
> Any final questions?"

---

# 7. POST-MEETING CHECKLIST (DO THIS IMMEDIATELY AFTER)

- [ ] **SHARE THE 3 DOCS** with the CEO (email or chat) — presentation/01_WEBSITE_RATIONALE.md, 02_COMPENSATION_CASE.md, 03_SLIDES.md
- [ ] **SEND THE VERCEL URL** in the same message
- [ ] **NOTE ANY QUESTIONS** the CEO asked that you didn't have an answer for — research and respond within 48 hours
- [ ] **SAVE THIS SCRIPT** to your notes for future presentations
- [ ] **DEFER** sending anything until you have a clear go-ahead from the CEO
- [ ] **FOLLOW UP** with a 1-line message 3 business days later: "Hi [CEO name], checking in on the website presentation. Let me know if you have any questions or want to discuss next steps."

---

# 8. TROUBLESHOOTING (IF SOMETHING GOES WRONG DURING DEMO)

## IF VERCEL GOES DOWN

> "The demo URL is down — let me switch to the local mirror I have on my laptop."

**ACTION:** Switch to http://127.0.0.1:4323/ (you should have a local server running as backup).

## IF A PAGE LOADS SLOWLY

> "Network's a bit slow here. The site itself loads in under 2 seconds on a fast connection, so this is venue-specific. Let me reload."

**ACTION:** Refresh the page (F5).

## IF THE CEO ASKS SOMETHING YOU DON'T KNOW

> "That's a good question. I want to give you a precise answer rather than guess, so let me research it and get back to you by [date]."

**DO NOT MAKE UP ANSWERS.** Confidence is built by admitting what you don't know and following up reliably.

## IF THE CEO WANTS TO SKIP AHEAD

> "Sure, let me jump to [topic]."

**ACTION:** Navigate directly. Don't force a linear walkthrough.

## IF THE CEO IS IMPRESSED

> "Thank you. The next step I'd suggest is the photography shoot at the Cebu yard — that's where the site goes from 'professional' to 'unbeatable.' Real site photos are the highest-impact upgrade we can make in the next 30 days."

## IF THE CEO IS SKEPTICAL

> "I understand. I'd like to give you time to review the rationale document and the compensation case. If you'd like to walk through it again or have a longer conversation, I'm available. The site is live now — you can review it on your own time before we make any decisions."

---

# 9. FILES TO BRING TO THE MEETING

- [ ] **THIS PRACTICE SCRIPT** (printed or on a second screen)
- [ ] **LAPTOP WITH LIVE DEMO LOADED** in browser tab
- [ ] **3 PRESENTATION DOCS** in another tab (presentation/01, 02, 03)
- [ ] **PHONE AS BACKUP** (with the Vercel URL bookmarked)
- [ ] **WATER**
- [ ] **NOTEBOOK + PEN** for handwritten notes during Q&A

---

**PREPARED BY:** SALES AND MARKETING OFFICER
**DATE:** 2026-07-07
**VERSION:** 1.0 (READY FOR REHEARSAL)
**STATUS:** DRAFT, NOT SENT (PER MEMORY RULE)
