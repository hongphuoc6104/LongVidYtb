"""Unit tests for the Unified Flow Remotion E2E runner (produce_unified_flow_remotion_e2e.py)."""
from __future__ import annotations

import json
from pathlib import Path
from sys.flow_cdp.credit_ledger import CreditLedger
from sys.flow_video.models import ChainMode, KeyframeSpec
from sys.tools.produce_unified_flow_remotion_e2e import (
    collect_full_chain_keyframes,
    collect_hybrid_scene_pairs,
    produce_unified_flow_remotion_e2e,
    register_clips_to_timeline,
    resolve_motion_mode,
    select_hybrid_hero_scenes,
)
from unittest.mock import MagicMock, patch


def test_select_hybrid_hero_scenes() -> None:
    # 1. When scenes have flow_motion explicitly set
    scenes_explicit = [
        {"id": "SC01", "flow_motion": False, "beats": []},
        {"id": "SC02", "flow_motion": True, "beats": []},
        {"id": "SC03", "beats": [{"id": "b3", "flow_motion": True}]},
        {"id": "SC04", "beats": []},
    ]
    hero = select_hybrid_hero_scenes(scenes_explicit)
    assert len(hero) == 2
    assert hero[0]["id"] == "SC02"
    assert hero[1]["id"] == "SC03"

    # 2. When no scene has flow_motion set: picks hook (0), midpoint (2), pre-outro (3)
    scenes_implicit = [
        {"id": "SC01", "images": [{"id": "img1"}]},
        {"id": "SC02", "images": [{"id": "img2"}]},
        {"id": "SC03", "images": [{"id": "img3"}]},
        {"id": "SC04", "images": [{"id": "img4"}]},
        {"id": "SC_END", "is_endcard": True, "images": [{"id": "endcard", "is_endcard": True}]},
    ]
    hero_implicit = select_hybrid_hero_scenes(scenes_implicit)
    hero_ids = [s["id"] for s in hero_implicit]
    # Non-endcard scenes: SC01, SC02, SC03, SC04 (len 4)
    # Indices: 0 (SC01), 4//2=2 (SC03), max(1, 4-2)=2 (SC03) -> SC01, SC03
    assert "SC01" in hero_ids
    assert "SC_END" not in hero_ids


def test_collect_full_chain_keyframes(tmp_path: Path) -> None:
    # Prepare dummy files
    img_dir = tmp_path / "revisions/images/1"
    img_dir.mkdir(parents=True)
    (img_dir / "IMG01_9x16.jpg").write_bytes(b"dummy1")
    (img_dir / "IMG02_9x16.jpg").write_bytes(b"dummy2")

    scenes = [
        {
            "id": "SC01",
            "duration": 4.5,
            "images": [
                {"id": "IMG01", "description": "Stickman reading a book"},
                {"id": "IMG02", "description": "Stickman looking surprised"},
            ],
        },
        {
            "id": "SC_END",
            "is_endcard": True,
            "images": [
                {"id": "ENDCARD", "is_endcard": True, "spec": "endcard"},
            ],
        },
    ]

    kfs = collect_full_chain_keyframes(
        scenes=scenes,
        job_dir=tmp_path,
        aspect_tag="9x16",
        ch_profile=None,
        visual_style_id="handdrawn_2d_explainer",
    )

    # Must contain 2 non-endcard keyframes and strictly exclude endcard
    assert len(kfs) == 2
    assert kfs[0].id == "IMG01"
    assert kfs[1].id == "IMG02"
    assert "no talking" in kfs[0].motion_prompt
    assert "no talking" in kfs[1].motion_prompt


