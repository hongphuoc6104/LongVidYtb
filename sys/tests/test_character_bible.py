"""Unit and E2E integration tests for `sys/short_engine/character_bible.py` and `character_vault.json`."""
from __future__ import annotations

import copy
import json
import re
import shutil
from pathlib import Path

import pytest
from short_engine.character_bible import (
    REQUIRED_CHARACTER_FIELDS,
    ROOT_DIR,
    VALID_FACTIONS,
    apply_cast_continuity_to_spec,
    detect_episode_cast_and_sets,
    get_vault_path,
    load_character_vault,
    sanitize_benign_face_dna,
    save_character_profile,
)

EXPECTED_DAI_VIET_HEROES = {
    "ngo_quyen",
    "dinh_bo_linh",
    "le_hoan",
    "ly_cong_uan",
    "ly_thuong_kiet",
    "tran_hung_dao",
    "tran_quang_khai",
    "tran_quoc_toan",
    "tran_binh_trong",
    "tran_khanh_du",
    "le_loi",
    "le_lai",
    "nguyen_trai",
    "quang_trung",
}

EXPECTED_OPPOSING_COMMANDERS = {
    "luu_hoang_thao",
    "to_giam",
    "quach_quy",
    "thoat_hoan",
    "o_ma_nhi",
    "lieu_thang",
    "ton_si_nghi",
}


def test_su_ke_lai_character_vault_completeness_and_real_frames() -> None:
    vault = load_character_vault("su_ke_lai")
    assert vault["channel_id"] == "su_ke_lai"
    assert vault["visual_grammar"] == "su_ke_lai_35mm_live_action_v3"

    # 6 Faction Visual Style Locks
    factions = vault["faction_style_locks"]
    assert set(factions.keys()) == set(VALID_FACTIONS)
    for fac_id, fac in factions.items():
        assert fac["faction_id"] == fac_id
        assert fac["armor_and_wardrobe_lock"]
        assert fac["weapons_and_vessels_lock"]
        assert fac["banners_and_insignia_lock"]
        assert len(fac["anti_anachronism_bans"]) >= 3
        assert not re.search(r"[\u4e00-\u9fff]", json.dumps(fac, ensure_ascii=False))

    # 21 Historical Characters (14 Đại Việt + 7 Opposing Commanders)
    chars = vault["characters"]
    assert len(chars) >= 20
    by_id = {c["character_id"]: c for c in chars}
    assert EXPECTED_DAI_VIET_HEROES.issubset(by_id.keys())
    assert EXPECTED_OPPOSING_COMMANDERS.issubset(by_id.keys())

    hex_re = re.compile(r"^#[0-9A-Fa-f]{6}$")
    for cid, prof in by_id.items():
        for req_key in REQUIRED_CHARACTER_FIELDS:
            assert req_key in prof, f"{cid} missing {req_key}"
            assert prof[req_key] not in (None, "", []), f"{cid} has empty {req_key}"

        assert prof["faction"] in VALID_FACTIONS
        if cid in EXPECTED_DAI_VIET_HEROES:
            assert prof["faction"] == "dai_viet"
        else:
            assert prof["faction"] != "dai_viet"

        pal = prof["lighting_and_color_palette"]
        assert hex_re.match(pal["primary_hex"])
        assert hex_re.match(pal["accent_hex"])
        assert pal["lighting_key"]

        # Benign face DNA check: zero celebrity likeness triggers, zero CJK glyphs.
        face_low = prof["face_and_age_dna"].lower()
        assert "zero celebrity likeness" in face_low
        assert "resembling" not in face_low
        assert "looks like" not in face_low
        assert not re.search(r"[\u4e00-\u9fff]", prof["face_and_age_dna"])
        assert not re.search(r"[\u4e00-\u9fff]", prof["armor_and_wardrobe_lock"])
        assert "dense battlefield mist" not in prof["armor_and_wardrobe_lock"].lower()

        # Verify linked sample_frame_relpath points to a real rendered PNG on disk.
        rel = prof["sample_frame_relpath"]
        assert rel.startswith("video/vn_su_ke_lai_") and rel.endswith(".png")
        assert (ROOT_DIR / rel).is_file(), f"Missing frame on disk for {cid}: {rel}"
        assert prof["sample_frame_exists"] is True
        assert prof["portrait_url"] == f"/media/{rel}"

    # 8 Reusable Dynasty Set / Location Archetypes
    sets = vault["sets"]
    assert len(sets) == 8
    set_ids = {s["set_id"] for s in sets}
    assert len(set_ids) == 8
    for st in sets:
        assert st["location_id"] == st["set_id"]
        assert st["terrain_and_architecture_dna"]
        assert st["atmosphere_lock"]
        assert len(st["recommended_lens_pairings"]) >= 3
        assert "dense battlefield mist" not in st["atmosphere_lock"].lower()
        assert (ROOT_DIR / st["sample_frame_relpath"]).is_file()
        assert st["sample_frame_exists"] is True


