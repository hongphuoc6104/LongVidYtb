#!/usr/bin/env python3
"""Project entry point; implementation and runtime data live in sys/."""
import importlib.util
import os
import runpy
import sys
from pathlib import Path

SYSTEM = Path(__file__).resolve().parent / 'sys'
venv_py = SYSTEM / '.venv' / 'bin' / 'python'
if __name__ == '__main__' and venv_py.is_file() and Path(sys.executable).resolve() != venv_py.resolve():
    os.execv(str(venv_py), [str(venv_py), str(Path(__file__).resolve())] + sys.argv[1:])

sys.path.insert(0, str(SYSTEM))
# Keep runtime bytecode out of the project root.
sys.pycache_prefix = str(SYSTEM / '.cache' / 'pycache')

if __name__ == '__main__':
    runpy.run_path(str(SYSTEM / 'pilot.py'), run_name='__main__')
else:
    spec = importlib.util.spec_from_file_location(__name__, SYSTEM / 'pilot.py')
    implementation = importlib.util.module_from_spec(spec)
    sys.modules[__name__] = implementation
    spec.loader.exec_module(implementation)