def test_collect_hybrid_scene_pairs(tmp_path: Path) -> None:
    img_dir = tmp_path / "revisions/images/1"
    img_dir.mkdir(parents=True)
    (img_dir / "HERO1_16x9.jpg").write_bytes(b"dummy1")
    (img_dir / "HERO2_16x9.jpg").write_bytes(b"dummy2")

    hero_scene = {
        "id": "SC_HERO",
        "duration": 5.0,
        "images": [
            {"id": "HERO1", "description": "Hero starts walking", "duration": 2.5},
            {"id": "HERO2", "description": "Hero reaches destination", "duration": 2.5},
        ],
    }
    scenes = [hero_scene]

    pairs = collect_hybrid_scene_pairs(
        scenes=scenes,
        hero_scenes=[hero_scene],
        job_dir=tmp_path,
        aspect_tag="16x9",
        ch_profile=None,
        visual_style_id="handdrawn_2d_explainer",
    )

    assert len(pairs) == 1
    assert "pair_SC_HERO_HERO1_to_HERO2" in pairs[0].id
    assert pairs[0].target_duration == 2.5


def test_register_clips_to_timeline(tmp_path: Path) -> None:
    clip0 = tmp_path / "clip0.mp4"
    clip1 = tmp_path / "clip1.mp4"
    clip0.write_bytes(b"dummy_mp4_0")
    clip1.write_bytes(b"dummy_mp4_1")

    tasks = [
        {
            "clip_id": "clip_000",
            "index": 0,
            "status": "completed",
            "output_mp4_path": str(clip0),
            "trim_first_frame": False,
            "duration_seconds": 3.0,
        },
        {
            "clip_id": "clip_001",
            "index": 1,
            "status": "completed",
            "output_mp4_path": str(clip1),
            "trim_first_frame": True,
            "duration_seconds": 3.0,
        },
    ]

    images_payload = {
        "items": [
            {"image_id": "IMG01", "path": "/path/IMG01.jpg", "aspect_ratio": "9:16"},
            {"image_id": "IMG02", "path": "/path/IMG02.jpg", "aspect_ratio": "9:16"},
            {"image_id": "ENDCARD", "path": "/path/ENDCARD.jpg", "aspect_ratio": "9:16", "is_endcard": True},
        ]
    }

    content = {
        "scenes": [
            {
                "id": "SC01",
                "duration": 6.0,
                "images": [
                    {"id": "IMG01", "path": "/path/IMG01.jpg"},
                    {"id": "IMG02", "path": "/path/IMG02.jpg"},
                    {"id": "ENDCARD", "path": "/path/ENDCARD.jpg", "is_endcard": True},
                ],
                "beats": [
                    {"id": "B01", "image_id": "IMG01", "duration": 3.0},
                    {"id": "B02", "image_id": "IMG02", "duration": 3.0},
                    {"id": "B_END", "image_id": "ENDCARD", "duration": 3.0, "is_endcard": True},
                ],
            }
        ]
    }

    kfs = [
        KeyframeSpec(id="IMG01", image_path="/path/IMG01.jpg"),
        KeyframeSpec(id="IMG02", image_path="/path/IMG02.jpg"),
    ]

    with patch("sys.tools.produce_unified_flow_remotion_e2e.probe_video_clip") as mock_probe:
        mock_probe.return_value = {"duration": 3.0}
        count = register_clips_to_timeline(
            tasks=tasks,
            images_payload=images_payload,
            content=content,
            mode=ChainMode.DAISY_CHAIN,
            keyframes=kfs,
            scene_pairs=[],
            aspect_ratio="9:16",
        )

    assert count == 2
    # Verify images_payload items updated to MP4
    by_id = {it["image_id"]: it for it in images_payload["items"]}
    assert by_id["IMG01"]["path"] == str(clip0.resolve())
    assert by_id["IMG02"]["path"] == str(clip1.resolve())
    assert by_id["ENDCARD"]["path"] == "/path/ENDCARD.jpg"  # Endcard unchanged

    # Verify content beats
    beats = {b["image_id"]: b for b in content["scenes"][0]["beats"]}
    assert beats["IMG01"]["trim_before"] == 0
    assert beats["IMG01"]["clip_duration"] == 3.0
    assert 0.28 <= beats["IMG01"]["playback_rate"] <= 1.45
    assert beats["IMG02"]["trim_before"] == 1
    assert beats["IMG02"]["clip_duration"] == 3.0
    assert 0.28 <= beats["IMG02"]["playback_rate"] <= 1.45
    assert "trim_before" not in beats["ENDCARD"]  # Endcard beat untouched


