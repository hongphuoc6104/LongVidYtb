#!/usr/bin/env python3
"""Generate YouTube branding assets for all 8 Video Pilot channels.

Generates:
1. avatar_800x800.png: 800x800 px square crop centered on character/focal illustration from endcard_9x16.jpg.
2. banner_2048x1152.png: 2048x1152 px YouTube banner with safe center area 1546x423 derived from endcard_16x9.jpg.
3. watermark_150x150.png: 150x150 px square watermark icon.
4. channel_setup_spec.json: Complete setup configuration for YouTube Studio CDP automation.

Copies all assets to both sys/channels/<channel_id>/assets/ and
/home/hongphuoc6104/Desktop/vp-channels/channel-<slug>/sys/channels/<channel_id>/assets/.
"""
from __future__ import annotations

import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "sys") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "sys"))

from sys.channels.registry import ChannelProfile, channels

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("generate_channel_branding")

CHANNELS_WORKSPACE_BASE = Path("/home/hongphuoc6104/Desktop/vp-channels")

# Safe area constants for YouTube banner (2048 x 1152)
BANNER_W = 2048
BANNER_H = 1152
SAFE_X1 = 251
SAFE_X2 = 1797
SAFE_Y1 = 364
SAFE_Y2 = 788
SAFE_W = SAFE_X2 - SAFE_X1  # 1546
SAFE_H = SAFE_Y2 - SAFE_Y1  # 424

