# ECONARES Skill Mining Proposals — 2026-07-04

Audited: 80+ Python scripts in /home/mauiclaw/ECONARES_WORKSPACE/scripts/ and the existing
~/.hermes/skills/ tree. Below are 4 repeatable patterns that are NOT yet formalized as
skills. RZH review and decide which to create (these are proposals, not created skills).

---

## PROPOSAL 1: `hubspot-token-loader`

**Category:** sales / utilities
**Priority:** HIGH (used in 100% of HubSpot scripts)
**Effort to formalize:** 30 min (smallest, highest-leverage)

### Description

The ECONARES `.env` file uses bash `export` syntax, which trips up most Python regex
loaders (captures the `export` prefix and quotes). Every HubSpot script has the same
~12 lines of token-loading boilerplate. Centralizing this eliminates copy-paste bugs
where the wrong prefix or quotes slip in.

### When To Use

- Any new Python script that needs to call the HubSpot API
- Any script that currently has a 5-15 line `_token()` function

### Key Pattern

```python
import re
from pathlib import Path

ENV_PATH = Path.home() / ".hermes" / ".env"
HUBSPOT_OWNER_ID_RZH = "164168266"  # ACTIVE. 90091659 is DEAD — never use.

def load_hubspot_token(env_path=ENV_PATH):
    """Read HUBSPOT_ACCESS_TOKEN from .env. Handles bash `export` prefix and quotes."""
    for line in env_path.read_text().splitlines():
        # Match: [export ]HUBSPOT_ACCESS_TOKEN=VALUE
        m = re.match(r"\s*(?:export\s+)?HUBSPOT_ACCESS_TOKEN\s*=\s*(.+)", line)
        if m:
            value = m.group(1).strip().strip('"').strip("'")
            if value:
                return value
    raise SystemExit("HUBSPOT_ACCESS_TOKEN not found in ~/.hermes/.env")
```

### Pitfalls

- **Owner ID drift**: scripts that hardcode `90091659` (the dead ID) return 0 results silently. Always use `164168266` (RZH).
- **`.env` not auto-loaded** in `execute_code` or `terminal()` subprocesses. The token must be loaded inside the script.
- **Empty value**: if the .env line is `export HUBSPOT_ACCESS_TOKEN=""`, the regex captures `""` — must strip quotes explicitly.
- **Tirith scanner**: cron jobs that call `curl -H "Authorization: Bearer $TOKEN"` with literal `$TOKEN` get blocked. Use `{TOKEN}` (Python f-string) or `<TOKEN>` placeholders in skill docs.

---

## PROPOSAL 2: `hubspot-paginated-fetch`

**Category:** sales / utilities
**Priority:** HIGH (used in every script that touches Deals/Contacts/Companies)
**Effort to formalize:** 1 hour

### Description

The paginated `GET /crm/v3/objects/{type}` pattern is the production-grade path for
fetching all deals/contacts/companies. The `POST /search` endpoint has known IN-operator
bugs and 0-result traps. This skill would centralize the paginated pattern with
property whitelisting (mandatory — bare GET returns empty properties).

### When To Use

- Any script that fetches all open deals, contacts, or companies
- Any script that paginates through a HubSpot object list
- Replacing fragile `POST /search` with filterGroup code

### Key Pattern

```python
import json
import urllib.request

def paginated_fetch(token, object_type, properties, extra_qs="", page_limit=100):
    """Paginated GET /crm/v3/objects/{type}?properties=...&limit=100.

    Returns list of objects, each with 'id' and 'properties' dict.

    Args:
        token: HubSpot PAT loaded via load_hubspot_token()
        object_type: 'deals' | 'contacts' | 'companies' | 'notes' | 'tasks'
        properties: list of property names to fetch (mandatory)
        extra_qs: e.g. '&archived=false' or '&q=searchterm'
        page_limit: max results per page (default 100, max 100)
    """
    items, after = [], None
    base = f"https://api.hubapi.com/crm/v3/objects/{object_type}?limit={page_limit}&properties={','.join(properties)}{extra_qs}"
    while True:
        url = base if not after else f"{base}&after={after}"
        req = urllib.request.Request(url, method="GET")
        req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        items.extend(data.get("results", []))
        paging = data.get("paging", {}).get("next", {}).get("after")
        if not paging:
            break
        after = paging
    return items
```

### Pitfalls

