# ECONARES Commodity Cold Call Ebook - build script
# Generates 75 cold call hooks (HTML + PDF) modeled on AIPBI 75 B2B Cold Call Hooks
# All 8 categories. Each hook has 8 components: opening, why, when, research,
# response A, response B, follow-up, call flow, customize note.

import json
import html as html_lib
from datetime import datetime

CATEGORIES = [
    {"id":1,"title":"Competitor / Supplier Reference Hooks",
     "subtitle":"Reference what they currently source \u2014 without naming your product",
     "intro":"Buyers in commodity trading are loyal to their incumbent supply chain \u2014 but quietly frustrated by it. These hooks let you name the pain without naming your product. You sound like someone who understands their supply book, not a salesperson trying to displace it."},
    {"id":2,"title":"Plant / Asset Observation Hooks",
     "subtitle":"Anchor the call in something physical you noticed about their facility",
     "intro":"A commodity buyer respects anyone who can name a kiln, a smelter, a CFBC boiler, or a stockpile pad. These hooks show you have done the homework on their physical asset. The first ten seconds of trust in commodity sales are won by demonstrating you know what they actually do, not what their website says they do."},
    {"id":3,"title":"Recent News / Change Hooks",
     "subtitle":"Use public news, M&A, and leadership moves as the reason for the call",
     "intro":"Commodity markets respond to events: new projects commissioned, ownership changes, plant heads appointed, ESG announcements, contract wins. A buyer cannot ignore a hook tied to something in their inbox from last week. The risk: news goes stale fast \u2014 always date-check the article before dialing."},
    {"id":4,"title":"Industry / Commodity Challenge Hooks",
     "subtitle":"Lead with the market condition they are living through right now",
     "intro":"Most powerful when the market is in motion. Tight supply, freight spikes, port congestion, export bans \u2014 buyers are dealing with these daily. By naming the pain first, you position as someone with situational awareness, not a cold caller. Be ready to talk specifics, because the buyer will test you."},
    {"id":5,"title":"Mutual Connection / Trade Group Hooks",
     "subtitle":"Use a real or sector-credible bridge to earn the first 30 seconds",
     "intro":"A warm introduction is the gold standard in commodity trading \u2014 but most cold calls do not have one. These hooks simulate that effect by referencing trade groups, conferences, sister plants, and industry consultants. Only use a name the buyer can verify. A fake reference destroys credibility faster than any other mistake."},
    {"id":6,"title":"Spec / Logistics Problem Hooks",
     "subtitle":"Surface the operational issue their current supplier cannot solve",
     "intro":"Commodity buyers live and die by spec sheets, port logistics, and quality consistency. These hooks name real, recurring problems \u2014 moisture creep, sulfur penalties, demurrage, container shortage. You are not pitching product. You are asking a question that implies you have seen the problem before and may have a fix."},
    {"id":7,"title":"Timing / Seasonal / Shipping Hooks",
     "subtitle":"Anchor the call in a date on the buyer's calendar, not yours",
     "intro":"Commodity trading is seasonal. Monsoon stockpile builds, maintenance shutdowns, Lunar New Year vessel windows, Chinese winter heating demand \u2014 the calendar is a cheat code. These hooks let you call at the exact moment the buyer is internally planning tonnage. You are not cold-calling; you are showing up on the day they would have called a supplier if they had one in mind."},
    {"id":8,"title":"Direct Question Hooks",
     "subtitle":"Open with a spec-led question \u2014 no pitch, no product mention",
     "intro":"The boldest hooks in this book. No reference, no observation, no event. Just a question. A confident, specific question signals expertise and forces the buyer to engage before they have a chance to dismiss you. Highest-risk and highest-reward openings. Use them when you have a strong contact and a sharp spec hunch."},
]

# Hooks list. Each: (cat, title, commodities_str, opening, why, when, research_list, a, b, follow, flow, customize)
HOOKS = []

def H(cat, title, comm, opening, why, when, research, a, b, follow, flow, customize):
    """Compact hook constructor."""
    return {
        "cat": cat, "title": title, "comm": comm, "opening": opening,
        "why": why, "when": when, "research": research,
        "a": a, "b": b, "follow": follow, "flow": flow, "customize": customize,
    }

# ============ CATEGORY 1: COMPETITOR/SUPPLIER REFERENCE (7) ============
HOOKS.append(H(1, "The Origin Swap", "Nickel ore; Coal; Copper concentrate",
"Hi {name}, this is {rep} from ECONARES in Cebu. I have been watching how {company} sources its {commodity} for the {line} line \u2014 most of your tonnage still comes out of {origin}, right? Just curious whether you have stress-tested that against a {alt_origin} option in the last twelve months.",
"You name their incumbent supply chain. The buyer instantly registers you understand their world, not a salesperson trying to break in.",
"Buyer is known to source from a specific region or named supplier. Customs data or trade press confirms the pattern.",
["Panjiva / ImportGenius customs data for the buyer's shipments","Company website, annual report, or sustainability filing for sourcing language","LinkedIn for any procurement manager who joined from a competitor"],
"'Yeah, we are running a tight book with {supplier}. Why?'",
"'Actually, consistency has been an issue. We have been looking.'",
"Totally fair. Most of the operators we work with say the same thing about {supplier} on the consistency side. I am not here to pitch \u2014 I would just like to understand what your spec tolerance looks like so I know whether it is even worth a conversation.",
"1. {rep}: {opening}\n2. Buyer: confirms or corrects origin\n3. {rep}: 'What would need to change for you to add a second source?'\n4. Buyer: 'Price' / 'Consistency' / 'Nothing right now'\n5. {rep}: 'Understood. Send me your typical spec sheet and I will tell you straight whether we fit. Twenty minutes, no pitch.'\n6. Confirm email, close warm.",
"Replace {origin} with the actual sourcing region the buyer uses today. {alt_origin} should be a credible alternative (PH origin, Indonesia, South Africa, etc.)."))

HOOKS.append(H(1, "The New-Entrant Probe", "All",
"Hi {name}, {rep} from ECONARES, calling from Cebu. Quick one \u2014 I noticed {company} added a second supplier to the {commodity} book sometime in the last quarter. Was that a one-off trial or are you running dual-sourcing as a permanent policy?",
"Asking a yes/no question about a recent sourcing change forces the buyer to either confirm dual-sourcing is now policy (a buying signal) or correct you (a chance to ask why you are calling).",
"Customs data shows a new shipper appearing in the buyer's import log that was not there 6 months ago.",
["Panjiva / ImportGenius for the buyer's supplier history","Annual report language on 'supply diversification'","LinkedIn announcement of new sourcing contract"],
"'Yeah, we trialed a second source for {period}. Standard play.'",
"'Where did you get that from? We are not supposed to disclose that.'",
"Fair question \u2014 I will respect the confidentiality. The reason I ask: if you are running dual-sourcing, I would love to be on the shortlist for the next trial. Can I send a one-page spec summary?",
"1. {rep}: {opening}\n2. Buyer: confirms or deflects\n3. {rep}: 'Understood. If a second-source opportunity opens up, would you take a one-page spec summary?'\n4. Buyer: 'Yes, send it.' / 'Not interested.'\n5. {rep}: 'Will do. And what is the cleanest email \u2014 {email}?'\n6. Log to CRM, follow up next Tuesday.",
"Pre-verify the customs data point before dialing. Do not invent a shipper name \u2014 buyers check."))

HOOKS.append(H(1, "The Niche Spec They Cannot Get", "Nickel ore; Coal; PKS; Woodchips",
"Hi {name}, {rep} from ECONARES. Most of the {commodity} buyers we talk to in {region} say the same thing \u2014 they can get the headline spec from their incumbent, but the niche grade {spec_band} is almost impossible to source on a regular lift. Is that an issue for {company}?",
"You name a real, recurring pain \u2014 a narrow grade band that incumbents treat as a side order, not a core SKU. The buyer either confirms it (high intent) or explains how they solve it (warm intel).",
"You know a specific grade band that is underserved in that buyer's region. Common examples: 1.5\u20131.8% Ni limonite, GAR 5000\u20135400 coal, low-moisture PKS.",
["Trade press for the buyer's typical grade range","Your own supply book \u2014 confirm you can actually deliver the niche band","LinkedIn for the procurement manager's prior roles"],
"'Yes, that is exactly our problem right now.'",
"'We blend for that. Not a real issue.'",
"Got it. If we can run a consistent {spec_band} parcel on FOB basis, would {company} be open to a one-vessel trial?",
"1. {rep}: {opening}\n2. Buyer: confirms or downplays\n3. {rep}: 'Last year, a {region} plant in your position ran a {volume} MT trial with us on that exact spec. They are now a regular. Mind if I share the trial framework?'\n4. Buyer: 'Send it.'\n5. {rep}: 'Emailing it today. Should I loop in {colleague} as well?'\n6. Confirm both emails, schedule follow-up.",
"Replace {spec_band} with a real, narrow grade range. Use a real trial story if you have one \u2014 never invent."))

HOOKS.append(H(1, "The Quality-Complaint Echo", "All",
"Hi {name}, {rep} from ECONARES. I read the {company} procurement bulletin \u2014 they raised a flag on {supplier}'s last shipment to the {plant} plant. Without naming names, is {commodity} consistency still the number-one complaint from your operations team?",
"You surface a known internal pain (a published complaint) and frame it as a question. The buyer is now talking about their problem, not your product.",
"Buyer has published quality concerns via tender documents, sustainability reports, or trade press interviews.",
["Buyer's tender documents and RFQs (often published on company site)","Recent trade press interviews with plant managers","LinkedIn posts from the buyer's operations team"],
"'You saw that. Yeah, consistency is the issue.'",
"'Different problem. We are fine on quality. Logistics is the issue.'",
"Appreciate the honesty. If I send you a one-page note on how we run pre-shipment inspection and lab certification per lot, would that be useful \u2014 even if you do not move off {supplier} today?",
"1. {rep}: {opening}\n2. Buyer: opens up\n3. {rep}: 'Mind if I ask what spec band is hardest to keep tight?'\n4. Buyer: shares detail\n5. {rep}: 'Send me a recent failed-lot report and I will tell you if we can hit it. No charge for the assessment.'\n6. Email follow-up same day.",
"Never invent a complaint. If you cannot cite a real, citable source, swap to a softer variant: 'In your tender documents, you emphasized {spec} tolerance \u2014 is that still the priority?'"))

HOOKS.append(H(1, "The Logistics Bottleneck Of The Incumbent", "Coal; Nickel ore; Diesel",
"Hi {name}, {rep} from ECONARES. I work with a few {commodity} buyers in {region} and the same logistics pain keeps coming up \u2014 {incumbent}'s tonnage out of {port} has been late on {n} of the last {m} shipments this year. Is that what {company} is seeing as well?",
"Logistics reliability is the silent deal-killer. Buyers will not switch on price, but they will switch when their incumbent misses three vessels. Naming the pain establishes you have seen the pattern, not the marketing brochure.",
"Trade press, Lloyd's List, or freight forums confirm port congestion, scheduling delays, or shipping line issues at the incumbent's load port.",
["Lloyd's List Intelligence or freight forums for port delays","Trade press for the buyer's typical discharge port","Vessel tracking sites (MarineTraffic) for the incumbent's fleet"],
"'Yes. It has been a nightmare.'",
"'No, we have not seen that.'",
"Got it. Worth knowing anyway. If a parallel FOB option out of {alt_port} could shave {days} days off your typical transit, would {company} entertain a quote on a single trial vessel?",
"1. {rep}: {opening}\n2. Buyer: confirms or denies\n3. {rep}: 'What discharge window are you working toward right now?'\n4. Buyer: gives a date\n5. {rep}: 'We can move a {volume} MT parcel out of {alt_port} and hit that window. Want me to send the indicative schedule?'\n6. Follow up same day with the schedule, not a price.",
"Use a real freight intelligence data point. If the data is two quarters old, swap to a less time-bound version: 'Historically, tonnage out of {port} runs hot in {month} \u2014 is {company} covered?'"))

HOOKS.append(H(1, "The Acquired-Supplier Pivot", "All",
"Hi {name}, {rep} from ECONARES. I saw the news on {supplier} being acquired by {acquirer}. In these situations the procurement book usually gets shaken up in the first {n} months. Has {company} been told to revisit its {commodity} supplier shortlist yet?",
"M&A in commodity supply chains is a once-a-decade opening. New owners typically re-evaluate everything in 6\u201312 months. By being the first to call, you position as a known option before the formal review.",
"An actual M&A announcement has been made public within the last 6\u201312 months involving a supplier in the buyer's supply book.",
["Reuters / Bloomberg / FT / S&P Global for the M&A announcement","Buyer's annual report for language on supplier diversification","LinkedIn for any hiring announcements in the buyer's procurement team post-deal"],
"'Actually yes, we have been told to widen the field.'",
"'No, we are continuing with them. Nothing has changed.'",
"Understood. If the review does open up, ECONARES can deliver FOB {origin} with a pre-shipment lab cert per lot. May I send a one-pager just to be on file?",
"1. {rep}: {opening}\n2. Buyer: confirms or denies\n3. {rep}: 'When is the review window likely to open?'\n4. Buyer: gives timeline\n5. {rep}: 'I will time a one-pager to land in {colleague}'s inbox that week. Anything else I should include?'\n6. Calendar reminder set in CRM.",
"If the buyer is large, find the actual press release and quote the date. Buyers remember the callers who read the announcement, not the ones who guessed."))

HOOKS.append(H(1, "The Failed-Shipment Outreach", "Nickel ore; Coal; PKS; Copper concentrate",
"Hi {name}, {rep} from ECONARES. I heard through the {port} grapevine that a {commodity} parcel out of {incumbent_origin} failed inspection at {discharge_port} earlier this quarter. Was that one of {company}'s shipments, or am I crossing wires?",
"Quality failures are public, even when the parties involved are not. By asking 'was that yours', you invite the buyer to either confirm (problem is real, you are relevant) or correct you (you learn their actual supplier, useful intel).",
"Trade press, port authority reports, or buyer-side operational posts reference a quality incident at a known discharge port.",
["Port authority quality reports (often published monthly)","Trade press for the discharge port's quality incidents","LinkedIn posts from the buyer's QC team"],
"'That was not us, but I know exactly which parcel you mean.'",
"'Yes, that was painful. We are still reconciling with the supplier.'",
"Apologies for stirring that up. If ECONARES is ever asked to step in on a replacement parcel \u2014 same grade, FOB basis, lab cert per lot \u2014 would {company} want a quote?",
"1. {rep}: {opening}\n2. Buyer: confirms or corrects\n3. {rep}: 'Worth flagging. If a backup option helps, I can have a quote ready in {hours} hours.'\n4. Buyer: 'Send indicative numbers.'\n5. {rep}: 'Will do. I will use {benchmark} as the floor and {adjustment} above. Spec-confirmed before firm offer.'\n6. Email follow-up with indicative range, not firm price.",
"Only use this hook when you have a citable source. Never invent quality incidents \u2014 it destroys trust in commodity circles within one phone call."))