# Channel specific handle candidates
HANDLE_CANDIDATES: Dict[str, List[str]] = {
    "ai_binh_dan": ["@AIBinhDanVN", "@AIBinhDanOfficial", "@KenhAIBinhDan", "@AIBinhDan"],
    "co_the_ke": ["@CoTheKeVN", "@CoTheKeOfficial", "@KenhCoTheKe", "@CoTheKe"],
    "ho_so_ky_la": ["@HoSoKyLaVN", "@HoSoKyLaOfficial", "@KenhHoSoKyLa", "@HoSoKyLa"],
    "nao_luoi": ["@NaoLuoiVN", "@NaoLuoiOfficial", "@KenhNaoLuoi", "@NaoLuoi"],
    "su_ke_lai": ["@SuKeLaiVN", "@SuKeLaiOfficial", "@KenhSuKeLai", "@SuKeLai"],
    "thuong_cho_kheo": ["@ThuongChoKheoVN", "@ThuongChoKheoOfficial", "@KenhThuongChoKheo", "@ThuongChoKheo"],
    "tui_tien": ["@TuiTienBietNoiVN", "@TuiTienVN", "@TuiTienOfficial", "@KenhTuiTien"],
    "ua_sao_vay": ["@UaSaoVayVN", "@UaSaoVayOfficial", "@KenhUaSaoVay", "@UaSaoVay"],
    "luat_ngam": ["@LuatNgamDamDongVN", "@LuatNgamVN", "@KenhLuatNgam", "@LuatNgamDamDong"],
    "ban_do_quyen_luc": ["@BanDoQuyenLucVN", "@BanDoQuyenLucOfficial", "@KenhBanDoQuyenLuc", "@BanDoQuyenLuc"],
    "dia_com": ["@DiaComKhoaHocVN", "@DiaComKhoaHocOfficial", "@KenhDiaComKhoaHoc", "@DiaComKhoaHoc"],
    "luat_doi_thuong": ["@LuatDoiThuongVN", "@LuatDoiThuongOfficial", "@KenhLuatDoiThuong", "@LuatDoiThuong"],
    "banh_rang": ["@BanhRangTheGioiVN", "@BanhRangTheGioiOfficial", "@KenhBanhRangTheGioi", "@BanhRangTheGioi"],
    "vu_tru_ti_hon": ["@VuTruTiHonVN", "@VuTruTiHonOfficial", "@KenhVuTruTiHon", "@VuTruTiHon"],
    "nghe_song_sot": ["@NgheSongSotVN", "@NgheSongSotOfficial", "@KenhNgheSongSot", "@NgheSongSot"],
    "la_ban_hoc_thuat": ["@LaBanHocThuatVN", "@LaBanHocThuatOfficial", "@KenhLaBanHocThuat", "@LaBanHocThuat"],
    "chanh_niem_ke": ["@ChanhNiemKeVN", "@ChanhNiemKeOfficial", "@KenhChanhNiemKe", "@ChanhNiemKe"],
    "loi_sang_soi": ["@LoiSangSoiVN", "@LoiSangSoiOfficial", "@KenhLoiSangSoi", "@LoiSangSoi"],
    "minh_triet_song": ["@MinhTrietSongVN", "@MinhTrietSongOfficial", "@KenhMinhTrietSong", "@MinhTrietSong"],
    "tam_tinh_dem": ["@TamTinhDemVN", "@TamTinhDemOfficial", "@KenhTamTinhDem", "@TamTinhDem"],
    "en_lazy_brain": ["@LazyBrainLab", "@LazyBrainLabHQ", "@LazyBrainDoodle", "@TheLazyBrainLab"],
    "en_crowd_strings": ["@CrowdStrings", "@CrowdStringsHQ", "@CrowdStringsLab", "@TheCrowdStrings"],
    "en_kindred_sketch": ["@KindredSketch", "@KindredSketchHQ", "@KindredDoodle", "@TheKindredSketch"],
    "en_ego_unmasked": ["@EgoUnmasked", "@EgoUnmaskedHQ", "@EgoUnmaskedLab", "@TheEgoUnmasked"],
    "en_first_principles": ["@FirstPrinciplesInk", "@FirstPrinciplesHQ", "@FirstPrinciplesLab", "@MentalModelsInk"],
    "en_wallet_anatomy": ["@WalletAnatomy", "@WalletAnatomyHQ", "@WalletAnatomyLab", "@TheWalletAnatomy"],
    "en_macro_gears": ["@MacroGears", "@MacroGearsHQ", "@MacroGearsLab", "@TheMacroGears"],
    "en_plain_sight_ai": ["@PlainSightAI", "@PlainSightAIHQ", "@PlainSightAILab", "@GetPlainSightAI"],
    "en_career_leverage": ["@CareerLeverage", "@CareerLeverageHQ", "@CareerLeverageLab", "@TheCareerLeverage"],
    "en_fine_print": ["@EverydayFinePrint", "@FinePrintDoodle", "@EverydayFinePrintHQ", "@ReadTheFinePrintLab"],
    "en_inside_vessel": ["@InsideTheVessel", "@InsideTheVesselHQ", "@InsideVesselLab", "@BodyVesselDoodle"],
    "en_kitchen_molecules": ["@KitchenMolecules", "@KitchenMoleculesHQ", "@KitchenScienceInk", "@FoodMoleculesLab"],
    "en_wait_how": ["@WaitHowScience", "@WaitHowDoodle", "@WaitHowExplained", "@WaitHowLab"],
    "en_cold_case_ink": ["@ColdCaseInk", "@ColdCaseInkHQ", "@ColdCaseDoodle", "@UnsolvedInkLab"],
    "en_choke_point": ["@ChokePointMaps", "@ChokePointMapsHQ", "@ChokePointInk", "@StrategicMapsLab"],
    "en_pocket_cosmos": ["@PocketCosmos", "@PocketCosmosHQ", "@PocketCosmosLab", "@TinyCosmosInk"],
    "en_second_arrow": ["@TheSecondArrowZen", "@SecondArrowDoodle", "@SecondArrowMind", "@TheSecondArrowLab"],
    "en_parable_lamp": ["@ParableAndLamp", "@ParableAndLampHQ", "@ParableLampDoodle", "@TheParableLamp"],
    "en_bamboo_marble": ["@BambooAndMarble", "@BambooAndMarbleHQ", "@BambooMarbleInk", "@StoicAndTaoLab"],
}