def test_unified_e2e_registers_orchestrator_clips_dict(tmp_path: Path) -> None:
    """Verify FlowVideoChainOrchestrator.run() {'clips': [...]} payload registers >0 MP4 clips cleanly."""
    job_dir = tmp_path / "sys/runs/test-clips-9x16"
    img_dir = job_dir / "revisions/images/1"
    img_dir.mkdir(parents=True)
    (img_dir / "SC01_I1_9x16.jpg").write_bytes(b"jpg1")
    (img_dir / "SC01_I2_9x16.jpg").write_bytes(b"jpg2")

    clip0 = job_dir / "revisions/flow_video/1/clips/clip_000.mp4"
    clip0.parent.mkdir(parents=True)
    clip0.write_bytes(b"mp4_0")

    brief = {"channel": "ai_binh_dan", "title": "Test Clips"}
    content = {
        "schema_version": "3.0",
        "scenes": [
            {
                "id": "SC01",
                "duration": 5.2,
                "images": [
                    {"id": "SC01_I1", "description": "Start frame"},
                    {"id": "SC01_I2", "description": "End frame"},
                ],
                "beats": [
                    {"id": "B01", "image_id": "SC01_I1"},
                    {"id": "B02", "image_id": "SC01_I2"},
                ],
            }
        ],
    }
    (job_dir / "brief.json").write_text(json.dumps(brief), encoding="utf-8")
    (job_dir / "content.json").write_text(json.dumps(content), encoding="utf-8")

    q_file = tmp_path / "sys/channels/video_review_queue.json"
    q_file.parent.mkdir(parents=True, exist_ok=True)
    final_mp4 = tmp_path / "video/test-clips-9x16/test-clips-9x16.mp4"
    final_mp4.parent.mkdir(parents=True, exist_ok=True)
    final_mp4.write_bytes(b"rendered mp4")

    fake_images_output = {
        "items": [
            {"image_id": "SC01_I1", "path": "revisions/images/1/SC01_I1_9x16.jpg", "ratio": "9:16"},
            {"image_id": "SC01_I2", "path": "revisions/images/1/SC01_I2_9x16.jpg", "ratio": "9:16"},
        ]
    }
    fake_audio_payload = {
        "duration": 5.2,
        "scenes": [{"id": "SC01", "start": 0.0, "end": 5.2, "duration": 5.2}],
        "tracks": {"vi": {"duration": 5.2}},
    }
    captured_stage_c: dict = {}

    def fake_stage_c(**kwargs):
        captured_stage_c.update(kwargs)
        return (final_mp4, None, "account-01", {"duration": 5.2, "width": 1080, "height": 1920})

    fake_orch_report = {
        "nb_clips": 1,
        "clips": [
            {
                "clip_id": "clip_000_SC01_I1_to_SC01_I2",
                "index": 0,
                "duration_sec": 4.032,
                "output_mp4_path": str(clip0),
                "status": "completed",
            }
        ],
    }

    with (
        patch("sys.tools.produce_unified_flow_remotion_e2e.JobExecutionLock.try_acquire", return_value=True),
        patch("sys.tools.produce_unified_flow_remotion_e2e.JobExecutionLock.release", return_value=None),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_a_images", return_value=fake_images_output),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_b_audio", return_value=(fake_audio_payload, None, "account-01")),
        patch("sys.tools.produce_unified_flow_remotion_e2e.FlowVideoChainOrchestrator.run", return_value=fake_orch_report),
        patch("sys.tools.produce_unified_flow_remotion_e2e.probe_video_clip", return_value={"duration": 4.032}),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_c_render", side_effect=fake_stage_c),
        patch("sys.tools.produce_unified_flow_remotion_e2e.build_publish_kit", return_value=None),
        patch("sys.tools.review_queue_manager.DEFAULT_QUEUE_PATH", q_file),
    ):
        res = produce_unified_flow_remotion_e2e(
            channel_arg="ai_binh_dan",
            job_id_arg=str(job_dir),
            format_profile="short_9x16",
            motion_mode="full_chain",
            dry_run=True,
        )

    assert res["clips_generated"] == 1
    items_by_id = {it["image_id"]: it for it in captured_stage_c["images_payload"]["items"]}
    assert items_by_id["SC01_I1"]["path"] == str(clip0.resolve())
    b01 = captured_stage_c["content"]["scenes"][0]["beats"][0]
    assert b01["clip_duration"] == 4.032
    assert b01["trim_before"] == 0
    # On-disk content.json stays clean Schema 3.0 without .mp4 paths
    disk_content = json.loads((job_dir / "content.json").read_text(encoding="utf-8"))
    assert "src" not in disk_content["scenes"][0]["beats"][0]


