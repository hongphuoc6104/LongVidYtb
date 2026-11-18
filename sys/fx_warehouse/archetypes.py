"""Archetype Profiles, 20-Channel Mapping & Bespoke Synthesis Policies.

Defines the 5 Vietnamese content archetypes, maps all 20 channels, and specifies
explicit `bespoke_synthesis_policy` and `topic_bespoke_triggers` so each niche
dynamically authors custom HUDs, VFX, and procedural SFX/BGM when shared presets
do not fit a specific video topic.
"""
from __future__ import annotations

import re
from typing import Any

ARCHETYPE_PROFILES: dict[str, dict[str, Any]] = {
    "archetype_1_forensic_noir": {
        "label": "Điều Tra Hồ Sơ Mật & Quy Luật Ngầm",
        "accent_rgba": (205, 52, 48, 255),
        "secondary_rgba": (212, 168, 72, 255),
        "default_camera": "parallax_push_in",
        "default_vfx": "kodak_35mm_grain",
        "default_bgm": "bgm_forensic_noir_drone.wav",
        "disallowed_vfx": (),
        "bespoke_synthesis_policy": (
            "Ưu tiên tư liệu thật & độ chính xác hiện trường: nếu vụ án/quy luật ngầm thuộc môi trường "
            "đặc thù (hàng hải, y khoa pháp y, tài chính rửa tiền, mật mã học, sinh tồn cực hạn), "
            "phải tổng hợp HUD/SFX riêng theo ngữ cảnh đó; tuyệt đối không gắn HUD buồng lái máy bay "
            "lên vụ án hàng hải hay đầu độc."
        ),
        "topic_bespoke_triggers": (
            "hàng hải|tàu ngầm|sonar|độ sâu",
            "độc chất|pháp y|xét nghiệm|mẫu máu|giải phẫu",
            "mật mã|giải mã|tín hiệu số|mã hóa",
            "rửa tiền|dòng tiền|tài khoản ẩn|offshore",
            "sinh tồn|bão tuyết|sa mạc|thân nhiệt",
        ),
    },
    "archetype_2_geopolitics_history": {
        "label": "Địa Chính Trị, Lịch Sử, Kinh Tế Vĩ Mô & Giải Phẫu Thảm Họa",
        "accent_rgba": (212, 168, 72, 255),
        "secondary_rgba": (32, 212, 248, 255),
        "default_camera": "anamorphic_pan_lr",
        "default_vfx": "kodak_35mm_grain",
        "default_bgm": "bgm_geopolitics_pulse.wav",
        "disallowed_vfx": (),
        "bespoke_synthesis_policy": (
            "Phân biệt rạch ròi thời đại lịch sử, chuỗi cung ứng hiện đại và thảm họa kỹ thuật/đại dịch: "
            "với sử cổ/trung đại tạo HUD bản đồ chiến dịch cổ; với địa chính trị & vĩ mô tạo biểu đồ eo biển/thương mại; "
            "với thảm họa hạt nhân/hạ tầng/đại dịch tạo bản đồ GIS phân tán, mặt cắt kỹ thuật 2D/3D và chuỗi domino nhân quả."
        ),
        "topic_bespoke_triggers": (
            "triều đại|cổ đại|trận đánh|kỵ binh|thành trì",
            "bán dẫn|chip|lithium|đất hiếm|chuỗi cung ứng",
            "lãi suất|trái phiếu|tỷ giá|dự trữ ngoại hối",
            "kênh đào|eo biển|cảng biển|hành lang năng lượng",
            "lò phản ứng|hạt nhân|phóng xạ|đập thủy điện|đại dịch|sụp đổ",
        ),
    },
    "archetype_3_science_xray": {
        "label": "Khoa Học, Vũ Trụ & Giải Phẫu Cơ Chế",
        "accent_rgba": (32, 212, 248, 255),
        "secondary_rgba": (205, 52, 48, 255),
        "default_camera": "parallax_push_in",
        "default_vfx": "chromatic_glitch_pulse",
        "default_bgm": "bgm_scifi_biotech_pad.wav",
        "disallowed_vfx": (),
        "bespoke_synthesis_policy": (
            "Mỗi cơ chế vật lý, thiên văn hay sinh học có thang đo riêng: tự tạo HUD đo bước sóng/quỹ đạo, "
            "sơ đồ synap/enzyme hoặc mặt cắt địa chất khi preset X-Ray chung không diễn đạt đúng bản chất."
        ),
        "topic_bespoke_triggers": (
            "lỗ đen|hố đen|thiên hà|năm ánh sáng|lượng tử",
            "synap|neuron|hormone|dopamine|miễn dịch|dna",
            "động đất|mảng kiến tạo|núi lửa|trầm tích",
            "phản ứng hóa học|áp suất|nhiệt động|từ trường",
        ),
    },
    "archetype_4_doodle_explainer": {
        "label": "2D Doodle Giáo Dục, Tài Chính, Luật & AI",
        "accent_rgba": (59, 130, 196, 255),
        "secondary_rgba": (245, 158, 11, 255),
        "default_camera": "breathing_drift",
        "default_vfx": "clean_daylight_none",
        "default_bgm": "bgm_curious_acoustic_loop.wav",
        "disallowed_vfx": ("crimson_strobe_alert", "camera_shake_impulse", "hypoxic_vignette"),
        "bespoke_synthesis_policy": (
            "Giữ nền sáng sạch, nét 2D dễ đọc và nhịp nảy nhẹ nhàng: khi chủ đề là bậc thuế, lãi kép, "
            "điều khoản hợp đồng, pipeline AI/prompt hay sơ đồ học tập, tạo thẻ/sơ đồ doodle riêng cho "
            "từng bài toán thay vì ép dùng khung radar hay đồng hồ sinh tồn."
        ),
        "topic_bespoke_triggers": (
            "bậc thuế|thuế thu nhập|lãi kép|cân đối thu chi|nợ xấu",
            "điều khoản|hợp đồng|bộ luật|án lệ|quyền lợi",
            "prompt|token|mô hình ngôn ngữ|ai agent|tự động hóa",
            "phương pháp học|trí nhớ|lộ trình|thói quen",
        ),
    },
    "archetype_5_mindful_healing": {
        "label": "Chánh Niệm, Minh Triết & Tâm Tình Đêm",
        "accent_rgba": (232, 200, 142, 255),
        "secondary_rgba": (182, 194, 210, 255),
        "default_camera": "breathing_drift",
        "default_vfx": "warm_dust_motes",
        "default_bgm": "bgm_zen_night_healing.wav",
        "disallowed_vfx": ("crimson_strobe_alert", "camera_shake_impulse", "chromatic_glitch_pulse", "hypoxic_vignette"),
        "bespoke_synthesis_policy": (
            "Tuyệt đối êm dịu, không chớp gắt hay tiếng động giật mình: khi bài nói chạm tới chu kỳ hơi thở, "
            "câu chuyện thiền, hay tâm sự đêm mưa/lò sưởi, tổng hợp thẻ thư pháp/nhịp thở và âm thanh thiên nhiên "
            "riêng (chuông xoay, mưa đêm, lửa trại, suối chảy) đồng bộ nhịp thở."
        ),
        "topic_bespoke_triggers": (
            "hít vào|thở ra|chu kỳ thở|4-7-8|thiền hành",
            "lò sưởi|đêm mưa|tiếng suối|rừng đêm|chuông gió",
            "cổ nhân|trang tử|phật pháp|minh triết|buông thư",
        ),
    },
}