def build_channel_description(ch: ChannelProfile) -> str:
    """Build natural engaging channel description."""
    tags = " ".join([t if t.startswith("#") else f"#{t}" for t in ch.hashtags])
    if getattr(ch, "language", "vi") == "en":
        desc_lines = [
            f"Welcome to the official {ch.name} channel!",
            "",
            f"{ch.promise}",
            f"Clear, visual, research-backed explainers crafted for {ch.audience.lower()}.",
            "",
            f"Core topics: {ch.niche}.",
            "",
            f"{tags}",
        ]
    else:
        desc_lines = [
            f"Chào mừng bạn đến với kênh chính thức của {ch.name}!",
            "",
            f"{ch.promise}",
            f"Nội dung được thiết kế dễ hiểu, trực quan và hấp dẫn dành riêng cho {ch.audience.lower()}.",
            "",
            f"Chủ đề trọng tâm: {ch.niche}.",
            "",
            f"{tags}",
        ]
    return "\n".join(desc_lines)


def get_background_color(arr: np.ndarray) -> np.ndarray:
    """Estimate solid background color from corners or flat canvas areas."""
    h, w = arr.shape[:2]
    corners = np.array([
        arr[10, 10],
        arr[10, w - 10],
        arr[h - 10, 10],
        arr[h - 10, w - 10],
    ])
    return np.median(corners, axis=0).astype(np.uint8)


def create_avatar(endcard_9x16_path: Path, output_path: Path) -> Path:
    """Create 800x800 square crop centered on the character from 9:16 endcard."""
    im = Image.open(endcard_9x16_path).convert("RGB")
    arr = np.array(im)
    bg = get_background_color(arr)
    diff = np.linalg.norm(arr.astype(float) - bg, axis=2)

    # Focus on character region (below top text, generally y in [600, 1750])
    sub = diff[600:1750, :]
    ys, xs = np.where(sub > 35)

    if len(ys) > 0:
        ymin = ys.min() + 600
        ymax = ys.max() + 600
        xmin = xs.min()
        xmax = xs.max()
        char_cx = (xmin + xmax) // 2
        # Head / upper body focus: center slightly above the full vertical middle
        char_cy = int(ymin + (ymax - ymin) * 0.45)
    else:
        char_cx = im.width // 2
        char_cy = int(im.height * 0.58)

    # Square box size: ~960 px for rich framing
    box_size = 960
    x1 = char_cx - box_size // 2
    y1 = char_cy - box_size // 2

    # Clamp boundaries
    if x1 < 0:
        x1 = 0
    if x1 + box_size > im.width:
        x1 = im.width - box_size
    if y1 < 0:
        y1 = 0
    if y1 + box_size > im.height:
        y1 = im.height - box_size

    crop = im.crop((x1, y1, x1 + box_size, y1 + box_size))
    avatar = crop.resize((800, 800), Image.Resampling.LANCZOS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    avatar.save(output_path, "PNG")
    logger.info("Generated Avatar: %s (crop box: %d,%d to %d,%d)", output_path, x1, y1, x1+box_size, y1+box_size)
    return output_path


def create_banner(endcard_16x9_path: Path, output_path: Path) -> Path:
    """Create 2048x1152 YouTube banner ensuring safe center area (1546x423) looks great."""
    im = Image.open(endcard_16x9_path).convert("RGB")
    arr = np.array(im)

    # Background color estimate from empty right side
    bg = np.median(arr[:, 1400:], axis=(0, 1)).astype(np.uint8)

    # Find the active artwork on left side (x < 1250)
    diff = np.linalg.norm(arr[:, :1250].astype(float) - bg, axis=2)
    ys, xs = np.where(diff > 35)

    canvas = Image.new("RGB", (BANNER_W, BANNER_H), tuple(bg))

    if len(ys) > 0:
        ymin, ymax = ys.min(), ys.max()
        xmin, xmax = xs.min(), xs.max()
        art_w = xmax - xmin
        art_h = ymax - ymin

        # Safe area height is 424 px. Scale artwork to 390 px height so it comfortably fits
        target_h = min(390, SAFE_H - 24)
        scale = target_h / float(art_h)
        target_w = int(art_w * scale)

        artwork = im.crop((xmin, ymin, xmax, ymax))
        artwork_resized = artwork.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # Place artwork inside the safe area
        # X: start at SAFE_X1 + 50 px margin
        paste_x = SAFE_X1 + 50
        # Y: center vertically in safe area
        paste_y = SAFE_Y1 + (SAFE_H - target_h) // 2

        canvas.paste(artwork_resized, (paste_x, paste_y))
    else:
        # Fallback: direct resize
        canvas = im.resize((BANNER_W, BANNER_H), Image.Resampling.LANCZOS)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, "PNG")
    logger.info("Generated Banner: %s", output_path)
    return output_path


