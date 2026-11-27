"""Unit tests covering all 16 Omni 1.2 Flash (macaron_cookie) RPC, catalog, credit, and deprecation combinations."""
from __future__ import annotations

import json
from typing import Any

import pytest
from flow_cdp import flow_rpc
from flow_video.chain_planner import select_clip_duration_and_credits

DURATIONS = (4, 6, 8, 10)
CREDIT_BY_DURATION = {4: 12, 6: 18, 8: 24, 10: 30}
ASPECT_CASES = (
    ("9:16", flow_rpc.VIDEO_ASPECT_PORTRAIT),
    ("16:9", flow_rpc.VIDEO_ASPECT_LANDSCAPE),
)
END_FRAME_CASES = (
    (False, flow_rpc.RPC_GEN_VIDEO_START_FRAME, "macaron_cookie_i2v_{dur}s"),
    (True, flow_rpc.RPC_GEN_VIDEO_START_END_FRAMES, "macaron_cookie_i2v_fl_{dur}s"),
)

ALL_16_COMBINATIONS = [
    (dur, has_end_frame, expected_rpc, template.format(dur=dur), aspect_str, aspect_int)
    for dur in DURATIONS
    for has_end_frame, expected_rpc, template in END_FRAME_CASES
    for aspect_str, aspect_int in ASPECT_CASES
]


def _make_raw_htrjv_usage(
    key: str,
    duration: int,
    capabilities: list[list[int]],
    aspects: list[int],
    credits: int,
) -> list[Any]:
    """Build a single raw HTrJv usage array matching `read_model_catalog` layout."""
    row: list[Any] = [None] * 17
    row[0] = key
    row[4] = [[1, [[None, credits]]]]
    row[7] = [[[caps] for caps in capabilities]]
    row[12] = [aspects]
    row[16] = duration
    return row


def _build_realistic_htrjv_payload() -> list[Any]:
    """Build a realistic raw `HTrJv` payload with Omni 1.2 Flash, legacy Omni 1.1, Veo Lite, and Veo Quality."""
    macaron_usages: list[Any] = []
    for dur in DURATIONS:
        credits = CREDIT_BY_DURATION[dur]
        # Put _360p decoys before HD keys to prove HD filtering prefers full-res keys.
        macaron_usages.append(
            _make_raw_htrjv_usage(
                f"macaron_cookie_i2v_{dur}s_360p",
                duration=dur,
                capabilities=[[1, 5]],
                aspects=[2, 1],
                credits=credits,
            )
        )
        macaron_usages.append(
            _make_raw_htrjv_usage(
                f"macaron_cookie_i2v_{dur}s",
                duration=dur,
                capabilities=[[1, 5]],
                aspects=[2, 1],
                credits=credits,
            )
        )
        macaron_usages.append(
            _make_raw_htrjv_usage(
                f"macaron_cookie_i2v_fl_{dur}s_360p",
                duration=dur,
                capabilities=[[1, 5, 7]],
                aspects=[2, 1],
                credits=credits,
            )
        )
        macaron_usages.append(
            _make_raw_htrjv_usage(
                f"macaron_cookie_i2v_fl_{dur}s",
                duration=dur,
                capabilities=[[1, 5, 7]],
                aspects=[2, 1],
                credits=credits,
            )
        )

    video_families = [
        [
            "Veo 3.1 - Quality",
            [
                _make_raw_htrjv_usage("veo_3_1_i2v_s_fl", 8, [[1, 5, 7]], [2, 1], 100),
                _make_raw_htrjv_usage("veo_3_1_i2v_s", 8, [[1, 5]], [2, 1], 100),
            ],
            None,
            "veo_3_1_quality",
        ],
        [
            "Veo 3.1 - Lite",
            [
                _make_raw_htrjv_usage("veo_3_1_i2v_s_lite", 8, [[1, 5]], [2, 1], 10),
                _make_raw_htrjv_usage("veo_3_1_interpolation_lite", 8, [[1, 5, 7]], [2, 1], 10),
            ],
            None,
            "veo_3_1_lite",
        ],
        [
            "Omni 1.1 Flash",
            [
                _make_raw_htrjv_usage("abra_i2v_8s", 8, [[1, 5]], [2, 1], 12),
                _make_raw_htrjv_usage("omni_flash_i2v_8s_first_last", 8, [[1, 5, 7]], [2, 1], 12),
            ],
            None,
            "abra",
        ],
        [
            "Omni 1.2 Flash",
            macaron_usages,
            None,
            "macaron_cookie",
        ],
    ]
    return [[None, None, None, None, video_families]]