def test_unified_e2e_dry_run_pipeline(tmp_path: Path) -> None:
    """Verify produce_unified_flow_remotion_e2e end-to-end dry run."""
    job_dir = tmp_path / "sys/runs/test-channel-week1-9x16"
    job_dir.mkdir(parents=True)

    brief = {
        "channel": "nao_luoi",
        "title": "Test Title for Review Queue",
        "packaging": {"youtube_title": "Test Title for Review Queue"},
    }
    (job_dir / "brief.json").write_text(json.dumps(brief), encoding="utf-8")

    content = {
        "scenes": [
            {
                "id": "SC01",
                "duration": 4.0,
                "images": [{"id": "IMG01", "description": "Stickman"}],
                "beats": [{"id": "B01", "image_id": "IMG01", "duration": 4.0}],
            }
        ]
    }
    (job_dir / "content.json").write_text(json.dumps(content), encoding="utf-8")

    q_file = tmp_path / "sys/channels/video_review_queue.json"
    q_file.parent.mkdir(parents=True, exist_ok=True)

    fake_images_output = {
        "items": [{"image_id": "IMG01", "path": str(job_dir / "img1.jpg")}]
    }
    fake_audio_payload = {
        "duration": 4.0,
        "tracks": {"vi": {"duration": 4.0}},
    }
    fake_render_report = {
        "duration": 4.0,
        "width": 1080,
        "height": 1920,
    }

    final_mp4 = tmp_path / "video/test-channel-week1-9x16/test-channel-week1-9x16.mp4"
    final_mp4.parent.mkdir(parents=True, exist_ok=True)
    final_mp4.write_bytes(b"mock mp4")

    with (
        patch("sys.tools.produce_unified_flow_remotion_e2e.JobExecutionLock.try_acquire", return_value=True),
        patch("sys.tools.produce_unified_flow_remotion_e2e.JobExecutionLock.release", return_value=None),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_a_images", return_value=fake_images_output),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_b_audio", return_value=(fake_audio_payload, None, "account-01")),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_c_render", return_value=(final_mp4, None, "account-01", fake_render_report)),
        patch("sys.tools.produce_unified_flow_remotion_e2e.build_publish_kit", return_value=None),
        patch("sys.tools.review_queue_manager.DEFAULT_QUEUE_PATH", q_file),
    ):
        res = produce_unified_flow_remotion_e2e(
            channel_arg="nao_luoi",
            job_id_arg=str(job_dir),
            format_profile="short_9x16",
            motion_mode="images_only",
            dry_run=True,
        )

    assert res["status"] == "SUCCESS"
    assert res["channel"] == "nao_luoi"
    assert res["review_queue"]["status"] == "PENDING_REVIEW"


