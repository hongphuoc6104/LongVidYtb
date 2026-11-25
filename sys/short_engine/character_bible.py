"""Historical Character Bible & Dynasty Wardrobe/Set Continuity Engine (`sys/short_engine/character_bible.py`).

Provides:
- `load_character_vault(channel_id="su_ke_lai") -> dict`
- `save_character_profile(profile: dict, channel_id="su_ke_lai") -> dict`
- `detect_episode_cast_and_sets(short_spec: dict) -> dict`
- `apply_cast_continuity_to_spec(short_spec: dict, character_ids: list[str] | None = None) -> dict`

Enforces 35mm Clear-Air Historical Cinema continuity (`allowed_text=None` on 100% of story beats,
benign fictionalized period-archetype facial DNA with zero celebrity likeness so Flow `PROMINENT_PEOPLE`
never triggers, and period-accurate dynasty armor/wardrobe locks with zero samurai/European/anachronism drift).
"""
from __future__ import annotations

import copy
import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
CHANNELS_DIR = SYS_DIR / "channels"
VIDEO_DIR = ROOT_DIR / "video"

VALID_FACTIONS: tuple[str, ...] = (
    "dai_viet",
    "northern_song",
    "mongol_yuan",
    "ming",
    "qing",
    "southern_han",
)

REQUIRED_CHARACTER_FIELDS: tuple[str, ...] = (
    "character_id",
    "name_vi",
    "aliases",
    "dynasty_era",
    "years_active",
    "faction",
    "role_archetype",
    "face_and_age_dna",
    "armor_and_wardrobe_lock",
    "signature_weapons_and_props",
    "lighting_and_color_palette",
    "voice_and_persona_note_vi",
    "anti_anachronism_bans",
    "sample_frame_relpath",
)

CLEAN_35MM_TAIL = (
    "Shot on 35mm Kodak Vision3 500T film, historical battle cinema docudrama, crisp optical clarity, "
    "deep-focus 35mm anamorphic depth, practical period-accurate wardrobe and set, plain unmarked banners "
    "with zero letters or glyphs, lips firmly closed in silent physical action, no text, no captions, "
    "no watermarks, no UI overlays."
)

_CELEBRITY_TRIGGER_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(?i:\b(?:resembling|look(?:s|ing)?\s+like|in\s+the\s+likeness\s+of|likeness\s+of|played\s+by|portrayed\s+by))\s+"
        r"[A-Z][a-zA-Z.'-]+(?:\s+[A-Z][a-zA-Z.'-]+){0,3}"
    ),
    re.compile(
        r"(?<!zero\s)(?<!no\s)\b(?:celebrity|movie\s+star|hollywood\s+actor|famous\s+actor)\b",
        re.IGNORECASE,
    ),
)

_BLANKET_FOG_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bdense\s+battlefield\s+mist\b", re.IGNORECASE), "crisp optical clarity"),
    (re.compile(r"\bdrifting\s+gunsmoke\s+fog\b", re.IGNORECASE), "clear directional cinema light"),
    (re.compile(r"\bthick\s+river\s+mist\b", re.IGNORECASE), "clear-air river depth"),
)

_HUMAN_SUBJECT_RE = re.compile(
    r"\b(?:general|commander|emperor|king|admiral|prince|marshal|scholar|strategist|warrior|soldier|"
    r"officer|marquis|vanguard|captain|guard|nobleman|hero|tướng|vua|hoàng\s+đế|chủ\s+tướng|chủ\s+soái|"
    r"thái\s+úy|quân\s+sư|anh\s+hùng|thống\s+soái|đô\s+giám)\b",
    re.IGNORECASE,
)

_ENEMY_CUE_RE = re.compile(
    r"\b(?:enemy|invader|invading|northern\s+song|mongol|yuan|ming|qing|southern\s+han|"
    r"giặc|quân\s+địch|tướng\s+giặc|xâm\s+lược|phương\s+bắc)\b",
    re.IGNORECASE,
)

_INANIMATE_ONLY_RE = re.compile(
    r"\b(?:submerged\s+rows\s+of|empty\s+wooden|silent\s+deserted|swept-bare|aerial\s+vista|"
    r"panorama\s+of|unrolled\s+golden\s+silk\s+imperial\s+edict|carved\s+stone\s+inkwell|"
    r"symmetrical\s+aged\s+bronze\s+temple\s+censer|underwater\s+cross-current)\b",
    re.IGNORECASE,
)


def _strip_accents(text: str) -> str:
    """Fold Vietnamese diacritics (including đ/Đ) into lowercase ASCII for resilient matching."""
    mapped = text.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", mapped)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def _slugify_id(raw: str) -> str:
    """Convert Vietnamese name or raw identifier into canonical snake_case `character_id`."""
    ascii_text = _strip_accents(str(raw or "").strip()).lower()
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_text).strip("_")
    return slug


def sanitize_benign_face_dna(text: str) -> str:
    """Remove any celebrity-likeness trigger phrases and CJK glyphs to prevent `PROMINENT_PEOPLE` blocks."""
    cleaned = str(text or "").strip()
    for pat in _CELEBRITY_TRIGGER_PATTERNS:
        cleaned = pat.sub("original historical archetype", cleaned)
    # Strip CJK ideographs so Flow never attempts to render Han characters onto armor or banners.
    cleaned = re.sub(r"[\u4e00-\u9fff]+", "", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" ,;-")
    return cleaned


def _clean_prompt_fog(text: str) -> str:
    """Replace blanket haze phrases with Clear-Air 35mm optical clarity per `su_ke_lai` visual law."""
    out = str(text or "")
    for pat, repl in _BLANKET_FOG_PATTERNS:
        out = pat.sub(repl, out)
    return re.sub(r"\s{2,}", " ", out).strip()


