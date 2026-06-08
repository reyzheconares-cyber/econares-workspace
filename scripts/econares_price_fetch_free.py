#!/usr/bin/env python3
"""
econares_price_fetch_free.py
============================
Fetches commodity prices for the ECONARES morning brief from FREE public sources.
No paid APIs, no subscriptions, no Tavily/Brave required.

Source priority (highest to lowest):
  1. Manual override file     — RZH's authoritative sales basis (always wins)
  2. Trading Economics        — free public pages, live market direction
  3. Yahoo Finance v8 API     — backup, may be rate-limited
  4. Mysteel public pages     — best-effort scrape
  5. ESDM HBA                 — Indonesian coal reference (best-effort)
  6. May 2026 benchmarks      — final fallback (always available)

Usage:
  # JSON output (for morning brief pipeline)
  python3 econares_price_fetch_free.py

  # Human-readable text
  python3 econares_price_fetch_free.py --format text

  # Bypass cache (force fresh fetch)
  python3 econares_price_fetch_free.py --no-cache

  # Set a manual price override
  python3 econares_price_fetch_free.py --set coal "USD 88/MT FOB Indo GAR 5500"
  python3 econares_price_fetch_free.py --set nickel "USD 45/MT CIF China 1.8%"

  # Show the manual file template
  python3 econares_price_fetch_free.py --show-template

  # Clear cache
  python3 econares_price_fetch_free.py --clear-cache

Output:
  - Writes price cache to ~/.hermes/econares/price_cache.json (TTL: 6h)
  - Manual overrides persist at ~/.hermes/econares/manual_prices.json
  - stdout: JSON dict of {commodity: {description, source, ...}}
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────
ECONARES_CONFIG_DIR = Path.home() / ".hermes" / "econares"
MANUAL_FILE = ECONARES_CONFIG_DIR / "manual_prices.json"
CACHE_FILE = ECONARES_CONFIG_DIR / "price_cache.json"
CACHE_TTL_HOURS = 6

# Last-resort benchmarks (May 2026) — used ONLY when every other source fails
FALLBACK_BENCHMARKS = {
    'nickel':    'USD 42–46/MT CIF China (1.8% Ni) — DMO cuts tightening supply',
    'coal':      'USD 84–98/MT FOB Indonesia (GAR 5500); PH landed ~$108–115/MT',
    'copper':    'USD 85–95/MT mined (0.5% Cu basis); LME ~$14,500/t',
    'diesel':    'USD 600–620/MT FOB Korea (MOPS 10ppm)',
    'pks':       'USD 95–110/MT FOB Indonesia (PKS spot)',
    'woodchips': 'USD 130–160/m³ CIF China (tropical HW chips; Q1 log imports -11% YoY)',
    'cpo':       'USD 1,039–1,105/MT FOB Malaysia (MDEX); ID $1,090–1,215/MT (B50 support)',
}

# Trading Economics commodity paths — covers 5 of 7 ECONARES commodities for free
# Returns CFD-tracked futures prices; useful as market DIRECTION indicators
TRADING_ECONOMICS = {
    'copper':    {'path': 'copper',       'unit_hint': 'USD/Lbs',  'note': 'LME 3M proxy (CFD)'},
    'nickel':    {'path': 'nickel',       'unit_hint': 'USD/T',    'note': 'LME 3M nickel metal (CFD)'},
    'coal':      {'path': 'coal',         'unit_hint': 'USD/T',    'note': 'Newcastle thermal coal (CFD)'},
    'diesel':    {'path': 'heating-oil',  'unit_hint': 'USD/Gal',  'note': 'NY Harbor ULSD — direction proxy for Asia gasoil'},
    'cpo':       {'path': 'palm-oil',     'unit_hint': 'MYR/T',    'note': 'Malaysian CPO futures (Bursa Malaysia)'},
}

# Yahoo Finance v8 chart API — backup, may be rate-limited (429)
YAHOO_TICKERS = {
    'copper_lb':  'HG=F',  # COMEX Copper, USD/lb → ×2204.62 = USD/MT
    'heating_gal':'HO=F',  # NY Harbor ULSD, USD/gal → ×317.98 = USD/MT
    'crude_bbl':  'CL=F',  # WTI Crude, USD/bbl
    'alum_mt':    'ALI=F', # Aluminum, USD/MT
}

# Mysteel public pages — Chinese, JS-rendered, best-effort
MYSTEEL_URLS = {
    'nickel_ore':         'https://www.mysteel.com/nickel/',
    'copper_concentrate': 'https://www.mysteel.com/copper/',
}

# ESDM (Indonesian Ministry of Energy & Mineral Resources) — official HBA price
ESDM_URL = 'https://www.minerba.esdm.go.id/'

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'


# ── MANUAL OVERRIDE FILE ──────────────────────────────────────
def load_manual():
    """Load RZH's manual price overrides. Always win over auto-fetched."""
    if not MANUAL_FILE.exists():
        return {}
    try:
        return json.loads(MANUAL_FILE.read_text())
    except Exception as e:
        print(f'⚠️  Manual file malformed: {e}', file=sys.stderr)
        return {}