# ============ CATEGORY 2: PLANT/ASSET OBSERVATION (10) ============
HOOKS.append(H(2, "The Capacity Upgrade", "Coal; Nickel ore; Woodchips",
"Hi {name}, {rep} from ECONARES. I saw the {plant} capacity expansion announcement \u2014 moving from {old_cap} to {new_cap} MT/year. Congrats on the milestone. Have you finalized the additional {commodity} sourcing yet, or is that still in planning?",
"Capacity expansions trigger new sourcing. You are calling at the exact moment the buyer's internal demand curve just bent upward. Most competitors call after the contract is signed.",
"Press release, environmental impact assessment, or government filing announces an expansion at the buyer's plant.",
["Company press releases, SEC/HKEX/PSE filings","EIA or Department of Energy filings (power plants)","Local newspaper for the plant's community"],
"'We have it under control, thanks.'",
"'Actually, the additional volume is still open. Why?'",
"No reason beyond making sure ECONARES is on the shortlist. Can I send a one-page summary of our FOB {commodity} offer so you have it on file for the tender?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'When is the tender window?'\n4. Buyer: gives a date\n5. {rep}: 'I will time the spec submission to land one week before. Anything you need from us pre-tender?'\n6. Log to CRM, set follow-up reminder.",
"Use the actual expansion figures from the press release. Generic language ('we are expanding') sounds unprepared."))

HOOKS.append(H(2, "The New Line Commissioning", "Nickel ore; Coal; PKS",
"Hi {name}, {rep} from ECONARES. I read that {company} commissioned the new {line_name} at {plant} last month. New lines usually have a different {commodity} spec profile than the existing fleet \u2014 what grade are you running on the new line, just out of curiosity?",
"New lines are the highest-intent moment to call. The buyer is in spec-definition mode. By asking a curiosity question, you get a spec sheet for free without sending your own.",
"A new line, kiln, boiler, or furnace has been commissioned within the last 30\u201360 days.",
["Press release on the commissioning date","Equipment supplier announcements (often the OEM publishes)","LinkedIn for the commissioning engineer or plant head"],
"'Different grade from the older line. I will send the spec.'",
"'We are still fine-tuning the recipe. Send me your range.'",
"Appreciate that. Once the recipe is set, mind if I send a one-paragraph note on what ECONARES can deliver against that band?",
"1. {rep}: {opening}\n2. Buyer: shares spec or defers\n3. {rep}: 'When does the line hit nameplate throughput?'\n4. Buyer: gives a date\n5. {rep}: 'I will line up a {volume} MT indicative offer for that window. Same FOB basis you run today?'\n6. Confirm incoterms, set calendar reminder.",
"If you can name the OEM of the new line (e.g., 'the new FFE Minerals kiln'), the buyer's confidence in you jumps 10x. OEM names are almost always in the press release."))

HOOKS.append(H(2, "The Maintenance Shutdown", "Coal; PKS; Woodchips; Diesel",
"Hi {name}, {rep} from ECONARES. I noticed the {plant} scheduled a {n}-day maintenance shutdown starting {date}. After a shutdown, {commodity} inventory is usually tight for the first {weeks} weeks. Has {company} lined up the post-shutdown replenishment yet?",
"Post-shutdown inventory drawdowns are real. The buyer knows it, their CFO knows it, and they are quietly nervous about it. By naming the timing, you show operational literacy, not a sales pitch.",
"Power plant, cement, or smelter has filed or published a maintenance outage schedule.",
["Plant outage reports (PSALM, ERC, MGB filings)","OEM service bulletins for the plant's equipment","Trade press for the regional maintenance calendar"],
"'Yes, we are covered. Thanks.'",
"'We are still working on it. What is the question?'",
"The question is whether ECONARES should be on the post-shutdown shortlist. If a single FOB parcel can land within {weeks} weeks of restart, would that be useful?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What vessel size suits the post-shutdown window?'\n4. Buyer: shares size\n5. {rep}: 'We can size the parcel to match. Send me the post-shutdown target date and I will come back with a freight-aligned window.'\n6. Email follow-up with proposed window.",
"Use the actual published shutdown date. If the date has slipped, do not call \u2014 buyers are hypersensitive to stale intel."))

HOOKS.append(H(2, "The Plant Restart", "Coal; Nickel ore; Diesel",
"Hi {name}, {rep} from ECONARES. Saw that {plant} restarted the {unit} on {date} after the unplanned outage. Welcome back online. How is the {commodity} inventory holding up at restart \u2014 tight, normal, or comfortable?",
"Restarts after unplanned outages are when buyers are most exposed. A short, sympathetic opener reads as helpful, not pushy.",
"An unplanned outage has been resolved and the plant has restarted within the last 7\u201314 days.",
["Plant status reports (ERC for power, MGB for mining)","Trade press for the outage root cause","LinkedIn posts from plant management"],
"'We are tight. Looking for a fast parcel.'",
"'Recovering. We have two more weeks of cover.'",
"Got it. If we can dispatch a fast-track parcel on a {vessel_size} basis, would {company} be open to a one-vessel trial?",
"1. {rep}: {opening}\n2. Buyer: inventory status\n3. {rep}: 'What discharge window are you targeting?'\n4. Buyer: gives a date\n5. {rep}: 'Send me the spec and I will tell you straight whether we can hit it. Honest answer only.'\n6. Same-day follow-up email.",
"Avoid the temptation to pile on the outage ('What happened?'). Lead with welcome-back, not interrogation."))

HOOKS.append(H(2, "The Closure Notice", "All",
"Hi {name}, {rep} from ECONARES. I read the closure notice on {plant} in {year}. Before the wind-down, are there any final {commodity} parcels the operations team still needs to clear inventory? ECONARES does a lot of close-out lifts.",
"Closure-phase procurement is invisible to most suppliers. A buyer with a closing plant still has 3\u201312 months of operations to manage, and they are often more flexible on spec and price because the corporate tail is short.",
"Plant has announced closure but is still operating during the wind-down period (typically 6\u201324 months).",
["Closure announcements, environmental remediation filings","Worker union announcements (NLRB, DOLE in PH)","Local government for tax / closure permits"],
"'We are winding down but still running. Possibly.'",
"'No, we are done. Stop calling.'",
"Understood. If anything changes in the next quarter, ECONARES can clear a close-out parcel on short notice. Email on file is {email}?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the last operating month?'\n4. Buyer: gives date\n5. {rep}: 'I will check in again in {month}. Anything specific I should track?'\n6. Calendar reminder set.",
"Be respectful. Plant closures are personal for the people still working there. Avoid language that sounds opportunistic."))

HOOKS.append(H(2, "The New Stockyard / Warehouse", "Coal; Nickel ore; PKS; Woodchips",
"Hi {name}, {rep} from ECONARES. I saw the new {storage_type} at {plant} was commissioned. That usually means a step-up in stockpile capacity \u2014 maybe 30 to 50 percent. What is the new {commodity} cover target, in days?",
"New storage capacity is a forward-looking signal of higher tonnage demand. Asking 'what is the new cover target' confirms the buyer's own planning math and reveals volume.",
"A new stockpile pad, silo, dome, or warehouse has been commissioned within the last 6 months.",
["Capex announcements for storage infrastructure","EPC contractor announcements (often the contractor publicizes)","Local permits for new construction"],
"'Around 45 days. We are still fine-tuning.'",
"'That information is not public.'",
"Understood. If ECONARES can support a higher cover target with multi-vessel scheduling, would {company} want a framing conversation?",
"1. {rep}: {opening}\n2. Buyer: shares or deflects\n3. {rep}: 'How many vessels per quarter does that translate to?'\n4. Buyer: gives number\n5. {rep}: 'We can hold a multi-vessel slot if the spec is steady. Send me the Q-by-Q forecast when ready.'\n6. Email follow-up.",
"If you do not know the storage type, do not guess. Use a generic: 'the new storage infrastructure at {plant}'."))

HOOKS.append(H(2, "The Plant Expansion Announcement", "All",
"Hi {name}, {rep} from ECONARES. Saw the expansion announcement at {plant} \u2014 moving from {old} to {new}. When does the new throughput come online, and is the additional {commodity} volume already covered?",
"Same logic as the capacity upgrade hook, but the angle is timing. Buyers under expansion pressure are usually running a tight procurement calendar \u2014 calling early means being on the shortlist, not the bench.",
"Major expansion project is in execution phase (12\u201324 months from completion).",
["EPC contractor press releases","Government permits and EIA filings","OEM announcements for the new equipment"],
"'Online next {month}. Sourcing is partly done.'",
"'Sourcing is still open. Why are you asking?'",
"Because most operators we work with add a parallel supplier at this stage to de-risk the ramp-up. ECONARES can deliver FOB {origin} on a flexible schedule. Mind if I send a one-pager?",
"1. {rep}: {opening}\n2. Buyer: timeline update\n3. {rep}: 'What is the cover policy during the ramp \u2014 single supplier or dual?'\n4. Buyer: answers\n5. {rep}: 'Send me the ramp spec and I will line up a parallel offer.'\n6. Log to CRM with expansion date and contact name.",
"Always use the actual capex figure. Buyers love the caller who knows the project number."))

HOOKS.append(H(2, "The Demolition Or Rebuild", "All",
"Hi {name}, {rep} from ECONARES. I saw the demolition notice on the old {unit} at {plant}. Out of curiosity \u2014 is the new {unit} going to run on the same {commodity} spec, or is this an opportunity to revisit the grade?",
"Demolition-and-rebuild is a buyer's chance to fix a spec they have always hated. They are open to conversations they would not have taken 6 months earlier. Be there at the moment of openness.",
"Plant has filed for demolition and announced a replacement unit within the last 6\u201312 months.",
["Demolition permits, environmental filings","Engineering contractor announcements","Local newspaper for community impact"],
"'Same spec, just newer equipment.'",
"'We are revisiting the spec. Send your range.'",
"Got it. If ECONARES can match the new spec on a multi-vessel schedule, I will send an indicative range. What is the new commissioning target?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'When does the new unit come online?'\n4. Buyer: gives date\n5. {rep}: 'I will time a one-pager for the new unit's commissioning quarter.'\n6. Calendar reminder set.",
"Buyers under demolition pressure are time-rich but information-poor. Be patient, ask more, pitch less."))

HOOKS.append(H(2, "The New Conveyor / Handling System", "Coal; Nickel ore; PKS; Woodchips",
"Hi {name}, {rep} from ECONARES. I saw the new conveyor / ship-loader at {port_or_plant} went live. That usually changes the optimal {commodity} vessel size \u2014 bigger parcels, faster turnaround. Has {company} rethought the lift size?",
"New material handling equipment signals a step-change in throughput. Buyers are recalibrating vessel sizes and frequency. By asking 'have you rethought the lift size', you surface a planning conversation most suppliers miss.",
"A new conveyor, ship-loader, stacker-reclaimer, or similar has been commissioned in the last 6 months.",
["EPC contractor announcements (FLSmidth, ThyssenKrupp, etc.)","Port authority capex reports","Trade press for the specific facility"],
"'We are running trials. Not final yet.'",
"'Same vessel size. Nothing has changed.'",
"Understood. If ECONARES can support a larger parcel on a single-vessel basis, I will keep that in mind. Send me a note when the new lift size is locked in.",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What throughput are you targeting per hour?'\n4. Buyer: gives figure\n5. {rep}: 'We can size the parcel to match. Mind if I check back in {weeks} weeks?'\n6. Set CRM reminder.",
"Know the OEM of the new equipment. It signals you have done the research. The OEM is almost always in the announcement."))

HOOKS.append(H(2, "The Capacity Factor Change", "Coal; Diesel; PKS",
"Hi {name}, {rep} from ECONARES. I noticed {plant}'s capacity factor has moved from {old_cf} to {new_cf} in the last {period}. That changes the {commodity} burn rate by roughly {delta} percent. Is the new burn rate reflected in the current supply contract, or are you running ahead of plan?",
"Capacity factor swings change burn rates silently. Buyers sometimes do not realize their own contract is now short until they are 30 days from a stockout. Naming the math positions you as a strategic partner, not a vendor.",
"The plant has publicly reported a sustained change in capacity factor (typically ERC filings for PH power plants).",
["ERC, MGB, DOE capacity factor reports","Plant's annual operating report","Industry trade press for outages or demand changes"],
"'We have spotted it. Re-procurement is in motion.'",
"'Good catch. We are still catching up.'",
"Got it. If ECONARES can deliver a top-up parcel to bridge the gap, we can turn it around in {weeks} weeks on FOB basis. Worth a quick spec check?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the top-up volume you need?'\n4. Buyer: gives number\n5. {rep}: 'Send me your burn forecast and I will line up a parallel offer.'\n6. Email follow-up with offer framework, not price.",
"Run the math yourself before calling. Buyers will test the figures, and being wrong destroys credibility instantly."))
HOOKS.append(H(3, "The Ownership / M&A Change", "All",
"Hi {name}, {rep} from ECONARES. Congratulations on the {new_owner} transaction closing last month. New ownership usually means a fresh review of the {commodity} supply book in the first {n} quarters. Has {company} kicked off that review yet, or is it still on the to-do list?",
"M&A closings are the highest-leverage moment to call. The new owner is mandated to find synergies and the procurement book is the easiest place to start. Be the first phone call after the announcement lands.",
"M&A transaction has formally closed (not just announced) within the last 1\u20136 months.",
["SEC / HKEX / PSE / local regulatory filings for the close date","Press releases from both buyer and seller","LinkedIn for new executives joining the buyer's procurement team"],
"'Yes, we are reviewing the supply book now.'",
"'No, we are continuing as-is.'",
"Understood. If the review does open up, ECONARES can deliver FOB {origin} with pre-shipment lab cert per lot. Mind if I send a one-pager for the file?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'Who is leading the supply book review?'\n4. Buyer: gives a name\n5. {rep}: 'I will reach out to {review_lead} directly. Should I cc you?'\n6. Confirm email addresses, set follow-up.",
"Always confirm the actual close date. Announced \u2260 closed. Calling on a rumored deal is reputationally fatal."))

HOOKS.append(H(3, "The New CEO / Plant Head", "All",
"Hi {name}, {rep} from ECONARES. I read that {new_leader} just took over as {title} at {company} \u2014 congrats to them. New leaders usually want to widen their supplier base in the first {n} months. Is the {commodity} procurement book on their early agenda, or is it inherited as-is?",
"New leaders are the most receptive buyers in any commodity market. They do not yet have loyalty to the incumbents, and they want to demonstrate they brought fresh thinking. Calling in the first 90 days is high-leverage.",
"A new C-level, plant head, or VP of operations has been appointed within the last 90 days.",
["Press release, LinkedIn announcement","Trade press interviews with the new leader","Industry associations' announcements (e.g., PHINMA, MEC, MAC)"],
"'They are reviewing. Send a one-pager.'",
"'They inherited the book. Nothing will change soon.'",
"Got it. Even so, having ECONARES on file helps when a one-off opportunity opens up. Mind if I send the spec summary to {new_leader}'s office?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'When is {new_leader}'s first town hall / industry appearance?'\n4. Buyer: gives a date\n5. {rep}: 'I will time a follow-up to land right after. Anything they will be reviewing first?'\n6. Calendar reminder set.",
"Spell the new leader's name correctly. First-time mispronunciation of the CEO is a call you cannot recover from."))

