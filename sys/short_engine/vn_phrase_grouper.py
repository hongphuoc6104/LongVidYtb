"""Vietnamese compound-aware & proper-noun-preserving subtitle phrase grouper."""
from __future__ import annotations

import re
from typing import Any

# Common 2-syllable Vietnamese compound words & historical military/chronicle bigrams
# that must never be split across consecutive subtitle cards.
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
    "vạn", "nghìn", "ngàn", "trăm", "triệu", "quân", "lính", "chiến", "thuyền",
    "ngày", "đêm", "năm", "tháng", "tuổi", "giờ", "khắc", "phút", "giây",
    "km", "mét", "cây", "tấn", "khẩu", "người", "vị", "vua", "tướng",
    "châu", "đồn", "thành", "mũi", "bao", "chữ", "tầng", "lần", "bước",
    "gia", "phát", "trận", "đòn",
})

_CONJUNCTION_BREAKERS: frozenset[str] = frozenset({
    "nhưng", "nhưng mà", "tuy nhiên", "vì vậy", "nên", "nếu", "khi", "lúc",
    "mà", "hoặc", "hay", "còn", "rồi", "để", "bằng", "tại", "trước", "sau",
})


def _is_proper_token(tok: str) -> bool:
    clean = re.sub(r"[^A-Za-zÀ-ỹ0-9]", "", tok)
    return bool(clean) and clean[0].isupper()


def _is_numeric_token(low: str) -> bool:
    return bool(re.fullmatch(r"\d+(?:[.,]\d+)?", low)) or low in VN_NUMBER_WORDS


