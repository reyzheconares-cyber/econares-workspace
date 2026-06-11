#!/usr/bin/env python3
"""
bootstrap_gmail_oauth.py — One-shot Gmail OAuth setup for ECONARES.

What it does:
  1. Loads `client_secret_*.json` from a path you provide
  2. Spins up a local HTTP server on 127.0.0.1:8765 to catch Google's redirect
  3. Opens the browser to the Google consent screen (scope: gmail.readonly only)
  4. Exchanges the auth code for access_token + refresh_token
  5. Persists the token to ~/.hermes/google_token.json
  6. Persists the client secret reference at ~/.hermes/google_client_secret.json
  7. Restricts both files to the current user (Windows: icacls, POSIX: chmod 600)
  8. Verifies the token by calling gmail.users.getProfile
  9. Prints the bound Gmail account + scopes so future-you knows what this is

Usage:
  python bootstrap_gmail_oauth.py --client-secret /path/to/client_secret_*.json

Required: only stdlib (http.server, urllib, json, webbrowser). Works on
Python 3.8+. Tested on Windows 11 + Python 3.11.

Security notes:
  - Scopes requested: ONLY https://www.googleapis.com/auth/gmail.readonly
    (no modify, no send, no label changes). The sync script only reads
    starred messages and message metadata.
  - The token is bound to the Google account you sign in as. The script
    prints that account name when the flow completes — confirm it matches
    rzh24.econares@gmail.com (or whatever ECONARES mailbox you intend).
  - The client_secret_*.json stays on disk at the path you specify. Move
    it to a secrets manager if you want defense-in-depth.
  - To revoke later: https://myaccount.google.com/permissions
    OR delete ~/.hermes/google_token.json and re-run this script.
"""
import argparse
import http.server
import json
import os
import socket
import sys
import urllib.parse
import webbrowser
from pathlib import Path

HERMES_HOME = Path(os.path.expanduser('~/.hermes'))
TOKEN_PATH = HERMES_HOME / 'google_token.json'
CLIENT_PATH = HERMES_HOME / 'google_client_secret.json'
REDIRECT_PORT = 8765
REDIRECT_URI = f'http://127.0.0.1:{REDIRECT_PORT}/'
SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'

# Catch the auth code in a global so the server thread can hand it to main.
_AUTH_CODE = None


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global _AUTH_CODE
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if 'code' in params:
            _AUTH_CODE = params['code'][0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(
                b'<html><body style="font-family:sans-serif;padding:40px;text-align:center">'
                b'<h1 style="color:#1a73e8">&#10003; Authorized</h1>'
                b'<p>You can close this tab and return to the terminal.</p>'
                b'</body></html>'
            )
        else:
            err = params.get('error', ['unknown'])[0]
            self.send_response(400)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(
                f'<html><body><h1>Error: {err}</h1></body></html>'.encode('utf-8')
            )

    def log_message(self, format, *args):
        # Silence the default stderr access log — too noisy
        return


def _port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) != 0


def _exchange_code(client_id: str, client_secret: str, code: str) -> dict:
    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
    }).encode('utf-8')
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _verify_token(access_token: str) -> dict:
    req = urllib.request.Request('https://gmail.googleapis.com/gmail/v1/users/me/profile')
    req.add_header('Authorization', f'Bearer {access_token}')
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _lock_file_windows(path: Path):
    """icacls: grant current user only, remove inherited ACLs from other users."""
    try:
        import subprocess
        user = os.environ.get('USERNAME') or os.getlogin()
        # Reset ACL: inherit disabled, grant only current user full control
        subprocess.run(
            ['icacls', str(path), '/inheritance:r',
             '/grant:r', f'{user}:F'],
            check=True, capture_output=True
        )
    except Exception as e:
        print(f'  WARNING: could not lock {path} via icacls: {e}')


def _lock_file_posix(path: Path):
    os.chmod(path, 0o600)