HOOKS.append(H(3, "The New Procurement Manager", "All",
"Hi {name}, {rep} from ECONARES. I saw you joined {company} as {title} last month \u2014 welcome. New procurement heads usually want to do a quick market scan in the first {n} days. Do you have a 15-minute slot this week or next to compare notes on the {commodity} supply book?",
"Procurement managers are the gatekeepers. Catching one in the first 30 days of a new role is the single highest-leverage call in commodity sales. They want to be seen as bringing new options to the table.",
"A new procurement manager, supply chain head, or materials director has joined within the last 30 days.",
["LinkedIn announcement of the new role","Press release from the new hire's prior company","Industry trade press"],
"'Yes, this is exactly what I am doing. Send a calendar invite.'",
"'I have inherited the book. I will call you if needed.'",
"Understood. Even if you do not need a new supplier now, having a second-source option is always useful. I will send a one-pager for the file. Welcome to the role.",
"1. {rep}: {opening}\n2. Buyer: warm or cool\n3. {rep}: 'What is your current priority \u2014 cost down, de-risking, or new specs?'\n4. Buyer: gives priority\n5. {rep}: 'ECONARES can support all three. Send me your priority and I will frame a one-pager to match.'\n6. Same-day follow-up email.",
"Look at the new manager's prior role. If they came from a competitor or a different commodity, mention it carefully \u2014 they may have opinions you can learn from."))

HOOKS.append(H(3, "The New Project Commissioning", "All",
"Hi {name}, {rep} from ECONARES. I read about the new {project_name} project at {company} \u2014 looks like a {capex} capex on a {timeline} timeline. Does the {commodity} supply for the project sit with your team, or with a separate EPC procurement function?",
"Major projects have a parallel procurement track that often runs faster than the operations procurement. By asking which function owns it, you learn who to call next and avoid the silent 'wrong department' trap.",
"Capex project announcement (typically USD 50M+) within the last 6\u201312 months.",
["Press release on the capex","EPC contractor announcements","Regulatory filings (EIS, ECC in PH)"],
"'It sits with EPC procurement. Their contact is {name}.'",
"'It sits with us. We own the supply.'",
"Got it. I will route the one-pager to the right inbox. Mind if I confirm the project timeline and the {commodity} annual volume?",
"1. {rep}: {opening}\n2. Buyer: route confirmation\n3. {rep}: 'What is the targeted commercial operation date?'\n4. Buyer: gives date\n5. {rep}: 'I will line up a one-pager for the bid window. What is the typical lead time for the EPC?'\n6. Set CRM reminder for bid window.",
"Have the capex number ready. Most callers do not \u2014 it is an easy credibility win."))

HOOKS.append(H(3, "The Industry Award Won", "All",
"Hi {name}, {rep} from ECONARES. Saw the {award_name} award announcement \u2014 well-deserved. Curious question: the operations team that pulled that off, are they the same team driving the {commodity} sourcing strategy?",
"Awards are public, positive, and almost always answered. By pivoting to operations, you enter the buyer's world through the door of their proudest moment, then route the conversation to procurement.",
"A trade group, government, or industry media has awarded the buyer within the last 6 months.",
["Trade association websites (e.g., MAC, PHINMA, MEC, JMC)","Government award announcements (DOE, DENR, BOI)","Industry media (Reuters, S&P Global, Argus)"],
"'Yes, the same team. They handle sourcing too.'",
"'Different team. Procurement is separate.'",
"Got it. I will route my note to the procurement side. Just to be on the radar \u2014 ECONARES can deliver FOB {origin} on a flexible schedule. Worth a one-pager?",
"1. {rep}: {opening}\n2. Buyer: team structure\n3. {rep}: 'Who leads procurement?'\n4. Buyer: gives name\n5. {rep}: 'Send me {procurement_lead}'s email. I will follow up directly.'\n6. Email follow-up same day.",
"Use the actual award name. Generic flattery ('saw you won an award') is detectable."))
HOOKS.append(H(3, "The ESG Announcement", "Coal; Nickel ore; CPO",
"Hi {name}, {rep} from ECONARES. Saw the {company} ESG / sustainability report for {year}. Most operators in {region} are tightening the chain-of-custody requirement for {commodity} \u2014 is that filtering into your sourcing criteria yet, or is it still upstream of procurement?",
"ESG is a real procurement filter now, especially for EU-bound and Japan-bound supply chains. The buyer is being asked about it by their board, their customers, or their lenders. Naming the pressure positions you as someone who understands the new question, not the old one.",
"Buyer has published a sustainability report, joined a responsible sourcing initiative (e.g., RMI, IRMA, ISCC), or made an ESG commitment within the last 12 months.",
["Buyer's annual sustainability report","Press releases on responsible sourcing commitments","Trade association ESG frameworks (e.g., IRMA, ASI)"],
"'Yes, it is filtering in. We have a compliance checklist.'",
"'Not yet, but it is on the roadmap.'",
"Got it. ECONARES works with operators who need documented chain-of-custody on {commodity}. I will send a one-pager on our documentation standard. Is {colleague} the right contact?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the most common documentation gap you see from suppliers?'\n4. Buyer: shares gap\n5. {rep}: 'Send me your checklist and I will pre-validate ECONARES against it before we even talk tonnage.'\n6. Email follow-up with checklist response.",
"Avoid the trap of being the ESG police. Frame the hook as a question, not an accusation."))

HOOKS.append(H(3, "The Plant Accident / Safety Incident", "All",
"Hi {name}, {rep} from ECONARES. I read the incident report on {plant} last month. Hope the team is back to normal operations. After a safety event, the {commodity} inventory is often the first thing that gets re-validated. Has {company} had to top up cover?",
"Post-incident, the buyer's first concern is operational continuity. Calling with empathy first, then asking a supply question, reads as helpful. Coming in with a hard pitch reads as predatory.",
"A documented safety, fire, or environmental incident has been made public within the last 1\u20133 months.",
["Regulatory filings (DOE, DENR, DOLE in PH)","Trade press for the incident","Local newspaper for community impact"],
"'Yes, we are rebuilding cover. Send a one-pager.'",
"'We are fine. Operations are normal.'",
"Understood. ECONARES can run a fast-track parcel if it ever helps. Worth a one-pager for the file?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the new cover policy post-incident?'\n4. Buyer: gives number\n5. {rep}: 'Send me the new cover number and I will line up a multi-vessel schedule.'\n6. Email follow-up with empathy note first.",
"Lead with empathy. The first 10 seconds of this call set the tone for the relationship. No pitching until at least 60 seconds in."))

HOOKS.append(H(3, "The IPO Or Bond Issuance", "All",
"Hi {name}, {rep} from ECONARES. I saw the {ipo_or_bond} announcement \u2014 congrats. Post-listing, capex discipline usually tightens and procurement gets pressure to validate every supplier on the books. Is {company} running a supplier rationalization exercise right now?",
"Post-IPO or post-bond-issuance, the buyer's CFO and board are asking procurement to justify every supplier. This is a procurement-reshuffling window. The supplier who shows up during the rationalization gets retained; the one who does not, gets cut.",
"IPO, follow-on offering, or major bond issuance within the last 6\u201312 months.",
["SEC / HKEX / PSE filings for the offering","Press releases from the issuer and the underwriters","Investor presentations and use-of-proceeds language"],
"'Yes, rationalization is underway.'",
"'No, we are continuing with the existing book.'",
"Understood. Even so, a documented FOB {origin} option with a pre-shipment lab cert per lot is useful for the file. Mind if I send a one-pager?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'When is the rationalization review due to close?'\n4. Buyer: gives date\n5. {rep}: 'I will time a one-pager to land in that window. Anything specific the review team will need?'\n6. Calendar reminder set.",
"Capital markets jargon is fine here. Buyers respect callers who understand their world."))

HOOKS.append(H(3, "The Subsidiary Launched", "All",
"Hi {name}, {rep} from ECONARES. Saw the announcement on the new {subsidiary_name} subsidiary. New entities usually start with a clean supplier book. Is the {commodity} sourcing for {subsidiary_name} on a fresh RFP, or carried over from {parent}?",
"Subsidiaries have no legacy supplier loyalty. They are setting up contracts from scratch. By catching the subsidiary at incorporation, you are at the front of the queue, not the back.",
"A new subsidiary, JV, or special-purpose vehicle has been announced or registered within the last 3\u20136 months.",
["SEC / corporate registry filings","Press releases on the new entity","LinkedIn for the subsidiary's leadership team"],
"'Fresh RFP. We are open to new suppliers.'",
"'Carried over from {parent}. Same book.'",
"Understood. If the subsidiary does open an RFP, ECONARES can deliver FOB {origin} on a flexible schedule. Mind if I send a one-pager for the file?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'Who is leading the new entity's procurement?'\n4. Buyer: gives name\n5. {rep}: 'Send me {subsidiary_procurement_lead}'s email. I will reach out directly.'\n6. Confirm email addresses, set follow-up.",
"The subsidiary's name is critical. Get it from the SEC / corporate registry, not from trade press headlines."))

HOOKS.append(H(3, "The Contract Win Announced", "All",
"Hi {name}, {rep} from ECONARES. Saw the contract win announcement on {project_or_buyer}. That kind of pipeline growth usually means {company}'s {commodity} burn rate is about to step up. Has procurement started the new sourcing review yet?",
"New contract wins trigger step-up in raw material needs. Procurement is usually behind operations in planning for this. Calling with the operational logic forces procurement to engage before the stockout happens.",
"A new contract win, customer addition, or major order has been announced within the last 1\u20133 months.",
["Press release on the contract win","Investor presentations or earnings calls","Trade press for the new customer or project"],
"'Yes, we are planning for it now.'",
"'We have not started. Operations is still confirming.'",
"Got it. ECONARES can support a stepped-up burn rate with a multi-vessel schedule. Mind if I send a one-pager?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the new annual volume expectation?'\n4. Buyer: gives number\n5. {rep}: 'We can size a multi-vessel program to match. Send me the new burn forecast.'\n6. Email follow-up.",
"Have the buyer's customer name ready. Buyers are proud of their wins. Acknowledging it earns trust fast."))
HOOKS.append(H(4, "The Tight-Market Probe", "Nickel ore; Coal; Copper concentrate; PKS",
"Hi {name}, {rep} from ECONARES. The {commodity} market has tightened in the last {period} \u2014 {benchmark} is up {delta} percent. Is {company} seeing that reflected in your landed cost, or are you still on legacy contract pricing?",
"You name the market move, the buyer immediately knows you are watching. The question forces them to reveal whether they are hedged (no urgency) or exposed (high intent).",
"A real, verifiable market move has occurred in the last 30\u201390 days. Use Argus, S&P Global, or Fastmarkets for the figure.",
["Argus / S&P Global / Fastmarkets for the latest benchmark","LME, SHFE, or Newcastle index moves","Trade press for the regional supply tightness"],
"'We are on legacy pricing. Not yet exposed.'",
"'Yes, we are exposed. Looking at options.'",
"Got it. If the legacy contract rolls over in the next {n} months, ECONARES can deliver against the new benchmark on FOB basis. Worth a one-pager?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'When does your current contract roll over?'\n4. Buyer: gives date\n5. {rep}: 'I will time a one-pager to land {weeks} weeks before. Anything I should pre-validate?'\n6. Calendar reminder set.",
"Use a real benchmark. Buyers test the math. Being wrong on the figure destroys credibility for the next 6 months."))

HOOKS.append(H(4, "The Oversupply Probe", "Nickel ore; Coal; PKS",
"Hi {name}, {rep} from ECONARES. With {commodity} oversupplied in {region} this quarter, spot is trading {delta} below benchmark. Are you taking spot parcels to capture the discount, or staying full on contract?",
"In an oversupplied market, buyers have leverage. By naming the spot discount, you signal you know the buyer's world. The question reveals whether they are price-takers (stuck on contract) or price-makers (active in spot).",
"A real oversupply has been documented in trade press within the last 30\u201360 days.",
["Argus / S&P Global for the spot-vs-benchmark spread","Trade press for the oversupply drivers","Port inventory data (where available)"],
"'We are full contract. Missed the spot window.'",
"'We are taking spot. Send your offer.'",
"Got it. If the spot window stays open, ECONARES can deliver against it on FOB basis. Mind if I send a one-pager?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is your typical spot parcel size?'\n4. Buyer: gives number\n5. {rep}: 'We can size a parcel to match. Send me the spec.'\n6. Email follow-up.",
"Oversupply windows are short. The call must be timely. If the oversupply is more than 60 days old, swap the hook to a softer variant."))

HOOKS.append(H(4, "The Freight Rate Spike", "All",
"Hi {name}, {rep} from ECONARES. Baltic Dry / Capesize indices spiked {delta} percent in the last {period}. That hits CIF landed cost hard. Is {company} seeing it in your last {n} shipments, or are you mostly on FOB and insulated?",
"Freight is the most volatile line item in commodity landed cost. Buyers on CIF feel it instantly. By asking whether they are FOB or CIF, you learn the buyer's contract structure without asking directly.",
"A real freight index move has occurred within the last 30 days (Baltic Exchange, Baltic Dry, Capesize).",
["Baltic Exchange for the index move","Trade press for the freight drivers (port congestion, tonnage shortage)","Lloyd's List for the regional view"],
"'CIF. We are feeling it.'",
"'FOB. We are insulated.'",
"Got it. If {company} is on CIF, ECONARES can deliver FOB and let you control the freight \u2014 typically shaving {delta} off the delivered cost. Worth a conversation?",
"1. {rep}: {opening}\n2. Buyer: incoterms confirmation\n3. {rep}: 'What discharge port are you targeting?'\n4. Buyer: gives port\n5. {rep}: 'Send me the latest freight quote and I will tell you straight whether FOB is competitive.'\n6. Email follow-up with framework.",
"Freight markets move fast. Refresh the index figure on the morning of the call."))

HOOKS.append(H(4, "The Port Congestion Hook", "Coal; Nickel ore; Diesel",
"Hi {name}, {rep} from ECONARES. {port} is showing {days}-day average berth wait this month, up from {baseline}. Is {company}'s discharge schedule slipping, or are you routing through {alt_port}?",
"Port congestion is real and public. By naming the wait time, you confirm you know the operational reality. The question reveals whether the buyer is exposed (urgent) or hedged (cool).",
"Port authority data or Lloyd's List confirms a congestion event in the last 30 days.",
["Port authority statistics (e.g., PPA, MPIC ports in PH)","Lloyd's List for the congestion report","Vessel tracking sites (MarineTraffic, Vesselfinder)"],
"'Yes, schedule has slipped. We are exposed.'",
"'We are routing around it. Insulated.'",
"Got it. ECONARES loads out of {alt_load_port} with shorter queue. If {company} ever needs a parallel discharge, I can line up a vessel from there.",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is your typical demurrage exposure on a {vessel_size} vessel at {port}?'\n4. Buyer: gives figure\n5. {rep}: 'We can route to {alt_discharge_port} and demurrage is typically lower. Mind if I send a framework?'\n6. Email follow-up with demurrage framework.",
"Always know a backup port. The hook is only as strong as the alternative you can offer."))

