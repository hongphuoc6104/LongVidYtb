"""Process-local CLI profile binding; installed package and HOME unchanged."""

import os
import sys
from pathlib import Path

# Ensure colab_cli is importable even when invoked from sys/.venv
try:
    import colab_cli  # noqa: F401
except ImportError:
    for cand in [
        Path.home() / ".local/share/uv/tools/google-colab-cli/lib/python3.12/site-packages",
        Path.home() / ".local/share/uv/tools/google-colab-cli/lib/python3.11/site-packages",
        Path.home() / ".local/lib/python3.12/site-packages",
    ]:
        if (cand / "colab_cli").is_dir():
            sys.path.insert(0, str(cand))
            break


def main():
    raw_args = sys.argv[1:]
    known_commands = {"list", "sessions", "status", "pool-status", "help"}
    if raw_args and raw_args[0] in ("--account", "-a"):
        if len(raw_args) < 2 or raw_args[1].startswith("-") or raw_args[1] in known_commands:
            raise SystemExit("Missing or invalid account argument")
        account_id = raw_args[1]
        args = raw_args[2:]
        folder = Path.home() / ".config/video-pilot/colab/profiles" / account_id
    elif raw_args and raw_args[0].startswith("--account="):
        account_id = raw_args[0].split("=", 1)[1]
        if not account_id or account_id.startswith("-") or account_id in known_commands:
            raise SystemExit("Missing or invalid account argument")
        args = raw_args[1:]
        folder = Path.home() / ".config/video-pilot/colab/profiles" / account_id
    elif raw_args and not raw_args[0].startswith("-") and raw_args[0] not in known_commands:
        folder = Path(raw_args[0]).resolve()
        args = raw_args[1:]
    else:
        raise SystemExit("Usage: account_cli.py <profile_folder | --account <id>> <colab_args...>")

    if any(x.split("=")[0] in ("--config", "--auth", "--client-oauth-config", "-c") for x in args):
        raise SystemExit("Profile owns authentication/session paths; overrides not allowed")
    if args and args[0] == "list":
        args[0] = "sessions"
    try:
        folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(folder, 0o700)
    except OSError:
        pass
    import colab_cli.auth as auth
    import colab_cli.common as common
    from colab_cli.common import state

    common.setup_logging = lambda *a, **kw: None
    from colab_cli.cli import main as run
    from colab_cli.history import HistoryLogger

    auth.TOKEN_CONFIG_PATH = str(folder / "token.json")
    state._history = HistoryLogger(str(folder / "history"))
    sys.argv = ["colab", "--auth", "oauth2", "--config", str(folder / "sessions.json"), *args]
    code = 0
    try:
        res = run()
        if isinstance(res, int):
            code = res
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else (1 if exc.code else 0)
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
    os._exit(code)


if __name__ == "__main__":
    main()

