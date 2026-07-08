"""Draft email to Cathy Chua (Century Peak Cement Manufacturing Purchasing). DO NOT SEND - draft only."""
import os, datetime

vault = r"C:/Users/reyma/Documents/Notes ECONARES/3_Resources/302 Sales Outreach/302a Web Form Templates"
os.makedirs(vault, exist_ok=True)
today = datetime.date.today().isoformat()

subject = "Indonesian Thermal Coal Supply for Century Peak Cement"

body = """Dear Ms. Chua,

My name is Reymarr Hijara, representing ECONARES International Trading Corp., a Philippine-based supplier of industrial fuels and minerals with direct access to Indonesian thermal coal from our Kalimantan stockpile and established mine access.

Mr. Rolando Ong (your Procurement Manager) kindly shared your contact for the email channel into CPC's procurement team, in line with his recommendation that we make initial contact via email.

I am writing to explore whether Century Peak Cement Manufacturing has interest in evaluating Indonesian thermal coal supply for your operations. We have a strong working knowledge of the cement-sector coal specifications (NAR 4,200-6,200 GAR, low-to-mid ash, low sulfur) and can tailor supply to your plant's specific CFB / coal-mill requirements.

WHAT WE OFFER
- Origin: Indonesian thermal coal (Kalimantan stockpile + established mine access)
- Grade: NAR 4,200-6,200 GAR, low-to-mid ash, low sulfur; flexible per plant specs
- Volume: 25,000-50,000 MT per month, scalable to your demand profile
- Incoterm: FOB Philippines ports (we ship APAC destinations on FOB terms only)
- Arrangement: Spot and medium-term supply contracts

WHY ECONARES
- Direct Indonesian mine access with no intermediary markup
- Established logistics from Indonesian ports to Philippine discharge ports
- Compliance documentation ready (origin, SGS, ISO-aligned)

I would welcome a brief call (15 minutes) to discuss CPC's current and projected coal demand and how our supply might align with your procurement schedule. Should email be preferred, I am happy to share our material specification sheet and current indicative pricing.

If there is a more appropriate contact within your procurement team for this inquiry, I would be grateful for an introduction. Per Mr. Ong's guidance, I am reaching out via email first and will await your direction before requesting further contact channels.

Thank you for your time and consideration.

Best regards,
Reymarr Hijara
Sales & Marketing
ECONARES International Trading Corp.
Email: rzh24.econares@gmail.com | Mobile: +63 927 872 5194

Note: For APAC destinations we offer FOB terms only. We do not offer DAP under any circumstance.

[OUTREACH CHANNEL NOTE - 2026-07-08]
- Referral source: Rolando Ong (Procurement Manager, rolando.ong@centurypeakcement.com)
- Rolando's guidance (verbatim): "I can only give her number after her expressed instruction to do so and recommended we reach out via email first. He assured she would definitely answer."
- Strategy: Email first. Wait for Cathy's response. Do NOT ask Rolando for phone number until Cathy consents.
- Per user instruction: "Draft and present external messages first; never send directly" - this is a DRAFT, not sent. Awaiting RZH approval before send.
"""

with open(os.path.join(vault, "Cathy_Chua_CPC_email_draft.txt"), 'w', encoding='utf-8') as f:
    f.write(f"SUBJECT ({len(subject.split())} words):\n{subject}\n\n")
    f.write(f"MESSAGE ({len(body.split())} words):\n{body}\n")

print(f"=== EMAIL DRAFT SAVED (NOT SENT) ===")
print(f"Vault: {vault}\\Cathy_Chua_CPC_email_draft.txt")
print(f"To: cathy.chua@centurypeakcement.com")
print(f"Subject ({len(subject.split())} words): {subject}")
print(f"Body ({len(body.split())} words)")
print()
print("=== STATUS: DRAFT ONLY - WAITING FOR RZH APPROVAL BEFORE SEND ===")