HOOKS.append(H(4, "The Quality-Issue-Region Hook", "Nickel ore; Coal; PKS",
"Hi {name}, {rep} from ECONARES. I am hearing a lot of complaints from buyers in {region} on {commodity} quality this quarter \u2014 moisture creep, off-spec ash, size fraction issues. Is that hitting {company} as well, or are you insulated?",
"Quality issues across a region are public. Buyers are quietly comparing notes. By raising the regional conversation, you position as a sector observer, not a desperate vendor.",
"Trade press, lab reports, or industry forums confirm a quality issue at the regional level within the last 30\u201390 days.",
["Trade press for the quality issue","Industry forums and trader networks","SGS / Intertek lab reports (sometimes public)"],
"'Yes, we are seeing it. Quality is slipping.'",
"'No, we are insulated. Our supplier is tight.'",
"Got it. ECONARES runs pre-shipment lab cert per lot on {commodity}. If {company} ever needs a backup, I will keep ECONARES in mind. Mind if I send a one-pager?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the most common failure mode you are seeing?'\n4. Buyer: shares detail\n5. {rep}: 'Send me a recent failed-lot report and I will tell you straight whether ECONARES can hit the spec.'\n6. Email follow-up with framework.",
"Do not name a specific supplier. The hook is about the region, not the company."))
HOOKS.append(H(4, "The New Regulation Hook", "Coal; Nickel ore; Diesel; CPO",
"Hi {name}, {rep} from ECONARES. The new {regulation_name} in {jurisdiction} kicks in on {date}. Most operators we work with are starting to think about the {commodity} sourcing implications. Is {company} reviewing the spec now, or after the implementation date?",
"Regulations are forcing functions. Buyers are obliged to react. By being the first to call, you help them think through the spec change rather than react to a deadline.",
"A new regulation has been published within the last 6 months, with an implementation date in the next 6\u201324 months.",
["Government gazettes (Philippine Gazette, BOI circulars)","Industry association briefings (MAC, PHINMA, JMC)","Trade press for the regulation analysis"],
"'Yes, we are reviewing now. Send your range.'",
"'We are reviewing. Will reach out if needed.'",
"Understood. ECONARES can pre-validate our {commodity} against the new spec. Mind if I send the documentation set?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the most operationally challenging element of the new rule?'\n4. Buyer: shares detail\n5. {rep}: 'Send me the spec interpretation memo and I will line up a {commodity} that fits.'\n6. Email follow-up with regulatory summary.",
"Always cite the regulation by its actual name and date. Generic references ('the new rules') sound unprepared."))

HOOKS.append(H(4, "The Competing-Buyer Tightening", "Nickel ore; Coal; CPO",
"Hi {name}, {rep} from ECONARES. {competing_buyer} has been actively lifting {commodity} parcels in {region} for the last {period}. Spot supply is getting thin. Has {company} secured the next quarter's volume yet, or are you still in the market?",
"A competing buyer ramping up is a public fact (visible in customs data). Naming them creates a real urgency for the buyer. The question forces them to confirm they are still shopping or admit they are covered.",
"Customs data or trade press confirms a competing buyer has increased offtake in the last 30\u201360 days.",
["Panjiva / ImportGenius for the competing buyer's volumes","Trade press for the buyer's expansion","LinkedIn for the competing buyer's hiring spree"],
"'We are still in the market. What is your offer?'",
"'We are covered. Not shopping right now.'",
"Got it. If {company} ever needs a top-up, ECONARES can deliver on FOB basis with pre-shipment lab cert per lot. Mind if I send a one-pager for the file?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the typical parcel size you would consider for a top-up?'\n4. Buyer: gives number\n5. {rep}: 'We can size a parcel to match. Send me the spec.'\n6. Email follow-up.",
"Name the competing buyer accurately. Wrong name = wrong intel = call over."))

HOOKS.append(H(4, "The Source-Country Export Ban", "Nickel ore; Coal; CPO",
"Hi {name}, {rep} from ECONARES. The {source_country} export ban on {commodity} is reshaping the regional supply book. Is {company} re-routing sourcing or running the existing book?",
"Export bans are seismic. The buyer's incumbent supply chain may collapse overnight. Being the first phone call after the announcement gives you a real seat at the table.",
"A real, verifiable export ban, quota, or licensing change has been announced within the last 1\u20136 months.",
["Government gazettes in the source country","Reuters / Bloomberg / FT for the announcement","Trade press for the regional impact analysis"],
"'We are re-routing. Open to options.'",
"'We are still running the existing book. Watching.'",
"Understood. If the re-routing opens up a gap, ECONARES can deliver FOB {alt_origin} as a parallel option. Mind if I send a one-pager?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the new landed cost you are working with?'\n4. Buyer: gives figure\n5. {rep}: 'Send me the spec and I will line up a parallel offer from {alt_origin}.'\n6. Email follow-up.",
"Have the actual gazette reference ready. Buyers will check."))

HOOKS.append(H(4, "The Currency Move", "All",
"Hi {name}, {rep} from ECONARES. {currency} has moved {delta} percent against USD in the last {period}. For buyers priced in {currency}, that hits landed cost. Is {company} hedging on {commodity} or riding the spot?",
"Currency moves are silent killers of margin. The buyer may not even be tracking the impact. By raising it, you position as a partner who thinks about their P&L, not just your own tonnage.",
"A real currency move of more than 3\u20135 percent in the last 30\u201360 days.",
["Bloomberg / Reuters for the FX move","Central bank statements (BSP, PBOC, BOJ)","Trade press for the regional currency impact"],
"'We are hedged. Insulated.'",
"'Riding the spot. Painful.'",
"Got it. If the spot ride gets too painful, ECONARES can offer a USD-priced FOB option to lock in the move. Mind if I send a one-pager?",
"1. {rep}: {opening}\n2. Buyer: hedging status\n3. {rep}: 'What is the contract currency mix today?'\n4. Buyer: gives mix\n5. {rep}: 'Send me the contract currency breakdown and I will line up a USD-priced FOB option.'\n6. Email follow-up.",
"Currency hooks work best with mid-cap and large-cap buyers. Small buyers often ride the spot anyway."))

HOOKS.append(H(4, "The Force Majeure At A Major Mine", "Nickel ore; Coal; Copper concentrate",
"Hi {name}, {rep} from ECONARES. The force majeure at {mine} is putting pressure on regional {commodity} supply. Is {company} seeing a knock-on effect, or are you covered under existing contracts?",
"Force majeure is the buyer's worst-case scenario. Calling with empathy and a parallel-supply offer is the right tone. Hard-sell during a crisis destroys the relationship.",
"A real, documented force majeure has been declared by a major mine in the last 1\u201330 days.",
["Mine operator press releases","Trade press for the impact analysis","Customs data for the affected buyer's volume changes"],
"'Yes, we are exposed. Looking for backup.'",
"'We are covered. Watching the market.'",
"Understood. If the exposure widens, ECONARES can deliver FOB {alt_origin} on a fast-track basis. Mind if I send a one-pager for the file?",
"1. {rep}: {opening}\n2. Buyer: exposure status\n3. {rep}: 'What volume gap are you trying to close?'\n4. Buyer: gives number\n5. {rep}: 'Send me the spec and I will line up a parallel offer.'\n6. Email follow-up with empathy note first.",
"Lead with empathy, not opportunity. The first 30 seconds set the tone."))
# ============ CATEGORY 5: MUTUAL CONNECTION (5) ============
HOOKS.append(H(5, "The Mutual Contact Intro", "All",
"Hi {name}, {rep} from ECONARES. {mutual_contact} at {mutual_company} suggested I reach out \u2014 they mentioned {company} has been reviewing the {commodity} supply book. Mind if I take 15 minutes to compare notes?",
"A real mutual contact turns a cold call into a warm one. The buyer's first question is 'why did they refer you', and the rest of the call flows from that answer.",
"You have a real, citable mutual contact who has explicitly said it is fine to use their name.",
["LinkedIn for the mutual contact's relationship to the buyer","Trade group rosters (MAC, PHINMA, MEC) for shared membership","Industry events (conferences, seminars) for prior meetings"],
"'Yes, {mutual_contact} and I talk often. What is the question?'",
"'Who? I do not recognize the name.'",
"Apologies for any confusion \u2014 {mutual_contact} and I worked together on a {commodity} project. I will reach out via them to confirm the intro. Thanks for the time.",
"1. {rep}: {opening}\n2. Buyer: warm or cool\n3. {rep}: 'What is the most pressing question on your {commodity} supply?'\n4. Buyer: shares question\n5. {rep}: 'Send me your spec and I will line up a parallel offer.'\n6. Email follow-up.",
"Only use this hook with a real, pre-cleared mutual contact. Fabricating a name is the fastest way to lose the deal and the network."))

HOOKS.append(H(5, "The Trade Group Member Intro", "All",
"Hi {name}, {rep} from ECONARES. I see we are both members of {trade_group} \u2014 I am on the {commodity} working group. Has {company} been active in the {trade_group} {commodity} sessions this year?",
"Trade group membership is a real, verifiable bridge. By referencing a working group, you enter the buyer's professional community, not as a salesperson.",
"You are a member of a trade group the buyer also belongs to. Common PH examples: MAC, PHINMA, JMC, PEC, PCCI, MEC.",
["Trade group membership rosters (often public)","Working group minutes (sometimes public)","LinkedIn for shared group memberships"],
"'Yes, we have been active. What is on your mind?'",
"'I am not the right contact for {trade_group} matters.'",
"Understood. If the working group is reviewing the {commodity} supply book, ECONARES can contribute data. Mind if I send a one-pager?",
"1. {rep}: {opening}\n2. Buyer: warm or cool\n3. {rep}: 'What is the working group focused on this year?'\n4. Buyer: shares focus\n5. {rep}: 'Send me the working group's output and I will line up a complementary offer.'\n6. Email follow-up.",
"Be a real member. Pretending to be in a trade group is detectable and reputationally fatal in PH commodity circles."))

HOOKS.append(H(5, "The Conference / Seminar Connection", "All",
"Hi {name}, {rep} from ECONARES. We were both at {event_name} last {month}. I remember the {commodity} panel generated a lot of follow-up questions. Did {company} take any action on the takeaways?",
"Conference attendance is public, LinkedIn-verifiable. By referencing a panel, you enter through the buyer's recent professional experience. The question 'did you take any action' is a probe for active intent.",
"You and the buyer were both at the same industry event within the last 3\u20136 months.",
["Event attendee lists (sometimes public, sometimes via LinkedIn)","Panel recordings and summaries","Trade press for the event recap"],
"'Yes, we are acting on a few of those points.'",
"'I missed the panel. Send me the summary.'",
"Will do. ECONARES can support the action items on the {commodity} side. Mind if I send a one-pager?",
"1. {rep}: {opening}\n2. Buyer: warm or cool\n3. {rep}: 'Which takeaway did the team prioritize?'\n4. Buyer: shares priority\n5. {rep}: 'Send me the spec and I will line up a parallel offer.'\n6. Email follow-up with event summary link.",
"Have a specific panel title or speaker ready. Generic 'we were at the same event' sounds lazy."))

HOOKS.append(H(5, "The Sister Plant Connection", "All",
"Hi {name}, {rep} from ECONARES. I work with {sister_plant} on the {commodity} supply book. They mentioned {company}'s {plant} has been looking at the same spec band. Are the two plants running the same grade, or different recipes?",
"Sister plants are a real bridge in commodity trading. Operators share spec knowledge, supplier shortlists, and sometimes procurement teams. By referencing the sister plant, you enter the buyer's world as a known entity.",
"You have a real relationship with a sister plant of the buyer. Verify the relationship before dialing.",
["Corporate website for plant network","Trade press for shared ownership / operations","LinkedIn for shared procurement staff"],
"'Yes, same grade. Send your offer.'",
"'Different recipes. We are independent.'",
"Understood. ECONARES can deliver against either spec. Mind if I send a one-pager?",
"1. {rep}: {opening}\n2. Buyer: spec confirmation\n3. {rep}: 'When does {plant} next re-tender?'\n4. Buyer: gives date\n5. {rep}: 'I will time a one-pager to land {weeks} weeks before. Anything specific the team will need?'\n6. Calendar reminder set.",
"Confirm the sister plant relationship. Calling on a rumor will fail the buyer's verification in 5 seconds."))

HOOKS.append(H(5, "The Industry Consultant Intro", "All",
"Hi {name}, {rep} from ECONARES. {consultant_name} shared a few insights on {company}'s {commodity} strategy with me at the {event} last {month}. They mentioned the team is reviewing the spec band. Is that still active, or has it landed?",
"Industry consultants are a real, citable bridge. Buyers respect the consultant network. By referencing the consultant, you enter with third-party validation.",
"A real industry consultant has explicitly given you permission to use their name.",
["Consultant's published work on the buyer's sector","LinkedIn for the consultant's relationship to the buyer","Conference / event rosters for shared attendance"],
"'Yes, the spec review is active. What is your offer?'",
"'Who? I do not recognize the name.'",
"Apologies for the confusion. {consultant_name} works across the {sector} sector. I will reach out via them to confirm. Thanks for the time.",
"1. {rep}: {opening}\n2. Buyer: warm or cool\n3. {rep}: 'What is the most pressing spec question the team is wrestling with?'\n4. Buyer: shares question\n5. {rep}: 'Send me the spec and I will line up a parallel offer.'\n6. Email follow-up.",
"Get the consultant's explicit pre-clearance. Most consultants will not appreciate being used as a bridge without consent."))
# ============ CATEGORY 6: SPEC/LOGISTICS PROBLEM (10) ============
HOOKS.append(H(6, "The Moisture Problem", "Coal; PKS; Woodchips",
"Hi {name}, {rep} from ECONARES. Moisture creep on {commodity} is the silent margin killer in {region} this season. What is the tightest moisture band you are willing to accept at the discharge port?",
"Moisture is a real, recurring pain. By naming it, you signal you understand the operational cost. The question reveals the buyer's tolerance \u2014 useful intel for tailoring the offer.",
"Moisture is a known issue in the buyer's sector or region. PKD shipments, monsoon-loaded coal, and woodchips are typical examples.",
["Trade press for moisture issues in the region","Buyer's tender documents (often specify moisture band)","Lab reports for the buyer's typical incoming material"],
"'Below {n} percent, no exceptions.'",
"'We accept a wider band. Mostly.'",
"Got it. ECONARES can deliver at moisture band {x} on FOB basis. Mind if I send the lab cert template?",
"1. {rep}: {opening}\n2. Buyer: moisture band\n3. {rep}: 'What is your demurrage exposure if a parcel lands above the band?'\n4. Buyer: gives figure\n5. {rep}: 'Send me your moisture penalty schedule and I will pre-validate ECONARES against it.'\n6. Email follow-up with lab cert template.",
"Have a real lab cert sample ready. Most suppliers do not \u2014 it is a credibility win."))

