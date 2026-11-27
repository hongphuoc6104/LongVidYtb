"""Historical Anachronism Sanitizer, Sub-Cut Crop-Safety & 2K Frame Quality Gate.

Enforces production-grade historical visual fidelity across `su_ke_lai` and historical
docudrama pipelines (`sys/channels/su_ke_lai/playbook/visual.md`, `PLAYBOOK.md`
`ERR-20261031-01`, `ERR-20261109-02`, `ERR-20261030-01`, `ERR-20261122-01`):

1. `audit_and_sanitize_historical_prompt`:
   - Detects & strips 60+ anachronistic tokens (Japanese samurai/katana/kabuto,
     European plate/knight/viking/horned helmet, firearms/musket/cannon before 1400,
     Qing queue/Manchu attire outside 1788-1789 Qing forces, blanket fog/mist white-outs,
     modern/sci-fi/fantasy slop, raw story-frame text requests when `is_thumbnail=False`,
     and living/celebrity actor names triggering Flow `PROMINENT_PEOPLE` blocks).
   - Injects period-accurate positive armor, weapon, and clear-air 35mm optical anchors
     when missing.
2. `audit_sub_cut_crop_geometry`:
   - Computes exact visible crop rectangle `[x0, y0, x1, y1]` for `1.25x..1.40x` sub-cuts
     and auto-corrects `(focus_cx, focus_cy)` so the upper head zone (`0.18..0.46` height)
     is never severed while avoiding collision with the `MarginV=660` subtitle band.
3. `audit_rendered_2k_frame`:
   - Uses `numpy`/`PIL` to verify resolution, file size (`< 2MB` strict gate when
     `is_thumbnail=True`), dynamic range (`p95 - p5 >= 85.0`), black-crush & overexposure
     clipping %, edge sharpness (`Laplacian` variance), and bottom-right `W-w-36:H-h-36`
     watermark + `MarginV=660` subtitle readability contrast.
4. `audit_full_episode_visual_readiness`:
   - Runs prompt + crop + rendered-frame + thumbnail QC across an entire Short or Long
     episode spec directory or spec JSON file.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

# ---------------------------------------------------------------------------
# Constants & Canonical Thresholds
# ---------------------------------------------------------------------------

SUBCUT_MIN_ZOOM: float = 1.25
SUBCUT_MAX_ZOOM: float = 1.40
V7_SUBCUT_PUSH_IN_FACTOR: float = 1.04

# Normalized primary-subject head safe-zone (ERR-20261031-01 & Short V7 framing)
HEAD_ZONE_Y_MIN: float = 0.18
HEAD_ZONE_Y_MAX: float = 0.46
HEAD_TOP_SAFETY_MARGIN: float = 0.015
HEAD_BOTTOM_SAFETY_MARGIN: float = 0.02

# Horizontal safe pivot bounds matching render_single_pass.py
FOCUS_CX_MIN: float = 0.22
FOCUS_CX_MAX: float = 0.78
FOCUS_CY_FLOOR: float = 0.20

# Subtitle band height fraction (~2 lines of 118px ExtraBold + 10px outline + clearance on 2560p)
SUBTITLE_BAND_HEIGHT_NORM: float = 0.115
CANONICAL_SHORT_HEIGHT: int = 2560
DEFAULT_SUBTITLE_MARGIN_V: int = 660

# Rendered 2K / HD Frame & Thumbnail QC Gates
MAX_THUMBNAIL_BYTES: int = 2 * 1024 * 1024  # Strict < 2MB gate (ERR-20261030-01)
MIN_LONG_EDGE_PX: int = 1280
MIN_SHORT_EDGE_PX: int = 720
MIN_DYNAMIC_RANGE_P95_P5: float = 85.0
MAX_BLACK_CRUSH_PCT: float = 45.0
MAX_OVEREXPOSURE_PCT: float = 25.0
MIN_LAPLACIAN_VARIANCE: float = 25.0
MAX_SUBTITLE_GLARE_PCT: float = 60.0
MIN_EFFECTIVE_SUBTITLE_CONTRAST: float = 4.5

CLEAR_AIR_OPTICAL_LOCK: str = (
    "Shot on 35mm Kodak Vision3 500T film, historical battle cinema docudrama, "
    "crisp optical clarity, deep-focus 35mm anamorphic depth, dramatic directional "
    "sunlight or warm Caravaggio torchlight chiaroscuro, rich tactile armor and terrain detail"
)
CLEAN_FRAME_NO_TEXT_LOCK: str = "no text, no captions, no watermarks, no UI overlays"


# ---------------------------------------------------------------------------
# Dynasty / Era & Faction Resolution
# ---------------------------------------------------------------------------

def _strip_diacritics(text: str) -> str:
    norm = unicodedata.normalize("NFD", text or "")
    stripped = "".join(ch for ch in norm if unicodedata.category(ch) != "Mn")
    return stripped.replace("đ", "d").replace("Đ", "D")


ERA_DEFINITIONS: tuple[tuple[str, tuple[str, ...], int, int, int], ...] = (
    # (era_id, keyword_aliases_ascii, start_year, end_year, representative_year)
    ("early_pre_938", ("hai ba trung", "ba trieu", "ly nam de", "van xuan", "au lac", "dong son", "hung vuong", "mai hac de", "phung hung"), 40, 937, 544),
    ("ngo_dinh_tien_le", ("nha ngo", "ngo quyen", "nha dinh", "dinh bo linh", "dai co viet", "tien le", "le hoan", "12 su quan"), 938, 1009, 968),
    ("ly", ("nha ly", "trieu ly", "ly thai to", "ly thuong kiet", "nhu nguyet", "ung chau", "chieu doi do"), 1009, 1225, 1077),
    ("tran", ("nha tran", "trieu tran", "tran hung dao", "tran quoc tuan", "dien hong", "binh than", "nguyen mong", "van don"), 1225, 1399, 1288),
    ("ho", ("nha ho", "trieu ho", "ho quy ly", "ho nguyen trung", "sung than co", "da bang", "hoa khi"), 1400, 1407, 1402),
    ("le_so", ("le so", "lam son", "le loi", "nguyen trai", "chi lang", "xuong giang", "dong quan", "le thanh tong", "le chi vien", "hau le"), 1418, 1527, 1427),
    ("mac_trinh_nguyen", ("nha mac", "trinh nguyen", "le trung hung", "dang trong", "dang ngoai", "luy thay"), 1527, 1770, 1627),
    ("tay_son", ("tay son", "quang trung", "nguyen hue", "ngoc hoi", "dong da", "rach gam", "xoai mut", "tam diep", "ha hoi"), 1771, 1802, 1789),
    ("nguyen", ("nha nguyen", "trieu nguyen", "gia long", "minh mang", "tu duc", "can vuong", "da nang 1858"), 1802, 1888, 1858),
)


def resolve_dynasty_era(dynasty_era: str) -> dict[str, Any]:
    """Normalize arbitrary `dynasty_era` strings into canonical era metadata and year."""
    raw = (dynasty_era or "").strip()
    ascii_l = _strip_diacritics(raw).lower()
    ascii_clean = re.sub(r"[_\-/]+", " ", ascii_l)

    # 1. Extract explicit 3- or 4-digit historical calendar year if present
    #    (exclude duration/quantity phrases like '1000 nam', '1000 years', '600 thuyen', '400 chiec')
    explicit_year: int | None = None
    unit_suffix = r"(?:\s*(?:nam|years?|yr|km|met|meters?|nguoi|van|thuyen|chiec|quan|voi|dai\s*bac|buoc|ngay|gio))\b"
    for m in re.finditer(rf"\b(9\d{{2}}|1[0-8]\d{{2}}|[1-8]\d{{2}})\b(?!{unit_suffix})", ascii_clean):
        yr = int(m.group(1))
        if 40 <= yr <= 1900:
            explicit_year = yr
            break

    # 2. Match explicit dynasty/campaign keywords first
    matched_era: str | None = None
    default_yr = 1077
    for era_id, aliases, _y_start, _y_end, rep_yr in ERA_DEFINITIONS:
        if era_id == ascii_l.replace(" ", "_") or any(alias in ascii_clean for alias in aliases):
            matched_era = era_id
            default_yr = rep_yr
            break

    # Short single-token dynasty names ("ngo", "dinh", "ly", "tran", "ho", "le", "nguyen")
    tokens = set(ascii_clean.split())
    if matched_era is None:
        if tokens & {"ngo", "dinh"}:
            matched_era, default_yr = "ngo_dinh_tien_le", 968
        elif "ly" in tokens:
            matched_era, default_yr = "ly", 1077
        elif "tran" in tokens:
            matched_era, default_yr = "tran", 1288
        elif "ho" in tokens:
            matched_era, default_yr = "ho", 1402
        elif "le" in tokens:
            matched_era, default_yr = "le_so", 1427
        elif "mac" in tokens or "trinh" in tokens:
            matched_era, default_yr = "mac_trinh_nguyen", 1627
        elif "qing" in tokens:
            matched_era, default_yr = "tay_son", 1789
        elif "nguyen" in tokens:
            matched_era, default_yr = "nguyen", 1858

    # 3. Century fallback (e.g. "10th century", "13th_century", "the ky 15")
    if explicit_year is None and matched_era is None:
        cm = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\s*century\b|\bthe\s*ky\s*(\d{1,2})\b", ascii_clean)
        if cm:
            cent = int(cm.group(1) or cm.group(2))
            explicit_year = cent * 100 - 50

    year = explicit_year if explicit_year is not None else default_yr

    if matched_era is None:
        for era_id, _aliases, y_start, y_end, _rep in ERA_DEFINITIONS:
            if y_start <= year <= y_end:
                matched_era = era_id
                break
    if matched_era is None:
        matched_era = "ly" if year < 1225 else ("tran" if year < 1400 else "le_so")

    return {
        "era_id": matched_era,
        "year": year,
        "AllowsEarlyGunpowder1400": year >= 1400,
        "AllowsMatchlock1520": year >= 1520,
        "AllowsFlintlock1650": year >= 1650,
    }


def normalize_faction(faction: str) -> str:
    """Normalize faction identifier into canonical historical force key."""
    f = _strip_diacritics(faction or "dai_viet").lower().strip()
    f = re.sub(r"[\s\-]+", "_", f)
    if any(k in f for k in ("qing", "manchu", "nha_thanh", "quan_thanh", "ton_si_nghi")):
        return "qing"
    if any(k in f for k in ("song", "bac_tong", "tong")):
        return "northern_song"
    if any(k in f for k in ("yuan", "mongol", "nguyen_mong", "o_ma_nhi", "thoat_hoan")):
        return "yuan_mongol"
    if any(k in f for k in ("ming", "nha_minh", "quan_minh", "vuong_thong", "lieu_thang")):
        return "ming"
    if any(k in f for k in ("siam", "xiem", "quan_xiem")):
        return "siam"
    if any(k in f for k in ("cham", "champa", "chiampa")):
        return "champa"
    if any(k in f for k in ("nam_han", "southern_han", "tang", "nha_duong", "dong_han", "han")):
        return "northern_imperial_early"
    return "dai_viet"


# ---------------------------------------------------------------------------
# Period-Accurate Positive Armor & Weapon Vocabulary
# ---------------------------------------------------------------------------

POSITIVE_ANCHOR_KEYWORDS: tuple[str, ...] = (
    "lamellar",
    "laminar",
    "shanwenjia",
    "lacquered leather",
    "iron scale",
    "scale cuirass",
    "brigandine",
    "giao linh",
    "giao lĩnh",
    "o sa",
    "court robe",
    "cross-collar",
    "hemp tunic",
    "ramie tunic",
    "ramie tunics",
    "silk war tunic",
    "imperial war coat",
    "rattan shield",
    "wooden shield",
    "straw shield",
    "ironwood stake",
    "river stake",
    "bamboo spear",
    "hardwood spear",
    "single-edged saber",
    "straight steel sword",
    "crossbow",
    "song halberd",
    "war junk",
    "river galley",
    "war galley",
    "war elephant",
    "bronze cannon",
    "swivel cannon",
    "sung than co",
    "súng thần cơ",
    "hoa ho",
    "hỏa hổ",
    "dong son",
    "đông sơn",
)

PERIOD_POSITIVE_ANCHORS: dict[tuple[str, str], str] = {
    ("early_pre_938", "dai_viet"): (
        "period-accurate early Vietnamese Đông Sơn and Vạn Xuân bronze-and-lacquered leather chest armor, "
        "indigo-dyed hemp cross-collar tunics, bronze-tipped spears, woven rattan shields, and war elephants"
    ),
    ("ngo_dinh_tien_le", "dai_viet"): (
        "period-accurate 10th-century Đại Cồ Việt lacquered dark-brown leather and iron lamellar cuirass, "
        "coarse hemp cross-collar battle tunics, conical rattan-and-iron helmets, iron-tipped hardwood spears, "
        "woven rattan shields, and sharpened ironwood river stakes"
    ),
    ("ly", "dai_viet"): (
        "period-accurate 11th-century Lý Dynasty Đại Việt lacquered leather and iron lamellar armor (giáp vảy), "
        "indigo and crimson cross-collar tunics, shallow-domed lacquered helmets, curved single-edged sabers, "
        "bamboo crossbows, and rattan shields"
    ),
    ("ly", "northern_song"): (
        "period-accurate 11th-century Northern Song Dynasty iron laminar armor (shanwenjia) over crimson padded "
        "gambesons, iron-rimmed round helmets with neck guards, long-shafted Song halberds, and wooden tower shields"
    ),
    ("tran", "dai_viet"): (
        "period-accurate 13th-century Trần Dynasty Đại Việt dark bronze-and-lacquered lamellar cuirass, "
        "crimson and indigo cross-collar war tunics, cloth-wrapped shins, single-edged sabers, iron-tipped spears, "
        "wooden crossbows, and charred ironwood river stakes"
    ),
    ("tran", "yuan_mongol"): (
        "period-accurate 13th-century Yuan-Mongol heavy iron lamellar armor over thick leather coats, "
        "conical iron helmets with leather neck flaps, composite recurve bows, and dark-timber war junks"
    ),
    ("ho", "dai_viet"): (
        "period-accurate early 15th-century Hồ Dynasty Đại Việt iron-studded brigandine and lamellar armor, "
        "stone citadel ramparts, heavy cast-bronze Súng Thần Cơ early gunpowder cannons, and hardwood polearms"
    ),
    ("le_so", "dai_viet"): (
        "period-accurate 15th-century Lam Sơn and Lê Sơ Đại Việt lacquered iron lamellar and brigandine armor, "
        "indigo-and-crimson cross-collar tunics, single-edged sabers, heavy crossbows, and bamboo shields"
    ),
    ("le_so", "ming"): (
        "period-accurate 15th-century Ming Dynasty iron brigandine coats with brass studs, flared iron helmets "
        "with red horsehair plumes, polearms, and heavy supply wagons"
    ),
    ("mac_trinh_nguyen", "dai_viet"): (
        "period-accurate 17th-century Đại Việt lacquered leather and iron-plate brigandine armor, "
        "cross-collar tunics, matchlock firearms, bronze cannons, and wooden war galleys"
    ),
    ("tay_son", "dai_viet"): (
        "period-accurate late 18th-century Tây Sơn Đại Việt crimson cloth war tunics and lacquered leather cuirasses, "
        "red cloth headscarves and conical rattan helmets, wet-straw shields, Hỏa Hổ fire-tubes, bronze cannons, and war elephants"
    ),
    ("tay_son", "qing"): (
        "period-accurate 1789 Qing Dynasty Eight Banners studded cotton-and-iron brigandine coats (dingjia), "
        "conical rattan and iron helmets with red tassels, shaved-forehead Manchu queues, dao sabers, and matchlocks"
    ),
    ("nguyen", "dai_viet"): (
        "period-accurate 19th-century Nguyễn Dynasty Đại Việt crimson-and-indigo military tunics, "
        "lacquered rattan helmets, earthen Vauban-style ramparts, cast-bronze cannons, and hardwood spears"
    ),
}


def _select_positive_anchor(era_id: str, norm_faction: str) -> str:
    if (era_id, norm_faction) in PERIOD_POSITIVE_ANCHORS:
        return PERIOD_POSITIVE_ANCHORS[(era_id, norm_faction)]
    if norm_faction == "northern_song":
        return PERIOD_POSITIVE_ANCHORS[("ly", "northern_song")]
    if norm_faction == "yuan_mongol":
        return PERIOD_POSITIVE_ANCHORS[("tran", "yuan_mongol")]
    if norm_faction == "ming":
        return PERIOD_POSITIVE_ANCHORS[("le_so", "ming")]
    if norm_faction == "qing":
        return PERIOD_POSITIVE_ANCHORS[("tay_son", "qing")]
    return PERIOD_POSITIVE_ANCHORS.get((era_id, "dai_viet"), PERIOD_POSITIVE_ANCHORS[("tran", "dai_viet")])


# ---------------------------------------------------------------------------
# 60+ Historical Anachronism, Fog, Text & Prominent-People Rule Catalog
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AnachronismRule:
    """Single anti-anachronism / anti-fog / Flow-policy sanitization rule."""

    token_id: str
    category: str
    pattern: re.Pattern[str]
    condition: str  # 'always', 'pre_1400', 'pre_1600', 'non_qing_1789', 'story_frame_only'
    replacement: str
    reason: str


def _compile_word(expr: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![A-Za-z0-9_])(?:{expr})(?![A-Za-z0-9_])", re.IGNORECASE)


HISTORICAL_ANACHRONISM_CATALOG: tuple[AnachronismRule, ...] = (
    # --- Category 1: Japanese Samurai / Sengoku Slop (12 rules) ---
    AnachronismRule("katana", "japanese_anachronism", _compile_word(r"katanas?"), "always", "curved single-edged saber", "Japanese katana is anachronistic in Vietnamese/Chinese history"),
    AnachronismRule("kabuto", "japanese_anachronism", _compile_word(r"kabuto(?:\s+helmets?)?"), "always", "lacquered iron helmet", "Japanese kabuto helmet is anachronistic"),
    AnachronismRule("samurai", "japanese_anachronism", _compile_word(r"samurais?"), "always", "armored Đại Việt warrior", "Japanese samurai is anachronistic"),
    AnachronismRule("wakizashi", "japanese_anachronism", _compile_word(r"wakizashis?"), "always", "short single-edged blade", "Japanese wakizashi is anachronistic"),
    AnachronismRule("nodachi", "japanese_anachronism", _compile_word(r"nodachis?|odachis?"), "always", "long-hafted pole-blade", "Japanese nodachi is anachronistic"),
    AnachronismRule("naginata", "japanese_anachronism", _compile_word(r"naginatas?"), "always", "long-shafted polearm", "Japanese naginata is anachronistic"),
    AnachronismRule("mempo", "japanese_anachronism", _compile_word(r"me[mn]po(?:\s+masks?)?"), "always", "", "Japanese samurai mempo mask is anachronistic"),
    AnachronismRule("o_yoroi", "japanese_anachronism", _compile_word(r"o[- ]yoroi|do[- ]maru"), "always", "lacquered lamellar cuirass", "Japanese o-yoroi/do-maru armor is anachronistic"),
    AnachronismRule("kusazuri", "japanese_anachronism", _compile_word(r"kusazuri|sode\s+shoulder\s+plates?"), "always", "laced lamellar skirt plates", "Japanese kusazuri/sode terms are anachronistic"),
    AnachronismRule("shogun", "japanese_anachronism", _compile_word(r"shoguns?|daimyos?"), "always", "imperial commander", "Japanese shogun/daimyo title is anachronistic"),
    AnachronismRule("ronin", "japanese_anachronism", _compile_word(r"ronins?|ashigarus?"), "always", "vanguard foot soldier", "Japanese ronin/ashigaru is anachronistic"),
    AnachronismRule("ninja", "japanese_anachronism", _compile_word(r"ninjas?|shinobis?|shurikens?"), "always", "night scout", "Japanese ninja/shinobi trope is anachronistic"),

    # --- Category 2: European Medieval / Classical / Viking Slop (15 rules) ---
    AnachronismRule("viking", "european_anachronism", _compile_word(r"vikings?|norse\s+warriors?"), "always", "riverine warrior", "Scandinavian Viking is anachronistic"),
    AnachronismRule("horned_helmet", "european_anachronism", _compile_word(r"(?:horned|winged)\s+helmets?"), "always", "conical lacquered iron helmet", "Horned/winged fantasy helmet is anachronistic"),
    AnachronismRule("european_plate", "european_anachronism", _compile_word(r"european\s+plate(?:\s+armou?r)?|full\s+plate\s+armou?r|plate\s+mail|gothic\s+plate|suits?\s+of\s+armou?r"), "always", "lacquered leather and iron lamellar armor", "European plate armor is anachronistic"),
    AnachronismRule("plate_armor", "european_anachronism", _compile_word(r"plate\s+armou?r"), "always", "iron lamellar armor", "Plate armor triggers Western medieval knight armor"),
    AnachronismRule("knight", "european_anachronism", _compile_word(r"(?:medieval\s+)?knights?"), "always", "armored cavalryman", "European medieval knight is anachronistic"),
    AnachronismRule("crusader", "european_anachronism", _compile_word(r"crusaders?|templars?|teutonic|paladins?"), "always", "vanguard soldier", "Crusader/Templar imagery is anachronistic"),
    AnachronismRule("great_helm", "european_anachronism", _compile_word(r"great\s+helms?|bascinets?|sallets?|armets?|visored\s+helms?"), "always", "shallow-domed iron helmet", "European visored helmet is anachronistic"),
    AnachronismRule("chainmail_coif", "european_anachronism", _compile_word(r"chain\s*mail(?:\s+coifs?|\s+hauberks?)?|hauberks?"), "always", "lacquered lamellar tunic", "European chainmail coif/hauberk is anachronistic"),
    AnachronismRule("claymore", "european_anachronism", _compile_word(r"claymores?|zweihanders?|flamberges?|rapiers?"), "always", "single-edged saber", "European sword type is anachronistic"),
    AnachronismRule("broadsword", "european_anachronism", _compile_word(r"european\s+broadswords?|longswords?"), "always", "straight iron sword", "European longsword is anachronistic"),
    AnachronismRule("roman_legion", "european_anachronism", _compile_word(r"roman\s+legion(?:aries|s)?|centurions?|gladius|lorica\s+segmentata|scutum"), "always", "imperial infantry", "Roman legionary gear is anachronistic"),
    AnachronismRule("spartan", "european_anachronism", _compile_word(r"spartans?|hoplites?|corinthian\s+helmets?"), "always", "spearman", "Greek Spartan/hoplite gear is anachronistic"),
    AnachronismRule("gothic_castle", "european_anachronism", _compile_word(r"gothic\s+castles?|european\s+stone\s+keeps?|medieval\s+drawbridges?"), "always", "earthen-and-laterite citadel ramparts", "European gothic castle architecture is anachronistic"),
    AnachronismRule("heater_shield", "european_anachronism", _compile_word(r"heater\s+shields?|kite\s+shields?"), "always", "woven rattan shield", "European heater/kite shield is anachronistic"),
    AnachronismRule("lance_jousting", "european_anachronism", _compile_word(r"jousting\s+lances?"), "always", "iron-tipped hardwood spear", "European jousting lance is anachronistic"),

    # --- Category 3: Era-Gated Firearms & Gunpowder Weapons (8 rules) ---
    AnachronismRule("musket", "firearm_anachronism", _compile_word(r"muskets?|musketeers?"), "pre_1400", "wooden crossbows", "Muskets did not exist before 1400"),
    AnachronismRule("arquebus", "firearm_anachronism", _compile_word(r"arquebus(?:es)?|matchlocks?|blunderbuss(?:es)?"), "pre_1400", "bamboo crossbows", "Matchlock/arquebus firearms did not exist before 1400"),
    AnachronismRule("flintlock", "firearm_anachronism", _compile_word(r"flintlocks?|wheellocks?|pistols?"), "pre_1600", "crossbows", "Flintlock/wheellock firearms are anachronistic before 1600"),
    AnachronismRule("cannon_pre1400", "firearm_anachronism", _compile_word(r"cannons?|culverins?|bombards?|howitzers?|field\s+artillery"), "pre_1400", "counterweighted trebuchets", "Gunpowder cannons are anachronistic in pre-1400 Đại Việt campaigns"),
    AnachronismRule("modern_rifle", "modern_anachronism", _compile_word(r"assault\s+rifles?|rifles?|carbines?|revolvers?|shotguns?|bayonets?"), "always", "iron-tipped spears", "Modern rifled firearms are anachronistic in pre-modern dynasties"),
    AnachronismRule("automatic_weapon", "modern_anachronism", _compile_word(r"machine\s+guns?|ak[- ]?47|gatling\s+guns?|submachine\s+guns?|sniper\s+rifles?"), "always", "crossbows", "Modern automatic weapons are anachronistic"),
    AnachronismRule("modern_explosives", "modern_anachronism", _compile_word(r"hand\s+grenades?|rocket\s+launchers?|bazookas?|dynamite|landmines?"), "always", "bamboo fire-rafts", "Modern explosives are anachronistic"),
    AnachronismRule("modern_tank_aircraft", "modern_anachronism", _compile_word(r"armored\s+tanks?|helicopters?|fighter\s+jets?|battleships?|submarines?"), "always", "wooden war galleys", "Modern vehicles are anachronistic"),

    # --- Category 4: Qing / Manchu Queue & Attire Outside 1788-1789 Qing Forces (5 rules) ---
    AnachronismRule("qing_queue", "qing_anachronism", _compile_word(r"qing\s+queues?|manchu\s+queues?|braided\s+queues?|shaved[- ]forehead\s+queues?|qing\s+braids?|manchu\s+braids?|pigtail\s+braids?"), "non_qing_1789", "cloth-bound topknot under war helmet", "Qing/Manchu shaved-forehead queue is only historically accurate for 1788-1789 Qing forces"),
    AnachronismRule("manchu_robe", "qing_anachronism", _compile_word(r"manchu\s+robes?|qing\s+robes?|magua\s+jackets?|changshans?"), "non_qing_1789", "cross-collar battle tunic", "Manchu/Qing robes are anachronistic outside 1788-1789 Qing forces"),
    AnachronismRule("qing_hat", "qing_anachronism", _compile_word(r"qing\s+mandarin\s+hats?|peacock[- ]feather\s+finials?|manchu\s+tassel\s+hats?"), "non_qing_1789", "lacquered iron helmet", "Qing mandarin/tassel headgear is anachronistic outside 1788-1789 Qing forces"),
    AnachronismRule("eight_banners", "qing_anachronism", _compile_word(r"eight\s+banners\s+(?:troops?|cavalry|army|bannermen)|manchu\s+bannermen"), "non_qing_1789", "armored vanguard troops", "Manchu Eight Banners existed only in Qing era"),
    AnachronismRule("dingjia_non_qing", "qing_anachronism", _compile_word(r"qing\s+dingjia"), "non_qing_1789", "iron lamellar cuirass", "Qing dingjia is specific to Qing forces"),

    # --- Category 5: Blanket Fog / Mist / Smoke White-Outs (10 rules, visual.md §7 & ERR-20261122-01) ---
    AnachronismRule("river_mist", "fog_smoke_ban", _compile_word(r"river\s+mist"), "always", "crisp clear-air river reflection", "Blanket 'river mist' washes out 35mm contrast"),
    AnachronismRule("dense_battlefield_mist", "fog_smoke_ban", _compile_word(r"dense\s+battlefield\s+mist"), "always", "crisp directional sunlight", "Blanket 'dense battlefield mist' causes white-out haze"),
    AnachronismRule("drifting_gunsmoke_fog", "fog_smoke_ban", _compile_word(r"drifting\s+gunsmoke\s+fog"), "always", "crisp optical clarity", "Blanket 'drifting gunsmoke fog' muddies frame dynamic range"),
    AnachronismRule("thick_heavy_fog", "fog_smoke_ban", _compile_word(r"(?:thick|heavy|dense|blanket|pea[- ]soup|murky|whiteout|opaque)\s+(?:fog|mist|haze)"), "always", "crisp optical clarity", "Heavy/blanket fog/mist washes out 2K dynamic range"),
    AnachronismRule("volumetric_fog", "fog_smoke_ban", _compile_word(r"volumetric\s+(?:fog|mist|smoke)"), "always", "deep-focus 35mm anamorphic depth", "Volumetric fog creates synthetic low-contrast haze"),
    AnachronismRule("opaque_smoke_cloud", "fog_smoke_ban", _compile_word(r"opaque\s+smoke(?:\s+clouds?)?|smoke\s+white[- ]?outs?"), "always", "warm torchlight chiaroscuro", "Opaque smoke white-outs are banned"),
    AnachronismRule("river_mist_map_dive", "fog_smoke_ban", _compile_word(r"river_mist_map_dive"), "always", "map_camera_zoom_match", "Procedural smoke transition river_mist_map_dive is banned (ERR-20261122-01)"),
    AnachronismRule("dust_smoke_cloud", "fog_smoke_ban", _compile_word(r"dust_smoke_cloud"), "always", "edge_pass", "dust_smoke_cloud smoke transition is banned on clean cinema prompts"),
    AnachronismRule("foggy_whiteout", "fog_smoke_ban", _compile_word(r"fog[- ]shrouded|shrouded\s+in\s+(?:thick\s+)?(?:fog|mist)"), "always", "bathed in crisp directional sunlight", "Fog-shrouded framing washes out subject contrast"),
    AnachronismRule("atmospheric_smog", "fog_smoke_ban", _compile_word(r"battlefield\s+smog|milky\s+haze"), "always", "clear atmospheric depth", "Milky haze/smog degrades p95-p5 dynamic range"),

    # --- Category 6: Modern, Fantasy, Sci-Fi & Sand-Table Artifacts (11 rules) ---
    AnachronismRule("wristwatch_glasses", "modern_anachronism", _compile_word(r"wristwatches?|smartwatches?|eyeglasses|sunglasses|plastic\s+goggles"), "always", "", "Modern eyewear/wristwatches are anachronistic"),
    AnachronismRule("modern_materials", "modern_anachronism", _compile_word(r"concrete\s+walls?|poured\s+concrete|asphalt\s+roads?|barbed\s+wire|steel\s+cables?|chain[- ]link\s+fences?"), "always", "rammed-earth and timber ramparts", "Modern industrial materials are anachronistic"),
    AnachronismRule("electric_lighting", "modern_anachronism", _compile_word(r"electric\s+floodlights?|fluorescent\s+lights?|streetlights?|power\s+lines?|utility\s+poles?|led\s+lights?"), "always", "warm pitch-torchlight", "Electric lighting/infrastructure is anachronistic"),
    AnachronismRule("neon_cyberpunk", "fantasy_slop", _compile_word(r"neon\s+rim(?:\s+lighting)?|neon\s+glow|cyberpunk|sci[- ]fi\s+hud|digital\s+radar|oscilloscopes?|sniper\s+reticles?"), "always", "natural 35mm film lighting", "Digital/neon/cyber HUD tropes are banned (visual.md §3, §5)"),
    AnachronismRule("modern_tactical_gear", "modern_anachronism", _compile_word(r"kevlar(?:\s+vests?)?|tactical\s+vests?|camouflage\s+uniforms?|camo\s+gear|combat\s+boots"), "always", "lacquered leather lamellar armor", "Modern tactical gear is anachronistic"),
    AnachronismRule("modern_star_flag", "modern_anachronism", _compile_word(r"modern\s+five[- ]pointed\s+star\s+flags?|modern\s+national\s+flags?"), "always", "plain unmarked crimson silk war pennants", "Modern national flags are anachronistic in dynastic eras"),
    AnachronismRule("glowing_magic", "fantasy_slop", _compile_word(r"glowing\s+magic(?:\s+weapons?|\s+swords?|\s+runes?)?|enchanted\s+blades?|energy\s+beams?|mana\s+auras?"), "always", "weathered forged iron weapons", "Fantasy magic tropes are banned"),
    AnachronismRule("chrome_superhero", "fantasy_slop", _compile_word(r"mirror[- ]polished\s+chrome(?:\s+armou?r)?|chrome\s+armou?r|superhero\s+capes?"), "always", "mud-splattered practical armor", "Polished chrome superhero tropes are banned"),
    AnachronismRule("sand_table_diorama", "fantasy_slop", _compile_word(r"tactical_sand_table|sand[- ]table\s+miniatures?|board[- ]game\s+miniatures?|3d\s+dioramas?|plastic\s+toy\s+soldiers?"), "always", "wide 35mm live-action terrain", "Sand-tables and toy dioramas are banned (visual.md §6)"),
    AnachronismRule("cgi_plasticity", "fantasy_slop", re.compile(r"(?<!zero\s)(?<!no\s)\b(?:unreal\s+engine\s*5?|octane\s+render|pixar\s+3d|anime\s+style|cartoon\s+clipart)\b", re.IGNORECASE), "always", "photorealistic 35mm Kodak Vision3 500T live-action", "3D game/cartoon render tokens violate 35mm live-action grammar"),
    AnachronismRule("pil_overlay_stub", "packaging_violation", _compile_word(r"pil\s+draw\s+overlay|html\s+text\s+box\s+overlay|dry[- ]run\s+stub"), "always", "", "PIL/HTML text overlays and dry-run stubs are banned (ERR-20261030-01)"),

    # --- Category 7: Raw Story-Frame Text Requests when `is_thumbnail=False` (5 rules) ---
    AnachronismRule(
        "story_text_reading_quote",
        "story_frame_text_request",
        re.compile(
            r"(?:bold\s+[^,.;]{0,50}?)?(?:title\s+lettering|lettering|text|words?|captions?|banners?|signs?)\s+reading(?:\s+exactly|\s+cleanly)?\s+['\"][^'\"]+['\"]",
            re.IGNORECASE,
        ),
        "story_frame_only",
        "plain unmarked surfaces with zero text",
        "Raw story frames must enforce allowed_text=None (Zero AI-Drawn Text)",
    ),
    AnachronismRule(
        "story_written_text_overlay",
        "story_frame_text_request",
        re.compile(
            r"(?<!no\s)(?<!zero\s)(?<!without\s)\b(?:typography\s+overlay|subtitle\s+overlay|speech\s+bubbles?|text\s+banners?|floating\s+text\s+labels?|on[- ]screen\s+title\s+text|bold\s+uppercase\s+(?:vietnamese\s+)?title(?:\s+lettering|\s+text)?)\b",
            re.IGNORECASE,
        ),
        "story_frame_only",
        "",
        "Story frames forbid typography/title/speech-bubble requests when is_thumbnail=False",
    ),
    AnachronismRule(
        "story_banner_characters",
        "story_frame_text_request",
        re.compile(
            r"(?<!no\s)(?<!zero\s)(?<!without\s)\b(?:chinese\s+characters\s+(?:written|painted|embroidered)|hanzi\s+inscriptions?|calligraphy\s+text\s+written|map\s+text\s+labels?)\b",
            re.IGNORECASE,
        ),
        "story_frame_only",
        "pure geometric unmarked emblems with zero characters",
        "Story-frame banners and maps must have zero Chinese/Vietnamese characters",
    ),

    # --- Category 8: Celebrity / Actor Likenesses Triggering Flow `PROMINENT_PEOPLE` (12 rules covering 30+ names) ---
    AnachronismRule("celeb_donnie_yen", "prominent_people", _compile_word(r"donnie\s+yen|chan\s+tu\s+dan|chân\s+tử\s+đan"), "always", "seasoned Đại Việt commander", "Actor name triggers Flow PROMINENT_PEOPLE safety filter"),
    AnachronismRule("celeb_jet_li", "prominent_people", _compile_word(r"jet\s+li|ly\s+lien\s+kiet|lý\s+liên\s+kiệt"), "always", "fierce martial commander", "Actor name triggers Flow PROMINENT_PEOPLE safety filter"),
    AnachronismRule("celeb_tony_leung", "prominent_people", _compile_word(r"tony\s+leung|luong\s+trieu\s+vy|lương\s+triều\s+vỹ"), "always", "stoic historical strategist", "Actor name triggers Flow PROMINENT_PEOPLE safety filter"),
    AnachronismRule("celeb_chow_yun_fat", "prominent_people", _compile_word(r"chow\s+yun[- ]?fat|chau\s+nhuan\s+phat|châu\s+nhuận\s+phát"), "always", "veteran imperial general", "Actor name triggers Flow PROMINENT_PEOPLE safety filter"),
    AnachronismRule("celeb_japanese_stars", "prominent_people", _compile_word(r"ken\s+watanabe|hiroyuki\s+sanada|toshiro\s+mifune|takeshi\s+kaneshiro"), "always", "weathered battlefield commander", "Actor name triggers Flow PROMINENT_PEOPLE safety filter"),
    AnachronismRule("celeb_hk_cn_stars", "prominent_people", _compile_word(r"jackie\s+chan|thanh\s+long|thành\s+long|andy\s+lau|luu\s+duc\s+hoa|lưu\s+đức\s+hoa|zhang\s+ziyi|chuong\s+tu\s+di|gong\s+li|wu\s+jing"), "always", "period-authentic historical figure", "Actor name triggers Flow PROMINENT_PEOPLE safety filter"),
    AnachronismRule("celeb_hollywood_action", "prominent_people", _compile_word(r"keanu\s+reeves|pedro\s+pascal|brad\s+pitt|tom\s+cruise|russell\s+crowe|orlando\s+bloom|liam\s+neeson|christian\s+bale|jason\s+momoa|henry\s+cavill|chris\s+hemsworth|dwayne\s+johnson|leonardo\s+dicaprio"), "always", "weathered historical warrior", "Hollywood actor name triggers Flow PROMINENT_PEOPLE safety filter"),
    AnachronismRule("celeb_vn_stars", "prominent_people", _compile_word(r"johnny\s+tr[ií]\s+nguy[eễ]n|ng[oô]\s+thanh\s+v[aâ]n|veronica\s+ngo|trấn\s+thành(?!\s+t[oô]ng)|lý\s+hải(?!\s+quân)"), "always", "authentic Vietnamese historical warrior", "Vietnamese celebrity name triggers Flow PROMINENT_PEOPLE safety filter"),
    AnachronismRule("celeb_public_figures", "prominent_people", _compile_word(r"taylor\s+swift|elon\s+musk|donald\s+trump|vladimir\s+putin|xi\s+jinping|barack\s+obama"), "always", "", "Public figure name triggers Flow PROMINENT_PEOPLE safety filter"),
    AnachronismRule(
        "celeb_likeness_phrase",
        "prominent_people",
        re.compile(
            r"\b(?i:played\s+by|portrayed\s+by|starring|in\s+the\s+likeness\s+of|resembling(?:\s+actor)?|looking\s+like(?:\s+actor)?)\s+[A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+){0,2}",
            re.UNICODE,
        ),
        "always",
        "",
        "Actor likeness phrasing triggers Flow PROMINENT_PEOPLE filter",
    ),
)


def _rule_applies(
    rule: AnachronismRule,
    *,
    year: int,
    norm_faction: str,
    is_thumbnail: bool,
) -> bool:
    cond = rule.condition
    if cond == "always":
        return True
    if cond == "pre_1400":
        return year < 1400
    if cond == "pre_1600":
        return year < 1600
    if cond == "non_qing_1789":
        is_legit_qing = (norm_faction == "qing") and (1644 <= year <= 1911)
        return not is_legit_qing
    if cond == "story_frame_only":
        return not is_thumbnail
    return True


_NEGATED_PREFIX_RE = re.compile(
    r"\b(?:no|zero|without|never|neither|forbid|forbidden)\s+"
    r"(?:[A-Za-z0-9_\-]+(?:\s+|/)){0,5}$",
    re.IGNORECASE,
)
_ACTION_BREAK_WORDS = {
    "holding",
    "wielding",
    "wearing",
    "carrying",
    "firing",
    "riding",
    "fighting",
    "charging",
    "standing",
    "marching",
    "dressed",
    "armed",
}


def _is_negated_mention(text: str, match_start: int) -> bool:
    """Return True when a matched token sits inside an explicit negative lock (e.g. 'zero blanket river mist')."""
    window_start = max(0, match_start - 56)
    prefix = text[window_start:match_start]
    # Trim to latest clause boundary
    for sep in (".", ";", ":", "!", "?", "(", ")", ","):
        idx = prefix.rfind(sep)
        if idx != -1:
            prefix = prefix[idx + 1 :]
    m = _NEGATED_PREFIX_RE.search(prefix)
    if not m:
        return False
    between_words = {w.lower() for w in re.findall(r"[A-Za-z]+", m.group(0))}
    return not bool(between_words & _ACTION_BREAK_WORDS)


def _has_positive_armor_anchor(prompt_text: str) -> bool:
    low = prompt_text.lower()
    ascii_low = _strip_diacritics(low)
    return any(kw in low or kw in ascii_low for kw in POSITIVE_ANCHOR_KEYWORDS)


def audit_and_sanitize_historical_prompt(
    prompt: str,
    dynasty_era: str,
    faction: str = "dai_viet",
    is_thumbnail: bool = False,
) -> dict[str, Any]:
    """Audit and sanitize a historical Flow image/thumbnail prompt.

    Detects & strips 60+ anachronistic, fog, raw-text, and `PROMINENT_PEOPLE` tokens,
    and injects period-accurate positive armor/weapon + clear-air anchors when missing.
    """
    era_info = resolve_dynasty_era(dynasty_era)
    era_id = str(era_info["era_id"])
    year = int(era_info["year"])
    norm_faction = normalize_faction(faction)

    working = str(prompt or "").strip()
    violations: list[dict[str, Any]] = []
    stripped_tokens: list[str] = []
    prominent_people_flagged: list[str] = []
    fog_tokens_stripped: list[str] = []
    text_request_stripped = False

    for rule in HISTORICAL_ANACHRONISM_CATALOG:
        if not _rule_applies(rule, year=year, norm_faction=norm_faction, is_thumbnail=is_thumbnail):
            continue
        raw_matches = list(rule.pattern.finditer(working))
        active_matches = [m for m in raw_matches if not _is_negated_mention(working, m.start())]
        if not active_matches:
            continue
        for m in active_matches:
            matched_str = m.group(0)
            violations.append(
                {
                    "token": rule.token_id,
                    "matched_text": matched_str,
                    "category": rule.category,
                    "reason": rule.reason,
                }
            )
            if rule.token_id not in stripped_tokens:
                stripped_tokens.append(rule.token_id)
            if rule.category == "prominent_people":
                prominent_people_flagged.append(matched_str)
            elif rule.category == "fog_smoke_ban":
                fog_tokens_stripped.append(matched_str)
            elif rule.category == "story_frame_text_request":
                text_request_stripped = True

        # Replace only non-negated occurrences from right to left so indices stay exact
        for m in reversed(active_matches):
            working = working[: m.start()] + rule.replacement + working[m.end() :]

    # Clean up redundant punctuation/whitespace produced by token removal
    working = re.sub(r"\s+,", ",", working)
    working = re.sub(r",\s*,+", ",", working)
    working = re.sub(r"\.\s*\.+", ".", working)
    working = re.sub(r"\s{2,}", " ", working).strip(" ,")

    injected_anchors: list[str] = []

    # Inject period-accurate positive armor/weapon anchor when missing
    if not _has_positive_armor_anchor(working):
        anchor_phrase = _select_positive_anchor(era_id, norm_faction)
        injected_anchors.append(anchor_phrase)
        if working and not working.endswith("."):
            working = f"{working}. Featuring {anchor_phrase}."
        elif working:
            working = f"{working} Featuring {anchor_phrase}."
        else:
            working = f"Historical scene featuring {anchor_phrase}."

    # Ensure Clear-Air 35mm Cinema Clarity anchor if missing or after stripping fog
    low_work = working.lower()
    if "crisp optical clarity" not in low_work and "35mm" not in low_work:
        injected_anchors.append(CLEAR_AIR_OPTICAL_LOCK)
        working = f"{working.rstrip('. ')}. {CLEAR_AIR_OPTICAL_LOCK}."

    # Ensure Zero-Text Lock on non-thumbnail story frames
    low_work = working.lower()
    if not is_thumbnail and not any(
        neg in low_work for neg in ("no text", "zero text", "zero letters")
    ):
        injected_anchors.append(CLEAN_FRAME_NO_TEXT_LOCK)
        working = f"{working.rstrip('. ')}, {CLEAN_FRAME_NO_TEXT_LOCK}."

    is_clean = len(violations) == 0
    return {
        "passed": is_clean,
        "is_clean": is_clean,
        "sanitized_valid": True,
        "original_prompt": prompt,
        "sanitized_prompt": working,
        "dynasty_era": dynasty_era,
        "resolved_era": era_id,
        "resolved_year": year,
        "faction": faction,
        "normalized_faction": norm_faction,
        "is_thumbnail": is_thumbnail,
        "violations": violations,
        "stripped_tokens": stripped_tokens,
        "injected_anchors": injected_anchors,
        "prominent_people_flagged": prominent_people_flagged,
        "fog_tokens_stripped": fog_tokens_stripped,
        "text_request_stripped": text_request_stripped,
        "catalog_rule_count": len(HISTORICAL_ANACHRONISM_CATALOG),
    }


# ---------------------------------------------------------------------------
# Sub-Cut Crop Geometry & Auto-Correction (1.25x..1.40x)
# ---------------------------------------------------------------------------

def _compute_crop_rect_px_and_norm(
    width: int,
    height: int,
    zoom: float,
    cx: float,
    cy: float,
) -> tuple[list[int], list[float]]:
    """Compute exact visible pixel `[x0, y0, x1, y1]` and normalized rect `[nx0, ny0, nx1, ny1]`."""
    eff_z = max(1.0, float(zoom))
    cx_c = max(0.0, min(1.0, float(cx)))
    cy_c = max(0.0, min(1.0, float(cy)))

    inv_z = 1.0 / eff_z
    nx0 = (1.0 - inv_z) * cx_c
    ny0 = (1.0 - inv_z) * cy_c
    nx1 = min(1.0, nx0 + inv_z)
    ny1 = min(1.0, ny0 + inv_z)

    vis_w = max(1, int(round(width * inv_z)))
    vis_h = max(1, int(round(height * inv_z)))
    x0 = max(0, min(width - vis_w, int(round((width - vis_w) * cx_c))))
    y0 = max(0, min(height - vis_h, int(round((height - vis_h) * cy_c))))
    x1 = min(width, x0 + vis_w)
    y1 = min(height, y0 + vis_h)

    return [x0, y0, x1, y1], [round(nx0, 5), round(ny0, 5), round(nx1, 5), round(ny1, 5)]


def audit_sub_cut_crop_geometry(
    width: int,
    height: int,
    focus_zoom: float,
    focus_cx: float,
    focus_cy: float,
    subtitle_margin_v: int = DEFAULT_SUBTITLE_MARGIN_V,
) -> dict[str, Any]:
    """Audit and auto-correct `1.25x..1.40x` sub-cut crop geometry.

    Computes exact visible crop rectangle `[x0, y0, x1, y1]` and guarantees:
    1. Upper head zone (`0.18..0.46` height) is 100% contained without top/bottom severing
       (including V7 `1.04x` dynamic zoompan tail headroom).
    2. Projected screen-space head zone avoids collision with the `subtitle_margin_v`
       kinetic subtitle band.
    3. Horizontal pivot stays within `[0.22, 0.78]` so hero shoulders/faces are never sliced.
    """
    w = max(64, int(width))
    h = max(64, int(height))
    raw_z = float(focus_zoom)
    raw_cx = float(focus_cx)
    raw_cy = float(focus_cy)
    margin_v = max(0, int(subtitle_margin_v))

    raw_rect_px, raw_rect_norm = _compute_crop_rect_px_and_norm(w, h, raw_z, raw_cx, raw_cy)

    issues: list[str] = []

    # 1. Sub-cut zoom bounds check (1.25x..1.40x)
    if raw_z < SUBCUT_MIN_ZOOM - 1e-6 or raw_z > SUBCUT_MAX_ZOOM + 1e-6:
        issues.append("ZOOM_OUT_OF_SUBCUT_RANGE")
    corr_z = min(SUBCUT_MAX_ZOOM, max(SUBCUT_MIN_ZOOM, raw_z))

    # 2. Compute safe vertical focus_cy window [cy_min, cy_max]
    #    - Upper bound `cy_max`: keeps crop top `ny0 <= HEAD_ZONE_Y_MIN` even after 1.04x V7 push-in
    z_end = corr_z * V7_SUBCUT_PUSH_IN_FACTOR
    span_end = max(1e-6, 1.0 - 1.0 / z_end)
    cy_max = min(0.85, (HEAD_ZONE_Y_MIN - HEAD_TOP_SAFETY_MARGIN) / span_end)

    #    - Lower bound `cy_min`: prevents camera floating into sky & pushing head zone [0.18..0.46]
    #      down onto the output screen's ASS subtitle band at `MarginV = subtitle_margin_v`.
    eff_margin_norm = min(0.50, margin_v / float(h))
    sub_bottom_screen_norm = 1.0 - eff_margin_norm
    sub_top_screen_norm = max(0.35, sub_bottom_screen_norm - SUBTITLE_BAND_HEIGHT_NORM)
    cy_for_sub_clearance = (HEAD_ZONE_Y_MAX * corr_z - sub_top_screen_norm) / max(1e-6, corr_z - 1.0)
    cy_min = max(FOCUS_CY_FLOOR, cy_for_sub_clearance)

    if cy_min > cy_max:
        # Never sever the head if caller passes an extreme subtitle_margin_v; meet at upper-safe bound
        cy_min = min(cy_max, FOCUS_CY_FLOOR)

    # Evaluate raw head-severance & subtitle-collision status at raw parameters
    raw_z_eff = max(1.0001, raw_z)
    raw_ny0 = raw_rect_norm[1]
    raw_ny1 = raw_rect_norm[3]
    raw_ny0_end = max(0.0, min(1.0, raw_cy)) * (1.0 - 1.0 / (raw_z_eff * V7_SUBCUT_PUSH_IN_FACTOR))
    head_severed = (
        raw_ny0 > HEAD_ZONE_Y_MIN - 1e-5
        or raw_ny0_end > (HEAD_ZONE_Y_MIN - HEAD_TOP_SAFETY_MARGIN) + 1e-5
        or raw_ny1 < (HEAD_ZONE_Y_MAX + HEAD_BOTTOM_SAFETY_MARGIN) - 1e-5
        or raw_cy < 0.0
        or raw_cy > 1.0
    )
    if head_severed:
        issues.append("UPPER_HEAD_ZONE_SEVERED")

    raw_head_screen_bottom = raw_z_eff * (HEAD_ZONE_Y_MAX - raw_ny0)
    subtitle_collision = (
        raw_head_screen_bottom > sub_top_screen_norm + 1e-4
        or raw_cy < cy_min - 1e-5
    )
    if subtitle_collision:
        issues.append("SUBTITLE_COLLISION_RISK")

    # 3. Horizontal safe-zone check
    horizontal_clipped = raw_cx < FOCUS_CX_MIN - 1e-5 or raw_cx > FOCUS_CX_MAX + 1e-5
    if horizontal_clipped:
        issues.append("HORIZONTAL_SAFE_ZONE_CLIPPED")

    corr_cx = round(min(FOCUS_CX_MAX, max(FOCUS_CX_MIN, raw_cx)), 4)
    corr_cy = round(min(cy_max, max(cy_min, raw_cy)), 4)
    corr_z = round(corr_z, 4)

    corr_rect_px, corr_rect_norm = _compute_crop_rect_px_and_norm(w, h, corr_z, corr_cx, corr_cy)
    corr_head_screen_top = round(corr_z * (HEAD_ZONE_Y_MIN - corr_rect_norm[1]), 4)
    corr_head_screen_bottom = round(corr_z * (HEAD_ZONE_Y_MAX - corr_rect_norm[1]), 4)

    was_corrected = (
        abs(corr_z - raw_z) > 1e-4
        or abs(corr_cx - raw_cx) > 1e-4
        or abs(corr_cy - raw_cy) > 1e-4
    )

    head_zone_px = [
        int(round(w * FOCUS_CX_MIN)),
        int(round(h * HEAD_ZONE_Y_MIN)),
        int(round(w * FOCUS_CX_MAX)),
        int(round(h * HEAD_ZONE_Y_MAX)),
    ]
    subtitle_zone_screen_px = [
        int(round(w * 0.06)),
        int(round(h * sub_top_screen_norm)),
        int(round(w * 0.94)),
        int(round(h * sub_bottom_screen_norm)),
    ]

    return {
        "passed": len(issues) == 0,
        "was_corrected": was_corrected,
        "issues": issues,
        "width": w,
        "height": h,
        "subtitle_margin_v": margin_v,
        "focus_zoom": raw_z,
        "focus_cx": raw_cx,
        "focus_cy": raw_cy,
        "corrected_focus_zoom": corr_z,
        "corrected_focus_cx": corr_cx,
        "corrected_focus_cy": corr_cy,
        "safe_cy_range": [round(cy_min, 4), round(cy_max, 4)],
        "safe_cx_range": [FOCUS_CX_MIN, FOCUS_CX_MAX],
        "crop_rect": raw_rect_px,
        "crop_rect_norm": raw_rect_norm,
        "corrected_crop_rect": corr_rect_px,
        "corrected_crop_rect_norm": corr_rect_norm,
        "head_zone_px": head_zone_px,
        "head_zone_norm": [HEAD_ZONE_Y_MIN, HEAD_ZONE_Y_MAX],
        "head_severed": head_severed,
        "subtitle_collision": subtitle_collision,
        "head_screen_y_span_after_fix": [corr_head_screen_top, corr_head_screen_bottom],
        "subtitle_top_screen_norm": round(sub_top_screen_norm, 4),
        "subtitle_zone_screen_px": subtitle_zone_screen_px,
    }


# ---------------------------------------------------------------------------
# Rendered 2K Frame & Thumbnail Pixel Quality Gate
# ---------------------------------------------------------------------------

def _srgb_to_relative_luminance(luma_0_255: float) -> float:
    """Convert 0..255 sRGB greyscale level to WCAG 2.1 relative luminance [0.0, 1.0]."""
    c = max(0.0, min(1.0, float(luma_0_255) / 255.0))
    return c / 12.92 if c <= 0.04045 else float(((c + 0.055) / 1.055) ** 2.4)


def _wcag_contrast_ratio(lum_a: float, lum_b: float) -> float:
    hi, lo = (lum_a, lum_b) if lum_a >= lum_b else (lum_b, lum_a)
    return (hi + 0.05) / (lo + 0.05)


def audit_rendered_2k_frame(
    image_path: Path,
    is_thumbnail: bool = False,
) -> dict[str, Any]:
    """Audit a rendered 2K story frame or Flow-native thumbnail with `numpy` & `PIL`.

    Checks:
    - File existence & `< 2MB` strict file-size gate when `is_thumbnail=True`.
    - Resolution (`>= 1280x720` / `720x1280` minimum HD/2K floor).
    - Dynamic range (`p95 - p5 >= 85.0`) catching murky fog/haze white-outs.
    - Black-crush (`<= 3` luma %) & overexposure clipping (`>= 252` luma %).
    - Edge sharpness (`Laplacian` variance `>= 25.0`).
    - Bottom-right `W-w-36:H-h-36` watermark region & `MarginV=660` subtitle readability contrast.
    """
    p = Path(image_path)
    if not p.is_file():
        return {
            "passed": False,
            "exists": False,
            "image_path": str(p),
            "is_thumbnail": is_thumbnail,
            "issues": ["FILE_NOT_FOUND"],
        }

    file_size_bytes = p.stat().st_size
    file_size_mb = round(file_size_bytes / (1024.0 * 1024.0), 4)

    try:
        with Image.open(p) as im:
            rgb = im.convert("RGB")
            width, height = rgb.size
            arr = np.asarray(rgb, dtype=np.float32)
    except Exception as exc:
        return {
            "passed": False,
            "exists": True,
            "image_path": str(p),
            "is_thumbnail": is_thumbnail,
            "file_size_bytes": file_size_bytes,
            "issues": [f"CORRUPT_IMAGE:{type(exc).__name__}"],
        }

    issues: list[str] = []

    # 1. File size gate (strict < 2MB on thumbnails per ERR-20261030-01)
    if file_size_bytes < 1024:
        issues.append("EMPTY_OR_STUB_IMAGE")
    if is_thumbnail and file_size_bytes >= MAX_THUMBNAIL_BYTES:
        issues.append("THUMBNAIL_EXCEEDS_2MB")

    # 2. Resolution gate
    long_edge = max(width, height)
    short_edge = min(width, height)
    if long_edge < MIN_LONG_EDGE_PX or short_edge < MIN_SHORT_EDGE_PX:
        issues.append("RESOLUTION_BELOW_HD_2K_FLOOR")

    # 3. Luminance, Dynamic Range (p95 - p5 >= 85), Black-Crush & Overexposure
    luma = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    p5, p50, p95 = (float(v) for v in np.percentile(luma, [5, 50, 95]))
    dynamic_range = round(p95 - p5, 3)
    if dynamic_range < MIN_DYNAMIC_RANGE_P95_P5:
        issues.append("WASHED_OUT_LOW_DYNAMIC_RANGE")

    black_crush_pct = round(float(np.mean(luma <= 3.0) * 100.0), 3)
    overexposure_pct = round(float(np.mean(luma >= 252.0) * 100.0), 3)
    if black_crush_pct > MAX_BLACK_CRUSH_PCT:
        issues.append("SEVERE_BLACK_CRUSH")
    if overexposure_pct > MAX_OVEREXPOSURE_PCT:
        issues.append("SEVERE_OVEREXPOSURE_CLIPPING")

    # 4. Edge sharpness via 2D discrete Laplacian variance
    if height >= 4 and width >= 4:
        center = luma[1:-1, 1:-1]
        lap = (
            -4.0 * center
            + luma[:-2, 1:-1]
            + luma[2:, 1:-1]
            + luma[1:-1, :-2]
            + luma[1:-1, 2:]
        )
        laplacian_variance = round(float(np.var(lap)), 3)
    else:
        laplacian_variance = 0.0
    if laplacian_variance < MIN_LAPLACIAN_VARIANCE:
        issues.append("BLURRY_LOW_LAPLACIAN_SHARPNESS")

    # 5. Bottom-Right W-w-36:H-h-36 Watermark Patch Readability (ERR-20261109-02)
    scale_ref = min(width, height) / 1080.0
    wm_size = max(32, min(min(width, height) // 3, int(round(100 * scale_ref))))
    wm_pad = max(8, min(min(width, height) // 6, int(round(36 * scale_ref))))
    wm_x1 = max(1, width - wm_pad)
    wm_y1 = max(1, height - wm_pad)
    wm_x0 = max(0, wm_x1 - wm_size)
    wm_y0 = max(0, wm_y1 - wm_size)
    wm_patch = luma[wm_y0:wm_y1, wm_x0:wm_x1]
    wm_mean = round(float(np.mean(wm_patch)), 3) if wm_patch.size else p50
    wm_std = round(float(np.std(wm_patch)), 3) if wm_patch.size else 0.0
    wm_rel_lum = _srgb_to_relative_luminance(wm_mean)
    wm_badge_contrast = round(
        max(_wcag_contrast_ratio(0.92, wm_rel_lum), _wcag_contrast_ratio(0.02, wm_rel_lum)),
        3,
    )

    # 6. MarginV=660 Subtitle Band Readability Contrast
    if height > width:
        sub_bottom_norm = 1.0 - (DEFAULT_SUBTITLE_MARGIN_V / float(CANONICAL_SHORT_HEIGHT))
        sub_top_norm = sub_bottom_norm - SUBTITLE_BAND_HEIGHT_NORM
        sx0, sx1 = int(round(width * 0.08)), int(round(width * 0.92))
    else:
        sub_bottom_norm = 0.90
        sub_top_norm = 0.76
        sx0, sx1 = int(round(width * 0.12)), int(round(width * 0.88))

    sy0 = max(0, min(height - 1, int(round(height * sub_top_norm))))
    sy1 = max(sy0 + 1, min(height, int(round(height * sub_bottom_norm))))
    sub_patch = luma[sy0:sy1, max(0, sx0):max(sx0 + 1, sx1)]

    sub_mean = round(float(np.mean(sub_patch)), 3) if sub_patch.size else p50
    sub_p90 = round(float(np.percentile(sub_patch, 90)), 3) if sub_patch.size else p95
    sub_glare_pct = round(float(np.mean(sub_patch >= 248.0) * 100.0), 3) if sub_patch.size else 0.0

    # Ivory-white subtitle fill (#FFF8E7 -> luma ~247.5 -> Y~0.935) + 10px black outline (Y=0.0)
    ivory_rel_lum = _srgb_to_relative_luminance(247.5)
    sub_bg_rel_lum = _srgb_to_relative_luminance(sub_mean)
    subtitle_ivory_contrast = round(_wcag_contrast_ratio(ivory_rel_lum, sub_bg_rel_lum), 3)
    subtitle_outlined_contrast = round(
        max(subtitle_ivory_contrast, _wcag_contrast_ratio(0.0, sub_bg_rel_lum)),
        3,
    )

    if not is_thumbnail and sub_glare_pct > MAX_SUBTITLE_GLARE_PCT:
        issues.append("SUBTITLE_ZONE_BLOWN_GLARE")
    if subtitle_outlined_contrast < MIN_EFFECTIVE_SUBTITLE_CONTRAST:
        issues.append("SUBTITLE_READABILITY_LOW_CONTRAST")

    return {
        "passed": len(issues) == 0,
        "exists": True,
        "image_path": str(p),
        "is_thumbnail": is_thumbnail,
        "width": width,
        "height": height,
        "resolution": [width, height],
        "is_true_2k": long_edge >= 1920,
        "file_size_bytes": file_size_bytes,
        "file_size_mb": file_size_mb,
        "thumbnail_under_2mb": file_size_bytes < MAX_THUMBNAIL_BYTES,
        "luma_p5": round(p5, 3),
        "luma_p50": round(p50, 3),
        "luma_p95": round(p95, 3),
        "dynamic_range": dynamic_range,
        "black_crush_pct": black_crush_pct,
        "overexposure_pct": overexposure_pct,
        "laplacian_variance": laplacian_variance,
        "watermark_zone": {
            "position_spec": "W-w-36:H-h-36",
            "bbox": [wm_x0, wm_y0, wm_x1, wm_y1],
            "mean_luma": wm_mean,
            "std_luma": wm_std,
            "badge_effective_contrast": wm_badge_contrast,
        },
        "subtitle_zone": {
            "margin_v": DEFAULT_SUBTITLE_MARGIN_V,
            "bbox": [sx0, sy0, sx1, sy1],
            "mean_luma": sub_mean,
            "p90_luma": sub_p90,
            "glare_pct": sub_glare_pct,
            "ivory_wcag_contrast": subtitle_ivory_contrast,
            "outlined_effective_contrast": subtitle_outlined_contrast,
        },
        "issues": issues,
    }


# ---------------------------------------------------------------------------
# Full-Episode Visual Readiness Gate (Short 9:16 & Long 16:9)
# ---------------------------------------------------------------------------

def _discover_spec_file(spec_path: Path) -> tuple[Path, Path | None]:
    """Return `(episode_dir, spec_json_file)` for either a directory or JSON path."""
    p = Path(spec_path)
    if p.is_file():
        return p.parent, p
    if not p.is_dir():
        return p, None

    direct_candidates = (
        p / "short_spec.json",
        p / "long_spec.json",
    )
    for cand in direct_candidates:
        if cand.is_file():
            return p, cand

    for pattern in ("*aligned_spec.json", "*_spec.json", "script_*_from_scratch.json", "script.json", "content.json"):
        matches = sorted(p.glob(pattern))
        if matches:
            return p, matches[0]
    return p, None


def _extract_episode_beats(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Collect deduplicated beat/scene records across Short V4-V8 and Long V5-V10 schemas."""
    collected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    def _add(item: dict[str, Any], fallback_idx: int) -> None:
        bid = str(item.get("beat_id") or item.get("id") or f"beat_{fallback_idx:03d}")
        if bid in seen_ids:
            return
        seen_ids.add(bid)
        rec = dict(item)
        rec.setdefault("beat_id", bid)
        collected.append(rec)

    has_primary_beats = False
    if isinstance(spec.get("beats"), list) and spec["beats"]:
        has_primary_beats = True
        for idx, b in enumerate(spec["beats"]):
            if isinstance(b, dict):
                _add(b, idx)

    cold_open = spec.get("cold_open")
    if isinstance(cold_open, list):
        for idx, b in enumerate(cold_open):
            if isinstance(b, dict):
                _add(b, len(collected) + idx)
    elif isinstance(cold_open, dict) and isinstance(cold_open.get("beats"), list):
        for idx, b in enumerate(cold_open["beats"]):
            if isinstance(b, dict):
                _add(b, len(collected) + idx)

    if isinstance(spec.get("chapters"), list):
        for ch in spec["chapters"]:
            if isinstance(ch, dict) and isinstance(ch.get("beats"), list) and ch["beats"]:
                has_primary_beats = True
                for idx, b in enumerate(ch["beats"]):
                    if isinstance(b, dict):
                        _add(b, len(collected) + idx)

    if not has_primary_beats and isinstance(spec.get("continuous_chains"), list):
        for chain in spec["continuous_chains"]:
            if isinstance(chain, dict) and isinstance(chain.get("beats"), list) and chain["beats"]:
                has_primary_beats = True
                for idx, b in enumerate(chain["beats"]):
                    if isinstance(b, dict):
                        _add(b, len(collected) + idx)

    if not has_primary_beats and isinstance(spec.get("scenes"), list):
        for s_idx, sc in enumerate(spec["scenes"]):
            if not isinstance(sc, dict):
                continue
            sub_beats = sc.get("beats") or sc.get("images")
            if isinstance(sub_beats, list) and sub_beats:
                images_by_id = {
                    im["id"]: im
                    for im in (sc.get("images") or [])
                    if isinstance(im, dict) and "id" in im
                }
                for b_idx, sb in enumerate(sub_beats):
                    if not isinstance(sb, dict):
                        continue
                    merged = dict(images_by_id.get(sb.get("image_id") or sb.get("id"), {}))
                    merged.update(sb)
                    _add(merged, s_idx * 100 + b_idx)
            else:
                _add(sc, s_idx)

    return collected


