"""Unit & Integration Tests for 10x10 Cinema Film-Stock Optical Grading & Lens FX Engine."""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pytest
from fx_warehouse.optical_luts_10x10 import (
    ALL_20_STYLE_IDS,
    CANONICAL_STYLE_NAMES,
    CINEMA_GRADE_IDS,
    LONG_STYLE_IDS,
    OPTICAL_GRADE_CATALOG,
    SHORT_STYLE_IDS,
    STYLE_TO_GRADE_MAP,
    apply_optical_grade_numpy,
    apply_optical_grade_pil,
    build_3d_lut_cube,
    export_3d_lut_cube_file,
    get_ffmpeg_grade_filter,
    get_optical_grade_profile,
    list_optical_grades,
    render_optical_luts_showcase,
    resolve_optical_grade_id,
    validate_ffmpeg_grade_filter,
)
from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_UNG_CHAU_FRAME = (
    REPO_ROOT / "video" / "vn_su_ke_lai_v6_prestige_ung_chau_1075_short" / "frames" / "beat_01.png"
)


def _make_synthetic_torch_battle_frame(width: int = 384, height: int = 512) -> Image.Image:
    """Create deterministic synthetic test frame with deep shadows, midtones, crimson silk, and bright torch."""
    yy = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None]
    xx = np.linspace(0.0, 1.0, width, dtype=np.float32)[None, :]
    base_y = 0.08 + 0.56 * (1.0 - 0.65 * yy) + 0.12 * np.sin(xx * 18.0) * np.cos(yy * 14.0)
    r = np.clip(base_y * 1.04, 0.0, 1.0)
    g = np.clip(base_y * 0.98, 0.0, 1.0)
    b = np.clip(base_y * 0.94, 0.0, 1.0)

    # Crimson war-banner swatch on upper-left
    banner = (xx > 0.10) & (xx < 0.28) & (yy > 0.10) & (yy < 0.42)
    r = np.where(banner, 0.78, r)
    g = np.where(banner, 0.12, g)
    b = np.where(banner, 0.14, b)

    # Cobalt-steel armor swatch on upper-right
    cobalt = (xx > 0.72) & (xx < 0.90) & (yy > 0.12) & (yy < 0.42)
    r = np.where(cobalt, 0.15, r)
    g = np.where(cobalt, 0.26, g)
    b = np.where(cobalt, 0.58, b)

    # Bright specular torch flame in center to trigger 35mm emulsion halation
    dist2 = ((xx - 0.50) / 0.045) ** 2 + ((yy - 0.48) / 0.045) ** 2
    torch_core = np.exp(-dist2 * 1.8)
    r = np.clip(r + 0.95 * torch_core, 0.0, 1.0)
    g = np.clip(g + 0.90 * torch_core, 0.0, 1.0)
    b = np.clip(b + 0.78 * torch_core, 0.0, 1.0)

    # Dark shadow region near bottom to verify zero fog / zero black-mud grain
    dark_zone = yy > 0.86
    r = np.where(dark_zone, 0.03, r)
    g = np.where(dark_zone, 0.03, g)
    b = np.where(dark_zone, 0.035, b)

    arr = np.stack([r, g, b], axis=-1)
    im = Image.fromarray(np.clip(arr * 255.0 + 0.5, 0.0, 255.0).astype(np.uint8), mode="RGB")
    draw = ImageDraw.Draw(im)
    # Fine metallic grid lines to test macro metallurgy micro-contrast
    for gx in range(120, 260, 14):
        draw.line([(gx, 300), (gx, 410)], fill=(185, 168, 128), width=2)
    return im