HOOKS.append(H(6, "The Grade Consistency Issue", "Nickel ore; Coal; Copper concentrate",
"Hi {name}, {rep} from ECONARES. Grade consistency on {commodity} is the most common complaint we hear from buyers in {region}. Within a single vessel parcel, how much variance do you typically see?",
"Grade consistency is the buyer's number-one quality concern. By naming it, you enter the buyer's world as a peer, not a vendor. The question reveals the buyer's tolerance and the typical quality of their incumbent supply.",
"Grade consistency is a known issue in the buyer's sector (HPAL feed nickel, cement-grade coal, copper concentrate).",
["Trade press for grade consistency complaints","Buyer's tender documents for the consistency band","SGS / Intertek reports for typical variance"],
"'{delta} percent. It is fine.'",
"'It is painful. We are losing throughput.'",
"Got it. ECONARES runs pre-shipment composite samples per {n} MT. Mind if I send the sampling protocol?",
"1. {rep}: {opening}\n2. Buyer: variance number\n3. {rep}: 'What is the cost impact on your operations when the variance is at the high end?'\n4. Buyer: shares impact\n5. {rep}: 'Send me your tolerance band and I will line up a {commodity} that fits.'\n6. Email follow-up with sampling protocol.",
"Have a real sampling protocol. Buyers are technical and will test your credibility."))

HOOKS.append(H(6, "The Sulfur / Ash Penalty", "Coal",
"Hi {name}, {rep} from ECONARES. Sulfur and ash penalties on coal shipments can wipe out a contract's margin in a single quarter. What is the tightest penalty schedule you have accepted from a supplier?",
"Penalties are a public spec in the buyer's tender documents. By naming them, you signal you understand the buyer's commercial terms. The question reveals the buyer's most stringent supplier and their tolerance.",
"Buyer is in a sector with sulfur / ash penalties (power, cement, ferrous smelting).",
["Buyer's tender documents for penalty schedules","Industry benchmark for typical penalty bands","Trade press for the buyer's recent penalty disputes"],
"'Below {x} percent, no penalty.'",
"'We accept a tighter band than most.'",
"Got it. ECONARES can deliver at sulfur / ash {x} on FOB basis. Mind if I send the lab cert template?",
"1. {rep}: {opening}\n2. Buyer: penalty band\n3. {rep}: 'What is the demurrage cost when a parcel lands above the band?'\n4. Buyer: gives figure\n5. {rep}: 'Send me the penalty schedule and I will pre-validate ECONARES against it.'\n6. Email follow-up.",
"Have a real lab cert sample. The penalty band is the buyer's hard line. Missing it is a deal-killer."))

HOOKS.append(H(6, "The Demurrage Hook", "All",
"Hi {name}, {rep} from ECONARES. Demurrage at {port} has been running {days} days on average this quarter. For a {vessel_size} vessel, that is roughly {cost} per shipment. Is {company} absorbing that, or passing it back to the supplier?",
"Demurrage is a real, recurring cost. By quantifying it, you show operational literacy. The question reveals the buyer's commercial structure \u2014 FOB or CIF \u2014 and the urgency of the problem.",
"Demurrage is a known issue at the buyer's discharge port within the last 30\u201390 days.",
["Port authority data for average wait times","Trade press for demurrage rates","Lloyd's List for the port congestion report"],
"'We absorb it. Painful.'",
"'We pass it back. Suppliers hate it.'",
"Got it. ECONARES loads out of {alt_load_port} with shorter queue. We can typically shave {n} days off the demurrage exposure. Mind if I send a framework?",
"1. {rep}: {opening}\n2. Buyer: cost confirmation\n3. {rep}: 'What is the typical demurrage cost you are absorbing per quarter?'\n4. Buyer: gives figure\n5. {rep}: 'Send me the demurrage log and I will line up a parallel offer that reduces exposure.'\n6. Email follow-up with demurrage framework.",
"Have a real demurrage rate. Buyers will test the math."))

HOOKS.append(H(6, "The Container Shortage Hook", "PKS; Woodchips; Diesel",
"Hi {name}, {rep} from ECONARES. Container availability for {commodity} out of {origin} has been tight for the last {period}. Is {company} feeling the squeeze, or are you routing through breakbulk?",
"Container shortages are a public, regional pain. By naming it, you signal sector awareness. The question reveals the buyer's logistics structure and the urgency of the problem.",
"Container availability is tight in the buyer's origin region within the last 30\u201360 days.",
["Drewry / Xeneta for container availability data","Trade press for the regional shortage","Freight forwarder bulletins"],
"'Yes, we are squeezed. Looking for options.'",
"'We are routing through breakbulk. Insulated.'",
"Got it. ECONARES can deliver on breakbulk basis from {alt_origin} if needed. Mind if I send a one-pager?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the typical parcel size you would consider on breakbulk?'\n4. Buyer: gives number\n5. {rep}: 'We can size a parcel to match. Send me the spec.'\n6. Email follow-up.",
"Have a real breakbulk alternative. Container-constrained buyers need a credible Plan B."))
HOOKS.append(H(6, "The Size Fraction Mismatch", "Coal; Nickel ore; PKS; Woodchips",
"Hi {name}, {rep} from ECONARES. Size fraction consistency is the silent throughput killer for {commodity} buyers in {region}. What size band does {company} actually require at the discharge port, in mm?",
"Size fraction is a hard spec that most suppliers underestimate. By asking the precise mm band, you signal you know the operational reality. The question reveals the buyer's true tolerance.",
"Buyer's operation has a screening or crushing step (smelters, kilns, CFBC boilers, biomass feeders).",
["Buyer's tender documents for the size band","Equipment OEM spec sheets for the screening step","Trade press for the buyer's typical incoming fraction"],
"'{n} mm to {m} mm. Hard line.'",
"'We accept a wider band. Mostly.'",
"Got it. ECONARES can deliver at the {n}\u2013{m} mm band on FOB basis. Mind if I send the screen test report template?",
"1. {rep}: {opening}\n2. Buyer: size band\n3. {rep}: 'What is the throughput penalty when the fraction is off?'\n4. Buyer: gives figure\n5. {rep}: 'Send me the spec and I will line up a {commodity} that fits.'\n6. Email follow-up with screen test report.",
"Have the buyer's equipment OEM ready. The size band is tied to the OEM's design \u2014 knowing it is a credibility win."))

HOOKS.append(H(6, "The Contamination Risk Hook", "Nickel ore; Coal; Copper concentrate; Woodchips",
"Hi {name}, {rep} from ECONARES. Contamination on {commodity} shipments is the most expensive surprise \u2014 a single contaminant can downgrade a whole vessel. What is the tightest contaminant threshold {company} enforces?",
"Contamination is the buyer's nightmare. By naming it, you signal you understand the buyer's quality risk. The question reveals the buyer's true tolerance.",
"Contamination is a known risk in the buyer's sector (foreign material in nickel ore, tramp metal in coal, plastic in woodchips).",
["Buyer's tender documents for contaminant limits","Trade press for contamination incidents","Industry forums for the buyer's complaints"],
"'Below {x} ppm, no exceptions.'",
"'We accept a wider band. Mostly.'",
"Got it. ECONARES runs pre-shipment contaminant scans. Mind if I send the protocol?",
"1. {rep}: {opening}\n2. Buyer: threshold\n3. {rep}: 'What is the demurrage cost when a parcel fails the contaminant check?'\n4. Buyer: gives figure\n5. {rep}: 'Send me the spec and I will line up a {commodity} that fits.'\n6. Email follow-up with contaminant protocol.",
"Have a real contaminant protocol. Buyers are technical and will test your credibility."))

HOOKS.append(H(6, "The Vessel Size Mismatch", "All",
"Hi {name}, {rep} from ECONARES. Vessel size alignment is a quiet margin item \u2014 a {size_a} vessel at the wrong port can cost {delta} versus a {size_b}. What is the optimal vessel size for {company}'s {discharge_port}?",
"Vessel size is a real, recurring cost. By naming it, you show operational literacy. The question reveals the buyer's port capacity and the urgency of the problem.",
"Buyer's discharge port has a known size constraint (draft, berth length, storage).",
["Port authority data for vessel size limits","Trade press for the buyer's typical vessel size","MarineTraffic for the buyer's recent arrivals"],
"'{size_a}. Hard limit.'",
"'We are flexible. Whatever is available.'",
"Got it. ECONARES can size the parcel to match. Mind if I send a one-pager with vessel options?",
"1. {rep}: {opening}\n2. Buyer: vessel size\n3. {rep}: 'What is the demurrage exposure if the vessel is oversized?'\n4. Buyer: gives figure\n5. {rep}: 'Send me the vessel spec and I will line up a parallel offer.'\n6. Email follow-up with vessel options.",
"Have a real vessel size limit. The buyer's port is the hard constraint \u2014 overshooting is a deal-killer."))

HOOKS.append(H(6, "The Bagging / Labelling Issue", "PKS; Woodchips",
"Hi {name}, {rep} from ECONARES. Bagging and labelling consistency on {commodity} is the kind of small detail that becomes a big problem at the discharge port. What is {company}'s bag spec \u2014 weight, material, labelling?",
"Bagging is a real, recurring pain at the receiving end. By naming it, you signal you understand the buyer's operational reality. The question reveals the buyer's true spec.",
"Buyer receives bagged or labeled commodity (PKS, woodchips, sometimes nickel ore in jumbo bags).",
["Buyer's tender documents for bag spec","Trade press for the buyer's recent receiving issues","Industry forums for the buyer's complaints"],
"'{n} kg, {material}, standard label.'",
"'We are flexible. Whatever is available.'",
"Got it. ECONARES can deliver to spec on FOB basis. Mind if I send the bag spec template?",
"1. {rep}: {opening}\n2. Buyer: bag spec\n3. {rep}: 'What is the receiving cost when the bag spec is off?'\n4. Buyer: gives figure\n5. {rep}: 'Send me the spec and I will line up a {commodity} that fits.'\n6. Email follow-up with bag spec template.",
"Have a real bag spec. Buyers are technical and will test your credibility."))

HOOKS.append(H(6, "The Documentation Delay", "All",
"Hi {name}, {rep} from ECONARES. Documentation delays \u2014 bill of lading, certificate of origin, phyto certificate \u2014 can add {n} days to a shipment's effective transit. Is {company} seeing that as a recurring issue, or is it isolated?",
"Documentation is the silent transit killer. By naming the typical document set, you signal operational literacy. The question reveals the buyer's most common documentation pain.",
"Documentation is a known issue in the buyer's origin region (PH customs, MGB, DA, BOI).",
["Trade press for the origin region's documentation delays","Industry forums for the buyer's complaints","Customs data for transit time variance"],
"'Yes, that is a recurring pain.'",
"'No, we are insulated.'",
"Got it. ECONARES can pre-clear the documentation set. Mind if I send the standard document package?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the most common document that causes the delay?'\n4. Buyer: shares document\n5. {rep}: 'Send me your document checklist and I will pre-validate ECONARES against it.'\n6. Email follow-up with document package.",
"Have a real document package ready. Buyers are technical and will test your credibility."))
# ============ CATEGORY 7: TIMING/SEASONAL/SHIPPING (10) ============
HOOKS.append(H(7, "The Monsoon Stockpile Build", "Coal; Nickel ore; PKS; Woodchips",
"Hi {name}, {rep} from ECONARES. Monsoon is hitting {region} in {n} weeks. Most operators we work with start the pre-monsoon stockpile build in the next {m} weeks. Has {company} locked in the pre-monsoon tonnage, or is it still open?",
"Monsoon is a date on the buyer's calendar. Calling {m} weeks before the monsoon forces the buyer to think about their cover, not your product.",
"Monsoon is {n} to {n+m} weeks away in the buyer's region. PH monsoon: June\u2013November. Indonesia: November\u2013March.",
["PAGASA for the PH monsoon forecast","BMKG for the Indonesia monsoon forecast","Buyer's tender documents for the typical pre-monsoon volume"],
"'Yes, we are locked in. No gap.'",
"'Still open. What is the offer?'",
"Got it. ECONARES can deliver FOB {origin} on a {vessel_size} vessel to land before the monsoon. Mind if I send an indicative window?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the target cover in days before the monsoon?'\n4. Buyer: gives number\n5. {rep}: 'Send me the spec and I will line up a parcel that lands {weeks} weeks before.'\n6. Email follow-up.",
"Use the actual monsoon onset date for the buyer's region. Buyers track the calendar precisely."))

HOOKS.append(H(7, "The Pre-Monsoon Tonnage Lock-In", "Coal; Nickel ore; Diesel",
"Hi {name}, {rep} from ECONARES. Pre-monsoon is the most expensive window of the year for {commodity} liftings \u2014 vessel availability tightens and freight spikes. Has {company} locked in the next {n} weeks of tonnage, or are you still in the spot market?",
"Pre-monsoon is a known, dated squeeze. By naming the cost implication, you signal operational literacy. The question reveals the buyer's procurement posture.",
"Pre-monsoon is {n} weeks away in the buyer's region.",
["PAGASA / BMKG for the monsoon forecast","Baltic Exchange for the freight spike","Trade press for the regional vessel tightness"],
"'Locked in. We are covered.'",
"'Still in spot. Looking for options.'",
"Got it. ECONARES can hold a multi-vessel slot at {vessel_size} if the spec is steady. Mind if I send a one-pager?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the typical parcel size you would consider for a multi-vessel slot?'\n4. Buyer: gives number\n5. {rep}: 'We can size the program to match. Send me the spec.'\n6. Email follow-up.",
"Have a real vessel availability window. The pre-monsoon squeeze is real and dated."))

HOOKS.append(H(7, "The Year-End Procurement Rush", "All",
"Hi {name}, {rep} from ECONARES. Year-end procurement is the noisiest window of the calendar \u2014 everyone trying to clear budget and close POs. Has {company} already locked in the Q4 {commodity} tonnage, or is there still a gap?",
"Year-end is a public, dated budget event. By naming the rush, you signal sector awareness. The question reveals the buyer's gap, if any.",
"Q4 (October\u2013December) is approaching or in progress. Most buyers finalize Q4 sourcing in September\u2013October.",
["Buyer's annual report for the typical Q4 procurement cycle","Trade press for the buyer's recent year-end disclosures","LinkedIn for the buyer's Q4 hiring or capex"],
"'Locked in. No gap.'",
"'There is still a gap. What is the offer?'",
"Got it. ECONARES can deliver FOB {origin} before year-end. Mind if I send an indicative window?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the gap in MT?'\n4. Buyer: gives number\n5. {rep}: 'We can size a parcel to match. Send me the spec.'\n6. Email follow-up.",
"Have the buyer's fiscal year-end ready. PH companies often follow calendar year, but some follow April or July."))

