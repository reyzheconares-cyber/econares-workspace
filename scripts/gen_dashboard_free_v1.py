import sys, json, re, urllib.request, subprocess
sys.path.insert(0, '/home/mauiclaw/.hermes/hermes-agent/venv/lib/python3.11/site-packages')
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ── Load free fetcher output (already saved) ──────────────
with open('/tmp/dashboard_prices.json') as f:
    free = json.load(f)
with open('/tmp/iron_ore_price.json') as f:
    iron = json.load(f)

def parse_manual(text):
    m = re.search(r'USD\s*(\d+(?:,\d{3})*(?:\.\d+)?)', text)
    return float(m.group(1).replace(',', '')) if m else None

def parse_te(d):
    if not d: return None
    return {'price': d.get('price_value'), 'unit': d.get('unit', ''), 'change_pct': d.get('change_pct', 0)}

nickel_data = parse_manual(free.get('nickel', {}).get('description', '')) or 45.0
coal_data   = parse_manual(free.get('coal', {}).get('description', '')) or 88.0
pks_data    = parse_manual(free.get('pks', {}).get('description', '')) or 102.0
wood_data   = parse_manual(free.get('woodchips', {}).get('description', '')) or 145.0

copper_te = parse_te(free.get('copper'))
diesel_te = parse_te(free.get('diesel'))
cpo_te    = parse_te(free.get('cpo'))

lme_cu_lbs = copper_te['price'] if copper_te else 6.26
lme_cu_mt  = lme_cu_lbs * 2204.62
cu_conc_cif = round(lme_cu_mt * 0.27 * 0.965, 0)

ho_gal = diesel_te['price'] if diesel_te else 3.67
diesel_mt = round(ho_gal * 317.98, 0)

myr_t = cpo_te['price'] if cpo_te else 4554
cpo_usd = round(myr_t * 0.23, 0)

iron_cfr = iron['price_value']
iron_fob = round(iron_cfr * 0.92, 0)
iron_cp = iron['change_pct']

nickel_medium = round(nickel_data * 0.78, 0)
nickel_limo   = round(nickel_data * 0.45, 0)

PAST = {
    'NICKEL SAPROLITE': 54.0, 'NICKEL MEDIUM': 49.0, 'NICKEL LIMONITE': 27.0,
    'IRON ORE': 92.0, 'CHROMITE': 181.0, 'COPPER ORE': 1900.0,
    'THERMAL COAL': 88.0, 'COKING COAL': 200.0, 'DIESEL': 660.0,
    'PALM KERNEL SHELLS': 97.0, 'WOODCHIPS': 73.0, 'PALM OIL (CPO)': 910.0,
}

def wow(name, current):
    p = PAST.get(name)
    if p and p > 0:
        pct = (current - p) / p * 100
        return f'{pct:+.1f}%', 'up' if pct > 0.3 else ('down' if pct < -0.3 else 'flat')
    return 'N/A', 'flat'

COMM = []
def card(name, grade, spec, price, unit, mkt, src, conf, comm):
    w, d = wow(name, price)
    COMM.append({
        'name': name, 'grade': grade, 'spec': spec, 'price': str(price),
        'unit': unit, 'mkt': mkt, 'source': src, 'conf': conf,
        'wow': w, 'dir': d, 'comm': comm,
    })

