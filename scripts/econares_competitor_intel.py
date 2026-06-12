#!/usr/bin/env python3
"""ECONARES Competitor Intelligence - Weekly Tracker."""
import os, sys, json, csv, datetime, urllib.request, urllib.error, subprocess

ENV_PATH = os.path.expanduser("~/.hermes/.env")
WORKSPACE = "/home/mauiclaw/ECONARES_WORKSPACE"
DATA_DIR = os.path.join(WORKSPACE, "intelligence", "competitor")
DATA_FILE = os.path.join(DATA_DIR, "competitor_intel.json")
HISTORY_FILE = os.path.join(DATA_DIR, "competitor_history.csv")
TELEGRAM_CHAT_ID = "707620807"
os.makedirs(DATA_DIR, exist_ok=True)


def load_env():
    env = {}
    try:
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line.startswith("export "):
                    line = line[7:]
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env


def tavily_search(query, max_results=3):
    env = load_env()
    api_key = env.get("TAVILY_API_KEY", "")
    if not api_key:
        return {"error": "no TAVILY_API_KEY"}
    payload = json.dumps({"api_key": api_key, "query": query, "max_results": max_results, "search_depth": "basic"}).encode("utf-8")
    req = urllib.request.Request("https://api.tavily.com/search", data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def get_manual_prices():
    script = os.path.join(WORKSPACE, "scripts", "econares_price_fetch_free.py")
    try:
        r = subprocess.run(["python3", script], capture_output=True, text=True, timeout=60)
        return json.loads(r.stdout)
    except Exception as e:
        return {"error": str(e)}


def build_intel_snapshot():
    snapshot = {
        "timestamp": datetime.datetime.now().isoformat(),
        "as_of_date": datetime.date.today().isoformat(),
        "prices": {
            "indonesian_coal_5800_gar": {"basis": "FOB South Kalimantan", "manual_basis_usd_mt": 101.00, "manual_basis_date": "2026-05-29", "source": "Coaltradeindo"},
            "indonesian_coal_6000_nar": {"basis": "FOB South Kalimantan (implied)", "manual_basis_usd_mt": 108.00, "manual_basis_date": "2026-05-29", "source": "Coaltradeindo (interpolated)"},
            "hba_reference_6322_gar": {"basis": "HBA index", "manual_basis_usd_mt": 121.83, "change_pct": 5.0, "manual_basis_date": "2026-06-01", "source": "HBA Indonesia MEMR"},
            "gc_newcastle_jun26": {"basis": "NEWC NCFM26 futures", "manual_basis_usd_mt": 149.25, "change_usd": -0.95, "manual_basis_date": "2026-06-10", "source": "MarketWatch"},
            "nickel_ore_1_8_cif_china": {"basis": "Philippine laterite CIF China", "manual_basis_usd_mt": 45.00, "manual_basis_date": "2026-06-08", "source": "RZH manual override (Tsingshan/YNQSGT)"},
        },
        "competitors": [
            {"name": "Semirara Mining (SCC)", "threat": "MEDIUM-HIGH", "products": "Coal (own mines)", "production_mt_yr": 16000000, "asp_php_mt": 2479, "note": "Largest PH coal producer; SMC-aligned; renewable pivot"},
            {"name": "Samar Pacific", "threat": "MEDIUM", "products": "Coal (Indo-origin blended)", "note": "Mid-tier PH trader; 5800-6200 GAR; Visayas focus"},
            {"name": "Jorge Griffith Enterprises", "threat": "LOW-MEDIUM", "products": "Coal, bunker fuel", "note": "Cebu-based; relationship-led"},
            {"name": "Pacific Global Coal", "threat": "HIGH", "products": "Indo thermal 5600-6500 GAR", "note": "Direct E. Kalimantan mine contracts"},
            {"name": "Glencore", "threat": "MEDIUM", "products": "Newcastle coal, nickel, copper", "note": "GC Newcastle price-setter; PH marginal"},
            {"name": "Trafigura", "threat": "HIGH", "products": "Nickel, coal, copper, diesel", "note": "Dominant PH nickel ore to China; post-2023 compliance focus"},
        ],
    }
    return snapshot


def write_snapshot(snapshot):
    with open(DATA_FILE, "w") as f:
        json.dump(snapshot, f, indent=2)
    new_file = not os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, "a", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["timestamp", "coal_5800_gar_usd", "coal_6000_nar_usd", "newcastle_usd", "nickel_1_8_cif_usd", "hba_6322_usd"])
        p = snapshot["prices"]
        w.writerow([snapshot["timestamp"], p["indonesian_coal_5800_gar"]["manual_basis_usd_mt"], p["indonesian_coal_6000_nar"]["manual_basis_usd_mt"], p["gc_newcastle_jun26"]["manual_basis_usd_mt"], p["nickel_ore_1_8_cif_china"]["manual_basis_usd_mt"], p["hba_reference_6322_gar"]["manual_basis_usd_mt"]])