def test_collect_full_chain_keyframes_motion_prompt_and_audio_durations(tmp_path: Path) -> None:
    """Verify full motion_prompt priority, physical transition fallback, and audio beat durations."""
    img_dir = tmp_path / "revisions/images/1"
    img_dir.mkdir(parents=True)
    (img_dir / "IMG01_9x16.jpg").write_bytes(b"dummy1")
    (img_dir / "IMG02_9x16.jpg").write_bytes(b"dummy2")

    explicit_prompt = (
        "Smooth 2D hand-drawn doodle explainer animation. Stickman raises hand enthusiastically pointing "
        "at a floating glowing math formula, clean lines, highly dynamic animation"
    )
    scenes = [
        {
            "id": "SC01",
            "duration": 5.0,
            "images": [
                {"id": "IMG01", "description": "Stickman stands", "motion_prompt": explicit_prompt},
                {"id": "IMG02", "description": "Formula transforms into lightbulb"},
            ],
            "beats": [
                {"id": "B01", "image_id": "IMG01", "duration": 2.2},
                {"id": "B02", "image_id": "IMG02", "duration": 2.8},
            ],
        }
    ]

    audio_payload = {
        "duration": 5.0,
        "scenes": [{"id": "SC01", "duration": 5.0}],
    }

    kfs = collect_full_chain_keyframes(
        scenes=scenes,
        job_dir=tmp_path,
        aspect_tag="9x16",
        ch_profile=None,
        visual_style_id="handdrawn_2d_explainer",
        audio_payload=audio_payload,
    )

    assert len(kfs) == 2
    # 1. Explicit motion_prompt is kept in full without truncation at 180 chars
    assert "raises hand enthusiastically pointing" in kfs[0].motion_prompt
    assert "clean lines, highly dynamic animation" in kfs[0].motion_prompt
    assert "no talking" in kfs[0].motion_prompt
    assert kfs[0].target_duration == round(2.2 + 0.35, 2)

    # 2. Fallback motion_prompt synthesizes transition into IMG02
    assert "Seamless continuous 2D character animation evolving smoothly" in kfs[1].motion_prompt
    assert "Formula transforms into lightbulb" in kfs[1].motion_prompt
    assert "no talking" in kfs[1].motion_prompt
    assert kfs[1].target_duration == round(2.8 + 0.35, 2)


def test_motion_mode_defaults_to_full_chain_for_both_formats(tmp_path: Path) -> None:
    """Verify both short_9x16 and long_16x9 default to full_chain motion mode."""
    for fmt, tag in [("short_9x16", "9x16"), ("long_16x9", "16x9")]:
        job_dir = tmp_path / f"job-{tag}"
        job_dir.mkdir(parents=True)
        (job_dir / "brief.json").write_text(json.dumps({"channel": "ai_binh_dan"}), encoding="utf-8")
        (job_dir / "content.json").write_text(json.dumps({
            "scenes": [{"id": "SC01", "duration": 3.0, "images": [{"id": "I1"}], "beats": [{"id": "b1", "image_id": "I1", "duration": 3.0}]}]
        }), encoding="utf-8")
        (job_dir / f"I1_{tag}.jpg").write_bytes(b"dummy")

        with (
            patch("sys.tools.produce_unified_flow_remotion_e2e.JobExecutionLock.try_acquire", return_value=True),
            patch("sys.tools.produce_unified_flow_remotion_e2e.JobExecutionLock.release", return_value=None),
            patch("sys.tools.produce_unified_flow_remotion_e2e.stage_a_images", return_value={"items": [{"image_id": "I1", "path": "p"}]}),
            patch("sys.tools.produce_unified_flow_remotion_e2e.stage_b_audio", return_value=({"duration": 3.0}, None, "account-01")),
            patch("sys.tools.produce_unified_flow_remotion_e2e.retime_long_beats_to_measured_audio", return_value=({"scenes": []}, {"beats": 1, "avg_hold": 3.0})),
            patch("sys.tools.produce_unified_flow_remotion_e2e.stage_c_render", return_value=(Path("video.mp4"), None, "account-01", {"duration": 3.0})),
            patch("sys.tools.produce_unified_flow_remotion_e2e.build_publish_kit", return_value=None),
            patch("sys.tools.produce_unified_flow_remotion_e2e.register_video_for_review", return_value={"status": "PENDING"}),
        ):
            res = produce_unified_flow_remotion_e2e(
                channel_arg="ai_binh_dan",
                job_id_arg=str(job_dir),
                format_profile=fmt,
                motion_mode=None,  # default
                dry_run=True,
            )
            assert res["motion_mode"] == "full_chain"


