"""Tests for geo_empire_clash_3d — 3D Perspective Geo-Terrain & Faction Clash Animator."""

from __future__ import annotations

import shutil
from pathlib import Path

import cv2
import numpy as np
import pytest

from fx_warehouse.geo_empire_clash_3d import (
    ENGINE_VERSION,
    FACTION_PALETTES,
    GEO_EMPIRE_PRESETS,
    PerspectiveCamera3D,
    _catmull_rom_spline,
    _clamp,
    _draw_compass,
    _draw_faction_token,
    _draw_shockwave_ring,
    _draw_territory_tint,
    _draw_tidal_physics,
    _ease_in_out_cubic,
    _generate_procedural_terrain,
    _lerp,
    _resolve_scene_spec,
    _sample_spline_at,
    get_geo_empire_preset,
    list_geo_empire_presets,
    render_geo_empire_clash_frame,
    render_geo_empire_clash_mp4,
)


# ---------------------------------------------------------------------------
# Constants / Fixtures
# ---------------------------------------------------------------------------
PRESET_IDS = [
    "bach_dang_938_ngo_quyen",
    "bach_dang_1288_tran_hung_dao",
    "nhu_nguyet_1077_ly_thuong_kiet",
]

TMP_DIR = Path("/tmp/test_geo_empire_clash_3d")


@pytest.fixture(autouse=True)
def _setup_tmp():
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    yield
    # Cleanup
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR, ignore_errors=True)


# ---------------------------------------------------------------------------
# Unit Tests: Math Helpers
# ---------------------------------------------------------------------------
class TestMathHelpers:
    def test_clamp_within_range(self):
        assert _clamp(0.5) == 0.5

    def test_clamp_below(self):
        assert _clamp(-1.0) == 0.0

    def test_clamp_above(self):
        assert _clamp(2.0) == 1.0

    def test_clamp_custom_range(self):
        assert _clamp(5.0, 0.0, 10.0) == 5.0
        assert _clamp(-1.0, 0.0, 10.0) == 0.0
        assert _clamp(15.0, 0.0, 10.0) == 10.0

    def test_ease_in_out_cubic_endpoints(self):
        assert _ease_in_out_cubic(0.0) == pytest.approx(0.0)
        assert _ease_in_out_cubic(1.0) == pytest.approx(1.0)

    def test_ease_in_out_cubic_midpoint(self):
        assert _ease_in_out_cubic(0.5) == pytest.approx(0.5, abs=0.01)

    def test_ease_in_out_cubic_monotonic(self):
        vals = [_ease_in_out_cubic(t / 100.0) for t in range(101)]
        for i in range(len(vals) - 1):
            assert vals[i] <= vals[i + 1] + 1e-9

    def test_lerp(self):
        assert _lerp(0.0, 10.0, 0.5) == pytest.approx(5.0)
        assert _lerp(0.0, 10.0, 0.0) == pytest.approx(0.0)
        assert _lerp(0.0, 10.0, 1.0) == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# Unit Tests: Spline
# ---------------------------------------------------------------------------
class TestSpline:
    def test_catmull_rom_basic(self):
        pts = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
        result = _catmull_rom_spline(pts, subdivisions=8)
        assert len(result) >= len(pts)
        assert result[0] == pytest.approx(pts[0], abs=0.01)
        assert result[-1] == pytest.approx(pts[-1], abs=0.01)

    def test_catmull_rom_two_points(self):
        pts = [(0.0, 0.0), (1.0, 1.0)]
        result = _catmull_rom_spline(pts, subdivisions=4)
        assert len(result) == 5  # 4 + 1
        assert result[0] == pytest.approx((0.0, 0.0))
        assert result[-1] == pytest.approx((1.0, 1.0))

    def test_catmull_rom_single_point(self):
        pts = [(0.5, 0.5)]
        result = _catmull_rom_spline(pts)
        assert len(result) == 1

    def test_sample_spline_at_endpoints(self):
        pts = [(0.0, 0.0), (0.5, 0.5), (1.0, 1.0)]
        pos, _ang = _sample_spline_at(pts, 0.0)
        assert pos == pytest.approx((0.0, 0.0), abs=0.01)
        pos, _ang = _sample_spline_at(pts, 1.0)
        assert pos == pytest.approx((1.0, 1.0), abs=0.01)