def _build_atomic_units(clause: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Bind proper-noun runs, number+unit runs, and Vietnamese compound bigrams into atomic units."""
    n = len(clause)
    if n == 0:
        return []
    units: list[list[dict[str, Any]]] = []
    i = 0
    while i < n:
        tok_i = clause[i]["_clean"]
        low_i = tok_i.lower()

        # 1. Consecutive capitalized proper-noun tokens (e.g. "Lý Thường Kiệt", "Thành Ung Châu")
        # Skip index 0 only if token 0 is sentence-initial and token 1 is NOT capitalized.
        if _is_proper_token(tok_i) and i + 1 < n and _is_proper_token(clause[i + 1]["_clean"]):
            j = i + 2
            while j < n and _is_proper_token(clause[j]["_clean"]) and (j - i) < 4:
                j += 1
            units.append(clause[i:j])
            i = j
            continue

        # 2. Numeric run + trailing measure unit (e.g. "mười vạn quân", "bốn mươi hai ngày", "16 tuổi")
        if _is_numeric_token(low_i):
            j = i + 1
            while j < n and _is_numeric_token(clause[j]["_clean"].lower()) and (j - i) < 4:
                j += 1
            if j < n and clause[j]["_clean"].lower() in VN_MEASURE_UNITS:
                j += 1
            if j - i >= 2:
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
    """Partition a spoken clause into 2-5 syllable phrases without ever splitting compounds or proper names."""
    units = _build_atomic_units(clause)
    if not units:
        return []

    chunks: list[list[dict[str, Any]]] = []
    cur_words: list[dict[str, Any]] = []
    for u_idx, unit in enumerate(units):
        cur_chars = sum(len(w["_clean"]) for w in cur_words) + max(0, len(cur_words) - 1)
        u_chars = sum(len(w["_clean"]) for w in unit) + max(0, len(unit) - 1)
        cand_words = len(cur_words) + len(unit)
        cand_chars = cur_chars + (1 if cur_words else 0) + u_chars

        # Prefer breaking cleanly before conjunctions once current phrase has >= 2 words
        starts_conj = unit[0]["_clean"].lower() in _CONJUNCTION_BREAKERS and len(cur_words) >= 2
        exceeds = (cand_words > max_words) or (cand_chars > max_chars)

        if cur_words and (exceeds or starts_conj):
            chunks.append(cur_words)
            cur_words = list(unit)
        else:
            cur_words.extend(unit)

        # If remaining units only have 1 single-word unit and current chunk has <= 3 words, keep scanning
        _ = u_idx

    if cur_words:
        chunks.append(cur_words)

    # Rebalance trailing 1-word orphan ONLY if it doesn't break an atomic unit cleanly
    if len(chunks) >= 2 and len(chunks[-1]) == 1:
        if len(chunks[-2]) <= 4:
            chunks[-2].extend(chunks[-1])
            chunks.pop()
    if len(chunks) >= 2 and len(chunks[0]) == 1:
        if len(chunks[1]) <= 4:
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
    max_words: int = 5,
) -> list[dict[str, Any]]:
    """Merge `<min_duration_sec` micro-flash/orphan phrases safely with neighbors while preserving compounds."""
    if min_duration_sec <= 0.0 or len(phrases) <= 1:
        return list(phrases)

    out = [dict(p, words=list(p["words"])) for p in phrases]
    changed = True
    while changed and len(out) > 1:
        changed = False
        for i, ph in enumerate(out):
            dur = float(ph["end"]) - float(ph["start"])
            is_short = dur < (min_duration_sec - 1e-6)
            if not is_short:
                continue

            left = out[i - 1] if i > 0 else None
            right = out[i + 1] if i + 1 < len(out) else None

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
                len_pen = 0 if combined_len <= 4 else (1 if combined_len <= max_words else 3)
                gap_pen = 0 if gap <= 0.45 else 2
                return (same_seg, gap_pen + len_pen, gap, combined_len)

            l_score = _score(left, True)
            r_score = _score(right, False)
            if left is None and right is None:
                continue
            pick_left = l_score <= r_score
            partner_idx = i - 1 if pick_left else i + 1
            partner = out[partner_idx]
            if min(l_score[0], r_score[0]) >= 2 and min(l_score[2], r_score[2]) > 0.65:
                continue

            combined_words = (partner["words"] + ph["words"]) if pick_left else (ph["words"] + partner["words"])
            # If merging pushes > 4 words, try atomic-unit rebalance into two >= min_duration_sec chunks
            if len(combined_words) > 4:
                units = _build_atomic_units(combined_words)
                best_split: tuple[list[dict[str, Any]], list[dict[str, Any]]] | None = None
                if len(units) >= 2:
                    for cut in range(1, len(units)):
                        w_a = [w for u in units[:cut] for w in u]
                        w_b = [w for u in units[cut:] for w in u]
                        if 2 <= len(w_a) <= 4 and 2 <= len(w_b) <= 4:
                            d_a = float(w_a[-1]["end"]) - float(w_a[0]["start"])
                            d_b = float(w_b[-1]["end"]) - float(w_b[0]["start"])
                            if d_a >= min_duration_sec and d_b >= min_duration_sec:
                                best_split = (w_a, w_b)
                                break
                if best_split is not None:
                    first_idx = min(i, partner_idx)
                    out[first_idx] = _rebuild_phrase(
                        best_split[0],
                        seg_key=partner["seg_key"],
                        clause_idx=int(partner["clause_idx"]),
                    )
                    out[first_idx + 1] = _rebuild_phrase(
                        best_split[1],
                        seg_key=ph["seg_key"],
                        clause_idx=int(ph["clause_idx"]),
                    )
                    changed = True
                    break

            merged = _rebuild_phrase(
                combined_words,
                seg_key=partner["seg_key"],
                clause_idx=int(partner["clause_idx"]),
            )
            first_idx = min(i, partner_idx)
            out[first_idx] = merged
            out.pop(first_idx + 1)
            changed = True
            break
    return out


def group_words_into_vn_phrases(
    words: list[dict[str, Any]],
    *,
    min_duration_sec: float = 0.0,
) -> list[dict[str, Any]]:
    """Group aligned word dicts into compound-safe, proper-noun-preserving Vietnamese phrases."""
    segments: list[tuple[tuple[str, int], list[dict[str, Any]]]] = []
    for w in words:
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
        if not segments or segments[-1][0] != seg_key:
            segments.append((seg_key, [item]))
        else:
            segments[-1][1].append(item)

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
            for ch in partition_vietnamese_clause(clause):
                phrase_records.append(_rebuild_phrase(ch, seg_key=seg_key, clause_idx=cl_idx))
    if min_duration_sec > 0.0:
        phrase_records = merge_short_orphan_phrases(phrase_records, min_duration_sec=min_duration_sec)
    return phrase_records
