"""Observable contract behavior; no providers, speech synthesis or video render."""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

from output_contract import languages, outputs, voice_settings

ROOT = Path(__file__).resolve().parents[1]


class OutputContractTests(unittest.TestCase):
    def fixture(self):
        brief = {
            "language": "en",
            "aspect_ratio": "9:16",
            "outputs": [
                {"aspect_ratio": "9:16", "language": "en", "subtitles": True, "voice": "VietNarrator", "speed": 0.92}
            ],
        }
        return brief, {}

    def test_job_voice_rate_override_unrelated_defaults(self):
        brief, _ = self.fixture()
        self.assertEqual(
            voice_settings(brief, "en", {"en_voice": "VietNarrator", "en_speed": 1.0}),
            {"voice": "VietNarrator", "speed": 0.92},
        )

    def test_aspect_does_not_choose_language_for_explicit_contract(self):
        for aspect in ("9:16", "16:9"):
            for language in ("vi", "en"):
                brief = {
                    "aspect_ratio": aspect,
                    "outputs": [dict(aspect_ratio=aspect, language=language, subtitles=False)],
                }
                self.assertEqual(languages(brief), [language])

    def test_legacy_default_routing_is_preserved(self):
        self.assertEqual(languages({"aspect_ratio": "dual", "language": "vi"}), ["vi", "en"])
        self.assertEqual(languages({"aspect_ratio": "9:16", "language": "vi"}), ["vi"])

    def test_conflicting_voice_and_invalid_contract_are_rejected(self):
        brief = {
            "aspect_ratio": "dual",
            "outputs": [
                dict(aspect_ratio="9:16", language="en", subtitles=True, speed=0.92),
                dict(aspect_ratio="16:9", language="en", subtitles=False, speed=1.08),
            ],
        }
        with self.assertRaises(ValueError):
            voice_settings(brief, "en", {})
        for bad in ([], [None], [dict(aspect_ratio="9:16", language="en", subtitles="yes")]):
            with self.assertRaises(ValueError):
                outputs({"aspect_ratio": "9:16", "outputs": bad})

    @unittest.skipUnless(shutil.which("node"), "Node required for renderer contract")
    def test_renderer_uses_english_track_cues_and_portrait_timeline(self):
        script = """
import {outputPlans} from './renderer/outputs.mjs';
const props={aspect_ratio:'9:16',duration:99,scenes:[{id:'wrong-vi'}],
 outputs:[{aspect_ratio:'9:16',language:'en',subtitles:true}],
 tracks:{en:{audioSrc:'english.wav',duration:48.5,scenesByAspect:{'9:16':[{id:'english-portrait'}]},cues:[{text:'A predator hunts.',start:0,end:2}]}}};
const actual=outputPlans(props,true)[0];
let missingBlocked=false;
try {outputPlans({...props,tracks:{en:{...props.tracks.en,scenesByAspect:{'16:9':[]}}}},true);} catch {missingBlocked=true;}
console.log(JSON.stringify({actual,missingBlocked}));
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        actual = data["actual"]["props"]
        self.assertEqual(
            (actual["width"], actual["height"], actual["audioSrc"], actual["duration"]),
            (1080, 1920, "english.wav", 48.5),
        )
        self.assertEqual(actual["scenes"][0]["id"], "english-portrait")
        self.assertEqual(actual["cues"][0]["text"], "A predator hunts.")
        self.assertFalse(actual["hideSubtitles"])
        self.assertTrue(data["missingBlocked"])

    def test_deleted_modules_unresolvable(self):
        import importlib

        for mod in (
            "pilot",
            "pipeline",
            "flow_cdp",
            "flow_prompts",
            "image_pipeline",
            "audio_processing",
            "blueprints",
            "permissions",
            "profile_setup",
        ):
            with self.assertRaises(ModuleNotFoundError, msg=f"{mod} should raise ModuleNotFoundError"):
                importlib.import_module(mod)

    def test_config_integrity_and_decoupling(self):
        cfg = json.loads((ROOT / "config.json").read_text())
        for _lang, p in cfg.get("voices", {}).items():
            self.assertTrue((ROOT / p).is_file(), f"Broken voice file path: {p}")
        dump = json.dumps(cfg)
        self.assertNotIn("parallel_images", dump)
        self.assertNotIn("KhanhTTS", dump)

    def test_retained_modules_have_no_dangling_flow_methods(self):
        from account_budget import Budgets
        from session_store import Sessions

        self.assertFalse(hasattr(Budgets, "allow_flow_repair"))
        self.assertFalse(hasattr(Budgets, "flow_submit"))
        self.assertFalse(hasattr(Budgets, "flow_submit_many"))
        self.assertFalse(hasattr(Budgets, "flow_state"))
        self.assertFalse(hasattr(Sessions, "bind_runtime"))
