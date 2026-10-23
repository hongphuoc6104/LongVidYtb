"""Lossless, phrase-aware captions with acoustic word-timestamp alignment support."""
import math
import re

MAX_CUE_CHARS = 56
MAX_LINE_CHARS = 30
_WEAK_END = {'a', 'an', 'the', 'to', 'of', 'at', 'on', 'in', 'for', 'with',
             'và', 'là', 'của', 'với', 'để', 'nhưng', 'một', 'những', 'các'}


def has_words(text):
    return any(c.isalnum() for c in text)


def _resolve_limits(aspect_ratio=None, max_line=None, max_cue=None):
    if aspect_ratio is not None:
        from format_profiles import caption_limits_for_aspect
        prof_line, prof_cue = caption_limits_for_aspect(aspect_ratio)
    else:
        prof_line, prof_cue = MAX_LINE_CHARS, MAX_CUE_CHARS
    return (max_line if max_line is not None else prof_line,
            max_cue if max_cue is not None else prof_cue)


# Sentence punctuation followed by whitespace; decimals remain inside a token.
_SENTENCE_BOUNDARY = re.compile(r'(?<=[.!?…])["”’\']*\s+')


def sentence_units(text: str) -> list[str]:
    """Preserve terminal quotes while splitting sentence boundaries."""
    clean = re.sub(r"\[pause:[^\]]+\]", " ", text)
    clean = ' '.join(clean.split())
    result: list[str] = []
    cursor = 0
    for match in _SENTENCE_BOUNDARY.finditer(clean):
        end = match.end() - len(match.group().lstrip('"”’\''))
        result.append(clean[cursor:end].strip())
        cursor = match.end()
    if clean[cursor:]:
        result.append(clean[cursor:])
    return result


def phrase_chunks(text: str, max_len: int | None = None, *, aspect_ratio: str | None = None) -> list[str]:
    """Balance phrases inside each sentence, never across sentence boundaries."""
    return [phrase for unit in sentence_units(text)
            for phrase in _phrase_chunks(unit, max_len, aspect_ratio=aspect_ratio)]


def _phrase_chunks(text, max_len=None, *, aspect_ratio=None):
    """Choose word boundaries globally; never split a token or drop punctuation.

    A short final fragment costs more than a slightly earlier balanced break.
    Punctuation stays attached to its token, including closing quotation marks.
    Long tokens are preserved and reported by QA rather than truncated.
    """
    text = re.sub(r"\[pause:[^\]]+\]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    _, resolved_max_cue = _resolve_limits(aspect_ratio=aspect_ratio, max_cue=max_len)
    max_len = resolved_max_cue
    words = text.split()
    if not words:
        return []
    n = len(words)
    costs = [math.inf] * (n + 1)
    paths = [None] * (n + 1)
    costs[n] = 0
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n + 1):
            phrase = ' '.join(words[i:j])
            if len(phrase) > max_len and j > i + 1:
                break
            if not has_words(phrase) and n > 1:
                continue
            length = len(phrase)
            penalty = 1 + ((max_len - min(length, max_len)) / max_len) ** 2
            if n > j and not has_words(words[j]):
                penalty += 100  # Do not strand closing punctuation.
            if j - i == 1 and n > 1:
                penalty += 8
            last = words[j - 1].strip('"\'“”‘’.,!?;:').lower()
            if j < n and last in _WEAK_END:
                penalty += 2
            if re.search(r'[.!?;:,]["”’\']?$', phrase):
                penalty -= .3
            if penalty + costs[j] < costs[i]:
                costs[i], paths[i] = penalty + costs[j], j
    result, i = [], 0
    while i < n:
        j = paths[i] or n
        result.append(' '.join(words[i:j]))
        i = j
    return result


def wrap_phrase(text, max_len=None, *, aspect_ratio=None):
    """At most two balanced lines, favoring a grammatical boundary."""
    resolved_max_line, _ = _resolve_limits(aspect_ratio=aspect_ratio, max_line=max_len)
    max_len = resolved_max_line
    if len(text) <= max_len:
        return text
    words = text.split()
    candidates = []
    for i in range(1, len(words)):
        left, right = ' '.join(words[:i]), ' '.join(words[i:])
        if max(len(left), len(right)) > max_len:
            continue
        if not has_words(left) or not has_words(right):
            continue
        penalty = abs(len(left) - len(right))
        if words[i - 1].strip('.,!?;:"').lower() in _WEAK_END:
            penalty += 12
        if re.search(r'[.!?;:,]["”’\']?$', left):
            penalty -= 6
        candidates.append((penalty, left + '\n' + right))
    return min(candidates, default=(0, text))[1]


