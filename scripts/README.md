# ECONARES Scripts — Gmail ↔ HubSpot Integration

This folder holds the scripts that wire the ECONARES Gmail account
(`rzh24.econares@gmail.com`) to the ECONARES HubSpot portal
(portal id 245683432).

All scripts use the same auth pattern: secrets live in `~/.hermes/.env`
and/or `~/.hermes/google_*.json`. Nothing in this folder should contain
real tokens or client secrets.

## Files

| Script | Purpose | Run frequency |
|--------|---------|---------------|
| `bootstrap_gmail_oauth.py` | One-shot OAuth consent flow. Prompts browser, writes `~/.hermes/google_token.json` + `~/.hermes/google_client_secret.json`. | Once (re-run only if token revoked) |
| `gmail_starred_hubspot_sync.py` | The main sync. Reads Gmail starred messages, creates HubSpot tasks prefixed `[Gmail ★]`, dedupes by subject. | Daily (cron) or manual |
| `hubspot_smoketest.py` | 3-call health check: portal info, `[Gmail*]` task search, known company fetch. | Ad hoc / pre-deploy |
| `hubspot_token_health.py` | Verifies token + all 4 required object scopes (contacts, companies, deals, tasks). Exits non-zero on failure. | Daily (cron) |

## OAuth flow (one-time setup)

```bash
# 1. Get a client_secret_*.json from Google Cloud Console:
#    https://console.cloud.google.com/apis/credentials
#    → Create Credentials → OAuth client ID → Application type: Desktop app
#    → Download JSON
#
# 2. Run the bootstrap (opens browser for consent):
python bootstrap_gmail_oauth.py --client-secret /path/to/client_secret_xxx.apps.googleusercontent.com.json
```

What you should see in the consent screen:
- App name: whatever you named it in Google Cloud Console
- Requesting permission: "Read your email" (gmail.readonly scope only)
- Account: confirm it matches the ECONARES mailbox (e.g. rzh24.econares@gmail.com)

After consent, the script:
- Persists refresh_token + access_token to `~/.hermes/google_token.json`
- Copies the client secret to `~/.hermes/google_client_secret.json`
- Locks both files to the current user only (icacls on Windows, chmod 600 on POSIX)
- Verifies the token by calling `gmail.users.getProfile`
- Prints the bound Gmail account + mailbox size — confirm these

## Revocation

If the machine is compromised, or you want to rotate the token:
- Visit https://myaccount.google.com/permissions and revoke "ECONARES Gmail Sync"
- Delete `~/.hermes/google_token.json` and `~/.hermes/google_client_secret.json`
- Re-run the bootstrap

## Sync script usage

```bash
# Normal run — refresh token, sync last 7 days, create tasks, send Telegram summary
python gmail_starred_hubspot_sync.py

# Read-only — what would it do, without writing?
python gmail_starred_hubspot_sync.py --dry-run

# Create tasks but don't send the Telegram summary
python gmail_starred_hubspot_sync.py --no-telegram

# Look back further (e.g. 30 days for first-time catch-up)
python gmail_starred_hubspot_sync.py --days 30
```

Log file: `~/ECONARES_WORKSPACE/logs/gmail_hubspot_sync.log`
Synced-IDs file: `~/ECONARES_WORKSPACE/synced_gmail_threads.txt` (auto-created)

## Scheduling

Recommended: run the sync once daily in the morning (e.g. 7:30 AM, before
the morning brief cron at 8:00 AM). Two cron jobs to register:

```bash
# Daily health check (lightweight, 1-2s)
hermes cron create "0 7 * * *" \
  --prompt "Run hubspot_token_health.py and report any FAIL" \
  --workdir "C:\\Users\\reyma\\Documents\\ECONARES_WORKSPACE\\scripts"

# Daily sync (only run if health check passed)
hermes cron create "30 7 * * *" \
  --prompt "Run gmail_starred_hubspot_sync.py. If it fails, report the error." \
  --workdir "C:\\Users\\reyma\\Documents\\ECONARES_WORKSPACE\\scripts"
```

## Required scopes (Google + HubSpot)

**Google OAuth (gmail_starred_hubspot_sync.py):**
- `https://www.googleapis.com/auth/gmail.readonly` (only — no modify, no send)

**HubSpot Private App (all HubSpot scripts):**
- `crm.objects.contacts.read` + `.write`
- `crm.objects.companies.read` + `.write`
- `crm.objects.deals.read` + `.write`
- `crm.objects.tasks.read` + `.write`

**Principle of least privilege:** if a script doesn't need to write, give
it only `.read`. Today both Gmail and HubSpot sides have the minimum
required.