HOOKS.append(H(7, "The Maintenance Season Window", "All",
"Hi {name}, {rep} from ECONARES. Maintenance season is coming up at {plant}. Pre-shutdown, most operators top up cover to last the outage. Has {company} lined up the pre-shutdown tonnage, or is that still open?",
"Maintenance season is a dated, public event. By naming it, you signal operational literacy. The question reveals the buyer's gap, if any.",
"Maintenance season is {n} weeks away in the buyer's plant.",
["Plant outage reports (PSALM, ERC, MGB in PH)","OEM service bulletins for the plant's equipment","Trade press for the buyer's maintenance calendar"],
"'Lined up. No gap.'",
"'Still open. What is the offer?'",
"Got it. ECONARES can deliver FOB {origin} to land before the shutdown. Mind if I send an indicative window?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the cover target in days before the shutdown?'\n4. Buyer: gives number\n5. {rep}: 'Send me the spec and I will line up a parcel to match.'\n6. Email follow-up.",
"Use the actual published shutdown date. Buyers are hypersensitive to stale intel."))

HOOKS.append(H(7, "The Lunar New Year Shipping Window", "Nickel ore; Coal; Copper concentrate",
"Hi {name}, {rep} from ECONARES. Lunar New Year shuts down Chinese ports for {n} weeks. For a {discharge_port} discharge, the pre-LNY vessel window is {m} weeks out. Has {company} locked in the pre-LNY tonnage, or is that still open?",
"Lunar New Year is a hard date on every commodity buyer's calendar. By naming the window, you show you know the buyer's operational reality. The question reveals the buyer's gap.",
"LNY is {n+m} weeks away. LNY falls in late January or early February.",
["LNY 2026 date (public calendar)","Trade press for the LNY shipping squeeze","Port authority bulletins for the LNY closure"],
"'Locked in. No gap.'",
"'Still open. What is the offer?'",
"Got it. ECONARES can hold a {vessel_size} slot to land before LNY. Mind if I send an indicative window?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the typical pre-LNY parcel size?'\n4. Buyer: gives number\n5. {rep}: 'We can size a parcel to match. Send me the spec.'\n6. Email follow-up.",
"Have the actual LNY date ready. Buyers track the calendar precisely."))
HOOKS.append(H(7, "The Chinese New Year Stockpile", "Nickel ore; Coal; CPO",
"Hi {name}, {rep} from ECONARES. Chinese New Year triggers a {n}-week stockpile build at most Chinese smelters and power plants. Has {company} lined up the stockpile tonnage, or is that still on the to-do list?",
"CNY stockpile is a real, dated squeeze. By naming the window, you signal operational literacy. The question reveals the buyer's gap, if any.",
"CNY is {n} weeks away.",
["CNY 2026 date (public calendar)","Trade press for the CNY stockpile build","Customs data for Chinese buyers' pre-CNY liftings"],
"'Lined up. No gap.'",
"'Still on the to-do list. What is the offer?'",
"Got it. ECONARES can deliver FOB {origin} on a {vessel_size} vessel to land before CNY. Mind if I send an indicative window?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the cover target in days before CNY?'\n4. Buyer: gives number\n5. {rep}: 'Send me the spec and I will line up a parcel to match.'\n6. Email follow-up.",
"Have the actual CNY date ready. Buyers track the calendar precisely."))

HOOKS.append(H(7, "The Typhoon Season Contingency", "All",
"Hi {name}, {rep} from ECONARES. Typhoon season in {region} is {n} weeks away. For a {discharge_port} discharge, the contingency planning usually starts now. Has {company} thought through a typhoon-season backup supplier?",
"Typhoon is a real, dated risk. By naming it, you signal sector awareness. The question reveals the buyer's contingency posture.",
"Typhoon season is {n} weeks away in the buyer's region. PH typhoon: June\u2013November, peak August\u2013October.",
["PAGASA for the PH typhoon forecast","JMA for the Japan typhoon forecast","Trade press for the buyer's recent typhoon-season issues"],
"'Yes, we have a backup. Insulated.'",
"'We are still planning. What is the offer?'",
"Got it. ECONARES can deliver from {alt_origin} as a typhoon-season backup. Mind if I send a one-pager?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the contingency volume you would need if your primary supplier is shut in?'\n4. Buyer: gives number\n5. {rep}: 'We can size a contingency parcel to match. Send me the spec.'\n6. Email follow-up.",
"Have a real typhoon track forecast. The buyer's planning is tied to the actual forecast."))

HOOKS.append(H(7, "The Vessel Scheduling Window", "All",
"Hi {name}, {rep} from ECONARES. The next {n}-week vessel scheduling window out of {origin} is filling up fast. Has {company} secured the next lift, or are you still lining up a vessel?",
"Vessel scheduling is a real, dated squeeze. By naming the window, you signal sector awareness. The question reveals the buyer's vessel posture.",
"Vessel availability is tight at the buyer's load port within the next {n} weeks.",
["Baltic Exchange for the vessel squeeze","Trade press for the regional vessel tightness","Lloyd's List for the load port congestion"],
"'Secured. We are covered.'",
"'Still lining up. What is the offer?'",
"Got it. ECONARES can hold a {vessel_size} slot in the {n}-week window. Mind if I send an indicative schedule?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the typical parcel size you would consider for a single lift?'\n4. Buyer: gives number\n5. {rep}: 'We can size a parcel to match. Send me the spec.'\n6. Email follow-up.",
"Have a real vessel availability window. The squeeze is real and dated."))

HOOKS.append(H(7, "The Chinese Winter Heating Demand", "Coal",
"Hi {name}, {rep} from ECONARES. Chinese winter heating demand starts in {n} weeks. For thermal coal buyers in {region}, the next {m} weeks are the squeeze window. Has {company} secured the winter tonnage, or is that still open?",
"Chinese winter heating is a real, dated demand event. By naming it, you signal sector awareness. The question reveals the buyer's gap, if any.",
"Chinese winter heating demand is {n} weeks away (typically mid-November start).",
["China NDRC announcements for the heating season start","Trade press for the thermal coal demand","Customs data for the buyer's pre-winter liftings"],
"'Secured. We are covered.'",
"'Still open. What is the offer?'",
"Got it. ECONARES can deliver thermal coal FOB {origin} on a {vessel_size} vessel to land before winter. Mind if I send an indicative window?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the cover target in days before the heating season?'\n4. Buyer: gives number\n5. {rep}: 'Send me the spec and I will line up a parcel to match.'\n6. Email follow-up.",
"Have the actual heating season start date. Buyers track the calendar precisely."))

HOOKS.append(H(7, "The Power Plant Dry-Season Build", "Coal; Diesel; PKS",
"Hi {name}, {rep} from ECONARES. Dry season in {region} is the high-demand window for {commodity} at power plants. Has {company} started the dry-season stockpile build, or is that still on the to-do list?",
"Dry season is a real, dated demand event. By naming it, you signal sector awareness. The question reveals the buyer's gap, if any.",
"Dry season is {n} weeks away in the buyer's region. PH dry season: December\u2013May.",
["PAGASA for the PH dry season forecast","ERC for the power plant's capacity factor","Trade press for the buyer's typical dry-season build"],
"'Started. No gap.'",
"'Still on the to-do list. What is the offer?'",
"Got it. ECONARES can deliver FOB {origin} on a {vessel_size} vessel to land before the peak. Mind if I send an indicative window?",
"1. {rep}: {opening}\n2. Buyer: status update\n3. {rep}: 'What is the typical dry-season parcel size?'\n4. Buyer: gives number\n5. {rep}: 'We can size a parcel to match. Send me the spec.'\n6. Email follow-up.",
"Have the actual dry season start date. Buyers track the calendar precisely."))
# ============ CATEGORY 8: DIRECT QUESTION (13) ============
HOOKS.append(H(8, "The Spec-First Question", "All",
"Hi {name}, {rep} from ECONARES. Quick question \u2014 what is the typical {commodity} spec band {company} runs on the {line} line? I am sizing a market scan and your name came up as a likely benchmark.",
"A spec-led question with no pitch signals expertise. The buyer is forced to engage with their own spec, which surfaces their tolerance and reveals intent.",
"You have a real spec hunch but no other hook. Use as a fallback.",
["Trade press for the buyer's typical spec","Buyer's tender documents for the spec band","Industry forums for the buyer's spec complaints"],
"'{spec_band}. Why?'",
"'We are reviewing. Send your range.'",
"Got it. I will line up an indicative offer against {spec_band} and send it for the file. Mind if I confirm the email?",
"1. {rep}: {opening}\n2. Buyer: spec band\n3. {rep}: 'When is the next tender window?'\n4. Buyer: gives date\n5. {rep}: 'I will time a one-pager to land {weeks} weeks before.'\n6. Email follow-up.",
"Have the spec band ready before the call. Being wrong on the spec is a deal-killer."))

HOOKS.append(H(8, "The Logistics Question", "All",
"Hi {name}, {rep} from ECONARES. Quick question \u2014 what is the typical {commodity} discharge window for {company}? I am trying to size a vessel program and your discharge cadence came up as a benchmark.",
"A logistics question is a soft, low-risk opener. It reveals the buyer's operational cadence without forcing a yes/no commitment.",
"You have a logistics hunch but no other hook. Use as a fallback.",
["Customs data for the buyer's discharge frequency","Trade press for the buyer's typical vessel size","MarineTraffic for the buyer's recent arrivals"],
"'{cadence}. Why?'",
"'We are reviewing. Send your offer.'",
"Got it. I will line up an indicative vessel schedule against {cadence} and send it for the file.",
"1. {rep}: {opening}\n2. Buyer: cadence\n3. {rep}: 'What is the typical vessel size you would consider?'\n4. Buyer: gives number\n5. {rep}: 'We can size the program to match. Send me the spec.'\n6. Email follow-up.",
"Have the discharge cadence ready. Buyers track their own operations precisely."))

HOOKS.append(H(8, "The Payment Terms Question", "All",
"Hi {name}, {rep} from ECONARES. Quick question \u2014 what is {company}'s standard payment terms for {commodity} supply? I am benchmarking the regional market and your policy came up as a reference.",
"Payment terms are a soft, factual question. The buyer's answer reveals their procurement posture and the urgency of working-capital pressure.",
"You have a payment terms hunch but no other hook. Use as a fallback. Skip this hook if the buyer is publicly known to insist on LC at sight \u2014 the question will sound naive.",
["Trade press for the buyer's typical payment terms","Buyer's annual report for working-capital policy","Industry forums for the buyer's payment practices"],
"'Net {n} days. Standard.'",
"'LC at sight. Non-negotiable.'",
"Got it. ECONARES can work within {n} days net or LC at sight. I will line up a one-pager to match.",
"1. {rep}: {opening}\n2. Buyer: terms\n3. {rep}: 'When does the next contract roll over?'\n4. Buyer: gives date\n5. {rep}: 'I will time a one-pager to land {weeks} weeks before.'\n6. Email follow-up.",
"Be careful. This question can sound like a credit check. Lead with 'I am benchmarking the regional market' to soften it."))

HOOKS.append(H(8, "The Volume Question", "All",
"Hi {name}, {rep} from ECONARES. Quick question \u2014 what is the typical {commodity} volume {company} lifts per quarter? I am sizing a market scan and your name came up as a benchmark.",
"A volume question is a soft, factual opener. The buyer's answer reveals their scale and the urgency of supply.",
"You have a volume hunch but no other hook. Use as a fallback.",
["Customs data for the buyer's typical liftings","Buyer's annual report for the volume disclosure","Trade press for the buyer's recent volume changes"],
"'{volume} MT per quarter. Why?'",
"'We are reviewing. Send your offer.'",
"Got it. I will line up an indicative offer against {volume} MT and send it for the file.",
"1. {rep}: {opening}\n2. Buyer: volume\n3. {rep}: 'What is the typical parcel size for a single lift?'\n4. Buyer: gives number\n5. {rep}: 'We can size a parcel to match. Send me the spec.'\n6. Email follow-up.",
"Have the volume ready. Buyers track their own operations precisely."))

HOOKS.append(H(8, "The Incoterms Question", "All",
"Hi {name}, {rep} from ECONARES. Quick question \u2014 what is {company}'s standard incoterms for {commodity} supply? FOB, CIF, or something else? I am benchmarking the regional market and your policy came up as a reference.",
"An incoterms question is a soft, factual opener. The buyer's answer reveals their commercial structure and the urgency of freight exposure.",
"You have an incoterms hunch but no other hook. Use as a fallback.",
["Trade press for the buyer's typical incoterms","Buyer's tender documents for the incoterms clause","Industry forums for the buyer's commercial practices"],
"'FOB. Standard.'",
"'CIF. We control the freight.'",
"Got it. ECONARES can work on FOB or CIF basis. I will line up a one-pager to match.",
"1. {rep}: {opening}\n2. Buyer: incoterms\n3. {rep}: 'What is the typical discharge port?'\n4. Buyer: gives port\n5. {rep}: 'We can size the vessel and freight to match. Send me the spec.'\n6. Email follow-up.",
"Have the incoterms ready. Buyers track their own commercial structure precisely."))
HOOKS.append(H(8, "The Compliance / Permit Question", "All",
"Hi {name}, {rep} from ECONARES. Quick question \u2014 what is {company}'s standard compliance checklist for {commodity} suppliers? I am benchmarking the regional market and your checklist came up as a reference.",
"A compliance question signals that you take documentation seriously. The buyer's answer reveals their hard requirements and the urgency of compliance.",
"Buyer is in a regulated sector (power, smelter, EU export, Japan export). Use as a fallback when no other hook is available.",
["Buyer's tender documents for the compliance checklist","Trade press for the buyer's typical compliance requirements","Industry forums for the buyer's compliance complaints"],
"'We have a {n}-point checklist. Why?'",
"'We are reviewing. Send your offer.'",
"Got it. ECONARES can pre-validate against {n}-point checklist. I will line up a documentation package.",
"1. {rep}: {opening}\n2. Buyer: checklist\n3. {rep}: 'What is the most common documentation gap you see from suppliers?'\n4. Buyer: shares gap\n5. {rep}: 'Send me the checklist and I will pre-validate ECONARES against it before we even talk tonnage.'\n6. Email follow-up with documentation package.",
"Avoid the trap of asking about MGB / DENR / environmental permits in the first call. Lead with the buyer's checklist, not yours."))