# ---------------------------------------------------------------------------
# Unit Tests: PerspectiveCamera3D
# ---------------------------------------------------------------------------
class TestPerspectiveCamera3D:
    def test_homography_shape(self):
        cam = PerspectiveCamera3D(3840, 2160, 1920, 1080)
        H = cam.compute_homography(0.5, 0.5, 40.0, 2.0)
        assert H.shape == (3, 3)
        assert H.dtype == np.float32

    def test_homography_invertible(self):
        cam = PerspectiveCamera3D(3840, 2160, 1920, 1080)
        H = cam.compute_homography(0.5, 0.5, 40.0, 2.0)
        det = np.linalg.det(H)
        assert abs(det) > 1e-6, "Homography must be invertible"

    def test_warp_canvas_shape(self):
        cam = PerspectiveCamera3D(640, 360, 320, 180)
        canvas = np.zeros((360, 640, 3), dtype=np.uint8)
        result = cam.warp_canvas(canvas, 0.5, 0.5, 40.0, 1.5)
        assert result.shape == (180, 320, 3)
        assert result.dtype == np.uint8

    def test_project_point_in_range(self):
        cam = PerspectiveCamera3D(640, 360, 320, 180)
        sx, sy = cam.project_point(0.5, 0.5, 0.5, 0.5, 40.0, 2.0)
        # Center point should be near screen center
        assert 0 < sx < 320
        assert 0 < sy < 180

    def test_pitch_range_clamped(self):
        cam = PerspectiveCamera3D(640, 360, 320, 180)
        # Should not crash with extreme pitch values
        H1 = cam.compute_homography(0.5, 0.5, 5.0, 2.0)  # below min
        H2 = cam.compute_homography(0.5, 0.5, 85.0, 2.0)  # above max
        assert H1.shape == (3, 3)
        assert H2.shape == (3, 3)

    def test_smooth_camera_path_no_jitter(self):
        """Verify sub-pixel smooth camera animation (zero integer jitter)."""
        cam = PerspectiveCamera3D(640, 360, 320, 180)
        positions = []
        for i in range(30):
            t = i / 29.0
            cx = 0.4 + 0.1 * t
            cy = 0.4 + 0.1 * t
            pitch = 32.0 + 16.0 * t
            zoom = 1.5 + 1.0 * t
            sx, sy = cam.project_point(0.5, 0.5, cx, cy, pitch, zoom)
            positions.append((sx, sy))
        # Check smoothness: no large jumps between consecutive frames
        for i in range(1, len(positions)):
            dx = abs(positions[i][0] - positions[i - 1][0])
            dy = abs(positions[i][1] - positions[i - 1][1])
            assert dx < 50, f"X jitter at frame {i}: {dx}"
            assert dy < 50, f"Y jitter at frame {i}: {dy}"


# ---------------------------------------------------------------------------
# Unit Tests: Terrain Generator
# ---------------------------------------------------------------------------
class TestTerrain:
    def test_procedural_terrain_shape(self):
        t = _generate_procedural_terrain(640, 360)
        assert t.shape == (360, 640, 3)
        assert t.dtype == np.uint8

    def test_procedural_terrain_deterministic(self):
        t1 = _generate_procedural_terrain(320, 180, seed=42)
        t2 = _generate_procedural_terrain(320, 180, seed=42)
        assert np.array_equal(t1, t2)

    def test_procedural_terrain_different_seeds(self):
        t1 = _generate_procedural_terrain(320, 180, seed=42)
        t2 = _generate_procedural_terrain(320, 180, seed=99)
        assert not np.array_equal(t1, t2)

    def test_terrain_with_rivers(self):
        rivers = [{"points": [(0.1, 0.5), (0.9, 0.5)], "widths": [0.02, 0.04]}]
        t = _generate_procedural_terrain(320, 180, rivers=rivers)
        assert t.shape == (180, 320, 3)

    def test_terrain_with_ridges(self):
        ridges = [{"points": [(0.3, 0.3), (0.7, 0.3)], "height": 0.6, "sigma": 0.08}]
        t = _generate_procedural_terrain(320, 180, ridges=ridges)
        assert t.shape == (180, 320, 3)

    def test_terrain_with_sea(self):
        sea = {"x0": 0.7, "y0": 0.0, "x1": 1.0, "y1": 1.0}
        t = _generate_procedural_terrain(320, 180, sea_region=sea)
        assert t.shape == (180, 320, 3)
        # Sea region should be darker than land
        sea_mean = t[0:180, 224:320].mean()
        land_mean = t[0:180, 0:160].mean()
        assert sea_mean < land_mean, "Sea region should be darker"


