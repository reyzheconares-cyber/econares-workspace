# Zettelkasten Method — ECONARES Adaptation

> Adapted from Niklas Luhmann's card-box system. The goal: build a **second brain** that thinks with you — connecting ideas across commodities, buyers, and markets.

---

## Core Principles

### 1. Atomic Notes
One idea per note. Not "everything about nickel." Not "coal report." One discrete insight.

**Good:** "Limonite ore with >48% Fe is priced at a discount because HPAL smelters penalize high iron content"
**Bad:** "Nickel ore specs and market overview"

### 2. Unique IDs
Every permanent note gets a unique ID for linking.

**Format:** `YYYYMMDDXXX` — date + sequence number
**Example:** `2026042001`, `2026042002`

### 3. Explicit Links
Notes must link to other notes using `[[wikilinks]]`.

- "This connects to [[2026042001]] because..."
- "See also: [[Buyer_Intelligence/econares_target_list_china_nickel_buyers]]"

### 4. Your Own Words
Never copy-paste. Always rephrase in your own language.

---

## Three Note Types

### A. Fleeting Note (Inbox)
Raw, quick capture. Brain dump. Ignorable later.
- Goes in `0 Inbox/`
- Template in `0 Inbox/INDEX.md`

### B. Literature Note (Source-based)
What you learned from a specific source.
- Goes in `3_Resources/Market_Intelligence/` or relevant commodity folder
- Reference the source explicitly

### C. Permanent Note (Idea-based)
**This is the Zettelkasten.** Your original thought, written in your own words.

---

## Permanent Note Template

```markdown
# [Title — atomic insight or claim]

**ID:** [[YYYYMMDDXX]]
**Date:** [[{{date}}]]
**Tags:** #nickel #pricing #china

## Insight

[One paragraph. Your original thought. In your words.]

## Source

[If derived from reading — who said it and when.
If from a call — who, when, what commodity.]

## Connected Notes

- [[YYYYMMDDXX]] — [why this connects]
- [[../Buyer_Intelligence/buyer-name]] — [context]

## Action (if any)

[Should you do something with this? Or just store it?]
```

---

## How to Write a Permanent Note — Step by Step

1. **Capture** → Something in inbox or an observation from research
2. **Process** → Ask: Is this new? Does it contradict something I have?
3. **Write** → One atomic idea. Use the template above.
4. **Link** → Add `[[wikilinks]]` to at least 2 existing notes
5. **Tag** → Add commodity and topic tags
6. **Discard or Store** → If it's reference material, file in Resources

---

## Linking Example

**Note 2026042001:**
> "TSINGSHAN GROUP is the world's largest NPI producer, with a 40% share of China's Ni ore imports."
> `[[Buyer_Intelligence/econares_target_list_china_nickel_buyers]]`

**Note 2026042002:**
> "Indonesian ore export ban (2020, re-imposed 2025) pushes CN buyers to Philippines for limonite supply."
> Links to [[2026042001]] (TSINGSHAN context) + [[../Product_Specs/econares_spec_sheet_limonite_nickel]]

Over time, a web of linked notes becomes a map of how the industry works — not just a collection of facts.

---

## ECONARES-Specific Rules

- **Market observations** → Market_Intelligence folder
- **Buyer insights** → Buyer_Intelligence folder
- **Price findings** → Operating_System (pricing_matrix or new atomic note)
- **Deal lessons** → Project folder retrospective
- **SOP changes** → Operating_System (update the SOP note)

---

## The Test

Before finishing a note, ask:
> *"If I read this note in 6 months with no context, would I understand it?"*

If no — rewrite it. Be specific. Include the why.

---

**Tags:** #methodology #Zettelkasten #note-taking
**Created:** April 20, 2026