def resolve_anchor_timestamp(segment: dict, anchor_quote: str, occurrence: int = 1) -> float:
    """Resolves the exact spoken start timestamp of `anchor_quote` inside `segment`.

    Uses `segment['word_timestamps']` from acoustic/forced alignment when present,
    falling back to proportional character interpolation when absent.
    """
    start = float(segment.get('start', 0.0))
    content_end = float(segment.get('content_end', segment.get('end', start)))
    text = re.sub(r"\[pause:[^\]]+\]", " ", segment.get('text') or '')
    text = re.sub(r"\s+", " ", text).strip()
    if not text or not anchor_quote:
        return start

    word_ts = segment.get('word_timestamps')
    if isinstance(word_ts, list) and word_ts:
        strip_chars = '.,!?;:"\'“”‘’()[]'
        clean_target_words = [w.strip(strip_chars).lower() for w in anchor_quote.split() if w.strip(strip_chars)]
        if clean_target_words:
            seg_words = [str(w.get('word', '')).strip(strip_chars).lower() for w in word_ts]
            found = 0
            t_len = len(clean_target_words)
            for idx in range(len(seg_words) - t_len + 1):
                if seg_words[idx:idx + t_len] == clean_target_words:
                    found += 1
                    if found == max(1, occurrence):
                        rel_start = float(word_ts[idx].get('start', 0.0))
                        return round(start + rel_start, 3)

    # Fallback: character offset interpolation
    pos = 0
    for _ in range(max(1, occurrence)):
        idx = text.find(anchor_quote, pos)
        if idx < 0:
            break
        pos = idx + len(anchor_quote)
    else:
        return round(start + (content_end - start) * (idx / max(1, len(text))), 3)
    return start


def subtitle_cues(segments, *, aspect_ratio=None):
    max_line, max_cue = _resolve_limits(aspect_ratio=aspect_ratio)
    cues = []
    for seg in segments:
        text = ' '.join((seg.get('text') or '').split())
        start, end = seg['start'], seg['end']
        if not all(math.isfinite(float(x)) for x in (start, end)) or start < 0 or end <= start:
            raise ValueError('Invalid caption segment interval')
        content_end = seg.get('content_end', end)
        if not math.isfinite(float(content_end)) or not start < content_end <= end:
            raise ValueError('Invalid content interval before added silence')
        if not text:
            continue  # An explicit silent interval is not a visible caption.
        scene = seg.get('scene_id')
        if not has_words(text) and cues and cues[-1]['scene_id'] == scene and abs(cues[-1]['end'] - start) < .001:
            cues[-1]['text'] = wrap_phrase(' '.join((cues[-1]['text'] + ' ' + text).split()), max_len=max_line)
            cues[-1]['end'] = end
            continue
        chunks = phrase_chunks(text, max_len=max_cue)
        word_ts = seg.get('word_timestamps')
        if isinstance(word_ts, list) and len(word_ts) >= sum(len(c.split()) for c in chunks) and chunks:
            w_cursor = 0
            for idx_c, chunk in enumerate(chunks):
                w_count = len(chunk.split())
                first_w = word_ts[w_cursor]
                last_w = word_ts[min(len(word_ts) - 1, w_cursor + w_count - 1)]
                w_cursor += w_count
                rel_a = float(first_w.get('start', 0.0))
                rel_z = float(last_w.get('end', content_end - start))
                a = start if idx_c == 0 else start + rel_a
                z = end if idx_c == len(chunks) - 1 else start + rel_z
                a = max(start, min(content_end, a))
                if cues:
                    a = max(cues[-1]['end'], a)
                z = max(a + 0.01, min(end, z))
                cues.append({'text': wrap_phrase(chunk, max_len=max_line), 'start': a, 'end': z, 'scene_id': scene})
            continue
        weights = [len(c) for c in chunks]
        total = sum(weights)
        used = 0
        for chunk, weight in zip(chunks, weights, strict=True):
            a = start + (content_end - start) * used / total
            used += weight
            z = end if used == total else start + (content_end - start) * used / total
            if cues:
                a = max(cues[-1]['end'], a)
            z = max(a + 0.01, min(end, z))
            cues.append({'text': wrap_phrase(chunk, max_len=max_line), 'start': a, 'end': z, 'scene_id': scene})
    return cues


def audit_cues(cues, *, aspect_ratio=None):
    """Technical defects and editorial warnings, never a semantic approval."""
    max_line, _ = _resolve_limits(aspect_ratio=aspect_ratio)
    errors, warnings = [], []
    last = 0.
    for i, cue in enumerate(cues):
        text = cue.get('text', '')
        start, end = cue['start'], cue['end']
        ref = {'cue': i + 1, 'start': start, 'end': end, 'text': text}
        if not all(math.isfinite(float(x)) for x in (start, end)) or start < last - .001 or end <= start:
            errors.append(dict(ref, code='CAPTION_TIMELINE', message='Thời gian phụ đề không hợp lệ hoặc chồng lấn.'))
        if not has_words(text):
            errors.append(dict(ref, code='CAPTION_ORPHAN', message='Phụ đề rỗng hoặc chỉ có dấu câu.'))
        if len(sentence_units(text)) > 1:
            errors.append(dict(ref, code='CAPTION_CROSS_SENTENCE', message='Cue crosses a sentence boundary.'))
        lines = text.splitlines()
        if len(lines) > 2 or any(len(line) > max_line for line in lines):
            warnings.append(dict(ref, code='CAPTION_LAYOUT', message='Cần kiểm tra độ dài dòng trên khung thật.'))
        duration = end - start
        if duration > 0 and len(''.join(text.split())) / duration > 20:
            warnings.append(dict(ref, code='CAPTION_READING_RATE', message='Mật độ trên 20 ký tự/giây; đây là ngưỡng gợi ý, cần thử đọc với người học.'))
        if duration < .7:
            warnings.append(dict(ref, code='CAPTION_SHORT_HOLD', message='Thẻ dưới 0,7 giây; kiểm tra đọc và ngắt cụm, không tự kéo lệch lời.'))
        last = end
    return {'errors': errors, 'warnings': warnings,
            'timing_method': 'segment_character_interpolation_not_word_alignment',
            'quality_approval': False}