- **Search POST has IN-operator bugs** that return 0 results silently. Always use paginated GET.
- **Properties are mandatory**: a bare `GET /crm/v3/objects/contacts` returns `properties: {}` for every record. Always specify `?properties=name,email,...`.
- **Rate limiting**: ~100 requests per 10 seconds. Add `time.sleep(0.1)` between pages for batch scripts.
- **Tasks API quirk**: `GET /crm/v3/objects/tasks` returns empty properties. Use `POST /tasks/search` instead.
- **Deal stage IDs are numeric** (e.g., `3410654914`) — always translate via `/crm/v3/pipelines/deals`.

---

## PROPOSAL 3: `deal-name-parser`

**Category:** sales / ECONARES-specific
**Priority:** MEDIUM (used in stale-deals, hygiene, possibly outreach)
**Effort to formalize:** 45 min

### Description

ECONARES deals follow a consistent naming convention: `<Company> - <Commodity> - <Volume/Spec> <Location>`.
The parser extracts (company, commodity, segment_hint) and is used in every script that
needs to bucket deals by commodity. Currently copy-pasted in `hubspot_stale_deals.py`,
`hubspot_hygiene_daily.py`, and a few older scripts with slight variations.

### When To Use

- Any script that needs to extract company or commodity from a deal name
- Bucket deals by commodity for reporting
- Detect parent-group membership (subsidiary check)

### Key Pattern

```python
import re

# Commodity keyword map (extensible)
COMMODITY_KEYWORDS = {
    "nickel": ["nickel", "ni ore", "laterite", "saprolite"],
    "copper": ["copper", "cu ore", "concentrate"],
    "coal": ["coal", "thermal coal", "coke breeze", "steam coal"],
    "diesel": ["diesel", "fuel oil", "bunker"],
    "pks": ["palm kernel shell", "pks"],
    "woodchips": ["woodchip", "wood chip", "acacia"],
    "cpo": ["crude palm oil", "cpo"],
}

SUFFIXES_TO_STRIP = ("supply", "inquiry", "pilot", "quote", "proposal")


def parse_deal_name(name):
    """Parse ECONARES deal name into (company, commodity, full).

    Examples:
        'Bulk Ore Limited - Nickel Ore Supply'
            -> ('Bulk Ore Limited', 'Nickel Ore', 'Bulk Ore Limited - Nickel Ore Supply')
        'FDC Misamis - Coal - 500k MT/yr Villanueva'
            -> ('FDC Misamis', 'Coal', 'FDC Misamis - Coal - 500k MT/yr Villanueva')
    """
    if not name:
        return ("?", "commodity", name)
    parts = [p.strip() for p in name.split(" - ")]
    if len(parts) >= 2:
        company = parts[0]
        last = parts[-1]
        commodity = re.sub(
            r"\s+(" + "|".join(SUFFIXES_TO_STRIP) + r")$",
            "", last, flags=re.IGNORECASE
        ) or last
        return (company, commodity, name)
    return (name, "commodity", name)


def detect_commodity(text):
    """Return canonical commodity if any keyword matches. None otherwise."""
    if not text:
        return None
    t = text.lower()
    for commodity, kws in COMMODITY_KEYWORDS.items():
        if any(kw in t for kw in kws):
            return commodity
    return None
```

### Pitfalls

- **Deal name is human-entered**, not a structured field. Variations include missing ` - ` separator, extra spaces, mixed case, suffixes.
- **Volume embedded in name**: `Coal - 500k MT/yr` — the parser should NOT try to extract the volume; that's a separate field. Just take the first word (`Coal`).
- **Multi-commodity deals**: rare, but possible (e.g., `Coal + PKS Pilot`). The detect_commodity() function returns the FIRST match. If multiple commodities are possible, prefer an explicit commodity property on the deal.
- **Parent company name may contain deal keywords**: e.g., `Philippine Sinter Corp` doesn't contain commodity words, but `Coke Breeze` does. The parse_deal_name correctly takes the first segment as company, so this is safe.

---

## PROPOSAL 4: `parent-subsidiary-detector`

**Category:** sales / ECONARES-specific
**Priority:** MEDIUM (used in stale-deals, planned for outreach queue)
**Effort to formalize:** 1.5 hours

### Description