def _infer_beat_faction(beat: dict[str, Any], resolved_year: int, default_faction: str = "dai_viet") -> str:
    explicit = beat.get("faction")
    if explicit:
        return normalize_faction(str(explicit))

    text = _strip_diacritics(
        f"{beat.get('hero_subject', '')} {beat.get('prompt', '')} {beat.get('visual_prompt', '')}"
    ).lower()
    if 1780 <= resolved_year <= 1805 and any(
        kw in text for kw in ("qing ", "manchu", "ton si nghi", "sam nghi dong", "hua the hanh", "quan thanh", "bannermen")
    ) and not any(v in text for v in ("tay son", "quang trung", "nguyen hue")):
        return "qing"
    if 960 <= resolved_year <= 1279 and any(kw in text for kw in ("northern song", "song naval", "song dynasty", "quan tong")):
        return "northern_song"
    if 1250 <= resolved_year <= 1368 and any(kw in text for kw in ("yuan ", "mongol", "o ma nhi", "thoat hoan")):
        return "yuan_mongol"
    if 1400 <= resolved_year <= 1500 and any(kw in text for kw in ("ming ", "vuong thong", "lieu thang", "quan minh")):
        return "ming"
    return normalize_faction(default_faction)


def _discover_rendered_frames_and_thumbnails(episode_dir: Path) -> tuple[list[Path], list[Path]]:
    """Locate rendered story frames and deliverable thumbnails inside `episode_dir`."""
    img_exts = {".png", ".jpg", ".jpeg", ".webp"}
    story_frames: list[Path] = []
    for sub in ("frames", "images", "revisions/images/1"):
        d = episode_dir / sub
        if d.is_dir():
            for f in sorted(d.iterdir()):
                if f.is_file() and f.suffix.lower() in img_exts and "_master" not in f.stem.lower():
                    story_frames.append(f)
            if story_frames:
                break

    thumbnails: list[Path] = []
    preferred_names = (
        "thumbnail_9x16.png",
        "thumbnail_9x16.jpg",
        "thumbnail_16x9.png",
        "thumbnail_16x9.jpg",
        "thumbnail.png",
        "thumbnail.jpg",
    )
    for name in preferred_names:
        tp = episode_dir / name
        if tp.is_file():
            thumbnails.append(tp)

    if not thumbnails:
        for f in sorted(episode_dir.glob("*thumbnail*")):
            if f.is_file() and f.suffix.lower() in img_exts and "_master" not in f.stem.lower():
                thumbnails.append(f)

    return story_frames, thumbnails