def test_resolve_motion_mode_credit_aware(tmp_path: Path) -> None:
    """Verify resolve_motion_mode logic for full_chain priority and images_only fallback."""
    ledger_path = tmp_path / "test_credits.json"
    ledger = CreditLedger(path=ledger_path)

    # 1. Profile with remaining credits (> 0) -> resolves to full_chain
    ledger.set_credits("p1", 100, status="active")
    with patch("sys.tools.produce_unified_flow_remotion_e2e.get_all_configured_profiles", return_value=[{"name": "p1"}]):
        assert resolve_motion_mode(motion_mode="auto", ledger=ledger) == "full_chain"
        assert resolve_motion_mode(motion_mode="full_chain", ledger=ledger) == "full_chain"
        assert resolve_motion_mode(motion_mode=None, ledger=ledger) == "full_chain"
        assert resolve_motion_mode(motion_mode="hybrid", ledger=ledger) == "hybrid"
        assert resolve_motion_mode(motion_mode="images_only", ledger=ledger) == "images_only"

    # 2. 100% of profiles in pool exhausted (0 credits) -> automatically falls back to images_only
    ledger.mark_exhausted("p1", reason="quota_exceeded")
    with patch("sys.tools.produce_unified_flow_remotion_e2e.get_all_configured_profiles", return_value=[{"name": "p1"}]):
        assert resolve_motion_mode(motion_mode="auto", ledger=ledger) == "images_only"
        assert resolve_motion_mode(motion_mode="full_chain", ledger=ledger) == "images_only"
        assert resolve_motion_mode(motion_mode=None, ledger=ledger) == "images_only"
        assert resolve_motion_mode(motion_mode="hybrid", ledger=ledger) == "images_only"
        assert resolve_motion_mode(motion_mode="images_only", ledger=ledger) == "images_only"


def test_unified_e2e_full_chain_when_credits_available(tmp_path: Path) -> None:
    """Verify that when credits are available (> 0), full_chain 100% video clip mode is executed."""
    ledger_path = tmp_path / "active_credits.json"
    ledger = CreditLedger(path=ledger_path)
    ledger.set_credits("profile_01", 500, status="active")

    job_dir = tmp_path / "test_job_full_chain"
    job_dir.mkdir(parents=True)
    img_dir = job_dir / "revisions/images/1"
    img_dir.mkdir(parents=True)
    (img_dir / "I1_9x16.jpg").write_bytes(b"dummy1")
    (img_dir / "I2_9x16.jpg").write_bytes(b"dummy2")

    (job_dir / "brief.json").write_text(json.dumps({"channel": "nao_luoi"}), encoding="utf-8")
    (job_dir / "content.json").write_text(
        json.dumps({
            "scenes": [
                {
                    "id": "SC01",
                    "duration": 4.0,
                    "images": [
                        {"id": "I1", "description": "Scene 1 stickman"},
                        {"id": "I2", "description": "Scene 2 stickman"},
                    ],
                    "beats": [
                        {"id": "b1", "image_id": "I1", "duration": 2.0},
                        {"id": "b2", "image_id": "I2", "duration": 2.0},
                    ],
                }
            ]
        }),
        encoding="utf-8",
    )

    fake_video = tmp_path / "clip_0.mp4"
    fake_video.write_bytes(b"mp4data")
    fake_render_mp4 = tmp_path / "final.mp4"
    fake_render_mp4.write_bytes(b"finalmp4")

    mock_report = {
        "clips": [
            {
                "task_id": "clip_0",
                "output_mp4_path": str(fake_video),
                "duration_sec": 2.35,
                "status": "completed",
            }
        ]
    }

    with (
        patch("sys.tools.produce_unified_flow_remotion_e2e.get_all_configured_profiles", return_value=[{"name": "profile_01"}]),
        patch("sys.tools.produce_unified_flow_remotion_e2e.JobExecutionLock.try_acquire", return_value=True),
        patch("sys.tools.produce_unified_flow_remotion_e2e.JobExecutionLock.release", return_value=None),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_a_images", return_value={"items": [{"image_id": "I1", "path": str(img_dir / "I1_9x16.jpg")}, {"image_id": "I2", "path": str(img_dir / "I2_9x16.jpg")}]}),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_b_audio", return_value=({"duration": 4.0, "scenes": [{"id": "SC01", "duration": 4.0}]}, None, "account-01")),
        patch("sys.tools.produce_unified_flow_remotion_e2e.FlowVideoChainOrchestrator.run", return_value=mock_report),
        patch("sys.tools.produce_unified_flow_remotion_e2e.probe_video_clip", return_value={"duration": 2.35, "width": 1080, "height": 1920}),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_c_render", return_value=(fake_render_mp4, None, "account-01", {"duration": 4.0})),
        patch("sys.tools.produce_unified_flow_remotion_e2e.build_publish_kit", return_value=None),
        patch("sys.tools.produce_unified_flow_remotion_e2e.register_video_for_review", return_value={"status": "PENDING"}),
    ):
        res = produce_unified_flow_remotion_e2e(
            channel_arg="nao_luoi",
            job_id_arg=str(job_dir),
            format_profile="short_9x16",
            motion_mode="auto",
            dry_run=True,
            credit_ledger=ledger,
        )

    assert res["status"] == "SUCCESS"
    assert res["motion_mode"] == "full_chain"
    assert res["clips_generated"] == 1