def render_report(snapshot):
    today = datetime.datetime.now().strftime("%A, %B %d, %Y")
    threat_emoji = {"HIGH": "[H]", "MEDIUM-HIGH": "[M-H]", "MEDIUM": "[M]", "LOW-MEDIUM": "[L-M]", "LOW": "[L]"}
    p = snapshot["prices"]
    lines = [
        "*ECONARES Competitor Intelligence - {0}*".format(today),
        "_Weekly price summary + competitor positioning_",
        "",
        "=" * 30,
        "*TRACKED COMMODITY PRICES*",
        "=" * 30,
        "",
        "*NICKEL ORE (PH laterite 1.8% CIF China)*",
        "- Current: ~USD {0}/MT CIF".format(p['nickel_ore_1_8_cif_china']['manual_basis_usd_mt']),
        "- Source: {0}".format(p['nickel_ore_1_8_cif_china']['source']),
        "",
        "*INDONESIAN COAL - 5800 GAR / 5500 NAR*",
        "- Current: ~USD {0}/MT FOB S. Kalimantan".format(p['indonesian_coal_5800_gar']['manual_basis_usd_mt']),
        "- HBA 6322 GAR: USD {0}/MT (+{1}% MoM)".format(p['hba_reference_6322_gar']['manual_basis_usd_mt'], p['hba_reference_6322_gar']['change_pct']),
        "",
        "*INDONESIAN COAL - 6000 NAR*",
        "- Current: ~USD {0}/MT FOB S. Kalimantan".format(p['indonesian_coal_6000_nar']['manual_basis_usd_mt']),
        "",
        "*GC NEWCASTLE COAL (NEWC Jun 2026)*",
        "- Current: USD {0}/MT (settle 6/10)".format(p['gc_newcastle_jun26']['manual_basis_usd_mt']),
        "",
        "=" * 30,
        "*COMPETITOR POSITIONING*",
        "=" * 30,
    ]
    for c in snapshot["competitors"]:
        lines.extend(["*{0}* {1}".format(c['name'], threat_emoji.get(c['threat'], '')), "  {0}".format(c.get('note', '')), "  _THREAT: {0}_".format(c['threat']), ""])
    lines.extend(["_Generated: {0}_".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M PHT')), "_Sources: Coaltradeindo, Asian Metal, SMM, NEWC (MarketWatch), RZH manual basis, Glencore Q1 2026_"])
    return "\n".join(lines)


def send_telegram(text, chat_id=TELEGRAM_CHAT_ID):
    env = load_env()
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        return {"error": "no TELEGRAM_BOT_TOKEN"}
    url = "https://api.telegram.org/bot{0}/sendMessage".format(token)
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": "HTTP {0}: {1}".format(e.code, e.read().decode()[:500])}
    except Exception as e:
        return {"error": str(e)}


def main():
    args = sys.argv[1:]
    snapshot = build_intel_snapshot()
    if "--update" in args or not args:
        write_snapshot(snapshot)
        print("[OK] Snapshot written -> {0}".format(DATA_FILE))
        print("[OK] History appended -> {0}".format(HISTORY_FILE))
    if "--report" in args or "--deliver" in args or not args:
        report = render_report(snapshot)
        result = send_telegram(report)
        print("[TELEGRAM] {0}".format(json.dumps(result)[:200]))


if __name__ == "__main__":
    main()