CHANNEL_ARCHETYPE_MAP: dict[str, str] = {
    # Group 1: Forensic Noir & Hidden Laws
    "ho_so_ky_la": "archetype_1_forensic_noir",
    "luat_ngam": "archetype_1_forensic_noir",
    "nghe_song_sot": "archetype_1_forensic_noir",
    # Group 2: Geopolitics, History, Macro Economy & Causal Disaster Chronicles
    "ban_do_quyen_luc": "archetype_2_geopolitics_history",
    "su_ke_lai": "archetype_2_geopolitics_history",
    "banh_rang": "archetype_2_geopolitics_history",
    "chanh_niem_ke": "archetype_2_geopolitics_history",
    # Group 3: Science, Cosmos & Anatomy/Mechanism X-Ray
    "vu_tru_ti_hon": "archetype_3_science_xray",
    "co_the_ke": "archetype_3_science_xray",
    "ua_sao_vay": "archetype_3_science_xray",
    "dia_com": "archetype_3_science_xray",
    # Group 4: 2D Doodle Explainer, Finance, Law & AI
    "nao_luoi": "archetype_4_doodle_explainer",
    "tui_tien": "archetype_4_doodle_explainer",
    "luat_doi_thuong": "archetype_4_doodle_explainer",
    "ai_binh_dan": "archetype_4_doodle_explainer",
    "la_ban_hoc_thuat": "archetype_4_doodle_explainer",
    "thuong_cho_kheo": "archetype_4_doodle_explainer",
    # Group 5: Mindfulness, Wisdom & Night Reflections
    "minh_triet_song": "archetype_5_mindful_healing",
    "loi_sang_soi": "archetype_5_mindful_healing",
    "tam_tinh_dem": "archetype_5_mindful_healing",
}

