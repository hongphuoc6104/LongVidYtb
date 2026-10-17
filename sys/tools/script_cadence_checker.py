#!/usr/bin/env python3
"""Script Cadence & Dead-Air Checker for Video Pilot.

Automated analysis and validation of video script lines/scenes against the
Conversational Essayist acoustic model. Calculates target syllables using
the exact dead-air elimination formula:
    Target Syllables = round((Duration - P_tail - T_pause) * 4.0)

Detects speech rate warnings (> 4.5 or < 3.2 syl/s), timeline drift (> 0.5s),
opening scene pause violations (OPENING_SCENE_PAUSE_FORBIDDEN), and opening hook
length violations (OPENING_HOOK_TOO_LONG > 18 syllables).
Supports both JSON and Markdown script formats.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Acoustic constants matching sys/adapters.py and voice-cadence-pacing.md
DEFAULT_P_TAIL_PARA = 0.70    # Intermediate scenes: DEFAULT_PAUSE['para']
DEFAULT_P_TAIL_LAST = 0.35    # Final scene: DEFAULT_PAUSE['tail']
DEFAULT_P_COMMA = 0.30        # Comma / minor pause: DEFAULT_PAUSE['minor']
NOMINAL_SPEECH_RATE = 4.0     # Nominal speech rate (syllables / second)
OPENING_DYNAMIC_RATE_RANGE: Tuple[float, float] = (4.2, 4.4)  # First 30s dynamic pacing target (1.26x on short_9x16)

# Warning thresholds
MIN_SAFE_SPEECH_RATE = 3.2
MAX_SAFE_SPEECH_RATE = 4.5
MAX_ALLOWABLE_DRIFT = 0.50
DEFAULT_MAX_SENTENCE_SYLLABLES = 25       # Recommended upper limit for a single spoken sentence
DEFAULT_MAX_CLAUSE_SYLLABLES = 18         # Max syllables in a clause without a breathing comma/pause
DEFAULT_MAX_DRAMATIC_PAUSES = 4           # Max Tier-3 dramatic pauses per video (dramatic reveals only)
DEFAULT_MAX_OPENING_HOOK_SYLLABLES = 18   # Max syllables for the first sentence of SC01 (Counter-Intuitive Hook)

# Vietnamese vowel diacritics pattern
VI_DIACRITICS_RE = re.compile(
    r"[àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]",
    re.IGNORECASE,
)

# Pause marker regex e.g. [pause:900ms], [pause:0.9s], [pause:1.2s], [pause:500]
PAUSE_RE = re.compile(r"\[pause:\s*([0-9.]+)\s*(ms|s)?\s*\]", re.IGNORECASE)


def extract_pauses(text: str) -> Tuple[float, List[Dict[str, Any]], str]:
    """Extract dramatic pause markers (e.g. [pause:900ms]) from narration text.

    Returns:
        total_pause_seconds: Sum of all dramatic pauses in seconds.
        pauses: List of dicts describing each pause marker.
        cleaned_text: Narration text with pause tags stripped out.
    """
    pauses: List[Dict[str, Any]] = []
    total_pause_sec = 0.0

    for m in PAUSE_RE.finditer(text):
        val_str = m.group(1)
        unit = (m.group(2) or "").lower()
        val = float(val_str)
        if unit == "ms" or (not unit and val > 10):
            sec = val / 1000.0
        else:
            sec = val
        pauses.append({"raw": m.group(0), "seconds": sec, "position": m.start()})
        total_pause_sec += sec

    cleaned_text = PAUSE_RE.sub(" ", text).strip()
    return round(total_pause_sec, 3), pauses, cleaned_text


def is_vietnamese_text(text: str) -> bool:
    """Detect whether text is predominantly Vietnamese based on diacritics."""
    return bool(VI_DIACRITICS_RE.search(text))


def count_english_syllables_in_word(word: str) -> int:
    """Heuristic rule-based syllable counter for English words."""
    w = word.lower().strip()
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return 0
    if len(w) <= 3:
        return 1

    # Well-known irregular words / common patterns / tech loan words
    overrides = {
        "the": 1, "you": 1, "are": 1, "were": 1, "some": 1, "one": 1,
        "two": 1, "three": 1, "four": 1, "five": 1, "six": 1, "seven": 2,
        "eight": 1, "nine": 1, "ten": 1, "eleven": 3, "twelve": 1,
        "machine": 2, "people": 2, "because": 2, "different": 3,
        "history": 3, "memory": 3, "mystery": 3, "every": 2,
        "skeleton": 3, "science": 2, "quiet": 2, "diet": 2, "poem": 2,
        "create": 2, "creative": 3, "creation": 3, "chaos": 2, "cooperate": 4,
        "archaeologist": 5, "civilization": 5, "agriculture": 4,
        "video": 3, "audio": 3, "media": 3, "area": 3, "idea": 3,
        "radio": 3, "studio": 3, "piano": 3, "data": 2, "wifi": 2,
        "smartphone": 2, "online": 2, "podcast": 2, "ai": 2,
    }
    if w in overrides:
        return overrides[w]

    # Count vowel groups
    vowel_groups = re.findall(r"[aeiouy]+", w)
    count = len(vowel_groups)

    # Silent 'e' at end
    if w.endswith("e") and not w.endswith("ee"):
        # Endings like -le preceded by a consonant (table, bottle) keep syllable
        if len(w) >= 3 and w[-2] == "l" and w[-3] not in "aeiouy":
            pass
        else:
            count -= 1

    # Endings like -ed
    if w.endswith("ed") and len(w) > 3:
        if w[-3] not in "td":
            count -= 1

    # Endings like -es (unless preceded by s, z, x, ch, sh)
    if w.endswith("es") and len(w) > 3:
        if not (w.endswith("ses") or w.endswith("zes") or w.endswith("xes") or w.endswith("ches") or w.endswith("shes")):
            count -= 1

    # Diphthongs that split into two vowels (e.g., -ia-, -io-, -iu-)
    split_vowels = re.findall(r"(?:ia|io|iu|eo|oi|ua)", w)
    if split_vowels and not w.endswith("tion") and not w.endswith("sion"):
        count += len(split_vowels)

    return max(1, count)


# Common tech / media English loanwords in Vietnamese explainer narrations
COMMON_VI_LOANWORDS = {
    "video": 3, "audio": 3, "media": 3, "data": 2, "wifi": 2, "camera": 3,
    "smartphone": 2, "laptop": 2, "internet": 3, "podcast": 2, "online": 2,
    "youtube": 2, "tiktok": 2, "facebook": 2, "ceo": 3,
}


def is_thousand_separated_number(tok: str) -> bool:
    """Detect if a numeric token has thousand separators e.g. 50.000 or 90,000."""
    return bool(re.match(r"^\d{1,3}(?:[.,]\d{3})+$", tok))


def count_vietnamese_number_syllables(tok: str) -> int:
    """Count spoken Vietnamese syllables for numeric tokens."""
    if is_thousand_separated_number(tok):
        cleaned = tok.replace(".", "").replace(",", "")
        val = int(cleaned)
        if val < 1000:
            return 2 if val % 100 == 0 else 3
        elif val < 10000:
            return 2 if val % 1000 == 0 else 4
        elif val < 100000:
            return 3 if val % 1000 == 0 else 4
        elif val < 1000000:
            return 3 if val % 100000 == 0 else 4
        else:
            return 2 if val % 1000000 == 0 else 4

    # Decimals e.g. 2.4 or 2,4
    if "." in tok or "," in tok:
        parts = re.split(r"[.,]", tok)
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            left = count_vietnamese_number_syllables(parts[0])
            right = len(parts[1])
            return left + 1 + right

    if tok.isdigit():
        val = int(tok)
        if val <= 10:
            return 1
        elif val < 20:
            return 2
        elif val < 100:
            return 2
        elif val < 1000:
            return 2 if val % 100 == 0 else 3
        elif val < 10000:
            return 2 if val % 1000 == 0 else 4
        else:
            return len(tok)

    return 1


def is_number_token(tok: str) -> bool:
    """Check if token is a number (integer, decimal, or thousand-separated)."""
    if is_thousand_separated_number(tok):
        return True
    if tok.isdigit():
        return True
    if ("." in tok or "," in tok) and re.match(r"^\d+[.,]\d+$", tok):
        return True
    return False


def count_syllables(text: str, lang: str = "auto") -> int:
    """Accurately count syllables in Vietnamese or English narration text.

    In Vietnamese, words are monosyllabic when tokenized by whitespace.
    Slashes (/) and hyphens (-) separating words are split appropriately.
    In English, words are counted using vowel heuristics and pronunciation rules.
    """
    _, _, clean = extract_pauses(text)
    # Strip markdown symbols and formatting
    clean = re.sub(r"[*_`#~]", "", clean)
    # Split compound connectors like / or hyphens into whitespace
    clean = re.sub(r"[\u2014\u2013—–-]", " ", clean)
    clean = clean.replace("/", " ")

    # Tokenize by whitespace
    raw_tokens = clean.split()
    tokens = []
    for tok in raw_tokens:
        # Strip outer punctuation
        t = re.sub(r"^[^\w]+|[^\w]+$", "", tok, flags=re.UNICODE)
        if t and any(c.isalnum() for c in t):
            tokens.append(t)

    if not tokens:
        return 0

    if lang == "auto":
        is_vi = is_vietnamese_text(clean)
    else:
        is_vi = (lang.lower() == "vi")

    if is_vi:
        total = 0
        for tok in tokens:
            lower = tok.lower()
            if is_number_token(tok):
                total += count_vietnamese_number_syllables(tok)
            elif tok.isupper() and len(tok) <= 4 and tok.isalpha():
                # Acronym e.g. AI, CEO, DNA
                total += len(tok)
            elif lower in COMMON_VI_LOANWORDS:
                total += COMMON_VI_LOANWORDS[lower]
            elif any(c in "fjwz" for c in lower) and tok.isalpha():
                # Non-native Vietnamese letters indicate loanword
                total += count_english_syllables_in_word(tok)
            else:
                total += 1
        return total
    else:
        # English counting
        total = 0
        for tok in tokens:
            if is_number_token(tok):
                if is_thousand_separated_number(tok):
                    total += 2  # e.g. 50,000 -> "fifty thousand"
                elif ("." in tok or "," in tok):
                    total += 3  # e.g. 2.4 -> "two point four"
                else:
                    total += 2 if len(tok) <= 2 else len(tok)
            else:
                total += count_english_syllables_in_word(tok)
        return total


def count_commas(text: str) -> int:
    """Count commas and minor pause marks in text (excluding numerical separators)."""
    _, _, clean = extract_pauses(text)
    # Match commas and semicolons that are NOT sandwiched between digits (e.g. 2,4 or 50,000)
    commas = re.findall(r"(?<!\d)[,;]|[,;](?!\d)", clean)
    return len(commas)


def split_sentences(text: str) -> List[str]:
    """Split narration text into individual sentences (ignoring numeric dots like 50.000 or 2.4)."""
    _, _, clean = extract_pauses(text)
    parts = re.split(r"(?<!\d)[.!?…]+(?!\d)", clean)
    return [p.strip() for p in parts if p.strip()]


def calculate_target_syllables(
    duration: float,
    is_last: bool = False,
    pause_seconds: float = 0.0,
    nominal_rate: float = NOMINAL_SPEECH_RATE,
    compensate_commas: bool = False,
    comma_count: int = 0,
    p_tail_para: float = DEFAULT_P_TAIL_PARA,
    p_tail_last: float = DEFAULT_P_TAIL_LAST,
) -> int:
    """Calculate the target syllables according to the dead-air formula.

    Formula:
        Target Syllables = round((Duration - P_tail - pause_seconds) * nominal_rate)
    """
    p_tail = p_tail_last if is_last else p_tail_para
    net_duration = duration - p_tail - pause_seconds

    if compensate_commas and comma_count > 0:
        net_duration -= comma_count * DEFAULT_P_COMMA

    if net_duration <= 0:
        return 0

    return round(net_duration * nominal_rate)


def parse_json_script(content: str) -> List[Dict[str, Any]]:
    """Parse JSON script content into standardized scene objects."""
    data = json.loads(content)
    raw_scenes: List[Dict[str, Any]] = []

    if isinstance(data, list):
        raw_scenes = data
    elif isinstance(data, dict):
        if "scenes" in data and isinstance(data["scenes"], list):
            raw_scenes = data["scenes"]
        elif "content_scenes" in data and isinstance(data["content_scenes"], list):
            raw_scenes = data["content_scenes"]
        else:
            # Single scene object
            raw_scenes = [data]

    standardized = []
    for idx, sc in enumerate(raw_scenes, 1):
        scene_id = sc.get("id") or sc.get("scene_id") or sc.get("name") or f"SC{idx:02d}"
        dur = sc.get("duration") or sc.get("target_duration") or sc.get("seconds") or 0.0
        narration = sc.get("narration") or sc.get("text") or sc.get("dialogue") or sc.get("script") or ""
        beats = sc.get("beats") or sc.get("visual_beats") or []
        standardized.append({
            "id": str(scene_id),
            "duration": float(dur),
            "narration": str(narration),
            **({"beats": beats} if "beats" in sc or "visual_beats" in sc else {}),
        })
    return standardized


def parse_markdown_script(content: str) -> List[Dict[str, Any]]:
    """Parse Markdown script content into standardized scene objects.

    Supports:
    1. Header format: ## SC01 (12.0s) / ### Scene 1 [12s] / ## Phân cảnh 01 (12.0s)
    2. Table format: | SC01 | 12.0s | Narration... | (supports Cảnh, Phân cảnh, Thời gian, Lời thoại...)
    3. Bullet format: - **SC01** (12.0s): Narration...
    """
    scenes: List[Dict[str, Any]] = []

    # Check for Markdown table format across all table blocks in the file
    raw_lines = content.splitlines()
    table_blocks: List[List[str]] = []
    curr_tbl: List[str] = []
    for raw_line in raw_lines:
        ls = raw_line.strip()
        if ls.startswith("|"):
            curr_tbl.append(ls)
        else:
            if len(curr_tbl) >= 3:
                table_blocks.append(curr_tbl)
            curr_tbl = []
    if len(curr_tbl) >= 3:
        table_blocks.append(curr_tbl)

    candidate_tables: List[List[Dict[str, Any]]] = []
    id_keywords = ("scene", "phân cảnh", "cảnh", "id", "stt", "màn")
    dur_keywords = ("dự kiến", "target", "duration", "thời lượng", "thời gian", "sec", "giây", "time", "length")
    narr_keywords = ("narration", "thoại", "câu thoại", "lời thoại", "lời bình", "lời đọc", "script", "kịch bản", "voiceover", "vo", "nội dung", "text")

    for tbl in table_blocks:
        header_cols = [re.sub(r"\\[a-zA-Z]+", "", c.strip().lower()) for c in tbl[0].strip("|").split("|")]
        id_col = -1
        dur_col = -1
        narr_col = -1
        for i, col in enumerate(header_cols):
            if any(k in col for k in id_keywords) and id_col == -1:
                id_col = i
            elif any(k in col for k in dur_keywords) and dur_col == -1:
                dur_col = i
            elif (any(k in col for k in narr_keywords) or re.search(r"\btext\b", col)) and narr_col == -1:
                narr_col = i

        if id_col != -1 and dur_col != -1 and narr_col != -1:
            tbl_scenes: List[Dict[str, Any]] = []
            for row in tbl[2:]:  # skip header and separator
                cols = [c.strip() for c in row.strip("|").split("|")]
                if len(cols) > max(id_col, dur_col, narr_col):
                    sc_id = cols[id_col].replace("**", "").strip()
                    dur_match = re.search(r"([0-9.]+)", cols[dur_col])
                    if not dur_match or not sc_id or sc_id.lower() in ("tổng", "total"):
                        continue
                    dur = float(dur_match.group(1))
                    narr = cols[narr_col].strip().strip('"')
                    tbl_scenes.append({
                        "id": sc_id,
                        "duration": dur,
                        "narration": narr,
                    })
            if tbl_scenes:
                candidate_tables.append(tbl_scenes)

    if candidate_tables:
        # Choose the table with the most scenes (prevents overview tables with 1 row from shadowing scripts)
        candidate_tables.sort(key=len, reverse=True)
        return candidate_tables[0]

    # Header / Section based format
    lines = content.splitlines()
    current_scene: Optional[Dict[str, Any]] = None
    narr_lines: List[str] = []

    header_re = re.compile(
        r"^(?:#{1,4})\s+(?:\*{0,2})([^\n:(\[\]]+?)(?:\*{0,2})\s*[:\-\(\[]\s*([0-9.]+)\s*(?:s|sec|giây)?[\]\)]?",
        re.IGNORECASE,
    )
    bullet_re = re.compile(
        r"^[-*]\s+\*{0,2}([^\n:(\[\]]+?)\*{0,2}\s*[\(\[]\s*([0-9.]+)\s*(?:s|sec|giây)?[\]\)]\s*[:\-]\s*(.*)$",
        re.IGNORECASE,
    )

    for line in lines:
        line_str = line.strip()

        # Check if line is a markdown heading (#...)
        if line_str.startswith("#"):
            h_m = header_re.match(line_str)
            if h_m:
                if current_scene:
                    current_scene["narration"] = " ".join(narr_lines).strip()
                    scenes.append(current_scene)
                    narr_lines = []
                current_scene = {
                    "id": h_m.group(1).strip(),
                    "duration": float(h_m.group(2)),
                    "narration": "",
                }
            else:
                # Non-scene heading e.g. ## Notes, ## Overview
                if current_scene:
                    current_scene["narration"] = " ".join(narr_lines).strip()
                    scenes.append(current_scene)
                    narr_lines = []
                    current_scene = None
            continue

        # Check bullet format
        b_m = bullet_re.match(line_str)
        if b_m:
            if current_scene:
                current_scene["narration"] = " ".join(narr_lines).strip()
                scenes.append(current_scene)
                narr_lines = []
                current_scene = None
            scenes.append({
                "id": b_m.group(1).strip(),
                "duration": float(b_m.group(2)),
                "narration": b_m.group(3).strip().strip('"'),
            })
            continue

        if current_scene:
            # Skip visual beat lines or commentary lines
            lower = line_str.lower()
            if re.match(r"^(?:visual|beats?|ghi chú|note|hình ảnh)\s*[:\-]", line_str, re.IGNORECASE):
                continue
            if lower.startswith("[visual") or lower.startswith("(visual") or lower.startswith("[beat") or lower.startswith("(beat"):
                continue
            if line_str:
                # Strip inline bracketed visual tags e.g. [Visual: ...]
                cleaned_line = re.sub(r"\[(?:visual|beats?|ghi chú|note|hình ảnh)[^\]]*\]", "", line_str, flags=re.IGNORECASE).strip()
                cleaned_line = re.sub(r"\((?:visual|beats?|ghi chú|note|hình ảnh)[^\)]*\)", "", cleaned_line, flags=re.IGNORECASE).strip()
                if cleaned_line:
                    narr_lines.append(cleaned_line.strip('"'))

    if current_scene:
        current_scene["narration"] = " ".join(narr_lines).strip()
        scenes.append(current_scene)

    return scenes


def parse_script_file(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Parse a script file from disk, detecting JSON or Markdown format."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Script file not found: {path}")

    content = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in (".json",):
        scenes = parse_json_script(content)
        if any(sc.get("duration", 0.0) <= 0.0 for sc in scenes) and path.parent:
            for companion_name in ("script.json", "scene_durations.json"):
                companion = path.parent / companion_name
                if companion.is_file() and companion.resolve() != path.resolve():
                    try:
                        c_scenes = parse_json_script(companion.read_text(encoding="utf-8"))
                        dur_map = {cs["id"]: cs["duration"] for cs in c_scenes if cs.get("duration", 0.0) > 0.0}
                        for sc in scenes:
                            if sc.get("duration", 0.0) <= 0.0 and sc["id"] in dur_map:
                                sc["duration"] = dur_map[sc["id"]]
                    except Exception:
                        pass
                    if all(sc.get("duration", 0.0) > 0.0 for sc in scenes):
                        break
        return scenes
    elif suffix in (".md", ".markdown", ".txt"):
        try:
            return parse_json_script(content)
        except json.JSONDecodeError:
            return parse_markdown_script(content)
    else:
        try:
            return parse_json_script(content)
        except json.JSONDecodeError:
            return parse_markdown_script(content)


class SceneCadenceReport:
    """Individual scene cadence analysis report."""

    def __init__(
        self,
        scene_id: str,
        duration: float,
        narration: str,
        is_last: bool,
        nominal_rate: float = NOMINAL_SPEECH_RATE,
        p_tail_para: float = DEFAULT_P_TAIL_PARA,
        p_tail_last: float = DEFAULT_P_TAIL_LAST,
        compensate_commas: bool = False,
        lang: str = "auto",
        max_sentences: int = 5,
        max_syllables: Optional[int] = None,
        max_sentence_syllables: Optional[int] = None,
        max_clause_syllables: Optional[int] = None,
        is_first: bool = False,
        forbid_opening_pause: bool = False,
        max_opening_hook_syllables: Optional[int] = None,
    ):
        self.scene_id = scene_id
        self.duration = duration
        self.narration = narration
        self.is_last = is_last
        self.is_first = is_first
        self.forbid_opening_pause = forbid_opening_pause
        self.max_opening_hook_syllables = max_opening_hook_syllables
        self.nominal_rate = nominal_rate
        self.p_tail = p_tail_last if is_last else p_tail_para
        self.compensate_commas = compensate_commas
        self.lang = lang
        self.max_sentences = max_sentences
        self.max_syllables = max_syllables
        self.max_sentence_syllables = max_sentence_syllables
        self.max_clause_syllables = max_clause_syllables

        # Analysis
        self.pause_seconds, self.pauses, self.clean_narration = extract_pauses(narration)
        self.comma_count = count_commas(self.clean_narration)
        self.syllable_count = count_syllables(self.clean_narration, lang=lang)
        self.sentences = split_sentences(self.clean_narration)
        self.sentence_count = len(self.sentences)
        self.short_sentence_count = sum(
            1 for s in self.sentences if 0 < count_syllables(s, lang=lang) < 6
        )

        # Net speaking duration
        comma_overhead = (self.comma_count * DEFAULT_P_COMMA) if self.compensate_commas else 0.0
        self.net_speaking_duration = max(0.0, self.duration - self.p_tail - self.pause_seconds - comma_overhead)

        # Target syllables
        self.target_syllables = calculate_target_syllables(
            duration=self.duration,
            is_last=self.is_last,
            pause_seconds=self.pause_seconds,
            nominal_rate=self.nominal_rate,
            compensate_commas=self.compensate_commas,
            comma_count=self.comma_count,
            p_tail_para=p_tail_para,
            p_tail_last=p_tail_last,
        )

        # Effective speech rate
        if self.net_speaking_duration > 0:
            self.speech_rate = round(self.syllable_count / self.net_speaking_duration, 2)
        else:
            self.speech_rate = 0.0

        # Estimated audio duration and drift
        self.estimated_speech_duration = round(self.syllable_count / self.nominal_rate, 2)
        self.estimated_audio_duration = round(
            self.estimated_speech_duration + self.p_tail + self.pause_seconds + comma_overhead, 2
        )
        self.drift = round(self.estimated_audio_duration - self.duration, 2)

        # Warnings
        self.warnings: List[str] = []
        if self.duration <= 0:
            self.warnings.append("INVALID_DURATION: Scene duration must be > 0s")
        elif (self.duration - self.p_tail - self.pause_seconds) <= 0 and self.syllable_count > 0:
            self.warnings.append(
                f"DURATION_TOO_SHORT: Scene duration ({self.duration:.1f}s) is shorter than tail/pause overhead ({self.p_tail + self.pause_seconds:.2f}s)"
            )
        elif self.speech_rate > MAX_SAFE_SPEECH_RATE:
            self.warnings.append(
                f"RATE_TOO_FAST: {self.speech_rate} syl/s exceeds maximum safe rate {MAX_SAFE_SPEECH_RATE} syl/s"
            )
        elif self.speech_rate < MIN_SAFE_SPEECH_RATE and self.syllable_count > 0:
            self.warnings.append(
                f"RATE_TOO_SLOW: {self.speech_rate} syl/s is below minimum safe rate {MIN_SAFE_SPEECH_RATE} syl/s"
            )

        if abs(self.drift) > MAX_ALLOWABLE_DRIFT:
            if self.drift < -MAX_ALLOWABLE_DRIFT:
                self.warnings.append(
                    f"DEAD_AIR: Audio is {abs(self.drift):.2f}s shorter than scene duration (drift: {self.drift:+.2f}s)"
                )
            else:
                self.warnings.append(
                    f"TIMELINE_DRIFT: Audio exceeds scene duration by {self.drift:.2f}s (tolerance: ±{MAX_ALLOWABLE_DRIFT}s)"
                )

        # Longer scenes can carry more natural short sentences. Flag only a
        # genuinely compressed sequence, not short wording by itself.
        sentence_limit = max(self.max_sentences, int(self.duration / 1.5))
        if self.sentence_count > sentence_limit:
            self.warnings.append(
                f"SENTENCE_FRAGMENTATION: Scene has {self.sentence_count} sentences "
                f"({self.short_sentence_count} short sentences < 6 syl), risking TTS boundary pause buildup"
            )
        if self.max_syllables is not None and self.syllable_count > self.max_syllables:
            self.warnings.append(
                f"SCENE_TOO_LONG: Scene has {self.syllable_count} syllables (exceeds concise limit of {self.max_syllables}); split into shorter scenes"
            )

        # Opening scene specific guards: Zero Pause in First 15s (SC01) & Counter-Intuitive Hook <= 18 syl
        is_opening_scene = self.is_first or str(self.scene_id).strip().upper() in ("SC01", "SCENE 1", "PHÂN CẢNH 01")
        if self.forbid_opening_pause and is_opening_scene and self.pauses:
            self.warnings.append(
                f"OPENING_SCENE_PAUSE_FORBIDDEN: Opening scene {self.scene_id} contains {len(self.pauses)} pause tag(s) "
                f"({self.pause_seconds:.2f}s); zero [pause:...] allowed in first 15 seconds (SC01)"
            )

        if self.max_opening_hook_syllables is not None and is_opening_scene and self.sentences:
            first_sent_syl = count_syllables(self.sentences[0], lang=self.lang)
            if first_sent_syl > self.max_opening_hook_syllables:
                self.warnings.append(
                    f"OPENING_HOOK_TOO_LONG: Opening hook sentence in {self.scene_id} has {first_sent_syl} syllables "
                    f"(exceeds Counter-Intuitive Hook limit of {self.max_opening_hook_syllables}): '{self.sentences[0][:40]}...'"
                )

        if self.max_sentence_syllables is not None:
            for s_idx, s in enumerate(self.sentences, 1):
                s_syl = count_syllables(s, lang=self.lang)
                if s_syl > self.max_sentence_syllables:
                    self.warnings.append(
                        f"SENTENCE_TOO_LONG: Sentence #{s_idx} has {s_syl} syllables "
                        f"(exceeds limit of {self.max_sentence_syllables}); split into shorter sentences"
                    )

        if self.max_clause_syllables is not None:
            for s_idx, s in enumerate(self.sentences, 1):
                clauses = re.split(r"[,;—\u2013\u2014]", s)
                for c_idx, c in enumerate(clauses, 1):
                    c_clean = c.strip()
                    if not c_clean:
                        continue
                    c_syl = count_syllables(c_clean, lang=self.lang)
                    if c_syl > self.max_clause_syllables:
                        snippet = c_clean[:35] + ("..." if len(c_clean) > 35 else "")
                        self.warnings.append(
                            f"BREATHLESS_CLAUSE: Clause #{c_idx} in sentence #{s_idx} has {c_syl} syllables "
                            f"without a breathing comma (exceeds limit of {self.max_clause_syllables}): '{snippet}'"
                        )

        unnatural_comma_re = re.compile(
            r",\s+(?:là|chỉ\s+tạo|bằng\s+cách|nhằm)\b",
            re.IGNORECASE,
        )
        for s_idx, s in enumerate(self.sentences, 1):
            m = unnatural_comma_re.search(s)
            if m:
                self.warnings.append(
                    f"UNNATURAL_SUBJECT_VERB_COMMA: Sentence #{s_idx} in {self.scene_id} places an unnatural comma "
                    f"before predicate/connector ('{m.group(0).strip()}'); split into 2 sentences instead"
                )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "duration": self.duration,
            "is_last": self.is_last,
            "p_tail": self.p_tail,
            "pause_seconds": self.pause_seconds,
            "comma_count": self.comma_count,
            "sentence_count": self.sentence_count,
            "target_syllables": self.target_syllables,
            "actual_syllables": self.syllable_count,
            "speech_rate": self.speech_rate,
            "estimated_audio_duration": self.estimated_audio_duration,
            "drift": self.drift,
            "warnings": self.warnings,
            "status": "PASS" if not self.warnings else "WARN",
        }


class ScriptCadenceChecker:
    """Master checker and orchestrator for entire script cadence analysis."""

    def __init__(
        self,
        nominal_rate: float = NOMINAL_SPEECH_RATE,
        p_tail_para: float = DEFAULT_P_TAIL_PARA,
        p_tail_last: float = DEFAULT_P_TAIL_LAST,
        compensate_commas: bool = False,
        lang: str = "auto",
        max_sentences: int = 5,
        max_syllables: Optional[int] = None,
        max_sentence_syllables: Optional[int] = None,
        max_clause_syllables: Optional[int] = None,
        max_dramatic_pauses: Optional[int] = None,
        forbid_opening_pause: bool = False,
        max_opening_hook_syllables: Optional[int] = None,
    ):
        self.nominal_rate = nominal_rate
        self.p_tail_para = p_tail_para
        self.p_tail_last = p_tail_last
        self.compensate_commas = compensate_commas
        self.lang = lang
        self.max_sentences = max_sentences
        self.max_syllables = max_syllables
        self.max_sentence_syllables = max_sentence_syllables
        self.max_clause_syllables = max_clause_syllables
        self.max_dramatic_pauses = max_dramatic_pauses
        self.forbid_opening_pause = forbid_opening_pause
        self.max_opening_hook_syllables = max_opening_hook_syllables

    def check_scenes(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a list of scene dictionaries."""
        if not scenes:
            return {
                "total_scenes": 0,
                "total_duration": 0.0,
                "total_target_syllables": 0,
                "total_actual_syllables": 0,
                "total_estimated_audio": 0.0,
                "net_drift": 0.0,
                "max_drift": 0.0,
                "warnings_count": 0,
                "scenes": [],
                "status": "PASS",
            }

        total_scenes = len(scenes)
        reports: List[SceneCadenceReport] = []

        for idx, sc in enumerate(scenes):
            is_last = (idx == total_scenes - 1)
            is_first = (idx == 0)
            report = SceneCadenceReport(
                scene_id=sc.get("id", f"SC{idx+1:02d}"),
                duration=float(sc.get("duration", 0.0)),
                narration=sc.get("narration", ""),
                is_last=is_last,
                nominal_rate=self.nominal_rate,
                p_tail_para=self.p_tail_para,
                p_tail_last=self.p_tail_last,
                compensate_commas=self.compensate_commas,
                lang=self.lang,
                max_sentences=self.max_sentences,
                max_syllables=self.max_syllables,
                max_sentence_syllables=self.max_sentence_syllables,
                max_clause_syllables=self.max_clause_syllables,
                is_first=is_first,
                forbid_opening_pause=self.forbid_opening_pause,
                max_opening_hook_syllables=self.max_opening_hook_syllables,
            )
            if 'beats' in sc and report.duration / max(1, len(sc['beats'])) > 2.8:
                report.warnings.append(
                    f"LOW_VISUAL_BEAT_DENSITY: {report.scene_id} averages "
                    f"{report.duration / max(1, len(sc['beats'])):.2f}s per visual beat (maximum 2.8s)"
                )
            reports.append(report)

        total_pauses = sum(len(r.pauses) for r in reports)
        if self.max_dramatic_pauses is not None and total_pauses > self.max_dramatic_pauses:
            for r in reports:
                if r.pauses:
                    r.warnings.append(
                        f"EXCESSIVE_DRAMATIC_PAUSES: Script contains {total_pauses} dramatic pauses "
                        f"(exceeds limit of {self.max_dramatic_pauses}). Tier-3 [pause] must be reserved for dramatic reveals only"
                    )

        total_duration = round(sum(r.duration for r in reports), 2)
        total_target_syl = sum(r.target_syllables for r in reports)
        total_actual_syl = sum(r.syllable_count for r in reports)
        total_est_audio = round(sum(r.estimated_audio_duration for r in reports), 2)
        net_drift = round(total_est_audio - total_duration, 2)
        max_drift = round(max((abs(r.drift) for r in reports), default=0.0), 2)
        total_warnings = sum(len(r.warnings) for r in reports)

        return {
            "total_scenes": total_scenes,
            "total_duration": total_duration,
            "total_target_syllables": total_target_syl,
            "total_actual_syllables": total_actual_syl,
            "total_estimated_audio": total_est_audio,
            "net_drift": net_drift,
            "max_drift": max_drift,
            "warnings_count": total_warnings,
            "scenes": [r.to_dict() for r in reports],
            "status": "PASS" if total_warnings == 0 else "WARN",
        }

    def check_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Analyze a script file from disk."""
        scenes = parse_script_file(file_path)
        return self.check_scenes(scenes)


def format_text_report(result: Dict[str, Any]) -> str:
    """Format analysis results into a clean, human-readable terminal table."""
    lines = []
    lines.append("=" * 96)
    lines.append("               VIDEO PILOT SCRIPT CADENCE & DEAD-AIR CHECKER REPORT")
    lines.append("=" * 96)
    lines.append(
        f"{'Scene':<8} {'Dur':<7} {'P_tail':<7} {'Pause':<7} {'Target':<7} {'Actual':<7} {'Rate':<9} {'Est Audio':<10} {'Drift':<8} {'Status':<6}"
    )
    lines.append("-" * 96)

    for sc in result.get("scenes", []):
        drift_str = f"{sc['drift']:+.2f}s"
        rate_str = f"{sc['speech_rate']:.2f}/s"
        status_str = sc["status"]
        lines.append(
            f"{sc['scene_id']:<8} {sc['duration']:<6.1f}s {sc['p_tail']:<6.2f}s {sc['pause_seconds']:<6.2f}s "
            f"{sc['target_syllables']:<7} {sc['actual_syllables']:<7} {rate_str:<9} {sc['estimated_audio_duration']:<9.2f}s "
            f"{drift_str:<8} {status_str:<6}"
        )
        if sc.get("warnings"):
            for w in sc["warnings"]:
                lines.append(f"  └─ [!] {w}")

    lines.append("-" * 96)
    lines.append(
        f"TOTAL:   {result.get('total_duration', 0.0):<6.1f}s                      "
        f"{result.get('total_target_syllables', 0):<7} {result.get('total_actual_syllables', 0):<7}          "
        f"{result.get('total_estimated_audio', 0.0):<9.2f}s {result.get('net_drift', 0.0):+.2f}s  {result.get('status', 'PASS')}"
    )
    lines.append("=" * 96)
    lines.append(
        f"Summary: {result.get('total_scenes', 0)} scenes | Max drift: {result.get('max_drift', 0.0):.2f}s | "
        f"Warnings: {result.get('warnings_count', 0)} | Overall: {result.get('status', 'PASS')}"
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate video script syllable cadence, dead-air padding, and duration drift."
    )
    parser.add_argument("script", help="Path to script file (JSON or Markdown)")
    parser.add_argument("--rate", type=float, default=NOMINAL_SPEECH_RATE, help="Nominal speech rate (syl/s)")
    parser.add_argument("--p-tail-para", type=float, default=DEFAULT_P_TAIL_PARA, help="P_tail for intermediate scenes")
    parser.add_argument("--p-tail-last", type=float, default=DEFAULT_P_TAIL_LAST, help="P_tail for final scene")
    parser.add_argument("--compensate-commas", action="store_true", help="Compensate minor pauses for commas")
    parser.add_argument("--lang", default="auto", choices=["auto", "vi", "en"], help="Narration language")
    parser.add_argument("--max-syllables", type=int, default=None, help="Maximum syllables per scene (e.g. 36 for concise scenes)")
    parser.add_argument("--max-sentence-syllables", type=int, default=None, help="Maximum syllables per sentence (e.g. 25)")
    parser.add_argument("--max-clause-syllables", type=int, default=None, help="Maximum syllables per clause without comma (e.g. 18)")
    parser.add_argument("--max-dramatic-pauses", type=int, default=None, help="Maximum dramatic [pause] markers in entire script (e.g. 4)")
    parser.add_argument("--forbid-opening-pause", action="store_true", help="Forbid any [pause:...] tag in opening scene SC01 (first 15s)")
    parser.add_argument("--max-opening-hook-syllables", type=int, default=None, help="Maximum syllables in the first sentence of SC01 (e.g. 18)")
    parser.add_argument("--json", action="store_true", help="Output analysis in JSON format")
    parser.add_argument("--strict", action="store_true", help="Exit with non-zero code if any warning is found")

    args = parser.parse_args()

    checker = ScriptCadenceChecker(
        nominal_rate=args.rate,
        p_tail_para=args.p_tail_para,
        p_tail_last=args.p_tail_last,
        compensate_commas=args.compensate_commas,
        lang=args.lang,
        max_syllables=args.max_syllables,
        max_sentence_syllables=args.max_sentence_syllables,
        max_clause_syllables=args.max_clause_syllables,
        max_dramatic_pauses=args.max_dramatic_pauses,
        forbid_opening_pause=args.forbid_opening_pause,
        max_opening_hook_syllables=args.max_opening_hook_syllables,
    )

    try:
        result = checker.check_file(args.script)
    except Exception as ex:
        print(f"Error checking script: {ex}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_text_report(result))

    if args.strict and result.get("warnings_count", 0) > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
