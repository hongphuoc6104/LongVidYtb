"""Unit and CLI tests for the modular Single-Pass Turbo Serialized Short Engine."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest
import short_engine
from tools.produce_serialized_short import (
    build_kenburns_filter,
    classify_hybrid_beats,
    main,
    plan_chunked_render_timeline,
    render_heroic_banner_png,
    resolve_worker_count,
    select_idle_colab_accounts,
    slice_ass_for_window,
    synthesize_heroic_epic_score,
)


def _make_synthetic_28_beat_spec_and_timings() -> tuple[dict, dict]:
    beats: list[dict] = []
    t_beats: list[dict] = []
    dur_sec = (4371 / 30.0) / 28.0
    cur = 4 / 30.0
    for i in range(28):
        bid = f"B{i:02d}"
        act = 1 if i < 5 else (2 if i < 8 else (3 if i < 14 else (4 if i < 22 else 5)))
        if i == 0:
            role, stype, deliv, tmode = "hook", "live_action", "climax_heroic", "seam"
        elif i in (3, 7, 12, 22, 24):
            role, stype, deliv, tmode = "mechanism", "tactical_sand_table", "tactical_breakdown", "seam"
        elif i == 17:
            role, stype, deliv, tmode = "twist", "live_action", "urgent_escalation", "frame_link"
        elif i == 18:
            role, stype, deliv, tmode = "mechanism", "live_action", "tactical_breakdown", "seam"
        elif i in (2, 11):
            role, stype, deliv, tmode = "mechanism", "live_action", "tactical_breakdown", "seam"
        elif i == 23:
            role, stype, deliv, tmode = "payoff", "live_action", "reflective_lesson", "seam"
        else:
            role, stype, deliv, tmode = "context", "live_action", "narrative_cinema", "seam"

        end_t = (4375 / 30.0) if i == 27 else (cur + dur_sec)
        beats.append({
            "beat_index": i,
            "beat_id": bid,
            "act": act,
            "role": role,
            "scene_type": stype,
            "delivery_mode": deliv,
            "transition_mode": tmode,
            "camera_move": ("push_in", "pull_back", "truck_lateral", "orbit", "crane_up")[i % 5],
            "clip_duration_seconds": 6,
        })
        t_beats.append({
            "beat_id": bid,
            "start_sec": round(cur, 6),
            "end_sec": round(end_t, 6),
            "duration_sec": round(end_t - cur, 6),
        })
        cur = end_t

    return {"job_id": "synth_28", "channel_id": "su_ke_lai", "beats": beats}, {"total_duration_sec": round(4375 / 30.0, 6), "beats": t_beats}


def _make_synthetic_20_beat_v3_spec_and_timings() -> tuple[dict, dict]:
    beats: list[dict] = []
    t_beats: list[dict] = []
    total_sec = 108.0
    total_frames = int(round(total_sec * 30))
    dur_sec = ((total_frames - 4) / 30.0) / 20.0
    cur = 4 / 30.0
    flow_set = {0, 1, 4, 6, 8, 11, 12, 13, 14, 15, 16, 19}
    for i in range(20):
        bid = f"B{i:02d}"
        act = 1 if i < 5 else (2 if i < 7 else (3 if i < 10 else (4 if i < 17 else 5)))
        override = "flow_video" if i in flow_set else "2k_native_kenburns"
        deliv = "tense_whisper" if i in (10, 11, 12) else ("climax_heroic" if i in (0, 14, 15, 16, 19) else "narrative_cinema")
        end_t = total_sec if i == 19 else (cur + dur_sec)
        beats.append({
            "beat_index": i,
            "beat_id": bid,
            "act": act,
            "role": "silence_vacuum" if i == 12 else ("twist" if i in (13, 14) else "context"),
            "scene_type": "live_action",
            "asset_mode_override": override,
            "delivery_mode": deliv,
            "transition_mode": "seam",
            "camera_move": ("push_in", "pull_back", "truck_lateral", "crane_up", "orbit")[i % 5],
            "clip_duration_seconds": 6,
        })
        t_beats.append({"beat_id": bid, "start_sec": round(cur, 6), "end_sec": round(end_t, 6), "duration_sec": round(end_t - cur, 6)})
        cur = end_t

    hud_stamps = [
        {"beat_id": "B00", "kind": "heroic_banner", "headline": "KHÔNG 1 MŨI TÊN", "font_size": 136, "anchor_y": 150},
        {"beat_id": "B05", "kind": "heroic_banner", "headline": "LỪA THỜI GIAN", "font_size": 136, "anchor_y": 150},
        {"beat_id": "B09", "kind": "heroic_banner", "headline": "BỊT MẮT ĐỊCH", "font_size": 136, "anchor_y": 150},
        {"beat_id": "B13", "kind": "heroic_banner", "headline": "VÒNG LỬA RỰC TRỜI", "font_size": 136, "anchor_y": 150},
        {"beat_id": "B17", "kind": "heroic_banner", "headline": "MƯU TRÍ QUANG TRUNG", "font_size": 136, "anchor_y": 150},
    ]
    spec = {
        "job_id": "synth_20_v3",
        "channel_id": "su_ke_lai",
        "bgm_plan": {"mode": "heroic_vietnam_epic", "silence_vacuum": {"beat_id": "B12"}, "climax_beats": ["B13", "B14", "B15", "B16"], "proud_beats": ["B17", "B18", "B19"]},
        "hud_stamps": hud_stamps,
        "beats": beats,
    }
    return spec, {"total_duration_sec": total_sec, "beats": t_beats}


def test_classify_hybrid_beats_full_video_hybrid_2k_and_override() -> None:
    spec, _ = _make_synthetic_28_beat_spec_and_timings()
    spec["beats"][14].update({"act": 4, "role": "mechanism", "delivery_mode": "tactical_breakdown"})
    spec["beats"][18].update({"act": 5, "scene_type": "tactical_sand_table", "role": "mechanism", "delivery_mode": "tactical_breakdown"})

    assert all(b["asset_mode"] == "flow_video" for b in classify_hybrid_beats(spec, visual_mode="full_video"))
    by_id = {b["beat_id"]: b for b in classify_hybrid_beats(spec, visual_mode="hybrid_2k")}
    assert by_id["B00"]["asset_mode"] == "flow_video"
    assert by_id["B14"]["asset_mode"] == "flow_video"
    assert by_id["B17"]["asset_mode"] == "flow_video"
    assert by_id["B18"]["asset_mode"] == "flow_video"
    for bid in ("B02", "B03", "B07", "B11", "B12", "B22", "B23", "B24"):
        assert by_id[bid]["asset_mode"] == "2k_native_kenburns"

    spec20, _ = _make_synthetic_20_beat_v3_spec_and_timings()
    cls20 = classify_hybrid_beats(spec20, visual_mode="hybrid_2k")
    assert sum(1 for b in cls20 if b["asset_mode"] == "flow_video") == 12
    assert sum(1 for b in cls20 if b["asset_mode"] == "2k_native_kenburns") == 8
    assert all(b["asset_mode"] == "flow_video" for b in classify_hybrid_beats(spec20, visual_mode="full_video"))


def test_plan_chunked_render_timeline_single_pass_and_two_pass() -> None:
    spec28, tim28 = _make_synthetic_28_beat_spec_and_timings()
    items28, chunks28, tf28 = plan_chunked_render_timeline(spec28, tim28, visual_mode="hybrid_2k", render_mode="two_pass", require_media=False)
    assert len(chunks28) == 4 and [len(c["clip_indices"]) for c in chunks28] == [7, 7, 7, 7]
    assert tf28 == 4375 and sum(chk["chunk_base_frames"] for chk in chunks28) == 4375
    assert items28[17]["overlap_frames"] == 2 and items28[18]["trim_lead_frame"] is True

    spec20, tim20 = _make_synthetic_20_beat_v3_spec_and_timings()
    items20, chunks20, tf20 = plan_chunked_render_timeline(spec20, tim20, visual_mode="hybrid_2k", render_mode="single_pass", require_media=False)
    assert tf20 == 3240 and len(chunks20) == 4 and [len(c["clip_indices"]) for c in chunks20] == [5, 5, 5, 5]
    assert all(chk["overhang_frames"] == 0 for chk in chunks20)
    assert sum(chk["expected_frames"] for chk in chunks20) == 3240
    assert sum(1 for it in items20 if it["asset_mode"] == "flow_video") == 12
    assert chunks20[0]["has_poster"] is True


def test_render_heroic_banner_png_enforces_min_132px_and_max_4_words() -> None:
    banner_1, sz_1 = render_heroic_banner_png({"headline": "KHÔNG 1 MŨI TÊN", "font_size": 80})
    assert sz_1 == 132 and banner_1.mode == "RGBA" and banner_1.width <= 1400
    banner_2, sz_2 = render_heroic_banner_png({"headline": "MƯU TRÍ QUANG TRUNG", "font_size": 140})
    assert sz_2 == 140 and banner_2.height >= 180
    with pytest.raises(ValueError, match="1..4 words"):
        render_heroic_banner_png({"headline": "QUÁ NĂM TỪ TRÊN MÀN"})
    with pytest.raises(ValueError, match="1..4 words"):
        render_heroic_banner_png({"headline": "   "})


def test_slice_ass_for_window_rebases_and_clamps(tmp_path: Path) -> None:
    src = tmp_path / "full.ass"
    src.write_text(
        "[Script Info]\nPlayResX: 1440\n\n[V4+ Styles]\nStyle: KineticRed,Noto Sans,132,&H00303BFF\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        "Dialogue: 0,0:00:02.00,0:00:05.00,KineticRed,,0,0,0,,Một\n"
        "Dialogue: 0,0:00:26.00,0:00:28.50,KineticRed,,0,0,0,,Hai\n"
        "Dialogue: 0,0:00:29.50,0:00:31.00,KineticRed,,0,0,0,,Ba\n",
        encoding="utf-8",
    )
    out = slice_ass_for_window(src, 27.0, 30.0, tmp_path / "chunk.ass")
    lines = [ln for ln in out.read_text(encoding="utf-8").splitlines() if ln.startswith("Dialogue:")]
    assert lines == [
        "Dialogue: 0,0:00:00.00,0:00:01.50,KineticRed,,0,0,0,,Hai",
        "Dialogue: 0,0:00:02.50,0:00:03.00,KineticRed,,0,0,0,,Ba",
    ]


def test_synthesize_heroic_epic_score_climax_stronger_than_vacuum() -> None:
    spec, tim = _make_synthetic_20_beat_v3_spec_and_timings()
    measured = [{"beat_id": b["beat_id"], "act": b["act"], "role": b["role"], "delivery_mode": b["delivery_mode"], "start_sec": t["start_sec"], "end_sec": t["end_sec"]} for b, t in zip(spec["beats"], tim["beats"], strict=True)]
    sr = 48000
    score = synthesize_heroic_epic_score(measured, spec, int(tim["total_duration_sec"] * sr), sr=sr)
    assert score.shape == (int(tim["total_duration_sec"] * sr), 2) and np.isfinite(score).all()
    b12 = measured[12]
    b14 = measured[14]
    vac_slice = score[int(b12["start_sec"] * sr) : int((b12["start_sec"] + 2.0) * sr)]
    clx_slice = score[int(b14["start_sec"] * sr) : int(b14["end_sec"] * sr)]
    vac_rms = float(np.sqrt(np.mean(vac_slice ** 2)))
    clx_rms = float(np.sqrt(np.mean(clx_slice ** 2)))
    assert clx_rms > vac_rms * 5.0


def test_resolve_worker_count_and_kenburns_trajectories() -> None:
    assert 6 <= resolve_worker_count("auto") <= 10
    assert resolve_worker_count("9") == 9
    assert resolve_worker_count(0) == 1
    for move in ("push_in", "pull_back", "truck_lateral", "tracking_alongside", "crane_up", "orbit"):
        assert ":d=120:s=1440x2560:fps=30,setsar=1" in build_kenburns_filter(move, 120)


def test_select_idle_colab_accounts_probes_with_refresh_auth_and_fast_boot_order(monkeypatch, tmp_path: Path) -> None:
    probe_server_calls, probe_calls = [], []

    class FakePoolManager:
        binary = "/usr/bin/colab"

        def get_status(self, probe_server: bool = False) -> dict:
            probe_server_calls.append(probe_server)
            return {
                "workers": [
                    {"id": "account-01", "state": "healthy", "external_lock_busy": False, "local_sessions": []},
                    {"id": "account-02", "state": "healthy", "external_lock_busy": False, "local_sessions": []},
                    {"id": "account-08", "state": "healthy", "external_lock_busy": False, "local_sessions": []},
                    {"id": "account-13", "state": "healthy", "external_lock_busy": False, "local_sessions": []},
                ]
            }

    class FakeBudgets:
        path = tmp_path / "budgets.json"

        def read(self) -> dict:
            return {"aliases": {f"colab:account-{k}": f"id-{k}" for k in ("01", "02", "08", "13")}}

        def snapshot(self, alias: str) -> dict:
            base = {"identity_configured": True, "blocks": {}, "allocated_sessions": [], "uncertain": False, "needs_service_recheck": False, "available_seconds": 12000.0}
            if alias == "colab:account-02":
                return {**base, "blocks": {"colab": {"error": "429"}}}
            if alias == "colab:account-08":
                return {**base, "needs_service_recheck": True}
            return base

    class FakeClient:
        def __init__(self, *_a, **_kw) -> None:
            pass

        def _budgets(self) -> FakeBudgets:
            return FakeBudgets()

    def fake_assign(_bin: str, acc: str, session: str, *, refresh_auth: bool = False) -> dict:
        probe_calls.append((acc, session, refresh_auth))
        assert refresh_auth is True
        return {"verified": True, "assignment_count": 1 if acc == "account-13" else 0}

    target_mod = sys.modules[select_idle_colab_accounts.__module__]
    assert target_mod is short_engine
    monkeypatch.setattr(target_mod, "ColabPoolManager", FakePoolManager)
    monkeypatch.setattr(target_mod, "Client", FakeClient)
    monkeypatch.setattr(target_mod.colab_accounts, "assignment_state", fake_assign)

    selected = select_idle_colab_accounts("vp-r1-test", max_accounts=4, min_seconds=360.0)
    assert selected == ["account-01"]
    assert probe_server_calls == [False]
    assert probe_calls == [("account-01", "vp-r1-test", True), ("account-13", "vp-r1-test", True)]


def test_cli_prep_only_validates_single_pass_20_beat_v3(tmp_path: Path, capsys) -> None:
    spec, tim = _make_synthetic_20_beat_v3_spec_and_timings()
    job_dir = tmp_path / "ep06_v3"
    job_dir.mkdir()
    spec_path = job_dir / "ep06_p1_short_spec.json"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    (job_dir / "audio_timings.json").write_text(json.dumps(tim, ensure_ascii=False), encoding="utf-8")

    out_bench = job_dir / "bench.mp4"
    rc = main(["--spec", str(spec_path), "--prep-only", "--render-mode", "single_pass", "--visual-mode", "hybrid_2k", "--out-mp4", str(out_bench)])
    assert rc == 0
    r = json.loads(capsys.readouterr().out)["render"]
    assert r["prep_only"] is True and r["render_mode"] == "single_pass"
    assert r["total_beats"] == 20 and r["flow_video_beats"] == 12 and r["kenburns_2k_beats"] == 8
    assert r["total_frames"] == 3240 and r["hud_stamps_count"] == 5
    assert [c["items"] for c in r["chunks"]] == [5, 5, 5, 5]
    assert all(c["overhang_frames"] == 0 for c in r["chunks"])
    assert Path(r["hud_stamps_preview"]).is_file() and not out_bench.exists()