def create_watermark(avatar_path: Path, output_path: Path) -> Path:
    """Create 150x150 square watermark icon from avatar."""
    im = Image.open(avatar_path).convert("RGB")
    watermark = im.resize((150, 150), Image.Resampling.LANCZOS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    watermark.save(output_path, "PNG")
    logger.info("Generated Watermark: %s", output_path)
    return output_path


def process_channel(cid: str) -> Dict[str, Any]:
    ch = channels()[cid]
    src_asset_dir = REPO_ROOT / "sys" / "channels" / cid / "assets"
    dest_workspace_dir = CHANNELS_WORKSPACE_BASE / f"channel-{ch.slug}" / "sys" / "channels" / cid / "assets"
    dest_workspace_dir.mkdir(parents=True, exist_ok=True)

    endcard_16x9_path = src_asset_dir / "endcard_16x9.jpg"
    endcard_9x16_path = src_asset_dir / "endcard_9x16.jpg"

    if not endcard_16x9_path.exists() or not endcard_9x16_path.exists():
        raise FileNotFoundError(f"Missing endcards in {src_asset_dir}")

    avatar_path = src_asset_dir / "avatar_800x800.png"
    banner_path = src_asset_dir / "banner_2048x1152.png"
    watermark_path = src_asset_dir / "watermark_150x150.png"
    spec_path = src_asset_dir / "channel_setup_spec.json"

    # Generate assets
    create_avatar(endcard_9x16_path, avatar_path)
    create_banner(endcard_16x9_path, banner_path)
    create_watermark(avatar_path, watermark_path)

    # Build spec
    handles = HANDLE_CANDIDATES.get(cid, [f"@{ch.slug.replace('-', '').capitalize()}VN"])
    description = build_channel_description(ch)
    keywords = list(dict.fromkeys([t.lstrip("#") for t in ch.hashtags] + [ch.niche]))

    spec_data = {
        "channel_id": ch.id,
        "slug": ch.slug,
        "youtube_name": ch.name,
        "handle_candidates": handles,
        "description": description,
        "keywords": keywords,
        "assets": {
            "avatar_800x800": str(avatar_path),
            "banner_2048x1152": str(banner_path),
            "watermark_150x150": str(watermark_path),
            "endcard_16x9": str(endcard_16x9_path),
            "endcard_9x16": str(endcard_9x16_path),
        }
    }
    spec_path.write_text(json.dumps(spec_data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Saved channel setup spec: %s", spec_path)

    # Mirror to workspace
    for filename in ["avatar_800x800.png", "banner_2048x1152.png", "watermark_150x150.png", "channel_setup_spec.json", "endcard_16x9.jpg", "endcard_9x16.jpg"]:
        src_file = src_asset_dir / filename
        dest_file = dest_workspace_dir / filename
        if src_file.exists():
            shutil.copy2(src_file, dest_file)
            logger.info("Mirrored %s -> %s", src_file.name, dest_file)

    return spec_data


def main():
    logger.info("Generating branding assets for all 8 Video Pilot channels...")
    all_specs = {}
    for cid in channels():
        logger.info("=== Processing channel: %s ===", cid)
        spec = process_channel(cid)
        all_specs[cid] = spec

    logger.info("All 8 channel branding assets generated and mirrored successfully!")


if __name__ == "__main__":
    main()
