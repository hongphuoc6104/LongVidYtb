import sys
from pathlib import Path

# Automatically add sys and repo root to sys.path for all pytest invocations
SYS_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = SYS_DIR.parent
VENV_PKGS = list((SYS_DIR / '.venv/lib').glob('python*/site-packages'))

if not hasattr(sys, "__path__"):
    sys.__path__ = [str(SYS_DIR)]

for p in [str(REPO_DIR), str(SYS_DIR)] + [str(d) for d in VENV_PKGS]:
    if p not in sys.path:
        sys.path.insert(0, p)
