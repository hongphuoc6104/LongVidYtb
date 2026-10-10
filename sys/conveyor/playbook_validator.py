#!/usr/bin/env python3
"""Playbook & Issue Log Schema Validator.

Validates that PLAYBOOK.md strictly adheres to the 6 mandatory fields
for all documented operational and engineering lessons:
1. Triệu chứng (Symptom)
2. Tái hiện E2E (Reproduction Path)
3. Nguyên nhân cốt lõi (Root Cause)
4. Giả định sai (Wrong Assumptions)
5. Giải pháp & Kiểm chứng (Resolution & E2E Proof)
6. Quy tắc phòng ngừa vàng (Golden Rule)
"""

import re
from pathlib import Path
from typing import Dict, Tuple

MANDATORY_FIELDS = [
    ("Triệu chứng", "Symptom"),
    ("Tái hiện E2E", "Reproduction Path"),
    ("Nguyên nhân cốt lõi", "Root Cause"),
    ("Giả định sai", "Wrong Assumptions"),
    ("Giải pháp & Kiểm chứng", "Resolution & E2E Proof"),
    ("Quy tắc phòng ngừa vàng", "Golden Rule"),
]


def validate_playbook(playbook_path: Path) -> Tuple[bool, Dict[str, any]]:
    """Validates schema of PLAYBOOK.md."""
    if not playbook_path.is_file():
        return False, {
            "passed": False,
            "error": f"PLAYBOOK.md not found at {playbook_path}",
            "entries_count": 0,
            "violations": ["File missing"],
        }

    content = playbook_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Split into sections starting with `### [`
    entry_indices = []
    for idx, line in enumerate(lines):
        if line.strip().startswith("### ["):
            entry_indices.append(idx)

    if not entry_indices:
        return False, {
            "passed": False,
            "error": "No error entries found starting with '### [' in PLAYBOOK.md",
            "entries_count": 0,
            "violations": ["No structured lessons documented"],
        }

    violations = []
    valid_entries = 0

    for i, start_idx in enumerate(entry_indices):
        end_idx = entry_indices[i + 1] if i + 1 < len(entry_indices) else len(lines)
        entry_text = "\n".join(lines[start_idx:end_idx])
        header = lines[start_idx].strip()

        missing_fields = []
        for vn_key, en_key in MANDATORY_FIELDS:
            # Check either Vietnamese or English key
            pattern = re.compile(
                rf"(?:\*\*{re.escape(vn_key)}|\*\*{re.escape(en_key)}|{re.escape(vn_key)}|{re.escape(en_key)})",
                re.IGNORECASE,
            )
            if not pattern.search(entry_text):
                missing_fields.append(f"{vn_key} / {en_key}")

        if missing_fields:
            violations.append({
                "header": header,
                "missing_fields": missing_fields,
            })
        else:
            valid_entries += 1

    passed = len(violations) == 0
    return passed, {
        "passed": passed,
        "entries_count": len(entry_indices),
        "valid_entries": valid_entries,
        "violations": violations,
    }


if __name__ == "__main__":
    import json
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("PLAYBOOK.md")
    ok, report = validate_playbook(target)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if ok else 1)