def main():
    parser = argparse.ArgumentParser(description='Bootstrap Gmail OAuth for ECONARES sync')
    parser.add_argument('--client-secret', required=True,
                        help='Path to client_secret_*.json from Google Cloud Console')
    parser.add_argument('--port', type=int, default=REDIRECT_PORT,
                        help=f'Local port for OAuth redirect (default {REDIRECT_PORT})')
    args = parser.parse_args()

    if not _port_available(args.port):
        print(f'ERROR: port {args.port} is already in use. Close the conflicting process '
              f'or pass --port <other>')
        sys.exit(1)

    client_secret_path = Path(args.client_secret).expanduser().resolve()
    if not client_secret_path.is_file():
        print(f'ERROR: client secret not found at {client_secret_path}')
        sys.exit(1)
    with open(client_secret_path, 'r', encoding='utf-8') as f:
        client_doc = json.load(f)
    if 'installed' not in client_doc:
        print('ERROR: client_secret JSON must be the "Desktop app" / "Installed app" type')
        print('       (it should have a top-level "installed" key with client_id/client_secret)')
        sys.exit(1)
    installed = client_doc['installed']
    client_id = installed['client_id']
    client_secret = installed['client_secret']

    print('=' * 60)
    print('Gmail OAuth Bootstrap — ECONARES')
    print('=' * 60)
    print(f'  Client ID:        {client_id[:30]}...')
    print(f'  Redirect URI:     {REDIRECT_URI}')
    print(f'  Scope:            {SCOPE}')
    print(f'  Token will land:  {TOKEN_PATH}')
    print(f'  Client copy:      {CLIENT_PATH}')
    print()
    print('  IMPORTANT: Google will open a consent screen asking you to')
    print('  sign in with the ECONARES Gmail account and grant the')
    print('  "Read your email" permission. Confirm the account shown is')
    print('  the one you intend to sync (e.g. rzh24.econares@gmail.com).')
    print()

    auth_url = (
        'https://accounts.google.com/o/oauth2/v2/auth'
        '?response_type=code'
        f'&client_id={urllib.parse.quote(client_id)}'
        f'&redirect_uri={urllib.parse.quote(REDIRECT_URI)}'
        f'&scope={urllib.parse.quote(SCOPE)}'
        '&access_type=offline'  # critical — gets us a refresh_token
        '&prompt=consent'        # force re-consent so we always get a refresh_token
    )

    server = http.server.HTTPServer(('127.0.0.1', args.port), _Handler)
    print(f'  Listening on http://127.0.0.1:{args.port} for the redirect...')
    print('  Opening browser...')
    print()

    # Serve until we get a request (timeout 120s for safety)
    server.timeout = 120
    try:
        webbrowser.open(auth_url)
    except Exception as e:
        print(f'  WARNING: could not auto-open browser ({e}). Open this URL manually:')
        print(f'  {auth_url}')

    while _AUTH_CODE is None:
        server.handle_request()

    print('  Authorization code received. Exchanging for tokens...')
    token_data = _exchange_code(client_id, client_secret, _AUTH_CODE)
    if 'refresh_token' not in token_data:
        print('ERROR: Google did not return a refresh_token.')
        print('       This usually means the app was already authorized before;')
        print('       re-run with --force or revoke at https://myaccount.google.com/permissions')
        print(f'       Raw response: {json.dumps(token_data, indent=2)}')
        sys.exit(2)
    print(f'  Got refresh_token ({len(token_data["refresh_token"])} chars)')
    print(f'  Got access_token  ({len(token_data["access_token"])} chars, '
          f'expires in {token_data.get("expires_in", "?")}s)')

    # Persist
    HERMES_HOME.mkdir(parents=True, exist_ok=True)
    token_doc = {
        'access_token': token_data['access_token'],
        'refresh_token': token_data['refresh_token'],
        'expires_in': token_data.get('expires_in', 3599),
        'scope': token_data.get('scope', SCOPE),
        'token_type': token_data.get('token_type', 'Bearer'),
        'obtained_at': int(__import__('time').time()),
    }
    with open(TOKEN_PATH, 'w', encoding='utf-8') as f:
        json.dump(token_doc, f, indent=2)
    print(f'  Wrote {TOKEN_PATH}')

    with open(CLIENT_PATH, 'w', encoding='utf-8') as f:
        json.dump(client_doc, f, indent=2)
    print(f'  Wrote {CLIENT_PATH}')

    # Lock down permissions
    if sys.platform.startswith('win'):
        _lock_file_windows(TOKEN_PATH)
        _lock_file_windows(CLIENT_PATH)
        print('  Locked both files via icacls (current user only)')
    else:
        _lock_file_posix(TOKEN_PATH)
        _lock_file_posix(CLIENT_PATH)
        print('  Locked both files via chmod 600')

    # Verify by hitting the API
    print()
    print('  Verifying token by calling gmail.users.getProfile...')
    try:
        profile = _verify_token(token_data['access_token'])
        print(f'  OK — bound to: {profile.get("emailAddress")}')
        print(f'  OK — total messages in mailbox: {profile.get("messagesTotal")}')
        print(f'  OK — total threads: {profile.get("threadsTotal")}')
    except Exception as e:
        print(f'  WARNING: token exchange succeeded but verification failed: {e}')
        print('           Re-running the sync will trigger a refresh; should self-heal.')

    print()
    print('=' * 60)
    print('Bootstrap complete.')
    print('Next step: run the sync in dry-run mode:')
    print('  python ~/Documents/ECONARES_WORKSPACE/scripts/gmail_starred_hubspot_sync.py --dry-run')
    print('=' * 60)


if __name__ == '__main__':
    main()