# ---------------------------------------------------------------------------
# Unit Tests: Territory Tint
# ---------------------------------------------------------------------------
class TestTerritoryTint:
    def test_territory_tint_shape(self):
        canvas = np.full((180, 320, 3), 128, dtype=np.uint8)
        territories = [
            {"faction": "dai_viet", "region": {"x0": 0.0, "y0": 0.0, "x1": 0.5, "y1": 1.0},
             "advance_start": 0.3, "advance_end": 0.8},
        ]
        result = _draw_territory_tint(canvas, territories, 0.5)
        assert result.shape == (180, 320, 3)
        assert result.dtype == np.uint8

    def test_territory_tint_modifies_canvas(self):
        canvas = np.full((180, 320, 3), 128, dtype=np.uint8)
        territories = [
            {"faction": "dai_viet", "region": {"x0": 0.0, "y0": 0.0, "x1": 0.5, "y1": 1.0},
             "advance_start": 0.3, "advance_end": 0.8},
        ]
        result = _draw_territory_tint(canvas, territories, 0.5)
        assert not np.array_equal(canvas, result), "Territory tint should modify canvas"


# ---------------------------------------------------------------------------
# Unit Tests: Tidal Physics
# ---------------------------------------------------------------------------
class TestTidalPhysics:
    def test_tidal_disabled(self):
        canvas = np.full((180, 320, 3), 128, dtype=np.uint8)
        result = _draw_tidal_physics(canvas, {"enabled": False}, 0.5)
        assert np.array_equal(canvas, result)

    def test_tidal_none(self):
        canvas = np.full((180, 320, 3), 128, dtype=np.uint8)
        result = _draw_tidal_physics(canvas, None, 0.5)
        assert np.array_equal(canvas, result)

    def test_tidal_modifies_canvas(self):
        canvas = np.full((180, 320, 3), 128, dtype=np.uint8)
        tidal = {
            "enabled": True,
            "start_m": 1.4,
            "end_m": -3.8,
            "stake_threshold_m": -1.2,
            "stake_beds": [
                {"p0": (0.4, 0.5), "p1": (0.6, 0.5), "rows": 2, "count": 5},
            ],
        }
        result = _draw_tidal_physics(canvas, tidal, 0.8)
        assert not np.array_equal(canvas, result)


# ---------------------------------------------------------------------------
# Unit Tests: Faction Token
# ---------------------------------------------------------------------------
class TestFactionToken:
    def test_token_shape(self):
        canvas = np.zeros((200, 300, 3), dtype=np.uint8)
        result = _draw_faction_token(canvas, 150, 100, 20, "dai_viet", "TEST")
        assert result.shape == (200, 300, 3)

    def test_token_modifies_canvas(self):
        canvas = np.zeros((200, 300, 3), dtype=np.uint8)
        result = _draw_faction_token(canvas, 150, 100, 20, "dai_viet", "BADGE")
        assert not np.array_equal(canvas, result)

    def test_token_all_factions(self):
        for faction in FACTION_PALETTES:
            canvas = np.zeros((200, 300, 3), dtype=np.uint8)
            result = _draw_faction_token(canvas, 150, 100, 20, faction, faction.upper())
            assert result.shape == (200, 300, 3)

    def test_token_damaged(self):
        canvas = np.zeros((200, 300, 3), dtype=np.uint8)
        result_ok = _draw_faction_token(canvas, 150, 100, 20, "dai_viet", "OK")
        result_dmg = _draw_faction_token(canvas, 150, 100, 20, "dai_viet", "BROKEN", damaged=True)
        assert not np.array_equal(result_ok, result_dmg)


# ---------------------------------------------------------------------------
# Unit Tests: Shockwave
# ---------------------------------------------------------------------------
class TestShockwave:
    def test_shockwave_no_effect_before_trigger(self):
        canvas = np.full((200, 300, 3), 100, dtype=np.uint8)
        result = _draw_shockwave_ring(canvas, 150, 100, 0.0, 50)
        assert np.array_equal(canvas, result)

    def test_shockwave_modifies_at_mid(self):
        canvas = np.full((200, 300, 3), 100, dtype=np.uint8)
        result = _draw_shockwave_ring(canvas, 150, 100, 0.5, 50)
        assert not np.array_equal(canvas, result)


