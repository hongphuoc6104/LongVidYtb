"""Vietnamese spoken-numeral normalizer & compound-safe 1-3 word subtitle grouper."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# V12 Zero-Box Subtitle Color & Card Contract
V12_SUBTITLE_WHITE_HEX = "#F8FAFC"
V12_SUBTITLE_GOLD_HEX = "#FFE066"
V12_SUBTITLE_WHITE_RGBA = (248, 250, 252, 255)
V12_SUBTITLE_GOLD_RGBA = (255, 224, 102, 255)
# ASS uses &HAABBGGRR / &HBBGGRR& (BGR byte order)
V12_ASS_WHITE = "&H00FCFAF8"
V12_ASS_WHITE_TAG = "&HFCFAF8&"
V12_ASS_GOLD = "&H0066E0FF"
V12_ASS_GOLD_TAG = "&H66E0FF&"
MAX_V12_SUBTITLE_WORDS = 3

# Common 2-syllable Vietnamese compound words & historical military/chronicle bigrams
# that should stay paired when possible.
VN_COMPOUND_BIGRAMS: frozenset[str] = frozenset({
    "lịch sử", "chiến thắng", "chiến trường", "chiến dịch", "chiến thuyền", "chiến bào",
    "quân đội", "đội quân", "tướng quân", "danh tướng", "binh lính", "binh sĩ",
    "đại quân", "tiền quân", "hậu quân", "thủy quân", "kỵ binh", "bộ binh",
    "tượng binh", "hỏa hổ", "hỏa công", "đại bác", "cung nỏ", "nỏ thần",
    "thành trì", "pháo đài", "bến cảng", "cửa biển", "thủy triều", "con nước",
    "hoàng đế", "triều đình", "vua tôi", "công thần", "trung thần", "gian thần",
    "gia nô", "thân thuộc", "dân chúng", "bách tính", "nhân dân", "đất nước",
    "giang sơn", "sơn hà", "biên cương", "biên giới", "lãnh thổ", "kinh thành",
    "thời đại", "thế kỷ", "một nghìn", "hai mươi", "bốn mươi", "mười sáu",
    "mười vạn", "ba mươi", "trăm vạn", "hàng vạn", "hàng nghìn", "nghìn năm",
    "thiếu niên", "tuổi trẻ", "khí phách", "hào khí", "anh hùng", "bất khuất",
    "phẫn uất", "uất ức", "quyết định", "kế hoạch", "mưu lược", "mưu kế",
    "tâm lý", "phủ đầu", "tấn công", "phản công", "phục kích", "bao vây",
    "công thành", "thủ thành", "giữ thành", "vượt biên", "hành quân", "truy kích",
    "tàn khốc", "sinh tử", "sống chết", "cái giá", "sự thật", "bí mật",
    "nghịch lý", "sai lầm", "thất bại", "chiến lược", "chiến thuật", "hậu cần",
    "lương thảo", "vũ khí", "giáp sắt", "khiên mây", "thang mây", "tên lửa",
    "nhựa thông", "thổ sơn", "bao đất", "biển lửa", "ngọn đuốc", "ánh đuốc",
    "mưa đêm", "rạng đông", "bình minh", "đại Việt", "đại việt", "nhà tống",
    "nhà trần", "nhà lý", "nhà lê", "nhà hồ", "tây sơn", "lam sơn",
    "xâm lược", "chống trả", "bảo vệ", "độc lập", "hòa bình", "chiến tranh",
    "khắc sâu", "bất ngờ", "đối đầu", "chỉ huy", "tư lệnh", "thái úy",
    "đô giám", "tể tướng", "tân pháp", "lộ bố", "chính sử", "sử liệu",
    "không ngờ", "duy nhất", "trực tiếp", "ngay lập", "lập tức", "cuối cùng",
    "thực sự", "hoàn toàn", "chắc chắn", "tuyệt đối", "nguy hiểm", "khốc liệt",
    "trận đánh", "cuộc chiến", "bài học", "lựa chọn", "quan điểm", "tranh luận",
    "phản đối", "đồng ý", "thế mạng", "cứu nước", "giữ nước", "đánh giặc",
    "ngoài thuyền", "thuyền rồng", "quả cam", "gia sản", "thái ấp", "tư binh",
    "đại kỳ", "chữ vàng", "sáu chữ", "cường địch", "hoàng ân", "vương hầu",
    "thế giới", "nhân loại", "hiện đại", "quá khứ", "tương lai",
    "câu chuyện", "số phận", "cục diện", "bước ngoặt", "đỉnh cao", "kỷ nguyên",
})

VN_NUMBER_WORDS: frozenset[str] = frozenset({
    "không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười",
    "mươi", "trăm", "nghìn", "ngàn", "vạn", "triệu", "tỷ", "chục", "đôi", "vài",
    "nhiều", "hàng", "hơn", "gần", "khoảng", "nửa", "từng",
})

VN_MEASURE_UNITS: frozenset[str] = frozenset({
    "vạn", "nghìn", "ngàn", "trăm", "triệu", "tỷ", "quân", "lính", "chiến", "thuyền",
    "ngày", "đêm", "năm", "tháng", "tuổi", "giờ", "khắc", "phút", "giây",
    "km", "mét", "cây", "tấn", "khẩu", "người", "vị", "vua", "tướng",
    "châu", "đồn", "thành", "mũi", "bao", "chữ", "tầng", "lần", "lượt", "bước",
    "gia", "phát", "trận", "đòn", "họ", "cánh", "đạo", "cửa",
})

_CONJUNCTION_BREAKERS: frozenset[str] = frozenset({
    "nhưng", "nhưng mà", "tuy nhiên", "vì vậy", "nên", "nếu", "khi", "lúc",
    "mà", "hoặc", "hay", "còn", "rồi", "để", "bằng", "tại", "trước", "sau",
})

# Spoken-VN-to-Digits lookup tables (carefully disambiguated so Vietnamese words/diacritics stay intact)
_D0_9: dict[str, int] = {
    "không": 0, "một": 1, "hai": 2, "ba": 3, "bốn": 4,
    "năm": 5, "sáu": 6, "bảy": 7, "bẩy": 7, "tám": 8, "chín": 9,
}
_D1_9_START: dict[str, int] = {k: v for k, v in _D0_9.items() if v >= 1}
_D2_9_START: dict[str, int] = {k: v for k, v in _D0_9.items() if v >= 2}
# Note: "năm" is NEVER a unit digit after "mười"/"mươi" in Vietnamese ("15"="mười lăm", "20 năm"="twenty years")
_UNIT_AFTER_MUOI_10: dict[str, int] = {
    "một": 1, "hai": 2, "ba": 3, "bốn": 4, "lăm": 5, "nhăm": 5,
    "sáu": 6, "bảy": 7, "bẩy": 7, "tám": 8, "chín": 9,
}
_UNIT_AFTER_MUOI_20: dict[str, int] = {
    "một": 1, "mốt": 1, "hai": 2, "ba": 3, "bốn": 4, "tư": 4,
    "lăm": 5, "nhăm": 5, "sáu": 6, "bảy": 7, "bẩy": 7, "tám": 8, "chín": 9,
}
_UNIT_AFTER_LINH: dict[str, int] = {
    "một": 1, "hai": 2, "ba": 3, "bốn": 4, "tư": 4, "năm": 5, "lăm": 5,
    "sáu": 6, "bảy": 7, "bẩy": 7, "tám": 8, "chín": 9,
}

# Strict quantitative followers for single-word numbers so idioms ("chín chắn", "năm tháng", "một mình", "không ngờ") stay untouched
_SINGLE_DIGIT_UNITS_FOR_NAM: frozenset[str] = frozenset({
    "giờ", "phút", "giây", "khắc", "ngày", "đêm", "năm", "tuổi",
    "vạn", "triệu", "tỷ", "quân", "lính", "thuyền", "họ", "người",
    "mũi", "lần", "lượt", "bước", "tầng", "khẩu", "phát", "đòn",
    "trận", "cánh", "đạo", "km", "mét", "tấn", "chữ",
})
_SINGLE_DIGIT_UNITS_GENERAL: frozenset[str] = _SINGLE_DIGIT_UNITS_FOR_NAM | frozenset({
    "tháng", "chiến", "vua", "tướng", "đồn", "thành", "cửa", "cây",
})
_NON_NUMERIC_PREFIXES: frozenset[str] = frozenset({
    "thứ", "ngã", "cấp", "bậc", "đôi", "vài", "không", "một", "từng",
})
_IDIOM_FOLLOWERS_BLOCKLIST: frozenset[str] = frozenset({
    "lòng", "phương", "hướng", "chắn", "muồi", "hoa", "phải", "chân", "miền", "bể",
})

_PUNCT_STRIP_RE = re.compile(r"^([.,;:!?\"'“”‘’()\[\]…—–-]*)(.*?)([.,;:!?\"'“”‘’()\[\]…—–-]*)$")
_CLAUSE_STOP_SUFFIX_RE = re.compile(r"[,.;:!?…—–]")


def _split_affixes(raw_tok: str) -> tuple[str, str, str, bool]:
    m = _PUNCT_STRIP_RE.match(raw_tok)
    if not m:
        return "", raw_tok, "", False
    pre, core, suf = m.group(1), m.group(2), m.group(3)
    stops = bool(_CLAUSE_STOP_SUFFIX_RE.search(suf))
    return pre, core, suf, stops


def _parse_sub_thousand(
    low_tokens: list[str],
    stops: list[bool],
    pos: int,
    *,
    allow_zero_hundred: bool = False,
) -> tuple[int, int] | None:
    """Parse a spoken Vietnamese cardinal value in `0..999` starting at `pos`."""
    n = len(low_tokens)
    if pos >= n or not low_tokens[pos]:
        return None

    p = pos
    val = 0
    has_hundreds = False

    # Optional `[0..9] trăm`
    if (
        p + 1 < n
        and not stops[p]
        and low_tokens[p + 1] == "trăm"
        and (low_tokens[p] in _D0_9 if allow_zero_hundred else low_tokens[p] in _D1_9_START)
    ):
        val = _D0_9[low_tokens[p]] * 100
        p += 2
        has_hundreds = True
        if stops[p - 1] or p >= n:
            return val, p

        # Optional `linh/lẻ [1..9]` after `trăm`
        if p + 1 < n and not stops[p] and low_tokens[p] in ("linh", "lẻ") and low_tokens[p + 1] in _UNIT_AFTER_LINH:
            return val + _UNIT_AFTER_LINH[low_tokens[p + 1]], p + 2

    if p >= n:
        return (val, p) if has_hundreds else None

    # Tens: `mười [1..9]?`
    if low_tokens[p] == "mười":
        val += 10
        p += 1
        if not stops[p - 1] and p < n and low_tokens[p] in _UNIT_AFTER_MUOI_10:
            # Do not consume if next token starts `trăm`
            if not (p + 1 < n and not stops[p] and low_tokens[p + 1] == "trăm"):
                val += _UNIT_AFTER_MUOI_10[low_tokens[p]]
                p += 1
        return val, p

    # Tens: `[2..9] mươi [1..9]?`
    if p + 1 < n and not stops[p] and low_tokens[p] in _D2_9_START and low_tokens[p + 1] == "mươi":
        val += _D2_9_START[low_tokens[p]] * 10
        p += 2
        if not stops[p - 1] and p < n and low_tokens[p] in _UNIT_AFTER_MUOI_20:
            if not (p + 1 < n and not stops[p] and low_tokens[p + 1] == "trăm"):
                val += _UNIT_AFTER_MUOI_20[low_tokens[p]]
                p += 1
        return val, p

    # Tens: `[1..9] chục` (standalone tens)
    if not has_hundreds and p + 1 < n and not stops[p] and low_tokens[p] in _D1_9_START and low_tokens[p + 1] == "chục":
        return _D1_9_START[low_tokens[p]] * 10, p + 2

    # Colloquial tens after `trăm`, e.g. `một nghìn bốn trăm hai bảy` -> `1427`
    if has_hundreds and p + 1 < n and not stops[p] and low_tokens[p] in _D2_9_START and low_tokens[p + 1] in _UNIT_AFTER_MUOI_20:
        return val + _D2_9_START[low_tokens[p]] * 10 + _UNIT_AFTER_MUOI_20[low_tokens[p + 1]], p + 2

    if has_hundreds:
        return val, p

    # Single leading digit `1..9`
    if low_tokens[p] in _D1_9_START:
        return _D1_9_START[low_tokens[p]], p + 1

    return None


def _match_spoken_vn_number_span(
    low_tokens: list[str],
    stops: list[bool],
    idx: int,
) -> tuple[int, int] | None:
    """Match a spoken Vietnamese number span `[idx, end_idx)` returning `(numeric_value, end_idx)`."""
    n = len(low_tokens)
    if idx >= n or not low_tokens[idx]:
        return None

    # Disambiguate "năm" ("year" vs "5") BEFORE greedy parsing when "năm" precedes another number:
    # e.g. "năm một nghìn bốn trăm hai mươi bảy" -> "năm" is "year", NOT 5!
    if low_tokens[idx] == "năm":
        nxt = low_tokens[idx + 1] if (idx + 1 < n and not stops[idx]) else ""
        if nxt not in ("mươi", "trăm", "nghìn", "ngàn", "chục") and nxt not in _SINGLE_DIGIT_UNITS_FOR_NAM:
            return None

    head = _parse_sub_thousand(low_tokens, stops, idx, allow_zero_hundred=False)
    if head is None:
        return None
    g1, p1 = head

    # Check `[1..999] nghìn/ngàn ...`
    if p1 < n and not stops[p1 - 1] and low_tokens[p1] in ("nghìn", "ngàn"):
        total = g1 * 1000
        p = p1 + 1
        if not stops[p - 1] and p < n:
            # e.g. `một nghìn linh bảy mươi lăm` or `hai nghìn lẻ năm`
            if p + 1 < n and not stops[p] and low_tokens[p] in ("linh", "lẻ"):
                after_linh = _parse_sub_thousand(low_tokens, stops, p + 1, allow_zero_hundred=False)
                if after_linh is not None and after_linh[0] < 100:
                    return total + after_linh[0], after_linh[1]
                if low_tokens[p + 1] in _UNIT_AFTER_LINH:
                    return total + _UNIT_AFTER_LINH[low_tokens[p + 1]], p + 2
            # e.g. `một nghìn bốn trăm hai mươi bảy` or `một nghìn không trăm linh năm`
            elif p + 1 < n and not stops[p] and low_tokens[p] in _D0_9 and low_tokens[p + 1] == "trăm":
                rem = _parse_sub_thousand(low_tokens, stops, p, allow_zero_hundred=True)
                if rem is not None:
                    return total + rem[0], rem[1]
        return total, p

    span_len = p1 - idx
    if span_len >= 2:
        return g1, p1

    # Single-word number (`span_len == 1`): enforce contextual guards so normal words stay intact
    prev_low = low_tokens[idx - 1] if (idx > 0 and not stops[idx - 1]) else ""
    next_low = low_tokens[p1] if (p1 < n and not stops[idx]) else ""

    if prev_low in _NON_NUMERIC_PREFIXES:
        return None
    if next_low in _IDIOM_FOLLOWERS_BLOCKLIST:
        return None

    # Calendar patterns: "tháng bảy" -> "tháng 7", "mùng năm" -> "mùng 5"
    if prev_low in ("tháng", "mùng", "mồng"):
        if prev_low == "tháng" and (1 <= g1 <= 12) and not (idx >= 2 and low_tokens[idx - 2] == "năm"):
            return g1, p1
        if prev_low in ("mùng", "mồng") and (1 <= g1 <= 10):
            return g1, p1

    if g1 == 1:
        return (g1, p1) if next_low in ("vạn", "triệu", "tỷ") else None
    if g1 == 5 and low_tokens[idx] == "năm":
        return (g1, p1) if next_low in _SINGLE_DIGIT_UNITS_FOR_NAM else None
    if 2 <= g1 <= 10:
        return (g1, p1) if next_low in _SINGLE_DIGIT_UNITS_GENERAL else None

    return None


def normalize_spoken_vn_numbers(text: str) -> str:
    """Convert spoken Vietnamese number phrases into compact Arabic digits for clean display subtitles.

    Examples:
        - `"một nghìn bốn trăm hai mươi bảy"` -> `"1427"`
        - `"năm một nghìn bốn trăm hai mươi bảy"` -> `"năm 1427"`
        - `"bốn mươi tám giờ"` -> `"48 giờ"`
        - `"mười vạn quân"` -> `"10 vạn quân"`
    """
    if not text or not text.strip():
        return text

    parts = re.split(r"(\s+)", text)
    word_indices: list[int] = []
    affixes: list[tuple[str, str, str, bool]] = []
    low_tokens: list[str] = []
    stops: list[bool] = []

    for p_idx, part in enumerate(parts):
        if not part or part.isspace():
            continue
        pre, core, suf, stop = _split_affixes(part)
        word_indices.append(p_idx)
        affixes.append((pre, core, suf, stop))
        low_tokens.append(core.lower())
        stops.append(stop)

    if not word_indices:
        return text

    out_parts: list[str] = []
    w_cursor = 0
    p_cursor = 0
    n_words = len(word_indices)

    while w_cursor < n_words:
        p_idx = word_indices[w_cursor]
        while p_cursor < p_idx:
            out_parts.append(parts[p_cursor])
            p_cursor += 1

        match = _match_spoken_vn_number_span(low_tokens, stops, w_cursor)
        if match is not None:
            num_val, end_w = match
            first_pre = affixes[w_cursor][0]
            last_suf = affixes[end_w - 1][2]
            out_parts.append(f"{first_pre}{num_val}{last_suf}")
            p_cursor = word_indices[end_w - 1] + 1
            w_cursor = end_w
        else:
            out_parts.append(parts[p_idx])
            p_cursor = p_idx + 1
            w_cursor += 1

    while p_cursor < len(parts):
        out_parts.append(parts[p_cursor])
        p_cursor += 1

    return "".join(out_parts)


def normalize_word_tokens_vn_numbers(
    words: list[dict[str, Any]],
    *,
    max_gap_sec: float = 0.35,
) -> list[dict[str, Any]]:
    """Collapse multi-word spoken Vietnamese numeral spans across the full word-timing stream into compact digit tokens."""
    if not words:
        return []

    n = len(words)
    affixes = [_split_affixes(str(it.get("word", "")).strip()) for it in words]
    low_tokens = [af[1].lower() for af in affixes]
    stops = [af[3] for af in affixes]
    for idx in range(n - 1):
        if not stops[idx] and "end" in words[idx] and "start" in words[idx + 1]:
            if float(words[idx + 1]["start"]) - float(words[idx]["end"]) >= max_gap_sec:
                stops[idx] = True

    out: list[dict[str, Any]] = []
    i = 0
    while i < n:
        match = _match_spoken_vn_number_span(low_tokens, stops, i)
        if match is not None:
            num_val, end_i = match
            span = words[i:end_i]
            first_pre = affixes[i][0]
            last_suf = affixes[end_i - 1][2]
            merged_tok = dict(span[0])
            merged_tok["word"] = f"{first_pre}{num_val}{last_suf}"
            if "start" in span[0]:
                merged_tok["start"] = float(span[0]["start"])
            if "end" in span[-1]:
                merged_tok["end"] = float(span[-1]["end"])
            if "seg_end" in span[-1]:
                merged_tok["seg_end"] = float(span[-1]["seg_end"])
            out.append(merged_tok)
            i = end_i
        else:
            out.append(dict(words[i]))
            i += 1
    return out


def _is_proper_token(tok: str) -> bool:
    clean = re.sub(r"[^A-Za-zÀ-ỹ0-9]", "", tok)
    return bool(clean) and clean[0].isupper()


_CALENDAR_PREFIX_WORDS: frozenset[str] = frozenset({
    "mùng", "mồng", "tháng", "năm", "ngày", "thứ",
})
_CALENDAR_NUM_WORDS: frozenset[str] = frozenset(_D1_9_START) | frozenset({
    "mười", "mươi", "chục", "trăm", "nghìn", "ngàn", "tư", "lăm", "nhăm",
})


def _is_numeric_token(low: str) -> bool:
    return bool(re.fullmatch(r"\d+(?:[.,]\d+)?", low)) or low in VN_NUMBER_WORDS


def _is_calendar_value_token(low: str) -> bool:
    return bool(re.fullmatch(r"\d+(?:[.,]\d+)?", low)) or low in _CALENDAR_NUM_WORDS


def _build_atomic_units(
    clause: list[dict[str, Any]],
    *,
    max_unit_words: int = 4,
) -> list[list[dict[str, Any]]]:
    """Bind proper-noun runs, number+unit runs, calendar dates, and Vietnamese compound bigrams into atomic units."""
    n = len(clause)
    if n == 0:
        return []
    cap = max(2, int(max_unit_words))
    units: list[list[dict[str, Any]]] = []
    i = 0
    while i < n:
        tok_i = clause[i]["_clean"]
        low_i = tok_i.lower()

        # 1. Consecutive capitalized proper-noun tokens (e.g. "Lý Thường Kiệt", "Thành Ung Châu")
        if _is_proper_token(tok_i) and i + 1 < n and _is_proper_token(clause[i + 1]["_clean"]):
            j = i + 2
            while j < n and _is_proper_token(clause[j]["_clean"]) and (j - i) < cap:
                j += 1
            units.append(clause[i:j])
            i = j
            continue

        # 2. Numeric run + trailing measure unit (e.g. "10 vạn quân", "48 giờ", "16 tuổi")
        if _is_numeric_token(low_i):
            j = i + 1
            while j < n and _is_numeric_token(clause[j]["_clean"].lower()) and (j - i) < cap:
                j += 1
            if j < n and (j - i) < cap and clause[j]["_clean"].lower() in VN_MEASURE_UNITS:
                j += 1
            if j - i >= 2:
                units.append(clause[i:j])
                i = j
                continue

        # 2b. Calendar / ordinal prefix + numeric value (e.g. "mùng 4", "tháng 8", "năm 1464", "ngày 16")
        if low_i in _CALENDAR_PREFIX_WORDS and i + 1 < n:
            next_low = clause[i + 1]["_clean"].lower()
            if _is_calendar_value_token(next_low):
                if re.fullmatch(r"\d+(?:[.,]\d+)?", next_low):
                    j = i + 2
                else:
                    j = i + 2
                    while j < n and _is_numeric_token(clause[j]["_clean"].lower()) and (j - i) < cap:
                        j += 1
                units.append(clause[i:j])
                i = j
                continue

        # 3. Known 2-syllable Vietnamese compound word / historical bigram
        if i + 1 < n:
            bigram = f"{low_i} {clause[i + 1]['_clean'].lower()}"
            if bigram in VN_COMPOUND_BIGRAMS:
                units.append(clause[i : i + 2])
                i += 2
                continue

        units.append([clause[i]])
        i += 1
    return units


def partition_vietnamese_clause(
    clause: list[dict[str, Any]],
    *,
    max_words: int = 5,
    max_chars: int = 24,
) -> list[list[dict[str, Any]]]:
    """Partition a spoken clause into compound-safe phrase cards (`1..max_words` words)."""
    eff_max_words = max(1, int(max_words))
    units = _build_atomic_units(clause, max_unit_words=min(4, eff_max_words))
    if not units:
        return []

    chunks: list[list[dict[str, Any]]] = []
    cur_words: list[dict[str, Any]] = []
    for unit in units:
        if len(unit) > eff_max_words:
            if cur_words:
                chunks.append(cur_words)
                cur_words = []
            for k in range(0, len(unit), eff_max_words):
                chunks.append(list(unit[k : k + eff_max_words]))
            continue

        cur_chars = sum(len(w["_clean"]) for w in cur_words) + max(0, len(cur_words) - 1)
        u_chars = sum(len(w["_clean"]) for w in unit) + max(0, len(unit) - 1)
        cand_words = len(cur_words) + len(unit)
        cand_chars = cur_chars + (1 if cur_words else 0) + u_chars

        starts_conj = unit[0]["_clean"].lower() in _CONJUNCTION_BREAKERS and len(cur_words) >= 2
        exceeds = (cand_words > eff_max_words) or (cand_chars > max_chars and len(cur_words) >= 1)

        if cur_words and (exceeds or starts_conj):
            chunks.append(cur_words)
            cur_words = list(unit)
        else:
            cur_words.extend(unit)

    if cur_words:
        chunks.append(cur_words)

    # Rebalance trailing/leading 1-word orphan ONLY when combined length stays <= eff_max_words
    if len(chunks) >= 2 and len(chunks[-1]) == 1:
        if len(chunks[-2]) + 1 <= eff_max_words:
            chunks[-2].extend(chunks[-1])
            chunks.pop()
        elif eff_max_words == 3 and len(chunks[-2]) == 3:
            combined = chunks[-2] + chunks[-1]
            sub_units = _build_atomic_units(combined, max_unit_words=2)
            if len(sub_units) >= 2:
                w_a = [w for u in sub_units[: len(sub_units) // 2] for w in u]
                w_b = [w for u in sub_units[len(sub_units) // 2 :] for w in u]
                if 2 <= len(w_a) <= 3 and 2 <= len(w_b) <= 3:
                    chunks[-2] = w_a
                    chunks[-1] = w_b

    if len(chunks) >= 2 and len(chunks[0]) == 1:
        if len(chunks[1]) + 1 <= eff_max_words:
            chunks[1] = chunks[0] + chunks[1]
            chunks.pop(0)

    return chunks


def _rebuild_phrase(
    words_list: list[dict[str, Any]],
    *,
    seg_key: tuple[str, int],
    clause_idx: int,
) -> dict[str, Any]:
    return {
        "seg_key": seg_key,
        "clause_idx": clause_idx,
        "words": words_list,
        "text": " ".join(x["_clean"] for x in words_list),
        "start": float(words_list[0]["start"]),
        "end": float(words_list[-1]["end"]),
        "seg_end": float(words_list[-1].get("seg_end", words_list[-1]["end"])),
        "emphatic": any(bool(x.get("_emphatic")) for x in words_list),
    }


def merge_short_orphan_phrases(
    phrases: list[dict[str, Any]],
    *,
    min_duration_sec: float = 0.40,
    max_words: int = MAX_V12_SUBTITLE_WORDS,
) -> list[dict[str, Any]]:
    """Eliminate `<min_duration_sec` micro-flash phrases while strictly respecting `max_words`."""
    if min_duration_sec <= 0.0 or not phrases:
        return list(phrases)

    eff_max = max(1, int(max_words))
    out = [dict(p, words=list(p["words"])) for p in phrases]

    # Step 1: Extend natural speech coda into silent gap before next phrase when available
    for idx, ph in enumerate(out):
        dur = float(ph["end"]) - float(ph["start"])
        if dur >= min_duration_sec - 1e-6:
            continue
        ceil_end = float(ph.get("seg_end", ph["end"])) + 0.05
        if idx + 1 < len(out):
            ceil_end = min(ceil_end, float(out[idx + 1]["start"]))
        if ceil_end - float(ph["start"]) >= min_duration_sec - 1e-6:
            ph["end"] = round(float(ph["start"]) + min_duration_sec, 6)

    if len(out) <= 1:
        return out

    changed = True
    while changed and len(out) > 1:
        changed = False
        for i, ph in enumerate(out):
            dur = float(ph["end"]) - float(ph["start"])
            next_gap_short = (
                i + 1 < len(out)
                and (float(out[i + 1]["start"]) - float(ph["start"])) < (min_duration_sec - 1e-6)
            )
            if dur >= (min_duration_sec - 1e-6) and not next_gap_short:
                continue

            left = out[i - 1] if i > 0 else None
            right = out[i + 1] if i + 1 < len(out) else None
            if left is None and right is None:
                continue

            def _score(cand: dict[str, Any] | None, is_left: bool, base_ph: dict[str, Any] = ph) -> tuple[int, int, float, int]:
                if cand is None:
                    return (99, 99, 999.0, 99)
                same_seg = 0 if cand["seg_key"] == base_ph["seg_key"] else (1 if cand["seg_key"][0] == base_ph["seg_key"][0] else 2)
                gap = (
                    max(0.0, float(base_ph["start"]) - float(cand["end"]))
                    if is_left
                    else max(0.0, float(cand["start"]) - float(base_ph["end"]))
                )
                combined_len = len(cand["words"]) + len(base_ph["words"])
                len_pen = 0 if combined_len <= eff_max else 5
                gap_pen = 0 if gap <= 0.45 else 2
                return (same_seg, len_pen + gap_pen, gap, combined_len)

            l_score = _score(left, True)
            r_score = _score(right, False)
            pick_left = l_score <= r_score
            partner_idx = i - 1 if pick_left else i + 1
            partner = out[partner_idx]
            if min(l_score[0], r_score[0]) >= 2 and min(l_score[2], r_score[2]) > 0.65:
                continue

            combined_words = (partner["words"] + ph["words"]) if pick_left else (ph["words"] + partner["words"])
            first_idx = min(i, partner_idx)

            if len(combined_words) <= eff_max:
                merged = _rebuild_phrase(
                    combined_words,
                    seg_key=partner["seg_key"],
                    clause_idx=int(partner["clause_idx"]),
                )
                ceil_end = float(merged.get("seg_end", merged["end"])) + 0.05
                if first_idx + 2 < len(out):
                    ceil_end = min(ceil_end, float(out[first_idx + 2]["start"]))
                if float(merged["end"]) - float(merged["start"]) < min_duration_sec and ceil_end - float(merged["start"]) >= min_duration_sec - 1e-6:
                    merged["end"] = round(float(merged["start"]) + min_duration_sec, 6)
                out[first_idx] = merged
                out.pop(first_idx + 1)
                changed = True
                break

            # Rebalance > eff_max words into two `<= eff_max` cards when total window supports `2 * min_duration_sec`
            span_start = float(combined_words[0]["start"])
            ceil_end = float(combined_words[-1].get("seg_end", combined_words[-1]["end"])) + 0.05
            if first_idx + 2 < len(out):
                ceil_end = min(ceil_end, float(out[first_idx + 2]["start"]))
            span_end = max(float(combined_words[-1]["end"]), min(ceil_end, span_start + 2.0 * min_duration_sec))
            if (span_end - span_start) >= (2.0 * min_duration_sec - 1e-6) and len(combined_words) <= 2 * eff_max:
                min_cut = max(1, len(combined_words) - eff_max)
                max_cut = min(eff_max, len(combined_words) - 1)
                atom_units = _build_atomic_units(combined_words, max_unit_words=eff_max)
                unit_bounds: set[int] = set()
                acc_u = 0
                for au in atom_units[:-1]:
                    acc_u += len(au)
                    unit_bounds.add(acc_u)

                cut = min_cut
                best_score: tuple[int, int, float] | None = None
                for cand_c in range(min_cut, max_cut + 1):
                    breaks_unit = 0 if cand_c in unit_bounds else 1
                    dur_a = float(combined_words[cand_c - 1]["end"]) - span_start
                    dur_b = span_end - float(combined_words[cand_c]["start"])
                    short_halves = int(dur_a < min_duration_sec - 1e-6) + int(dur_b < min_duration_sec - 1e-6)
                    cand_score = (breaks_unit, short_halves, abs(cand_c - len(combined_words) / 2.0))
                    if best_score is None or cand_score < best_score:
                        best_score = cand_score
                        cut = cand_c
                w_a = [dict(x) for x in combined_words[:cut]]
                w_b = [dict(x) for x in combined_words[cut:]]
                mid_t = round(max(span_start + min_duration_sec, min(span_end - min_duration_sec, float(w_b[0]["start"]))), 6)
                w_a[-1]["end"] = max(float(w_a[0]["start"]) + 0.02, mid_t)
                w_b[0]["start"] = mid_t
                w_b[-1]["end"] = max(float(w_b[-1]["end"]), round(mid_t + min_duration_sec, 6))
                p_a = _rebuild_phrase(w_a, seg_key=partner["seg_key"], clause_idx=int(partner["clause_idx"]))
                p_b = _rebuild_phrase(w_b, seg_key=ph["seg_key"], clause_idx=int(ph["clause_idx"]))
                p_a["end"] = max(float(p_a["end"]), round(float(p_a["start"]) + min_duration_sec, 6))
                p_b["end"] = max(float(p_b["end"]), round(float(p_b["start"]) + min_duration_sec, 6))
                if (
                    abs(float(out[first_idx]["start"]) - float(p_a["start"])) > 1e-5
                    or abs(float(out[first_idx]["end"]) - float(p_a["end"])) > 1e-5
                    or out[first_idx]["text"] != p_a["text"]
                ):
                    out[first_idx] = p_a
                    out[first_idx + 1] = p_b
                    changed = True
                    break

    return out


def group_words_into_vn_phrases(
    words: list[dict[str, Any]],
    *,
    min_duration_sec: float = 0.0,
    normalize_numbers: bool | None = None,
    max_words: int | None = None,
) -> list[dict[str, Any]]:
    """Group aligned word dicts into compound-safe Vietnamese subtitle phrases.

    When `normalize_numbers=True` or `min_duration_sec > 0` (V7/V12 cinema subtitles),
    spoken Vietnamese numerals are automatically normalized to digits (`"1427"`, `"48 giờ"`)
    and each card is capped at `1..3` words (`MAX_V12_SUBTITLE_WORDS`).
    """
    v12_active = bool(normalize_numbers) if normalize_numbers is not None else (min_duration_sec > 0.0 or max_words is not None)
    eff_normalize = bool(normalize_numbers) if normalize_numbers is not None else (min_duration_sec > 0.0)
    eff_max_words = int(max_words) if max_words is not None else (MAX_V12_SUBTITLE_WORDS if v12_active else 5)
    eff_max_chars = 22 if eff_max_words <= 3 else 24

    working_words = normalize_word_tokens_vn_numbers(words) if eff_normalize else list(words)

    segments: list[tuple[tuple[str, int], list[dict[str, Any]]]] = []
    for w in working_words:
        raw = str(w.get("word", "")).strip().replace("{", "").replace("}", "")
        clean = re.sub(r"^[.,;:!?\"'“”‘’()\[\]]+|[.,;:!?\"'“”‘’()\[\]]+$", "", raw)
        if not clean:
            continue
        item = {
            **w,
            "_clean": clean,
            "_ends_punct": bool(re.search(r"[,.;:!?…—–][\"'”’)\]]*$", raw)),
            "_emphatic": bool(re.search(r"[!?][\"'”’)\]]*$", raw)),
        }
        seg_key = (str(w.get("beat_id", "")), int(w.get("seg_idx", 0)))
        if not segments:
            segments.append((seg_key, [item]))
            continue
        prev_key, prev_list = segments[-1]
        prev_item = prev_list[-1]
        gap = (
            float(item["start"]) - float(prev_item["end"])
            if ("start" in item and "end" in prev_item)
            else 0.0
        )
        same_beat = seg_key[0] == prev_key[0]
        if seg_key == prev_key or (same_beat and gap < 0.35 and not prev_item["_ends_punct"]):
            prev_list.append(item)
        else:
            segments.append((seg_key, [item]))

    phrase_records: list[dict[str, Any]] = []
    for seg_key, seg_words in segments:
        clauses: list[list[dict[str, Any]]] = []
        cur_clause: list[dict[str, Any]] = []
        for item in seg_words:
            cur_clause.append(item)
            if item["_ends_punct"]:
                clauses.append(cur_clause)
                cur_clause = []
        if cur_clause:
            clauses.append(cur_clause)

        for cl_idx, clause in enumerate(clauses):
            for ch in partition_vietnamese_clause(clause, max_words=eff_max_words, max_chars=eff_max_chars):
                phrase_records.append(_rebuild_phrase(ch, seg_key=seg_key, clause_idx=cl_idx))
    if min_duration_sec > 0.0:
        phrase_records = merge_short_orphan_phrases(
            phrase_records,
            min_duration_sec=min_duration_sec,
            max_words=eff_max_words,
        )
    return phrase_records


def _fmt_ass_time(sec: float) -> str:
    cs = max(0, int(round(sec * 100.0)))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def write_v12_clean_cinema_ass_2k(
    words: list[dict[str, Any]],
    total_duration: float,
    out_ass: Path,
    *,
    muted_beat_ids: set[str] | None = None,
    margin_v: int = 560,
    font_size: int = 114,
    font_name: str = "Be Vietnam Pro ExtraBold",
    min_phrase_dur: float = 0.40,
) -> Path:
    """Write V12 Zero-Box 2K ASS subtitles (`1-3` words/card, `#F8FAFC` + `#FFE066` gold, digits normalized)."""
    muted = {str(b) for b in (muted_beat_ids or set())}
    filtered_words = [w for w in words if str(w.get("beat_id", "")) not in muted]
    phrases = group_words_into_vn_phrases(
        filtered_words,
        min_duration_sec=min_phrase_dur,
        normalize_numbers=True,
        max_words=MAX_V12_SUBTITLE_WORDS,
    )

    ass_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1440",
        "PlayResY: 2560",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: V12Clean,{font_name},{int(font_size)},{V12_ASS_WHITE},{V12_ASS_WHITE},&H000A0B0D,&HA6000000,-1,0,0,0,100,100,0,0,1,9,5,2,96,96,{int(margin_v)},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    for idx, ph in enumerate(phrases):
        ws = max(0.0, float(ph["start"]))
        we = float(ph["end"])
        se = float(ph.get("seg_end", total_duration))
        if idx + 1 < len(phrases):
            next_ws = float(phrases[idx + 1]["start"])
            we = min(next_ws, max(we + 0.06, min(se + 0.06, ws + min_phrase_dur)))
        else:
            we = min(total_duration, max(we + 0.06, ws + min_phrase_dur))
        we = min(total_duration, we)
        if we <= ws + 0.02:
            continue

        pop_tag = r"{\fscx105\fscy105\t(0,70,\fscx100\fscy100)}"
        tokens_parts: list[str] = [pop_tag]
        phrase_words = ph.get("words") or []
        for wi, w_item in enumerate(phrase_words):
            tok_txt = str(w_item.get("_clean") or w_item.get("word") or "").strip()
            if not tok_txt:
                continue
            sep = " " if wi < len(phrase_words) - 1 else ""
            is_gold = bool(re.search(r"\d", tok_txt)) or (ph.get("emphatic") and wi == len(phrase_words) - 1)
            if is_gold:
                tokens_parts.append(f"{{\\c{V12_ASS_GOLD_TAG}}}{tok_txt}{{\\c{V12_ASS_WHITE_TAG}}}{sep}")
            else:
                tokens_parts.append(f"{{\\c{V12_ASS_WHITE_TAG}}}{tok_txt}{sep}")
        rendered = "".join(tokens_parts).strip()
        if rendered:
            ass_lines.append(f"Dialogue: 0,{_fmt_ass_time(ws)},{_fmt_ass_time(we)},V12Clean,,0,0,0,,{rendered}")

    out_ass.parent.mkdir(parents=True, exist_ok=True)
    out_ass.write_text("\n".join(ass_lines) + "\n", encoding="utf-8")
    return out_ass