def test_unified_e2e_fallback_to_dense_images_when_pool_exhausted(tmp_path: Path) -> None:
    """Verify automatic fallback to dense multi-image (images_only) mode when 100% of Flow profiles are exhausted."""
    ledger_path = tmp_path / "exhausted_credits.json"
    ledger = CreditLedger(path=ledger_path)
    ledger.mark_exhausted("profile_01", reason="quota_exceeded")
    ledger.mark_exhausted("profile_02", reason="quota_exceeded")

    job_dir = tmp_path / "test_job_exhausted"
    job_dir.mkdir(parents=True)
    img_dir = job_dir / "revisions/images/1"
    img_dir.mkdir(parents=True)
    (img_dir / "I1_9x16.jpg").write_bytes(b"dummy1")
    (img_dir / "I2_9x16.jpg").write_bytes(b"dummy2")

    (job_dir / "brief.json").write_text(json.dumps({"channel": "nao_luoi"}), encoding="utf-8")
    (job_dir / "content.json").write_text(
        json.dumps({
            "scenes": [
                {
                    "id": "SC01",
                    "duration": 4.0,
                    "images": [
                        {"id": "I1", "description": "Scene 1 stickman"},
                        {"id": "I2", "description": "Scene 2 stickman"},
                    ],
                    "beats": [
                        {"id": "b1", "image_id": "I1", "duration": 2.0},
                        {"id": "b2", "image_id": "I2", "duration": 2.0},
                    ],
                }
            ]
        }),
        encoding="utf-8",
    )

    fake_render_mp4 = tmp_path / "final_images_only.mp4"
    fake_render_mp4.write_bytes(b"finalmp4")

    mock_stage_c = MagicMock(return_value=(fake_render_mp4, None, "account-01", {"duration": 4.0}))

    with (
        patch("sys.tools.produce_unified_flow_remotion_e2e.get_all_configured_profiles", return_value=[{"name": "profile_01"}, {"name": "profile_02"}]),
        patch("sys.tools.produce_unified_flow_remotion_e2e.JobExecutionLock.try_acquire", return_value=True),
        patch("sys.tools.produce_unified_flow_remotion_e2e.JobExecutionLock.release", return_value=None),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_a_images", return_value={"items": [{"image_id": "I1", "path": str(img_dir / "I1_9x16.jpg")}, {"image_id": "I2", "path": str(img_dir / "I2_9x16.jpg")}]}),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_b_audio", return_value=({"duration": 4.0, "scenes": [{"id": "SC01", "duration": 4.0}]}, None, "account-01")),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_c_render", mock_stage_c),
        patch("sys.tools.produce_unified_flow_remotion_e2e.build_publish_kit", return_value=None),
        patch("sys.tools.produce_unified_flow_remotion_e2e.register_video_for_review", return_value={"status": "PENDING"}),
    ):
        res = produce_unified_flow_remotion_e2e(
            channel_arg="nao_luoi",
            job_id_arg=str(job_dir),
            format_profile="short_9x16",
            motion_mode="auto",  # Defaults/resolves to images_only because pool has 0 credits
            dry_run=True,
            credit_ledger=ledger,
        )

    assert res["status"] == "SUCCESS"
    assert res["motion_mode"] == "images_only"
    assert res["clips_generated"] == 0
    # Stage C render was called with dense keyframe image content
    assert mock_stage_c.called
    render_content_arg = mock_stage_c.call_args.kwargs["content"]
    assert len(render_content_arg["scenes"][0]["images"]) == 2


