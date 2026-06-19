"""
ECONARES Task Subject Standard
================================
Canonical format for HubSpot task subjects. Adopt this to prevent the
"follow up with X" fragmentation pattern that splits one contact
follow-up cadence across multiple visual clusters.

CANONICAL FORMAT
----------------
    <Action>: <Contact or Company> | <Reason or Stage>

Examples (good)
---------------
    Follow up: Liza Sigua | Q2 reply
    Follow up: San Miguel Global Power | Q2 reply
    Call: Cynthia Cabrera | CoA request
    Email: Andy Sebastian | Toledo next steps
    Research: Durano Paper/Sugar | KYC identity verification
    Outreach: Zhejiang Huayou Cobalt | Day 1 email

Examples (bad — current state, before standardization)
------------------------------------------------------
    follow up with liza sigua
    Follow up with San Miguel Global Power
    Follow up with San Miguel Global Power Holdings Corporation
    follow up with san miguel global power
    FOLLOW UP Allan Saquilayan - Republic Cement
    Outreach - Zhejiang Huayou Cobalt Co. Ltd. | Day 1 Email

The bad ones collapse into the good ones when grouped by normalized
contact name. Two visual clusters for the same contact (one
"san miguel global power" and one "san miguel global power holdings
corporation") is exactly the fragmentation this standard prevents.

WHY PIPE-DELIMITER
-----------------
- Visually scannable in the HubSpot list view (subject truncates at ~80 chars)
- Splits cleanly on the pipe for the audit "same contact" grouping
- Pairs naturally with econares-task-cli style commands later
- Plays well with mobile / Outlook / Gmail preview rendering

RULES
-----
1. Action verb first, Title Case. Standard verbs:
     Follow up | Call | Email | SMS | WhatsApp | Outreach | Research
2. Contact or company name, as filed in the CRM (or close to it).
3. Pipe character, then reason or stage. Optional but recommended.
4. NEVER use the contact name in BOTH sides of the pipe.
   Bad:  Follow up: Rose Calba | Rose Calba follow-up
   Good: Follow up: Rose Calba | Q2 reply
5. For Gmail-star sync tasks: keep the Gmail-star prefix the sync adds.
   It already produces a consistent subject.
"""

import re

# Standard action verbs (Title Case, for new tasks)
ACTION_VERBS = (
    "Follow up",
    "Call",
    "Email",
    "SMS",
    "WhatsApp",
    "Outreach",
    "Research",
    "Meeting",
    "Note",
    "Review",
)

# Contact / company name canonicalization map.
# When the OLD form appears in a task subject, the MIGRATION step will
# rewrite it to the NEW form. Keys are normalized (lowercase, no suffix).
# This handles the "San Miguel Global Power" vs "... Holdings Corporation"
# fragmentation case and similar variants.
CANONICAL_NAMES = {
    # already migrated (after the Jun 18 2026 audit)
    "san miguel global power": "San Miguel Global Power",
    "san miguel global power holdings corporation": "San Miguel Global Power",
    "smc global power": "San Miguel Global Power",
    "smc global power holdings": "San Miguel Global Power",
    "smc global power holdings corporation": "San Miguel Global Power",
    "smcgp": "San Miguel Global Power",
    # other contacts likely to need this - add as you encounter
    "republic cement": "Republic Cement",
    "mgen": "Meralco PowerGen",
    "meralco powergen": "Meralco PowerGen",
    "team energy": "TeaM Energy",
}


def canonical_name(name_or_phrase):
    """Return the canonical display form of a contact or company name.
    Lookup is case-insensitive on the normalized (lower, stripped) form."""
    if not name_or_phrase:
        return name_or_phrase
    norm = name_or_phrase.strip().lower()
    norm = norm.rstrip(".")  # drop trailing periods
    return CANONICAL_NAMES.get(norm, name_or_phrase.strip())


