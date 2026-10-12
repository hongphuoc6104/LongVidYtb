#!/usr/bin/env python3
"""
Vietnamese Text Normalizer for TTS (Colab OmniVoice — Adam).
Converts numbers, dates, percentages, symbols, and foreign loanwords/names
into 100% natural Vietnamese phonetic spellings.
"""
import re
from typing import Dict

# Dictionary of specialized foreign names & proper nouns to Vietnamese phonetics
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
}

ONES = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]


def num_to_vn_words(n: int) -> str:
    """Converts an integer from 0 to 999,999 into Vietnamese words."""
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
    # Check percentage
    if raw.endswith("%"):
        val_str = raw[:-1].replace(".", "").replace(",", "")
        try:
            return f"{num_to_vn_words(int(val_str))} phần trăm"
        except ValueError:
            return raw

    # Clean dots used as thousand separators (e.g., 50.000 -> 50000)
    clean_val = raw.replace(".", "")
    if clean_val.isdigit():
        n = int(clean_val)
        return num_to_vn_words(n)
    return raw


def normalize_for_tts(text: str) -> str:
    """
    Normalizes a sentence for flawless Vietnamese TTS pronunciation:
    - 100% natural number-to-words conversion
    - Percentage conversion (81% -> tám mươi mốt phần trăm)
    - Foreign names & proper nouns phonetic transliteration
    - Punctuation sanitization for natural breathing pauses
    """
    res = text

    # 1. Foreign proper nouns & names replacement (case-insensitive regex)
    for pattern, replacement in FOREIGN_NAMES_MAP.items():
        res = re.sub(pattern, replacement, res, flags=re.IGNORECASE)

    # 2. Year special case: e.g. "năm 1963" -> "năm một nghìn chín trăm sáu mươi ba"
    def replace_year(m):
        prefix = m.group(1)
        year_num = int(m.group(2))
        return f"{prefix} {num_to_vn_words(year_num)}"

    res = re.sub(r"(Năm|năm)\s+(\d{4})\b", replace_year, res)

    # 3. Percentages: e.g. "81%" -> "tám mươi mốt phần trăm"
    res = re.sub(r"\b(\d+)%", lambda m: f"{num_to_vn_words(int(m.group(1)))} phần trăm", res)

    # 4. Thousand separator numbers: e.g. "50.000", "70.000", "40.000", "10.000", "90.000"
    res = re.sub(r"\b\d{1,3}(?:\.\d{3})+\b", normalize_number_token, res)

    # 5. Standalone digits/numbers: e.g. "17", "15", "20", "6", "4"
    res = re.sub(r"\b\d+\b", normalize_number_token, res)

    # 6. Punctuation sanitization for natural speech and pauses
    res = res.replace("...", ",").replace("…", ",")
    res = res.replace("—", ",").replace("–", ",")
    res = res.replace(":", ",").replace(";", ",")

    # Clean double commas and excessive spaces
    res = re.sub(r",\s*,", ",", res)
    res = re.sub(r"\s+", " ", res).strip()

    return res


if __name__ == "__main__":
    # Test cases
    test_samples = [
        "Bây giờ, hãy thử quay ngược thời gian về 50.000 năm trước.",
        "Năm 1963, nhà nhân chủng học Richard Lee đã lặn lội đặt chân vào sa mạc Kalahari, ngay vùng biên giới Botswana.",
        "Ông đến đây để tận mắt nghiên cứu người Ju/'hoansi.",
        "Những người tiền sử này chỉ mất vỏn vẹn khoảng 17 giờ mỗi tuần để kiếm đủ thức ăn!",
        "Thế nhưng, kết quả mỗi lần đo đạc đều tương tự đến kinh ngạc: chỉ dao động từ 15 đến 20 giờ mỗi tuần!",
        "Có tới 81% các cuộc trò chuyện quanh ánh lửa... đã biến thành những câu chuyện kể!",
        "Tại hang Blombos ở Nam Phi, các nhà khảo cổ đã tìm thấy những chuỗi hạt vỏ ốc hơn 70.000 năm tuổi.",
        "Chưa hết, vào năm 2008 tại nước Đức, người ta còn khai quật được cây sáo 40.000 năm.",
        "Vào năm 2014, nhà nhân chủng học Polly Wiessner đã công bố nghiên cứu.",
        "Ngày nay, bạn sẽ dành khoảng 90.000 giờ trong cuộc đời mình... chỉ để làm việc.",
    ]
    print("=== TEST PHONETIC NORMALIZATION ===")
    for s in test_samples:
        print("IN :", s)
        print("OUT:", normalize_for_tts(s))
        print()
