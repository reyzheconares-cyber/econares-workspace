#!/usr/bin/env python3
"""
ECONARES Competitor Price Intelligence
Weekly Report Generator for Coal and Nickel Markets
Phase 8 - Market Monitoring System
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

WORKSPACE = "/home/mauiclaw/ECONARES_WORKSPACE"
INTEL_DIR = f"{WORKSPACE}/intel"
COMPETITOR_PRICES_FILE = f"{INTEL_DIR}/competitor_prices.json"
WEEKLY_REPORT_FILE = f"{INTEL_DIR}/weekly_report_{datetime.now().strftime('%Y-W%W')}.txt"
TELEGRAM_CONFIG_FILE = f"{WORKSPACE}/telegram_config.json"

# Market data structure
MARKETS = {
    "coal": {
        "gc_newcastle_6000_nar": {
            "name": "GC Newcastle 6000 NAR",
            "unit": "USD/MT",
            "region": "Australia",
            " competitors": ["Newcastle Futures", "ICE", "globalCOAL"]
        },
        "indonesian_5800_gar": {
            "name": "Indonesian 5800 GAR",
            "unit": "USD/MT",
            "region": "Indonesia",
            "competitors": ["Samar Pacific", "Semirara", "HBA Reference"]
        },
        "indonesian_5500_gar": {
            "name": "Indonesian 5500 GAR",
            "unit": "USD/MT",
            "region": "Indonesia",
            "competitors": ["Samar Pacific", "Berau Coal", "Kideco"]
        }
    },
    "nickel": {
        "nickel_ore_15_fe": {
            "name": "Nickel Ore 1.5% Fe",
            "unit": "USD/MT",
            "region": "Indonesia",
            "competitors": ["Huayou Cobalt", "Brunp", "CATL", "Tsingshan"]
        },
        "nickel_ore_18_fe": {
            "name": "Nickel Ore 1.8% Fe",
            "unit": "USD/MT",
            "region": "Indonesia",
            "competitors": ["Huayou Cobalt", "Brunp", "CATL", "Tsingshan"]
        }
    }
}

# Known competitor references
COMPETITORS = {
    "Samar Pacific": {"type": "coal", "region": "Philippines", "notes": "Semirara Mining subsidiary"},
    "Semirara Mining": {"type": "coal", "region": "Philippines", "notes": "Major PH coal producer"},
    "Berau Coal": {"type": "coal", "region": "Indonesia", "notes": "Berau basin producer"},
    "Kideco": {"type": "coal", "region": "Indonesia", "notes": "East Kalimantan producer"},
    "HBA Reference": {"type": "coal", "region": "Indonesia", "notes": "HPB/ICB index reference"},
    "globalCOAL": {"type": "coal", "region": "Global", "notes": "Coal trading platform"},
    "ICE Newcastle": {"type": "coal", "region": "Australia", "notes": "Futures exchange"},
    "Huayou Cobalt": {"type": "nickel", "region": "China", "notes": "Major nickel importer"},
    "Brunp": {"type": "nickel", "region": "China", "notes": "CATL subsidiary, nickel recycler"},
    "CATL": {"type": "nickel", "region": "China", "notes": "Largest battery manufacturer"},
    "Tsingshan stainless": {"type": "nickel", "region": "China", "notes": "Major stainless steel mill"},
    "Jorge Griffith": {"type": "coal", "region": "Colombia", "notes": "Reference trader"}
}

# ============================================================================
# DATA MANAGEMENT
# ============================================================================

def ensure_dirs():
    """Ensure required directories exist."""
    os.makedirs(INTEL_DIR, exist_ok=True)

def load_price_history() -> Dict:
    """Load historical price data."""
    if os.path.exists(COMPETITOR_PRICES_FILE):
        with open(COMPETITOR_PRICES_FILE, 'r') as f:
            return json.load(f)
    return {"coal": {}, "nickel": {}, "last_updated": None}

def save_price_history(data: Dict) -> None:
    """Save price history."""
    data["last_updated"] = datetime.now().isoformat()
    with open(COMPETITOR_PRICES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def update_price(market: str, commodity_key: str, price: float, 
                 competitor: str = "market", trend: str = "stable") -> None:
    """Update a price point in history."""
    data = load_price_history()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if market not in data:
        data[market] = {}
    
    if commodity_key not in data[market]:
        data[market][commodity_key] = {"prices": {}, "current": None}
    
    data[market][commodity_key]["prices"][today] = {
        "price": price,
        "competitor": competitor,
        "trend": trend
    }
    data[market][commodity_key]["current"] = {
        "price": price,
        "competitor": competitor,
        "trend": trend,
        "date": today
    }
    
    save_price_history(data)

def get_current_prices() -> Dict:
    """Get current prices for all markets."""
    return load_price_history()

def get_price_trend(market: str, commodity_key: str) -> str:
    """Calculate price trend based on 7-day history."""
    data = load_price_history()
    
    if market not in data or commodity_key not in data[market]:
        return "unknown"
    
    prices = data[market][commodity_key]["prices"]
    if len(prices) < 2:
        return "stable"
    
    sorted_dates = sorted(prices.keys())
    recent = [float(prices[d]["price"]) for d in sorted_dates[-7:]]
    
    if len(recent) >= 2:
        change = recent[-1] - recent[0]
        if change > 1:
            return "rising"
        elif change < -1:
            return "falling"
    return "stable"

# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_weekly_report() -> str:
    """Generate weekly competitor price summary report."""
    ensure_dirs()
    data = load_price_history()
    today = datetime.now().strftime("%Y-%m-%d")
    week = datetime.now().strftime("%Y-W%W")
    
    report = []
    report.append("=" * 70)
    report.append("ECONARES WEEKLY COMPETITOR PRICE INTELLIGENCE REPORT")
    report.append(f"Report Date: {today} | Week: {week}")
    report.append("=" * 70)
    report.append("")
    
    # Coal Section
    report.append("## COAL MARKET SUMMARY")
    report.append("-" * 40)
    
    coal_markets = data.get("coal", {})
    for key, info in MARKETS["coal"].items():
        current = coal_markets.get(key, {}).get("current")
        trend = get_price_trend("coal", key)
        
        if current:
            report.append(f"\n{info['name']} ({info['region']})")
            report.append(f"  Price: {current['price']} {info['unit']}")
            report.append(f"  Trend (7d): {trend}")
            report.append(f"  Source: {current['competitor']}")
            report.append(f"  Known Competitors: {', '.join(info['competitors'])}")
        else:
            report.append(f"\n{info['name']} - No data available")
    
    # Nickel Section
    report.append("\n")
    report.append("## NICKEL MARKET SUMMARY")
    report.append("-" * 40)
    
    nickel_markets = data.get("nickel", {})
    for key, info in MARKETS["nickel"].items():
        current = nickel_markets.get(key, {}).get("current")
        trend = get_price_trend("nickel", key)
        
        if current:
            report.append(f"\n{info['name']} ({info['region']})")
            report.append(f"  Price: {current['price']} {info['unit']}")
            report.append(f"  Trend (7d): {trend}")
            report.append(f"  Source: {current['competitor']}")
            report.append(f"  Known Offtakers: {', '.join(info['competitors'])}")
        else:
            report.append(f"\n{info['name']} - No data available")
    
    # Competitor Directory
    report.append("\n")
    report.append("## COMPETITOR DIRECTORY")
    report.append("-" * 40)
    
    for name, info in COMPETITORS.items():
        report.append(f"\n{name}")
        report.append(f"  Type: {info['type']} | Region: {info['region']}")
        report.append(f"  Notes: {info['notes']}")
    
    # Footer
    report.append("\n")
    report.append("=" * 70)
    report.append("END OF REPORT")
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append("ECONARES - Philippine Commodities Desk")
    report.append("=" * 70)
    
    report_text = "\n".join(report)
    
    # Save report
    with open(WEEKLY_REPORT_FILE, 'w') as f:
        f.write(report_text)
    
    return report_text

def generate_telegram_summary() -> str:
    """Generate short Telegram-formatted summary."""
    data = load_price_history()
    today = datetime.now().strftime("%Y-%m-%d")
    
    summary = []
    summary.append(f"📊 *ECONARES Weekly Intel - {today}*")
    summary.append("")
    
    # Coal snapshot
    coal_markets = data.get("coal", {})
    if "indonesian_5500_gar" in coal_markets:
        current = coal_markets["indonesian_5500_gar"].get("current")
        if current:
            trend = get_price_trend("coal", "indonesian_5500_gar")
            trend_emoji = "📈" if trend == "rising" else "📉" if trend == "falling" else "➡️"
            summary.append(f"{trend_emoji} Indonesian Coal 5500 GAR: ${current['price']}/MT")
    
    if "indonesian_5800_gar" in coal_markets:
        current = coal_markets["indonesian_5800_gar"].get("current")
        if current:
            trend = get_price_trend("coal", "indonesian_5800_gar")
            trend_emoji = "📈" if trend == "rising" else "📉" if trend == "falling" else "➡️"
            summary.append(f"{trend_emoji} Indonesian Coal 5800 GAR: ${current['price']}/MT")
    
    # Nickel snapshot
    nickel_markets = data.get("nickel", {})
    if "nickel_ore_15_fe" in nickel_markets:
        current = nickel_markets["nickel_ore_15_fe"].get("current")
        if current:
            trend = get_price_trend("nickel", "nickel_ore_15_fe")
            trend_emoji = "📈" if trend == "rising" else "📉" if trend == "falling" else "➡️"
            summary.append(f"{trend_emoji} Nickel Ore 1.5% Fe: ${current['price']}/MT CIF China")
    
    summary.append("")
    summary.append("📋 Full report in intel/ folder")
    
    return "\n".join(summary)

# ============================================================================
# CLI INTERFACE
# ============================================================================

def print_current_intel():
    """Print current intelligence summary."""
    data = load_price_history()
    print("\n=== ECONARES COMPETITOR INTEL ===")
    print(f"Last Updated: {data.get('last_updated', 'Never')}")
    print("\nCOAL:")
    for key, info in MARKETS["coal"].items():
        current = data.get("coal", {}).get(key, {}).get("current")
        if current:
            trend = get_price_trend("coal", key)
            print(f"  {info['name']}: ${current['price']} ({trend})")
        else:
            print(f"  {info['name']}: No data")
    
    print("\nNICKEL:")
    for key, info in MARKETS["nickel"].items():
        current = data.get("nickel", {}).get(key, {}).get("current")
        if current:
            trend = get_price_trend("nickel", key)
            print(f"  {info['name']}: ${current['price']} ({trend})")
        else:
            print(f"  {info['name']}: No data")

def main():
    """Main CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ECONARES Competitor Intelligence")
    parser.add_argument("--status", action="store_true", help="Show current intel")
    parser.add_argument("--update", nargs=3, metavar=("MARKET", "COMMODITY_KEY", "PRICE"),
                        help="Update a price (coal/nickel, key, price)")
    parser.add_argument("--report", action="store_true", help="Generate weekly report")
    parser.add_argument("--telegram", action="store_true", help="Generate Telegram summary")
    
    args = parser.parse_args()
    
    ensure_dirs()
    
    if args.status:
        print_current_intel()
    elif args.update:
        market, key, price = args.update
        update_price(market, key, float(price))
        print(f"Updated {market}/{key} = ${price}")
    elif args.report:
        report = generate_weekly_report()
        print(f"\nReport saved to: {WEEKLY_REPORT_FILE}")
        print("\n" + report)
    elif args.telegram:
        summary = generate_telegram_summary()
        print(summary)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