def _decode_rpc_envelope(envelope: str) -> tuple[str, list[Any], list[Any]]:
    """Decode a batchexecute JSON envelope into `(rpcid, inner, first_item)`."""
    outer = json.loads(envelope)
    assert isinstance(outer, list) and len(outer) == 1
    batch = outer[0]
    assert isinstance(batch, list) and len(batch) == 1
    entry = batch[0]
    assert entry[2] is None and entry[3] == "generic"
    rpcid = entry[0]
    inner = json.loads(entry[1])
    items = inner[0]
    assert isinstance(items, list) and len(items) == 1
    return rpcid, inner, items[0]


@pytest.fixture(scope="module")
def htrjv_catalog() -> list[dict[str, Any]]:
    """Parsed `HTrJv` catalog containing realistic `macaron_cookie` usages."""
    catalog = flow_rpc.read_model_catalog(_build_realistic_htrjv_payload())
    macaron_fams = [f for f in catalog if f["id"] == "macaron_cookie"]
    assert len(macaron_fams) == 1
    assert macaron_fams[0]["display_name"] == "Omni 1.2 Flash"
    assert len(macaron_fams[0]["usages"]) == 16  # 8 HD + 8 _360p
    return catalog


def test_htrjv_catalog_parses_all_macaron_cookie_credits_and_capabilities(
    htrjv_catalog: list[dict[str, Any]],
) -> None:
    """Verify `read_model_catalog` extracts durations, aspects, capabilities, and credit costs."""
    macaron = next(f for f in htrjv_catalog if f["id"] == "macaron_cookie")
    by_key = {u["key"]: u for u in macaron["usages"]}

    for dur in DURATIONS:
        sf_key = f"macaron_cookie_i2v_{dur}s"
        fl_key = f"macaron_cookie_i2v_fl_{dur}s"
        assert sf_key in by_key
        assert fl_key in by_key

        assert by_key[sf_key]["duration"] == dur
        assert by_key[sf_key]["aspects"] == [2, 1]
        assert by_key[sf_key]["capabilities"] == [[1, 5]]
        assert by_key[sf_key]["credits"] == {1: CREDIT_BY_DURATION[dur]}

        assert by_key[fl_key]["duration"] == dur
        assert by_key[fl_key]["aspects"] == [2, 1]
        assert by_key[fl_key]["capabilities"] == [[1, 5, 7]]
        assert by_key[fl_key]["credits"] == {1: CREDIT_BY_DURATION[dur]}


@pytest.mark.parametrize("use_catalog", [False, True], ids=["catalog_none", "catalog_htrjv"])
@pytest.mark.parametrize("model_alias", ["macaron_cookie", "omni_flash", "OMNI_1_2_FLASH"])
@pytest.mark.parametrize(
    ("dur", "has_end_frame", "expected_rpc", "expected_key", "aspect_str", "expected_aspect_int"),
    ALL_16_COMBINATIONS,
    ids=[
        f"{dur}s_{'fl' if fl else 'sf'}_{asp.replace(':', 'x')}"
        for dur, fl, _, _, asp, _ in ALL_16_COMBINATIONS
    ],
)
def test_all_16_omni12_combinations_resolve_and_build_rpc(
    htrjv_catalog: list[dict[str, Any]],
    use_catalog: bool,
    model_alias: str,
    dur: int,
    has_end_frame: bool,
    expected_rpc: str,
    expected_key: str,
    aspect_str: str,
    expected_aspect_int: int,
) -> None:
    """Verify all 16 combinations across `resolve_video_model` and `eb1hJf`/`nprQif` RPC envelopes."""
    catalog = htrjv_catalog if use_catalog else None

    assert expected_aspect_int == (1 if aspect_str == "9:16" else 2)
    assert flow_rpc.resolve_video_aspect(aspect_str) == expected_aspect_int

    resolved = flow_rpc.resolve_video_model(
        model_alias,
        aspect=aspect_str,
        has_start_frame=True,
        has_end_frame=has_end_frame,
        catalog=catalog,
        duration_seconds=dur,
    )
    assert resolved == expected_key

    last_frame_id = "media_end_002" if has_end_frame else None
    rpcid, envelope = flow_rpc.video_frames_request(
        prompt="Stickman walks cleanly across white canvas",
        project_id="proj-omni12",
        first_frame_media_id="media_start_001",
        last_frame_media_id=last_frame_id,
        aspect=aspect_str,
        model=model_alias,
        catalog=catalog,
        duration_seconds=dur,
    )
    assert rpcid == expected_rpc

    decoded_rpc, inner, item = _decode_rpc_envelope(envelope)
    assert decoded_rpc == expected_rpc
    assert item[1] == expected_key
    assert item[2] == expected_aspect_int
    assert item[3] is None
    assert "media_start_001" in json.dumps(item[4])

    if has_end_frame:
        assert expected_rpc == "nprQif"
        assert len(item) == 7
        assert "media_end_002" in json.dumps(item[5])

        direct_env = flow_rpc.video_start_end_frames_request(
            prompt="Stickman walks cleanly across white canvas",
            project_id="proj-omni12",
            first_frame_media_id="media_start_001",
            last_frame_media_id="media_end_002",
            aspect=aspect_str,
            model=model_alias,
            catalog=catalog,
            duration_seconds=dur,
        )
        direct_rpc, _, direct_item = _decode_rpc_envelope(direct_env)
        assert direct_rpc == "nprQif"
        assert direct_item[1] == expected_key
        assert direct_item[2] == expected_aspect_int
    else:
        assert expected_rpc == "eb1hJf"
        assert len(item) == 6

        direct_env = flow_rpc.video_start_frame_request(
            prompt="Stickman walks cleanly across white canvas",
            project_id="proj-omni12",
            first_frame_media_id="media_start_001",
            aspect=aspect_str,
            model=model_alias,
            catalog=catalog,
            duration_seconds=dur,
        )
        direct_rpc, _, direct_item = _decode_rpc_envelope(direct_env)
        assert direct_rpc == "eb1hJf"
        assert direct_item[1] == expected_key
        assert direct_item[2] == expected_aspect_int

    # Outer context carries project_id
    assert "proj-omni12" in json.dumps(inner[1])


