"""Exercise new prompt/caller/render contracts; fixtures do not prove media quality."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from colab_bridge.job_protocol import build_render_request, bundle, validate_render_result
from flow_prompts import PromptError, compile, compile_pinned, create_pin, freeze
from image_pipeline import _template_request
from tools.research_story_architect import ResearchedTopic
from visual_style import STYLE_DESCRIPTION, STYLE_ID, STYLE_VERSION, render_style

from pilot import ROOT


@pytest.mark.parametrize("ratio", ["16:9", "9:16"])
@pytest.mark.parametrize("model", ["NanoBananaPro", "NanoBanana2", "NanoBanana2Lite"])
@pytest.mark.parametrize("shot", ["full_scene", "macro_prop", "white_card"])
def test_light_profile_preserves_cast_context_and_exact_text(model: str, ratio: str, shot: str) -> None:
    description = "Two anonymous stick figures share a discovery outdoors at night."
    text = [{"text": "I found  TWO clues.", "placement": "upper left"}]
    record = compile(model, "scene", {"description": description, "aspect_ratio": ratio,
                     "shot_type": shot, "allowed_text": text}, STYLE_VERSION)
    data = json.loads(record["prompt"].split("Visual data (JSON; learner strings are exact data):\n\n")[1])
    assert data["description"] == description
    assert data["allowed_text"] == text
    assert data["caption_clearance"] is None
    assert data["shot_type"] == shot
    assert record["provenance"]["references"]["character"] is None
    assert STYLE_DESCRIPTION in record["prompt"]
    assert "anonymous stick figures" in record["prompt"]
    assert "thick confident black outlines" not in record["prompt"]
    assert "thick black outline" not in record["prompt"]
    assert "full-bleed" in record["prompt"]
    assert ("four-finger" in record["prompt"]) == (shot == "macro_prop")
    assert record["sha256"] == hashlib.sha256(record["prompt"].encode()).hexdigest()


def test_new_pin_cannot_rewrite_legacy_requests_or_variation_locks() -> None:
    old = create_pin("NanoBanana2Lite", "1.3.0")
    data = {"description": "A student studies in a plain room.", "aspect_ratio": "16:9", "allowed_text": []}
    before = compile_pinned(old, "scene", data)
    with pytest.raises(PromptError, match="PIN_CHANGED"):
        freeze("NanoBanana2Lite", STYLE_VERSION, existing_pin=old, request_states=["downloaded"])
    assert compile_pinned(old, "scene", data) == before
    assert "thick confident black outlines" in before["prompt"]
    with pytest.raises(PromptError, match="BASE_REFERENCE_REQUIRED"):
        compile("NanoBanana2Lite", "variation", {**data, "preserve": ["same room"]}, STYLE_VERSION)
    varied = compile("NanoBanana2Lite", "variation", {**data, "shot_type": "variation",
                     "base_reference": {"media_id": "00000000-0000-4000-8000-000000000001", "sha256": "a" * 64},
                     "preserve": ["Keep room, costume and expression."], "change": ["Raise one hand."]}, STYLE_VERSION)
    assert "Keep room, costume and expression." in varied["prompt"]
    assert "Raise one hand." in varied["prompt"]


@pytest.mark.parametrize("ratio", ["16:9", "9:16"])
def test_real_caller_keeps_shot_type_without_mascot_or_caption_band(tmp_path: Path, ratio: str) -> None:
    pin = create_pin("NanoBanana2Lite", STYLE_VERSION)
    image = {"id": "IM01", "description": "A scholar listens in a simple open courtyard.",
             "preserve": "", "change": "The scholar listens."}
    content = {"characters": [], "scenes": [{"images": [image]}]}
    p = SimpleNamespace(root=tmp_path, brief=lambda job: ({"format_profile": "long_16x9" if ratio == "16:9" else "short_9x16",
                        "aspect_ratio": ratio, "outputs": [{"aspect_ratio": ratio, "subtitles": ratio == "9:16",
                        "language": "vi", "voice": "VietNarrator", "speed": 1.0}]},))
    scene = {"id": "IM01", "shot_type": "full_scene", "visible_text": []}
    with patch("flow_management.prompt_pin", return_value=pin), patch("image_pipeline.content", return_value=content):
        prompt, metadata = _template_request(p, "sample", "IM01", "fallback", "", ratio, [], None, None, scene)
    assert metadata["data"]["description"] == image["description"]
    assert metadata["data"]["shot_type"] == "full_scene"
    assert metadata["data"]["caption_clearance"] is None
    assert "character_reference" not in metadata["data"]
    assert "#8CCFE8" not in prompt


def test_authoring_and_remote_manifest_use_same_style_without_adopting_legacy(tmp_path: Path) -> None:
    topic = ResearchedTopic(topic="A discovery", audience="Students", goal="Understand", video_type="research_explainer")
    assert topic.style == STYLE_DESCRIPTION
    assert render_style({"style": "Legacy marker style"}) is None
    assert render_style({}, {"items": [{"actual_prompt": "legacy"}]}) is None
    assert render_style({}, {"items": [{"actual_prompt": STYLE_DESCRIPTION}]}) == STYLE_ID
    assert render_style({}, {"items": [{"actual_prompt": STYLE_DESCRIPTION}, {"actual_prompt": "legacy"}]}) is None
    (tmp_path / "image.jpg").write_bytes(b"fixture-image")
    (tmp_path / "audio.wav").write_bytes(b"fixture-audio")
    brief = {"aspect_ratio": "16:9", "style": topic.style,
             "outputs": [{"aspect_ratio": "16:9", "language": "vi", "subtitles": False}]}
    images = {"items": [{"path": "image.jpg"}]}
    audio = {"wav": "audio.wav"}
    request = build_render_request(ROOT, brief, {"scenes": []}, images, audio, lambda name: tmp_path / name)
    assert request["visual_style_profile"] == STYLE_ID
    assert "source/renderer/visual-style.mjs" in {entry["name"] for entry in request["files"]}
    old = build_render_request(ROOT, {**brief, "style": "legacy"}, {"scenes": []}, images, audio, lambda name: tmp_path / name)
    assert "visual_style_profile" not in old


def test_executable_renderer_preserves_new_colors_and_legacy_overlays() -> None:
    module = (ROOT / "renderer/visual-style.mjs").as_uri()
    code = f"import {{vignetteBackground as v}} from '{module}'; console.log(JSON.stringify([v({{visual_style_profile:'{STYLE_ID}'}}),v({{hide_overlays:true}}),v({{modern_style:true}}),v({{}})]));"
    result = subprocess.run(["node", "--input-type=module", "-e", code], capture_output=True, text=True, check=True)
    values = json.loads(result.stdout)
    assert values[:2] == [None, None]
    assert "0.22" in values[2]
    assert "0.42" in values[3]


def test_preview_freezes_source_lineage_and_refuses_unresolved_resubmission(tmp_path: Path) -> None:
    from tools.preview_soft_visual_style import SAMPLES, generate, prepare

    for _, job, revision, image_id, _, _, _ in SAMPLES:
        folder = tmp_path / "source/sys/runs" / job / f"revisions/images/{revision}"
        folder.mkdir(parents=True, exist_ok=True)
        image = folder / f"{image_id}.jpg"
        image.write_bytes(b"historical-fixture")
        gallery = folder / "gallery.json"
        items = json.loads(gallery.read_text())["items"] if gallery.exists() else []
        items.append({"image_id": image_id, "path": f"revisions/images/{revision}/{image.name}", "prompt": "Historical action."})
        gallery.write_text(json.dumps({"items": items}))
    output = tmp_path / "preview"
    manifest = prepare(tmp_path / "source", output)
    assert len(manifest["samples"]) == 6
    assert manifest["pin"]["version"] == STYLE_VERSION
    assert all(sample["source_sha256"] == hashlib.sha256(b"historical-fixture").hexdigest() for sample in manifest["samples"])
    assert prepare(tmp_path / "source", output) == manifest
    manifest["samples"][0]["status"] = "unknown"
    with patch("flow_cdp.bridge.generate_cdp_image") as send:
        with pytest.raises(RuntimeError, match="unresolved"):
            generate(manifest, output, ROOT.parent)
    assert not send.called


def test_remote_worker_routes_light_profile_and_rejects_lost_treatment(tmp_path: Path) -> None:
    from colab_bridge.job_worker import run

    for name in ("image.png", "audio.wav"):
        (tmp_path / name).write_bytes(b"contract-fixture")
    brief = {"aspect_ratio": "9:16", "style": STYLE_DESCRIPTION,
             "outputs": [{"aspect_ratio": "9:16", "language": "en", "subtitles": True, "voice": "VietNarrator", "speed": 1.0}]}
    content = {"schema_version": "3.0", "scenes": [{"id": "SC01", "title": "A question", "narration_en": "I see a bird.",
               "beats": [{"id": "BT01", "image_id": "IM01", "anchor": {"en": {"quote": "I", "occurrence": 1}},
                          "effect": "hold", "focus": {"x": .5, "y": .5}}]}]}
    images = {"items": [{"scene_id": "SC01", "image_id": "IM01", "ratio": "9:16", "path": "image.png"}]}
    track = {"language": "en", "voice": "VietNarrator", "speed": 1.0, "wav": "audio.wav", "duration": 5.,
             "segments": [{"scene_id": "SC01", "text": "I see a bird.", "start": 0., "end": 5., "content_end": 4.5, "path": "audio.wav"}]}
    request = build_render_request(ROOT, brief, content, images, {**track, "tracks": {"en": track}}, lambda name: tmp_path / name)
    archive = tmp_path / "input.zip"
    bundle(request, archive)
    chrome = tmp_path / "chrome"
    chrome.touch()

    def fake_render(argv: list[str], **kwargs: object) -> None:
        if argv[0] == "node":
            out = Path(argv[-1])
            (out / "video.mp4").write_bytes(b"\0\0\0\x18ftypisom-contract-fixture")
            (out / "layout.json").write_text(json.dumps({"passed": True}))

    def fake_probe(argv: list[str], **kwargs: object) -> str:
        if argv[0] == "node":
            return str(chrome)
        if argv[0] == "nvidia-smi":
            return "contract-fixture Tesla T4"
        return json.dumps({"format": {"duration": "5.0"}, "streams": [
            {"codec_type": "video", "codec_name": "h264", "width": 1080, "height": 1920},
            {"codec_type": "audio", "codec_name": "aac"}]})

    with patch("colab_bridge.job_worker.subprocess.run", side_effect=fake_render), patch("colab_bridge.job_worker.subprocess.check_output", side_effect=fake_probe):
        report = run(archive, tmp_path / "output", request["request_id"], request["worker_sha256"])
    output = tmp_path / "output"
    props_file = output / "props.json"
    props = json.loads(props_file.read_text())
    assert props["visual_style_profile"] == STYLE_ID
    assert report["processing_location"] == "colab"
    validate_render_result(output, request)
    del props["visual_style_profile"]
    props_file.write_text(json.dumps(props))
    report["files"]["props.json"] = {"size": props_file.stat().st_size, "sha256": hashlib.sha256(props_file.read_bytes()).hexdigest()}
    (output / "render-result.json").write_text(json.dumps(report))
    with pytest.raises(ValueError, match="visual style mismatch"):
        validate_render_result(output, request)