def audit_full_episode_visual_readiness(spec_path: Path) -> dict[str, Any]:
    """Run prompt + sub-cut crop + rendered 2K frame + thumbnail QC across an episode."""
    episode_dir, spec_file = _discover_spec_file(Path(spec_path))
    if spec_file is None or not spec_file.is_file():
        return {
            "passed": False,
            "spec_path": str(spec_path),
            "episode_dir": str(episode_dir),
            "summary": {
                "total_beats": 0,
                "prompts_audited": 0,
                "prompt_violations_count": 0,
                "crops_audited": 0,
                "crop_violations_count": 0,
                "frames_audited": 0,
                "frame_failures_count": 0,
                "thumbnails_audited": 0,
                "thumbnail_failures_count": 0,
                "rendered_assets_present": False,
            },
            "blocking_issues": [f"SPEC_NOT_FOUND:{spec_path}"],
        }

    spec = json.loads(spec_file.read_text(encoding="utf-8"))

    # Determine format & resolution
    fmt_raw = str(spec.get("format_profile") or spec.get("aspect_ratio") or spec_file.name).lower()
    is_long = (
        "16x9" in fmt_raw
        or "16:9" in fmt_raw
        or "long" in fmt_raw
        or spec_file.name == "long_spec.json"
        or episode_dir.name.endswith("_long")
    )
    format_profile = "long_16x9" if is_long else "short_9x16"

    res_str = str(spec.get("resolution") or "").lower()
    if "x" in res_str:
        parts = res_str.split("x", 1)
        width, height = int(parts[0]), int(parts[1])
    elif isinstance(spec.get("width"), int) and isinstance(spec.get("height"), int):
        width, height = int(spec["width"]), int(spec["height"])
    else:
        width, height = (1920, 1080) if is_long else (1440, 2560)

    subtitle_margin_v = int(spec.get("subtitle_margin_v") or DEFAULT_SUBTITLE_MARGIN_V)

    # Infer dynasty_era context from spec metadata
    era_context = " ".join(
        str(spec.get(k) or "")
        for k in ("dynasty_era", "era", "job_id", "topic", "youtube_title")
    ).strip() or episode_dir.name
    era_info = resolve_dynasty_era(era_context)
    resolved_year = int(era_info["year"])
    default_faction = str(spec.get("faction") or "dai_viet")

    blocking_issues: list[str] = []
    prompt_audits: list[dict[str, Any]] = []
    crop_audits: list[dict[str, Any]] = []

    # 1. Audit episode style lock if present
    style_lock = spec.get("visual_style_lock") or spec.get("style_lock")
    if isinstance(style_lock, str) and len(style_lock.split()) >= 6:
        sl_audit = audit_and_sanitize_historical_prompt(
            style_lock, era_context, faction=default_faction, is_thumbnail=False
        )
        sl_audit["target_id"] = "STYLE_LOCK"
        prompt_audits.append(sl_audit)
        if not sl_audit["passed"]:
            blocking_issues.append(f"STYLE_LOCK_ANACHRONISM:{','.join(sl_audit['stripped_tokens'])}")

    # 2. Audit thumbnail prompt if present
    thumbnail_prompt_audit: dict[str, Any] | None = None
    thumb_spec = spec.get("thumbnail_spec")
    thumb_prompt = (
        thumb_spec.get("prompt")
        if isinstance(thumb_spec, dict)
        else spec.get("thumbnail_prompt")
    )
    if isinstance(thumb_prompt, str) and thumb_prompt.strip():
        thumbnail_prompt_audit = audit_and_sanitize_historical_prompt(
            thumb_prompt, era_context, faction=default_faction, is_thumbnail=True
        )
        thumbnail_prompt_audit["target_id"] = "THUMBNAIL_PROMPT"
        if not thumbnail_prompt_audit["passed"]:
            blocking_issues.append(
                f"THUMBNAIL_PROMPT_VIOLATION:{','.join(thumbnail_prompt_audit['stripped_tokens'])}"
            )

    # 3. Audit per-beat prompts & sub-cut crop geometries
    beats = _extract_episode_beats(spec)
    for b in beats:
        bid = str(b.get("beat_id") or b.get("id") or "UNKNOWN")
        beat_faction = _infer_beat_faction(b, resolved_year, default_faction=default_faction)

        beat_prompt = (
            b.get("prompt")
            or b.get("visual_prompt")
            or b.get("image_prompt")
            or b.get("start_frame_prompt")
        )
        if isinstance(beat_prompt, str) and beat_prompt.strip():
            pa = audit_and_sanitize_historical_prompt(
                beat_prompt, era_context, faction=beat_faction, is_thumbnail=False
            )
            pa["beat_id"] = bid
            prompt_audits.append(pa)
            if not pa["passed"]:
                blocking_issues.append(f"PROMPT[{bid}]:{','.join(pa['stripped_tokens'])}")

        # Sub-cut crop check when beat configures sub-cut or focus zoom
        scr = b.get("sub_cut_ratio")
        focus_dict = b.get("focus") if isinstance(b.get("focus"), dict) else {}
        fz_raw = b.get("focus_zoom") if b.get("focus_zoom") is not None else focus_dict.get("scale")
        has_subcut = (scr is not None and float(scr) > 0.0) or (fz_raw is not None and float(fz_raw) > 1.05)
        if has_subcut:
            fz = float(fz_raw if fz_raw is not None else 1.32)
            fcx = float(b["focus_cx"] if b.get("focus_cx") is not None else focus_dict.get("x", 0.50))
            fcy = float(b["focus_cy"] if b.get("focus_cy") is not None else focus_dict.get("y", 0.34))
            ca = audit_sub_cut_crop_geometry(
                width=width,
                height=height,
                focus_zoom=fz,
                focus_cx=fcx,
                focus_cy=fcy,
                subtitle_margin_v=subtitle_margin_v,
            )
            ca["beat_id"] = bid
            crop_audits.append(ca)
            if not ca["passed"]:
                blocking_issues.append(f"CROP[{bid}]:{','.join(ca['issues'])}")

    # 4. Audit rendered 2K frames & deliverable thumbnails on disk
    story_frames, thumb_files = _discover_rendered_frames_and_thumbnails(episode_dir)
    frame_audits: list[dict[str, Any]] = []
    for fp in story_frames:
        fa = audit_rendered_2k_frame(fp, is_thumbnail=False)
        frame_audits.append(fa)
        if not fa["passed"]:
            blocking_issues.append(f"FRAME[{fp.name}]:{','.join(fa['issues'])}")

    thumbnail_audits: list[dict[str, Any]] = []
    for tp in thumb_files:
        ta = audit_rendered_2k_frame(tp, is_thumbnail=True)
        thumbnail_audits.append(ta)
        if not ta["passed"]:
            blocking_issues.append(f"THUMBNAIL[{tp.name}]:{','.join(ta['issues'])}")

    prompt_violations_count = sum(1 for a in prompt_audits if not a["passed"]) + (
        1 if (thumbnail_prompt_audit and not thumbnail_prompt_audit["passed"]) else 0
    )
    crop_violations_count = sum(1 for a in crop_audits if not a["passed"])
    frame_failures_count = sum(1 for a in frame_audits if not a["passed"])
    thumbnail_failures_count = sum(1 for a in thumbnail_audits if not a["passed"])

    # 5. V12 4 Hard Auto-Fail Gates (spec + discovered frames + rendered MP4 if present)
    video_candidates = sorted(
        p for p in episode_dir.glob("*.mp4") if p.is_file() and "_raw" not in p.stem.lower()
    )
    primary_video = video_candidates[0] if video_candidates else None
    v12_gates_report = audit_v12_hard_gates(
        spec=spec,
        format_profile=format_profile,
        frame_paths=story_frames,
        video_path=primary_video,
    )
    if not v12_gates_report["passed"]:
        for issue in v12_gates_report["blocking_issues"]:
            if issue not in blocking_issues:
                blocking_issues.append(issue)

    passed = len(blocking_issues) == 0
    return {
        "passed": passed,
        "spec_path": str(spec_file),
        "episode_dir": str(episode_dir),
        "format_profile": format_profile,
        "dynasty_era": str(era_info["era_id"]),
        "resolved_year": resolved_year,
        "resolution": [width, height],
        "subtitle_margin_v": subtitle_margin_v,
        "summary": {
            "total_beats": len(beats),
            "prompts_audited": len(prompt_audits) + (1 if thumbnail_prompt_audit else 0),
            "prompt_violations_count": prompt_violations_count,
            "crops_audited": len(crop_audits),
            "crop_violations_count": crop_violations_count,
            "frames_audited": len(frame_audits),
            "frame_failures_count": frame_failures_count,
            "thumbnails_audited": len(thumbnail_audits),
            "thumbnail_failures_count": thumbnail_failures_count,
            "rendered_assets_present": bool(frame_audits or thumbnail_audits or primary_video),
            "v12_gates_passed": v12_gates_report["passed"],
            "v12_failed_gates": v12_gates_report["failed_gates"],
        },
        "v12_hard_gates": v12_gates_report,
        "thumbnail_prompt_audit": thumbnail_prompt_audit,
        "prompt_audits": prompt_audits,
        "crop_audits": crop_audits,
        "frame_audits": frame_audits,
        "thumbnail_audits": thumbnail_audits,
        "blocking_issues": blocking_issues,
    }