@pytest.mark.parametrize("has_end_frame", [False, True], ids=["start_frame", "start_end_frames"])
@pytest.mark.parametrize(
    ("dur", "expected_credits"),
    [(4, 12), (6, 18), (8, 24), (10, 30)],
)
def test_omni12_credit_mapping_fixed_and_auto_durations(
    has_end_frame: bool,
    dur: int,
    expected_credits: int,
) -> None:
    """Verify 4s->12c, 6s->18c, 8s->24c, 10s->30c across fixed and auto duration modes."""
    resolved_key = (
        f"macaron_cookie_i2v_fl_{dur}s" if has_end_frame else f"macaron_cookie_i2v_{dur}s"
    )
    for model_name in ("macaron_cookie", "omni_flash", "omni_1_2_flash", resolved_key):
        selected_dur, credits = select_clip_duration_and_credits(
            target_sec=float(dur),
            video_model=model_name,
            has_end_frame=has_end_frame,
            default_duration_sec=dur,
            auto_duration=False,
        )
        assert selected_dur == dur
        assert credits == expected_credits

    # Auto duration boundary probes: <=4.8 -> 4s, <=6.8 -> 6s, <=8.8 -> 8s, >8.8 -> 10s
    target_probes = {
        4: (3.5, 4.8),
        6: (4.9, 6.8),
        8: (6.9, 8.8),
        10: (8.9, 10.5),
    }
    for probe in target_probes[dur]:
        auto_dur, auto_credits = select_clip_duration_and_credits(
            target_sec=probe,
            video_model="macaron_cookie",
            has_end_frame=has_end_frame,
            auto_duration=True,
        )
        assert auto_dur == dur
        assert auto_credits == expected_credits


@pytest.mark.parametrize(
    "model_key",
    [
        "macaron_cookie",
        "omni_flash",
        "OMNI_1_2_FLASH",
        *(f"macaron_cookie_i2v_{d}s" for d in DURATIONS),
        *(f"macaron_cookie_i2v_fl_{d}s" for d in DURATIONS),
    ],
)
def test_omni12_models_have_zero_deprecation_warnings(model_key: str) -> None:
    """Verify all Omni 1.2 Flash keys and aliases return `(False, '')` from deprecation check."""
    assert flow_rpc.is_video_model_deprecated(model_key) == (False, "")


def test_legacy_omni11_keys_remain_flagged_deprecated() -> None:
    """Sanity check that legacy 1.1 keys warn while Omni 1.2 replacements do not."""
    for legacy_key in ("omni_flash_i2v_8s_first_last", "abra_i2v_8s"):
        deprecated, notice = flow_rpc.is_video_model_deprecated(legacy_key)
        assert deprecated is True
        assert "2026-12-05" in notice
        assert "macaron_cookie" in notice