card('NICKEL SAPROLITE', 'Ni 1.6-1.8%', 'Mg 20-30%, Fe 8-12%', nickel_data, 'USD/MT', 'FOB Philippines (Surigao)', 'Manual override (RZH)', 'HIGH', 'PH-origin FOB; DMO cuts tighten supply.')
card('NICKEL MEDIUM', 'Ni 1.3-1.5%', 'Fe 15-25%, Mg 8-15%', nickel_medium, 'USD/MT', 'FOB Philippines (Surigao)', 'Derived from saprolite (78%)', 'MED', 'Mid-grade ore; lower payability; Asia-Pac discount.')
card('NICKEL LIMONITE', 'Ni 0.8-1.2%', 'Fe 30-50%, Mg 2-5%', nickel_limo, 'USD/MT', 'FOB Philippines (Palawan/Mindanao)', 'Derived from saprolite (45%)', 'LOW', 'Heap-leach feed; HPAL processors; volatile basis.')
card('IRON ORE', '62% Fe Fines ICX', 'CFR Tianjin (TE) → FOB AU', iron_fob, 'USD/MT', 'FOB Australia (Pilbara)', 'Trading Economics (iron-ore)', 'HIGH', f'CFR ${iron_cfr}/T ×0.92 = FOB AU; {iron_cp:+.2f}% WoW.')
card('CHROMITE', '42-48% Cr2O3', 'SiO2 <8%, Al2O3 <12%', 181.0, 'USD/MT', 'FOB Philippines (Dinagat/Surigao)', 'No free source - May 2026 est.', 'LOW', 'Met-grade lump premium; PH metallurgical exports limited.')
card('COPPER ORE', '25-30% Cu conc', 'CIF China (reference)', cu_conc_cif, 'USD/MT', 'CIF China (smelter return)', f'LME Cu ${lme_cu_lbs}/lb × 27% × 96.5% payable', 'MED', 'ID export ban Jan 2025 - PH viable; smelter return basis.')
card('THERMAL COAL', '5,500 kcal/kg GAR', 'FOB Indonesia (Kalimantan)', coal_data, 'USD/MT', 'FOB Indo (Kalimantan)', 'Manual override (RZH) / TE coal', 'HIGH', 'ICI 3 reference; PH landed ~$108-115/MT; PLN + Indian demand firm.')
card('COKING COAL', 'HCC PLV 64% CSR', 'FOB Australia (Newcastle)', 200.0, 'USD/MT', 'FOB Australia (Newcastle)', 'No free source - May 2026 est.', 'LOW', 'Premium HCC; metallurgical use; Indian steel mills buy.')
card('DIESEL', 'MGO 0.1%S IMO 2020', 'FOB Singapore (ULSD proxy)', diesel_mt, 'USD/MT', 'FOB Singapore (NY Harbor ULSD proxy)', 'Trading Economics (heating-oil)', 'MED', f'ULSD ${ho_gal}/gal; {diesel_te["change_pct"] if diesel_te else 0:+.2f}% WoW; Asia gasoil direction proxy.')
card('PALM KERNEL SHELLS', 'NCV 3,800-4,400 kcal/kg', 'FOB Sumatra', pks_data, 'USD/MT', 'FOB Indonesia (Sumatra)', 'Manual override (RZH)', 'HIGH', 'PH cement AF demand (Holcim, REYMA, Northern); biomass alt.')
card('WOODCHIPS', 'NCV 3,200-4,000 kcal/kg', 'CIF China tropical HW', wood_data, 'USD/m3', 'CIF China', 'Manual override (RZH)', 'HIGH', 'Biomass fuel; competes with PKS; Q1 2026 log imports -11% YoY.')
card('PALM OIL (CPO)', 'Crude 24% FFA', 'FOB Indonesia-Malaysia', cpo_usd, 'USD/MT', 'FOB Malaysia (Bursa reference)', 'Trading Economics (palm-oil) x MYR->USD', 'MED', f'MYR {myr_t}/T -> USD ${cpo_usd}/T; B50 mandate support firm.')

# ── PIL rendering ──────────────────────────────────────────
W, H = 1200, 900
CW, CH = 285, 248
GX, GY = 10, 14
HH, FH = 50, 30
PADX = (W - 4*(CW+GX) + GX) // 2
PH = 3

BG=(15,23,42); CD=(24,34,58); GD=(250,190,50); GN=(52,220,130); RD=(255,90,90)
WH=(248,248,252); GR=(140,155,185); G2=(85,98,135); G3=(95,108,150)
COH=(40,200,120); COM=(220,180,60); COL=(200,100,80)
AC=[(40,210,100),(255,175,50),(255,130,40),(100,155,210),(60,210,160),(255,220,80),(240,140,60),(190,200,215),(80,155,255),(200,130,60),(130,180,120),(220,80,80)]

FN='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

NF=ImageFont.truetype(FN,12)
GF=ImageFont.truetype(FR,8)
PF=ImageFont.truetype(FN,28)
UF=ImageFont.truetype(FR,10)
OF=ImageFont.truetype(FR,7)
CF=ImageFont.truetype(FR,7)
TF=ImageFont.truetype(FN,9)
HF=ImageFont.truetype(FN,13)
FF=ImageFont.truetype(FR,7)
BF=ImageFont.truetype(FN,8)

def bs(f,t):
    b = f.getbbox(t)
    return b[2]-b[0], b[3]-b[1]

def rr(d,xy,r,F):
    x0,y0,x1,y1=xy
    d.ellipse((x0,y0,x0+r*2,y0+r*2),fill=F)
    d.ellipse((x1-r*2,y0,x1,y0+r*2),fill=F)
    d.ellipse((x0,y1-r*2,x0+r*2,y1),fill=F)
    d.ellipse((x1-r*2,y1-r*2,x1,y1),fill=F)
    d.rectangle((x0+r,y0,x1-r,y1),fill=F)
    d.rectangle((x0,y0+r,x1,y1-r),fill=F)

