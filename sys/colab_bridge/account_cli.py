"""Process-local CLI profile binding; installed package and HOME unchanged."""

import os
import sys
from pathlib import Path


def main():
    folder = Path(sys.argv[1]).resolve()
    args = sys.argv[2:]
    if any(x.split("=")[0] in ("--config", "--auth", "--client-oauth-config", "-c") for x in args):
        raise SystemExit("Profile owns authentication/session paths; overrides not allowed")
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
    run()


if __name__ == "__main__":
    main()
