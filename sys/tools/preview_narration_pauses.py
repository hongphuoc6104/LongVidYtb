#!/usr/bin/env python3
"""Preview format-aware pause budgets without synthesis, uploads or job-state edits."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from narration_pauses import plan_tracks
from output_contract import primary_language


def preview(brief: dict, content: dict) -> dict:
    """Return planned boundary silence, explicitly excluding model-internal gaps."""
    _, _, plan = plan_tracks(brief, content, {}, primary_language(brief))
    return {"status": "planned_not_measured", "pause_plan": plan,
            "excludes": ["model_internal_pauses", "utterance_boundary_buffers", "bilingual_span_gaps"],
            "duration_note": "Regenerate WAV, subtitles and render timelines together; do not pad to an estimate."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", type=Path, required=True)
    parser.add_argument("--content", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = preview(json.loads(args.brief.read_text()), json.loads(args.content.read_text()))
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
