#!/usr/bin/env python3
"""Unit test suite for Short (9:16) vs Long (16:9) pipeline separation and zero-duration-lock contracts."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))
if str(SYS_DIR / "tools") not in sys.path:
    sys.path.insert(0, str(SYS_DIR / "tools"))

from content_contract import ContractError, validate_brief, validate_content  # noqa: E402
from flow_prompts import PromptError  # noqa: E402
from flow_prompts import compile as compile_prompt  # noqa: E402
from format_profiles import (  # noqa: E402
    PROFILES,
    caption_limits_for_aspect,
    clearance_for_output,
    default_text_style,
    get_profile,
    resolve_format_profile,
    validate_format_separation,
)
from output_contract import validate_explicit_outputs  # noqa: E402
from research_story_architect import (  # noqa: E402
    build_brief_v3,
    build_content_v3,
    compute_brief_hash,
    create_demo_trial_topic,
)
from scripts.subtitles import audit_cues, phrase_chunks, subtitle_cues, wrap_phrase  # noqa: E402


class TestFormatSeparation(unittest.TestCase):
    """Verify strict separation of short_9x16 and long_16x9 and removal of implicit defaults."""

    def test_format_profiles_ssot_and_zero_duration_locks(self):
        """Verify short_9x16 and long_16x9 profiles and absence of fixed duration locks."""
        short_prof = get_profile("short_9x16")
        long_prof = get_profile("long_16x9")

        assert short_prof["aspect_ratio"] == "9:16"
        assert (short_prof["width"], short_prof["height"]) == (1080, 1920)
        assert short_prof["flow_rpc_aspect"] == 2
        assert short_prof["caption_layout"]["max_line_chars"] == 28
        assert short_prof["caption_layout"]["max_cue_chars"] == 54
        assert "min_seconds" not in short_prof
        assert "max_seconds" not in short_prof

        assert long_prof["aspect_ratio"] == "16:9"
        assert (long_prof["width"], long_prof["height"]) == (1920, 1080)
        assert long_prof["flow_rpc_aspect"] == 3
        assert long_prof["caption_layout"]["max_line_chars"] == 42
        assert long_prof["caption_layout"]["max_cue_chars"] == 84
        assert "min_seconds" not in long_prof
        assert "max_seconds" not in long_prof

        assert get_profile("9:16") == PROFILES["short_9x16"]
        assert get_profile("16:9") == PROFILES["long_16x9"]

        # Verify sys/config.json has no global width/height or min_seconds/max_seconds locks
        cfg = json.loads((SYS_DIR / "config.json").read_text(encoding="utf-8"))
        assert "width" not in cfg
        assert "height" not in cfg
        assert "min_seconds" not in cfg
        assert "max_seconds" not in cfg

    def test_format_separation_rejects_cross_contamination(self):
        """Verify cross-mixed format_profile, aspect_ratio, and outputs are rejected."""
        with self.assertRaises(ValueError):
            validate_format_separation({"format_profile": "short_9x16", "aspect_ratio": "16:9"})
        with self.assertRaises(ValueError):
            validate_format_separation({"format_profile": "long_16x9", "aspect_ratio": "9:16"})
        with self.assertRaises(ValueError):
            validate_format_separation({
                "format_profile": "short_9x16",
                "aspect_ratio": "9:16",
                "outputs": [{"aspect_ratio": "16:9", "language": "vi", "subtitles": True}],
            })
        with self.assertRaises(ValueError):
            validate_explicit_outputs({"aspect_ratio": "16:9", "format_profile": "long_16x9"})

        topic = create_demo_trial_topic()
        brief = build_brief_v3(topic)
        brief["format_profile"] = "short_9x16"  # Mismatches brief["aspect_ratio"] == "16:9"
        with self.assertRaises(ContractError):
            validate_brief(SYS_DIR, brief)
        assert brief["aspect_ratio"] == "16:9"

    def test_duration_optional_and_unbounded_for_short_and_long(self):
        """Verify both short_9x16 and long_16x9 pass brief/content validation without fixed duration bounds."""
        for ratio, expected_profile in [("9:16", "short_9x16"), ("16:9", "long_16x9")]:
            topic = create_demo_trial_topic()
            topic.aspect_ratio = ratio
            topic.min_duration = None
            topic.max_duration = None

            brief = build_brief_v3(topic)
            assert brief["duration"] is None
            assert brief["format_profile"] == expected_profile
            assert resolve_format_profile(brief) == expected_profile
            assert brief["planning"]["text_style"] == default_text_style(ratio)

            validate_brief(SYS_DIR, brief)
            bhash = compute_brief_hash(brief)
            content = build_content_v3(topic, brief, bhash, brief_revision=1)
            assert content["duration"] is None
            validate_content(SYS_DIR, brief, 1, bhash, content)

        assert default_text_style("9:16")["size"] != default_text_style("16:9")["size"]

    def test_flow_compiler_requires_explicit_aspect_and_supports_null_clearance(self):
        """Verify Flow prompt compiler rejects missing aspect_ratio and omits clearance rule when None."""
        with self.assertRaisesRegex(PromptError, "FLOW_PROMPT_RATIO_UNSUPPORTED"):
            compile_prompt("NanoBanana2", "scene", {"description": "A stick figure at a desk.", "allowed_text": []}, "1.1.0")

        # Unsubtitled 16:9 output has clearance None -> no clearance_rule injected
        c_none = clearance_for_output("16:9", subtitles=False)
        assert c_none is None
        res_unsub = compile_prompt(
            "NanoBanana2",
            "scene",
            {
                "description": "Wide landscape of an ancient valley with stick figures.",
                "aspect_ratio": "16:9",
                "allowed_text": [],
                "caption_clearance": c_none,
            },
            "1.1.0",
        )
        assert "Reserve clear space" not in res_unsub["prompt"]
        assert '"caption_clearance": null' in res_unsub["prompt"]

        # Subtitled 9:16 vs Subtitled 16:9 clearance fractions
        c_short = clearance_for_output("9:16", subtitles=True)
        c_long = clearance_for_output("16:9", subtitles=True)
        assert c_short == {"edge": "bottom", "fraction": 0.18}
        assert c_long is None

    def test_subtitles_wrapping_and_audit_by_aspect_ratio(self):
        """Verify 9:16 wraps at 28/54 chars while 16:9 wraps at 42/84 chars."""
        assert caption_limits_for_aspect("9:16") == (28, 54)
        assert caption_limits_for_aspect("16:9") == (42, 84)

        sample_line = "Một câu phụ đề dài ba mươi sáu ký tự."
        assert 28 < len(sample_line) <= 42

        wrapped_short = wrap_phrase(sample_line, aspect_ratio="9:16")
        wrapped_long = wrap_phrase(sample_line, aspect_ratio="16:9")
        assert "\n" in wrapped_short
        assert "\n" not in wrapped_long

        cues_single_line = [{"text": sample_line, "start": 0.0, "end": 3.0, "scene_id": "SC01"}]
        audit_short = audit_cues(cues_single_line, aspect_ratio="9:16")
        audit_long = audit_cues(cues_single_line, aspect_ratio="16:9")
        assert any(w["code"] == "CAPTION_LAYOUT" for w in audit_short["warnings"])
        assert not any(w["code"] == "CAPTION_LAYOUT" for w in audit_long["warnings"])

        long_seg = [{"scene_id": "SC01", "start": 0.0, "end": 5.0, "text": "Khi phần thưởng bị trì hoãn sáu tháng ròng rã, bộ não con người cổ đại buộc phải thích nghi."}]
        cues_9x16 = subtitle_cues(long_seg, aspect_ratio="9:16")
        cues_16x9 = subtitle_cues(long_seg, aspect_ratio="16:9")
        assert len(cues_9x16) >= len(cues_16x9)
        assert len( phrase_chunks(long_seg[0]["text"], aspect_ratio="16:9")) >= 1

    def test_renderer_and_schema_have_zero_autoreframe_zoom_or_shift(self):
        """Verify autoReframe/auto_reframe zoom and downward shift are completely removed from outputs.mjs, index.tsx, and brief-v3.json."""
        index_tsx = (SYS_DIR / "renderer/index.tsx").read_text(encoding="utf-8")
        assert "autoReframe" not in index_tsx
        assert "autoReframeScale" not in index_tsx
        assert "autoReframeShiftY" not in index_tsx
        assert re.search(r"\b1\.18\b", index_tsx) is None
        assert re.search(r"\b8\.5\b", index_tsx) is None

        outputs_mjs_text = (SYS_DIR / "renderer/outputs.mjs").read_text(encoding="utf-8")
        assert "autoReframe" not in outputs_mjs_text
        assert "auto_reframe" not in outputs_mjs_text
        assert "VP_SMART_AUTOREFRAME" not in outputs_mjs_text

        brief_schema = (SYS_DIR / "schemas/brief-v3.json").read_text(encoding="utf-8")
        assert "auto_reframe" not in brief_schema

        outputs_mjs = (SYS_DIR / "renderer/outputs.mjs").resolve().as_uri()
        js_code = f"""
        import {{ outputPlans }} from {json.dumps(outputs_mjs)};
        const baseProps = {{
          aspect_ratio: '16:9',
          outputs: [{{ aspect_ratio: '16:9', language: 'vi', subtitles: false }}],
          tracks: {{
            vi: {{
              audioSrc: 'narration.wav',
              duration: 120,
              cues: [],
              scenesByAspect: {{ '16:9': [{{ id: 'SC01', start: 0, end: 120 }}] }}
            }}
          }}
        }};
        const plansDefault = outputPlans(baseProps, false);
        console.log(JSON.stringify({{
          hasAutoReframeKey: 'autoReframe' in plansDefault[0].props,
          defaultHideSubtitles: plansDefault[0].props.hideSubtitles,
          defaultWidth: plansDefault[0].props.width,
          defaultHeight: plansDefault[0].props.height
        }}));
        """
        res = subprocess.run(["node", "--input-type=module", "-e", js_code], capture_output=True, text=True, check=True)
        payload = json.loads(res.stdout.strip())
        assert payload["defaultHideSubtitles"] is True
        assert payload["hasAutoReframeKey"] is False
        assert payload["defaultWidth"] == 1920
        assert payload["defaultHeight"] == 1080

    def test_adapters_gflow_rejects_missing_ratio_instead_of_overwriting_16x9(self):
        """Verify adapters.gflow requires explicit ratio instead of silently falling back to 16:9."""
        import adapters

        from pilot import Blocked

        dummy_pilot = type("DummyPilot", (), {"root": SYS_DIR, "brief": lambda self, j: None})()
        with self.assertRaisesRegex(Blocked, "FLOW_RATIO_REQUIRED"):
            adapters.gflow(dummy_pilot, "image", "--prompt", "test prompt")
        assert hasattr(adapters, "gflow")


if __name__ == "__main__":
    unittest.main()