def get_vault_path(channel_id: str = "su_ke_lai", vault_path: Path | str | None = None) -> Path:
    """Return filesystem path to `<channel_id>/character_vault.json`."""
    if vault_path is not None:
        return Path(vault_path)
    clean_channel = re.sub(r"[^a-zA-Z0-9_-]", "", str(channel_id or "su_ke_lai")) or "su_ke_lai"
    return CHANNELS_DIR / clean_channel / "character_vault.json"


def _auto_find_sample_frame_relpath(aliases: list[str], channel_id: str = "su_ke_lai") -> str:
    """Scan existing `video/vn_<channel_id>_*/*spec.json` on disk for a rendered `frames/beat_XX.png` match."""
    if not VIDEO_DIR.is_dir() or not aliases:
        return ""
    norm_aliases = [a.strip().lower() for a in aliases if len(a.strip()) >= 4]
    if not norm_aliases:
        return ""

    spec_dirs = sorted(VIDEO_DIR.glob(f"vn_{channel_id}_*"), reverse=True)
    for ep_dir in spec_dirs:
        if not ep_dir.is_dir():
            continue
        spec_files = sorted(ep_dir.glob("*spec.json"))
        for sp in spec_files:
            try:
                data = json.loads(sp.read_text(encoding="utf-8"))
            except Exception:
                continue
            beats = data.get("beats") or data.get("scenes") or []
            for idx, beat in enumerate(beats):
                if not isinstance(beat, dict):
                    continue
                bi = int(beat.get("beat_index", idx))
                frame_file = ep_dir / "frames" / f"beat_{bi:02d}.png"
                if not frame_file.is_file():
                    continue
                blob = " ".join(
                    str(beat.get(k) or "")
                    for k in ("hero_subject", "narration", "display_text", "prompt", "visual_anchor")
                ).lower()
                if any(alias in blob for alias in norm_aliases):
                    return frame_file.relative_to(ROOT_DIR).as_posix()
    return ""


def _enrich_runtime_character(raw_profile: dict[str, Any]) -> dict[str, Any]:
    """Attach non-destructive convenience URLs/flags while keeping all canonical vault fields intact."""
    prof = copy.deepcopy(raw_profile)
    rel = str(prof.get("sample_frame_relpath") or "").strip().lstrip("/")
    prof["sample_frame_relpath"] = rel
    faction = str(prof.get("faction") or "dai_viet")
    prof.setdefault("faction_group", "dai_viet" if faction == "dai_viet" else "opposing")
    prof.setdefault("era_bucket", str(prof.get("era_group") or "ly_tran"))
    if rel:
        abs_frame = ROOT_DIR / rel
        prof["sample_frame_exists"] = abs_frame.is_file()
        prof.setdefault("portrait_url", f"/media/{rel}")
    else:
        prof["sample_frame_exists"] = False
        prof.setdefault("portrait_url", "")
    return prof


def _enrich_runtime_set(raw_set: dict[str, Any]) -> dict[str, Any]:
    """Normalize set/location archetype entry with `set_id`, `location_id`, and `preview_url`."""
    st = copy.deepcopy(raw_set)
    sid = str(st.get("set_id") or st.get("location_id") or "").strip()
    st["set_id"] = sid
    st["location_id"] = str(st.get("location_id") or sid)
    eras = list(st.get("dynasty_eras") or [])
    st.setdefault("dynasty_era", " · ".join(str(x) for x in eras) if eras else "Đại Việt")
    if "recommended_lenses_mm" not in st:
        lenses_mm: list[int] = []
        for lp in st.get("recommended_lens_pairings") or []:
            m_mm = re.search(r"(\d{2,3})\s*mm", str(lp))
            if m_mm:
                lenses_mm.append(int(m_mm.group(1)))
        st["recommended_lenses_mm"] = lenses_mm or [24, 35, 85]
    rel = str(st.get("sample_frame_relpath") or "").strip().lstrip("/")
    st["sample_frame_relpath"] = rel
    if rel:
        st["sample_frame_exists"] = (ROOT_DIR / rel).is_file()
        st.setdefault("preview_url", f"/media/{rel}")
        st.setdefault("sample_frame_url", f"/media/{rel}")
    else:
        st["sample_frame_exists"] = False
        st.setdefault("preview_url", "")
        st.setdefault("sample_frame_url", "")
    return st


def load_character_vault(
    channel_id: str = "su_ke_lai",
    *,
    vault_path: Path | str | None = None,
) -> dict[str, Any]:
    """Load and normalize the Historical Character, Dynasty Wardrobe, Prop & Set Vault."""
    path = get_vault_path(channel_id=channel_id, vault_path=vault_path)
    if not path.is_file():
        raise FileNotFoundError(f"Character vault not found at {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid character vault JSON root in {path}; expected object")

    vault = copy.deepcopy(raw)
    vault.setdefault("vault_version", "7.0.0")
    vault.setdefault("channel_id", channel_id)
    vault.setdefault("visual_grammar", "su_ke_lai_35mm_live_action_v3")
    vault["characters"] = [_enrich_runtime_character(c) for c in (raw.get("characters") or []) if isinstance(c, dict)]
    vault["sets"] = [_enrich_runtime_set(s) for s in (raw.get("sets") or []) if isinstance(s, dict)]
    vault["faction_style_locks"] = copy.deepcopy(raw.get("faction_style_locks") or {})
    return vault