def normalize_existing_subject(s):
    """Normalize a CURRENT (pre-standard) subject into the canonical format.
    Returns the new subject, or `s` unchanged if no migration is needed.

    Handles the recurring patterns from the Jun 18 audit:
      - "follow up with <name>" -> "Follow up: <Name> | <reason>"
      - "Follow up - <name> | <reason>" -> "Follow up: <Name> | <reason>"
      - "FOLLOW UP <name> ..." -> "Follow up: <Name> | <reason>"
      - "Outreach - <company> | <reason>" -> "Outreach: <Company> | <reason>"
      - "Research <name> - <reason>" -> "Research: <Name> | <reason>"
      - "MTG CONFIRMED: <name> - <date>" -> "Meeting: <Name> | <date>"
    """
    if not s:
        return s
    s = s.strip()

    # Gmail-star sync: leave alone (sync adds the prefix)
    if s.startswith("[Gmail"):
        return s

    # 1. FOLLOW UP WITH / FOLLOW UP - <name>[ - reason]
    # Also handles "FOLLOW UP on <X>" and "FOLLOW UP <X>".
    m = re.match(
        r"^follow[\s-]*up\s+(?:with|—|-|on)\s+(.+)$",
        s, flags=re.IGNORECASE,
    )
    if m:
        rest = m.group(1).strip()
        # split on last separator (en/em dash, pipe, hyphen) to get name + reason
        split = re.search(r"\s+[—\-|]\s+", rest)
        if split:
            name = canonical_name(rest[:split.start()].strip())
            reason = rest[split.end():].strip()
            return f"Follow up: {name} | {reason}"
        name = canonical_name(rest)
        return f"Follow up: {name}"

    # 2. FOLLOW UP X (no "with")
    m = re.match(
        r"^follow[\s-]*up\s+(.+)$",
        s, flags=re.IGNORECASE,
    )
    if m:
        rest = m.group(1).strip()
        split = re.search(r"\s+[—\-|]\s+", rest)
        if split:
            name = canonical_name(rest[:split.start()].strip())
            reason = rest[split.end():].strip()
            return f"Follow up: {name} | {reason}"
        name = canonical_name(rest)
        return f"Follow up: {name}"

    # 3. CALL X - reason
    m = re.match(r"^call\s+(.+)$", s, flags=re.IGNORECASE)
    if m:
        rest = m.group(1).strip()
        split = re.search(r"\s+[—\-|]\s+", rest)
        if split:
            name = canonical_name(rest[:split.start()].strip())
            reason = rest[split.end():].strip()
            return f"Call: {name} | {reason}"
        return f"Call: {canonical_name(rest)}"

    # 4. EMAIL X - reason
    m = re.match(r"^email\s+(.+)$", s, flags=re.IGNORECASE)
    if m:
        rest = m.group(1).strip()
        split = re.search(r"\s+[—\-|]\s+", rest)
        if split:
            name = canonical_name(rest[:split.start()].strip())
            reason = rest[split.end():].strip()
            return f"Email: {name} | {reason}"
        return f"Email: {canonical_name(rest)}"

    # 5. OUTREACH - X | reason
    m = re.match(r"^outreach\s*[—\-]\s*(.+)$", s, flags=re.IGNORECASE)
    if m:
        rest = m.group(1).strip()
        split = re.search(r"\s+[—\-|]\s+", rest)
        if split:
            name = canonical_name(rest[:split.start()].strip())
            reason = rest[split.end():].strip()
            return f"Outreach: {name} | {reason}"
        return f"Outreach: {canonical_name(rest)}"

    # 6. RESEARCH X - reason
    m = re.match(r"^research\s+(.+)$", s, flags=re.IGNORECASE)
    if m:
        rest = m.group(1).strip()
        split = re.search(r"\s+[—\-|]\s+", rest)
        if split:
            name = canonical_name(rest[:split.start()].strip())
            reason = rest[split.end():].strip()
            return f"Research: {name} | {reason}"
        return f"Research: {canonical_name(rest)}"

    # 7. MTG CONFIRMED: X - date
    m = re.match(r"^(?:mtg confirmed|meeting)\s*[:\-]\s*(.+)$", s, flags=re.IGNORECASE)
    if m:
        rest = m.group(1).strip()
        split = re.search(r"\s+[—\-|]\s+", rest)
        if split:
            name = canonical_name(rest[:split.start()].strip())
            reason = rest[split.end():].strip()
            return f"Meeting: {name} | {reason}"
        return f"Meeting: {canonical_name(rest)}"

    # 8. "Day N Email" -> Outreach: ...
    if re.match(r"^day\s+\d+\s+email\b", s, flags=re.IGNORECASE):
        return f"Outreach: {s}"

    return s  # already canonical or unrecognized


def make_subject(action, contact_or_company, reason=""):
    """Build a canonical subject for a NEW task.
    Use this from any script that creates HubSpot tasks going forward.

    Example:
        make_subject("Follow up", "Liza Sigua", "Q2 reply")
        -> "Follow up: Liza Sigua | Q2 reply"
    """
    action = action.strip().title()
    name = canonical_name(contact_or_company)
    if reason:
        reason = reason.strip()
        if reason.lower() in ("follow up", "call", "email", "outreach", "research", "meeting"):
            # do not repeat the action verb
            reason = ""
    if reason:
        return f"{action}: {name} | {reason}"
    return f"{action}: {name}"


# Self-check when run directly
if __name__ == "__main__":
    samples = [
        "follow up with liza sigua",
        "Follow up with San Miguel Global Power",
        "Follow up with San Miguel Global Power Holdings Corporation",
        "FOLLOW UP Allan Saquilayan - Republic Cement (profile sent)",
        "Outreach - Zhejiang Huayou Cobalt Co. Ltd. | Day 1 Email",
        "Research Emmanuel Castro - Acciona Daanbantayan site (diesel",
        "MTG CONFIRMED: Sebastian/MGEN - May 4, 10:30 AM Virtual",
        "Fraser Outreach - Team Energy Corporation",
        "Apo Cement / Taiheiyo follow up",
        "[Gmail *] Philippine Nickel Ore Supply | ECONARES",
        "Follow up: Liza Sigua | Q2 reply",  # already canonical
        "Follow up - L.M. Pantilo, Carmen Copper | lmpantilo@carmencopper.com",
        "Follow up - Andy Sebastian | Toledo next steps",
    ]
    print(f"{'BEFORE':<70}  ->  AFTER")
    print("-" * 120)
    for s in samples:
        n = normalize_existing_subject(s)
        marker = "CHANGED" if n != s else "ok"
        print(f"[{marker:7}] {s[:68]:<68}  ->  {n}")
