#!/usr/bin/env python3
"""Interactive OAuth login runner for Colab CLI accounts."""

import json
import os
import sys
from importlib import resources
from pathlib import Path

from colab_cli.auth import PUBLIC_SCOPES, REMOTE_REDIRECT_URI
from google_auth_oauthlib.flow import InstalledAppFlow

STORE = Path.home() / ".config/video-pilot/colab"


def login_account(account_id: str) -> None:
    config_resource = resources.files("colab_cli").joinpath("oauth_config.json")
    client_config = json.loads(config_resource.read_text())

    flow = InstalledAppFlow.from_client_config(client_config, PUBLIC_SCOPES)
    flow.redirect_uri = REMOTE_REDIRECT_URI
    auth_url, _ = flow.authorization_url(prompt="consent", token_usage="remote")

    print(f"READY_AUTH_URL:{auth_url}", flush=True)

    # Read code from stdin
    code = sys.stdin.readline().strip()
    if not code:
        print("ERROR: Empty authorization code received", flush=True)
        sys.exit(1)

    flow.fetch_token(code=code)
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

    # Update accounts.json
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

    print("AUTH_SUCCESS", flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: interactive_auth.py <account_id>")
        sys.exit(1)
    login_account(sys.argv[1])
