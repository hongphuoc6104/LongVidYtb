#!/usr/bin/env python3
"""Helper script to generate Colab OAuth URL and exchange authorization code for multi-account setup."""

import argparse
import json
import os
import sys
from importlib import resources
from pathlib import Path

from colab_cli.auth import PUBLIC_SCOPES, REMOTE_REDIRECT_URI
from google_auth_oauthlib.flow import InstalledAppFlow

STORE = Path.home() / ".config/video-pilot/colab"
STATE_DIR = STORE / ".oauth_states"


def get_client_config() -> dict:
    config_resource = resources.files("colab_cli").joinpath("oauth_config.json")
    return json.loads(config_resource.read_text())


def generate_auth_url(account_id: str) -> str:
    STATE_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    client_config = get_client_config()
    flow = InstalledAppFlow.from_client_config(client_config, PUBLIC_SCOPES)
    flow.redirect_uri = REMOTE_REDIRECT_URI
    auth_url, state = flow.authorization_url(prompt="consent", token_usage="remote")

    # Save state and code_verifier to exchange later
    state_file = STATE_DIR / f"{account_id}.json"
    state_file.write_text(
        json.dumps(
            {
                "state": state,
                "client_config": client_config,
                "code_verifier": getattr(flow, "code_verifier", None),
            }
        )
    )
    os.chmod(state_file, 0o600)
    return auth_url


def exchange_code(account_id: str, code: str) -> bool:
    state_file = STATE_DIR / f"{account_id}.json"
    code_verifier = None
    if not state_file.is_file():
        client_config = get_client_config()
    else:
        saved = json.loads(state_file.read_text())
        client_config = saved["client_config"]
        code_verifier = saved.get("code_verifier")

    flow = InstalledAppFlow.from_client_config(client_config, PUBLIC_SCOPES)
    flow.redirect_uri = REMOTE_REDIRECT_URI
    if code_verifier:
        flow.code_verifier = code_verifier
    flow.fetch_token(code=code.strip(), code_verifier=code_verifier)
    creds = flow.credentials

    dest_dir = STORE / "profiles" / account_id
    dest_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    token_file = dest_dir / "token.json"
    token_file.write_text(creds.to_json())
    os.chmod(token_file, 0o600)

    sess_file = dest_dir / "sessions.json"
    if not sess_file.is_file():
        sess_file.write_text("{}\n")
        os.chmod(sess_file, 0o600)

    # Register into accounts.json
    acc_json_path = STORE / "accounts.json"
    acc_data = (
        json.loads(acc_json_path.read_text()) if acc_json_path.is_file() else {"preferred": account_id, "accounts": []}
    )
    existing = {x["id"] for x in acc_data["accounts"]}
    if account_id not in existing:
        acc_data["accounts"].append({"id": account_id, "enabled": True, "role": "any"})
    if acc_data.get("preferred") is None:
        acc_data["preferred"] = account_id
    acc_json_path.write_text(json.dumps(acc_data, indent=2) + "\n")

    if state_file.is_file():
        state_file.unlink()

    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["get-url", "exchange"])
    parser.add_argument("account_id")
    parser.add_argument("code", nargs="?", default="")
    args = parser.parse_args()

    if args.action == "get-url":
        url = generate_auth_url(args.account_id)
        print("AUTH_URL=" + url)
    elif args.action == "exchange":
        if not args.code:
            print("Error: missing authorization code", file=sys.stderr)
            sys.exit(1)
        ok = exchange_code(args.account_id, args.code)
        print("SUCCESS" if ok else "FAILED")


if __name__ == "__main__":
    main()