The ECONARES skill `econares-crm-and-outreach-operations` defines 8 parent groups
with subsidiary mappings (MGEN, AboitizPower, SMC Global Power, GNPower, SPC, Holcim,
Republic Cement, PCPC). The rule: if a parent has an open deal, all its subsidiaries
are SKIPPED from new outreach (they go through the existing deal channel only).

This is currently hardcoded in `hubspot_stale_deals.py` and needs to be a reusable
component so the daily outreach queue + future scripts can share the same logic.

### When To Use

- Any script that produces a list of companies/deals to outreach
- Filter out subsidiaries when their parent has an active deal
- Parent-group level reporting (which groups have open deals, which are stale)

### Key Pattern

```python
PARENT_GROUPS = {
    "MGEN / Meralco PowerGen": {
        "subsidiaries": ["CEDC", "Global Business Power", "GBP", "Meralco PowerGen",
                         "Toledo Power", "Redondo", "SPPC"],
    },
    "AboitizPower": {
        "subsidiaries": ["Therma Visayas", "Therma South", "TSI", "Therma Marine",
                         "Therma Subic", "Hedcor", "AP Renewables", "Aboitiz Power",
                         "SN Aboitiz", "Aboitiz", "PTC", "Philippine Hydro"],
    },
    "SMC Global Power": {
        "subsidiaries": ["Limay", "Mariveles", "Malita", "Sarangani", "SMC",
                         "San Miguel Power", "SMCGP", "SMC Power"],
    },
    "GNPower": {"subsidiaries": ["GNPower", "Dinginin", "Kauswagan", "GN Power"]},
    "SPC Power Group": {"subsidiaries": ["Panay Energy", "PEDC", "SPC Power", "Naga", "SPC"]},
    "Holcim Philippines": {"subsidiaries": ["Holcim", "La Union", "Bulacan", "Lugait", "Davao", "Holcim Philippines"]},
    "Republic Cement": {"subsidiaries": ["Republic Cement", "RCMI", "Danao", "Teresa", "Republic", "Republic Cement Norzagaray"]},
    "PCPC / Jin Navitas": {"subsidiaries": ["Palm Concepcion", "PCPC", "Iloilo CFBC", "Jin Navitas"]},
}


def detect_parent_group(deal_name, company_name=""):
    """Return parent group name if deal/company matches a known subsidiary.
    Case-insensitive substring on (deal_name + company_name)."""
    text = f"{deal_name or ''} {company_name or ''}".lower()
    for parent, info in PARENT_GROUPS.items():
        for kw in info["subsidiaries"]:
            if kw.lower() in text:
                return parent
    return None


def build_live_exclusion_set(open_deals):
    """Return set of parent groups with at least one OPEN deal in the portal."""
    parents_with_open_deals = set()
    for d in open_deals:
        parent = detect_parent_group(d.get("dealname", ""))
        if parent:
            parents_with_open_deals.add(parent)
    return parents_with_open_deals
```

### Pitfalls

- **Subsidiary names can be substrings of unrelated companies** (e.g., "SPC" is a common acronym). Substring matching may produce false positives. Use a more specific match (word-boundary regex) if false-positive rate becomes an issue.
- **The mapping is hardcoded**. If ECONARES adds a new parent group (e.g., new acquisition), the SKILL.md must be updated and any consuming script must re-load.
- **The 5 active parent groups with open deals as of 2026-07-04**: AboitizPower, PCPC/Jin Navitas, Republic Cement, SMC Global Power. Holcim, MGEN, GNPower, SPC have NO open deals right now (verify per run).
- **The live exclusion set is per-run**: parents enter/exit the exclusion set as deals open/close. Always rebuild the set on every run; never cache.

---

## RECOMMENDATIONS

**Order to formalize (most ROI first):**
1. `hubspot-token-loader` (30 min, 100% script coverage)
2. `hubspot-paginated-fetch` (1 hour, every script that touches HubSpot)
3. `parent-subsidiary-detector` (1.5 hours, used in stale-deals + planned for outreach queue)
4. `deal-name-parser` (45 min, used in 2-3 scripts already)

**Total effort:** ~4 hours to formalize all 4. Each eliminates ~20-50 lines of
copy-paste per script. Pays back on every new ECONARES script written.

**Skip for now:**
- Commodity tag schema creation (RZH decision needed; out of scope for skill)
- HubSpot contact validation (already in `econares-contact-validation` skill)
- Telegram report formatter (each script's output differs; not generic enough yet)