HOOKS.append(H(8, "The Vessel Size Question", "All",
"Hi {name}, {rep} from ECONARES. Quick question \u2014 what is the typical vessel size {company} uses for {commodity} liftings? I am sizing a vessel program and your name came up as a benchmark.",
"A vessel size question is a soft, factual opener. The buyer's answer reveals their port capacity and the urgency of supply.",
"You have a vessel size hunch but no other hook. Use as a fallback.",
["Port authority data for the buyer's typical vessel size","MarineTraffic for the buyer's recent arrivals","Trade press for the buyer's typical vessel program"],
"'{size}. Why?'",
"'We are reviewing. Send your offer.'",
"Got it. ECONARES can hold a {size} slot in the next {n}-week window. I will line up an indicative schedule.",
"1. {rep}: {opening}\n2. Buyer: vessel size\n3. {rep}: 'What is the typical discharge port?'\n4. Buyer: gives port\n5. {rep}: 'We can size the parcel and vessel to match. Send me the spec.'\n6. Email follow-up.",
"Have the vessel size ready. Buyers track their own operations precisely."))

HOOKS.append(H(8, "The Trial Shipment Question", "All",
"Hi {name}, {rep} from ECONARES. Quick question \u2014 does {company} ever consider trial shipments from new suppliers on {commodity}? I am benchmarking the regional market and your policy on trials came up as a reference.",
"A trial shipment question is a soft, factual opener. The buyer's answer reveals their procurement posture and the urgency of new-supplier onboarding.",
"You have a trial shipment hunch but no other hook. Use as a fallback.",
["Trade press for the buyer's typical trial policy","Buyer's tender documents for the trial shipment clause","Industry forums for the buyer's trial practices"],
"'Yes, on a {n}-MT basis. Why?'",
"'No, we do not do trials.'",
"Got it. ECONARES can deliver a {n}-MT trial parcel on FOB basis. I will line up a one-pager.",
"1. {rep}: {opening}\n2. Buyer: trial policy\n3. {rep}: 'What is the typical success criterion for a trial?'\n4. Buyer: shares criterion\n5. {rep}: 'Send me the criterion and I will pre-validate ECONARES against it before we even talk tonnage.'\n6. Email follow-up with trial framework.",
"Have a real trial framework ready. Buyers are technical and will test your credibility."))

HOOKS.append(H(8, "The Stockpile Level Question", "All",
"Hi {name}, {rep} from ECONARES. Quick question \u2014 what is {company}'s typical {commodity} stockpile target in days of cover? I am benchmarking the regional market and your policy came up as a reference.",
"A stockpile question is a soft, factual opener. The buyer's answer reveals their risk tolerance and the urgency of supply.",
"You have a stockpile hunch but no other hook. Use as a fallback.",
["Trade press for the buyer's typical stockpile policy","Buyer's annual report for the stockpile disclosure","Industry forums for the buyer's stockpile practices"],
"'{n} days. Why?'",
"'We are reviewing. Send your offer.'",
"Got it. ECONARES can support a {n}-day cover target with a multi-vessel schedule. I will line up a one-pager.",
"1. {rep}: {opening}\n2. Buyer: cover target\n3. {rep}: 'What is the typical parcel size for a top-up?'\n4. Buyer: gives number\n5. {rep}: 'We can size a parcel to match. Send me the spec.'\n6. Email follow-up.",
"Have the cover target ready. Buyers track their own operations precisely."))

HOOKS.append(H(8, "The Current Supplier Question", "All",
"Hi {name}, {rep} from ECONARES. Quick question \u2014 is {company} currently considering any new {commodity} suppliers, or is the book closed? I am benchmarking the regional market and your policy came up as a reference.",
"A direct question on the buyer's openness to new suppliers. The answer reveals their procurement posture and the urgency of new-supplier onboarding.",
"You have no other hook. Use as a last-resort fallback.",
["Trade press for the buyer's typical supplier policy","Buyer's annual report for the supplier disclosure","Industry forums for the buyer's supplier practices"],
"'Yes, we are reviewing. Send your offer.'",
"'No, the book is closed.'",
"Got it. ECONARES can deliver FOB {origin} with pre-shipment lab cert per lot. I will line up a one-pager for the file.",
"1. {rep}: {opening}\n2. Buyer: openness\n3. {rep}: 'When does the next supplier review open up?'\n4. Buyer: gives date\n5. {rep}: 'I will time a one-pager to land {weeks} weeks before.'\n6. Calendar reminder set.",
"Use sparingly. The question is direct and can sound like a generic cold-call. Lead with a sector observation to soften it."))

HOOKS.append(H(8, "The Quality Complaint Question", "All",
"Hi {name}, {rep} from ECONARES. Quick question \u2014 what is the most common quality complaint {company} has on {commodity} right now? I am benchmarking the regional market and your team's voice came up as a reference.",
"A quality complaint question signals you care about the buyer's pain. The answer reveals their tolerance and the urgency of supply.",
"You have a quality hunch but no other hook. Use as a fallback.",
["Trade press for the buyer's typical quality complaints","Buyer's tender documents for the quality clauses","Industry forums for the buyer's quality practices"],
"'{complaint}. Why?'",
"'We are reviewing. Send your offer.'",
"Got it. ECONARES runs pre-shipment lab cert per lot to mitigate {complaint}. I will line up a one-pager.",
"1. {rep}: {opening}\n2. Buyer: complaint\n3. {rep}: 'What is the typical cost impact on your operations?'\n4. Buyer: gives figure\n5. {rep}: 'Send me the spec and I will line up a {commodity} that fits.'\n6. Email follow-up with lab cert template.",
"Have a real lab cert sample. Buyers are technical and will test your credibility."))

HOOKS.append(H(8, "The Future Demand Question", "All",
"Hi {name}, {rep} from ECONARES. Quick question \u2014 what is {company}'s projected {commodity} demand over the next {n} quarters? I am sizing a market scan and your forecast came up as a benchmark.",
"A future demand question signals you are thinking long-term. The buyer's answer reveals their growth trajectory and the urgency of supply.",
"You have a demand hunch but no other hook. Use as a fallback.",
["Trade press for the buyer's typical demand growth","Buyer's annual report for the demand forecast","Industry forums for the buyer's demand practices"],
"'{volume} MT per quarter. Why?'",
"'We are reviewing. Send your offer.'",
"Got it. ECONARES can support the projected demand with a multi-vessel schedule. I will line up a one-pager.",
"1. {rep}: {opening}\n2. Buyer: demand projection\n3. {rep}: 'What is the typical parcel size for a top-up?'\n4. Buyer: gives number\n5. {rep}: 'We can size a parcel to match. Send me the spec.'\n6. Email follow-up.",
"Have the demand projection ready. Buyers track their own forecasts precisely."))

HOOKS.append(H(8, "The Decision-Maker Question", "All",
"Hi {name}, {rep} from ECONARES. Quick question \u2014 who ultimately signs off on a {commodity} supplier decision at {company}? I am benchmarking the regional market and the typical org chart came up as a reference.",
"A decision-maker question is a soft, factual opener. The buyer's answer reveals the org chart and the urgency of supply.",
"You have no other hook. Use as a last-resort fallback to map the org.",
["LinkedIn for the buyer's org chart","Buyer's annual report for the leadership team","Trade press for the buyer's recent leadership changes"],
"'{name}. Why?'",
"'We are reviewing. Send your offer.'",
"Got it. ECONARES can line up a one-pager for {decision_maker}. I will route it directly.",
"1. {rep}: {opening}\n2. Buyer: decision maker\n3. {rep}: 'When is the next supplier review window?'\n4. Buyer: gives date\n5. {rep}: 'I will time a one-pager to land {weeks} weeks before.'\n6. Calendar reminder set.",
"Use this hook sparingly. Asking for the decision-maker can sound like a generic cold-call. Lead with a sector observation to soften it."))

# ============================================================================
# HTML RENDERER
# ============================================================================

def esc(s):
    return html_lib.escape(str(s), quote=True)

def render_hook(hook, index):
    """Render a single hook as HTML."""
    research_items = "".join(f"<li>{esc(r)}</li>" for r in hook["research"])
    flow_lines = hook["flow"].split("\n")
    flow_html = "\n".join(f"<div class='flow-line'>{esc(line)}</div>" for line in flow_lines)
    comm_html = ", ".join(esc(c) for c in hook["comm"].split("; "))

    return f"""
<div class="hook" id="hook-{index}">
    <div class="hook-header">
        <span class="hook-num">#{index:02d}</span>
        <h2 class="hook-title">{esc(hook['title'])}</h2>
        <div class="hook-commodities"><em>Applies to:</em> {comm_html}</div>
    </div>

    <div class="hook-section">
        <h3>Opening Line</h3>
        <blockquote class="opening">{esc(hook['opening'])}</blockquote>
    </div>

    <div class="hook-section">
        <h3>Why It Works</h3>
        <p>{esc(hook['why'])}</p>
    </div>

    <div class="hook-section">
        <h3>When To Use It</h3>
        <p>{esc(hook['when'])}</p>
    </div>

    <div class="hook-section">
        <h3>Research Required</h3>
        <ul>{research_items}</ul>
    </div>

    <div class="hook-section two-col">
        <div>
            <h3>Likely Response A</h3>
            <blockquote class="response">{esc(hook['a'])}</blockquote>
        </div>
        <div>
            <h3>Likely Response B</h3>
            <blockquote class="response">{esc(hook['b'])}</blockquote>
        </div>
    </div>

    <div class="hook-section">
        <h3>Natural Follow-Up</h3>
        <p class="follow-up">{esc(hook['follow'])}</p>
    </div>

    <div class="hook-section">
        <h3>60-90 Second Call Flow</h3>
        <div class="flow">{flow_html}</div>
    </div>

    <div class="hook-section">
        <h3>Customize Note</h3>
        <p class="customize"><em>{esc(hook['customize'])}</em></p>
    </div>
</div>
"""

def render_category(cat, hooks_in_cat, start_index):
    cat_num = cat["id"]
    total = len(hooks_in_cat)
    rendered_hooks = "".join(render_hook(h, start_index + i) for i, h in enumerate(hooks_in_cat))
    return f"""
<div class="category-header" id="cat-{cat_num}">
    <div class="cat-num">CATEGORY {cat_num} OF 8</div>
    <h1 class="cat-title">{esc(cat['title'])}</h1>
    <p class="cat-subtitle">{esc(cat['subtitle'])}</p>
    <div class="cat-count">{total} hooks &middot; Hooks #{start_index:02d} &ndash; #{start_index + total - 1:02d}</div>
    <p class="cat-intro">{esc(cat['intro'])}</p>
</div>
{rendered_hooks}
"""

def render_toc(cat_index):
    items = []
    for cat in CATEGORIES:
        h_count = cat_index[cat["id"]]
        items.append(
            f"<li><a href='#cat-{cat['id']}'>Category {cat['id']}: {esc(cat['title'])}</a> "
            f"<span class='toc-count'>({h_count} hooks)</span></li>"
        )
    return "<ul class='toc-list'>\n" + "\n".join(items) + "\n</ul>"

def build_html():
    # Group hooks by category, track starting index
    by_cat = {c["id"]: [] for c in CATEGORIES}
    for h in HOOKS:
        by_cat[h["cat"]].append(h)
    cat_index = {c["id"]: len(by_cat[c["id"]]) for c in CATEGORIES}

    # Build per-category index
    start = {}
    running = 1
    for c in CATEGORIES:
        start[c["id"]] = running
        running += cat_index[c["id"]]

    # Render TOC
    toc = render_toc(cat_index)

    # Render each category
    cat_blocks = []
    for c in CATEGORIES:
        cat_blocks.append(render_category(c, by_cat[c["id"]], start[c["id"]]))
    cat_html = "\n".join(cat_blocks)

    # Compose full document
    today = datetime.now().strftime("%B %Y")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>75 Cold Call Hooks That Don't Sound Like Cold Calls \u2014 The Commodity Trading Edition</title>
<style>
@page {{
    size: A4;
    margin: 22mm 18mm 22mm 18mm;
    @bottom-center {{
        content: "Page " counter(page) " of " counter(pages) "  \u2014  ECONARES  \u2014  Commodity Trading Edition";
        font-family: Georgia, serif;
        font-size: 9pt;
        color: #888;
    }}
    @top-left {{
        content: "ECONARES";
        font-family: Georgia, serif;
        font-size: 9pt;
        color: #888;
        letter-spacing: 0.1em;
    }}
}}

* {{ box-sizing: border-box; }}

body {{
    font-family: Georgia, 'Times New Roman', serif;
    color: #1a1a1a;
    line-height: 1.55;
    margin: 0;
    padding: 0;
    background: #fff;
    font-size: 11pt;
}}