def _normalize_profile_for_storage(
    incoming: dict[str, Any],
    existing: dict[str, Any] | None,
    *,
    channel_id: str = "su_ke_lai",
    faction_locks: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge, validate, and sanitize a character profile before atomic persistence."""
    if not isinstance(incoming, dict):
        raise TypeError("profile must be a dict")

    merged: dict[str, Any] = copy.deepcopy(existing) if existing else {}
    for k, v in incoming.items():
        if k in ("sample_frame_exists", "portrait_url"):
            continue
        if v is not None:
            merged[k] = copy.deepcopy(v)

    raw_cid = str(merged.get("character_id") or "").strip()
    name_vi = str(merged.get("name_vi") or "").strip()
    cid = _slugify_id(raw_cid) if raw_cid else _slugify_id(name_vi)
    if not cid:
        raise ValueError("Character profile requires a non-empty 'character_id' or 'name_vi'")
    if not name_vi:
        name_vi = cid.replace("_", " ").title()

    faction = str(merged.get("faction") or "dai_viet").strip().lower()
    if faction not in VALID_FACTIONS:
        raise ValueError(f"Unsupported faction {faction!r}; expected one of {VALID_FACTIONS}")

    f_lock = (faction_locks or {}).get(faction) or {}
    default_wardrobe = str(
        f_lock.get("armor_and_wardrobe_lock")
        or "Period-accurate lamellar war armor over woven silk battle tunic, leather bracers, and iron-ribbed helmet."
    )
    default_palette_raw = f_lock.get("palette_hex") or {}

    raw_aliases = merged.get("aliases")
    alias_items: list[str] = []
    if isinstance(raw_aliases, str):
        alias_items = [x.strip() for x in raw_aliases.split(",") if x.strip()]
    elif isinstance(raw_aliases, list):
        alias_items = [str(x).strip() for x in raw_aliases if str(x).strip()]

    ascii_name = _strip_accents(name_vi)
    dedup_aliases: list[str] = []
    seen_lower: set[str] = set()
    for cand in [name_vi, ascii_name, cid, *alias_items]:
        c_clean = str(cand or "").strip()
        if c_clean and c_clean.lower() not in seen_lower:
            seen_lower.add(c_clean.lower())
            dedup_aliases.append(c_clean)

    raw_props = merged.get("signature_weapons_and_props")
    if isinstance(raw_props, str):
        props = [x.strip() for x in raw_props.split(",") if x.strip()]
    elif isinstance(raw_props, list):
        props = [str(x).strip() for x in raw_props if str(x).strip()]
    else:
        props = []
    if not props:
        props = ["period-accurate forged steel command sword"]

    raw_bans = merged.get("anti_anachronism_bans")
    if isinstance(raw_bans, str):
        bans = [x.strip() for x in raw_bans.split(",") if x.strip()]
    elif isinstance(raw_bans, list):
        bans = [str(x).strip() for x in raw_bans if str(x).strip()]
    else:
        bans = []
    if not bans:
        bans = list(
            f_lock.get("anti_anachronism_bans")
            or [
                "no Japanese samurai kabuto or katana",
                "no European medieval plate armor",
                "no text, letters, or calligraphy on banners",
            ]
        )

    palette_in = merged.get("lighting_and_color_palette")
    if not isinstance(palette_in, dict):
        palette_in = {}
    palette = {
        "primary_hex": str(palette_in.get("primary_hex") or default_palette_raw.get("primary_hex") or "#8B1E24"),
        "accent_hex": str(palette_in.get("accent_hex") or default_palette_raw.get("accent_hex") or "#D4A037"),
        "lighting_key": str(palette_in.get("lighting_key") or "amber_brazier"),
    }

    face_dna = sanitize_benign_face_dna(
        str(
            merged.get("face_and_age_dna")
            or merged.get("face_dna")
            or (
                "A weathered 42-year-old historical East/Southeast Asian commander with angular cheekbones, "
                "resolute dark eyes, tied dark hair, and firmly closed lips, original historical archetype "
                "with zero celebrity likeness."
            )
        )
    )
    if "celebrity" not in face_dna.lower():
        face_dna = f"{face_dna.rstrip('. ')}, zero celebrity likeness."

    wardrobe_lock = sanitize_benign_face_dna(
        _clean_prompt_fog(str(merged.get("armor_and_wardrobe_lock") or merged.get("wardrobe_lock") or default_wardrobe))
    )

    sample_rel = str(merged.get("sample_frame_relpath") or "").strip().lstrip("/")
    if not sample_rel:
        sample_rel = _auto_find_sample_frame_relpath(dedup_aliases, channel_id=channel_id)

    side_default = "dai_viet_hero" if faction == "dai_viet" else "opposing_commander"
    stored: dict[str, Any] = {
        "character_id": cid,
        "name_vi": name_vi,
        "aliases": dedup_aliases,
        "dynasty_era": str(merged.get("dynasty_era") or "Đại Việt Cổ Trung Đại"),
        "era_group": str(merged.get("era_group") or "ly_tran"),
        "years_active": str(merged.get("years_active") or "1000–1800"),
        "faction": faction,
        "side": str(merged.get("side") or side_default),
        "role_archetype": str(merged.get("role_archetype") or merged.get("role") or "Danh Tướng Lịch Sử"),
        "face_and_age_dna": face_dna,
        "armor_and_wardrobe_lock": wardrobe_lock,
        "signature_weapons_and_props": props,
        "lighting_and_color_palette": palette,
        "voice_and_persona_note_vi": str(
            merged.get("voice_and_persona_note_vi") or "Điềm tĩnh, uy nghiêm, nhịp kể sắc bén chuẩn điện ảnh lịch sử."
        ),
        "anti_anachronism_bans": bans,
        "sample_frame_relpath": sample_rel,
    }
    # Preserve any additional custom metadata keys supplied by callers.
    for extra_k, extra_v in merged.items():
        if extra_k not in stored and extra_k not in ("sample_frame_exists", "portrait_url", "face_dna", "wardrobe_lock"):
            stored[extra_k] = extra_v
    return stored


def save_character_profile(
    profile: dict[str, Any],
    channel_id: str = "su_ke_lai",
    *,
    vault_path: Path | str | None = None,
) -> dict[str, Any]:
    """Create or update a character profile inside `character_vault.json` atomically and return it."""
    path = get_vault_path(channel_id=channel_id, vault_path=vault_path)
    if path.is_file():
        raw_vault = json.loads(path.read_text(encoding="utf-8"))
    else:
        raw_vault = {
            "vault_version": "7.0.0",
            "channel_id": channel_id,
            "visual_grammar": "su_ke_lai_35mm_live_action_v3",
            "faction_style_locks": {},
            "characters": [],
            "sets": [],
        }

    chars: list[dict[str, Any]] = [c for c in (raw_vault.get("characters") or []) if isinstance(c, dict)]
    probe_cid = _slugify_id(str(profile.get("character_id") or profile.get("name_vi") or ""))
    existing_idx = next(
        (i for i, c in enumerate(chars) if _slugify_id(str(c.get("character_id") or "")) == probe_cid),
        None,
    )
    existing_obj = chars[existing_idx] if existing_idx is not None else None
    normalized = _normalize_profile_for_storage(
        profile,
        existing_obj,
        channel_id=channel_id,
        faction_locks=raw_vault.get("faction_style_locks") or {},
    )

    if existing_idx is not None:
        chars[existing_idx] = normalized
    else:
        chars.append(normalized)

    raw_vault["characters"] = chars
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp.json")
    tmp_path.write_text(json.dumps(raw_vault, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp_path, path)
    return _enrich_runtime_character(normalized)


def _compile_character_matchers(
    characters: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, str], list[tuple[str, re.Pattern[str], re.Pattern[str] | None]]]:
    """Build exact ID/alias lookup tables and boundary-safe regexes sorted longest-alias-first."""
    by_id: dict[str, dict[str, Any]] = {}
    alias_to_id: dict[str, str] = {}
    patterns: list[tuple[str, re.Pattern[str], re.Pattern[str] | None]] = []

    raw_pairs: list[tuple[int, str, str]] = []
    for ch in characters:
        cid = str(ch.get("character_id") or "").strip()
        if not cid:
            continue
        by_id[cid] = ch
        alias_to_id[cid.lower()] = cid
        alias_to_id[_slugify_id(cid)] = cid

        candidates: list[str] = [str(ch.get("name_vi") or ""), cid]
        # Strip parenthetical alternate names like "Trần Hưng Đạo (Trần Quốc Tuấn)" into separate exact phrases too.
        name_vi = str(ch.get("name_vi") or "")
        if "(" in name_vi:
            base_part = name_vi.split("(", 1)[0].strip()
            if base_part:
                candidates.append(base_part)
            for inner in re.findall(r"\(([^)]+)\)", name_vi):
                if inner.strip():
                    candidates.append(inner.strip())
        candidates.extend(str(a) for a in (ch.get("aliases") or []))

        seen_alias: set[str] = set()
        for raw_a in candidates:
            a = raw_a.strip()
            if len(a) < 4:
                continue
            low = a.lower()
            alias_to_id[low] = cid
            alias_to_id[_slugify_id(a)] = cid
            if low not in seen_alias:
                seen_alias.add(low)
                raw_pairs.append((len(a), cid, a))

    # Match longer specific names ("Hưng Đạo Đại Vương") before shorter ones ("Hưng Đạo").
    raw_pairs.sort(key=lambda item: (-item[0], item[1], item[2]))
    for _, cid, alias in raw_pairs:
        acc_pat = re.compile(rf"(?<![\w]){re.escape(alias)}(?![\w])", re.IGNORECASE)
        folded = _strip_accents(alias)
        ascii_pat: re.Pattern[str] | None = None
        if len(folded) >= 5 and (" " in folded or "_" in folded):
            ascii_pat = re.compile(rf"(?<![a-zA-Z0-9_]){re.escape(folded)}(?![a-zA-Z0-9_])", re.IGNORECASE)
        patterns.append((cid, acc_pat, ascii_pat))

    return by_id, alias_to_id, patterns


def _match_characters_in_text(
    text: str,
    patterns: list[tuple[str, re.Pattern[str], re.Pattern[str] | None]],
) -> list[str]:
    """Return ordered unique `character_id`s matched in `text` by earliest occurrence."""
    if not text or not text.strip():
        return []
    folded_text = _strip_accents(text)
    hits: list[tuple[int, str]] = []
    seen: set[str] = set()
    for cid, acc_pat, ascii_pat in patterns:
        if cid in seen:
            continue
        m = acc_pat.search(text)
        pos = m.start() if m else None
        if pos is None and ascii_pat is not None:
            m2 = ascii_pat.search(folded_text)
            if m2:
                pos = m2.start()
        if pos is not None:
            seen.add(cid)
            hits.append((pos, cid))
    hits.sort(key=lambda item: item[0])
    return [cid for _, cid in hits]


def _score_set_for_text(set_entry: dict[str, Any], weighted_texts: list[tuple[str, int]]) -> int:
    """Score a Dynasty Set archetype against weighted location/prompt/narration strings."""
    sid = str(set_entry.get("set_id") or "").lower()
    keywords = [str(k).strip().lower() for k in (set_entry.get("keywords") or []) if str(k).strip()]
    score = 0
    for txt, weight in weighted_texts:
        if not txt:
            continue
        low = txt.lower()
        folded = _strip_accents(low)
        if sid and (sid in low or sid.replace("_", " ") in folded):
            score += 5 * weight
        for kw in keywords:
            kw_folded = _strip_accents(kw)
            if re.search(rf"(?<![\w]){re.escape(kw)}(?![\w])", low):
                score += 2 * weight
            elif len(kw_folded) >= 5 and re.search(rf"(?<![a-z0-9]){re.escape(kw_folded)}(?![a-z0-9])", folded):
                score += 1 * weight
    return score


def _build_cast_roster_entry(profile: dict[str, Any]) -> dict[str, Any]:
    """Format a vault character profile into an episode `cast_roster` object supporting V7 Studio keys."""
    palette = profile.get("lighting_and_color_palette") or {}
    p_hex = str(palette.get("primary_hex") or "#8B1E24")
    a_hex = str(palette.get("accent_hex") or "#D4A037")
    props = list(profile.get("signature_weapons_and_props") or [])
    rel = str(profile.get("sample_frame_relpath") or "")
    return {
        "character_id": profile["character_id"],
        "name_vi": profile["name_vi"],
        "dynasty_era": profile.get("dynasty_era", ""),
        "years_active": profile.get("years_active", ""),
        "faction": profile["faction"],
        "side": profile.get("side", "dai_viet_hero" if profile["faction"] == "dai_viet" else "opposing_commander"),
        "role_archetype": profile["role_archetype"],
        "role": profile["role_archetype"],
        "face_and_age_dna": profile["face_and_age_dna"],
        "face_dna": profile["face_and_age_dna"],
        "armor_and_wardrobe_lock": profile["armor_and_wardrobe_lock"],
        "wardrobe_lock": profile["armor_and_wardrobe_lock"],
        "signature_weapons_and_props": props,
        "signature_prop": props[0] if props else "",
        "lighting_and_color_palette": copy.deepcopy(palette),
        "palette_hex": [p_hex, a_hex],
        "voice_and_persona_note_vi": profile.get("voice_and_persona_note_vi", ""),
        "anti_anachronism_bans": list(profile.get("anti_anachronism_bans") or []),
        "sample_frame_relpath": rel,
        "portrait_url": f"/media/{rel}" if rel else "",
    }


def _build_location_bible_entry(set_entry: dict[str, Any]) -> dict[str, Any]:
    """Format a Dynasty Set archetype into an episode `locations_bible` object."""
    sid = str(set_entry.get("set_id") or set_entry.get("location_id") or "")
    rel = str(set_entry.get("sample_frame_relpath") or "")
    return {
        "set_id": sid,
        "location_id": sid,
        "name_vi": str(set_entry.get("name_vi") or sid),
        "dynasty_eras": list(set_entry.get("dynasty_eras") or []),
        "time_of_day": str(set_entry.get("time_of_day") or "dawn"),
        "lighting_key": str(set_entry.get("lighting_key") or "amber_brazier"),
        "terrain_and_architecture_dna": str(set_entry.get("terrain_and_architecture_dna") or ""),
        "atmosphere_lock": str(set_entry.get("atmosphere_lock") or ""),
        "recommended_lens_pairings": list(set_entry.get("recommended_lens_pairings") or []),
        "sample_frame_relpath": rel,
        "preview_url": f"/media/{rel}" if rel else "",
    }


def _resolve_requested_character_ids(
    raw_ids: list[str],
    by_id: dict[str, dict[str, Any]],
    alias_to_id: dict[str, str],
    patterns: list[tuple[str, re.Pattern[str], re.Pattern[str] | None]],
) -> list[str]:
    """Resolve user- or spec-supplied character identifiers/names to canonical vault `character_id`s."""
    resolved: list[str] = []
    seen: set[str] = set()
    for raw in raw_ids:
        token = str(raw or "").strip()
        if not token:
            continue
        cid = None
        if token in by_id:
            cid = token
        elif token.lower() in alias_to_id:
            cid = alias_to_id[token.lower()]
        elif _slugify_id(token) in alias_to_id:
            cid = alias_to_id[_slugify_id(token)]
        else:
            matched = _match_characters_in_text(token, patterns)
            if matched:
                cid = matched[0]
        if cid and cid not in seen:
            seen.add(cid)
            resolved.append(cid)
    return resolved


def detect_episode_cast_and_sets(
    short_spec: dict[str, Any],
    *,
    channel_id: str = "su_ke_lai",
    vault: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Auto-detect historical characters, factions, and Dynasty Sets per beat and episode-wide."""
    if not isinstance(short_spec, dict):
        raise TypeError("short_spec must be a dict")

    eff_channel = str(short_spec.get("channel_id") or channel_id or "su_ke_lai")
    vault_data = vault if vault is not None else load_character_vault(eff_channel)
    characters = vault_data.get("characters") or []
    sets = vault_data.get("sets") or []
    sets_by_id = {str(s.get("set_id") or s.get("location_id")): s for s in sets if isinstance(s, dict)}

    by_id, alias_to_id, char_patterns = _compile_character_matchers(characters)
    beats = list(short_spec.get("beats") or short_spec.get("scenes") or [])

    # Pre-collect top-level cast_roster hints if present.
    roster_raw_tokens: list[str] = []
    for item in short_spec.get("cast_roster") or []:
        if isinstance(item, dict):
            for k in ("character_id", "name_vi"):
                if item.get(k):
                    roster_raw_tokens.append(str(item[k]))
        elif isinstance(item, str):
            roster_raw_tokens.append(item)
    roster_hint_ids = _resolve_requested_character_ids(roster_raw_tokens, by_id, alias_to_id, char_patterns)

    # Determine episode-wide dominant set for fallback when an individual beat describes an interior/tent.
    episode_header_blob = " ".join(
        str(short_spec.get(k) or "")
        for k in ("job_id", "youtube_title", "topic", "parent_long_title", "thumbnail_text")
    )
    episode_weighted: list[tuple[str, int]] = [(episode_header_blob, 3)]
    for b in beats:
        if isinstance(b, dict):
            episode_weighted.append((str(b.get("location") or ""), 2))
            episode_weighted.append((str(b.get("narration") or b.get("display_text") or ""), 1))

    ep_set_scores = [(s["set_id"], _score_set_for_text(s, episode_weighted)) for s in sets]
    ep_set_scores.sort(key=lambda item: -item[1])
    dominant_set_id = ep_set_scores[0][0] if (ep_set_scores and ep_set_scores[0][1] > 0) else (
        sets[0]["set_id"] if sets else ""
    )

    episode_char_ids: list[str] = []
    seen_ep_chars: set[str] = set()
    episode_set_ids: list[str] = []
    seen_ep_sets: set[str] = set()
    episode_factions: list[str] = []
    seen_ep_factions: set[str] = set()

    def _record_char(cid: str) -> None:
        if cid in by_id and cid not in seen_ep_chars:
            seen_ep_chars.add(cid)
            episode_char_ids.append(cid)
            fac = str(by_id[cid].get("faction") or "")
            if fac and fac not in seen_ep_factions:
                seen_ep_factions.add(fac)
                episode_factions.append(fac)

    def _record_set(sid: str) -> None:
        if sid and sid in sets_by_id and sid not in seen_ep_sets:
            seen_ep_sets.add(sid)
            episode_set_ids.append(sid)

    # Record top-level title/header character mentions first if any, plus explicit cast_roster hints.
    for cid in roster_hint_ids:
        _record_char(cid)

    beat_reports: list[dict[str, Any]] = []
    for idx, beat in enumerate(beats):
        if not isinstance(beat, dict):
            continue
        bi = int(beat.get("beat_index", idx))
        bid = str(beat.get("beat_id") or beat.get("id") or f"B{bi:02d}")

        explicit_tokens = list(beat.get("character_ids") or [])
        if beat.get("cast_spec") and str(beat.get("cast_spec")).lower() != "none":
            explicit_tokens.append(str(beat.get("cast_spec")))
        explicit_cids = _resolve_requested_character_ids(explicit_tokens, by_id, alias_to_id, char_patterns)

        visual_blob = " ".join(str(beat.get(k) or "") for k in ("hero_subject", "prompt"))
        narration_blob = " ".join(
            str(beat.get(k) or "") for k in ("narration", "display_text", "text", "caption", "visual_anchor")
        )
        visual_cids = _match_characters_in_text(visual_blob, char_patterns)
        narr_cids = _match_characters_in_text(narration_blob, char_patterns)

        merged_beat_cids: list[str] = []
        for cid in [*explicit_cids, *visual_cids, *narr_cids]:
            if cid not in merged_beat_cids:
                merged_beat_cids.append(cid)
                _record_char(cid)

        # Determine which characters are visually depicted in the frame (vs purely referenced in VO).
        person_count_raw = beat.get("person_count")
        explicit_zero_people = person_count_raw is not None and int(person_count_raw) == 0
        depicted_cids: list[str] = []
        if not explicit_zero_people:
            for cid in [*explicit_cids, *visual_cids]:
                if cid not in depicted_cids:
                    depicted_cids.append(cid)
            if not depicted_cids and narr_cids and not _INANIMATE_ONLY_RE.search(visual_blob):
                depicted_cids.append(narr_cids[0])

        # Detect Dynasty Set for this beat.
        explicit_set = str(beat.get("set_id") or beat.get("location_id") or "").strip()
        if explicit_set in sets_by_id:
            beat_set_id = explicit_set
        else:
            weighted = [
                (str(beat.get("location") or ""), 3),
                (str(beat.get("hero_subject") or ""), 2),
                (str(beat.get("prompt") or ""), 1),
                (narration_blob, 2),
            ]
            scored = [(s["set_id"], _score_set_for_text(s, weighted)) for s in sets]
            scored.sort(key=lambda item: -item[1])
            beat_set_id = scored[0][0] if (scored and scored[0][1] > 0) else dominant_set_id

        _record_set(beat_set_id)
        beat_factions: list[str] = []
        for cid in merged_beat_cids:
            fac = str(by_id[cid].get("faction") or "")
            if fac and fac not in beat_factions:
                beat_factions.append(fac)

        beat_reports.append(
            {
                "beat_index": bi,
                "beat_id": bid,
                "character_ids": merged_beat_cids,
                "visual_character_ids": depicted_cids,
                "set_id": beat_set_id,
                "location_id": beat_set_id,
                "factions": beat_factions,
            }
        )

    # Also match characters from episode header if none of the beats matched yet.
    for cid in _match_characters_in_text(episode_header_blob, char_patterns):
        _record_char(cid)
    if not episode_set_ids and dominant_set_id:
        _record_set(dominant_set_id)

    return {
        "channel_id": eff_channel,
        "job_id": str(short_spec.get("job_id") or ""),
        "character_ids": episode_char_ids,
        "cast_roster": [_build_cast_roster_entry(by_id[cid]) for cid in episode_char_ids if cid in by_id],
        "set_ids": episode_set_ids,
        "sets": [copy.deepcopy(sets_by_id[sid]) for sid in episode_set_ids if sid in sets_by_id],
        "locations_bible": [_build_location_bible_entry(sets_by_id[sid]) for sid in episode_set_ids if sid in sets_by_id],
        "factions": episode_factions,
        "beats": beat_reports,
    }


def _enrich_hero_subject_with_profile(hero_subject: str, profile: dict[str, Any]) -> str:
    """Idempotently weave wardrobe & benign age/facial cues into `hero_subject`."""
    base = sanitize_benign_face_dna(_clean_prompt_fog(hero_subject))
    wardrobe = str(profile.get("armor_and_wardrobe_lock") or "").strip().rstrip(".")
    face_dna = str(profile.get("face_and_age_dna") or "").strip().rstrip(".")

    # Check idempotency via stable substring signature from `wardrobe` and `face_dna`.
    wardrobe_sig = wardrobe[:48].lower()
    face_sig = face_dna[:42].lower()
    if wardrobe_sig and wardrobe_sig in base.lower():
        return base

    if not base:
        return f"{profile['name_vi']} ({face_dna}), clad in {wardrobe}"

    if face_sig and face_sig in base.lower():
        return f"{base.rstrip('. ')}, clad in {wardrobe}"

    return f"{base.rstrip('. ')} — {face_dna}; clad in {wardrobe}"


def _enrich_prompt_with_continuity(
    prompt: str,
    hero_subject: str,
    location: str,
    profile: dict[str, Any] | None,
    set_entry: dict[str, Any] | None,
) -> str:
    """Build or idempotently enrich a 5-block 35mm cinema prompt with locked character & set continuity."""
    cleaned_prompt = sanitize_benign_face_dna(_clean_prompt_fog(prompt))
    wardrobe = str(profile.get("armor_and_wardrobe_lock") or "").strip().rstrip(".") if profile else ""
    face_dna = str(profile.get("face_and_age_dna") or "").strip().rstrip(".") if profile else ""
    props = list(profile.get("signature_weapons_and_props") or []) if profile else []
    prop_clause = f", carrying {props[0]}" if props else ""
    set_dna = str(set_entry.get("terrain_and_architecture_dna") or "").strip().rstrip(".") if set_entry else ""
    atmos_lock = str(set_entry.get("atmosphere_lock") or "").strip().rstrip(".") if set_entry else ""

    if not cleaned_prompt:
        subj_block = hero_subject or (profile["name_vi"] if profile else "historical battlefield scene")
        loc_block = location or set_dna or "period-accurate Đại Việt historical terrain"
        parts = [f"{subj_block.rstrip('. ')}, inside {loc_block.rstrip('. ')}."]
        if profile and wardrobe and wardrobe[:48].lower() not in subj_block.lower():
            parts.append(f"Character wardrobe continuity: {face_dna}; {wardrobe}{prop_clause}.")
        if atmos_lock:
            parts.append(f"{atmos_lock}.")
        parts.append(CLEAN_35MM_TAIL)
        return " ".join(parts)

    # Existing prompt: inject character wardrobe + benign face DNA idempotently if not already present.
    if profile and wardrobe and wardrobe[:48].lower() not in cleaned_prompt.lower():
        continuity_clause = f"Depicted with consistent period-accurate features ({face_dna}) and wearing {wardrobe}{prop_clause}."
        cleaned_prompt = f"{cleaned_prompt.rstrip('. ')}. {continuity_clause}"

    # Ensure Zero-Text & closed-lips clean-frame lock is always present on raw Flow prompts.
    low = cleaned_prompt.lower()
    tail_additions: list[str] = []
    if "plain unmarked" not in low and "zero letters" not in low:
        tail_additions.append("plain unmarked banners with zero letters or glyphs")
    if "closed" not in low and "no talking" not in low:
        tail_additions.append("lips firmly closed in silent physical action")
    if "no text" not in low and "zero text" not in low:
        tail_additions.append("no text, no captions, no watermarks, no UI overlays")
    if tail_additions:
        cleaned_prompt = f"{cleaned_prompt.rstrip('. ')}, {', '.join(tail_additions)}."
    return cleaned_prompt


def apply_cast_continuity_to_spec(
    short_spec: dict[str, Any],
    character_ids: list[str] | None = None,
    *,
    channel_id: str = "su_ke_lai",
    vault: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Populate `cast_roster`, `locations_bible`, per-beat `character_ids` & `set_id`, and lock 35mm wardrobe/face DNA."""
    if not isinstance(short_spec, dict):
        raise TypeError("short_spec must be a dict")

    spec = copy.deepcopy(short_spec)
    eff_channel = str(spec.get("channel_id") or channel_id or "su_ke_lai")
    vault_data = vault if vault is not None else load_character_vault(eff_channel)
    characters = vault_data.get("characters") or []
    sets = vault_data.get("sets") or []
    sets_by_id = {str(s.get("set_id") or s.get("location_id")): s for s in sets if isinstance(s, dict)}
    by_id, alias_to_id, char_patterns = _compile_character_matchers(characters)

    requested_cids: list[str] | None = None
    if character_ids is not None:
        requested_cids = _resolve_requested_character_ids(character_ids, by_id, alias_to_id, char_patterns)

    detected = detect_episode_cast_and_sets(spec, channel_id=eff_channel, vault=vault_data)
    detected_beats_by_idx = {int(b["beat_index"]): b for b in detected["beats"]}

    # Build ordered episode character roster: requested IDs first (if supplied), then detected IDs.
    final_roster_ids: list[str] = []
    for cid in [*(requested_cids or []), *detected["character_ids"]]:
        if cid in by_id and cid not in final_roster_ids:
            final_roster_ids.append(cid)

    requested_heroes = [cid for cid in (requested_cids or []) if by_id[cid].get("faction") == "dai_viet"]
    requested_opponents = [cid for cid in (requested_cids or []) if by_id[cid].get("faction") != "dai_viet"]

    beats_key = "beats" if "beats" in spec or "scenes" not in spec else "scenes"
    beats = list(spec.get(beats_key) or [])
    anchor_beat_by_char: dict[str, str] = {}
    used_set_ids: list[str] = list(detected["set_ids"])

    for idx, beat in enumerate(beats):
        if not isinstance(beat, dict):
            continue
        bi = int(beat.get("beat_index", idx))
        bid = str(beat.get("beat_id") or beat.get("id") or f"B{bi:02d}")
        det_beat = detected_beats_by_idx.get(bi) or {
            "character_ids": [],
            "visual_character_ids": [],
            "set_id": detected["set_ids"][0] if detected["set_ids"] else "",
        }

        beat_cids = list(det_beat["character_ids"])
        visual_cids = list(det_beat["visual_character_ids"])

        # If caller explicitly passed `character_ids` (e.g., 1-click Apply Cast on a generic/scaffolded spec),
        # prioritize requested IDs and bind generic human/commander beats to the requested hero/opponent.
        if requested_cids:
            prioritized = [c for c in beat_cids if c in requested_cids] + [
                c for c in beat_cids if c not in requested_cids
            ]
            beat_cids = prioritized
            visual_cids = [c for c in visual_cids if c in requested_cids] + [
                c for c in visual_cids if c not in requested_cids
            ]
            person_count_raw = beat.get("person_count")
            explicit_zero = person_count_raw is not None and int(person_count_raw) == 0
            combined_blob = " ".join(
                str(beat.get(k) or "") for k in ("hero_subject", "prompt", "narration", "display_text")
            )
            has_human_cue = (
                (person_count_raw is not None and int(person_count_raw) >= 1)
                or bool(_HUMAN_SUBJECT_RE.search(combined_blob))
                or (bi == 0 and not explicit_zero and not _INANIMATE_ONLY_RE.search(combined_blob))
            )
            if not beat_cids and has_human_cue and not explicit_zero:
                if _ENEMY_CUE_RE.search(combined_blob) and requested_opponents:
                    chosen_cid = requested_opponents[0]
                elif requested_heroes:
                    chosen_cid = requested_heroes[0]
                else:
                    chosen_cid = requested_cids[0]
                beat_cids = [chosen_cid]
                visual_cids = [chosen_cid]

        for cid in beat_cids:
            if cid in by_id and cid not in final_roster_ids:
                final_roster_ids.append(cid)

        set_id = str(beat.get("set_id") or det_beat.get("set_id") or "")
        set_entry = sets_by_id.get(set_id)
        if set_id and set_id not in used_set_ids and set_id in sets_by_id:
            used_set_ids.append(set_id)

        beat["allowed_text"] = None
        beat["character_ids"] = beat_cids
        if set_id:
            beat["set_id"] = set_id
            beat.setdefault("location_id", set_id)
        if set_entry and not beat.get("lighting_key"):
            beat["lighting_key"] = str(set_entry.get("lighting_key") or "amber_brazier")

        primary_visual_cid = visual_cids[0] if visual_cids else None
        primary_profile = by_id.get(primary_visual_cid) if primary_visual_cid else None

        if primary_visual_cid and primary_profile:
            if not beat.get("lighting_key"):
                pal = primary_profile.get("lighting_and_color_palette") or {}
                beat["lighting_key"] = str(pal.get("lighting_key") or "amber_brazier")

            # Track 1-hop root anchor beat for Flow BELUGA reference continuity (`PLAYBOOK` star-flatten rule).
            if primary_visual_cid not in anchor_beat_by_char:
                anchor_beat_by_char[primary_visual_cid] = bid
                if not beat.get("cast_spec") or str(beat.get("cast_spec")).lower() == "none":
                    beat["cast_spec"] = f"NEW: {primary_visual_cid} ({primary_profile['name_vi']})"
            else:
                anchor_bid = anchor_beat_by_char[primary_visual_cid]
                if not beat.get("cast_spec") or str(beat.get("cast_spec")).lower() == "none":
                    beat["cast_spec"] = f"SAME as {anchor_bid}: {primary_visual_cid}"
                if not beat.get("reference_scene_ids") and anchor_bid != bid:
                    beat["reference_scene_ids"] = [anchor_bid]

            orig_hero = str(beat.get("hero_subject") or "")
            beat["hero_subject"] = _enrich_hero_subject_with_profile(orig_hero, primary_profile)
            beat["prompt"] = _enrich_prompt_with_continuity(
                str(beat.get("prompt") or ""),
                beat["hero_subject"],
                str(beat.get("location") or ""),
                primary_profile,
                set_entry,
            )
        else:
            # Non-character landscape/prop beat: still sanitize fog/text and preserve Clean-Frame Law.
            if beat.get("hero_subject"):
                beat["hero_subject"] = sanitize_benign_face_dna(_clean_prompt_fog(str(beat["hero_subject"])))
            if beat.get("prompt"):
                beat["prompt"] = _enrich_prompt_with_continuity(
                    str(beat["prompt"]),
                    str(beat.get("hero_subject") or ""),
                    str(beat.get("location") or ""),
                    None,
                    set_entry,
                )

    spec[beats_key] = beats
    spec["cast_roster"] = [_build_cast_roster_entry(by_id[cid]) for cid in final_roster_ids if cid in by_id]
    if not spec.get("locations_bible") and used_set_ids:
        spec["locations_bible"] = [
            _build_location_bible_entry(sets_by_id[sid]) for sid in used_set_ids if sid in sets_by_id
        ]
    return spec


__all__ = [
    "CLEAN_35MM_TAIL",
    "REQUIRED_CHARACTER_FIELDS",
    "VALID_FACTIONS",
    "apply_cast_continuity_to_spec",
    "detect_episode_cast_and_sets",
    "get_vault_path",
    "load_character_vault",
    "sanitize_benign_face_dna",
    "save_character_profile",
]
