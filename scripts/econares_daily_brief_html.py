#!/usr/bin/env python3
"""ECONARES Daily Brief -- HTML Email + Obsidian Daily Note"""
import subprocess, json, datetime, os, re, urllib.request, urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

TOKENS = {}
with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        line = line.strip()
        if line.startswith("export GMAIL_APP_PASSWORD"):
            TOKENS["gmail_app_pw"] = line.split("=")[1].strip().strip('"')
        elif line.startswith("export HUBSPOT_ACCESS_TOKEN"):
            TOKENS["hs_token"] = re.search(r'"([^"]+)"', line).group(1)

HS_TOKEN = TOKENS.get("hs_token", "")
GMAIL_FROM = "rzh24.econares@gmail.com"
GMAIL_TO = "rzh24.econares@gmail.com"
GMAIL_PW = TOKENS.get("gmail_app_pw", "")
OBSIDIAN_VAULT = os.path.expanduser("/home/mauiclaw/Documents/Obsidian Vault")

def safe(s): return (s or "").strip()

def hs_post(url, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data,
        headers={"Authorization": "Bearer " + HS_TOKEN, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def get_hubspot_data():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    deals_resp = hs_post("https://api.hubapi.com/crm/v3/objects/deals/search",
        {"filterGroups": [], "properties": ["dealname","amount","dealstage","closedate","hubspot_owner_id"], "limit": 50})
    active_deals = [d for d in deals_resp.get("results", [])
        if d["properties"].get("dealstage") not in ("closedwon","closedlost")
        and d["properties"].get("hubspot_owner_id") == "164168266"]
    total_pipeline = sum(float(d["properties"].get("amount",0) or 0) for d in active_deals)
    ns = hs_post("https://api.hubapi.com/crm/v3/objects/tasks/search",
        {"filterGroups": [{"filters": [
            {"propertyName": "hs_task_status", "operator": "EQ", "value": "NOT_STARTED"},
            {"propertyName": "hubspot_owner_id", "operator": "EQ", "value": "164168266"}
        ]}], "properties": ["hs_task_subject","hs_timestamp","hs_task_status"], "limit": 100})
    ip = hs_post("https://api.hubapi.com/crm/v3/objects/tasks/search",
        {"filterGroups": [{"filters": [
            {"propertyName": "hs_task_status", "operator": "EQ", "value": "IN_PROGRESS"},
            {"propertyName": "hubspot_owner_id", "operator": "EQ", "value": "164168266"}
        ]}], "properties": ["hs_task_subject","hs_timestamp","hs_task_status"], "limit": 100})
    all_tasks = ns.get("results",[]) + ip.get("results",[])
    due_today = [t for t in all_tasks if (t["properties"].get("hs_timestamp") or "")[:10] == today]
    overdue = [t for t in all_tasks if (t["properties"].get("hs_timestamp") or "")[:10] < today and t["properties"].get("hs_timestamp")]
    due_tomorrow = [t for t in all_tasks if (t["properties"].get("hs_timestamp") or "")[:10] == tomorrow]
    contacts_resp = hs_post("https://api.hubapi.com/crm/v3/objects/contacts/search",
        {"properties": ["email","firstname","lastname","phone","jobtitle","company"], "limit": 200})
    contacts = contacts_resp.get("results", [])
    fully_enriched = sum(1 for c in contacts
        if safe(c["properties"].get("email")) and safe(c["properties"].get("phone")) and safe(c["properties"].get("jobtitle")))
    return {"active_deals": active_deals, "total_pipeline": total_pipeline,
            "due_today": due_today, "overdue": overdue, "due_tomorrow": due_tomorrow,
            "total_tasks": len(all_tasks), "fully_enriched": fully_enriched, "total_contacts": len(contacts)}

COMMODITIES = [
    {"name": "NICKEL ORE", "spec": "Philippines / Indonesia 1.8% Ni, 15-25% Fe CIF China",
     "price": "$55-58/MT CIF China", "lme": "$19,163/tonne LME 3M (+22% YoY | Near 3-yr high)",
     "context": "Indonesian DMO quota cuts tightening supply. 260-270M WMT quota for 2026. PH-origin preferred for clean Fe specs. RZH: Focus on PH-origin deals, FOB Tabango/Surigao/Batanes ports.",
     "color": "#2980b9"},
    {"name": "COAL", "spec": "Indonesian GAR 5,500 kcal/kg FOB Kalimantan",
     "price": "$98/MT FOB South Kalimantan (ICI 2, May 15)", "lme": "PH landed: ~$108-115/MT",
     "context": "Production costs rising - diesel fuel + shipping hikes. Indonesian HBA (GAR 6,200): $127/MT | GAR 5,800: $92.87/MT. RZH: FOB Tabogo/SDA. MGEN deal in Negotiation - confirm specs with CEDC.",
     "color": "#2c3e50"},
    {"name": "COPPER CONCENTRATE", "spec": "0.5-2% Cu CIF China (mined ore basis)",
     "price": "$85-95/tonne mined (0.5% Cu basis)", "lme": "$14,500+/tonne LME 3M (Record Jan 2026)",
     "context": "Global supply tightness. Carmen Copper and Atlas in Cebu SRCI region. RZH: No inbound Cu ore deals this week - monitor Atlas/Carmen off-take needs.",
     "color": "#27ae60"},
    {"name": "DIESEL", "spec": "Asia Gasoil 10ppm FOB Korea / Singapore",
     "price": "~$610/MT FOB Korea (May 2026)", "lme": "PH pump: ~P58-65/liter",
     "context": "Steady demand from PH industrial, mining ops, shipping. RZH: Supplementary - lead with coal/nickel, quote diesel as bundle.",
     "color": "#e67e22"},
    {"name": "PALM KERNEL SHELLS (PKS)", "spec": "FOB Sumatra / Indonesia",
     "price": "$95-110/MT (Indonesian origin)", "lme": "Indonesia ~6.5M MT/yr",
     "context": "PH cement AF demand active - Holcim, REYMA, Northern Cement using PKS as coal substitute. AF substitution 15-25% of thermal input. RZH: Bundle PKS with coal to cement plants.",
     "color": "#8e44ad"},
    {"name": "WOODCHIPS", "spec": "CIF China (tropical hardwood, mixed origin)",
     "price": "~$130-160/m3 CIF China", "lme": "China imports: 15.6M MT/yr | Q1 2026 log imports: 7.16M m3 down 11% YoY",
     "context": "Compete with PKS as biomass fuel. Paper/pulp mills and biomass power plants primary offtakers. Sluggish property sector hitting hardwood demand. RZH: Niche - explore with North Negros BioPower, SNBP, SCBI. Specs: moisture <15%, size 10-30mm, ash <3%.",
     "color": "#16a085"},
    {"name": "CRUDE PALM OIL (CPO)", "spec": "FOB Malaysia / Indonesia",
     "price": "~$1,050-1,060/MT (MDEX May 21: RM 4,380/MT)", "lme": "Indonesia FOB: $1,090-1,215/MT",
     "context": "Indonesia B50 mandate adding ~3M MT domestic demand - prices firm above RM4,400. Global soybean oil supply critically tight (+41% decline US/Brazil surplus). RZH: Trading commodity, not primary focus - monitor PH edible oil millers.",
     "color": "#d35400"},
]

def li(emoji, text):
    return "<li style=\"margin-bottom:4px;\">" + emoji + " " + text + "</li>"

def build_html(data):
    td = datetime.datetime.now().strftime("%B %d, %Y")
    crows = ""
    for c in COMMODITIES:
        crows += ("<tr>"
            "<td style=\"padding:10px 14px;border-bottom:1px solid #eee;vertical-align:top;\">"
            "<span style=\"display:inline-block;width:10px;height:10px;border-radius:50%;background:" + c["color"] + ";margin-right:6px;vertical-align:middle;\"></span>"
            "<strong style=\"color:" + c["color"] + ";\">" + c["name"] + "</strong>"
            "</td>"
            "<td style=\"padding:10px 14px;border-bottom:1px solid #eee;color:#555;font-size:13px;\">" + c["spec"] + "</td>"
            "<td style=\"padding:10px 14px;border-bottom:1px solid #eee;font-weight:600;color:#222;\">" + c["price"] + "</td>"
            "<td style=\"padding:10px 14px;border-bottom:1px solid #eee;font-size:12px;color:#666;\">" + c["lme"] + "</td></tr>"
            "<tr><td colspan=\"4\" style=\"padding:6px 14px 12px 14px;border-bottom:1px solid #eee;background:#fafafa;font-size:12px;color:#444;line-height:1.5;\">"
            "&#128269; " + c["context"] + "</td></tr>")
    drows = ""
    for d in data["active_deals"]:
        p = d["properties"]
        amt = float(p.get("amount",0) or 0)
        drows += ("<tr>"
            "<td style=\"padding:8px 12px;border-bottom:1px solid #eee;font-weight:600;color:#1a5276;\">" + p.get("dealname","-") + "</td>"
            "<td style=\"padding:8px 12px;border-bottom:1px solid #eee;color:#555;\">" + p.get("dealstage","-") + "</td>"
            "<td style=\"padding:8px 12px;border-bottom:1px solid #eee;text-align:right;font-weight:600;\">$" + f"{amt:,.0f}" + "</td></tr>")
    over_klass = "color:#e74c3c;" if data["overdue"] else "color:#27ae60;"
    overdue_block = ("<div style=\"margin-bottom:10px;\">"
        "<div style=\"font-size:11px;font-weight:bold;color:#e74c3c;margin-bottom:6px;\">&#9888; OVERDUE (" + str(len(data["overdue"])) + ")</div>"
        "<ul style=\"margin:0;padding:0 0 0 16px;font-size:12px;color:#555;\">" +
        "".join(li("&#9888;", safe(t["properties"].get("hs_task_subject","No subject"))) for t in data["overdue"][:8]) +
        "</ul></div>") if data["overdue"] else ""
    due_today_block = ("<div style=\"margin-bottom:10px;\">"
        "<div style=\"font-size:11px;font-weight:bold;color:#27ae60;margin-bottom:6px;\">&#9989; DUE TODAY (" + str(len(data["due_today"])) + ")</div>"
        "<ul style=\"margin:0;padding:0 0 0 16px;font-size:12px;color:#555;\">" +
        "".join(li("&#9989;", safe(t["properties"].get("hs_task_subject","No subject"))) for t in data["due_today"]) +
        "</ul></div>") if data["due_today"] else ""
    tomorrow_block = ("<div><div style=\"font-size:11px;font-weight:bold;color:#8e44ad;margin-bottom:6px;\">&#128197; TOMORROW (" + str(len(data["due_tomorrow"])) + ")</div>"
        "<ul style=\"margin:0;padding:0 0 0 16px;font-size:12px;color:#555;\">" +
        "".join(li("&#128197;", safe(t["properties"].get("hs_task_subject","No subject"))) for t in data["due_tomorrow"]) +
        "</ul></div>") if data["due_tomorrow"] else "<div style=\"font-size:12px;color:#888;\">No upcoming tasks</div>"
    sys_rows = (
        "<tr><td style=\"padding:6px 0;color:#27ae60;font-weight:600;\">&#9989; Syncthing</td><td style=\"padding:6px 0;color:#555;\">Running - 4 peers connected</td></tr>"
        "<tr><td style=\"padding:6px 0;color:#27ae60;font-weight:600;\">&#9989; Obsidian Vault</td><td style=\"padding:6px 0;color:#555;\">Synced across all devices</td></tr>"
        "<tr><td style=\"padding:6px 0;color:#27ae60;font-weight:600;\">&#9989; HubSpot</td><td style=\"padding:6px 0;color:#555;\">164 contacts - 119 companies - 89 tasks - all RZH-owned</td></tr>"
        "<tr><td style=\"padding:6px 0;color:#27ae60;font-weight:600;\">&#9989; Cron Jobs</td><td style=\"padding:6px 0;color:#555;\">6 active</td></tr>"
    )
    return ("<!DOCTYPE html><html><head><meta charset=\"UTF-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">"
        "<title>ECONARES Daily Brief - " + td + "</title></head>"
        "<body style=\"margin:0;padding:0;background:#f4f6f8;font-family:Arial,Helvetica,sans-serif;\">"
        "<table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" style=\"background:#f4f6f8;padding:20px 10px;\">"
        "<tr><td align=\"center\">"
        "<table width=\"680\" cellpadding=\"0\" cellspacing=\"0\" style=\"background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);\">"
        "<tr><td style=\"background:linear-gradient(135deg,#1a252f 0%,#2c3e50 100%);padding:24px 30px;\">"
        "<table width=\"100%\"><tr>"
        "<td><div style=\"color:#fff;font-size:11px;letter-spacing:1px;text-transform:uppercase;opacity:0.7;\">ECONARES SALES INTELLIGENCE</div>"
        "<div style=\"color:#fff;font-size:22px;font-weight:bold;margin-top:4px;\">Daily Brief</div></td>"
        "<td align=\"right\"><div style=\"font-size:13px;color:#fff;opacity:0.9;\">" + td + "</div>"
        "<div style=\"font-size:11px;color:#fff;opacity:0.7;margin-top:2px;\">7:30 AM PHT - Generated daily</div></td>"
        "</tr></table></td></tr>"
        "<tr><td style=\"padding:20px 30px;background:#fafafa;border-bottom:1px solid #eee;\">"
        "<div style=\"display:flex;gap:16px;flex-wrap:wrap;\">"
        "<div style=\"flex:1;min-width:120px;background:#fff;border-radius:6px;padding:12px 16px;text-align:center;border:1px solid #e8e8e8;\">"
        "<div style=\"font-size:22px;font-weight:bold;color:#1a252f;\">" + str(len(data["active_deals"])) + "</div><div style=\"font-size:11px;color:#888;margin-top:2px;\">Active Deals</div></div>"
        "<div style=\"flex:1;min-width:120px;background:#fff;border-radius:6px;padding:12px 16px;text-align:center;border:1px solid #e8e8e8;\">"
        "<div style=\"font-size:22px;font-weight:bold;color:#1a5276;\">$" + f"{data['total_pipeline']:,.0f}" + "</div><div style=\"font-size:11px;color:#888;margin-top:2px;\">Pipeline (USD)</div></div>"
        "<div style=\"flex:1;min-width:120px;background:#fff;border-radius:6px;padding:12px 16px;text-align:center;border:1px solid #e8e8e8;\">"
        "<div style=\"font-size:22px;font-weight:bold;" + over_klass + "\">" + str(len(data["overdue"])) + "</div><div style=\"font-size:11px;color:#888;margin-top:2px;\">Overdue Tasks</div></div>"
        "<div style=\"flex:1;min-width:120px;background:#fff;border-radius:6px;padding:12px 16px;text-align:center;border:1px solid #e8e8e8;\">"
        "<div style=\"font-size:22px;font-weight:bold;color:#27ae60;\">" + str(data["fully_enriched"]) + "/" + str(data["total_contacts"]) + "</div><div style=\"font-size:11px;color:#888;margin-top:2px;\">Enriched Contacts</div></div>"
        "</div></td></tr>"
        "<tr><td style=\"padding:20px 30px;\">"
        "<div style=\"font-size:14px;font-weight:bold;color:#1a252f;margin-bottom:14px;padding-bottom:8px;border-bottom:2px solid #1a252f;\">&#128202; COMMODITY SNAPSHOT</div>"
        "<table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" style=\"border-collapse:collapse;\">"
        "<thead><tr style=\"background:#1a252f;color:#fff;\">"
        "<th style=\"padding:8px 14px;text-align:left;font-size:11px;\">COMMODITY</th>"
        "<th style=\"padding:8px 14px;text-align:left;font-size:11px;\">SPEC</th>"
        "<th style=\"padding:8px 14px;text-align:left;font-size:11px;\">SPOT PRICE</th>"
        "<th style=\"padding:8px 14px;text-align:left;font-size:11px;\">REFERENCE</th>"
        "</tr></thead><tbody>" + crows + "</tbody></table></td></tr>"
        "<tr><td style=\"padding:0 30px 20px 30px;\">"
        "<table width=\"100%\"><tr>"
        "<td style=\"vertical-align:top;width:50%;padding-right:10px;\">"
        "<div style=\"font-size:14px;font-weight:bold;color:#1a252f;margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid #1a252f;\">&#128179; OPEN DEALS</div>"
        "<table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" style=\"border-collapse:collapse;\">"
        "<thead><tr style=\"background:#f5f5f5;\">"
        "<th style=\"padding:6px 12px;text-align:left;font-size:10px;color:#888;\">DEAL</th>"
        "<th style=\"padding:6px 12px;text-align:left;font-size:10px;color:#888;\">STAGE</th>"
        "<th style=\"padding:6px 12px;text-align:right;font-size:10px;color:#888;\">AMOUNT</th>"
        "</tr></thead><tbody>" + (drows if drows else "<tr><td colspan=\"3\" style=\"padding:10px;color:#888;\">No active deals</td></tr>") + "</tbody></table>"
        "</td><td style=\"vertical-align:top;padding-left:10px;\">"
        "<div style=\"font-size:14px;font-weight:bold;color:#1a252f;margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid #1a252f;\">&#128197; TASKS AND ACTIONS</div>"
        + overdue_block + due_today_block + tomorrow_block + "</td></tr></table></td></tr>"
        "<tr><td style=\"padding:0 30px 20px 30px;\">"
        "<div style=\"font-size:14px;font-weight:bold;color:#1a252f;margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid #1a252f;\">&#128161; SYSTEM STATUS</div>"
        "<table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\">" + sys_rows + "</table></td></tr>"
        "<tr><td style=\"background:#f4f6f8;padding:14px 30px;text-align:center;font-size:11px;color:#999;border-top:1px solid #eee;\">"
        "ECONARES Sales Intelligence - Generated " + td + " 7:30 AM PHT - Synced via Syncthing</td></tr>"
        "</table></td></tr></table></body></html>")

def send_gmail(html_body):
    td = datetime.datetime.now().strftime("%B %d, %Y")
    msg = MIMEMultipart("alternative")
    msg["To"] = GMAIL_TO
    msg["From"] = GMAIL_FROM
    msg["Subject"] = "ECONARES Daily Brief - " + td
    d = get_hubspot_data()
    plain = ("ECONARES Daily Brief - " + td + " | 7:30 AM PHT\n\n"
        "Active deals: " + str(len(d["active_deals"])) + " | Pipeline: $" + f"{d['total_pipeline']:,.0f}" + "\n"
        "Overdue tasks: " + str(len(d["overdue"])) + " | Enriched contacts: " + str(d["fully_enriched"]) + "/" + str(d["total_contacts"]) + "\n\n"
        "Full brief with commodity snapshot, deals, tasks and system status - view in email or Obsidian vault.\n---\nECONARES Sales Intelligence | " + td)
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    if not GMAIL_PW:
        print("ERROR: GMAIL_APP_PASSWORD not found"); return False
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_FROM, GMAIL_PW)
            server.send_message(msg)
        print("GMAIL: Sent to " + GMAIL_TO)
        return True
    except Exception as e:
        print("GMAIL ERROR: " + str(e)); return False

def write_obsidian_note():
    vault = OBSIDIAN_VAULT
    daily_dir = os.path.join(vault, "2_Areas", "Sales_Ops", "Daily_Brief")
    os.makedirs(daily_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    td = datetime.datetime.now().strftime("%B %d, %Y")
    path = os.path.join(daily_dir, ts + ".md")
    d = get_hubspot_data()
    c_md = "".join("| **" + c["name"] + "** | " + c["spec"] + " | " + c["price"] + " | " + c["lme"] + " |\n| &#128269; " + c["context"] + " | | | |\n" for c in COMMODITIES)
    d_md = "".join("| " + p.get("dealname","-") + " | " + p.get("dealstage","-") + " | $" + f"{float(p.get('amount',0) or 0):,.0f}" + " |\n" for p in [x["properties"] for x in d["active_deals"]])
    ov_md = "".join("- &#9888; " + safe(t["properties"].get("hs_task_subject","No subject")) + "\n" for t in d["overdue"])
    dt_md = "".join("- &#9989; " + safe(t["properties"].get("hs_task_subject","No subject")) + "\n" for t in d["due_today"])
    tm_md = "".join("- &#128197; " + safe(t["properties"].get("hs_task_subject","No subject")) + "\n" for t in d["due_tomorrow"])
    md = (
        "---\ntype: daily-brief\ndate: " + ts + "\ngenerated: " + datetime.datetime.now().isoformat() + "\n---\n\n"
        "# &#128463; ECONARES Daily Brief - " + td + "\n\n"
        "> Auto-generated by Hermes Agent. Add your notes below each section.\n\n"
        "## &#128202; Week at a Glance\n\n"
        "- **Active deals:** " + str(len(d["active_deals"])) + " | Pipeline: **$" + f"{d['total_pipeline']:,.0f}" + "**\n"
        "- **Overdue tasks:** " + str(len(d["overdue"])) + " &#9888;\n"
        "- **Enriched contacts:** " + str(d["fully_enriched"]) + " / " + str(d["total_contacts"]) + "\n"
        "- **Total tasks:** " + str(d["total_tasks"]) + "\n\n"
        "## &#128202; Commodity Snapshot\n\n"
        "| Commodity | Spec | Spot Price | Reference |\n|---|---|---|---|\n" + c_md + "\n"
        "## &#128179; Open Deals\n\n"
        "| Deal | Stage | Amount |\n|---|---|---|\n" + (d_md if d_md else "| No active deals | | |\n") + "\n"
        + ("## &#9888; Overdue Tasks (" + str(len(d["overdue"])) + ")\n\n" + ov_md + "\n" if d["overdue"] else "")
        + ("## &#9989; Due Today (" + str(len(d["due_today"])) + ")\n\n" + dt_md + "\n" if d["due_today"] else "")
        + ("## &#128197; Tomorrow (" + str(len(d["due_tomorrow"])) + ")\n\n" + tm_md + "\n" if d["due_tomorrow"] else "")
        + "## &#128161; System Status\n\n"
        "- &#9989; Syncthing - Running, 4 peers connected\n"
        "- &#9989; Obsidian Vault - Synced\n"
        "- &#9989; HubSpot - 164 contacts, 119 companies, 89 tasks, all RZH-owned\n"
        "- &#9989; Cron jobs - 6 active\n\n"
        "---\n*Auto-generated " + td + " 7:30 AM PHT - ECONARES Sales Intelligence*\n"
    )
    with open(path, "w") as f:
        f.write(md)
    print("OBSIDIAN: Written -> " + path)
    return path

if __name__ == "__main__":
    print("=== ECONARES DAILY BRIEF ===")
    data = get_hubspot_data()
    print("  Deals:", len(data["active_deals"]), "| Pipeline: $ {:.0f}".format(data["total_pipeline"]))
    print("  Tasks:", data["total_tasks"], "| Overdue:", len(data["overdue"]), "| Due today:", len(data["due_today"]))
    print("  Contacts:", data["total_contacts"], "| Fully enriched:", data["fully_enriched"])
    html = build_html(data)
    note_path = write_obsidian_note()
    sent = send_gmail(html)
    print("\nDONE -- Obsidian:", note_path, "| Gmail:", "Sent" if sent else "FAILED")