def test_unified_e2e_fallback_when_orchestrator_exhausts_mid_chain(tmp_path: Path) -> None:
    """Verify fallback to dense images when FlowVideoChainOrchestrator raises credit exhaustion mid-chain."""
    ledger_path = tmp_path / "midchain_credits.json"
    ledger = CreditLedger(path=ledger_path)
    ledger.set_credits("profile_01", 100, status="active")

    job_dir = tmp_path / "test_job_midchain"
    job_dir.mkdir(parents=True)
    img_dir = job_dir / "revisions/images/1"
    img_dir.mkdir(parents=True)
    (img_dir / "I1_9x16.jpg").write_bytes(b"dummy1")
    (img_dir / "I2_9x16.jpg").write_bytes(b"dummy2")

    (job_dir / "brief.json").write_text(json.dumps({"channel": "nao_luoi"}), encoding="utf-8")
    (job_dir / "content.json").write_text(
        json.dumps({
            "scenes": [
                {
                    "id": "SC01",
                    "duration": 4.0,
                    "images": [
                        {"id": "I1", "description": "Scene 1 stickman"},
                        {"id": "I2", "description": "Scene 2 stickman"},
                    ],
                    "beats": [
                        {"id": "b1", "image_id": "I1", "duration": 2.0},
                        {"id": "b2", "image_id": "I2", "duration": 2.0},
                    ],
                }
            ]
        }),
        encoding="utf-8",
    )

    fake_render_mp4 = tmp_path / "final_midchain.mp4"
    fake_render_mp4.write_bytes(b"finalmp4")

    mock_stage_c = MagicMock(return_value=(fake_render_mp4, None, "account-01", {"duration": 4.0}))

    with (
        patch("sys.tools.produce_unified_flow_remotion_e2e.get_all_configured_profiles", return_value=[{"name": "profile_01"}]),
        patch("sys.tools.produce_unified_flow_remotion_e2e.JobExecutionLock.try_acquire", return_value=True),
        patch("sys.tools.produce_unified_flow_remotion_e2e.JobExecutionLock.release", return_value=None),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_a_images", return_value={"items": [{"image_id": "I1", "path": str(img_dir / "I1_9x16.jpg")}, {"image_id": "I2", "path": str(img_dir / "I2_9x16.jpg")}]}),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_b_audio", return_value=({"duration": 4.0, "scenes": [{"id": "SC01", "duration": 4.0}]}, None, "account-01")),
        patch("sys.tools.produce_unified_flow_remotion_e2e.FlowVideoChainOrchestrator.run", side_effect=RuntimeError("All profiles exhausted or insufficient credits (needed 7)")),
        patch("sys.tools.produce_unified_flow_remotion_e2e.stage_c_render", mock_stage_c),
        patch("sys.tools.produce_unified_flow_remotion_e2e.build_publish_kit", return_value=None),
        patch("sys.tools.produce_unified_flow_remotion_e2e.register_video_for_review", return_value={"status": "PENDING"}),
    ):
        res = produce_unified_flow_remotion_e2e(
            channel_arg="nao_luoi",
            job_id_arg=str(job_dir),
            format_profile="short_9x16",
            motion_mode="full_chain",
            dry_run=True,
            credit_ledger=ledger,
        )

    # Must complete cleanly via dense multi-image fallback without failing or crashing
    assert res["status"] == "SUCCESS"
    assert res["motion_mode"] == "images_only"
    assert res["clips_generated"] == 0
    assert mock_stage_c.called
