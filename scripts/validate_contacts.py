#!/usr/bin/env python3
"""
ECONARES Contact Validation Engine v1.0
=========================================
Validates email addresses and PH phone numbers before HubSpot encoding
and outreach. Designed for batch processing of lead lists.

SCORING
-------
Email Score (0.0 – 1.0):
  +0.3  Valid syntax (RFC 5322)
  +0.5  Domain has MX records (DNS check via dig)
  +0.2  Not a disposable email domain
  1.0 = valid | 0.5 = uncertain | 0.3 disposable = hard-block

Phone Score (0.0 – 1.0):
  0.9  Valid PH mobile (Globe/Smart/DITO prefix) → valid
  0.5  PH mobile, unrecognized prefix            → uncertain
  0.5  PH landline                              → uncertain (prefer mobile)

ACTIONS
-------
  encode_to_hubspot  — score >= 0.8 email OR >= 0.9 phone; no hard-blocks
  manual_review      — any score 0.5–0.8; or email hard-block
  investigate_correct— both channels < 0.5
  missing_contact_data — no email AND no phone provided

USAGE
-----
  python validate_contacts.py leads.xlsx [output.xlsx]

INPUT EXCEL: columns name, email, phone, company (optional)
OUTPUT: 4 sheets — Summary / Valid / Uncertain / Invalid / Full Results

DEPENDENCIES: pip install email-validator pandas openpyxl
Requires: dig (DNS/MX), phonenumbers, email-validator
"""

import subprocess, re, os, sys
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException
import pandas as pd
from datetime import datetime

PH_REGION = "PH"

DISPOSABLE_DOMAINS = {
    "mailinator.com","guerrillamail.com","tempmail.com","throwaway.email","10minutemail.com",
    "fakeinbox.com","trashmail.com","yopmail.com","getnada.com","temp-mail.org","emailondeck.com",
    "maildrop.cc","dispostable.com","mailnesia.com","tempr.email","discard.email","sharklasers.com",
    "grr.la","guerrillamailblock.com","pokemail.net","spam4.me","tempail.com","mytrashmail.com",
    "mt2009.com","thankyou2010.com","trash2009.com","mt2014.com","dropmail.me"
}

PH_PREFIX_TO_CARRIER = {}
for carrier, prefixes in {
    "Globe":  ["817","905","906","915","916","917","926","927","935","936","937","938","939","945","946","947",
               "953","955","956","957","965","966","967","975","976","977","978","979","995","996","997"],
    "Smart":  ["908","909","910","911","912","913","914","918","919","920","921","928","929","930","940",
               "948","949","950","951","959","970","981","998","999"],
    "DITO":   ["989","990","991","992","993"],
    "Sun":    ["922","923","924","925","931","932","933","934","942","943","944"],
}.items():
    for p in prefixes: PH_PREFIX_TO_CARRIER[p] = carrier

AREA_CODES = {
    "02":"Metro Manila","032":"Cebu City","033":"Iloilo","034":"Bacolod","035":"Cebu Province",
    "036":"Cebu/Leyte","042":"Luzon","043":"Luzon","044":"Bulacan","045":"Pampanga","046":"Batangas",
    "047":"Cavite","052":"Visayas","053":"Leyte/Samar","054":"Sorsogon","055":"Bataan",
    "062":"Zamboanga","063":"Tarlac","072":"Lucena","074":"Baguio","075":"Pangasinan",
    "077":"Nueva Ecija","078":"Isabela","082":"Mindanao","083":"Visayas","084":"Davao",
    "085":"Surigao","086":"Butuan","087":"Ozamis","088":"Cagayan de Oro","089":"Zamboanga"
}

def normalize_to_e164(raw):
    cleaned = re.sub(r"[\s\-\(\)]+", "", (raw or "").strip())
    if re.match(r"^0[789][0-9]{9}$", cleaned):    return "+63" + cleaned[1:]
    if re.match(r"^\+?63[789][0-9]{9}$", cleaned): return ("+" + cleaned) if not cleaned.startswith("+") else cleaned
    if re.match(r"^(\+?63|0)[2-7][0-9]{7,8}$", cleaned):
        if cleaned.startswith("0"): return "+63" + cleaned[1:]
        return cleaned if cleaned.startswith("+") else "+63" + cleaned
    return cleaned