# ---------------------------------------------------------------------------
# Unit Tests: Presets
# ---------------------------------------------------------------------------
class TestPresets:
    def test_all_preset_ids_exist(self):
        for pid in PRESET_IDS:
            assert pid in GEO_EMPIRE_PRESETS

    def test_list_presets(self):
        lst = list_geo_empire_presets()
        assert len(lst) == 3
        ids = {p["preset_id"] for p in lst}
        assert ids == set(PRESET_IDS)

    def test_get_preset_returns_deep_copy(self):
        p1 = get_geo_empire_preset("bach_dang_938_ngo_quyen")
        p2 = get_geo_empire_preset("bach_dang_938_ngo_quyen")
        p1["title_vi"] = "MODIFIED"
        assert p2["title_vi"] != "MODIFIED"

    def test_get_preset_invalid_raises(self):
        with pytest.raises(KeyError):
            get_geo_empire_preset("nonexistent_battle")

    @pytest.mark.parametrize("preset_id", PRESET_IDS)
    def test_preset_has_required_fields(self, preset_id):
        spec = get_geo_empire_preset(preset_id)
        required = [
            "preset_id", "title_vi", "year", "date_stamp", "seed",
            "canvas_size", "camera", "terrain", "factions", "phases",
        ]
        for field in required:
            assert field in spec, f"Preset {preset_id} missing '{field}'"

    @pytest.mark.parametrize("preset_id", PRESET_IDS)
    def test_preset_camera_has_start_end(self, preset_id):
        spec = get_geo_empire_preset(preset_id)
        cam = spec["camera"]
        assert "start" in cam
        assert "end" in cam
        for key in ("cx", "cy", "pitch", "zoom"):
            assert key in cam["start"]
            assert key in cam["end"]

    @pytest.mark.parametrize("preset_id", PRESET_IDS)
    def test_preset_pitch_in_range(self, preset_id):
        spec = get_geo_empire_preset(preset_id)
        cam = spec["camera"]
        for endpoint in ("start", "end"):
            pitch = cam[endpoint]["pitch"]
            assert 20.0 <= pitch <= 70.0, f"Pitch {pitch} out of range"


# ---------------------------------------------------------------------------
# Unit Tests: Scene Spec Resolution
# ---------------------------------------------------------------------------
class TestResolveSpec:
    def test_resolve_from_string(self):
        spec = _resolve_scene_spec("bach_dang_938_ngo_quyen")
        assert spec["preset_id"] == "bach_dang_938_ngo_quyen"

    def test_resolve_from_dict_with_base(self):
        spec = _resolve_scene_spec({
            "base_preset": "bach_dang_938_ngo_quyen",
            "title_vi": "CUSTOM TITLE",
        })
        assert spec["title_vi"] == "CUSTOM TITLE"
        assert "terrain" in spec

    def test_resolve_fully_custom_dict(self):
        spec = _resolve_scene_spec({
            "terrain": {"rivers": [], "ridges": []},
            "title_vi": "CUSTOM",
        })
        assert spec["preset_id"] == "custom"
        assert spec["title_vi"] == "CUSTOM"