# 18 English physical channels + 4 canonical aliases mapped across the 5 archetypes
EN_CHANNEL_ARCHETYPE_MAP: dict[str, str] = {
    # Group 1: Forensic Noir & Workplace/Crowd Laws
    "en_cold_case_ink": "archetype_1_forensic_noir",
    "en_crowd_strings": "archetype_1_forensic_noir",
    "en_career_leverage": "archetype_1_forensic_noir",
    # Group 2: Geopolitics, Deep Time & Macroeconomics
    "en_choke_point": "archetype_2_geopolitics_history",
    "en_macro_gears": "archetype_2_geopolitics_history",
    "en_parable_lamp": "archetype_2_geopolitics_history",
    "en_deep_time_strata": "archetype_2_geopolitics_history",
    # Group 3: Science, Cosmos & Organism/Mechanism X-Ray
    "en_inside_vessel": "archetype_3_science_xray",
    "en_pocket_cosmos": "archetype_3_science_xray",
    "en_plain_sight_ai": "archetype_3_science_xray",
    "en_scale_and_bone": "archetype_3_science_xray",
    "en_kitchen_molecules": "archetype_3_science_xray",
    "en_root_and_canopy": "archetype_3_science_xray",
    "en_wait_how": "archetype_3_science_xray",
    "en_spawn_to_apex": "archetype_3_science_xray",
    # Group 4: Behavioral Psych, Finance, Consumer Law & Mental Models
    "en_lazy_brain": "archetype_4_doodle_explainer",
    "en_wallet_anatomy": "archetype_4_doodle_explainer",
    "en_fine_print": "archetype_4_doodle_explainer",
    "en_kindred_sketch": "archetype_4_doodle_explainer",
    "en_first_principles": "archetype_4_doodle_explainer",
    # Group 5: Mindfulness, Wisdom & Night Reflections
    "en_second_arrow": "archetype_5_mindful_healing",
    "en_bamboo_marble": "archetype_5_mindful_healing",
}


def get_channel_archetype(channel_id: str) -> str:
    """Resolve archetype for any VN, EN, or alias channel ID (supports dash or underscore)."""
    norm = (channel_id or "").strip().replace("-", "_")
    return (
        CHANNEL_ARCHETYPE_MAP.get(channel_id)
        or CHANNEL_ARCHETYPE_MAP.get(norm)
        or EN_CHANNEL_ARCHETYPE_MAP.get(channel_id)
        or EN_CHANNEL_ARCHETYPE_MAP.get(norm)
        or "archetype_1_forensic_noir"
    )