def get_mobile_prefix(e164):
    digits = re.sub(r"\D", "", e164)
    if digits.startswith("63") and len(digits) == 12: return digits[2:5]
    if digits.startswith("9") and len(digits) == 10:    return digits[1:4]
    return ""

def validate_email_full(raw):
    r = {"input": raw, "normalized": None, "valid_syntax": False, "domain": None,
         "has_mx": False, "is_disposable": False, "issues": [], "status": "invalid", "score": 0.0}
    if not raw or not isinstance(raw, str): r["issues"].append("Empty input"); return r
    raw = raw.strip().lower(); r["input"] = raw
    try:
        v = validate_email(raw, check_deliverability=False)
        r["valid_syntax"] = True; r["normalized"] = v.normalized; r["domain"] = v.domain
    except EmailNotValidError as e:
        r["issues"].append(str(e)); return r
    try:
        dig_out = subprocess.run(["dig","+short","MX",r["domain"]], capture_output=True, text=True, timeout=10)
        r["has_mx"] = bool(dig_out.stdout.strip())
        if not r["has_mx"]: r["issues"].append("No MX — undeliverable")
    except: r["issues"].append("MX lookup failed")
    if r["domain"].lower() in DISPOSABLE_DOMAINS:
        r["is_disposable"] = True; r["issues"].append("Disposable domain"); r["has_mx"] = False
    score = 0.3 if r["valid_syntax"] else 0
    if r["has_mx"]: score += 0.5
    if not r["is_disposable"]: score += 0.2
    r["score"] = min(round(score, 2), 1.0)
    r["status"] = "valid" if score >= 0.8 else ("uncertain" if score >= 0.5 else "invalid")
    return r

def validate_phone_full(raw):
    r = {"input": raw, "normalized": None, "valid_format": False, "country": None,
         "line_type": None, "carrier": None, "location_hint": None, "issues": [], "status": "invalid", "score": 0.0}
    if not raw or not isinstance(raw, str): r["issues"].append("Empty input"); return r
    e164 = normalize_to_e164(raw); r["normalized"] = e164
    is_mobile = bool(re.match(r"^\+639[0-9]{9}$", e164))
    is_landline = bool(re.match(r"^\+63[2-7][0-9]{7,8}$", e164))
    if not is_mobile and not is_landline:
        r["issues"].append(f"Invalid PH format: {e164}"); return r
    r["valid_format"] = True
    if is_mobile:
        prefix = get_mobile_prefix(e164)
        r["carrier"] = PH_PREFIX_TO_CARRIER.get(prefix, "Unknown")
        try:
            parsed = phonenumbers.parse(e164, PH_REGION)
            r["country"] = phonenumbers.region_code_for_number(parsed)
        except: pass
        r["line_type"] = "mobile"
        if r["carrier"] in ("Globe","Smart","DITO"):
            r["score"] = 0.9; r["status"] = "valid"
        else:
            r["score"] = 0.5; r["status"] = "uncertain"
            r["issues"].append(f"Unrecognized prefix +63{prefix}")
    elif is_landline:
        r["carrier"] = "Landline"; r["line_type"] = "landline"
        code = re.sub(r"\D","",e164)[2:4] if len(e164) > 4 else ""
        r["location_hint"] = AREA_CODES.get("0"+code, code)
        r["score"] = 0.5; r["status"] = "uncertain"
        r["issues"].append("Landline — prefer mobile for WhatsApp/Viber outreach")
    return r

