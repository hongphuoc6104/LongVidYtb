"""Pause selection, real PCM assembly and cache contracts; no live voice-quality claim."""

from __future__ import annotations

import json
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import adapters
import pytest
import test_colab_worker as worker_tests
from colab_bridge.protocol import build_request, validate_result
from narration_pauses import plan_scene, plan_tracks, settings_for_language, split_narration
from remote_audio import produce
from tools.preview_narration_pauses import preview

from pilot import write


def brief(aspect: str = "9:16", language: str = "vi") -> dict:
    return {"aspect_ratio": aspect, "outputs": [
        {"aspect_ratio": aspect, "language": language, "subtitles": aspect == "9:16"},
    ]}


def test_sentence_length_opening_and_quote_boundaries() -> None:
    settings = settings_for_language(brief(), "vi")
    text = '“Bạn hiểu thật sao?” Bạn vẫn chưa thể giải thích điều đó bằng lời của mình.'
    body = split_narration(text, settings)
    opening = split_narration(text, settings, opening=True)
    assert [row["pause"] for row in body] == [0.16, 0.22]
    assert [row["pause"] for row in opening] == [0.12, 0.16]
    assert " ".join(row["text"] for row in body) == text
    long = settings_for_language(brief("16:9"), "vi")
    assert [row["pause"] for row in split_narration(text, long)] == [0.20, 0.28]


def test_minor_only_splits_long_utterances() -> None:
    settings = settings_for_language(brief(), "vi")
    assert len(split_narration("Bạn đọc, rồi tự giải thích.", settings)) == 1
    text = "Một " * 45 + ", sau đó tự giải thích."
    parts = split_narration(text, settings)
    assert [row["pause"] for row in parts] == [0.12, 0.16]


def test_exact_explicit_pauses_override_defaults_without_stacking() -> None:
    settings = settings_for_language(brief(), "vi")
    scene = {"id": "SC02"}
    request, audit = plan_scene(scene, "Đọc lại. [pause:900ms] Hiểu chưa? [pause:0.45s]", "vi", settings, 0, True)
    assert request["gaps"] == [0.9]
    assert request["tail"] == 0.45
    assert [row["reason"] for row in audit] == ["explicit", "explicit"]
    assert split_narration("Đợi. [pause:100ms][pause:200ms] Rồi nói.", settings)[0]["pause"] == 0.3


@pytest.mark.parametrize("text", ["[pause:100ms] Xin chào.", "Xin chào. [pause:nan]", "Xin chào. [pause:9s]"])
def test_invalid_authored_pause_blocks(text: str) -> None:
    with pytest.raises(ValueError, match="PAUSE_POLICY"):
        split_narration(text, settings_for_language(brief(), "vi"))


def test_opening_forbids_explicit_pause_but_keeps_short_automatic_breaths() -> None:
    settings = settings_for_language(brief(), "vi")
    with pytest.raises(ValueError, match="OPENING_SCENE_PAUSE_FORBIDDEN"):
        split_narration("Đọc lại. [pause:100ms]", settings, opening=True)
    scene, _ = plan_scene({"id": "SC01"}, "Đọc lại. Hiểu chưa?", "vi", settings, 0, False, opening=True)
    assert scene["gaps"] == [0.12]
    assert scene["tail"] == 0.30


def test_learner_hold_is_a_minimum_and_final_tail_is_not_added_twice() -> None:
    settings = settings_for_language(brief(), "vi")
    scene = {"id": "SC02", "audio_direction": {"vi": {"learner_pause_seconds": 3}}}
    request, audit = plan_scene(scene, "Tự trả lời. [pause:900ms]", "vi", settings, 2, True)
    assert request["tail"] == 3
    assert request["retake"] == 2
    assert audit[-1]["reason"] == "learner_hold"
    with pytest.raises(ValueError, match="PAUSE_POLICY"):
        plan_scene({"id": "SC02", "audio_direction": {"vi": {"learner_pause_seconds": True}}},
                   "Tự trả lời.", "vi", settings, 0, True)


def test_dual_output_resolution_and_track_budget() -> None:
    b = {"aspect_ratio": "dual", "outputs": brief()["outputs"] + brief("16:9", "en")["outputs"]}
    content = {"scenes": [
        {"id": "SC01", "narration": "Đọc lại. Hiểu chưa?", "narration_en": "Read again. Do you understand?"},
        {"id": "SC02", "narration": "Tự giải thích.", "narration_en": "Explain it yourself."},
    ]}
    scenes, secondary, plan = plan_tracks(b, content, {}, "vi")
    assert scenes[0]["gaps"] == [0.12]
    assert [row["tail"] for row in secondary] == [0.16, 0.4, 0.25]
    assert plan["tracks"]["vi"]["inserted_seconds"] == 0.57
    assert plan["tracks"]["en"]["inserted_seconds"] == 0.81
    b["outputs"][1]["language"] = "vi"
    assert settings_for_language(b, "vi")["profile"] == "long_16x9"