CHANNEL_BESPOKE_RULES: dict[str, dict[str, Any]] = {
    "ho_so_ky_la": {
        "focus": "Hồ sơ bí ẩn, tai nạn lịch sử, giải mã hiện trường đa góc nhìn",
        "preferred_bespoke_hud_kind": "sonar_radial",
        "preferred_bespoke_sfx_profile": "forensic_pulse",
        "bespoke_synthesis_policy": "Tạo HUD hiện trường theo đúng loại phương tiện/vụ án (hàng hải, đường sắt, phòng thí nghiệm, không lưu).",
        "topic_bespoke_triggers": ("tàu ngầm", "độc chất", "hiện trường", "mất tích", "giám định"),
    },
    "luat_ngam": {
        "focus": "Quy luật quyền lực, thao túng tâm lý, mạng lưới lợi ích ẩn",
        "preferred_bespoke_hud_kind": "timeline_nodes",
        "preferred_bespoke_sfx_profile": "noir_tension",
        "bespoke_synthesis_policy": "Tạo sơ đồ mạng lưới quan hệ/dòng tiền ẩn riêng cho từng vụ việc thay vì dùng bảng điểm chung.",
        "topic_bespoke_triggers": ("rửa tiền", "mạng lưới", "thao túng", "lobby", "bóng tối"),
    },
    "nghe_song_sot": {
        "focus": "Chiến lược sự nghiệp công sở, đàm phán lương thưởng và năng lực sinh tồn kỷ nguyên AI",
        "preferred_bespoke_hud_kind": "comparison_matrix",
        "preferred_bespoke_sfx_profile": "noir_tension",
        "bespoke_synthesis_policy": "Tạo bảng ma trận đàm phán, đòn bẩy sự nghiệp và thẻ so sánh chiến lược công sở thực tế cho từng kịch bản nghề nghiệp.",
        "topic_bespoke_triggers": ("công sở", "đàm phán", "thăng tiến", "tự động hóa", "lương"),
    },
    "ban_do_quyen_luc": {
        "focus": "Địa chính trị, điểm nghẽn hàng hải, chuỗi cung ứng chiến lược",
        "preferred_bespoke_hud_kind": "sonar_radial",
        "preferred_bespoke_sfx_profile": "geopolitical_radar",
        "bespoke_synthesis_policy": "Tạo HUD tọa độ eo biển, bán kính tên lửa/tuyến vận tải và chuỗi cung ứng đặc thù cho từng khu vực.",
        "topic_bespoke_triggers": ("eo biển", "bán dẫn", "căn cứ", "đường ống", "hành lang"),
    },
    "su_ke_lai": {
        "focus": "Lịch sử sống động 35mm, chiến dịch quân sự và bước ngoặt triều đại",
        "preferred_bespoke_hud_kind": "timeline_nodes",
        "preferred_bespoke_sfx_profile": "historical_resonance",
        "bespoke_synthesis_policy": "Dựng thẻ niên đại, sơ đồ đội hình chiến dịch và âm thanh trống/kim khí cổ đại phù hợp từng thời kỳ.",
        "topic_bespoke_triggers": ("triều đại", "trận đánh", "chiến dịch", "hoàng đế", "thế kỷ"),
    },
    "banh_rang": {
        "focus": "Kinh tế vĩ mô, chu kỳ khủng hoảng, cơ chế vận hành thị trường",
        "preferred_bespoke_hud_kind": "comparison_matrix",
        "preferred_bespoke_sfx_profile": "mechanical_clockwork",
        "bespoke_synthesis_policy": "Tạo bảng cân đối vĩ mô, đồng hồ chu kỳ nợ/lạm phát riêng cho từng cuộc khủng hoảng.",
        "topic_bespoke_triggers": ("lạm phát", "bong bóng", "ngân hàng trung ương", "trái phiếu", "chu kỳ"),
    },
    "vu_tru_ti_hon": {
        "focus": "Thiên văn học, vật lý lượng tử và quy mô vũ trụ",
        "preferred_bespoke_hud_kind": "sonar_radial",
        "preferred_bespoke_sfx_profile": "cosmic_shimmer",
        "bespoke_synthesis_policy": "Tổng hợp HUD thang đo khoảng cách/bước sóng và âm nền không gian sâu cho từng thiên thể.",
        "topic_bespoke_triggers": ("lỗ đen", "quasar", "lượng tử", "thiên hà", "sóng hấp dẫn"),
    },
    "co_the_ke": {
        "focus": "Giải phẫu học, thần kinh học, cơ chế sinh hóa bên trong cơ thể",
        "preferred_bespoke_hud_kind": "timeline_nodes",
        "preferred_bespoke_sfx_profile": "biometric_pulse",
        "bespoke_synthesis_policy": "Tạo sơ đồ dẫn truyền thần kinh/hormone/miễn dịch theo đúng cơ quan được nhắc tới.",
        "topic_bespoke_triggers": ("synap", "dopamine", "cortisol", "kháng thể", "tế bào"),
    },
    "ua_sao_vay": {
        "focus": "Giải mã hiện tượng đời sống bằng vật lý & hóa học trực quan",
        "preferred_bespoke_hud_kind": "metric_meter",
        "preferred_bespoke_sfx_profile": "spark_chime",
        "bespoke_synthesis_policy": "Tạo đồng hồ đo hiện tượng (nhiệt độ, áp suất, độ pH, khúc xạ) riêng cho từng câu hỏi.",
        "topic_bespoke_triggers": ("áp suất", "khúc xạ", "phản ứng", "tại sao", "hiện tượng"),
    },
    "dia_com": {
        "focus": "Hóa học ẩm thực, nhiệt động học căn bếp, dinh dưỡng và an toàn thực phẩm",
        "preferred_bespoke_hud_kind": "metric_meter",
        "preferred_bespoke_sfx_profile": "spark_chime",
        "bespoke_synthesis_policy": "Tạo đồng hồ nhiệt độ Maillard, pH, kết cấu phân tử thực phẩm và cảnh báo an toàn bếp núc riêng cho từng món ăn.",
        "topic_bespoke_triggers": ("maillard", "nhiệt độ", "chảo gang", "an toàn thực phẩm", "dinh dưỡng"),
    },
    "nao_luoi": {
        "focus": "Tâm lý hành vi, thiên kiến nhận thức, cơ chế trì hoãn",
        "preferred_bespoke_hud_kind": "timeline_nodes",
        "preferred_bespoke_sfx_profile": "doodle_pop",
        "bespoke_synthesis_policy": "Vẽ vòng lặp thói quen/thiên kiến nhận thức riêng theo đúng bẫy tâm lý của tập.",
        "topic_bespoke_triggers": ("thiên kiến", "trì hoãn", "hiệu ứng", "não bộ", "thói quen"),
    },
    "tui_tien": {
        "focus": "Tài chính cá nhân, đầu tư, quản trị rủi ro và thuế",
        "preferred_bespoke_hud_kind": "comparison_matrix",
        "preferred_bespoke_sfx_profile": "doodle_pop",
        "bespoke_synthesis_policy": "Tạo bảng tính lãi kép, bậc thuế hoặc phân bổ tài sản riêng cho từng kịch bản tiền bạc.",
        "topic_bespoke_triggers": ("bậc thuế", "lãi kép", "danh mục", "nợ", "dòng tiền"),
    },
    "luat_doi_thuong": {
        "focus": "Pháp luật dân sự, lao động, hợp đồng và quyền lợi thường ngày",
        "preferred_bespoke_hud_kind": "comparison_matrix",
        "preferred_bespoke_sfx_profile": "paper_crisp",
        "bespoke_synthesis_policy": "Tạo thẻ đối chiếu điều khoản hợp pháp/rủi ro riêng cho từng tình huống pháp lý.",
        "topic_bespoke_triggers": ("hợp đồng", "điều khoản", "bồi thường", "khiếu nại", "quyền lợi"),
    },
    "ai_binh_dan": {
        "focus": "Ứng dụng AI thực chiến, prompt engineering và tự động hóa",
        "preferred_bespoke_hud_kind": "timeline_nodes",
        "preferred_bespoke_sfx_profile": "tech_bleep",
        "bespoke_synthesis_policy": "Tạo sơ đồ luồng Prompt -> Context -> Tool -> Output riêng cho từng workflow AI.",
        "topic_bespoke_triggers": ("prompt", "agent", "token", "workflow", "mô hình"),
    },
    "la_ban_hoc_thuat": {
        "focus": "Phương pháp học tập, nghiên cứu, tư duy hệ thống",
        "preferred_bespoke_hud_kind": "timeline_nodes",
        "preferred_bespoke_sfx_profile": "doodle_pop",
        "bespoke_synthesis_policy": "Tạo sơ đồ phương pháp học (Feynman, Spaced Repetition, Zettelkasten) theo đúng kỹ thuật trong tập.",
        "topic_bespoke_triggers": ("feynman", "ghi nhớ", "lộ trình", "tư duy", "hệ thống"),
    },
    "thuong_cho_kheo": {
        "focus": "Giao tiếp tinh tế, ứng xử gia đình - công sở, EQ thực hành",
        "preferred_bespoke_hud_kind": "comparison_matrix",
        "preferred_bespoke_sfx_profile": "doodle_pop",
        "bespoke_synthesis_policy": "Tạo thẻ đối chiếu 'Cách nói gây tổn thương vs Cách nói khéo léo' riêng theo từng tình huống.",
        "topic_bespoke_triggers": ("ứng xử", "từ chối", "lắng nghe", "ranh giới", "công sở"),
    },
    "chanh_niem_ke": {
        "focus": "Hiểu Tận Gốc — Giải phẫu thảm họa kỹ thuật, sự cố hạt nhân, đại dịch và sụp đổ hạ tầng trên bản đồ GIS",
        "preferred_bespoke_hud_kind": "sonar_radial",
        "preferred_bespoke_sfx_profile": "geopolitical_radar",
        "bespoke_synthesis_policy": "Dựng bản đồ địa hình GIS Web Mercator, mặt cắt kỹ thuật 2D/3D sự cố và chuỗi domino nhân quả cho từng thảm họa.",
        "topic_bespoke_triggers": ("lò phản ứng", "phóng xạ", "đập thủy điện", "đại dịch", "sụp đổ"),
    },
    "minh_triet_song": {
        "focus": "Triết lý sống phương Đông - phương Tây, cổ học tinh hoa",
        "preferred_bespoke_hud_kind": "telemetry_card",
        "preferred_bespoke_sfx_profile": "zen_bowl",
        "bespoke_synthesis_policy": "Tạo thẻ trích dẫn thư pháp ấm và âm nền gỗ/chuông nhẹ phù hợp bối cảnh triết gia.",
        "topic_bespoke_triggers": ("trang tử", "lão tử", "khắc kỷ", "minh triết", "đạo"),
    },
    "loi_sang_soi": {
        "focus": "Chiêm nghiệm chữa lành, vượt qua khủng hoảng tinh thần",
        "preferred_bespoke_hud_kind": "telemetry_card",
        "preferred_bespoke_sfx_profile": "warm_pad",
        "bespoke_synthesis_policy": "Tạo thẻ khẳng định dịu mắt và âm thanh thiên nhiên ấm áp (suối, gió nhẹ) đồng bộ nhịp chậm.",
        "topic_bespoke_triggers": ("chữa lành", "tổn thương", "tha thứ", "ánh sáng", "bình phục"),
    },
    "tam_tinh_dem": {
        "focus": "Tâm sự đêm khuya, cô đơn, giấc ngủ và sự vỗ về",
        "preferred_bespoke_hud_kind": "telemetry_card",
        "preferred_bespoke_sfx_profile": "night_ambience",
        "bespoke_synthesis_policy": "Tạo thẻ đêm tĩnh lặng và âm thanh mưa đêm/lò sưởi/gió đêm êm dịu tuyệt đối.",
        "topic_bespoke_triggers": ("đêm mưa", "lò sưởi", "mất ngủ", "khuya", "tâm sự"),
    },
}


