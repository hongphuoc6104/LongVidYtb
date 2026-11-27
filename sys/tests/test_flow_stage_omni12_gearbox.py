"""Regression tests for Flow Stage B Omni 1.2 variable gearbox & anti-MISMATCHED_FRAMELINK_JUMPCUT guard."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from PIL import Image
from short_engine import flow_stage


def _make_dummy_frame(path: Path) -> None:
    import numpy as np

    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    arr = rng.integers(0, 255, size=(1920, 1080, 3), dtype=np.uint8)
    Image.fromarray(arr, mode="RGB").save(path, format="PNG")


def _make_dummy_mp4(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x00" * 250_000)


class _DummyLock:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def acquire_patiently(self, *args: Any, **kwargs: Any) -> bool:
        return True

    def release(self) -> None:
        pass


def test_select_omni12_gearbox_duration() -> None:
    assert flow_stage._select_omni12_gearbox_duration(2.5) == 4
    assert flow_stage._select_omni12_gearbox_duration(4.2) == 4
    assert flow_stage._select_omni12_gearbox_duration(4.3) == 6
    assert flow_stage._select_omni12_gearbox_duration(6.2) == 6
    assert flow_stage._select_omni12_gearbox_duration(6.3) == 8
    assert flow_stage._select_omni12_gearbox_duration(8.2) == 8
    assert flow_stage._select_omni12_gearbox_duration(8.3) == 10


def test_stage_b_never_auto_framelinks_across_cuts_and_guards_oner_pairs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spec_dir = tmp_path / "run"
    work_root = tmp_path / "work"
    frames_dir = spec_dir / "frames"
    for i in range(7):
        _make_dummy_frame(frames_dir / f"beat_{i:02d}.png")

    short_spec: dict[str, Any] = {
        "job_id": "test_v12_framelink_guard",
        "channel_id": "su_ke_lai",
        "schema_version": "v12_cinematic",
        "beats": [
            # B00: frame_link WITHOUT explicit end_beat_id -> MUST force seam & end_image_path=None (never auto-link B01!)
            {
                "beat_id": "B00",
                "beat_index": 0,
                "start_sec": 0.0,
                "end_sec": 3.5,
                "asset_mode_override": "flow_video",
                "transition_mode": "frame_link",
                "lighting_key": "night_torch",
                "motion_prompt": "Slow macro push-in on wet stones.",
            },
            # B01: frame_link WITH explicit end_beat_id="B02" -> allowed!
            {
                "beat_id": "B01",
                "beat_index": 1,
                "start_sec": 3.5,
                "end_sec": 8.5,
                "asset_mode_override": "flow_video",
                "transition_mode": "frame_link",
                "end_beat_id": "B02",
                "lighting_key": "night_torch",
                "motion_prompt": "Continuous glide from B01 to B02.",
            },
            # B02 + B03: oner_pair with BOTH frame_link & SAME lighting_key -> links B02 -> B03 (NEVER B04!)
            {
                "beat_id": "B02",
                "beat_index": 2,
                "start_sec": 8.5,
                "end_sec": 13.0,
                "asset_mode_override": "flow_video",
                "oner_group_id": "oner_same_light",
                "transition_mode": "frame_link",
                "lighting_key": "dawn_mist",
                "motion_prompt": "Steadicam follow behind sandals.",
            },
            {
                "beat_id": "B03",
                "beat_index": 3,
                "start_sec": 13.0,
                "end_sec": 17.5,
                "asset_mode_override": "flow_video",
                "oner_group_id": "oner_same_light",
                "transition_mode": "frame_link",
                "lighting_key": "dawn_mist",
                "motion_prompt": "Tilting up to carrying pole.",
            },
            # B04 + B05: oner_pair with MISMATCHED lighting_key -> MUST force seam & end_image_path=None!
            {
                "beat_id": "B04",
                "beat_index": 4,
                "start_sec": 17.5,
                "end_sec": 22.0,
                "asset_mode_override": "flow_video",
                "oner_group_id": "oner_mismatched_light",
                "transition_mode": "frame_link",
                "lighting_key": "night_torch",
                "motion_prompt": "Dark torchlit alley.",
            },
            {
                "beat_id": "B05",
                "beat_index": 5,
                "start_sec": 22.0,
                "end_sec": 26.5,
                "asset_mode_override": "flow_video",
                "oner_group_id": "oner_mismatched_light",
                "transition_mode": "frame_link",
                "lighting_key": "noon_sunlight",
                "motion_prompt": "Bright sunny courtyard.",
            },
            # B06: normal seam beat > 6.2s -> 8s gearbox, seam mode, end_image_path=None
            {
                "beat_id": "B06",
                "beat_index": 6,
                "start_sec": 26.5,
                "end_sec": 33.5,
                "asset_mode_override": "flow_video",
                "transition_mode": "seam",
                "lighting_key": "noon_sunlight",
                "motion_prompt": "Wide sunlit street receding glide.",
            },
        ],
    }

    captured: dict[str, Any] = {}

    class _FakeOrchestrator:
        def __init__(self, spec: Any, work_dir: Path, **kwargs: Any) -> None:
            captured["spec"] = spec
            self.spec = spec
            self.work_dir = work_dir

        def run(self) -> dict[str, Any]:
            clips = []
            for idx, sp in enumerate(self.spec.scene_pairs):
                out_mp4 = self.work_dir / f"fake_{idx:03d}_{sp.id}.mp4"
                _make_dummy_mp4(out_mp4)
                clips.append({"clip_id": f"clip_{idx:03d}_{sp.id}", "output_mp4_path": str(out_mp4)})
            return {"clips": clips, "total_credit_cost": 0, "credits_deducted": {}}

    def _fake_split(src_mp4: Path, split_sec: float, dst_first: Path, dst_second: Path) -> None:
        _make_dummy_mp4(dst_first)
        _make_dummy_mp4(dst_second)

    monkeypatch.setattr(flow_stage, "FlowVideoChainOrchestrator", _FakeOrchestrator)
    monkeypatch.setattr(flow_stage, "GlobalFlowProductionLock", _DummyLock)
    monkeypatch.setattr(flow_stage, "_cleanup_all_chrome", lambda: None)
    monkeypatch.setattr(flow_stage, "_split_oner_clip_mp4", _fake_split)

    res = flow_stage.run_flow_stage_b(short_spec, spec_dir, work_root, max_workers=2)
    assert res["status"] == "completed"
    assert res["oner_pairs_split"] == 2

    pairs = {sp.id: sp for sp in captured["spec"].scene_pairs}
    assert set(pairs.keys()) == {"B00", "B01", "B02_B03_oner", "B04_B05_oner", "B06"}

    # B00: MUST NOT auto-link B01
    assert pairs["B00"].transition_mode == "seam"
    assert pairs["B00"].end_image_path is None
    assert pairs["B00"].end_image_prompt is None
    assert pairs["B00"].clip_duration_sec == 4

    # B01: explicit end_beat_id="B02" honored
    assert pairs["B01"].transition_mode == "frame_link"
    assert Path(pairs["B01"].end_image_path).name == "beat_02.png"
    assert pairs["B01"].clip_duration_sec == 6

    # B02_B03_oner: same lighting + both frame_link -> links B02 -> B03 (NEVER B04!)
    assert pairs["B02_B03_oner"].transition_mode == "frame_link"
    assert Path(pairs["B02_B03_oner"].start_image_path).name == "beat_02.png"
    assert Path(pairs["B02_B03_oner"].end_image_path).name == "beat_03.png"
    assert pairs["B02_B03_oner"].clip_duration_sec == 10

    # B04_B05_oner: mismatched lighting -> forced seam & end_image_path=None
    assert pairs["B04_B05_oner"].transition_mode == "seam"
    assert pairs["B04_B05_oner"].end_image_path is None
    assert pairs["B04_B05_oner"].end_image_prompt is None
    assert pairs["B04_B05_oner"].clip_duration_sec == 10

    # B06: 7.0s -> 8s gearbox, seam mode
    assert pairs["B06"].transition_mode == "seam"
    assert pairs["B06"].end_image_path is None
    assert pairs["B06"].clip_duration_sec == 8
