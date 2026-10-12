#!/usr/bin/env python3
"""Apply refreshed narrations and anchor quotes to build_study_motivation_history_13m.py."""
import pprint
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sys"))
sys.path.insert(0, str(ROOT / "sys" / "tools"))

from tune_all_scenes import SCENES_DEF
import build_study_motivation_history_13m as bsm

builder_file = ROOT / "sys" / "tools" / "build_study_motivation_history_13m.py"
content = builder_file.read_text(encoding="utf-8")

def json_repr(val):
    import json
    return json.dumps(val, ensure_ascii=False)


# Prepare new RAW_SCENES_DATA
raw_scenes = list(bsm.RAW_SCENES_DATA)
assert len(raw_scenes) == 48

for sc, def_sc in zip(raw_scenes, SCENES_DEF):
    assert sc["scene_id"] == def_sc["scene_id"]
    sc["narration"] = def_sc["narration"]
    sc["claim"] = def_sc["claim"]
    first_sent = def_sc["sentences"][0]
    words = first_sent.split()
    sc["anchor_quote"] = " ".join(words[:5])

# Format RAW_SCENES_DATA as python code
lines = ["RAW_SCENES_DATA: List[Dict[str, Any]] = ["]
for sc in raw_scenes:
    lines.append("    {")
    lines.append(f'        "scene_id": {json_repr(sc["scene_id"])},')
    lines.append(f'        "chapter": {sc["chapter"]},')
    lines.append(f'        "duration": {sc["duration"]},')
    lines.append(f'        "title": {json_repr(sc["title"])},')
    lines.append(f'        "purpose": {json_repr(sc["purpose"])},')
    lines.append(f'        "narration": {json_repr(sc["narration"])},')
    lines.append(f'        "requirements": {json_repr(sc["requirements"])},')
    lines.append(f'        "source_ids": {json_repr(sc["source_ids"])},')
    lines.append(f'        "action": {json_repr(sc["action"])},')
    lines.append(f'        "setting": {json_repr(sc["setting"])},')
    lines.append(f'        "camera": {json_repr(sc["camera"])},')
    lines.append(f'        "bg_description": {json_repr(sc["bg_description"])},')
    lines.append(f'        "sticker_description": {json_repr(sc["sticker_description"])},')
    lines.append(f'        "anchor_quote": {json_repr(sc["anchor_quote"])},')
    lines.append(f'        "fx": {json_repr(sc["fx"])},')
    lines.append(f'        "x": {sc["x"]},')
    lines.append(f'        "y": {sc["y"]},')
    lines.append(f'        "w": {sc["w"]},')
    if sc["claim"]:
        q, s_id, f = sc["claim"]
        lines.append('        "claim": (')
        lines.append(f"            {json_repr(q)},")
        lines.append(f"            {json_repr(s_id)},")
        lines.append(f"            {json_repr(f)},")
        lines.append("        ),")
    else:
        lines.append('        "claim": None,')
    lines.append("    },")
lines.append("]\n")

new_raw_code = "\n".join(lines)


def json_repr(val):
    import json
    return json.dumps(val, ensure_ascii=False)


# Replace between RAW_SCENES_DATA: List[Dict[str, Any]] = [ and def create_study_motivation_13m_topic
idx_start = content.find("RAW_SCENES_DATA: List[Dict[str, Any]] = [")
idx_end = content.find("def create_study_motivation_13m_topic(")
assert idx_start != -1 and idx_end != -1, "Could not find slice boundaries"

updated_content = content[:idx_start] + new_raw_code + "\n\n" + content[idx_end:]
builder_file.write_text(updated_content, encoding="utf-8")
print("Updated build_study_motivation_history_13m.py successfully.")