def test_save_character_profile_create_update_and_sanitization(tmp_path: Path) -> None:
    src_vault = get_vault_path("su_ke_lai")
    temp_vault = tmp_path / "character_vault.json"
    shutil.copy2(src_vault, temp_vault)

    # Create new character profile with accidental celebrity trigger & CJK glyph -> sanitized cleanly.
    created = save_character_profile(
        {
            "name_vi": "Trần Nhật Duật",
            "aliases": ["Chiêu Văn Vương", "Tran Nhat Duat"],
            "dynasty_era": "Nhà Trần (1285)",
            "years_active": "1285–1288",
            "faction": "dai_viet",
            "role_archetype": "Chiêu Văn Vương Đa Ngôn Ngữ · Danh Tướng Hàm Tử 1285",
            "face_and_age_dna": "A calm 30-year-old Đại Việt prince resembling Donnie Yen with sharp dark eyes and closed lips.",
            "armor_and_wardrobe_lock": "13th-century Trần bronze将军 lamellar armor over indigo silk robe amidst dense battlefield mist.",
        },
        vault_path=temp_vault,
    )
    assert created["character_id"] == "tran_nhat_duat"
    assert "donnie yen" not in created["face_and_age_dna"].lower()
    assert "zero celebrity likeness" in created["face_and_age_dna"].lower()
    assert not re.search(r"[\u4e00-\u9fff]", created["armor_and_wardrobe_lock"])
    assert "dense battlefield mist" not in created["armor_and_wardrobe_lock"].lower()
    assert "Trần Nhật Duật" in created["aliases"]
    assert "Chiêu Văn Vương" in created["aliases"]

    # Partial update preserves untouched fields while updating patched fields.
    updated = save_character_profile(
        {
            "character_id": "tran_nhat_duat",
            "voice_and_persona_note_vi": "Uyên bác, am hiểu ngoại giao và binh pháp đường sông Hàm Tử.",
        },
        vault_path=temp_vault,
    )
    assert updated["voice_and_persona_note_vi"].startswith("Uyên bác")
    assert "Chiêu Văn Vương" in updated["aliases"]

    reloaded = load_character_vault(vault_path=temp_vault)
    reloaded_ids = [c["character_id"] for c in reloaded["characters"]]
    assert "tran_nhat_duat" in reloaded_ids

    with pytest.raises(ValueError, match="Unsupported faction"):
        save_character_profile({"name_vi": "Test", "faction": "roman_empire"}, vault_path=temp_vault)

    with pytest.raises(ValueError, match="character_id"):
        save_character_profile({"character_id": "", "name_vi": ""}, vault_path=temp_vault)


