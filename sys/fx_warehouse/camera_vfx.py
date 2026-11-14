"""Camera Motion & GPU VFX Shader Sub-Warehouse.

Holds the 8 shared sub-pixel 2.5D camera moves (`CAMERA_MOTION_CATALOG`),
the 7 shared GPU frame shaders (`VFX_SHADER_CATALOG`), and per-video bespoke
registration APIs (`register_bespoke_camera_motion`, `register_bespoke_vfx_shader`).
"""
from __future__ import annotations

from typing import Any

CAMERA_MOTION_CATALOG: dict[str, dict[str, Any]] = {
    "parallax_push_in": {
        "z0": 1.045, "z1": 1.120, "x0": -0.008, "x1": 0.008, "y0": 0.004, "y1": -0.004, "parallax_amp": 0.024,
        "description": "Tiến máy 2.5D mượt tách lớp tiền-hậu cảnh tạo chiều sâu căng thẳng.",
    },
    "parallax_pull_out": {
        "z0": 1.110, "z1": 1.042, "x0": 0.010, "x1": -0.010, "y0": -0.004, "y1": 0.004, "parallax_amp": 0.022,
        "description": "Lùi máy 2.5D hé lộ toàn cảnh lớn hơn.",
    },
    "anamorphic_pan_lr": {
        "z0": 1.060, "z1": 1.090, "x0": -0.020, "x1": 0.020, "y0": 0.0, "y1": 0.0, "parallax_amp": 0.020,
        "description": "Lia ngang trái-sang-phải phong cách ống kính anamorphic điện ảnh.",
    },
    "anamorphic_pan_rl": {
        "z0": 1.085, "z1": 1.055, "x0": 0.018, "x1": -0.018, "y0": 0.002, "y1": -0.002, "parallax_amp": 0.018,
        "description": "Lia ngang phải-sang-trái tạo chuyển động phản chiều.",
    },
    "orbital_tilt_up": {
        "z0": 1.045, "z1": 1.100, "x0": -0.006, "x1": 0.006, "y0": 0.010, "y1": -0.010, "parallax_amp": 0.020,
        "description": "Nghiêng máy hướng lên tôn vinh quy mô công trình/chủ thể.",
    },
    "orbital_tilt_down": {
        "z0": 1.045, "z1": 1.092, "x0": 0.0, "x1": 0.0, "y0": -0.010, "y1": 0.008, "parallax_amp": 0.016,
        "description": "Nghiêng góc nhìn từ trên cao xuống bản đồ vệ tinh hoặc bàn hồ sơ.",
    },
    "breathing_drift": {
        "z0": 1.020, "z1": 1.045, "x0": -0.004, "x1": 0.004, "y0": -0.002, "y1": 0.002, "parallax_amp": 0.008,
        "description": "Nhịp thở cực êm bảo toàn bố cục 2D doodle sạch hoặc cảnh chữa lành.",
    },
    "static_clean": {
        "z0": 1.000, "z1": 1.000, "x0": 0.0, "x1": 0.0, "y0": 0.0, "y1": 0.0, "parallax_amp": 0.0,
        "description": "Khung tĩnh tuyệt đối dành cho split-screen hoặc sơ đồ chữ dày.",
    },
}

VFX_SHADER_CATALOG: dict[str, dict[str, Any]] = {
    "camera_shake_impulse": {"intensity": "high", "description": "Rung máy tắt dần theo hàm mũ đồng bộ cú va chạm/đóng dấu."},
    "kodak_35mm_grain": {"intensity": "low", "description": "Nhiễu hạt phim 35mm điện ảnh tăng độ chân thực."},
    "crimson_strobe_alert": {"intensity": "high", "description": "Ánh chớp đỏ cảnh báo 2200K cho phân cảnh khẩn cấp."},
    "chromatic_glitch_pulse": {"intensity": "medium", "description": "Tách kênh màu RGB micro-glitch khi nhiễu sóng/nhầm lẫn."},
    "hypoxic_vignette": {"intensity": "medium", "description": "Tối viền co thắt dần mô phỏng mất nhận thức/thiếu oxy."},
    "warm_dust_motes": {"intensity": "low", "description": "Ánh hạt bụi vàng ấm trôi chậm dịu mắt."},
    "clean_daylight_none": {"intensity": "none", "description": "Giữ khung hình sạch 100%, không thêm hiệu ứng nhiễu."},
}

BESPOKE_CAMERA_MOTIONS: dict[str, dict[str, Any]] = {}
BESPOKE_VFX_SHADERS: dict[str, dict[str, Any]] = {}


def register_bespoke_camera_motion(
    name: str,
    z0: float = 1.03,
    z1: float = 1.08,
    x0: float = 0.0,
    x1: float = 0.0,
    y0: float = 0.0,
    y1: float = 0.0,
    parallax_amp: float = 0.015,
    description: str = "",
    topic: str | None = None,
    promote: bool = False,
) -> dict[str, Any]:
    """Register a custom per-video 2.5D camera motion curve."""
    entry: dict[str, Any] = {
        "z0": float(z0),
        "z1": float(z1),
        "x0": float(x0),
        "x1": float(x1),
        "y0": float(y0),
        "y1": float(y1),
        "parallax_amp": float(parallax_amp),
        "description": description or f"Bespoke camera motion '{name}'",
        "is_bespoke": True,
    }
    if topic:
        entry["topic"] = topic
    BESPOKE_CAMERA_MOTIONS[name] = entry
    if promote:
        CAMERA_MOTION_CATALOG[name] = entry
    return entry


def register_bespoke_vfx_shader(
    name: str,
    intensity: str = "medium",
    description: str = "",
    params: dict[str, Any] | None = None,
    topic: str | None = None,
    promote: bool = False,
) -> dict[str, Any]:
    """Register a custom per-video GPU VFX shader specification."""
    entry: dict[str, Any] = {
        "intensity": intensity,
        "description": description or f"Bespoke VFX shader '{name}'",
        "params": dict(params or {}),
        "is_bespoke": True,
    }
    if topic:
        entry["topic"] = topic
    BESPOKE_VFX_SHADERS[name] = entry
    if promote:
        VFX_SHADER_CATALOG[name] = entry
    return entry


def get_camera_motion(name: str) -> dict[str, Any]:
    """Look up a camera motion from bespoke registrations first, then shared catalog."""
    if name in BESPOKE_CAMERA_MOTIONS:
        return BESPOKE_CAMERA_MOTIONS[name]
    return CAMERA_MOTION_CATALOG.get(name, CAMERA_MOTION_CATALOG["parallax_push_in"])


def get_vfx_shader(name: str) -> dict[str, Any]:
    """Look up a VFX shader from bespoke registrations first, then shared catalog."""
    if name in BESPOKE_VFX_SHADERS:
        return BESPOKE_VFX_SHADERS[name]
    return VFX_SHADER_CATALOG.get(name, VFX_SHADER_CATALOG["clean_daylight_none"])