# ---------------------------------------------------------------------------
# V12 4 Hard Auto-Fail Visual QC Gates
# ---------------------------------------------------------------------------

V12_GATE_ZERO_BOX_HUD: str = "ZERO_BOX_HUD_GATE"
V12_GATE_SLOW_GIANT_MAP: str = "SLOW_GIANT_MAP_V9_GATE"
V12_GATE_ANTI_SLIDESHOW_60S: str = "ANTI_SLIDESHOW_FIRST60S_GATE"
V12_GATE_LIVE_COVERAGE: str = "LIVE_COVERAGE_DIVERSITY_GATE"

# Gate A thresholds & forbidden boxed HUD / VS badge catalog
FORBIDDEN_BOXED_HUD_KINDS: frozenset[str] = frozenset(
    {
        "v7_stat_versus",
        "v7_hook_headline",
        "prestige_dateline",
        "stat_versus",
        "vs_badge",
        "vs_card",
        "versus_card",
        "pill_badge",
        "dark_pill",
        "dark_banner",
        "rounded_rectangle",
        "boxed_hud",
        "kahoot_quiz",
        "quiz_box",
        "hp_bar",
        "health_bar",
        "cad_modal",
        "sniper_reticle",
        "sniper_crosshair",
        "pov_survival_gauge",
        "myth_vs_chronicle_split",
        "commander_duel_1v1",
        "forensic_evidence_stamp_boxed",
        "weapon_engineering_spec_boxed",
        "counterfactual_branch_stamp_boxed",
    }
)
FORBIDDEN_OVERLAY_MODES: frozenset[str] = frozenset(
    {"legacy", "v7_boxed", "boxed", "hud_boxes", "v7_legacy"}
)