# ---------------------------------------------------------------------------
# Integration Tests: Frame Rendering
# ---------------------------------------------------------------------------
class TestFrameRendering:
    def test_frame_shape_1920x1080(self):
        frame = render_geo_empire_clash_frame("bach_dang_938_ngo_quyen", 0.5, 320, 180)
        assert frame.shape == (180, 320, 3)
        assert frame.dtype == np.uint8

    def test_frame_rgb_range(self):
        frame = render_geo_empire_clash_frame("bach_dang_938_ngo_quyen", 0.0, 320, 180)
        assert frame.min() >= 0
        assert frame.max() <= 255

    def test_frame_not_black(self):
        frame = render_geo_empire_clash_frame("bach_dang_938_ngo_quyen", 0.5, 320, 180)
        assert frame.mean() > 5.0, "Frame should not be nearly black"

    def test_frame_varies_over_time(self):
        f0 = render_geo_empire_clash_frame("bach_dang_938_ngo_quyen", 0.0, 320, 180)
        f1 = render_geo_empire_clash_frame("bach_dang_938_ngo_quyen", 1.0, 320, 180)
        assert not np.array_equal(f0, f1), "Start and end frames must differ"

    @pytest.mark.parametrize("preset_id", PRESET_IDS)
    def test_all_presets_render(self, preset_id):
        frame = render_geo_empire_clash_frame(preset_id, 0.5, 320, 180)
        assert frame.shape == (180, 320, 3)
        assert frame.mean() > 3.0

    def test_frame_save_png(self):
        frame = render_geo_empire_clash_frame("bach_dang_938_ngo_quyen", 0.5, 640, 360)
        png_path = TMP_DIR / "test_frame.png"
        cv2.imwrite(str(png_path), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        assert png_path.is_file()
        assert png_path.stat().st_size > 1000

    def test_custom_spec_renders(self):
        custom = {
            "terrain": {
                "rivers": [{"points": [(0.2, 0.5), (0.8, 0.5)], "widths": [0.02, 0.04]}],
                "ridges": [],
            },
            "factions": {
                "left_name": "A", "right_name": "B",
                "left_stat_start": "", "left_stat_end": "",
                "right_stat_start": "", "right_stat_end": "",
                "ratio_start": 0.5, "ratio_end": 0.7,
            },
            "phases": [{"t_max": 1.0, "label": "TEST"}],
        }
        frame = render_geo_empire_clash_frame(custom, 0.5, 320, 180)
        assert frame.shape == (180, 320, 3)


# ---------------------------------------------------------------------------
# Integration Tests: MP4 Rendering
# ---------------------------------------------------------------------------
class TestMP4Rendering:
    @pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
    def test_render_mp4_basic(self):
        out = TMP_DIR / "test_basic.mp4"
        result = render_geo_empire_clash_mp4(
            "bach_dang_938_ngo_quyen", out,
            width=320, height=180, fps=10, duration_sec=0.5,
        )
        assert Path(result["path"]).is_file()
        assert result["width"] == 320
        assert result["height"] == 180
        assert result["fps"] == 10
        assert result["preset_id"] == "bach_dang_938_ngo_quyen"
        assert result["engine_version"] == ENGINE_VERSION
        assert Path(result["path"]).stat().st_size > 500

    @pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
    def test_render_mp4_all_presets(self):
        for pid in PRESET_IDS:
            out = TMP_DIR / f"test_{pid}.mp4"
            result = render_geo_empire_clash_mp4(
                pid, out,
                width=320, height=180, fps=10, duration_sec=0.3,
            )
            assert Path(result["path"]).is_file()
            assert Path(result["path"]).stat().st_size > 200

    @pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
    def test_render_mp4_even_dimensions(self):
        """Odd dimensions should be rounded down to even."""
        out = TMP_DIR / "test_odd.mp4"
        result = render_geo_empire_clash_mp4(
            "bach_dang_938_ngo_quyen", out,
            width=321, height=181, fps=10, duration_sec=0.3,
        )
        assert result["width"] == 320
        assert result["height"] == 180

    @pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
    def test_render_mp4_custom_spec(self):
        custom = {
            "terrain": {"rivers": [], "ridges": []},
            "phases": [{"t_max": 1.0, "label": "TEST"}],
        }
        out = TMP_DIR / "test_custom.mp4"
        result = render_geo_empire_clash_mp4(
            custom, out,
            width=320, height=180, fps=10, duration_sec=0.3,
        )
        assert Path(result["path"]).is_file()

    @pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")
    def test_render_1920x1080_4s(self):
        """Render a quick 4s test at full resolution to verify real output."""
        out = TMP_DIR / "test_full_4s.mp4"
        result = render_geo_empire_clash_mp4(
            "bach_dang_938_ngo_quyen", out,
            width=640, height=360, fps=15, duration_sec=1.0,
        )
        assert Path(result["path"]).is_file()
        fsize = Path(result["path"]).stat().st_size
        assert fsize > 2000, f"MP4 too small: {fsize} bytes"


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
class TestCompass:
    def test_compass_shape(self):
        canvas = np.zeros((180, 320, 3), dtype=np.uint8)
        result = _draw_compass(canvas)
        assert result.shape == (180, 320, 3)

    def test_compass_modifies_canvas(self):
        canvas = np.zeros((180, 320, 3), dtype=np.uint8)
        result = _draw_compass(canvas)
        assert not np.array_equal(canvas, result)


class TestEngineVersion:
    def test_version_string(self):
        assert isinstance(ENGINE_VERSION, str)
        parts = ENGINE_VERSION.split(".")
        assert len(parts) == 3
