#!/usr/bin/env python3
"""Batch 1 Spec Generator for Channels 04-06 (Squad 2).
Channels:
  4. en-deep-time-strata (Long 16:9 + Short 9:16)
  5. en-inside-vessel    (Long 16:9 + Short 9:16)
  6. en-macro-gears      (Long 16:9 + Short 9:16)

Generates exact JSON specs conforming to Schema 3.0 / Flow Video specs:
- sys/channels/en_batch1_specs/en-deep-time-strata_long_16x9.json
- sys/channels/en_batch1_specs/en-deep-time-strata_short_9x16.json
- sys/channels/en_batch1_specs/en-inside-vessel_long_16x9.json
- sys/channels/en_batch1_specs/en-inside-vessel_short_9x16.json
- sys/channels/en_batch1_specs/en-macro-gears_long_16x9.json
- sys/channels/en_batch1_specs/en-macro-gears_short_9x16.json
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

# Ensure sys and sys/tools are on path
ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
TOOLS_DIR = SYS_DIR / "tools"
SPECS_DIR = SYS_DIR / "channels" / "en_batch1_specs"

for p in [str(ROOT_DIR), str(SYS_DIR), str(TOOLS_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from build_en_batch1_squad2_data_strata import (
    get_deep_time_strata_long,
    get_deep_time_strata_short,
)
from build_en_batch1_squad2_data_vessel import (
    get_inside_vessel_long,
    get_inside_vessel_short,
)
from build_en_batch1_squad2_data_gears import (
    get_macro_gears_long,
    get_macro_gears_short,
)


def write_spec(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"[✓] Wrote spec -> {path} ({len(data['shots'])} shots, {sum(len(s['narration'].split()) for s in data['shots'])} words)")


def main() -> int:
    SPECS_DIR.mkdir(parents=True, exist_ok=True)

    specs = [
        ("en-deep-time-strata_short_9x16.json", get_deep_time_strata_short()),
        ("en-inside-vessel_short_9x16.json", get_inside_vessel_short()),
        ("en-macro-gears_short_9x16.json", get_macro_gears_short()),
        ("en-deep-time-strata_long_16x9.json", get_deep_time_strata_long()),
        ("en-inside-vessel_long_16x9.json", get_inside_vessel_long()),
        ("en-macro-gears_long_16x9.json", get_macro_gears_long()),
    ]

    for fname, spec_data in specs:
        out_p = SPECS_DIR / fname
        write_spec(out_p, spec_data)

    print("\n[✓] All 6 specs generated successfully in sys/channels/en_batch1_specs/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
