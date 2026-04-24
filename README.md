# ECONARES Workspace

Automation scripts and templates for ECONARES trading operations.

## Structure

- `scripts/` — Automation scripts (HubSpot, Gmail, Sheets, DSR)
- `templates/` — LOI/FCO/contract templates
- `.github/workflows/` — GitHub Actions CI/CD

## Scripts

| Script | Purpose |
|--------|---------|
| `econares_morning_brief.py` | Daily 7:30 AM brief via Telegram |
| `econares_evening_dsr.py` | Daily EOD sales report |
| `hubspot_log.py` | Log prospect interactions to HubSpot |

## Setup

1. Copy `.env.example` to `.env` and fill in your API keys
2. Run `pip install requests` for Python scripts