def test_exact_10_grades_and_20_style_mappings() -> None:
    expected_map = {
        "S01": "kodak_500t_torch_battle",
        "L01": "kodak_500t_torch_battle",
        "S02": "pov_adrenaline_grit",
        "S03": "imperial_cartography_gold",
        "L03": "imperial_cartography_gold",
        "L09": "imperial_cartography_gold",
        "S04": "noir_silver_dossier",
        "L02": "noir_silver_dossier",
        "S05": "chronicle_split_contrast",
        "L06": "chronicle_split_contrast",
        "S06": "macro_metallurgy_crisp",
        "L10": "macro_metallurgy_crisp",
        "S07": "duel_bipolar_crimson_cobalt",
        "L07": "duel_bipolar_crimson_cobalt",
        "S08": "humanist_35mm_natural",
        "L08": "humanist_35mm_natural",
        "S09": "chrono_tension_teal_amber",
        "L05": "chrono_tension_teal_amber",
        "S10": "eastern_lacquer_ink_to_cinema",
        "L04": "eastern_lacquer_ink_to_cinema",
    }
    assert len(CINEMA_GRADE_IDS) == 10
    assert len(SHORT_STYLE_IDS) == 10
    assert len(LONG_STYLE_IDS) == 10
    assert len(ALL_20_STYLE_IDS) == 20
    assert STYLE_TO_GRADE_MAP == expected_map

    # Every Short/Long style resolves via short code, lowercase, canonical slug, and grade_id
    covered_from_catalog: list[str] = []
    for gid in CINEMA_GRADE_IDS:
        assert resolve_optical_grade_id(gid) == gid
        prof = OPTICAL_GRADE_CATALOG[gid]
        covered_from_catalog.extend(prof.style_ids)

    assert sorted(covered_from_catalog) == sorted(ALL_20_STYLE_IDS)
    for sid in ALL_20_STYLE_IDS:
        expected_gid = expected_map[sid]
        assert resolve_optical_grade_id(sid) == expected_gid
        assert resolve_optical_grade_id(sid.lower()) == expected_gid
        assert resolve_optical_grade_id(CANONICAL_STYLE_NAMES[sid]) == expected_gid
        assert get_optical_grade_profile(sid).grade_id == expected_gid

    catalog_meta = list_optical_grades()
    assert len(catalog_meta) == 10

    with pytest.raises(ValueError):
        resolve_optical_grade_id("   ")
    with pytest.raises(KeyError):
        resolve_optical_grade_id("S99_UNKNOWN_STYLE")


@pytest.mark.parametrize("style_id", ALL_20_STYLE_IDS)
def test_ffmpeg_lavfi_execution_all_20_styles(style_id: str) -> None:
    """Execute real local `ffmpeg -f lavfi` on all 20 styles across Acts 1, 2, and 4."""
    for act in (1, 2, 4):
        f_chain = get_ffmpeg_grade_filter(style_id, act=act)
        assert f_chain
        assert ";" not in f_chain
        assert "[" not in f_chain and "]" not in f_chain

        res = validate_ffmpeg_grade_filter(f_chain, width=256, height=144)
        assert res["valid"], f"FFmpeg failed for {style_id} act={act}: {res['stderr']}"
        assert res["mean_luma"] > 15.0
        assert res["std_luma"] > 12.0


def test_ffmpeg_multi_splice_filter_complex_colab_compatibility() -> None:
    """Verify splicing multiple grade filters inside a single `render_single_pass.py`-style `filter_complex`."""
    g_a = get_ffmpeg_grade_filter("S01", act=1)
    g_b = get_ffmpeg_grade_filter("S02", act=2)
    g_c = get_ffmpeg_grade_filter("S10", act=4)
    fc = (
        f"[0:v]split=2[spa][spb];"
        f"[spa]unsharp=3:3:0.45:3:3:0.25,{g_a},trim=end_frame=2,setpts=PTS-STARTPTS[vca];"
        f"[spb]unsharp=3:3:0.55:3:3:0.30,{g_b},trim=end_frame=2,setpts=PTS-STARTPTS[vcb];"
        f"[vca][vcb]concat=n=2:v=1:a=0,{g_c},format=yuv420p[vout]"
    )
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "lavfi",
        "-i",
        "testsrc2=s=256x256:r=30:d=0.2",
        "-filter_complex",
        fc,
        "-map",
        "[vout]",
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    assert proc.returncode == 0, proc.stderr


