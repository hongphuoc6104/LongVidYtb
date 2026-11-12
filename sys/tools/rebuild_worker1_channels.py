#!/usr/bin/env python3
"""Rebuild and compile Long (16:9) aligned specs for Worker 1 channels:
1. ai_binh_dan (117 beats)
2. ban_do_quyen_luc (98 beats)
3. banh_rang (98 beats)

Uses sys.tools.batch1_spec_builder.compile_and_save_spec
"""

import json
from sys.tools.batch1_scenes_ai_binh_dan import AI_BINH_DAN_SCENES
from sys.tools.batch1_scenes_ban_do_quyen_luc import BAN_DO_QUYEN_LUC_SCENES
from sys.tools.batch1_scenes_banh_rang import BANH_RANG_SCENES
from sys.tools.batch1_spec_builder import compile_and_save_spec
from typing import Any, Dict

CHANNELS = [
    ("ai_binh_dan", AI_BINH_DAN_SCENES),
    ("ban_do_quyen_luc", BAN_DO_QUYEN_LUC_SCENES),
    ("banh_rang", BANH_RANG_SCENES),
]


def run_rebuild() -> Dict[str, Any]:
    reports = {}
    all_valid = True

    for slug, scenes in CHANNELS:
        print("\n==========================================")
        print(f"Compiling spec for {slug} ({len(scenes)} scenes)...")
        print("==========================================")
        report = compile_and_save_spec(slug, scenes)
        reports[slug] = report

        print(json.dumps(report, indent=2))
        if not report.get("is_valid"):
            all_valid = False
            print(f"ERROR: Spec validation FAILED for {slug}!")
        else:
            print(f"SUCCESS: Spec validation PASSED for {slug}!")

    print("\n==========================================")
    print(f"Summary: All valid = {all_valid}")
    print("==========================================")
    return {"all_valid": all_valid, "reports": reports}


if __name__ == "__main__":
    result = run_rebuild()
    if not result["all_valid"]:
        exit(1)