/* COVER */
.cover {{
    height: 100vh;
    text-align: center;
    padding-top: 18%;
    page-break-after: always;
    background: linear-gradient(180deg, #ffffff 0%, #f6f4ef 100%);
}}
.cover-eyebrow {{
    font-size: 11pt;
    letter-spacing: 0.4em;
    color: #8a6f3a;
    font-weight: bold;
    text-transform: uppercase;
    margin-bottom: 28px;
}}
.cover-title {{
    font-size: 38pt;
    line-height: 1.1;
    color: #1a1a1a;
    margin: 0 0 12px 0;
    font-weight: bold;
}}
.cover-subtitle {{
    font-size: 16pt;
    line-height: 1.4;
    color: #444;
    font-style: italic;
    margin: 16px auto 36px auto;
    max-width: 480px;
}}
.cover-meta {{
    margin-top: 60px;
    font-size: 11pt;
    color: #555;
    line-height: 1.7;
}}
.cover-brand {{
    font-size: 14pt;
    color: #1a1a1a;
    font-weight: bold;
    letter-spacing: 0.2em;
    margin-top: 24px;
}}
.cover-rule {{
    width: 60px;
    height: 2px;
    background: #8a6f3a;
    margin: 36px auto 24px auto;
}}

/* DEDICATION / FRONT MATTER */
.front-matter {{
    page-break-after: always;
    padding-top: 30px;
}}
.front-matter h1 {{
    font-size: 22pt;
    color: #1a1a1a;
    margin-bottom: 16px;
    border-bottom: 2px solid #8a6f3a;
    padding-bottom: 8px;
}}
.front-matter p {{
    font-size: 11.5pt;
    line-height: 1.7;
    margin-bottom: 14px;
}}
.important-note {{
    background: #faf6ec;
    border-left: 4px solid #8a6f3a;
    padding: 16px 20px;
    margin: 24px 0;
    font-style: italic;
}}

/* TOC */
.toc-page {{
    page-break-after: always;
}}
.toc-page h1 {{
    font-size: 22pt;
    color: #1a1a1a;
    margin-bottom: 20px;
    border-bottom: 2px solid #8a6f3a;
    padding-bottom: 8px;
}}
.toc-list {{
    list-style: none;
    padding: 0;
    margin: 0;
}}
.toc-list li {{
    font-size: 12pt;
    padding: 10px 0;
    border-bottom: 1px dotted #bbb;
}}
.toc-list li a {{
    color: #1a1a1a;
    text-decoration: none;
    font-weight: bold;
}}
.toc-list li a:hover {{
    color: #8a6f3a;
}}
.toc-count {{
    color: #777;
    font-weight: normal;
    font-size: 10.5pt;
    margin-left: 8px;
}}
.toc-quick-jump {{
    margin-top: 32px;
    background: #f6f4ef;
    padding: 18px 22px;
    border-radius: 4px;
}}
.toc-quick-jump h3 {{
    margin: 0 0 10px 0;
    font-size: 12pt;
    color: #1a1a1a;
}}
.toc-quick-jump p {{
    font-size: 10.5pt;
    line-height: 1.6;
    margin: 6px 0;
    color: #444;
}}

/* CATEGORY HEADERS */
.category-header {{
    page-break-before: always;
    padding: 32px 0 24px 0;
    border-bottom: 3px solid #8a6f3a;
    margin-bottom: 30px;
}}
.cat-num {{
    font-size: 10pt;
    letter-spacing: 0.35em;
    color: #8a6f3a;
    font-weight: bold;
    margin-bottom: 8px;
}}
.cat-title {{
    font-size: 26pt;
    color: #1a1a1a;
    margin: 6px 0 8px 0;
    line-height: 1.15;
}}
.cat-subtitle {{
    font-size: 13pt;
    color: #555;
    font-style: italic;
    margin: 0 0 14px 0;
    line-height: 1.4;
}}
.cat-count {{
    font-size: 10.5pt;
    color: #8a6f3a;
    font-weight: bold;
    letter-spacing: 0.05em;
    margin-bottom: 18px;
}}
.cat-intro {{
    font-size: 11.5pt;
    line-height: 1.65;
    color: #333;
    margin: 16px 0 0 0;
}}

/* HOOK BLOCKS */
.hook {{
    page-break-inside: avoid;
    margin-bottom: 38px;
    padding: 18px 0;
    border-bottom: 1px solid #e6e1d4;
}}
.hook:last-child {{
    border-bottom: none;
}}
.hook-header {{
    margin-bottom: 14px;
}}
.hook-num {{
    display: inline-block;
    background: #8a6f3a;
    color: white;
    font-weight: bold;
    padding: 3px 12px;
    border-radius: 3px;
    font-size: 10pt;
    letter-spacing: 0.1em;
    margin-right: 10px;
}}
.hook-title {{
    display: inline;
    font-size: 16pt;
    color: #1a1a1a;
    margin: 0;
    line-height: 1.2;
}}
.hook-commodities {{
    font-size: 10pt;
    color: #666;
    margin-top: 6px;
    margin-left: 4px;
}}
.hook-section {{
    margin: 14px 0;
}}
.hook-section h3 {{
    font-size: 10.5pt;
    color: #8a6f3a;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 0 0 6px 0;
    font-weight: bold;
}}
.hook-section.two-col {{
    display: table;
    width: 100%;
    table-layout: fixed;
    border-spacing: 12px 0;
}}
.hook-section.two-col > div {{
    display: table-cell;
    vertical-align: top;
    width: 50%;
}}
.opening {{
    background: #f6f4ef;
    border-left: 4px solid #8a6f3a;
    padding: 14px 18px;
    margin: 0;
    font-size: 12pt;
    line-height: 1.55;
    font-style: italic;
}}
.response {{
    background: #fafafa;
    border-left: 3px solid #ccc;
    padding: 10px 14px;
    margin: 0;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #333;
}}
.follow-up {{
    background: #faf6ec;
    padding: 10px 14px;
    margin: 0;
    font-size: 11pt;
    line-height: 1.55;
    border-radius: 3px;
}}
.flow {{
    background: #f9f8f5;
    padding: 12px 16px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 9.5pt;
    line-height: 1.55;
    color: #2a2a2a;
}}
.flow-line {{
    margin: 3px 0;
    white-space: pre-wrap;
}}
.customize {{
    font-size: 10.5pt;
    line-height: 1.55;
    color: #555;
    margin: 0;
}}
ul {{
    margin: 4px 0;
    padding-left: 22px;
}}
ul li {{
    margin: 4px 0;
    font-size: 10.5pt;
    line-height: 1.5;
}}

/* BACK MATTER */
.back-matter {{
    page-break-before: always;
    padding-top: 30px;
}}
.back-matter h1 {{
    font-size: 22pt;
    color: #1a1a1a;
    margin-bottom: 16px;
    border-bottom: 2px solid #8a6f3a;
    padding-bottom: 8px;
}}
.back-matter h2 {{
    font-size: 14pt;
    color: #1a1a1a;
    margin-top: 24px;
    margin-bottom: 10px;
}}
.back-matter p {{
    font-size: 11pt;
    line-height: 1.65;
    margin-bottom: 12px;
}}
.back-matter ul {{
    margin: 8px 0 16px 0;
}}
</style>
</head>
<body>

<div class="cover">
    <div class="cover-eyebrow">75 Hooks \u00b7 8 Categories \u00b7 Commodity Trading</div>
    <h1 class="cover-title">75 Cold Call Hooks<br>That Don't Sound<br>Like Cold Calls</h1>
    <div class="cover-rule"></div>
    <p class="cover-subtitle">The physical commodity trading edition \u2014 a strategic system for account executives, traders, and sales managers selling nickel ore, copper concentrate, coal, diesel, PKS, woodchips, and CPO.</p>
    <div class="cover-meta">
        {today}<br>
        <span class="cover-brand">ECONARES</span><br>
        Cebu, Philippines
    </div>
</div>

<div class="front-matter">
    <h1>Important Note Before You Use This Book</h1>
    <p>These are not scripts to copy and paste. They are proven frameworks designed to spark real conversations. Every prospect, situation, tone of voice, and context is different. Always customize the hook with specific research about the person and company you are calling. The goal is to sound like a sharp, helpful trader, not a robot reading lines.</p>
    <p>Prospect responses will always be unpredictable, so use these as your starting point, then listen, adapt, and flow naturally from there. The single biggest mistake a commodity sales professional can make is to deliver a hook like a script. The second biggest mistake is to walk in with no hook at all.</p>

    <div class="important-note">
        <strong>The ECONARES Mindset.</strong> Silence is strategy. Never reveal pricing in the first contact. Never mention MGB or DENR compliance details in the opening \u2014 keep the first message focused on volume, chemical specifications, and availability to gauge interest. The 50% down payment / FOB-only / entire-Philippines supply policy is a closing tool, not an opening one. Use it when the buyer has confirmed a spec match, not before.
    </div>

    <p>Each of the 75 hooks in this book is built around a single psychological principle: <strong>the buyer is far more interested in their own problem than in your product</strong>. The hook earns the next 30 seconds by naming something the buyer already knows but has not yet been asked about. After that, the call is a conversation, not a pitch.</p>

    <h1>How To Use This Book</h1>
    <p><strong>1. Pick the category that matches the buyer's situation.</strong> The eight categories are organized by the buyer's most likely current state \u2014 not by your product, and not by your sales cycle. Read the section intros to find the right fit.</p>
    <p><strong>2. Read the entire hook \u2014 not just the opening line.</strong> Every hook comes with the research required, two realistic response scenarios, a natural follow-up, and a 60\u201390 second call flow. The opening line is 10% of the work. The follow-up is 80%.</p>
    <p><strong>3. Customize the placeholders before you dial.</strong> Every bracketed placeholder ({'{name}'}, {'{company}'}, {'{plant}'}, {'{commodity}'}) must be replaced with a real, verified, citable fact. Buyers can tell the difference in five seconds.</p>
    <p><strong>4. Track what works.</strong> After every call, log which hook you used, the buyer's response pattern, and the next step. The first ten calls are calibration. The next hundred are compounding.</p>
</div>

<div class="toc-page">
    <h1>Table of Contents</h1>
    {toc}
    <div class="toc-quick-jump">
        <h3>How to navigate this book</h3>
        <p>If you have a buyer in mind, jump to the category that matches their current situation \u2014 are they reviewing a recent plant change, a recent news event, an industry shift, or just a routine quarterly call?</p>
        <p>If you do not have a buyer in mind, start with the Direct Question Hooks (Category 8) \u2014 they are the lowest-risk way to open a cold call and force the buyer to engage with their own situation.</p>
        <p>If you are calling on a high-value target, study the Recent News Hooks (Category 3) and the Industry Challenge Hooks (Category 4) first \u2014 they take more research but they earn the most attention.</p>
    </div>
</div>

{cat_html}

<div class="back-matter">
    <h1>Advanced Techniques</h1>
    <p>These 75 hooks are the foundation. The following techniques compound on top of them. Use them to convert a hook into a booked meeting, and a meeting into a long-term supply relationship.</p>

    <h2>1. The First Five Seconds</h2>
    <p>The buyer's first impression is set in the first five seconds of the call. Tone, pace, and confidence matter more than the words. Speak at the buyer's pace, not yours. Pause before the hook to signal that you have something specific to say. Do not apologize for calling. Do not ask if it is a good time \u2014 ask a question that makes time irrelevant.</p>

    <h2>2. The Follow-Up Frame</h2>
    <p>The follow-up is where most commodity sales calls die. The buyer gives a soft answer, and the salesperson either pitches harder or hangs up. Neither works. Instead, use the follow-up frame: <em>acknowledge \u2192 label \u2192 redirect</em>. Acknowledge what the buyer said. Label the underlying need ("it sounds like consistency is the real issue"). Redirect to a next step ("send me a recent failed-lot report and I will tell you straight whether we can hit it").</p>

    <h2>3. The Inquiry-First Posture</h2>
    <p>Before you propose anything, understand the buyer's full requirements: specs, volume, destination port, incoterms, payment terms, vessel size, discharge window. Never quote price until every variable is known. The buyer is not buying a price \u2014 they are buying certainty. Inquiry-first posture signals you are the supplier who actually understands the deal.</p>

    <h2>4. The One-Pager That Sells The Meeting</h2>
    <p>If the hook earns a soft yes, your one-pager earns the meeting. A commodity one-pager is not a brochure. It is six lines: origin, spec band, FOB basis, vessel size, lab certification, contact. Send it within an hour of the call. Buyers forget conversations \u2014 they do not forget one-pagers that arrive fast.</p>

    <h2>5. The CRM Discipline</h2>
    <p>Every hook used, every response heard, every follow-up sent must be logged in the same day. Include: hook category, hook number, buyer's exact words, next step, follow-up date. The pattern emerges after 30 calls. By call 100, the patterns are obvious. The top 10% of commodity sales professionals are not naturally better \u2014 they are systematically tracking.</p>

    <h2>6. The Multi-Channel Sequence</h2>
    <p>The hook is the cold call. The follow-up is the email. The reminder is the WhatsApp. The closer is the LinkedIn. The four-channel sequence is the standard for commodity sales in 2026. Most buyers respond on channel two or three, not channel one. The salesperson who only calls never hears back. The salesperson who calls, emails, and messages \u2014 books the meeting.</p>

    <h2>7. The Tone Calibration</h2>
    <p>Match the buyer's tone. If they are technical, be technical. If they are warm, be warm. If they are rushed, be brief. The single biggest tell of an inexperienced commodity sales professional is a tone that does not match the buyer's. Listen to the buyer's first ten words. Mirror their pace, formality, and energy. They will not notice you are doing it. They will notice you are easy to talk to.</p>

    <h2>8. The Objection Map</h2>
    <p>Five objections cover 90% of commodity sales calls. "We are covered." "Send a one-pager." "Not interested." "Call me next quarter." "Your price is too high." Each has a specific reframe. "We are covered" \u2192 "Got it. Worth knowing anyway. If a backup option ever helps, I will be on file." "Send a one-pager" \u2192 "Will do today. What is the cleanest email?" "Not interested" \u2192 "Understood. Mind if I ask one quick question first \u2014 is it timing, or is it the incumbent?" Map your own objections. Practice the reframes until they are muscle memory.</p>

    <h1>About ECONARES</h1>
    <p>ECONARES is a Cebu-based physical commodity trading and logistics company, with field sales coverage across the Visayas and Mindanao. The company sources and supplies nickel ore, copper concentrate, coal, diesel (10ppm gasoil), palm kernel shells (PKS), and related bulk commodities to domestic Philippine buyers and to Chinese and Japanese offtakers.</p>
    <p>Operating principles: FOB origin supply. 50% down payment. Coverage of the entire Philippines. Chain-of-custody documentation per lot. Pre-shipment lab certification. Inquiry-first engagement on every first contact.</p>
    <p>This book is a working tool, not a finished product. It will be updated as new hooks are tested and validated in the field. The next edition will add hooks for nickel-cobalt blends, electric arc furnace (EAF) feedstock, and sustainable aviation fuel (SAF) precursor supply \u2014 categories that are emerging as the PH commodity market matures into 2027.</p>

    <h1>Contact</h1>
    <p>For questions, custom hook requests, or bulk licensing of this framework for your own sales team, contact:</p>
    <p><strong>ECONARES</strong><br>
    G/F BT&amp;T Bldg. Hollowblock Rd. Tabunok<br>
    Talisay City, Cebu, Philippines<br>
    rzh24.econares@gmail.com<br>
    +63 927 872 5194 (Mobile \u00b7 WhatsApp \u00b7 Telegram \u00b7 WeChat \u00b7 Viber)<br>
    (+63) 32 232 6280 (Landline)</p>

    <h1>Fulfillment &amp; Use Policy</h1>
    <p>This ebook is a digital product. No physical items will be shipped. The framework is shared freely with the PH and APAC commodity trading community. Internal use within a single sales organization is permitted. Redistribution of the full text outside of ECONARES requires written permission. Quoting individual hooks in sales training or client conversations is encouraged \u2014 that is exactly what the framework is for.</p>
</div>

</body>
</html>
"""
    return html


if __name__ == "__main__":
    # Validate hook count and category distribution
    expected = {1: 7, 2: 10, 3: 10, 4: 10, 5: 5, 6: 10, 7: 10, 8: 13}
    counts = {c["id"]: 0 for c in CATEGORIES}
    for h in HOOKS:
        counts[h["cat"]] += 1
    total = sum(counts.values())
    print(f"Hook count: {total}")
    for c in CATEGORIES:
        exp = expected[c["id"]]
        actual = counts[c["id"]]
        flag = "OK" if actual == exp else "MISMATCH"
        print(f"  Cat {c['id']:>1} ({c['title'][:42]:42}): {actual:>2}/{exp} [{flag}]")
    assert total == 75, f"Expected 75, got {total}"
    for c in CATEGORIES:
        assert counts[c["id"]] == expected[c["id"]], f"Cat {c['id']} mismatch"

    # Build HTML
    html = build_html()
    html_path = "/home/mauiclaw/EBOOK_COMMODITY/ebook.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nHTML written: {html_path} ({len(html):,} chars)")

    # Build PDF
    pdf_path = "/home/mauiclaw/EBOOK_COMMODITY/ebook.pdf"
    from weasyprint import HTML
    doc = HTML(string=html, base_url="/home/mauiclaw/EBOOK_COMMODITY/")
    doc.write_pdf(pdf_path)
    import os
    size = os.path.getsize(pdf_path)
    print(f"PDF written: {pdf_path} ({size:,} bytes / {size/1024:.1f} KB)")

    print("\nDONE.")
