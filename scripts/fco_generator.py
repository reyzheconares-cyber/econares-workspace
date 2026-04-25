#!/usr/bin/env python3
"""ECONARES FCO Generator"""
import sys, datetime

TODAY = datetime.datetime.utcnow().strftime('%d %B %Y')

def gen_nickel(company, qty, terms, price):
    port = terms.split()[-1] if terms else "[PORT]"
    return f"""FIRM PRICE INDICATION — SUBJECT TO FINAL CONFIRMATION
================================================================================
DATE: {TODAY}
FROM: ECONARES INTERNATIONAL TRADING CORP.
TO: {company}

Dear Sir / Madam,

We are pleased to submit the following Firm Price Indication:

COMMODITY: Nickel Ore - Limonite (Low Grade)
ORIGIN: Tawi-Tawi, Republic of the Philippines
LOADING PORT: Tawi-Tawi (or nearest acceptable Philippine port)
DISCHARGE PORT: {port}
AVAILABLE VOLUME: {qty} Metric Tons (Wet Basis)

QUALITY SPECIFICATIONS:
- Nickel (Ni): 0.50% min
- Iron (Fe): 40.00% typical
- Cobalt (Co): 0.02-0.05% indicative
- Silica (SiO2): 8-15% indicative
- Loss on Ignition (LOI): 8-14% indicative
- Moisture Content: 8-12% at time of loading

Note: Pre-shipment analysis by SGS or equivalent at load port.

PRICE INDICATION:
Unit Price: {price}
Basis: {terms}
Payment: Letter of Credit at Sight (L/C at Sight)
Currency: United States Dollar (USD)

LOGISTICS:
Loading Rate: 10,000 - 15,000 MT/day (vessel dependent)
Loading Terms: FOB Stowed / FIOST
Suggested Vessel: Handymax / Panamax (50,000 - 80,000 DWT)

VALIDITY: This indication is valid for 30 days from the date of this letter.

PROCEDURE:
1. Buyer confirms interest and provides LOI / ICPO
2. Seller issues FCO (Full Corporate Offer)
3. Buyer provides Performance Bond / POP as required
4. Execution of formal Sales Contract
5. Loading at Tawi-Tawi port

For clarifications, please contact us.

Best regards,

Reymarr Hijara (RZH)
Sales and Marketing Officer
ECONARES International Trading Corp.
Tabunok, Talisay City, Cebu, Philippines
reyzh.econares@gmail.com | +63 927 872 5194
WhatsApp / Telegram / Viber | Landline: (+63) 32 232 6280

Document Reference: ECONARES-NIO-FCO-{TODAY.replace(' ', '-').upper()}
================================================================================
"""

def gen_coal(company, qty, terms, price):
    port = terms.split()[-1] if terms else "[PORT]"
    return f"""FIRM PRICE INDICATION — SUBJECT TO FINAL CONFIRMATION
================================================================================
DATE: {TODAY}
FROM: ECONARES INTERNATIONAL TRADING CORP.
TO: {company}

Dear Sir / Madam,

We are pleased to submit the following Firm Price Indication:

COMMODITY: Thermal / Steam Coal
GRADE: Bituminous (Medium to High Calorific Value)
ORIGIN: Philippines (Surigao / Mindanao) / Indonesia
LOADING PORT: Tablaher / Bislig / Nasipit (Surigao)
DISCHARGE PORT: {port}
AVAILABLE VOLUME: {qty} Metric Tons

QUALITY SPECIFICATIONS:
- Gross Calorific Value: 5,500 - 6,500 kcal/kg (Min 5,200 GAR)
- Total Moisture (TM): 8 - 15% (Max 18%)
- Ash Content (AD): 8 - 15% (Max 18%)
- Volatile Matter (VM): 25 - 40% (Min 20%)
- Total Sulfur (TS): 0.5 - 1.2% (Max 1.5%)
- Size (Granulation): 0 - 50mm (Standard)

PRICE INDICATION:
Unit Price: {price}
Basis: {terms}
Payment: Letter of Credit at Sight / TT
Currency: United States Dollar (USD)

LOGISTICS:
Loading Rate: 3,000 - 5,000 MT/day
Loading Terms: FOB Stowed / FIOST
Suggested Vessel: Handymax (30,000 - 50,000 DWT)

VALIDITY: This indication is valid for 14 days from the date of this letter.

Best regards,

Reymarr Hijara (RZH)
Sales and Marketing Officer
ECONARES International Trading Corp.
reyzh.econares@gmail.com | +63 927 872 5194

Document Reference: ECONARES-COAL-FCO-{TODAY.replace(' ', '-').upper()}
================================================================================
"""

def gen_diesel(company, qty, terms, price):
    return f"""FIRM PRICE INDICATION — SUBJECT TO FINAL CONFIRMATION
================================================================================
DATE: {TODAY}
FROM: ECONARES INTERNATIONAL TRADING CORP.
TO: {company}

Dear Sir / Madam,

We are pleased to submit the following Firm Price Indication:

COMMODITY: Diesel (Automotive Gas Oil)
GRADE: Euro 5 / Philippines PNS Standards
ORIGIN: Imported / Domestic (confirmed per shipment)
DELIVERY POINT: {terms}
AVAILABLE VOLUME: {qty} Metric Tons / Liters

QUALITY SPECIFICATIONS:
- Density @ 15 deg C: 0.820 - 0.870 kg/L
- Sulfur Content: Max 50 ppm (Euro 5)
- Cetane Number: Min 51
- Flash Point: Min 60 deg C

PRICE INDICATION:
Unit Price: {price}
Basis: {terms}
Payment: Letter of Credit at Sight / TT in Advance
Currency: Philippine Peso (PHP) or USD

LOGISTICS:
Delivery Mode: Bulk (tanker truck) or Drums
Lead Time: 7 - 14 days from order confirmation

VALIDITY: This indication is valid for 7 days from the date of this letter.

Best regards,

Reymarr Hijara (RZH)
Sales and Marketing Officer
ECONARES International Trading Corp.
reyzh.econares@gmail.com | +63 927 872 5194

Document Reference: ECONARES-DSL-FCO-{TODAY.replace(' ', '-').upper()}
================================================================================
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fco_generator.py COMPANY QUANTITY PRODUCT TERMS PRICE")
        print("Example: python3 fco_generator.py Tsingshan 5000 Nickel-Ore CIF-Rizhao USD-45-WMT")
        sys.exit(1)
    
    company = sys.argv[1] if len(sys.argv) > 1 else "BUYER"
    qty = sys.argv[2] if len(sys.argv) > 2 else "[QTY]"
    product = sys.argv[3].lower() if len(sys.argv) > 3 else "nickel"
    terms = sys.argv[4] if len(sys.argv) > 4 else "[TERMS]"
    price = sys.argv[5] if len(sys.argv) > 5 else "[PRICE]"
    
    if "nickel" in product or "ore" in product:
        print(gen_nickel(company, qty, terms, price))
    elif "coal" in product:
        print(gen_coal(company, qty, terms, price))
    elif "diesel" in product or "fuel" in product:
        print(gen_diesel(company, qty, terms, price))
    else:
        print(gen_nickel(company, qty, terms, price))