def resolve_niche_fx_blueprint(
    channel_id: str,
    video_topic: str | None = None,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve archetype defaults, channel bespoke policy, and topic bespoke triggers."""
    arch_id = get_channel_archetype(channel_id)
    arch = ARCHETYPE_PROFILES[arch_id]
    ch_rule = CHANNEL_BESPOKE_RULES.get(channel_id, {})
    ovr = dict(overrides or {})
    topic_l = (video_topic or "").lower().strip()

    matched_triggers: list[str] = []
    if topic_l:
        for pat in arch.get("topic_bespoke_triggers", ()):
            if re.search(pat, topic_l):
                matched_triggers.append(pat)
        for kw in ch_rule.get("topic_bespoke_triggers", ()):
            if kw in topic_l and kw not in matched_triggers:
                matched_triggers.append(kw)

    return {
        "channel_id": channel_id,
        "archetype_id": arch_id,
        "archetype_label": arch["label"],
        "accent_rgba": ovr.get("accent_rgba", arch["accent_rgba"]),
        "secondary_rgba": ovr.get("secondary_rgba", arch["secondary_rgba"]),
        "default_camera": arch["default_camera"],
        "default_vfx": arch["default_vfx"],
        "default_bgm": arch["default_bgm"],
        "disallowed_vfx": arch["disallowed_vfx"],
        "bespoke_synthesis_policy": ch_rule.get("bespoke_synthesis_policy") or arch["bespoke_synthesis_policy"],
        "preferred_bespoke_hud_kind": ch_rule.get("preferred_bespoke_hud_kind", "telemetry_card"),
        "preferred_bespoke_sfx_profile": ch_rule.get("preferred_bespoke_sfx_profile", "forensic_pulse"),
        "matched_topic_triggers": matched_triggers,
        "should_consider_bespoke": bool(matched_triggers) or bool(ovr.get("bespoke_hud_spec") or ovr.get("bespoke_sfx_spec")),
    }