def test_detect_episode_cast_and_sets_on_real_v7_and_v6_specs() -> None:
    v7_path = ROOT_DIR / "video" / "vn_su_ke_lai_v7_bach_dang_1288_short" / "short_spec.json"
    v7_spec = json.loads(v7_path.read_text(encoding="utf-8"))
    det_v7 = detect_episode_cast_and_sets(v7_spec)

    assert {"o_ma_nhi", "tran_khanh_du", "thoat_hoan", "tran_hung_dao"}.issubset(set(det_v7["character_ids"]))
    assert "bach_dang_tidal_estuary" in det_v7["set_ids"]
    assert "van_don_coastal_supply_strait" in det_v7["set_ids"]
    assert {"mongol_yuan", "dai_viet"}.issubset(set(det_v7["factions"]))

    # Beat B00 features Ô Mã Nhi on the Bạch Đằng prow; Beat B03 features Vân Đồn supply fire; Beat B07 features Trần Quốc Tuấn.
    b00 = det_v7["beats"][0]
    b03 = det_v7["beats"][3]
    b07 = det_v7["beats"][7]
    assert "o_ma_nhi" in b00["character_ids"]
    assert b00["set_id"] == "bach_dang_tidal_estuary"
    assert "tran_khanh_du" in b03["character_ids"]
    assert b03["set_id"] == "van_don_coastal_supply_strait"
    assert b03["visual_character_ids"] == []  # person_count == 0 ship-fire scene
    assert "tran_hung_dao" in b07["character_ids"]
    assert "tran_hung_dao" in b07["visual_character_ids"]

    v6_path = ROOT_DIR / "video" / "vn_su_ke_lai_v6_prestige_ung_chau_1075_short" / "short_spec.json"
    v6_spec = json.loads(v6_path.read_text(encoding="utf-8"))
    det_v6 = detect_episode_cast_and_sets(v6_spec)
    assert {"ly_thuong_kiet", "to_giam"}.issubset(set(det_v6["character_ids"]))
    assert "ung_chau_stone_siege_fortress" in det_v6["set_ids"]


def test_apply_cast_continuity_to_spec_idempotency_anchor_dag_and_clean_frame() -> None:
    raw_spec = {
        "job_id": "vn_su_ke_lai_v7_chi_lang_1427_test_short",
        "channel_id": "su_ke_lai",
        "youtube_title": "Ải Chi Lăng 1427: Mưu Lê Lợi & Nguyễn Trãi Chém Liễu Thăng",
        "beats": [
            {
                "beat_index": 0,
                "beat_id": "B00",
                "person_count": 1,
                "allowed_text": "ACCIDENTAL_TEXT_MUST_BE_CLEARED",
                "location": "Narrow rocky throat of Chi Lăng Pass",
                "hero_subject": "General Liễu Thăng resembling Jet Li charging on horseback through dense battlefield mist",
                "narration": "Vì sao An Viễn Hầu Liễu Thăng dẫn 100 kỵ binh lao thẳng vào ải Chi Lăng?",
                "prompt": "",
            },
            {
                "beat_index": 1,
                "beat_id": "B01",
                "person_count": 2,
                "location": "Open timber pavilion at Lam Sơn headquarters",
                "hero_subject": "Bình Định Vương Lê Lợi standing beside Ức Trai inspecting bamboo terrain rods",
                "narration": "Lê Lợi và Nguyễn Trãi chọn kế vây thành diệt viện.",
                "prompt": "Bình Định Vương Lê Lợi standing beside Ức Trai inside timber pavilion.",
            },
            {
                "beat_index": 2,
                "beat_id": "B02",
                "person_count": 0,
                "location": "Deceptive marsh reeds at the foot of Mã Yên mountain",
                "hero_subject": "submerged rows of black bog mud beneath golden-green reeds at Mã Yên",
                "narration": "Đầm lầy Mã Yên chờ sẵn kỵ binh của Liễu Thăng.",
                "prompt": "Wide shot of Mã Yên marsh reeds and black mud.",
            },
            {
                "beat_index": 3,
                "beat_id": "B03",
                "person_count": 1,
                "location": "Muddy creek bridge at Mã Yên",
                "hero_subject": "Liễu Thăng trapped in deep black marsh mud on his warhorse",
                "narration": "Ngựa Liễu Thăng sụp lầy tại chân núi Mã Yên.",
                "prompt": "Liễu Thăng on warhorse sinking into Mã Yên bog.",
            },
            {
                "beat_index": 4,
                "beat_id": "B04",
                "person_count": 1,
                "location": "Southern throat of Chi Lăng gorge",
                "hero_subject": "disarmed Ming general Liễu Thăng surrounded in marsh reeds",
                "narration": "Chủ tướng Liễu Thăng gục ngã giữa vòng vây Chi Lăng.",
                "prompt": "Liễu Thăng surrounded in Chi Lăng gorge.",
            },
        ],
    }
    orig_snapshot = copy.deepcopy(raw_spec)

    enriched = apply_cast_continuity_to_spec(raw_spec)
    # Input dict must not be mutated in place.
    assert raw_spec == orig_snapshot

    roster_ids = [c["character_id"] for c in enriched["cast_roster"]]
    assert {"lieu_thang", "le_loi", "nguyen_trai"}.issubset(set(roster_ids))
    assert enriched["locations_bible"]
    assert enriched["locations_bible"][0]["location_id"] == "chi_lang_ma_yen_ambush_gorge"

    # Check V7 Studio compatibility fields on cast_roster
    lt_entry = next(c for c in enriched["cast_roster"] if c["character_id"] == "lieu_thang")
    assert lt_entry["wardrobe_lock"] == lt_entry["armor_and_wardrobe_lock"]
    assert lt_entry["face_dna"] == lt_entry["face_and_age_dna"]
    assert lt_entry["role"] == lt_entry["role_archetype"]
    assert len(lt_entry["palette_hex"]) == 2
    assert lt_entry["portrait_url"].startswith("/media/video/")

    beats = enriched["beats"]
    for b in beats:
        assert b["allowed_text"] is None
        assert b["set_id"] == "chi_lang_ma_yen_ambush_gorge"
        assert b["location_id"] == "chi_lang_ma_yen_ambush_gorge"
        assert "jet li" not in b["hero_subject"].lower()
        assert "jet li" not in b["prompt"].lower()
        assert "dense battlefield mist" not in b["hero_subject"].lower()
        assert "no text" in b["prompt"].lower() or "zero text" in b["prompt"].lower()

    # Check wardrobe injection on human beats vs non-human beat B02
    assert "mountain-scale iron armor" in beats[0]["prompt"]
    assert "Lam Sơn" in beats[1]["prompt"]
    assert "person_count" in beats[2] and beats[2]["person_count"] == 0
    assert "mountain-scale iron armor" not in beats[2]["prompt"]

    # Check 1-hop star-flattened reference_scene_ids for Liễu Thăng (B00 -> B03 & B04 both reference ["B00"])
    assert beats[0]["cast_spec"].startswith("NEW: lieu_thang")
    assert beats[3]["reference_scene_ids"] == ["B00"]
    assert beats[4]["reference_scene_ids"] == ["B00"]

    # Strict idempotency when applied a second time
    enriched_twice = apply_cast_continuity_to_spec(enriched)
    assert enriched_twice == enriched