def test_pil_grade_distinctness_halation_and_zero_fog() -> None:
    src = _make_synthetic_torch_battle_frame()
    src_np = np.asarray(src, dtype=np.float32)

    graded_by_id: dict[str, np.ndarray] = {}
    for gid in CINEMA_GRADE_IDS:
        out_im = apply_optical_grade_pil(src, gid, act=2)
        assert out_im.size == src.size
        assert out_im.mode == "RGB"
        arr = np.asarray(out_im, dtype=np.float32)
        graded_by_id[gid] = arr

        # Dynamic range gate: no washed-out fog/mud (`p95 - p5 >= 85` on 0..255 luma)
        luma = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
        dr = float(np.percentile(luma, 95) - np.percentile(luma, 5))
        assert dr >= 110.0, f"{gid} dynamic range too low (washed-out fog): {dr:.2f}"

        # Deep shadow floor stays dark and fog-free
        shadow_luma = float(luma[-24:, :].mean())
        assert shadow_luma < 18.0, f"{gid} lifted black floor into fog/mud: {shadow_luma:.2f}"

    # All 10 cinema grades produce mutually distinct visual signatures
    for i, g1 in enumerate(CINEMA_GRADE_IDS):
        for g2 in CINEMA_GRADE_IDS[i + 1 :]:
            mad = float(np.mean(np.abs(graded_by_id[g1] - graded_by_id[g2])))
            assert mad >= 2.2, f"Grades {g1} and {g2} are too similar (MAD={mad:.3f})"

    # Verify Kodak 500T warm amber highlights + Prussian-indigo shadows
    k500 = graded_by_id["kodak_500t_torch_battle"]
    # Upper-mid bright warm shift vs shadow blue dominance
    hi_mask = (0.2126 * src_np[..., 0] + 0.7152 * src_np[..., 1] + 0.0722 * src_np[..., 2]) > 175.0
    sh_mask = (0.2126 * src_np[..., 0] + 0.7152 * src_np[..., 1] + 0.0722 * src_np[..., 2]) < 55.0
    assert float((k500[..., 0] - k500[..., 2])[hi_mask].mean()) > float(
        (src_np[..., 0] - src_np[..., 2])[hi_mask].mean()
    )
    assert float((k500[..., 2] - k500[..., 0])[sh_mask].mean()) > 0.0

    # Verify POV Adrenaline Grit desaturates non-red while keeping crimson banner pop
    pov = graded_by_id["pov_adrenaline_grit"]
    banner_slice = pov[60:180, 45:95]
    assert float(banner_slice[..., 0].mean() - banner_slice[..., 1].mean()) > 95.0

    # Verify physical halation adds warm red-amber energy around bright torch core vs no-halation
    with_hal = apply_optical_grade_numpy(np.asarray(src, dtype=np.uint8), "S01", act=2, include_halation=True, include_grain=False)
    no_hal = apply_optical_grade_numpy(np.asarray(src, dtype=np.uint8), "S01", act=2, include_halation=False, include_grain=False)
    cy, cx = src.height // 2, src.width // 2
    ring = with_hal[cy - 28 : cy + 28, cx - 28 : cx + 28, 0].astype(np.float32) - no_hal[
        cy - 28 : cy + 28, cx - 28 : cx + 28, 0
    ].astype(np.float32)
    assert float(ring.mean()) > 1.2

    # Verify stateful Act 1 -> Act 2 transitions for S05 (chronicle_split_contrast) & S10 (eastern_lacquer_ink_to_cinema)
    s05_myth = np.asarray(apply_optical_grade_pil(src, "S05", act=1), dtype=np.float32)
    s05_chron = np.asarray(apply_optical_grade_pil(src, "S05", act=2), dtype=np.float32)
    assert float((s05_chron[..., 0] - s05_chron[..., 2]).mean()) > float((s05_myth[..., 0] - s05_myth[..., 2]).mean()) + 10.0

    s10_ink = np.asarray(apply_optical_grade_pil(src, "S10", act=1), dtype=np.float32)
    s10_cinema = np.asarray(apply_optical_grade_pil(src, "S10", act=2), dtype=np.float32)
    assert float(np.mean(np.abs(s10_cinema - s10_ink))) > 8.0


def test_rgba_alpha_preservation_and_3d_lut_export(tmp_path: Path) -> None:
    rgba = Image.new("RGBA", (96, 96), (210, 160, 110, 137))
    graded_rgba = apply_optical_grade_pil(rgba, "L02", act=3)
    assert graded_rgba.mode == "RGBA"
    assert np.all(np.asarray(graded_rgba)[..., 3] == 137)

    cube_path = export_3d_lut_cube_file("S07", tmp_path / "s07_duel.cube", act=2, size=9)
    assert cube_path.is_file()
    cube = build_3d_lut_cube("S07", act=2, size=9)
    assert cube.shape == (9, 9, 9, 3)
    assert float(cube.min()) >= 0.0 and float(cube.max()) <= 1.0


def test_ffmpeg_10_distinct_grade_chains_and_cube_lut_playback(tmp_path: Path) -> None:
    chains = {gid: get_ffmpeg_grade_filter(gid, act=2) for gid in CINEMA_GRADE_IDS}
    assert len(set(chains.values())) == 10

    # Also verify exported .cube LUT loads cleanly in real FFmpeg `lut3d` filter!
    cube_file = export_3d_lut_cube_file("kodak_500t_torch_battle", tmp_path / "k500t.cube", act=2, size=9)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "lavfi",
        "-i",
        "testsrc2=s=160x90:r=30:d=0.1",
        "-vf",
        f"lut3d=file='{cube_file.as_posix()}'",
        "-frames:v",
        "1",
        "-f",
        "null",
        "-",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    assert res.returncode == 0, res.stderr


def test_real_35mm_frame_and_2x5_showcase_strip(tmp_path: Path) -> None:
    src_path = REAL_UNG_CHAU_FRAME
    if not src_path.is_file():
        src_path = tmp_path / "fallback_beat_01.png"
        _make_synthetic_torch_battle_frame(540, 960).save(src_path)

    out_strip = tmp_path / "optical_luts_10x10_showcase.png"
    rendered = render_optical_luts_showcase(src_path, out_strip, act=2, tile_width=240)
    assert rendered.is_file()
    with Image.open(rendered) as strip_im:
        assert strip_im.mode == "RGB"
        assert strip_im.width > 1200
        assert strip_im.height > 900