# Gate B thresholds (tactical_battle_map_v9)
MIN_MAP_FONT_HEIGHT_RATIO: float = 0.050
MAX_MAP_WORDS_PER_LABEL: int = 3
MAX_MAP_SIMULTANEOUS_LABELS: int = 2
MIN_MAP_DURATION_SEC: float = 6.0

# Gate C thresholds (Long 0-60s anti-slideshow)
FIRST_15S_MAX_ASL_SEC: float = 3.8
FIRST_60S_FREEZE_DURATION_SEC: float = 3.5
FIRST_60S_FREEZE_NOISE_DB: str = "-50dB"
FIRST_60S_WINDOW_SEC: float = 60.0

STATIC_HOLD_MODES: frozenset[str] = frozenset(
    {
        "static",
        "static_png",
        "static_image",
        "static_jpg",
        "static_hold",
        "tpad_clone",
        "tpad_stop_clone",
        "beluga_static",
        "slideshow",
        "still",
        "still_image",
        "png_hold",
    }
)
ANIMATED_MOTION_MODES: frozenset[str] = frozenset(
    {
        "flow_video",
        "living_clip",
        "veo",
        "veo_3_1_lite",
        "omni",
        "omni_1_2_flash",
        "macaron_cookie",
        "tactical_map_v9",
        "tactical_battle_map_v9",
        "gis_map",
        "tactical_map",
        "analytical_rig",
        "rig_a",
        "rig_b",
        "rig_c",
        "rig_d",
        "rig_e",
        "rig_f",
        "parallax_30fps",
        "multiplane_parallax",
        "gpu_parallax",
        "editorial_stage_cutaway",
        "mp4",
    }
)

# Gate D thresholds & shot-class taxonomy
NON_PORTRAIT_SHOT_CLASSES: frozenset[str] = frozenset(
    {
        "MACRO_PROP",
        "OTS_DIRTY",
        "GROUND_MUD",
        "GODS_EYE",
        "ENV_SENSORY",
        "EDITORIAL_STAGE_CUTAWAY",
    }
)
PORTRAIT_FRONT_BACK_CLASSES: frozenset[str] = frozenset(
    {
        "WIDE_PORTRAIT",
        "MEDIUM_PORTRAIT",
        "FRONT_PORTRAIT",
        "BACK_PORTRAIT",
        "HERO_PORTRAIT",
        "MEDIUM_FRONT",
        "MEDIUM_BACK",
        "WIDE_FRONT",
        "WIDE_BACK",
        "REAR_SILHOUETTE",
        "BACK_OF_HEAD",
        "PORTRAIT",
        "LOW_ANGLE_HERO",
        "WIDE_ESTABLISHING",
        "MEDIUM_TWO_SHOT",
        "ESTABLISHING_WIDE",
    }
)
SHORT_MIN_NON_PORTRAIT_RATIO: float = 0.30
LONG_MIN_MACRO_PROP_RATIO: float = 0.15
MAX_CONSECUTIVE_PORTRAIT_RUN: int = 2  # >= 3 consecutive portrait shots is banned


def _resolve_ffmpeg_bin() -> str | None:
    for cand in ("ffmpeg", "/home/hongphuoc6104/.local/bin/ffmpeg", "/usr/bin/ffmpeg"):
        found = shutil.which(cand)
        if found:
            return found
    return None


def _resolve_ffprobe_bin() -> str | None:
    for cand in ("ffprobe", "/home/hongphuoc6104/.local/bin/ffprobe", "/usr/bin/ffprobe"):
        found = shutil.which(cand)
        if found:
            return found
    return None


def _probe_media_duration(media_path: Path) -> float | None:
    ffprobe = _resolve_ffprobe_bin()
    if not ffprobe or not media_path.is_file():
        return None
    try:
        proc = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(media_path),
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return float(proc.stdout.strip())
    except Exception:
        return None
    return None


def _sample_video_frames(video_path: Path, max_frames: int = 8, max_window_sec: float = 60.0) -> list[tuple[float, Image.Image]]:
    """Extract up to `max_frames` RGB frames from an MP4 file for pixel inspection."""
    ffmpeg = _resolve_ffmpeg_bin()
    if not ffmpeg or not video_path.is_file():
        return []
    dur = _probe_media_duration(video_path) or 10.0
    span = max(0.5, min(dur, max_window_sec))
    count = max(1, min(max_frames, int(round(span))))
    timestamps = [round((span * (i + 0.5)) / count, 3) for i in range(count)]

    sampled: list[tuple[float, Image.Image]] = []
    with tempfile.TemporaryDirectory(prefix="v12_qc_frames_") as tmpdir:
        tmp = Path(tmpdir)
        for idx, ts in enumerate(timestamps):
            out_png = tmp / f"f_{idx:02d}.png"
            proc = subprocess.run(
                [
                    ffmpeg,
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-ss",
                    f"{ts:.3f}",
                    "-i",
                    str(video_path),
                    "-frames:v",
                    "1",
                    "-y",
                    str(out_png),
                ],
                capture_output=True,
                timeout=20,
                check=False,
            )
            if proc.returncode == 0 and out_png.is_file():
                with Image.open(out_png) as im:
                    sampled.append((ts, im.copy()))
    return sampled


def _morph_close_1d_horizontal(mask: np.ndarray, radius: int) -> np.ndarray:
    """Fast 1D horizontal morphological closing (dilate then erode) on a 2D boolean mask."""
    if radius <= 0 or mask.size == 0:
        return mask
    h, w = mask.shape
    k = 2 * radius + 1
    if w <= k:
        return mask

    # Dilate via horizontal sliding sum > 0
    padded = np.pad(mask.astype(np.int32), ((0, 0), (radius, radius)), mode="edge")
    cs = np.cumsum(padded, axis=1)
    cs = np.pad(cs, ((0, 0), (1, 0)), mode="constant", constant_values=0)
    dilated = (cs[:, k:] - cs[:, :-k]) > 0

    # Erode via horizontal sliding sum == k
    padded2 = np.pad(dilated.astype(np.int32), ((0, 0), (radius, radius)), mode="edge")
    cs2 = np.cumsum(padded2, axis=1)
    cs2 = np.pad(cs2, ((0, 0), (1, 0)), mode="constant", constant_values=0)
    eroded = (cs2[:, k:] - cs2[:, :-k]) == k
    return eroded


def _find_connected_bboxes(mask: np.ndarray, min_pixels: int = 100) -> list[tuple[int, int, int, int, int]]:
    """Find axis-aligned bounding boxes (x0, y0, x1, y1, pixel_count) of 4-connected regions."""
    h, w = mask.shape
    visited = np.zeros((h, w), dtype=bool)
    ys, xs = np.nonzero(mask)
    bboxes: list[tuple[int, int, int, int, int]] = []
    for y0, x0 in zip(ys.tolist(), xs.tolist(), strict=True):
        if visited[y0, x0]:
            continue
        stack = [(y0, x0)]
        visited[y0, x0] = True
        min_x = max_x = x0
        min_y = max_y = y0
        count = 0
        while stack:
            cy, cx = stack.pop()
            count += 1
            if cx < min_x:
                min_x = cx
            if cx > max_x:
                max_x = cx
            if cy < min_y:
                min_y = cy
            if cy > max_y:
                max_y = cy
            for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                    visited[ny, nx] = True
                    stack.append((ny, nx))
        if count >= min_pixels:
            bboxes.append((min_x, min_y, max_x + 1, max_y + 1, count))
    return bboxes


