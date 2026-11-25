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
            "rendered_assets_present": bool(frame_audits or thumbnail_audits),
        },
        "thumbnail_prompt_audit": thumbnail_prompt_audit,
        "prompt_audits": prompt_audits,
        "crop_audits": crop_audits,
        "frame_audits": frame_audits,
        "thumbnail_audits": thumbnail_audits,
        "blocking_issues": blocking_issues,
    }


__all__ = [
    "HISTORICAL_ANACHRONISM_CATALOG",
    "MAX_THUMBNAIL_BYTES",
    "MIN_DYNAMIC_RANGE_P95_P5",
    "audit_and_sanitize_historical_prompt",
    "audit_full_episode_visual_readiness",
    "audit_rendered_2k_frame",
    "audit_sub_cut_crop_geometry",
    "normalize_faction",
    "resolve_dynasty_era",
]
