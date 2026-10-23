"""Entrypoint for `python3 -m sys.renderer <work_dir>`."""

import sys
from pathlib import Path

SYS_ROOT = Path(__file__).resolve().parents[1]
if str(SYS_ROOT) not in sys.path:
    sys.path.insert(0, str(SYS_ROOT))

try:
    from sys.render_cli import main
except ImportError:
    from render_cli import main

if __name__ == "__main__":
    sys.exit(main())
