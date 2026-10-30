#!/usr/bin/env python3
"""Forwarding script for build_quy_trinh_de_tai_lon_job living in sys/content/builders/."""
from __future__ import annotations

import sys
from pathlib import Path

BUILDER_DIR = Path(__file__).resolve().parents[1] / "content" / "builders"
if str(BUILDER_DIR) not in sys.path:
    sys.path.insert(0, str(BUILDER_DIR))

from build_quy_trinh_de_tai_lon_job import build_job, build_topic, main

if __name__ == "__main__":
    sys.exit(main())