r1y = HH+12
r2y = r1y+CH+GY
r3y = r2y+CH+GY
def ry(r): return r1y if r==0 else (r2y if r==1 else r3y)
def cx(c): return PADX + c*(CW+GX)

img = Image.new('RGB', (W, H), BG)
draw = ImageDraw.Draw(img)

# Header
draw.rectangle((0,0,W,HH), fill=(9,14,30))
ht = "ECONARES  DAILY  COMMODITY  DASHBOARD"
hw, hh_ = bs(HF, ht)
draw.text(((W-hw)//2, (HH-hh_)//2 - 2), ht, font=HF, fill=GD)
draw.rectangle((0, HH-3, W, HH), fill=GD)

# Footer
draw.rectangle((0, H-FH, W, H), fill=(9,14,30))
draw.rectangle((0, H-FH, W, H-FH+3), fill=GD)
ft = f"ALL PRICES INDICATIVE  |  FOB ORIGIN ONLY  |  VERIFY BEFORE USE  |  CONF:HIGH=quote  CONF:MED=derived  CONF:LOW=estimated  |  Free-Source Feed (TE)  |  {datetime.now().strftime('%B %Y')}"
fw, fh_ = bs(FF, ft)
draw.text(((W-fw)//2, H-FH + (FH-fh_)//2), ft, font=FF, fill=G2)

def conf_color(c):
    return COH if c=='HIGH' else (COM if c=='MED' else COL)

for i, c in enumerate(COMM):
    row = i // 4
    col = i % 4
    x = cx(col)
    y = ry(row)
    
    rr(draw, (x, y, x+CW, y+CH), 8, CD)
    draw.rectangle((x+8, y, x+CW-8, y+PH), fill=AC[i])
    
    nx, ny = x+12, y+12
    draw.text((nx, ny), c['name'], font=NF, fill=GD)
    
    gx_, gy_ = nx, ny + 18
    draw.text((gx_, gy_), c['grade'], font=GF, fill=G2)
    
    sx, sy = nx, gy_ + 12
    draw.text((sx, sy), c['spec'], font=GF, fill=GR)
    
    py = sy + 22
    pt = f"${c['price']}"
    pw, ph_ = bs(PF, pt)
    draw.text((nx, py), pt, font=PF, fill=WH)
    
    ut = f"/{c['unit']}"
    uw, uh = bs(UF, ut)
    draw.text((nx + pw + 4, py + ph_ - uh - 2), ut, font=UF, fill=GR)
    
    fy = py + ph_ + 4
    draw.text((nx, fy), c['mkt'], font=GF, fill=G2)
    
    wow_text = c['wow']
    arrow = '\u25B2' if c['dir'] == 'up' else ('\u25BC' if c['dir'] == 'down' else '\u25C6')
    wow_color = GN if c['dir'] == 'up' else (RD if c['dir'] == 'down' else GR)
    bt = f"{arrow} {wow_text}"
    bw, bh_ = bs(TF, bt)
    
    ct = f"CONF:{c['conf']}"
    ccw, cch = bs(BF, ct)
    
    pad = 8
    by = y + CH - bh_ - pad - 4
    bx_right = x + CW - pad
    draw.text((bx_right - bw, by), bt, font=TF, fill=wow_color)
    
    cb_y = by + bh_ + 2
    cb_w = ccw + 12
    cb_h = cch + 4
    cb_x = bx_right - cb_w
    rr(draw, (cb_x, cb_y, cb_x+cb_w, cb_y+cb_h), 4, conf_color(c['conf']))
    cw2, ch2 = bs(BF, ct)
    draw.text((cb_x + (cb_w-cw2)//2, cb_y + (cb_h-ch2)//2 - 1), ct, font=BF, fill=BG)
    
    cy_ = y + CH - 30
    words = c['comm'].split()
    lines, cur = [], ''
    for w_ in words:
        test = (cur + ' ' + w_).strip()
        if len(test) <= 32:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    if len(lines) > 2:
        lines = lines[:2]
        lines[1] = lines[1][:29] + '...'
    for ln in lines:
        lw, lh = bs(CF, ln)
        if lw > CW - 100:
            ln = ln[:28] + '...'
        draw.text((nx, cy_), ln, font=CF, fill=G3)
        cy_ += 10

out_path = '/tmp/commodity-dashboard-FREE.png'
img.save(out_path, 'PNG')
import os
print(f"OK saved {out_path} ({os.path.getsize(out_path)} bytes, {img.size})")
