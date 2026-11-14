"""Contract tests for the Unified Dual-Mode + Modular FX Warehouse Pipeline Bridge."""
from __future__ import annotations

import ast
import io
import json
import math
import subprocess
import sys
import wave
import zipfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

import fx_warehouse as fx_wh
import numpy as np
from flow_video.models import VideoClipTask
from fx_warehouse.audio_suspense_v2 import measure_ebur128
from fx_warehouse.fx_compositor import (
    build_ffmpeg_vfx_filter,
    mix_fx_warehouse_audio,
    prepare_fx_hud_assets,
)
from fx_warehouse.pipeline_bridge import (
    FX_MODE_CHOICES,
    TRIGGER_KEYWORD_TABLE,
    plan_and_prepare_dual_mode_fx,
    resolve_fx_intent_from_text,
)
from PIL import Image
from tools import produce_en_flow_dynamic_demo, produce_vn_dual_mode

ROOT_DIR = Path(__file__).resolve().parents[2]


def _write_minimal_test_spec(path: Path, title: str, beats: list[dict[str, object]]) -> None:
    payload = {
        "title": title,
        "youtube_title": title[:50],
        "beats": beats,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_trigger_keyword_resolution_cross_channel_and_comfort_guardrails() -> None:
    assert "auto_niche" in FX_MODE_CHOICES
    assert "forensic_v2" in FX_MODE_CHOICES
    assert len(TRIGGER_KEYWORD_TABLE) >= 5

    res_pro = resolve_fx_intent_from_text("[PRO_FX] giải mã chuỗi cung ứng bán dẫn", channel_id="ban_do_quyen_luc")
    assert res_pro["effective_mode"] == "auto_niche"
    assert "pro_fx" in res_pro["matched_keywords"]
    assert res_pro["allow_bespoke"] is True

    res_bespoke = resolve_fx_intent_from_text("[BESPOKE_FX] bậc thuế lãi kép mới", channel_id="tui_tien")
    assert res_bespoke["effective_mode"] == "full_fx"
    assert res_bespoke["force_bespoke"] is True
    assert res_bespoke["archetype_id"] == "archetype_4_doodle_explainer"

    res_mindful = resolve_fx_intent_from_text("[FORENSIC_V2] chu kỳ thở 4-7-8", channel_id="chanh_niem_ke")
    assert res_mindful["comfort_downgraded"] is True
    assert res_mindful["effective_mode"] == "auto_niche"

    res_static = resolve_fx_intent_from_text("[STATIC_CLEAN] bản vẽ 2d thuần", channel_id="nao_luoi")
    assert res_static["effective_mode"] == "static"
    assert res_static["allow_bespoke"] is False


def test_forensic_v2_exports_and_plan_routing(tmp_path: Path) -> None:
    assert len(fx_wh.FORENSIC_HUD_V2_CATALOG) == 9
    assert set(fx_wh.VARIANT_PROFILES.keys()) == {"A", "B", "C"}
    assert callable(fx_wh.plan_and_prepare_dual_mode_fx)

    beats = [
        {"narration": "Hồ sơ điều tra năm 2024 về hộp đen CVR và radar eo biển.", "duration": 3.0},
        {"narration": "So sánh hai giả thuyết gây thảm họa mất kiểm soát.", "duration": 2.8},
    ]
    summary = plan_and_prepare_dual_mode_fx(
        channel_slug="ho-so-ky-la",
        beats=beats,
        beat_durations=[3.0, 2.8],
        work_dir=tmp_path / "work_forensic",
        fx_mode="forensic_v2",
        video_topic="hồ sơ hộp đen [BESPOKE_FX]",
        spec_data={"suspense_variant": "B"},
        prepare_audio_assets=True,
    )
    assert summary["enabled"] is True
    assert summary["fx_mode"] == "forensic_v2"
    assert summary["forensic_v2"]["enabled"] is True
    assert summary["forensic_v2"]["hud_catalog_count"] == 9
    assert summary["bespoke_beats"] >= 1
    assert summary["bespoke_sfx_files"]
    for wav_file in summary["bespoke_sfx_files"]:
        with wave.open(wav_file, "rb") as wf:
            assert wf.getnchannels() == 2
            assert wf.getframerate() == 48000

    plan_json = json.loads(Path(summary["fx_plan_path"]).read_text(encoding="utf-8"))
    assert len(plan_json["beats"]) == 2
    assert plan_json["bgm_loop"] == "bgm_forensic_noir_drone.wav"


def test_dual_mode_dry_run_niche_branching_and_static_default(tmp_path: Path) -> None:
    beats_long = [
        {
            "narration": f"Beat {i + 1}: "
            + ("đối chiếu dữ liệu bản đồ eo biển và hồ sơ hộp đen." if i % 2 == 0 else "bậc thuế lãi kép và quy tắc tư duy."),
            "duration": 2.5,
        }
        for i in range(60)
    ]

    spec_forensic = tmp_path / "spec_forensic.json"
    _write_minimal_test_spec(spec_forensic, "Vụ án hộp đen radar", beats_long)

    # 1. Default mode stays backward-compatible static unless opted in
    res_static = produce_vn_dual_mode.run_dry_run_verify(
        produce_vn_dual_mode.DualModeJobConfig(
            mode=produce_vn_dual_mode.DualMode.DRY_RUN_VERIFY.value,
            job_id="dry_static",
            channel_slug="ho-so-ky-la",
            spec_path=spec_forensic,
            output_dir=tmp_path / "out_static",
            render_backend="local",
            dry_run=True,
        )
    )
    assert res_static["status"] == "verified"
    assert res_static["short_verification"]["fx_mode"] == "static"
    assert res_static["long_verification"]["fx_mode"] == "static"

    # 2. Branch A: ho-so-ky-la with [PRO_FX] [BESPOKE_FX]
    res_niche_a = produce_vn_dual_mode.run_dry_run_verify(
        produce_vn_dual_mode.DualModeJobConfig(
            mode=produce_vn_dual_mode.DualMode.DRY_RUN_VERIFY.value,
            job_id="dry_niche_a",
            channel_slug="ho-so-ky-la",
            spec_path=spec_forensic,
            output_dir=tmp_path / "out_niche_a",
            render_backend="local",
            dry_run=True,
            fx_mode="auto_niche",
            video_topic="[PRO_FX] [BESPOKE_FX] hộp đen radar điều tra",
        )
    )
    assert res_niche_a["short_verification"]["fx_archetype"] == "archetype_1_forensic_noir"
    assert res_niche_a["long_verification"]["fx_archetype"] == "archetype_1_forensic_noir"
    plan_a = json.loads(Path(res_niche_a["long_verification"]["fx_plan_path"]).read_text(encoding="utf-8"))
    assert plan_a["enabled"] is True
    assert plan_a["bgm_loop"] == "bgm_forensic_noir_drone.wav"
    assert plan_a["stats"]["bespoke_beats"] >= 1

    # 3. Branch B: tui-tien via universal prompt keywords only (no explicit fx_mode arg)
    spec_finance = tmp_path / "spec_finance.json"
    _write_minimal_test_spec(spec_finance, "Chiến lược lãi kép", beats_long)
    res_niche_b = produce_vn_dual_mode.run_dry_run_verify(
        produce_vn_dual_mode.DualModeJobConfig(
            mode=produce_vn_dual_mode.DualMode.DRY_RUN_VERIFY.value,
            job_id="dry_niche_b",
            channel_slug="tui-tien",
            spec_path=spec_finance,
            output_dir=tmp_path / "out_niche_b",
            render_backend="local",
            dry_run=True,
            video_topic="[FULL_FX] [BESPOKE_FX] bậc thuế và lãi kép",
        )
    )
    assert res_niche_b["long_verification"]["fx_archetype"] == "archetype_4_doodle_explainer"
    plan_b = json.loads(Path(res_niche_b["long_verification"]["fx_plan_path"]).read_text(encoding="utf-8"))
    assert plan_b["bgm_loop"] == "bgm_curious_acoustic_loop.wav"
    assert "crimson_strobe_alert" in plan_b["disallowed_vfx"]
    assert all(b["vfx"] not in plan_b["disallowed_vfx"] for b in plan_b["beats"])


def test_cli_flags_and_universal_docs_contract() -> None:
    with patch.object(
        sys,
        "argv",
        [
            "produce_vn_dual_mode.py",
            "--mode",
            "dry-run-verify",
            "--channel",
            "ban-do-quyen-luc",
            "--fx-mode",
            "auto_niche",
            "--video-topic",
            "[PRO_FX] bán dẫn eo biển",
        ],
    ):
        args = produce_vn_dual_mode.parse_args()
    assert args.fx_mode == "auto_niche"
    assert "[PRO_FX]" in args.video_topic

    index_text = (ROOT_DIR / "INDEX.md").read_text(encoding="utf-8")
    agents_text = (ROOT_DIR / "AGENTS.md").read_text(encoding="utf-8")
    prod_text = (ROOT_DIR / ".agents/skills/vp-production/SKILL.md").read_text(encoding="utf-8")
    wh_text = (ROOT_DIR / ".agents/skills/vp-motion-fx-warehouse/SKILL.md").read_text(encoding="utf-8")

    for text in (index_text, agents_text, prod_text, wh_text):
        assert "auto_niche" in text
        assert "[PRO_FX]" in text
        assert "[BESPOKE_FX]" in text
    assert "pipeline_bridge.py" in wh_text
    assert "Universal Trigger Keywords" in wh_text


def _write_synthetic_voice_wav(path: Path, duration_sec: float = 3.2, sr: int = 48000) -> None:
    n = int(round(duration_sec * sr))
    t = np.arange(n, dtype=np.float32) / float(sr)
    # Speech-like amplitude-modulated warm tone with mid-pause gap so voice ducking activates
    env = 0.55 + 0.45 * np.sin(2.0 * math.pi * 1.4 * t)
    sig = 0.25 * env * (np.sin(2.0 * math.pi * 190.0 * t) + 0.45 * np.sin(2.0 * math.pi * 380.0 * t))
    pcm = np.clip(np.round(np.column_stack([sig, sig]) * 32767.0), -32768, 32767).astype(np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def _write_solid_png(path: Path, size: tuple[int, int], color: tuple[int, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "RGBA" if len(color) == 4 else "RGB"
    Image.new(mode, size, color).save(path, format="PNG")


def test_fx_compositor_audio_mix_lufs_and_hud_assets(tmp_path: Path) -> None:
    voice_wav = tmp_path / "voice.wav"
    _write_synthetic_voice_wav(voice_wav, duration_sec=3.2)

    beats = [
        {"narration": "Hồ sơ điều tra năm 2024 về hộp đen CVR và radar eo biển.", "duration": 1.6},
        {"narration": "So sánh hai giả thuyết gây thảm họa mất kiểm soát.", "duration": 1.6},
    ]
    work_dir = tmp_path / "work"
    summary = plan_and_prepare_dual_mode_fx(
        channel_slug="ho-so-ky-la",
        beats=beats,
        beat_durations=[1.6, 1.6],
        work_dir=work_dir,
        fx_mode="forensic_v2",
        video_topic="[BESPOKE_FX] radar hộp đen",
        spec_data={"suspense_variant": "B"},
        prepare_audio_assets=True,
    )
    assert summary["enabled"] is True

    mixed_wav = work_dir / "mixed.wav"
    mix_info = mix_fx_warehouse_audio(voice_wav, summary["fx_plan_path"], mixed_wav)
    assert mix_info["mixed"] is True
    assert mix_info["bgm_used"] == "bgm_forensic_noir_drone.wav"
    assert mix_info["sfx_mixed"] >= 1
    assert Path(mix_info["out_wav"]).is_file()

    with wave.open(str(mixed_wav), "rb") as wf:
        assert wf.getnchannels() == 2
        assert wf.getframerate() == 48000
        mixed_pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    with wave.open(str(voice_wav), "rb") as wf:
        dry_pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    min_len = min(len(mixed_pcm), len(dry_pcm))
    assert float(np.mean(np.abs(mixed_pcm[:min_len].astype(np.float32) - dry_pcm[:min_len].astype(np.float32)))) > 25.0

    lufs = measure_ebur128(mixed_wav)
    assert -13.0 <= lufs["integrated_lufs"] <= -9.0
    assert lufs["true_peak_dbfs"] <= -0.3

    # Guardrails check
    assert build_ffmpeg_vfx_filter("crimson_strobe_alert", ["crimson_strobe_alert"]) == ""
    assert "vignette" in build_ffmpeg_vfx_filter("hypoxic_vignette", [])

    # 16:9 HUD PNGs + watermark exclusion clearance
    specs_16x9 = prepare_fx_hud_assets(
        fx_plan_path=summary["fx_plan_path"],
        beats=beats,
        overlay_dir=work_dir / "hud_16x9",
        target_w=1920,
        target_h=1080,
        is_short=False,
    )
    rendered_16x9 = [s for s in specs_16x9 if s.get("hud_local_path")]
    assert rendered_16x9
    for sp in rendered_16x9:
        p = Path(sp["hud_local_path"])
        assert p.is_file()
        with Image.open(p) as im:
            assert im.mode == "RGBA"
            assert im.size == (sp["hud_w"], sp["hud_h"])
            assert int(np.asarray(im)[:, :, 3].max()) > 0
        assert 0 <= sp["hud_x"] and sp["hud_x"] + sp["hud_w"] <= 1920
        assert 0 <= sp["hud_y"] and sp["hud_y"] + sp["hud_h"] <= 1080
        if sp["hud_w"] < int(1920 * 0.85):
            in_wm_zone = (sp["hud_x"] + sp["hud_w"] > 1920 - 180) and (sp["hud_y"] + sp["hud_h"] > 1080 - 180)
            assert not in_wm_zone

    # 9:16 Short proportional HUD PNGs
    specs_9x16 = prepare_fx_hud_assets(
        fx_plan_path=summary["fx_plan_path"],
        beats=beats,
        overlay_dir=work_dir / "hud_9x16",
        target_w=1080,
        target_h=1920,
        is_short=True,
    )
    rendered_9x16 = [s for s in specs_9x16 if s.get("hud_local_path")]
    assert rendered_9x16
    for sp in rendered_9x16:
        assert Path(sp["hud_local_path"]).is_file()
        assert 0 <= sp["hud_x"] and sp["hud_x"] + sp["hud_w"] <= 1080
        assert 0 <= sp["hud_y"] and sp["hud_y"] + sp["hud_h"] <= 1920


def test_local_long_mp4_e2e_renders_real_hud_vfx_and_mixed_audio(tmp_path: Path) -> None:
    beats = [
        {"beat_id": "B001", "narration": "Phân tích biểu đồ radar và hộp đen lúc 02:14.", "duration": 1.8},
        {"beat_id": "B002", "narration": "Đối chiếu hai đường áp suất khí quyển bất thường.", "duration": 1.8},
    ]
    durs = [1.8, 1.8]
    img_dir = tmp_path / "imgs"
    img_paths = [img_dir / "img_0000.png", img_dir / "img_0001.png"]
    _write_solid_png(img_paths[0], (640, 360), (14, 24, 38))
    _write_solid_png(img_paths[1], (640, 360), (20, 30, 44))
    wm_png = tmp_path / "watermark.png"
    _write_solid_png(wm_png, (40, 40), (255, 255, 255, 180))
    meta_txt = tmp_path / "chapters_metadata.txt"
    meta_txt.write_text(";FFMETADATA1\n", encoding="utf-8")
    voice_wav = tmp_path / "voice.wav"
    _write_synthetic_voice_wav(voice_wav, duration_sec=3.6)

    chunks = [
        produce_vn_dual_mode.BeatChunk(
            chunk_index=0,
            start_beat_idx=0,
            end_beat_idx=2,
            beats=beats,
            beat_durations=durs,
            chunk_duration=3.6,
            start_time=0.0,
            end_time=3.6,
        )
    ]

    work_dir = tmp_path / "fx_work"
    summary = plan_and_prepare_dual_mode_fx(
        channel_slug="ho-so-ky-la",
        beats=beats,
        beat_durations=durs,
        work_dir=work_dir,
        fx_mode="full_fx",
        video_topic="[FULL_FX] [BESPOKE_FX] radar hộp đen",
        prepare_audio_assets=True,
    )
    mixed_wav = work_dir / "mixed.wav"
    mix_fx_warehouse_audio(voice_wav, summary["fx_plan_path"], mixed_wav)
    specs = prepare_fx_hud_assets(
        fx_plan_path=summary["fx_plan_path"],
        beats=beats,
        overlay_dir=work_dir / "_hud_long",
        target_w=640,
        target_h=360,
        is_short=False,
    )
    assert any(sp.get("hud_local_path") for sp in specs)

    static_mp4 = tmp_path / "static_out.mp4"
    fx_mp4 = tmp_path / "fx_out.mp4"
    produce_vn_dual_mode.render_long_chapter_chunks_local(
        job_id="t_static",
        chunks=chunks,
        image_paths=img_paths,
        audio_path=voice_wav,
        metadata_path=meta_txt,
        watermark_png=wm_png,
        out_mp4=static_mp4,
        width=640,
        height=360,
        fps=15,
        scratch_dir=tmp_path / "_loc_static",
        beat_fx_specs=None,
    )
    produce_vn_dual_mode.render_long_chapter_chunks_local(
        job_id="t_fx",
        chunks=chunks,
        image_paths=img_paths,
        audio_path=mixed_wav,
        metadata_path=meta_txt,
        watermark_png=wm_png,
        out_mp4=fx_mp4,
        width=640,
        height=360,
        fps=15,
        scratch_dir=tmp_path / "_loc_fx",
        beat_fx_specs=specs,
    )

    assert fx_mp4.is_file() and fx_mp4.stat().st_size > 10_000
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(fx_mp4)],
        check=True,
        capture_output=True,
        text=True,
    )
    info = json.loads(probe.stdout)
    streams = {s["codec_type"]: s for s in info["streams"]}
    assert streams["video"]["width"] == 640 and streams["video"]["height"] == 360
    assert streams["audio"]["codec_name"] == "aac"
    assert int(streams["audio"]["channels"]) == 2
    assert float(info["format"]["duration"]) >= 3.0

    # Extract t=0.6s frame from both static & full_fx renders and verify rendered pixel delta
    f_static = tmp_path / "f_static.png"
    f_fx = tmp_path / "f_fx.png"
    for mp4, out_png in ((static_mp4, f_static), (fx_mp4, f_fx)):
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", "0.6", "-i", str(mp4), "-frames:v", "1", str(out_png)],
            check=True,
        )
    arr_s = np.asarray(Image.open(f_static).convert("RGB"), dtype=np.int16)
    arr_f = np.asarray(Image.open(f_fx).convert("RGB"), dtype=np.int16)
    abs_diff = np.abs(arr_f - arr_s)
    assert float(abs_diff.mean()) > 1.0
    assert int((abs_diff.max(axis=2) > 8).sum()) > 500


def test_colab_t4_long_and_short_bundle_pack_fx_hud_and_valid_scripts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    beats = [
        {"beat_id": "B001", "narration": "Dữ liệu radar hộp đen trên bản đồ eo biển.", "duration": 2.0},
    ]
    durs = [2.0]
    img_p = tmp_path / "img_0000.png"
    _write_solid_png(img_p, (640, 360), (24, 34, 52))
    wm_png = tmp_path / "watermark.png"
    _write_solid_png(wm_png, (64, 64), (255, 255, 255, 200))
    meta_txt = tmp_path / "chapters_metadata.txt"
    meta_txt.write_text(";FFMETADATA1\n", encoding="utf-8")
    voice_wav = tmp_path / "voice.wav"
    _write_synthetic_voice_wav(voice_wav, duration_sec=2.0)

    chunks = [
        produce_vn_dual_mode.BeatChunk(
            chunk_index=0,
            start_beat_idx=0,
            end_beat_idx=1,
            beats=beats,
            beat_durations=durs,
            chunk_duration=2.0,
            start_time=0.0,
            end_time=2.0,
        )
    ]
    work_dir = tmp_path / "colab_work"
    summary = plan_and_prepare_dual_mode_fx(
        channel_slug="ho-so-ky-la",
        beats=beats,
        beat_durations=durs,
        work_dir=work_dir,
        fx_mode="full_fx",
        video_topic="[FULL_FX] [BESPOKE_FX] radar",
        prepare_audio_assets=False,
    )
    specs = prepare_fx_hud_assets(
        fx_plan_path=summary["fx_plan_path"],
        beats=beats,
        overlay_dir=work_dir / "_hud_long",
        target_w=1920,
        target_h=1080,
        is_short=False,
    )

    captured_long_zip: dict[str, bytes] = {}

    class MockLongClient:
        def __init__(self, sys_dir, cfg):
            self.account = cfg.get("colab_tts", {}).get("account", "account-01")
            self.session = cfg.get("colab_tts", {}).get("session", "mock-long-sess")

        def ensure_authenticated(self):
            pass

        def _ready(self, auto_start=True):
            pass

        def exec(self, cmd, timeout=30):
            if "shutil.disk_usage" in cmd:
                return "WORK_DIR:/dev/shm/vp_fx_test"
            if "status.json" in cmd:
                return 'POLL_STATUS:{"status": "completed", "completed_chunks": 1, "total_chunks": 1}'
            return ""

        def call(self, action, *args, **kwargs):
            if action == "upload":
                captured_long_zip["bytes"] = Path(args[2]).read_bytes()
            elif action == "download":
                subprocess.run(
                    ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=64x64:d=0.2", "-c:v", "libx264", str(args[3])],
                    check=True,
                    capture_output=True,
                )

        def stop(self):
            pass

    monkeypatch.setattr(produce_vn_dual_mode, "Client", MockLongClient)
    long_meta = produce_vn_dual_mode.render_long_chapter_chunks_colab_t4(
        job_id="t_colab_fx",
        chunks=chunks,
        image_paths=[img_p],
        audio_path=voice_wav,
        metadata_path=meta_txt,
        watermark_png=wm_png,
        out_mp4=tmp_path / "colab_long.mp4",
        width=1920,
        height=1080,
        fps=30,
        scratch_dir=tmp_path / "_colab_long",
        fx_summary=summary,
        beat_fx_specs=specs,
    )
    assert long_meta["video_encoder"] == "colab_t4_h264_nvenc"
    with zipfile.ZipFile(io.BytesIO(captured_long_zip["bytes"])) as zf:
        names = set(zf.namelist())
        assert {"manifest.json", "render_job.py", "narration.m4a", "watermark.png", "chapters_metadata.txt"} <= names
        hud_names = [n for n in names if n.startswith("hud_overlays/") and n.endswith(".png")]
        assert hud_names
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
        assert manifest["fx_warehouse"]["enabled"] is True
        beat_m = manifest["chunks"][0]["beats"][0]
        assert beat_m["hud_file"].startswith("hud_overlays/")
        assert beat_m["fx_cam_params"]["z1"] > 0.0
        render_py = zf.read("render_job.py").decode("utf-8")
        ast.parse(render_py)
        assert "_render_fx_beat_cuda" in render_py

    # Now test Short 9:16 bundle packing + f-string script syntax + real ffmpeg HUD overlay filter
    short_specs = prepare_fx_hud_assets(
        fx_plan_path=summary["fx_plan_path"],
        beats=beats,
        overlay_dir=work_dir / "_hud_short",
        target_w=1080,
        target_h=1920,
        is_short=True,
    )
    short_events = [s for s in short_specs if s.get("hud_local_path")]
    assert short_events

    clip_mp4 = tmp_path / "clip_00.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=#141c28:s=360x640:d=1.2", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip_mp4)],
        check=True,
        capture_output=True,
    )
    ass_p = tmp_path / "subtitles.ass"
    ass_p.write_text("[Script Info]\nScriptType: v4.00+\n", encoding="utf-8")
    srt_p = tmp_path / "subtitles.srt"
    srt_p.write_text("1\n00:00:00,000 --> 00:00:01,000\nRadar\n", encoding="utf-8")

    captured_short: dict[str, Any] = {}

    class MockShortClient:
        def __init__(self, sys_dir, cfg):
            self.cfg = dict(cfg.get("colab_tts", {}))
            self.account = self.cfg.get("account", "account-01")
            self.session = self.cfg.get("session", "mock-short-sess")

        def ensure_authenticated(self):
            pass

        def _ready(self, auto_start=True):
            pass

        def exec(self, cmd, timeout=30):
            captured_short["exec_cmds"] = captured_short.get("exec_cmds", []) + [cmd]
            if "NVENC_RENDER_SUCCESS" in cmd:
                captured_short["remote_script"] = cmd
                ast.parse(cmd)
                return "NVENC_RENDER_SUCCESS"
            return ""

        def call(self, action, *args, **kwargs):
            if action == "upload":
                captured_short["zip_bytes"] = Path(args[2]).read_bytes()
            elif action == "download":
                shutil_copy_mp4 = Path(args[3])
                shutil_copy_mp4.write_bytes(clip_mp4.read_bytes())

        def stop(self):
            pass

    import colab_bridge.client as colab_client_mod

    monkeypatch.setattr(colab_client_mod, "Client", MockShortClient)
    task0 = VideoClipTask(clip_id="C0", index=0, start_frame_path=str(img_p), output_mp4_path=str(clip_mp4))
    short_meta = produce_en_flow_dynamic_demo.package_final_on_colab_t4_nvenc(
        channel_slug="ho-so-ky-la",
        job_id="t_short_fx",
        aspect="9:16",
        groups=[[0]],
        tasks=[task0],
        group_spoken_durs=[1.2],
        beat_durations=[1.2],
        audio_path=voice_wav,
        ass_path=ass_p,
        srt_path=srt_p,
        watermark_png=wm_png,
        out_mp4=tmp_path / "short_final.mp4",
        fps=30,
        scratch_dir=tmp_path / "_short_bundle",
        colab_account="account-01",
        fx_hud_events=short_events,
    )
    assert short_meta["video_encoder"] == "colab_t4_h264_nvenc"
    with zipfile.ZipFile(io.BytesIO(captured_short["zip_bytes"])) as zf:
        snames = set(zf.namelist())
        assert any(n.startswith("hud_overlays/") for n in snames)
        smanifest = json.loads(zf.read("bundle_manifest.json").decode("utf-8"))
        assert len(smanifest["fx_hud_events"]) == len(short_events)
    assert "enable='between(t," in captured_short["remote_script"]

    # Smoke-verify FFmpeg single-frame PNG + eof_action=repeat:enable='between(...)' overlay really burns pixels
    short_overlay_out = tmp_path / "short_hud_burned.mp4"
    ev0 = short_events[0]
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(clip_mp4),
            "-i", str(ev0["hud_local_path"]),
            "-filter_complex",
            "[0:v][1:v]overlay=x=0:y=40:eof_action=repeat:enable='between(t,0.100,0.900)'[vout]",
            "-map", "[vout]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an",
            str(short_overlay_out),
        ],
        check=True,
    )
    f_before = tmp_path / "before.png"
    f_after = tmp_path / "after.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "0.5", "-i", str(clip_mp4), "-frames:v", "1", str(f_before)], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "0.5", "-i", str(short_overlay_out), "-frames:v", "1", str(f_after)], check=True)
    diff_s = np.abs(np.asarray(Image.open(f_after), dtype=np.int16) - np.asarray(Image.open(f_before), dtype=np.int16))
    assert float(diff_s.mean()) > 0.5