def save_manual(data):
    """Persist manual overrides."""
    ECONARES_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    MANUAL_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f'✅ Manual prices saved → {MANUAL_FILE}')


# ── CACHE ─────────────────────────────────────────────────────
def load_cache():
    """Return cached prices if fresh (< CACHE_TTL_HOURS old), else None."""
    if not CACHE_FILE.exists():
        return None
    try:
        data = json.loads(CACHE_FILE.read_text())
        fetched = datetime.fromisoformat(data.get('fetched_at', '2000-01-01'))
        if datetime.now() - fetched < timedelta(hours=CACHE_TTL_HOURS):
            return data.get('prices', {})
    except Exception:
        pass
    return None


def save_cache(prices):
    """Persist successful fetches."""
    ECONARES_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({
        'fetched_at': datetime.now().isoformat(),
        'prices': prices,
    }, indent=2, ensure_ascii=False))


# ── TRADING ECONOMICS (primary free source) ──────────────────
def fetch_trading_economics(commodity_key):
    """Fetch commodity price from Trading Economics public page.

    Trading Economics publishes free public pages with a structured meta
    description containing: price, unit, date, % change, period comparisons.

    Example meta: "Copper fell to 6.26 USD/Lbs on June 8, 2026, down 0.01%..."

    Returns dict {description, source, price, unit, change_pct, as_of, ...} or None.
    """
    cfg = TRADING_ECONOMICS.get(commodity_key)
    if not cfg:
        return None
    url = f'https://tradingeconomics.com/commodity/{cfg["path"]}'
    try:
        r = subprocess.run(
            ['curl', '-s', '-L', '-A', USER_AGENT,
             '-H', 'Accept: text/html',
             '--max-time', '12', url],
            capture_output=True, text=True, timeout=15
        )
        if r.returncode != 0 or not r.stdout:
            return None
        m = re.search(r'<meta id="metaDesc"[^>]*content="([^"]+)"', r.stdout)
        if not m:
            return None
        meta = m.group(1)

        # Parse the meta description for price + change
        # Pattern: "<name> <rose|fell> to <PRICE> <UNIT> on <DATE>, <up|down> <X.XX>%"
        price_match = re.search(
            r'(?:rose|fell)\s+to\s+([\d,]+\.?\d*)\s*(\w+/[A-Za-z]+)\s+on\s+'
            r'(\w+\s+\d+,\s+\d{4}),\s*(up|down)\s+([\d.]+)%',
            meta
        )
        if not price_match:
            return None
        price_val = float(price_match.group(1).replace(',', ''))
        unit = price_match.group(2)
        date_str = price_match.group(3)
        direction = price_match.group(4)
        change_pct = float(price_match.group(5))
        if direction == 'down':
            change_pct = -change_pct

        arrow = '↑' if change_pct > 0 else ('↓' if change_pct < 0 else '→')
        note = cfg.get('note', '')
        return {
            'description': (
                f'{commodity_key.title()} (TE): {price_val:,.2f} {unit} '
                f'({arrow}{abs(change_pct):.2f}% on {date_str}) — {note}'
            ),
            'source': f'Trading Economics ({cfg["path"]})',
            'price_value': price_val,
            'unit': unit,
            'change_pct': round(change_pct, 2),
            'as_of': date_str,
            'note': note,
        }
    except Exception as e:
        print(f'⚠️  TE {commodity_key} failed: {e}', file=sys.stderr)
    return None