def test_legacy_helpers_keep_existing_contract() -> None:
    texts, gaps = adapters.chunks_with_gaps("Đọc lại. Hiểu chưa?", adapters.DEFAULT_PAUSE)
    assert texts == ["Đọc lại.", "Hiểu chưa?"]
    assert gaps == [0.5]
    assert adapters.scene_tail({"id": "SC01"}, "vi", adapters.DEFAULT_PAUSE, False) == 0.7


def test_english_primary_preview_and_secondary_preserve_text_and_retake() -> None:
    b = {"aspect_ratio": "dual", "outputs": brief(language="en")["outputs"] + brief("16:9")["outputs"]}
    content = {"scenes": [{"id": "SC01", "narration": "Đọc lại. Hiểu chưa?",
                           "narration_en": "Read again. Do you understand?"}]}
    scenes, secondary, plan = plan_tracks(b, content, {"SC01": 2}, "en")
    assert scenes[0]["texts"] == ["Read again.", "Do you understand?"]
    assert scenes[0]["gaps"] == [0.12]
    assert [row["text"] for row in secondary] == ["Đọc lại.", "Hiểu chưa?"]
    assert all(row["retake"] == 2 for row in secondary)
    report = preview(b, content)
    assert report["status"] == "planned_not_measured"
    assert report["pause_plan"]["tracks"] == plan["tracks"]
    assert "bilingual_span_gaps" in report["excludes"]


class TestPauseAssembly(unittest.TestCase):
    setUp = worker_tests.WorkerTests.setUp
    run_worker = worker_tests.WorkerTests.run_worker
    copy_processing_sources = worker_tests.WorkerTests.copy_processing_sources

    def test_production_routes_both_languages_through_measured_pcm(self) -> None:
        self.copy_processing_sources()
        self.cfg["tts_pause_policy"] = "format_v1"
        write(self.root / "config.json", self.cfg)
        b = {"aspect_ratio": "dual", "outputs": brief()["outputs"] + brief("16:9", "en")["outputs"]}
        content = {"scenes": [
            {"id": "SC01", "narration": "Đọc lại. Hiểu chưa?", "narration_en": "Read again. Do you understand?"},
            {"id": "SC02", "narration": "Tự giải thích. [pause:450ms] Thử lại.",
             "narration_en": "Explain it yourself. [pause:600ms] Try again.", "tone": "reflective_slow"},
        ]}
        job = self.root / "runs/test"
        out = job / "revisions/audio/1"
        out.mkdir(parents=True)
        pilot = SimpleNamespace(root=self.root, job=lambda _: job, brief=lambda _: (b, 1, "fixture"),
                                payload=lambda *_: content)
        seen = []

        def synthesize(client: object, request: dict, destination: Path, cache: Path, **kwargs: object) -> None:
            seen.append(request)
            self.run_worker(request, destination)
            validate_result(destination, request)

        with (patch("adapters.retakes", return_value={}), patch("execution.is_job", return_value=False),
              patch("colab_bridge.client.Client.synthesize", synthesize)):
            result = produce(pilot, "test", out)
        request = seen[0]
        assert [row["pause"] for row in request["segments"]] == [0.12, 0.3, 0.45, 0.15]
        assert [row["pause"] for row in request["secondary"]] == [0.16, 0.4, 0.6, 0.25]
        assert set(result["tracks"]) == {"vi", "en"}
        for language in ("vi", "en"):
            track = result["tracks"][language]
            with wave.open(str(job / track["wav"])) as handle:
                assert abs(handle.getnframes() / handle.getframerate() - track["duration"]) < 1 / 48000
            wanted = request["segments" if language == "vi" else "secondary"]
            for segment, expected in zip(track["segments"], wanted, strict=True):
                assert abs(segment["end"] - segment["content_end"] - expected["pause"]) < 1 / 48000
        assert request["items"][request["secondary"][-1]["items"][0]]["speed"] == 0.92
        # A newly planned request includes the policy in its content identity.
        primary, secondary, plan = plan_tracks(b, content, {}, "vi")
        one = build_request(self.root, self.cfg, primary, secondary_scenes=secondary, pause_plan=plan)
        plan["version"] = "different-policy"
        two = build_request(self.root, self.cfg, primary, secondary_scenes=secondary, pause_plan=plan)
        assert one["request_id"] != two["request_id"]
        assert json.loads((out / "request-colab.json").read_text())["pause_plan"]["version"] == "format_v1"