def validate_contact(name, email=None, phone=None, company=""):
    r = {"name": name, "company": company, "email_raw": email, "phone_raw": phone,
         "email_status": None, "email_score": None, "email_normalized": None, "email_issues": [],
         "phone_status": None, "phone_score": None, "phone_normalized": None,
         "phone_carrier": None, "phone_line_type": None, "phone_location": None, "phone_issues": [],
         "overall_status": "invalid", "overall_score": 0.0, "action": "manual_review"}
    email_hard_block = False
    if email:
        er = validate_email_full(email)
        r["email_status"]=er["status"]; r["email_score"]=er["score"]
        r["email_normalized"]=er["normalized"]; r["email_issues"]=er["issues"]
        if er.get("is_disposable") or er["status"] == "invalid": email_hard_block = True
    if phone:
        pr = validate_phone_full(phone)
        r["phone_status"]=pr["status"]; r["phone_score"]=pr["score"]
        r["phone_normalized"]=pr["normalized"]; r["phone_carrier"]=pr["carrier"]
        r["phone_line_type"]=pr["line_type"]; r["phone_location"]=pr.get("location_hint"); r["phone_issues"]=pr["issues"]
    scores = [s for s in [r["email_score"], r["phone_score"]] if s is not None]
    if not scores:
        r["action"] = "missing_contact_data"
    else:
        r["overall_score"] = round(sum(scores)/len(scores), 2)
        e, p = r["email_score"] or 0, r["phone_score"] or 0
        if email_hard_block:
            r["overall_status"] = "uncertain"; r["action"] = "manual_review"
        elif e >= 0.8 or p >= 0.9:
            r["overall_status"] = "valid"; r["action"] = "encode_to_hubspot"
        elif max(e, p) >= 0.5:
            r["overall_status"] = "uncertain"; r["action"] = "manual_review"
        else:
            r["action"] = "investigate_correct"
    return r

def validate_batch(contacts):
    rows = [validate_contact(c.get("name",""), c.get("email"), c.get("phone"), c.get("company","")) for c in contacts]
    df = pd.DataFrame(rows)
    df["email_issues"] = df["email_issues"].apply(lambda x: "; ".join(x) if x else "—")
    df["phone_issues"] = df["phone_issues"].apply(lambda x: "; ".join(x) if x else "—")
    return df

def export_to_excel(df, output_path):
    with pd.ExcelWriter(output_path, engine="openpyxl") as w:
        pd.DataFrame([
            {"Category":"Total Contacts","Count":len(df)},
            {"Category":"Valid — Encode to HubSpot","Count":len(df[df["action"]=="encode_to_hubspot"])},
            {"Category":"Uncertain — Manual Review","Count":len(df[df["overall_status"]=="uncertain"])},
            {"Category":"Invalid — Investigate","Count":len(df[df["action"].isin(["investigate_correct","missing_contact_data"])])},
            {"Category":"Generated","Count":datetime.now().strftime("%Y-%m-%d %H:%M")}
        ]).to_excel(w, sheet_name="Summary", index=False)
        valid = df[df["action"]=="encode_to_hubspot"][["name","company","email_raw","email_normalized","phone_raw","phone_normalized","phone_carrier","phone_line_type","email_score","phone_score","overall_score"]].rename(columns={"email_raw":"Email (original)","email_normalized":"Email (verified E.164)","phone_raw":"Phone (original)","phone_normalized":"Phone (E.164)"})
        valid.to_excel(w, sheet_name="Valid — HubSpot Ready", index=False)
        uncertain = df[df["overall_status"]=="uncertain"][["name","company","email_raw","email_normalized","phone_raw","phone_normalized","email_issues","phone_issues","email_score","phone_score","overall_status"]].rename(columns={"email_issues":"Email Issues","phone_issues":"Phone Issues"})
        uncertain.to_excel(w, sheet_name="Uncertain — Review", index=False)
        invalid = df[df["action"].isin(["investigate_correct","missing_contact_data"])][["name","company","email_raw","phone_raw","email_issues","phone_issues","overall_status","action"]].rename(columns={"email_issues":"Email Issues","phone_issues":"Phone Issues"})
        invalid.to_excel(w, sheet_name="Invalid — Investigate", index=False)
        df[["name","company","email_raw","phone_raw","email_status","email_score","phone_status","phone_score","phone_carrier","phone_line_type","overall_status","overall_score","action"]].to_excel(w, sheet_name="Full Results", index=False)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(0)
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else input_path.replace(".xlsx","_validated.xlsx")
    contacts_df = pd.read_excel(input_path)
    contacts = contacts_df.to_dict("records")
    result_df = validate_batch(contacts)
    export_to_excel(result_df, output_path)
    print(f"Validated {len(result_df)} contacts → {output_path}")
    print(result_df[["name","overall_status","action"]].to_string(index=False))