# ── YAHOO FINANCE (backup) ────────────────────────────────────
def fetch_yahoo(ticker, max_retries=1):
    """Fetch current price from Yahoo Finance v8 chart API. No auth required.

    Handles 429 rate limits with a single retry after a backoff.

    Returns dict {price, currency, change_pct, source, as_of} or None on failure.
    """
    for attempt in range(max_retries + 1):
        try:
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d'
            r = subprocess.run(
                ['curl', '-s', '-A', USER_AGENT,
                 '-H', 'Accept: application/json,text/plain,*/*',
                 '-H', 'Accept-Language: en-US,en;q=0.9',
                 '-H', 'Referer: https://finance.yahoo.com/',
                 '--max-time', '12', url],
                capture_output=True, text=True, timeout=15
            )
            if r.returncode != 0 or not r.stdout.strip():
                return None
            # Check for rate limit
            if 'Too Many Requests' in r.stdout or r.status_code if hasattr(r, 'status_code') else False:
                if attempt < max_retries:
                    time.sleep(15)
                    continue
                return None
            data = json.loads(r.stdout)
            result = data.get('chart', {}).get('result', [])
            if not result:
                return None
            meta = result[0].get('meta', {})
            price = meta.get('regularMarketPrice')
            prev = meta.get('chartPreviousClose', price)
            currency = meta.get('currency', 'USD')
            name = meta.get('longName') or meta.get('symbol', ticker)
            if price is None:
                return None
            change = ((price - prev) / prev * 100) if prev else 0
            return {
                'price': round(float(price), 4),
                'currency': currency,
                'change_pct': round(float(change), 2),
                'source': f'Yahoo Finance ({name})',
                'as_of': datetime.now().strftime('%Y-%m-%d %H:%M'),
            }
        except json.JSONDecodeError:
            # Empty/rate-limit response
            if attempt < max_retries:
                time.sleep(15)
                continue
            return None
        except Exception as e:
            print(f'⚠️  Yahoo {ticker} failed: {e}', file=sys.stderr)
            return None
    return None


# ── MYSTEEL (best-effort scrape) ─────────────────────────────
def fetch_mysteel(query_key):
    """Attempt to extract any visible price from Mysteel public page.

    NOTE: Mysteel public pages are mostly Chinese HTML, JS-rendered, and
    behind soft paywalls. Best-effort — failure is expected.
    """
    url = MYSTEEL_URLS.get(query_key)
    if not url:
        return None
    try:
        r = subprocess.run(
            ['curl', '-s', '-L', '-A', USER_AGENT,
             '-H', 'Accept: text/html,application/xhtml+xml',
             '-H', 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8',
             '--max-time', '10', url],
            capture_output=True, text=True, timeout=12
        )
        if r.returncode != 0 or not r.stdout:
            return None
        text = r.stdout
        nickel_match = re.search(
            r'1\.8%[^¥$元]{0,80}?([¥$]\s*[\d,]+(?:\.\d+)?)|'
            r'([¥$]\s*[\d,]+(?:\.\d+)?)[^¥$元]{0,80}?1\.8%',
            text
        )
        if nickel_match:
            price_str = nickel_match.group(1) or nickel_match.group(2)
            return {
                'description': f'Mysteel: 1.8% nickel ore {price_str}',
                'source': 'Mysteel.com',
                'raw_snippet': nickel_match.group(0)[:200],
                'as_of': datetime.now().strftime('%Y-%m-%d %H:%M'),
            }
    except Exception as e:
        print(f'⚠️  Mysteel {query_key} failed: {e}', file=sys.stderr)
    return None


# ── ESDM HBA (Indonesian coal reference) ─────────────────────
def fetch_esdm_hba():
    """Fetch Indonesian coal HBA reference price from ESDM website."""
    try:
        r = subprocess.run(
            ['curl', '-s', '-L', '-A', USER_AGENT,
             '-H', 'Accept: text/html',
             '-H', 'Accept-Language: id,en;q=0.9',
             '--max-time', '10', ESDM_URL],
            capture_output=True, text=True, timeout=12
        )
        if r.returncode != 0 or not r.stdout:
            return None
        text = r.stdout
        hba_match = re.search(
            r'HBA[^$]{0,40}?USD\s*([\d,]+(?:\.\d+)?)|'
            r'USD\s*([\d,]+(?:\.\d+)?)[^$]{0,40}?(?:per\s*ton|/ton)',
            text, re.IGNORECASE
        )
        if hba_match:
            price_str = hba_match.group(1) or hba_match.group(2)
            try:
                hba_value = float(price_str.replace(',', ''))
                gar5500_est = round(hba_value * 0.95, 2)
                return {
                    'description': (
                        f'ESDM HBA: USD {hba_value:.2f}/ton (GAR 6322); '
                        f'est. GAR 5500 ~USD {gar5500_est:.2f}/ton FOB'
                    ),
                    'source': 'minerba.esdm.go.id (HBA)',
                    'hba_value': hba_value,
                    'gar5500_estimate': gar5500_est,
                    'as_of': datetime.now().strftime('%Y-%m-%d'),
                }
            except ValueError:
                pass
    except Exception as e:
        print(f'⚠️  ESDM HBA failed: {e}', file=sys.stderr)
    return None