def _inspect_image_for_boxed_hud_or_vs(
    image: Image.Image | Path,
    *,
    label: str = "frame",
) -> dict[str, Any]:
    """Pixel-level Gate A detector for dark horizontal pill slabs and red 'VS' plaques."""
    if isinstance(image, (str, Path)):
        p = Path(image)
        if not p.is_file():
            return {"passed": False, "label": label, "issues": ["FILE_NOT_FOUND"], "detections": []}
        with Image.open(p) as im:
            img = im.copy()
    else:
        img = image

    issues: list[str] = []
    detections: list[dict[str, Any]] = []

    orig_w, orig_h = img.size
    has_alpha = img.mode in ("RGBA", "LA")
    if has_alpha:
        rgba = img.convert("RGBA")
        alpha_arr = np.asarray(rgba, dtype=np.float32)[:, :, 3]
        transparent_frac = float(np.mean(alpha_arr < 245.0))
    else:
        rgba = None
        transparent_frac = 0.0

    # Case 1: Standalone RGBA overlay PNG (cropped HUD card OR full-frame transparent overlay)
    if rgba is not None and transparent_frac >= 0.05:
        arr4 = np.asarray(rgba, dtype=np.float32)
        r4, g4, b4, a4 = arr4[:, :, 0], arr4[:, :, 1], arr4[:, :, 2], arr4[:, :, 3]
        luma4 = 0.299 * r4 + 0.587 * g4 + 0.114 * b4
        is_gold4 = (a4 >= 120) & (r4 >= 165) & (g4 >= 125) & (b4 <= 135) & ((r4 - b4) >= 48)
        dark_opaque = (a4 >= 130.0) & (luma4 <= 48.0)

        ys, xs = np.nonzero(dark_opaque)
        if ys.size >= 400:
            by0, by1 = int(ys.min()), int(ys.max()) + 1
            bx0, bx1 = int(xs.min()), int(xs.max()) + 1
            bw, bh = bx1 - bx0, by1 - by0
            fill_density = float(dark_opaque[by0:by1, bx0:bx1].mean())
            opaque_fill_density = float((a4[by0:by1, bx0:bx1] >= 130.0).mean())
            gold_present = bool(np.sum(is_gold4[max(0, by0 - 4) : min(orig_h, by1 + 4), max(0, bx0 - 4) : min(orig_w, bx1 + 4)]) >= max(24, int(0.08 * (bw + bh))))
            is_wide_slab = bw >= max(120, int(orig_w * 0.20)) and bh >= max(24, int(orig_h * 0.03))
            if is_wide_slab and (
                (fill_density >= 0.48 and opaque_fill_density >= 0.72)
                or (fill_density >= 0.35 and gold_present)
            ):
                issues.append("DARK_BOX_HUD_OVERLAY_DETECTED")
                detections.append(
                    {
                        "type": "rgba_dark_box_slab",
                        "bbox": [bx0, by0, bx1, by1],
                        "dark_fill_density": round(fill_density, 3),
                        "opaque_fill_density": round(opaque_fill_density, 3),
                        "gold_accent": gold_present,
                    }
                )

        # Red VS plaque on RGBA overlay
        red_opaque = (a4 >= 140.0) & (r4 >= 145.0) & (g4 <= 85.0) & (b4 <= 80.0) & ((r4 - g4) >= 75.0) & ((r4 - b4) >= 75.0)
        if int(red_opaque.sum()) >= 160:
            rys, rxs = np.nonzero(red_opaque)
            ry0, ry1 = int(rys.min()), int(rys.max()) + 1
            rx0, rx1 = int(rxs.min()), int(rxs.max()) + 1
            rbw, rbh = rx1 - rx0, ry1 - ry0
            bright_in_red = float(((a4[ry0:ry1, rx0:rx1] >= 140.0) & (luma4[ry0:ry1, rx0:rx1] >= 170.0)).mean())
            red_fill = float(red_opaque[ry0:ry1, rx0:rx1].mean())
            if rbw >= 24 and rbh >= 18 and red_fill >= 0.32 and bright_in_red >= 0.025:
                issues.append("RED_VS_PLAQUE_DETECTED")
                detections.append(
                    {
                        "type": "rgba_red_vs_plaque",
                        "bbox": [rx0, ry0, rx1, ry1],
                        "red_fill_density": round(red_fill, 3),
                        "bright_letter_ratio": round(bright_in_red, 3),
                    }
                )

        return {
            "passed": len(issues) == 0,
            "label": label,
            "mode": "rgba_overlay",
            "issues": sorted(set(issues)),
            "detections": detections,
        }

    # Case 2: Composited RGB live frame (or opaque HUD frame)
    rgb = img.convert("RGB")
    target_w = min(orig_w, 640)
    scale = target_w / float(max(1, orig_w))
    target_h = max(64, int(round(orig_h * scale)))
    if target_w != orig_w:
        rgb_small = rgb.resize((target_w, target_h), Image.Resampling.BILINEAR)
    else:
        rgb_small = rgb

    arr = np.asarray(rgb_small, dtype=np.float32)
    h, w, _ = arr.shape
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    luma = 0.299 * r + 0.587 * g + 0.114 * b

    is_dark = luma <= 48.0
    is_gold = (r >= 165.0) & (g >= 125.0) & (b <= 135.0) & ((r - b) >= 48.0) & ((g - b) >= 28.0)
    is_red = (r >= 145.0) & (g <= 85.0) & (b <= 80.0) & ((r - g) >= 75.0) & ((r - b) >= 75.0)

    # 2A: Dark horizontal pill slab / boxed banner detection
    closed_dark = _morph_close_1d_horizontal(is_dark, radius=max(6, int(round(w * 0.028))))
    y_min_scan = max(2, int(round(h * 0.02)))
    y_max_scan = min(h - 3, int(round(h * 0.96)))

    row_spans: dict[int, tuple[int, int]] = {}
    min_slab_w = max(80, int(round(w * 0.28)))
    for y in range(y_min_scan, y_max_scan):
        row = closed_dark[y]
        if int(row.sum()) < min_slab_w:
            continue
        # Longest contiguous True run in this row
        padded = np.concatenate(([False], row, [False]))
        diffs = np.diff(padded.astype(np.int8))
        starts = np.nonzero(diffs == 1)[0]
        ends = np.nonzero(diffs == -1)[0]
        if starts.size == 0:
            continue
        lengths = ends - starts
        best_i = int(np.argmax(lengths))
        if int(lengths[best_i]) >= min_slab_w:
            row_spans[y] = (int(starts[best_i]), int(ends[best_i]))

    # Group contiguous rows with overlapping spans into vertical candidate slabs
    sorted_ys = sorted(row_spans)
    bands: list[list[int]] = []
    for y in sorted_ys:
        if not bands or y > bands[-1][-1] + 2:
            bands.append([y])
        else:
            bands[-1].append(y)

    for band in bands:
        y0, y1 = band[0], band[-1] + 1
        bh = y1 - y0
        if bh < max(12, int(round(h * 0.028))) or bh > int(round(h * 0.32)):
            continue
        xs0 = [row_spans[y][0] for y in band]
        xs1 = [row_spans[y][1] for y in band]
        x0 = int(np.median(xs0))
        x1 = int(np.median(xs1))
        bw = x1 - x0
        if bw < min_slab_w:
            continue

        patch_luma = luma[y0:y1, x0:x1]
        dark_mask = patch_luma <= 48.0
        dark_ratio = float(dark_mask.mean())
        if dark_ratio < 0.50:
            continue

        dark_vals = patch_luma[dark_mask]
        dark_p25, dark_med, dark_p75 = (float(v) for v in np.percentile(dark_vals, [25, 50, 75]))
        dark_iqr = dark_p75 - dark_p25
        if dark_iqr > 16.0:
            continue

        bright_ratio = float((patch_luma >= 145.0).mean())

        # Proof 1: Gold border hairline or left vertical gold stripe (classic V7 pill/box;
        # requires inner bright lettering so empty dark obsidian margins above warm Dó-paper folios never false-positive)
        top_rim = is_gold[max(0, y0 - 3) : min(h, y0 + 3), x0:x1]
        bot_rim = is_gold[max(0, y1 - 3) : min(h, y1 + 3), x0:x1]
        left_edge = is_gold[y0:y1, max(0, x0 - 4) : min(w, x0 + 6)]
        gold_border_proof = bright_ratio >= 0.005 and (
            (top_rim.size > 0 and float(top_rim.any(axis=0).mean()) >= 0.12)
            or (bot_rim.size > 0 and float(bot_rim.any(axis=0).mean()) >= 0.12)
            or (left_edge.size > 0 and float(left_edge.any(axis=1).mean()) >= 0.42)
        )

        # Proof 2: Floating rectangular dark slab over brighter/textured video with lettering
        above_band = luma[max(0, y0 - 6) : max(1, y0 - 1), x0:x1]
        below_band = luma[min(h - 1, y1 + 1) : min(h, y1 + 6), x0:x1]
        above_step = (float(np.mean(above_band)) - dark_med) if above_band.size else 0.0
        below_step = (float(np.mean(below_band)) - dark_med) if below_band.size else 0.0
        sharp_floating_proof = (
            above_step >= 18.0
            and below_step >= 18.0
            and dark_ratio >= 0.72
            and bright_ratio >= 0.006
            and dark_iqr <= 10.0
        )

        if gold_border_proof or sharp_floating_proof:
            issues.append("DARK_HORIZONTAL_PILL_SLAB_DETECTED")
            detections.append(
                {
                    "type": "dark_horizontal_pill_slab",
                    "bbox_scaled": [x0, y0, x1, y1],
                    "bbox_px": [
                        int(round(x0 / scale)),
                        int(round(y0 / scale)),
                        int(round(x1 / scale)),
                        int(round(y1 / scale)),
                    ],
                    "dark_ratio": round(dark_ratio, 3),
                    "dark_iqr": round(dark_iqr, 2),
                    "bright_ratio": round(bright_ratio, 4),
                    "gold_border_proof": gold_border_proof,
                    "sharp_floating_proof": sharp_floating_proof,
                }
            )
            break

    # 2B: Red "VS" plaque detection over live video
    closed_red = _morph_close_1d_horizontal(is_red, radius=max(3, int(round(w * 0.012))))
    red_bboxes = _find_connected_bboxes(closed_red, min_pixels=max(80, int(round(w * h * 0.0004))))
    for rx0, ry0, rx1, ry1, _cnt in red_bboxes:
        rbw, rbh = rx1 - rx0, ry1 - ry0
        if not (max(14, int(w * 0.025)) <= rbw <= int(w * 0.28)):
            continue
        if not (max(12, int(h * 0.018)) <= rbh <= int(h * 0.18)):
            continue
        aspect = rbw / float(max(1, rbh))
        if not (0.50 <= aspect <= 3.5):
            continue
        sub_red = is_red[ry0:ry1, rx0:rx1]
        sub_luma = luma[ry0:ry1, rx0:rx1]
        sub_gold = is_gold[ry0:ry1, rx0:rx1]
        red_frac = float(sub_red.mean())
        bright_letter_frac = float((sub_luma >= 168.0).mean())
        solid_plaque_frac = float((sub_red | (sub_luma >= 168.0) | sub_gold).mean())
        ch, cw = max(2, rbh // 4), max(2, rbw // 4)
        sub_solid_mask = sub_red | (sub_luma >= 168.0)
        corner_fills = (
            float(sub_solid_mask[:ch, :cw].mean()),
            float(sub_solid_mask[:ch, -cw:].mean()),
            float(sub_solid_mask[-ch:, :cw].mean()),
            float(sub_solid_mask[-ch:, -cw:].mean()),
        )
        # Axis-aligned rounded-rect VS plaques fill all 4 outer quadrants (>=0.65), unlike tilted NATO map diamonds
        if red_frac >= 0.34 and bright_letter_frac >= 0.025 and solid_plaque_frac >= 0.60 and min(corner_fills) >= 0.65:
            issues.append("RED_VS_PLAQUE_DETECTED")
            detections.append(
                {
                    "type": "red_vs_plaque",
                    "bbox_scaled": [rx0, ry0, rx1, ry1],
                    "bbox_px": [
                        int(round(rx0 / scale)),
                        int(round(ry0 / scale)),
                        int(round(rx1 / scale)),
                        int(round(ry1 / scale)),
                    ],
                    "red_frac": round(red_frac, 3),
                    "bright_letter_frac": round(bright_letter_frac, 3),
                    "solid_plaque_frac": round(solid_plaque_frac, 3),
                }
            )
            break

    return {
        "passed": len(issues) == 0,
        "label": label,
        "mode": "composited_rgb",
        "issues": sorted(set(issues)),
        "detections": detections,
    }


def _collect_spec_hud_entries(spec: dict[str, Any]) -> list[tuple[str, Any]]:
    entries: list[tuple[str, Any]] = []
    for key in ("hud_stamps", "overlays", "hud_overlays", "style_hud_stamps", "graphics", "cards"):
        val = spec.get(key)
        if isinstance(val, list):
            for idx, item in enumerate(val):
                entries.append((f"{key}[{idx}]", item))
        elif isinstance(val, dict):
            entries.append((key, val))

    for beat in _extract_episode_beats(spec):
        bid = str(beat.get("beat_id") or beat.get("id") or "beat")
        for key in ("hud", "hud_stamp", "hud_stamps", "overlay", "overlays", "card", "stat_card", "vs_card"):
            val = beat.get(key)
            if isinstance(val, list):
                for idx, item in enumerate(val):
                    entries.append((f"{bid}.{key}[{idx}]", item))
            elif val:
                entries.append((f"{bid}.{key}", val))
    return entries


def audit_zero_box_hud_gate(
    spec: dict[str, Any] | None = None,
    *,
    frame_paths: list[Path | str] | None = None,
    video_path: Path | str | None = None,
) -> dict[str, Any]:
    """V12 Gate A (`ZERO_BOX_HUD_GATE`): Reject dark boxed HUDs/VS badges in specs & renders."""
    violations: list[dict[str, Any]] = []
    issues: list[str] = []

    if isinstance(spec, dict):
        # 1. Top-level overlay mode check
        for mode_key in ("overlay_mode", "hud_mode", "v7_hud_mode"):
            m_val = str(spec.get(mode_key) or "").strip().lower()
            if m_val in FORBIDDEN_OVERLAY_MODES:
                issues.append("FORBIDDEN_BOXED_OVERLAY_MODE")
                violations.append({"source": mode_key, "code": "FORBIDDEN_BOXED_OVERLAY_MODE", "value": m_val})

        # 2. Inspect all HUD stamp / overlay definitions
        for loc, item in _collect_spec_hud_entries(spec):
            if isinstance(item, str):
                low = item.strip().lower()
                if low in FORBIDDEN_BOXED_HUD_KINDS or "rounded_rectangle" in low or "vs_badge" in low:
                    issues.append("FORBIDDEN_BOXED_HUD_SPEC")
                    violations.append({"source": loc, "code": "FORBIDDEN_BOXED_HUD_SPEC", "value": item})
                continue
            if not isinstance(item, dict):
                continue

            kind = str(
                item.get("kind")
                or item.get("type")
                or item.get("widget")
                or item.get("template")
                or item.get("style")
                or ""
            ).strip().lower()
            shape = str(item.get("shape") or item.get("container") or item.get("bg_shape") or "").strip().lower()

            if kind in FORBIDDEN_BOXED_HUD_KINDS:
                code = "FORBIDDEN_VS_BADGE_HUD" if "vs" in kind or "versus" in kind else "FORBIDDEN_BOXED_HUD_KIND"
                issues.append(code)
                violations.append({"source": loc, "code": code, "kind": kind})

            if shape in {"rounded_rectangle", "rectangle", "dark_pill", "pill", "box", "dark_banner", "banner_box"}:
                issues.append("FORBIDDEN_ROUNDED_RECTANGLE_BANNER")
                violations.append({"source": loc, "code": "FORBIDDEN_ROUNDED_RECTANGLE_BANNER", "shape": shape})

            # Explicit VS badge or dark box flags
            has_vs = bool(
                item.get("vs_badge")
                or item.get("has_vs_badge")
                or item.get("show_vs_badge")
                or item.get("versus")
                or str(item.get("mode") or "").strip().lower() in {"vs", "versus", "stat_versus"}
                or str(item.get("badge_text") or item.get("center_badge") or "").strip().upper() == "VS"
            )
            if has_vs:
                issues.append("FORBIDDEN_VS_BADGE_HUD")
                violations.append({"source": loc, "code": "FORBIDDEN_VS_BADGE_HUD", "detail": "VS badge requested"})

            has_box = bool(
                item.get("rounded_rectangle")
                or item.get("draw_box")
                or item.get("opaque_box")
                or item.get("background_box")
                or item.get("box_bg")
                or item.get("box_fill")
                or item.get("dark_banner")
                or item.get("left_stripe")
            )
            if has_box:
                issues.append("FORBIDDEN_BOX_CONTAINER_FLAG")
                violations.append({"source": loc, "code": "FORBIDDEN_BOX_CONTAINER_FLAG", "kind": kind or "custom"})

            # Check pill bracket badges like '[SỬ LIỆU CHÍNH THỐNG]'
            combined_txt = " ".join(
                str(item.get(k) or "") for k in ("text", "title", "label", "badge", "header", "subtitle")
            )
            if "[sử liệu chính thống]" in combined_txt.lower():
                issues.append("FORBIDDEN_PILL_BADGE_TEXT")
                violations.append({"source": loc, "code": "FORBIDDEN_PILL_BADGE_TEXT", "text": combined_txt[:80]})

    # 3. Inspect rendered frames / overlay PNGs
    frame_results: list[dict[str, Any]] = []
    for fp in frame_paths or []:
        p = Path(fp)
        res = _inspect_image_for_boxed_hud_or_vs(p, label=p.name)
        frame_results.append(res)
        if not res["passed"]:
            for iss in res["issues"]:
                issues.append(iss)
                violations.append({"source": str(p), "code": iss, "detections": res["detections"]})

    # 4. Inspect sampled frames from rendered MP4
    video_frame_results: list[dict[str, Any]] = []
    if video_path is not None:
        vp = Path(video_path)
        if vp.is_file():
            for ts, frame_im in _sample_video_frames(vp, max_frames=8, max_window_sec=60.0):
                res = _inspect_image_for_boxed_hud_or_vs(frame_im, label=f"{vp.name}@{ts:.2f}s")
                res["timestamp_sec"] = ts
                video_frame_results.append(res)
                if not res["passed"]:
                    for iss in res["issues"]:
                        issues.append(iss)
                        violations.append(
                            {"source": f"{vp.name}@{ts:.2f}s", "code": iss, "detections": res["detections"]}
                        )

    dedup_issues = sorted(set(issues))
    return {
        "gate_id": V12_GATE_ZERO_BOX_HUD,
        "passed": len(dedup_issues) == 0,
        "issues": dedup_issues,
        "violations": violations,
        "frames_checked": len(frame_results),
        "video_frames_checked": len(video_frame_results),
        "frame_results": frame_results,
        "video_frame_results": video_frame_results,
    }


# --- Gate B: SLOW_GIANT_MAP_V9_GATE ---

def _count_map_label_words(text: str) -> int:
    tokens = [t for t in str(text or "").strip().split() if re.search(r"[0-9A-Za-zÀ-ỹ]", t)]
    return len(tokens)


def _extract_map_sequences(spec: dict[str, Any]) -> tuple[list[dict[str, Any]], int, int]:
    """Extract tactical map sequence dicts and canvas (width, height) from a spec or raw map dict."""
    res_str = str(spec.get("resolution") or "").lower()
    fmt_raw = str(spec.get("format_profile") or spec.get("aspect_ratio") or "").lower()
    is_long = "16x9" in fmt_raw or "16:9" in fmt_raw or "long" in fmt_raw or (
        isinstance(spec.get("chapters"), list) and len(spec.get("chapters", [])) > 0
    )
    if "x" in res_str:
        parts = res_str.split("x", 1)
        default_w, default_h = int(parts[0]), int(parts[1])
    elif isinstance(spec.get("width"), int) and isinstance(spec.get("height"), int):
        default_w, default_h = int(spec["width"]), int(spec["height"])
    else:
        default_w, default_h = (1920, 1080) if is_long else (1440, 2560)

    maps: list[dict[str, Any]] = []

    # Direct single-map config dict passed by caller
    if any(
        k in spec
        for k in (
            "preset_id",
            "campaign_preset",
            "act_1_terrain_lock",
            "map_font_height_ratio",
            "callouts",
            "show_tide_bar",
            "show_force_ratio_bar",
        )
    ) and not any(k in spec for k in ("beats", "chapters", "tactical_map_sequences", "tactical_battle_maps")):
        maps.append(dict(spec))
        return maps, default_w, default_h

    for list_key in ("tactical_map_sequences", "tactical_battle_maps", "map_sequences", "tactical_maps"):
        items = spec.get(list_key)
        if isinstance(items, list):
            for idx, m in enumerate(items):
                if isinstance(m, dict):
                    rec = dict(m)
                    rec.setdefault("map_id", f"{list_key}_{idx}")
                    maps.append(rec)

    # Also inspect beats that represent GIS/tactical maps
    seen_beat_ids = {str(m.get("beat_id")) for m in maps if m.get("beat_id")}
    for b in _extract_episode_beats(spec):
        bid = str(b.get("beat_id") or b.get("id") or "")
        st = str(b.get("scene_type") or b.get("beat_type") or b.get("kind") or b.get("asset_mode") or "").lower()
        nested = b.get("tactical_map") or b.get("map_spec")
        is_map_beat = isinstance(nested, dict) or st in {
            "gis_map",
            "tactical_map",
            "tactical_battle_map",
            "tactical_battle_map_v8",
            "tactical_battle_map_v9",
            "scene_map",
            "map",
        }
        if is_map_beat and bid not in seen_beat_ids:
            merged = dict(nested) if isinstance(nested, dict) else {}
            for k in (
                "beat_id",
                "duration_sec",
                "start_sec",
                "end_sec",
                "map_id",
                "map_group_id",
                "split_group_id",
                "seamless_split",
                "seamless_split_group",
                "campaign_preset",
                "preset_id",
                "map_font_height_ratio",
                "font_px",
                "label_font_px",
                "max_words_per_label",
                "max_simultaneous_labels",
                "show_tide_bar",
                "show_side_gauge",
                "show_force_ratio_bar",
                "bottom_troop_bar",
                "labels",
                "callouts",
                "units",
                "act_1_terrain_lock",
                "act_2_units",
                "act_3_maneuver",
                "transition_to_next",
                "transition_mode",
                "height",
                "width",
            ):
                if k in b and k not in merged:
                    merged[k] = b[k]
            merged.setdefault("map_id", bid or f"map_beat_{len(maps)}")
            maps.append(merged)

    return maps, default_w, default_h


def _inspect_map_frame_for_banned_chrome(image: Image.Image | Path, label: str = "map_frame") -> dict[str, Any]:
    """Detect V8 side tide/gorge gauges and bottom split force-ratio bars on rendered map frames."""
    if isinstance(image, (str, Path)):
        p = Path(image)
        if not p.is_file():
            return {"passed": False, "label": label, "issues": ["FILE_NOT_FOUND"]}
        with Image.open(p) as im:
            rgb = im.convert("RGB")
    else:
        rgb = image.convert("RGB")

    w0, h0 = rgb.size
    tw = min(w0, 640)
    th = max(64, int(round(h0 * tw / float(max(1, w0)))))
    arr = np.asarray(rgb.resize((tw, th), Image.Resampling.BILINEAR), dtype=np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    luma = 0.299 * r + 0.587 * g + 0.114 * b

    issues: list[str] = []

    # 1. Left-rail vertical side gauge bar (narrow tall dark rail with bright accent meniscus)
    left_zone = arr[int(th * 0.30) : int(th * 0.80), int(tw * 0.01) : int(tw * 0.14)]
    if left_zone.size > 0:
        lz_luma = luma[int(th * 0.30) : int(th * 0.80), int(tw * 0.01) : int(tw * 0.14)]
        # Look for a narrow vertical track (width 4..28px) that is consistently dark or cyan/amber framed
        col_dark_frac = (lz_luma <= 42.0).mean(axis=0)
        lz_cyan = ((left_zone[:, :, 2] - left_zone[:, :, 0]) >= 35.0) & (left_zone[:, :, 1] >= 90.0)
        lz_gold = (left_zone[:, :, 0] >= 165.0) & (left_zone[:, :, 1] >= 125.0) & (left_zone[:, :, 2] <= 130.0)
        col_accent = (lz_cyan | lz_gold).mean(axis=0)
        dark_cols = int(np.sum(col_dark_frac >= 0.65))
        accent_cols = int(np.sum(col_accent >= 0.20))
        if 2 <= dark_cols <= int(tw * 0.07) and accent_cols >= 2:
            issues.append("MAP_SIDE_GAUGE_CHROME_DETECTED")

    # 2. Bottom horizontal split force-ratio bar (wide crimson + contrasting gold/blue bar near bottom)
    bot_y0, bot_y1 = int(th * 0.78), int(th * 0.96)
    bot_x0, bot_x1 = int(tw * 0.08), int(tw * 0.92)
    bot_r = r[bot_y0:bot_y1, bot_x0:bot_x1]
    bot_g = g[bot_y0:bot_y1, bot_x0:bot_x1]
    bot_b = b[bot_y0:bot_y1, bot_x0:bot_x1]
    is_red_bar = (bot_r >= 140.0) & (bot_g <= 90.0) & (bot_b <= 90.0) & ((bot_r - bot_g) >= 65.0)
    is_gold_or_blue = (
        ((bot_r >= 170.0) & (bot_g >= 130.0) & (bot_b <= 125.0) & ((bot_r - bot_b) >= 50.0))
        | ((bot_b >= 125.0) & (bot_r <= 95.0) & ((bot_b - bot_r) >= 40.0))
    )
    row_red_frac = is_red_bar.mean(axis=1)
    row_other_frac = is_gold_or_blue.mean(axis=1)
    split_bar_rows = int(np.sum((row_red_frac >= 0.15) & (row_other_frac >= 0.15) & ((row_red_frac + row_other_frac) >= 0.45)))
    if split_bar_rows >= max(4, int(th * 0.008)):
        issues.append("MAP_BOTTOM_TROOP_BAR_CHROME_DETECTED")

    return {"passed": len(issues) == 0, "label": label, "issues": issues}


def audit_slow_giant_map_v9_gate(
    spec: dict[str, Any] | None = None,
    *,
    format_profile: str | None = None,
    video_paths: list[Path | str] | None = None,
    frame_paths: list[Path | str] | None = None,
) -> dict[str, Any]:
    """V12 Gate B (`SLOW_GIANT_MAP_V9_GATE`): Font >= 5% H, <= 3 words, <= 2 simultaneous, 0 bars, >= 6s."""
    issues: list[str] = []
    violations: list[dict[str, Any]] = []
    map_audits: list[dict[str, Any]] = []

    is_short = False
    if format_profile:
        is_short = "short" in format_profile.lower() or "9x16" in format_profile.lower()
    elif isinstance(spec, dict):
        fmt_raw = str(spec.get("format_profile") or spec.get("aspect_ratio") or "").lower()
        is_short = "short" in fmt_raw or "9x16" in fmt_raw or (
            not ("long" in fmt_raw or "16x9" in fmt_raw or spec.get("chapters"))
        )

    if isinstance(spec, dict):
        maps, default_w, default_h = _extract_map_sequences(spec)

        # Group Short seamless 2-beat splits for combined >= 6.0s duration validation
        split_groups: dict[str, list[dict[str, Any]]] = {}
        for idx, m in enumerate(maps):
            gid = str(
                m.get("split_group_id")
                or m.get("map_group_id")
                or m.get("seamless_split_group")
                or ""
            ).strip()
            if gid:
                split_groups.setdefault(gid, []).append(m)
            elif is_short and m.get("seamless_split"):
                # Pair with previous seamless_split map if same preset or adjacent
                pair_key = f"__auto_pair_{m.get('campaign_preset') or m.get('preset_id') or idx // 2}"
                split_groups.setdefault(pair_key, []).append(m)

        for idx, m in enumerate(maps):
            mid = str(m.get("map_id") or m.get("beat_id") or m.get("preset_id") or f"MAP_{idx:02d}")
            mh = int(m.get("height") or default_h)
            m_issues: list[str] = []

            # 1. Font height ratio >= 0.050 (>= 5.0% H)
            ratios: list[float] = []
            if m.get("map_font_height_ratio") is not None:
                ratios.append(float(m["map_font_height_ratio"]))
            for fk in (
                "font_px",
                "primary_font_px",
                "label_font_px",
                "title_font_px",
                "unit_font_px",
                "callout_font_px",
                "stamp_font_px",
                "font_size_px",
                "min_font_px",
            ):
                if m.get(fk) is not None:
                    ratios.append(float(m[fk]) / float(max(1, mh)))

            engine_mode = str(m.get("engine_mode") or m.get("map_version") or m.get("version") or "").lower()
            if engine_mode in {"v8", "v8_legacy", "tactical_battle_map_v8_legacy"} and not ratios:
                m_issues.append("LEGACY_V8_TINY_MAP_ENGINE")
                violations.append({"map_id": mid, "code": "LEGACY_V8_TINY_MAP_ENGINE", "engine_mode": engine_mode})

            min_font_ratio = min(ratios) if ratios else None
            if min_font_ratio is not None and min_font_ratio < MIN_MAP_FONT_HEIGHT_RATIO - 1e-6:
                m_issues.append("MAP_FONT_HEIGHT_BELOW_5PCT")
                violations.append(
                    {
                        "map_id": mid,
                        "code": "MAP_FONT_HEIGHT_BELOW_5PCT",
                        "observed_ratio": round(min_font_ratio, 4),
                        "required_min": MIN_MAP_FONT_HEIGHT_RATIO,
                    }
                )

            # 2. Label word count <= 3 & zero multiline/sub captions
            label_texts: list[str] = []
            staged_intervals: list[tuple[float, float]] = []

            def _add_label(
                txt: Any,
                t0: float = 0.0,
                t1: float = 1.0,
                *,
                source: str = "label",
                _mid: str = mid,
                _labels: list[str] = label_texts,
                _intervals: list[tuple[float, float]] = staged_intervals,
                _issues: list[str] = m_issues,
            ) -> None:
                s = str(txt or "").strip()
                if not s:
                    return
                _labels.append(s)
                _intervals.append((t0, t1))
                if "\n" in s:
                    _issues.append("MAP_LABEL_MULTILINE_FORBIDDEN")
                    violations.append({"map_id": _mid, "code": "MAP_LABEL_MULTILINE_FORBIDDEN", "source": source, "label": s})
                wc = _count_map_label_words(s)
                if wc > MAX_MAP_WORDS_PER_LABEL:
                    _issues.append("MAP_LABEL_EXCEEDS_3_WORDS")
                    violations.append(
                        {
                            "map_id": _mid,
                            "code": "MAP_LABEL_EXCEEDS_3_WORDS",
                            "source": source,
                            "label": s,
                            "word_count": wc,
                        }
                    )

            # V9 3-act structured schema
            act1 = m.get("act_1_terrain_lock")
            if isinstance(act1, dict):
                _add_label(act1.get("theater_stamp"), 0.0, 0.28, source="act_1.theater_stamp")
                pin = act1.get("landmark_pin")
                if isinstance(pin, dict):
                    _add_label(pin.get("label"), 0.0, 0.28, source="act_1.landmark_pin")
            act2 = m.get("act_2_units")
            if isinstance(act2, list):
                for u_i, u in enumerate(act2):
                    if isinstance(u, dict):
                        _add_label(u.get("label") or u.get("badge"), 0.28, 0.61, source=f"act_2_units[{u_i}]")
            act3 = m.get("act_3_maneuver")
            if isinstance(act3, dict):
                _add_label(act3.get("impact_stamp"), 0.61, 1.0, source="act_3.impact_stamp")

            # Generic lists: labels, callouts, units
            for list_field in ("labels", "callouts", "units"):
                arr_items = m.get(list_field)
                if not isinstance(arr_items, list):
                    continue
                for item_i, item in enumerate(arr_items):
                    if isinstance(item, str):
                        _add_label(item, 0.0, 1.0, source=f"{list_field}[{item_i}]")
                    elif isinstance(item, dict):
                        t0 = float(item.get("t_appear") if item.get("t_appear") is not None else item.get("t_start", 0.0))
                        t1 = float(item.get("t_disappear") if item.get("t_disappear") is not None else item.get("t_end", 1.0))
                        txt = item.get("label") or item.get("text") or item.get("badge") or item.get("name") or ""
                        _add_label(txt, t0, t1, source=f"{list_field}[{item_i}]")
                        sub = str(item.get("sub") or item.get("subtitle") or "").strip()
                        if sub:
                            m_issues.append("MAP_CALLOUT_SUBLINE_FORBIDDEN")
                            violations.append(
                                {
                                    "map_id": mid,
                                    "code": "MAP_CALLOUT_SUBLINE_FORBIDDEN",
                                    "source": f"{list_field}[{item_i}].sub",
                                    "sub": sub,
                                }
                            )

            for top_lbl_key in ("theater_stamp", "impact_stamp", "phase_label"):
                if m.get(top_lbl_key):
                    if top_lbl_key == "phase_label":
                        m_issues.append("MAP_PHASE_SUBHEADER_FORBIDDEN")
                        violations.append({"map_id": mid, "code": "MAP_PHASE_SUBHEADER_FORBIDDEN", "phase_label": m[top_lbl_key]})
                    else:
                        _add_label(m[top_lbl_key], 0.0, 0.30 if top_lbl_key == "theater_stamp" else 0.70, source=top_lbl_key)

            if m.get("max_words_per_label") is not None and int(m["max_words_per_label"]) > MAX_MAP_WORDS_PER_LABEL:
                m_issues.append("MAP_LABEL_EXCEEDS_3_WORDS")
                violations.append(
                    {
                        "map_id": mid,
                        "code": "MAP_LABEL_EXCEEDS_3_WORDS",
                        "declared_max_words": int(m["max_words_per_label"]),
                    }
                )

            # 3. Simultaneous labels <= 2
            peak_simultaneous = 0
            if staged_intervals:
                sample_pts = sorted(
                    {round(i / 40.0, 4) for i in range(41)}
                    | {round(t0 + 1e-4, 5) for t0, _t1 in staged_intervals}
                )
                for pt in sample_pts:
                    active = sum(1 for t0, t1 in staged_intervals if t0 <= pt < t1 or (pt == 1.0 and t1 >= 1.0 and t0 < 1.0))
                    if active > peak_simultaneous:
                        peak_simultaneous = active

            declared_sim = m.get("max_simultaneous_labels")
            if declared_sim is not None:
                peak_simultaneous = max(peak_simultaneous, int(declared_sim))

            if peak_simultaneous > MAX_MAP_SIMULTANEOUS_LABELS:
                m_issues.append("MAP_TOO_MANY_SIMULTANEOUS_LABELS")
                violations.append(
                    {
                        "map_id": mid,
                        "code": "MAP_TOO_MANY_SIMULTANEOUS_LABELS",
                        "peak_simultaneous": peak_simultaneous,
                        "allowed_max": MAX_MAP_SIMULTANEOUS_LABELS,
                    }
                )

            # 4. Zero side gauges & zero bottom troop bars
            has_side_gauge = bool(
                m.get("show_tide_bar")
                or m.get("show_side_gauge")
                or m.get("side_gauge")
                or m.get("tide_gauge")
                or m.get("elevation_gauge")
                or m.get("show_gorge_gauge")
                or int(m.get("side_gauges_count") or 0) > 0
            )
            if has_side_gauge:
                m_issues.append("MAP_SIDE_GAUGE_FORBIDDEN")
                violations.append({"map_id": mid, "code": "MAP_SIDE_GAUGE_FORBIDDEN"})

            has_bottom_bar = bool(
                m.get("show_force_ratio_bar")
                or m.get("bottom_troop_bar")
                or m.get("force_ratio_bar")
                or m.get("bottom_force_bar")
                or m.get("show_troop_bar")
                or m.get("troop_ratio_bar")
                or int(m.get("bottom_bars_count") or 0) > 0
            )
            if has_bottom_bar:
                m_issues.append("MAP_BOTTOM_TROOP_BAR_FORBIDDEN")
                violations.append({"map_id": mid, "code": "MAP_BOTTOM_TROOP_BAR_FORBIDDEN"})

            if m.get("show_phase_subheader"):
                m_issues.append("MAP_PHASE_SUBHEADER_FORBIDDEN")
                violations.append({"map_id": mid, "code": "MAP_PHASE_SUBHEADER_FORBIDDEN"})

            # 5. Duration >= 6.0s (or seamless 2-beat split totaling >= 6.0s on Shorts)
            dur = m.get("duration_sec")
            if dur is None and m.get("end_sec") is not None and m.get("start_sec") is not None:
                dur = float(m["end_sec"]) - float(m["start_sec"])
            effective_dur = float(dur) if dur is not None else None

            if effective_dur is not None:
                # Check if part of a Short 2-beat seamless split group
                gid = str(
                    m.get("split_group_id")
                    or m.get("map_group_id")
                    or m.get("seamless_split_group")
                    or ""
                ).strip()
                if not gid and is_short and m.get("seamless_split"):
                    gid = f"__auto_pair_{m.get('campaign_preset') or m.get('preset_id') or idx // 2}"
                if is_short and gid and gid in split_groups and len(split_groups[gid]) == 2:
                    group_total = sum(
                        float(
                            gm.get("duration_sec")
                            if gm.get("duration_sec") is not None
                            else (float(gm.get("end_sec", 0.0)) - float(gm.get("start_sec", 0.0)))
                        )
                        for gm in split_groups[gid]
                    )
                    if group_total < MIN_MAP_DURATION_SEC - 1e-6:
                        m_issues.append("MAP_DURATION_BELOW_6S")
                        violations.append(
                            {
                                "map_id": mid,
                                "code": "MAP_DURATION_BELOW_6S",
                                "split_group_id": gid,
                                "combined_duration_sec": round(group_total, 3),
                                "required_min": MIN_MAP_DURATION_SEC,
                            }
                        )
                elif effective_dur < MIN_MAP_DURATION_SEC - 1e-6:
                    m_issues.append("MAP_DURATION_BELOW_6S")
                    violations.append(
                        {
                            "map_id": mid,
                            "code": "MAP_DURATION_BELOW_6S",
                            "duration_sec": round(effective_dur, 3),
                            "required_min": MIN_MAP_DURATION_SEC,
                        }
                    )

            dedup_m = sorted(set(m_issues))
            issues.extend(dedup_m)
            map_audits.append(
                {
                    "map_id": mid,
                    "passed": len(dedup_m) == 0,
                    "min_font_height_ratio": round(min_font_ratio, 4) if min_font_ratio is not None else None,
                    "peak_simultaneous_labels": peak_simultaneous,
                    "duration_sec": effective_dur,
                    "issues": dedup_m,
                }
            )

    # 6. Audit rendered map MP4s (duration >= 6.0s + mid-frame chrome check)
    media_audits: list[dict[str, Any]] = []
    if video_paths:
        probed_durs: list[tuple[Path, float | None]] = []
        for vp_raw in video_paths:
            vp = Path(vp_raw)
            dur = _probe_media_duration(vp)
            probed_durs.append((vp, dur))
        # On Shorts with exactly 2 split map clips, combined >= 6.0s passes
        combined_short_split = (
            is_short
            and len(probed_durs) == 2
            and all(d is not None for _, d in probed_durs)
            and sum(float(d or 0.0) for _, d in probed_durs) >= MIN_MAP_DURATION_SEC - 1e-3
        )
        for vp, dur in probed_durs:
            v_issues: list[str] = []
            if not vp.is_file():
                v_issues.append("MAP_VIDEO_NOT_FOUND")
            elif dur is not None and dur < MIN_MAP_DURATION_SEC - 1e-3 and not combined_short_split:
                v_issues.append("MAP_VIDEO_DURATION_BELOW_6S")
                violations.append(
                    {"source": str(vp), "code": "MAP_VIDEO_DURATION_BELOW_6S", "duration_sec": round(dur, 3)}
                )
            for ts, fim in _sample_video_frames(vp, max_frames=3, max_window_sec=dur or 10.0):
                cr = _inspect_map_frame_for_banned_chrome(fim, label=f"{vp.name}@{ts:.2f}s")
                if not cr["passed"]:
                    v_issues.extend(cr["issues"])
                    for iss in cr["issues"]:
                        violations.append({"source": f"{vp.name}@{ts:.2f}s", "code": iss})
            dedup_v = sorted(set(v_issues))
            issues.extend(dedup_v)
            media_audits.append({"path": str(vp), "duration_sec": dur, "passed": len(dedup_v) == 0, "issues": dedup_v})

    # 7. Audit rendered map PNGs
    for fp_raw in frame_paths or []:
        fp = Path(fp_raw)
        cr = _inspect_map_frame_for_banned_chrome(fp, label=fp.name)
        media_audits.append(cr)
        if not cr["passed"]:
            issues.extend(cr["issues"])
            for iss in cr["issues"]:
                violations.append({"source": str(fp), "code": iss})

    dedup_all = sorted(set(issues))
    return {
        "gate_id": V12_GATE_SLOW_GIANT_MAP,
        "passed": len(dedup_all) == 0,
        "format": "short_9x16" if is_short else "long_16x9",
        "maps_audited": len(map_audits),
        "media_audited": len(media_audits),
        "issues": dedup_all,
        "violations": violations,
        "map_audits": map_audits,
        "media_audits": media_audits,
    }


# --- Gate C: ANTI_SLIDESHOW_FIRST60S_GATE ---

def _run_ffmpeg_freezedetect_first60s(
    video_path: Path,
    *,
    noise_db: str = FIRST_60S_FREEZE_NOISE_DB,
    min_freeze_sec: float = FIRST_60S_FREEZE_DURATION_SEC,
    window_sec: float = FIRST_60S_WINDOW_SEC,
) -> dict[str, Any]:
    """Run `ffmpeg freezedetect=n=-50dB:d=3.5` on `0.0s-60.0s` of a rendered Long MP4."""
    ffmpeg = _resolve_ffmpeg_bin()
    if not video_path.is_file():
        return {"ok": False, "error": "VIDEO_NOT_FOUND", "freeze_events": [], "ffmpeg_filter": ""}
    if not ffmpeg:
        return {"ok": False, "error": "FFMPEG_NOT_AVAILABLE", "freeze_events": [], "ffmpeg_filter": ""}

    vf_expr = f"freezedetect=n={noise_db}:d={min_freeze_sec}"
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-nostats",
        "-t",
        f"{window_sec:.2f}",
        "-i",
        str(video_path),
        "-vf",
        vf_expr,
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
    stderr = proc.stderr or ""
    vid_dur = _probe_media_duration(video_path) or window_sec
    effective_end = min(window_sec, vid_dur)

    events: list[dict[str, float]] = []
    pending_start: float | None = None
    for line in stderr.splitlines():
        m_start = re.search(r"freeze_start:\s*([0-9]+(?:\.[0-9]+)?)", line)
        if m_start:
            pending_start = float(m_start.group(1))
            continue
        m_end = re.search(r"freeze_end:\s*([0-9]+(?:\.[0-9]+)?)", line)
        if m_end:
            f_end = float(m_end.group(1))
            f_start = pending_start if pending_start is not None else max(0.0, f_end - min_freeze_sec)
            events.append({"start_sec": round(f_start, 3), "end_sec": round(f_end, 3), "duration_sec": round(max(0.0, f_end - f_start), 3)})
            pending_start = None
            continue
        m_dur = re.search(r"freeze_duration:\s*([0-9]+(?:\.[0-9]+)?)", line)
        if m_dur and events:
            events[-1]["duration_sec"] = round(float(m_dur.group(1)), 3)

    # Handle freeze running all the way to EOF / 60s trim cutoff
    if pending_start is not None:
        dur_tail = max(0.0, effective_end - pending_start)
        if dur_tail >= min_freeze_sec - 0.15:
            events.append(
                {
                    "start_sec": round(pending_start, 3),
                    "end_sec": round(effective_end, 3),
                    "duration_sec": round(dur_tail, 3),
                }
            )

    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "ffmpeg_filter": vf_expr,
        "window_sec": effective_end,
        "freeze_events": events,
    }


def _beat_is_static_png_hold(beat: dict[str, Any]) -> bool:
    """Return True if beat metadata indicates a static PNG/image hold (no 30fps motion)."""
    if beat.get("is_static") or beat.get("static_hold") or beat.get("tpad_clone"):
        return True
    for key in ("asset_mode", "render_mode", "source_type", "media_type", "motion_engine", "engine"):
        val = str(beat.get(key) or "").strip().lower()
        if val in STATIC_HOLD_MODES:
            return True
    # Check image file path without a real 30fps motion engine
    motion_val = str(
        beat.get("motion_engine")
        or beat.get("render_mode")
        or beat.get("asset_mode")
        or beat.get("source_type")
        or ""
    ).strip().lower()
    if motion_val in ANIMATED_MOTION_MODES:
        return False
    for path_key in ("asset_path", "media_path", "source_path", "image_path"):
        p_val = str(beat.get(path_key) or "").strip().lower()
        if p_val.endswith((".png", ".jpg", ".jpeg", ".webp")):
            return True
    return False


def audit_anti_slideshow_first60s_gate(
    spec: dict[str, Any] | None = None,
    *,
    video_path: Path | str | None = None,
    format_profile: str | None = None,
) -> dict[str, Any]:
    """V12 Gate C (`ANTI_SLIDESHOW_FIRST60S_GATE`): Zero slideshow freezes/PNG holds in Long 0-60s + 0-15s ASL <= 3.8s."""
    # Determine whether this is Long format
    is_long = False
    if format_profile:
        fl = format_profile.lower()
        is_long = "long" in fl or "16x9" in fl or "16:9" in fl
    elif isinstance(spec, dict):
        fl = str(spec.get("format_profile") or spec.get("aspect_ratio") or "").lower()
        is_long = (
            "long" in fl
            or "16x9" in fl
            or "16:9" in fl
            or (isinstance(spec.get("chapters"), list) and len(spec.get("chapters", [])) > 0)
            or spec.get("cold_open") is not None
        )
    elif video_path is not None:
        is_long = True

    if not is_long:
        return {
            "gate_id": V12_GATE_ANTI_SLIDESHOW_60S,
            "passed": True,
            "skipped": True,
            "reason": "SHORT_FORMAT_EXEMPT",
            "issues": [],
            "violations": [],
        }

    issues: list[str] = []
    violations: list[dict[str, Any]] = []
    asl_0_15s: float | None = None
    static_png_beats_0_60s: list[str] = []
    first15s_beat_count = 0
    first60s_beat_count = 0

    if isinstance(spec, dict):
        if str(spec.get("fx_mode") or "").strip().lower() == "static":
            issues.append("LONG_STATIC_FX_MODE_FORBIDDEN")
            violations.append({"source": "spec.fx_mode", "code": "LONG_STATIC_FX_MODE_FORBIDDEN"})
        if int(spec.get("cold_open_static_holds") or 0) > 0 or int(spec.get("first_60s_static_png_count") or 0) > 0:
            issues.append("STATIC_PNG_HOLD_IN_FIRST60S")
            violations.append({"source": "spec", "code": "STATIC_PNG_HOLD_IN_FIRST60S"})

        beats = _extract_episode_beats(spec)
        cursor = 0.0
        first15_durs: list[float] = []
        for b in beats:
            bid = str(b.get("beat_id") or b.get("id") or "beat")
            if b.get("start_sec") is not None and b.get("end_sec") is not None:
                t0 = float(b["start_sec"])
                t1 = float(b["end_sec"])
                dur = max(0.0, t1 - t0)
                cursor = max(cursor, t1)
            elif b.get("duration_sec") is not None:
                dur = float(b["duration_sec"])
                t0 = cursor
                t1 = cursor + dur
                cursor = t1
            else:
                # No explicit timing on beat; treat within 0-60s only for static check
                t0 = cursor
                dur = 0.0
                t1 = cursor

            in_first60 = t0 < FIRST_60S_WINDOW_SEC - 1e-6
            in_first15 = t0 < 15.0 - 1e-6

            if in_first60:
                first60s_beat_count += 1
                if _beat_is_static_png_hold(b):
                    static_png_beats_0_60s.append(bid)
                    issues.append("STATIC_PNG_HOLD_IN_FIRST60S")
                    violations.append(
                        {
                            "beat_id": bid,
                            "code": "STATIC_PNG_HOLD_IN_FIRST60S",
                            "t_start": round(t0, 2),
                            "duration_sec": round(dur, 2),
                        }
                    )

            if in_first15 and dur > 0.0:
                first15s_beat_count += 1
                first15_durs.append(dur)

        if first15_durs:
            asl_0_15s = round(sum(first15_durs) / len(first15_durs), 3)
            if asl_0_15s > FIRST_15S_MAX_ASL_SEC + 1e-6:
                issues.append("FIRST15S_ASL_EXCEEDS_3_8S")
                violations.append(
                    {
                        "code": "FIRST15S_ASL_EXCEEDS_3_8S",
                        "observed_asl_sec": asl_0_15s,
                        "max_allowed_asl_sec": FIRST_15S_MAX_ASL_SEC,
                        "beats_in_0_15s": len(first15_durs),
                    }
                )

    # Real FFmpeg freezedetect=n=-50dB:d=3.5 on 0.0s-60.0s of rendered Long MP4
    freezedetect_report: dict[str, Any] | None = None
    if video_path is not None:
        vp = Path(video_path)
        freezedetect_report = _run_ffmpeg_freezedetect_first60s(vp)
        if not freezedetect_report.get("ok"):
            issues.append(f"FREEZEDETECT_ERROR:{freezedetect_report.get('error', 'FAILED')}")
            violations.append({"source": str(vp), "code": "FREEZEDETECT_ERROR", "detail": freezedetect_report})
        elif freezedetect_report.get("freeze_events"):
            issues.append("SLIDESHOW_FREEZE_DETECTED_FIRST60S")
            for ev in freezedetect_report["freeze_events"]:
                violations.append(
                    {
                        "source": str(vp),
                        "code": "SLIDESHOW_FREEZE_DETECTED_FIRST60S",
                        "start_sec": ev["start_sec"],
                        "end_sec": ev["end_sec"],
                        "duration_sec": ev["duration_sec"],
                    }
                )

    dedup = sorted(set(issues))
    return {
        "gate_id": V12_GATE_ANTI_SLIDESHOW_60S,
        "passed": len(dedup) == 0,
        "skipped": False,
        "asl_0_15s": asl_0_15s,
        "first15s_beat_count": first15s_beat_count,
        "first60s_beat_count": first60s_beat_count,
        "static_png_beats_0_60s": static_png_beats_0_60s,
        "freezedetect": freezedetect_report,
        "issues": dedup,
        "violations": violations,
    }


# --- Gate D: LIVE_COVERAGE_DIVERSITY_GATE ---

_SHOT_CLASS_ALIASES: dict[str, str] = {
    "MACRO_PROP": "MACRO_PROP",
    "MACRO_TACTILE": "MACRO_PROP",
    "TIGHT_ACTION_MACRO": "MACRO_PROP",
    "MACRO_INSERT": "MACRO_PROP",
    "PROP_MACRO": "MACRO_PROP",
    "EXTREME_MACRO": "MACRO_PROP",
    "OTS_DIRTY": "OTS_DIRTY",
    "OVER_THE_SHOULDER": "OTS_DIRTY",
    "OTS": "OTS_DIRTY",
    "DIRTY_SINGLE": "OTS_DIRTY",
    "MEDIUM_OTS": "OTS_DIRTY",
    "GROUND_MUD": "GROUND_MUD",
    "GROUND_LEVEL": "GROUND_MUD",
    "BOOTS_IN_MUD": "GROUND_MUD",
    "ANKLE_HEIGHT": "GROUND_MUD",
    "GODS_EYE": "GODS_EYE",
    "BIRDS_EYE": "GODS_EYE",
    "OVERHEAD": "GODS_EYE",
    "TOP_DOWN": "GODS_EYE",
    "ENV_SENSORY": "ENV_SENSORY",
    "ENVIRONMENTAL_BROLL": "ENV_SENSORY",
    "SENSORY_BROLL": "ENV_SENSORY",
    "ENVIRONMENT_ONLY": "ENV_SENSORY",
    "ATMOSPHERIC_LANDSCAPE": "ENV_SENSORY",
    "EDITORIAL_STAGE_CUTAWAY": "EDITORIAL_STAGE_CUTAWAY",
    "ANALYTICAL_RIG": "EDITORIAL_STAGE_CUTAWAY",
    "OBSIDIAN_STAGE": "EDITORIAL_STAGE_CUTAWAY",
    "DO_PAPER_RIG": "EDITORIAL_STAGE_CUTAWAY",
    "CHRONICLE_PLATE": "EDITORIAL_STAGE_CUTAWAY",
    "RIG_A": "EDITORIAL_STAGE_CUTAWAY",
    "RIG_B": "EDITORIAL_STAGE_CUTAWAY",
    "RIG_C": "EDITORIAL_STAGE_CUTAWAY",
    "RIG_D": "EDITORIAL_STAGE_CUTAWAY",
    "RIG_E": "EDITORIAL_STAGE_CUTAWAY",
    "RIG_F": "EDITORIAL_STAGE_CUTAWAY",
    "REACTION_MICRO": "REACTION_MICRO",
    "ECU_EYES": "REACTION_MICRO",
    "MICRO_REACTION": "REACTION_MICRO",
    "TACTICAL_MAP": "TACTICAL_MAP",
    "GIS_MAP": "TACTICAL_MAP",
    "MAP_V9": "TACTICAL_MAP",
    "TACTICAL_MAP_V9": "TACTICAL_MAP",
}


def classify_beat_shot_class(beat: dict[str, Any]) -> str:
    """Resolve canonical V12 shot class from explicit beat metadata or visual prompt text."""
    for key in ("shot_class", "coverage_class", "camera_shot_class", "shot_type", "camera_slot", "shot_category"):
        raw = str(beat.get(key) or "").strip()
        if raw:
            norm = re.sub(r"[\s\-/]+", "_", _strip_diacritics(raw).upper()).strip("_")
            if norm in _SHOT_CLASS_ALIASES:
                return _SHOT_CLASS_ALIASES[norm]
            if norm in NON_PORTRAIT_SHOT_CLASSES or norm in PORTRAIT_FRONT_BACK_CLASSES:
                return norm

    st = str(beat.get("scene_type") or beat.get("beat_type") or beat.get("kind") or "").strip().lower()
    if st in {"gis_map", "tactical_map", "tactical_battle_map", "tactical_battle_map_v9", "scene_map", "map"}:
        return "TACTICAL_MAP"
    if st in {"chapter_card", "title_card"}:
        return "CHAPTER_CARD"
    if st in {"analytical_rig", "editorial_stage", "chronicle_plate", "editorial_stage_cutaway"}:
        return "EDITORIAL_STAGE_CUTAWAY"

    prompt_low = str(
        beat.get("visual_prompt") or beat.get("prompt") or beat.get("image_prompt") or ""
    ).lower()

    if any(
        kw in prompt_low
        for kw in (
            "100mm macro",
            "135mm macro",
            "extreme macro",
            "macro close-up",
            "macro insert",
            "no human face",
            "zero-face",
            "zero face",
            "cinnabar seal",
            "trigger mechanism",
            "wood shavings",
            "close-up of hands",
            "muddy calloused fingers",
        )
    ):
        return "MACRO_PROP"
    if any(kw in prompt_low for kw in ("over-the-shoulder", "over the shoulder", "ots ", "past shoulder", "behind shoulder")):
        return "OTS_DIRTY"
    if any(kw in prompt_low for kw in ("ground-level", "ground level", "ankle height", "boots in mud", "boot-level", "hooves")):
        return "GROUND_MUD"
    if any(kw in prompt_low for kw in ("god's-eye", "gods eye", "bird's-eye", "birds eye", "perpendicular overhead", "looking straight down", "directly overhead")):
        return "GODS_EYE"
    if any(kw in prompt_low for kw in ("no human figures", "zero human", "environmental b-roll", "empty battlefield", "rain streaming down", "terracotta roof", "river current swirling")):
        return "ENV_SENSORY"
    if any(kw in prompt_low for kw in ("obsidian spotlight", "editorial stage", "analytical canvas", "parchment plate", "dỏ paper", "dó paper", "cross-section rig")):
        return "EDITORIAL_STAGE_CUTAWAY"
    if any(kw in prompt_low for kw in ("extreme close-up", "ecu ", "eyes filling", "razor-thin depth of field on the iris", "jaw clenching", "bead of sweat")):
        return "REACTION_MICRO"
    if any(kw in prompt_low for kw in ("rear silhouette", "from behind", "back of head", "back view")):
        return "BACK_PORTRAIT"
    if any(kw in prompt_low for kw in ("wide shot", "wide establishing", "wide 35mm", "wide 28mm")):
        return "WIDE_PORTRAIT"
    return "MEDIUM_PORTRAIT"


def audit_live_coverage_diversity_gate(
    spec: dict[str, Any] | None = None,
    *,
    beats: list[dict[str, Any]] | None = None,
    format_profile: str | None = None,
) -> dict[str, Any]:
    """V12 Gate D (`LIVE_COVERAGE_DIVERSITY_GATE`): Enforce non-portrait/macro ratios and ban >=3 consecutive portraits."""
    if format_profile:
        is_long = "long" in format_profile.lower() or "16x9" in format_profile.lower() or "16:9" in format_profile.lower()
    elif isinstance(spec, dict):
        fl = str(spec.get("format_profile") or spec.get("aspect_ratio") or "").lower()
        is_long = (
            "long" in fl
            or "16x9" in fl
            or "16:9" in fl
            or (isinstance(spec.get("chapters"), list) and len(spec.get("chapters", [])) > 0)
        )
    else:
        is_long = False

    raw_beats = list(beats) if beats is not None else (_extract_episode_beats(spec) if isinstance(spec, dict) else [])

    classified: list[dict[str, Any]] = []
    live_beats: list[dict[str, Any]] = []
    for idx, b in enumerate(raw_beats):
        if not isinstance(b, dict):
            continue
        bid = str(b.get("beat_id") or b.get("id") or f"B{idx:02d}")
        scls = classify_beat_shot_class(b)
        rec = {"beat_id": bid, "shot_class": scls}
        classified.append(rec)
        if scls not in {"TACTICAL_MAP", "CHAPTER_CARD"}:
            live_beats.append(rec)

    issues: list[str] = []
    violations: list[dict[str, Any]] = []
    total_live = len(live_beats)

    if total_live == 0:
        return {
            "gate_id": V12_GATE_LIVE_COVERAGE,
            "passed": True,
            "format": "long_16x9" if is_long else "short_9x16",
            "total_live_beats": 0,
            "non_portrait_ratio": 0.0,
            "macro_prop_ratio": 0.0,
            "max_consecutive_portrait_run": 0,
            "shot_class_counts": {},
            "issues": [],
            "violations": [],
        }

    counts: dict[str, int] = {}
    for rec in live_beats:
        counts[rec["shot_class"]] = counts.get(rec["shot_class"], 0) + 1

    non_portrait_count = sum(1 for rec in live_beats if rec["shot_class"] in NON_PORTRAIT_SHOT_CLASSES)
    macro_prop_count = counts.get("MACRO_PROP", 0)
    non_portrait_ratio = round(non_portrait_count / float(total_live), 4)
    macro_prop_ratio = round(macro_prop_count / float(total_live), 4)

    # 1. Format-specific non-portrait / macro coverage floor
    if is_long:
        if macro_prop_ratio < LONG_MIN_MACRO_PROP_RATIO - 1e-6:
            issues.append("LONG_MACRO_PROP_COVERAGE_BELOW_15PCT")
            violations.append(
                {
                    "code": "LONG_MACRO_PROP_COVERAGE_BELOW_15PCT",
                    "observed_ratio": macro_prop_ratio,
                    "required_min": LONG_MIN_MACRO_PROP_RATIO,
                    "macro_prop_count": macro_prop_count,
                    "total_live_beats": total_live,
                }
            )
    else:
        if non_portrait_ratio < SHORT_MIN_NON_PORTRAIT_RATIO - 1e-6:
            issues.append("SHORT_NON_PORTRAIT_COVERAGE_BELOW_30PCT")
            violations.append(
                {
                    "code": "SHORT_NON_PORTRAIT_COVERAGE_BELOW_30PCT",
                    "observed_ratio": non_portrait_ratio,
                    "required_min": SHORT_MIN_NON_PORTRAIT_RATIO,
                    "non_portrait_count": non_portrait_count,
                    "total_live_beats": total_live,
                }
            )

    # 2. Ban >= 3 consecutive medium/wide front-or-back portrait shots
    max_run = 0
    curr_run: list[str] = []
    offending_runs: list[list[str]] = []
    for rec in classified:
        if rec["shot_class"] in PORTRAIT_FRONT_BACK_CLASSES:
            curr_run.append(rec["beat_id"])
            if len(curr_run) > max_run:
                max_run = len(curr_run)
        else:
            if len(curr_run) > MAX_CONSECUTIVE_PORTRAIT_RUN:
                offending_runs.append(list(curr_run))
            curr_run = []
    if len(curr_run) > MAX_CONSECUTIVE_PORTRAIT_RUN:
        offending_runs.append(list(curr_run))

    if offending_runs:
        issues.append("CONSECUTIVE_PORTRAIT_STREAK_GTE_3")
        for run in offending_runs:
            violations.append(
                {
                    "code": "CONSECUTIVE_PORTRAIT_STREAK_GTE_3",
                    "streak_length": len(run),
                    "beat_ids": run,
                }
            )

    dedup = sorted(set(issues))
    return {
        "gate_id": V12_GATE_LIVE_COVERAGE,
        "passed": len(dedup) == 0,
        "format": "long_16x9" if is_long else "short_9x16",
        "total_live_beats": total_live,
        "non_portrait_ratio": non_portrait_ratio,
        "macro_prop_ratio": macro_prop_ratio,
        "max_consecutive_portrait_run": max_run,
        "offending_portrait_runs": offending_runs,
        "shot_class_counts": counts,
        "issues": dedup,
        "violations": violations,
    }


def audit_v12_hard_gates(
    spec: dict[str, Any] | None = None,
    *,
    spec_path: Path | str | None = None,
    format_profile: str | None = None,
    frame_paths: list[Path | str] | None = None,
    video_path: Path | str | None = None,
    map_video_paths: list[Path | str] | None = None,
    map_frame_paths: list[Path | str] | None = None,
) -> dict[str, Any]:
    """Run all 4 V12 Hard Auto-Fail Visual QC Gates (Gate A..Gate D) on spec + rendered media."""
    loaded_spec = spec
    if loaded_spec is None and spec_path is not None:
        _ep_dir, sf = _discover_spec_file(Path(spec_path))
        if sf is not None and sf.is_file():
            loaded_spec = json.loads(sf.read_text(encoding="utf-8"))

    gate_a = audit_zero_box_hud_gate(loaded_spec, frame_paths=frame_paths, video_path=video_path)
    gate_b = audit_slow_giant_map_v9_gate(
        loaded_spec,
        format_profile=format_profile,
        video_paths=map_video_paths,
        frame_paths=map_frame_paths,
    )
    gate_c = audit_anti_slideshow_first60s_gate(
        loaded_spec,
        video_path=video_path,
        format_profile=format_profile,
    )
    gate_d = audit_live_coverage_diversity_gate(
        loaded_spec,
        format_profile=format_profile,
    )

    gates = {
        V12_GATE_ZERO_BOX_HUD: gate_a,
        V12_GATE_SLOW_GIANT_MAP: gate_b,
        V12_GATE_ANTI_SLIDESHOW_60S: gate_c,
        V12_GATE_LIVE_COVERAGE: gate_d,
    }
    failed_gates = [gid for gid, rep in gates.items() if not rep["passed"]]
    blocking_issues: list[str] = []
    for gid, rep in gates.items():
        if not rep["passed"]:
            for iss in rep.get("issues", []):
                blocking_issues.append(f"{gid}:{iss}")

    return {
        "passed": len(failed_gates) == 0,
        "auto_fail_triggered": len(failed_gates) > 0,
        "failed_gates": failed_gates,
        "gates": gates,
        "blocking_issues": blocking_issues,
    }


__all__ = [
    "FIRST_15S_MAX_ASL_SEC",
    "FIRST_60S_FREEZE_DURATION_SEC",
    "FORBIDDEN_BOXED_HUD_KINDS",
    "HISTORICAL_ANACHRONISM_CATALOG",
    "LONG_MIN_MACRO_PROP_RATIO",
    "MAX_MAP_SIMULTANEOUS_LABELS",
    "MAX_MAP_WORDS_PER_LABEL",
    "MAX_THUMBNAIL_BYTES",
    "MIN_DYNAMIC_RANGE_P95_P5",
    "MIN_MAP_DURATION_SEC",
    "MIN_MAP_FONT_HEIGHT_RATIO",
    "NON_PORTRAIT_SHOT_CLASSES",
    "PORTRAIT_FRONT_BACK_CLASSES",
    "SHORT_MIN_NON_PORTRAIT_RATIO",
    "V12_GATE_ANTI_SLIDESHOW_60S",
    "V12_GATE_LIVE_COVERAGE",
    "V12_GATE_SLOW_GIANT_MAP",
    "V12_GATE_ZERO_BOX_HUD",
    "audit_and_sanitize_historical_prompt",
    "audit_anti_slideshow_first60s_gate",
    "audit_full_episode_visual_readiness",
    "audit_live_coverage_diversity_gate",
    "audit_rendered_2k_frame",
    "audit_slow_giant_map_v9_gate",
    "audit_sub_cut_crop_geometry",
    "audit_v12_hard_gates",
    "audit_zero_box_hud_gate",
    "classify_beat_shot_class",
    "normalize_faction",
    "resolve_dynasty_era",
]
