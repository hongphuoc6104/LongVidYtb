#!/usr/bin/env python3
"""
Vietnamese Text Normalizer & Phonetic Gatekeeper for TTS (Colab OmniVoice — Adam).
Converts numbers, dates, percentages, symbols, and foreign loanwords/names
into 100% natural Vietnamese phonetic spellings, extracts exact [pause:Xms]
utterance boundaries, and blocks un-transliterated foreign tokens before TTS.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Set

# Expanded dictionary of foreign names, proper nouns, and scientific loanwords
FOREIGN_NAMES_MAP: Dict[str, str] = {
    r"\bRichard Lee\b": "Ri-chát Li",
    r"\bRichard\b": "Ri-chát",
    r"\bLee\b": "Li",
    r"\bJu/'hoansi\b": "Giu-hoan-si",
    r"\bJu/'\b": "Giu",
    r"\bKalahari\b": "Ka-la-ha-ri",
    r"\bBotswana\b": "Bốt-xoa-na",
    r"\bHadza\b": "Hát-da",
    r"\bTanzania\b": "Tan-da-ni-a",
    r"\bAche\b": "A-sê",
    r"\bParaguay\b": "Pa-ra-goay",
    r"\bMartu\b": "Mác-tu",
    r"\bBlombos\b": "Bờ-lôm-bốt",
    r"\bPolly Wiessner\b": "Pô-li Uýt-nơ",
    r"\bPolly\b": "Pô-li",
    r"\bWiessner\b": "Uýt-nơ",
    r"\bJames Suzman\b": "Giêm Xút-man",
    r"\bJames\b": "Giêm",
    r"\bSuzman\b": "Xút-man",
    r"\bdopamine\b": "đô-pa-min",
    r"\bcortisol\b": "cóc-ti-dôn",
    r"\badrenaline\b": "a-đrê-na-lin",
    r"\bserotonin\b": "sê-rô-tô-nin",
    r"\boxytocin\b": "ô-xi-tô-xin",
    r"\bendorphin\b": "en-đô-phin",
    r"\bglucose\b": "glu-cô-dơ",
    r"\bprefrontal cortex\b": "vỏ não trước trán",
    r"\bamygdala\b": "hạch hạnh nhân",
    r"\bhippocampus\b": "hồi hải mã",
    r"\bSumer\b": "Su-me",
    r"\bEdubba\b": "Ê-đu-ba",
    r"\bMesopotamia\b": "Mê-sô-pô-ta-mi-a",
    r"\bPrussia\b": "Phổ",
    r"\bJaak Panksepp\b": "Giác Păng-xép",
    r"\bJaak\b": "Giác",
    r"\bPanksepp\b": "Păng-xép",
    r"\bTim Pychyl\b": "Tim Pi-chin",
    r"\bPychyl\b": "Pi-chin",
    r"\bFuschia Sirois\b": "Phu-si-a Si-roa",
    r"\bSirois\b": "Si-roa",
    r"\bYuval Noah Harari\b": "Giu-van Nô-a Ha-ra-ri",
    r"\bHarari\b": "Ha-ra-ri",
    r"\bDarwin\b": "Đác-uyn",
    r"\bNewton\b": "Niu-tơn",
    r"\bEinstein\b": "Anh-xtanh",
    r"\bAristotle\b": "A-ri-xtốt",
    r"\bSocrates\b": "Xô-crát",
    r"\bPlato\b": "Pla-tông",
    r"\bHomo sapiens\b": "Hô-mô sa-pi-en",
    r"\bNeanderthal\b": "Nê-an-đơ-than",
    r"\bsmartphone\b": "điện thoại thông minh",
    r"\bpodcast\b": "pót-cát",
    r"\bvideo\b": "vi-đê-ô",
    r"\bemail\b": "i-meo",
    r"\binternet\b": "in-tơ-nét",
    r"\bwifi\b": "oai-phai",
}

ONES = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]

PAUSE_TAG_RE = re.compile(r"\[pause:\s*([0-9.]+)\s*(ms|s)?\s*\]", re.IGNORECASE)

# Foreign orthography patterns that do not exist in standard Vietnamese words
FOREIGN_ORTHOGRAPHY_PATTERNS = [
    (re.compile(r"[fjwz]", re.IGNORECASE), "chứa chữ cái ngoại lai f/j/w/z"),
    (re.compile(r"^[a-z]{8,}$", re.IGNORECASE), "từ không dấu dài trên 7 ký tự (tiếng Anh chưa phiên âm)"),
    (re.compile(r"^(?:sh|st|sp|sk|sl|sm|sn|sw|sc|str|spr|scr|pl|pr|bl|br|cl|cr|dr|fl|fr|gl|gr)", re.IGNORECASE), "cụm phụ âm đầu tiếng Anh"),
    (re.compile(r"(?:tion|sion|ment|ness|able|ible|ight|ough|ity|logy|graphy|ck|ld|lt|mp|nk|nd|nt|rk|rt|st|ct|pt|ft)$", re.IGNORECASE), "cụm phụ âm/hậu tố cuối tiếng Anh"),
]


def num_to_vn_words(n: int) -> str:
    """Converts an integer from 0 to 999,999,999 into Vietnamese words."""
    if n < 0:
        return "âm " + num_to_vn_words(-n)
    if n < 10:
        return ONES[n]
    if n < 20:
        if n == 10:
            return "mười"
        if n == 15:
            return "mười lăm"
        return "mười " + ONES[n % 10]
    if n < 100:
        tens = n // 10
        units = n % 10
        tens_str = (ONES[tens] + " mươi") if tens > 1 else "mười"
        if units == 0:
            return tens_str
        if units == 1:
            return tens_str + (" mốt" if tens > 1 else " một")
        if units == 4:
            return tens_str + " tư"
        if units == 5:
            return tens_str + " lăm"
        return f"{tens_str} {ONES[units]}"
    if n < 1000:
        hundreds = n // 100
        rem = n % 100
        h_str = f"{ONES[hundreds]} trăm"
        if rem == 0:
            return h_str
        if rem < 10:
            return f"{h_str} lẻ {ONES[rem]}"
        return f"{h_str} {num_to_vn_words(rem)}"
    if n < 1_000_000:
        thousands = n // 1000
        rem = n % 1000
        th_str = f"{num_to_vn_words(thousands)} nghìn"
        if rem == 0:
            return th_str
        if rem < 10:
            return f"{th_str} không trăm lẻ {ONES[rem]}"
        if rem < 100:
            return f"{th_str} không trăm {num_to_vn_words(rem)}"
        return f"{th_str} {num_to_vn_words(rem)}"
    if n < 1_000_000_000:
        millions = n // 1_000_000
        rem = n % 1_000_000
        m_str = f"{num_to_vn_words(millions)} triệu"
        if rem == 0:
            return m_str
        return f"{m_str} {num_to_vn_words(rem)}"
    return str(n)


def normalize_number_token(match: re.Match) -> str:
    raw = match.group(0)
    if raw.endswith("%"):
        val_str = raw[:-1].replace(".", "").replace(",", "")
        try:
            return f"{num_to_vn_words(int(val_str))} phần trăm"
        except ValueError:
            return raw

    clean_val = raw.replace(".", "")
    if clean_val.isdigit():
        n = int(clean_val)
        return num_to_vn_words(n)
    return raw


def parse_pause_seconds(raw_val: str, unit: str | None) -> float:
    val = float(raw_val)
    unit_clean = (unit or "").lower()
    if unit_clean == "ms" or (not unit_clean and val > 10):
        return round(val / 1000.0, 3)
    return round(val, 3)


def split_utterances_by_pause(
    text: str,
    normalize_segments: bool = True,
    default_tail_pause: float = 0.0,
) -> List[Dict[str, Any]]:
    """Splits a narration string at explicit [pause:Xms] tags into sub-utterances
    with exact pause_after durations in seconds, preserving dramatic timing.
    """
    parts: List[Dict[str, Any]] = []
    last_idx = 0
    for match in PAUSE_TAG_RE.finditer(text):
        chunk = text[last_idx:match.start()].strip()
        pause_sec = parse_pause_seconds(match.group(1), match.group(2))
        if chunk:
            norm_chunk = normalize_for_tts(chunk) if normalize_segments else chunk
            parts.append({"text": norm_chunk, "pause_after": pause_sec, "raw_pause_tag": match.group(0)})
        elif parts:
            parts[-1]["pause_after"] = round(parts[-1]["pause_after"] + pause_sec, 3)
        last_idx = match.end()

    tail_chunk = text[last_idx:].strip()
    if tail_chunk:
        norm_tail = normalize_for_tts(tail_chunk) if normalize_segments else tail_chunk
        parts.append({"text": norm_tail, "pause_after": round(float(default_tail_pause), 3), "raw_pause_tag": None})

    return parts


def normalize_for_tts(text: str, extra_map: Dict[str, str] | None = None) -> str:
    """
    Normalizes a sentence for flawless Vietnamese TTS pronunciation:
    - 100% natural number-to-words conversion
    - Percentage conversion (81% -> tám mươi mốt phần trăm)
    - Foreign names & proper nouns phonetic transliteration
    - Punctuation sanitization for natural breathing pauses
    """
    res = PAUSE_TAG_RE.sub(" , ", text)

    combined_map = dict(FOREIGN_NAMES_MAP)
    if extra_map:
        combined_map.update(extra_map)
    for pattern, replacement in combined_map.items():
        res = re.sub(pattern, replacement, res, flags=re.IGNORECASE)

    def replace_year(m: re.Match) -> str:
        prefix = m.group(1)
        year_num = int(m.group(2))
        return f"{prefix} {num_to_vn_words(year_num)}"

    res = re.sub(r"(Năm|năm)\s+(\d{4})\b", replace_year, res)
    res = re.sub(r"\b(\d+)%", lambda m: f"{num_to_vn_words(int(m.group(1)))} phần trăm", res)
    res = re.sub(r"\b\d{1,3}(?:\.\d{3})+\b", normalize_number_token, res)
    res = re.sub(
        r"\b(\d+),(\d+)\b",
        lambda m: f"{num_to_vn_words(int(m.group(1)))} phẩy {num_to_vn_words(int(m.group(2)))}",
        res,
    )
    res = re.sub(r"\b\d+\b", normalize_number_token, res)

    res = res.replace("...", ",").replace("…", ",")
    res = res.replace("—", ",").replace("–", ",")
    res = res.replace(":", ",").replace(";", ",")

    res = re.sub(r",\s*,", ",", res)
    res = re.sub(r"\s+", " ", res).strip()

    return res


def detect_unnormalized_tokens(
    text: str,
    allowed_tokens: Set[str] | None = None,
) -> List[Dict[str, str]]:
    """Scans normalized Vietnamese text and flags any leftover numbers, symbols,
    or un-transliterated foreign words that could cause TTS phoneme fallback.
    """
    allowed = {t.lower() for t in (allowed_tokens or set())}
    issues: List[Dict[str, str]] = []

    for m in re.finditer(r"\b\d+\b|[%/]", text):
        issues.append({
            "token": m.group(0),
            "reason": "Chứa chữ số hoặc ký hiệu chưa chuyển thành chữ tiếng Việt",
        })

    raw_words = re.findall(r"[A-Za-zÀ-ỹ]+(?:-[A-Za-zÀ-ỹ]+)*", text)
    for word in raw_words:
        w_lower = word.lower()
        if w_lower in allowed:
            continue
        sub_parts = w_lower.split("-")
        for part in sub_parts:
            if not part or part in allowed:
                continue
            for pat, reason in FOREIGN_ORTHOGRAPHY_PATTERNS:
                if pat.search(part):
                    issues.append({
                        "token": word,
                        "reason": f"Từ nghi vấn ngoại lai chưa phiên âm ({reason})",
                    })
                    break
    return issues


def enforce_tts_normalization_gate(
    text: str,
    extra_map: Dict[str, str] | None = None,
    allowed_tokens: Set[str] | None = None,
) -> str:
    """Normalizes text and enforces strict zero-foreign-token gate before TTS."""
    normalized = normalize_for_tts(text, extra_map=extra_map)
    issues = detect_unnormalized_tokens(normalized, allowed_tokens=allowed_tokens)
    if issues:
        bad_list = ", ".join(f"{x['token']!r} ({x['reason']})" for x in issues[:5])
        raise ValueError(f"UNNORMALIZED_FOREIGN_TOKEN: Phát hiện từ chưa chuẩn hóa ngữ âm: {bad_list}")
    return normalized