# ── MAIN FETCH ORCHESTRATOR ──────────────────────────────────
def fetch_all(use_cache=True, verbose=True):
    """Fetch all commodity prices using the priority chain.

    Returns: dict {commodity: {description, source, ...}}
    """
    if use_cache:
        cached = load_cache()
        if cached:
            if verbose:
                print('📦 Using cached prices (< 6h old)', file=sys.stderr)
            return cached

    prices = {}
    sources_used = []

    # 1. Trading Economics (primary free source — covers 5/7 commodities)
    if verbose: print('📡 Trading Economics (primary)...', file=sys.stderr)
    for commodity_key in TRADING_ECONOMICS:
        data = fetch_trading_economics(commodity_key)
        if data:
            prices[commodity_key] = data
            sources_used.append(f'TE-{commodity_key}')
        # Small delay to be polite
        time.sleep(0.5)

    # 2. Yahoo Finance (backup — only fills in commodities TE didn't cover)
    te_covered = set(TRADING_ECONOMICS.keys())
    yahoo_needs = []
    if 'copper' not in prices: yahoo_needs.append(('copper', 'HG=F'))
    if 'diesel' not in prices: yahoo_needs.append(('diesel', 'HO=F'))
    if yahoo_needs and verbose:
        print('📡 Yahoo Finance (backup for missing commodities)...', file=sys.stderr)
    for commodity, ticker in yahoo_needs:
        data = fetch_yahoo(ticker, max_retries=1)
        if data:
            if commodity == 'copper':
                usd_per_mt = data['price'] * 2204.62
                change = data['change_pct']
                arrow = '↑' if change > 0 else ('↓' if change < 0 else '→')
                prices['copper'] = {
                    'description': (
                        f'LME/COMEX Cu (Yahoo): USD {usd_per_mt:,.0f}/MT '
                        f'({arrow}{abs(change):.2f}% via HG=F ${data["price"]:.2f}/lb)'
                    ),
                    'source': 'Yahoo Finance (HG=F)',
                    'raw_value_usd_per_mt': round(usd_per_mt, 2),
                    'change_pct': change,
                    'as_of': data['as_of'],
                }
                sources_used.append('Yahoo-copper')
            elif commodity == 'diesel':
                usd_per_mt = data['price'] * 317.98
                change = data['change_pct']
                arrow = '↑' if change > 0 else ('↓' if change < 0 else '→')
                prices['diesel'] = {
                    'description': (
                        f'Diesel proxy (NY Harbor ULSD): USD {usd_per_mt:,.0f}/MT '
                        f'({arrow}{abs(change):.2f}% via HO=F ${data["price"]:.3f}/gal)'
                    ),
                    'source': 'Yahoo Finance (HO=F)',
                    'raw_value_usd_per_mt': round(usd_per_mt, 2),
                    'change_pct': change,
                    'as_of': data['as_of'],
                    'note': 'NY Harbor ULSD — direction proxy for Asia gasoil',
                }
                sources_used.append('Yahoo-diesel')

    # 3. ESDM HBA (only used if TE didn't already give us coal)
    if 'coal' not in prices:
        if verbose: print('📡 ESDM HBA (Indonesian coal ref)...', file=sys.stderr)
        hba = fetch_esdm_hba()
        if hba:
            prices['coal'] = hba
            sources_used.append('ESDM-HBA')

    # 4. Mysteel (best-effort — fills nickel if TE didn't)
    if 'nickel' not in prices:
        if verbose: print('📡 Mysteel (best-effort for nickel)...', file=sys.stderr)
        nickel_mysteel = fetch_mysteel('nickel_ore')
        if nickel_mysteel:
            prices['nickel'] = nickel_mysteel
            sources_used.append('Mysteel-nickel')

    # 5. Manual overrides (always win — overwrite any auto-fetched for set commodities)
    manual = load_manual()
    if manual:
        for k, v in manual.items():
            prices[k] = {
                'description': v.get('description', str(v)),
                'source': 'Manual override (RZH)',
                'manual_set_at': v.get('set_at', ''),
            }
        sources_used.append(f'Manual({len(manual)})')

    # 6. Fallback benchmarks for anything still missing
    for k, v in FALLBACK_BENCHMARKS.items():
        if k not in prices:
            prices[k] = {
                'description': v,
                'source': 'May 2026 fallback benchmark',
            }
            sources_used.append(f'Fallback-{k}')

    save_cache(prices)
    if verbose:
        print(f'✅ Sources used: {", ".join(sources_used)}', file=sys.stderr)
    return prices