def test_apply_cast_continuity_explicit_character_ids_on_generic_scaffold() -> None:
    scaffold_spec = {
        "job_id": "vn_su_ke_lai_v7_ngoc_hoi_scaffold_short",
        "channel_id": "su_ke_lai",
        "youtube_title": "Đêm Mùng 5 Tết Ngọc Hồi 1789",
        "beats": [
            {
                "beat_index": 0,
                "beat_id": "B00",
                "person_count": 1,
                "location": "Ngọc Hồi winter dawn plain",
                "hero_subject": "towering Vietnamese emperor atop an armored command war elephant",
                "narration": "Rạng sáng mùng 5 Tết, vị hoàng đế cưỡi voi thúc quân xung trận.",
                "prompt": "",
            },
            {
                "beat_index": 1,
                "beat_id": "B01",
                "person_count": 1,
                "location": "Thăng Long headquarters",
                "hero_subject": "complacent enemy commander seated beside lanterns",
                "narration": "Trong khi đó, chủ tướng giặc phương Bắc vẫn chủ quan trong trướng.",
                "prompt": "",
            },
        ],
    }

    applied = apply_cast_continuity_to_spec(scaffold_spec, character_ids=["Nguyễn Huệ", "ton_si_nghi"])
    roster_ids = [c["character_id"] for c in applied["cast_roster"]]
    assert roster_ids == ["quang_trung", "ton_si_nghi"]
    assert applied["beats"][0]["character_ids"] == ["quang_trung"]
    assert applied["beats"][1]["character_ids"] == ["ton_si_nghi"]
    assert "crimson silk war headband" in applied["beats"][0]["prompt"]
    assert "Qianlong-era Qing" in applied["beats"][1]["prompt"]


def test_sanitize_benign_face_dna_helper() -> None:
    dirty = "A fierce general looking like Andy Lau or portrayed by Tony Leung in 鎧甲 armor"
    clean = sanitize_benign_face_dna(dirty)
    assert "andy lau" not in clean.lower()
    assert "tony leung" not in clean.lower()
    assert not re.search(r"[\u4e00-\u9fff]", clean)