# ── CLI COMMANDS ──────────────────────────────────────────────
def cmd_set(commodity, description):
    if commodity not in FALLBACK_BENCHMARKS:
        valid = ', '.join(FALLBACK_BENCHMARKS.keys())
        print(f'❌ Unknown commodity "{commodity}". Valid: {valid}')
        sys.exit(1)
    manual = load_manual()
    manual[commodity] = {
        'description': description,
        'set_at': datetime.now().isoformat(),
    }
    save_manual(manual)
    print(f'✅ {commodity} = {description}')


def cmd_show_template():
    template = {
        '_comment': 'ECONARES manual price overrides — always win over auto-fetched prices',
        '_format': 'Free text; recommended: "USD XX/MT <basis>"',
        '_update': 'Edit this file directly, or use: --set <commodity> "<description>"',
        'coal':      {'description': 'USD 88/MT FOB Indo GAR 5500', 'set_at': ''},
        'nickel':    {'description': 'USD 45/MT CIF China 1.8% Ni', 'set_at': ''},
        'copper':    {'description': 'USD 90/MT mined 0.5% Cu', 'set_at': ''},
        'diesel':    {'description': 'USD 610/MT FOB Korea 10ppm', 'set_at': ''},
        'pks':       {'description': 'USD 102/MT FOB Indonesia', 'set_at': ''},
        'woodchips': {'description': 'USD 145/m³ CIF China', 'set_at': ''},
        'cpo':       {'description': 'USD 1,075/MT FOB Malaysia', 'set_at': ''},
    }
    print(json.dumps(template, indent=2, ensure_ascii=False))


def cmd_clear_cache():
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
        print(f'🗑️  Cache cleared: {CACHE_FILE}')
    else:
        print('No cache to clear.')


def cmd_format_text(prices):
    print(f'\n📊 ECONARES COMMODITY PRICES — {datetime.now().strftime("%Y-%m-%d %H:%M PHT")}\n')
    print('─' * 70)
    for k, v in prices.items():
        print(f'  {k.upper():12} {v.get("description", "N/A")}')
        print(f'  {"":12} source: {v.get("source", "?")}')
        if 'change_pct' in v:
            cp = v['change_pct']
            arrow = '↑' if cp > 0 else ('↓' if cp < 0 else '→')
            print(f'  {"":12} {arrow} {cp:+.2f}% from prev close')
        print()


# ── MAIN ──────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description='ECONARES free-source price fetcher (Trading Economics + Yahoo + manual + fallback)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format (default: json)')
    parser.add_argument('--no-cache', action='store_true',
                        help='Bypass cache and force fresh fetch')
    parser.add_argument('--set', metavar='COMMODITY=DESC',
                        help='Set manual price override (e.g. --set coal "USD 88/MT FOB")')
    parser.add_argument('--show-template', action='store_true',
                        help='Print manual price file template')
    parser.add_argument('--clear-cache', action='store_true',
                        help='Delete cached prices')
    args = parser.parse_args()

    if args.show_template:
        cmd_show_template()
        return
    if args.clear_cache:
        cmd_clear_cache()
        return
    if args.set:
        if '=' not in args.set:
            print('❌ --set format: --set <commodity> "<description>"')
            print('   Example: --set coal "USD 88/MT FOB Indo GAR 5500"')
            sys.exit(1)
        commodity, description = args.set.split('=', 1)
        cmd_set(commodity.strip(), description.strip())
        return

    prices = fetch_all(use_cache=not args.no_cache, verbose=True)

    if args.format == 'json':
        print(json.dumps(prices, indent=2, ensure_ascii=False))
    else:
        cmd_format_text(prices)


if __name__ == '__main__':
    main()