@pytest.mark.parametrize(
    ("narration_snippet", "expected_cid"),
    [
        ("Ngô Quyền đóng cọc trên sông Bạch Đằng năm 938.", "ngo_quyen"),
        ("Vạn Thắng Vương Đinh Bộ Lĩnh dẹp loạn 12 sứ quân ở Hoa Lư.", "dinh_bo_linh"),
        ("Hoàng đế Lê Đại Hành đích thân cầm gươm phá Tống năm 981.", "le_hoan"),
        ("Vua Lý Công Uẩn ban Chiếu dời đô ra thành Đại La năm 1010.", "ly_cong_uan"),
        ("Thái úy Lý Thường Kiệt cho đắp núi đất Thổ Sơn hạ thành Ung Châu.", "ly_thuong_kiet"),
        ("Hưng Đạo Đại Vương Trần Quốc Tuấn duyệt binh ở bến Đông Bộ Đầu.", "tran_hung_dao"),
        ("Thượng tướng Trần Quang Khải phản công giải phóng Chương Dương.", "tran_quang_khai"),
        ("Hoài Văn Hầu Trần Quốc Toản bóp nát quả cam bên bến Bình Than.", "tran_quoc_toan"),
        ("Bảo Nghĩa Vương Trần Bình Trọng khẳng khái giữa trướng giặc.", "tran_binh_trong"),
        ("Nhân Huệ Vương Trần Khánh Dư phục kích đốt sạch thuyền lương Vân Đồn.", "tran_khanh_du"),
        ("Bình Định Vương Lê Lợi nếm mật nằm gai mười năm ở Lam Sơn.", "le_loi"),
        ("Danh tướng Lê Lai khoác hoàng bào liều mình cứu chúa ở núi Chí Linh.", "le_lai"),
        ("Quân sư Ức Trai Nguyễn Trãi thảo Bình Ngô Đại Cáo.", "nguyen_trai"),
        ("Bắc Bình Vương Nguyễn Huệ lên ngôi Hoàng đế Quang Trung tại núi Bân.", "quang_trung"),
        ("Thái tử Nam Hán Lưu Hoằng Tháo tử trận giữa bãi cọc Bạch Đằng.", "luu_hoang_thao"),
        ("Đô giám Tô Giám tử thủ thành Ung Châu suốt 42 ngày đêm.", "to_giam"),
        ("Thống soái Quách Quỳ chùn bước trước lũy tre gai sông Như Nguyệt.", "quach_quy"),
        ("Trấn Nam Vương Thoát Hoan rút chạy khỏi Vạn Kiếp.", "thoat_hoan"),
        ("Thủy tướng Ô Mã Nhi sa lưới tại cửa sông Bạch Đằng năm 1288.", "o_ma_nhi"),
        ("An Viễn Hầu Liễu Thăng bị chém gục dưới chân núi Mã Yên.", "lieu_thang"),
        ("Tổng đốc Tôn Sĩ Nghị hoảng loạn tháo chạy qua cầu phao sông Hồng.", "ton_si_nghi"),
    ],
)
def test_all_21_characters_resolve_accurately_from_vietnamese_narration(
    narration_snippet: str,
    expected_cid: str,
) -> None:
    spec = {
        "job_id": f"test_{expected_cid}",
        "channel_id": "su_ke_lai",
        "beats": [
            {
                "beat_index": 0,
                "beat_id": "B00",
                "narration": narration_snippet,
                "hero_subject": "",
                "prompt": "",
            }
        ],
    }
    det = detect_episode_cast_and_sets(spec)
    assert expected_cid in det["character_ids"]
    assert expected_cid in det["beats"][0]["character_ids"]


def test_save_character_profile_auto_discovers_sample_frame_on_disk(tmp_path: Path) -> None:
    temp_vault = tmp_path / "character_vault.json"
    saved = save_character_profile(
        {
            "character_id": "quang_trung_test_auto",
            "name_vi": "Quang Trung",
            "aliases": ["Nguyễn Huệ"],
            "faction": "dai_viet",
        },
        channel_id="su_ke_lai",
        vault_path=temp_vault,
    )
    assert saved["sample_frame_relpath"].startswith("video/vn_su_ke_lai_")
    assert saved["sample_frame_relpath"].endswith(".png")
    assert saved["sample_frame_exists"] is True

