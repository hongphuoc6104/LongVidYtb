"""Unit tests for acoustic word-timestamp alignment, DP subtitle chunking, wrapping, anchor resolution, and cue audit."""

import numpy as np
import pytest
from colab_bridge.worker import _extract_word_timestamps_acoustic
from scripts.subtitles import (
    audit_cues,
    phrase_chunks,
    resolve_anchor_timestamp,
    sentence_units,
    subtitle_cues,
    wrap_phrase,
)

SR = 48000


# ---------------------------------------------------------------------------
# Functional Group 1: Acoustic Word Timestamps (_extract_word_timestamps_acoustic)
# ---------------------------------------------------------------------------


class TestExtractWordTimestampsAcoustic:
    """Verifies acoustic energy-windowed word timestamps, phonetic weights, time floor, and edge cases."""

    def test_word_count_and_token_alignment(self):
        """Clean speech waveform extracts exact token words and timestamps."""
        text = "Nhận thức bản chất tri thức."
        dur_sec = 2.0
        n_samples = round(dur_sec * SR)
        # Synthesize active speech signal
        t = np.arange(n_samples) / SR
        w = (0.25 * np.sin(2 * np.pi * 220.0 * t)).astype(np.float32)

        res = _extract_word_timestamps_acoustic(w, text, sr=SR)
        assert len(res) == 6
        assert [r["word"] for r in res] == ["Nhận", "thức", "bản", "chất", "tri", "thức."]

    def test_monotonicity_and_duration_bounds(self):
        """Start and end timestamps are strictly monotonic and obey minimum hold."""
        text = "Tư duy phản biện là công cụ nhận thức cốt lõi."
        dur_sec = 3.5
        n_samples = round(dur_sec * SR)
        w = (0.20 * np.sin(2 * np.pi * 180.0 * (np.arange(n_samples) / SR))).astype(np.float32)

        res = _extract_word_timestamps_acoustic(w, text, sr=SR)
        assert len(res) > 0
        for i, item in enumerate(res):
            assert item["start"] < item["end"], f"Word {item['word']} has invalid interval"
            assert item["end"] - item["start"] >= 0.010, f"Word {item['word']} duration below 10ms"
            assert item["start"] >= 0.0
            assert item["end"] <= dur_sec + 0.001
            if i > 0:
                assert item["start"] >= res[i - 1]["start"], "Start time is not monotonically non-decreasing"
                assert res[i - 1]["end"] <= item["start"], (
                    f"Timestamp interval overlap detected: '{res[i-1]['word']}' ends at {res[i-1]['end']} "
                    f"but '{item['word']}' starts at {item['start']}"
                )

    def test_pause_tags_stripped_from_words(self):
        """Explicit [pause:...] tags are stripped from words list."""
        text = "[pause:500ms] Xin chào [pause:800ms] các bạn. [pause:200ms]"
        w = (0.20 * np.sin(2 * np.pi * 200.0 * (np.arange(round(2.5 * SR)) / SR))).astype(np.float32)
        res = _extract_word_timestamps_acoustic(w, text, sr=SR)
        words = [r["word"] for r in res]
        assert words == ["Xin", "chào", "các", "bạn."]
        assert not any("[pause" in wd for wd in words)

    def test_pure_pause_text_returns_empty(self):
        """Text consisting only of pause tags returns an empty list."""
        w = np.zeros(SR, dtype=np.float32)
        assert _extract_word_timestamps_acoustic(w, "[pause:800ms]", sr=SR) == []
        assert _extract_word_timestamps_acoustic(w, "[pause:500ms] [pause:1s]", sr=SR) == []

    def test_empty_audio_or_empty_text_returns_empty(self):
        """Empty audio, zero-duration, or empty/whitespace text returns empty list."""
        w_active = np.full(SR, 0.1, dtype=np.float32)
        w_empty = np.array([], dtype=np.float32)

        assert _extract_word_timestamps_acoustic(w_empty, "Xin chào", sr=SR) == []
        assert _extract_word_timestamps_acoustic(w_active, "", sr=SR) == []
        assert _extract_word_timestamps_acoustic(w_active, "   ", sr=SR) == []
        assert _extract_word_timestamps_acoustic(w_active, None, sr=SR) == []

    def test_single_word_spans_total_duration(self):
        """A single word on a waveform spans the interval up to total duration."""
        dur_sec = 1.2
        w = (0.25 * np.sin(2 * np.pi * 250.0 * (np.arange(round(dur_sec * SR)) / SR))).astype(np.float32)
        res = _extract_word_timestamps_acoustic(w, "Alo", sr=SR)
        assert len(res) == 1
        assert res[0]["word"] == "Alo"
        assert res[0]["start"] == 0.0
        assert abs(res[0]["end"] - dur_sec) <= 0.02

    def test_short_audio_fallback_to_uniform_step(self):
        """When n_frames < len(words), safely triggers linear step fallback without crashing."""
        # 10ms hop = 480 samples. 0.05s audio = 2400 samples = 5 frames.
        # Text with 10 words -> 5 frames < 10 words.
        w = np.full(round(0.05 * SR), 0.1, dtype=np.float32)
        text = "Một hai ba bốn năm sáu bảy tám chín mười"
        res = _extract_word_timestamps_acoustic(w, text, sr=SR)
        assert len(res) == 10
        for i, item in enumerate(res):
            assert item["start"] <= item["end"]
            if i > 0:
                assert item["start"] >= res[i - 1]["start"]

    def test_energy_clustering_around_voiced_nuclei(self):
        """Acoustic energy clusters word timestamps around speech bursts rather than silent regions."""
        # 0.8s speech, 1.0s silence, 0.8s speech (total 2.6s)
        t_speech = np.arange(round(0.8 * SR)) / SR
        speech = (0.30 * np.sin(2 * np.pi * 300.0 * t_speech)).astype(np.float32)
        silence = np.zeros(round(1.0 * SR), dtype=np.float32)
        w = np.concatenate([speech, silence, speech])

        text = "Bắt đầu. Kết thúc."
        res = _extract_word_timestamps_acoustic(w, text, sr=SR)
        assert len(res) == 4
        assert [r["word"] for r in res] == ["Bắt", "đầu.", "Kết", "thúc."]

        # "Bắt" is completely inside the first speech block (t < 0.8s)
        assert res[0]["end"] <= 0.8
        # "thúc." is completely inside the second speech block (t >= 1.8s)
        assert res[3]["start"] >= 1.8

    def test_time_floor_prevents_zero_duration_during_silence(self):
        """30% time floor ensures even pure silent audio distributes non-zero word durations."""
        w = np.zeros(round(2.0 * SR), dtype=np.float32)
        text = "Từ một từ hai từ ba từ bốn"
        res = _extract_word_timestamps_acoustic(w, text, sr=SR)
        assert len(res) == 8
        for item in res:
            assert item["end"] - item["start"] >= 0.010
        assert res[0]["start"] == 0.0
        assert res[-1]["end"] <= 2.001

    def test_vietnamese_accented_phonetic_weighting(self):
        """Accented Vietnamese characters (À-ỹ) retain full phonetic length weighting."""
        w = (0.2 * np.sin(np.arange(round(1.5 * SR)) * 0.03)).astype(np.float32)
        text = '“Nghiên cứu” và "AI".'
        res = _extract_word_timestamps_acoustic(w, text, sr=SR)
        assert len(res) == 4
        # Tokens retain quotation marks in output dict
        assert res[0]["word"] == "“Nghiên"
        assert res[1]["word"] == "cứu”"
        assert res[2]["word"] == "và"
        assert res[3]["word"] == '"AI".'

    @pytest.mark.parametrize(
        ("text", "dur_sec"),
        [
            ("ai làm gì đây", 1.0),
            ("ba ba ba ba", 1.0),
            ("nhanh nhanh nhanh hơn nữa", 0.8),
            ("w0 w1 w2 w3 w4 w5 w6 w7", 1.0),
            ("Nguyễn Trãi danh nhân văn hóa thế giới", 2.0),
        ],
    )
    def test_consecutive_words_strictly_non_overlapping(self, text: str, dur_sec: float):
        """Consecutive word timestamps must strictly satisfy res[i]['end'] <= res[i+1]['start']."""
        n_samples = round(dur_sec * SR)
        t = np.arange(n_samples) / SR
        w = (0.25 * np.sin(2 * np.pi * 220.0 * t)).astype(np.float32)

        res = _extract_word_timestamps_acoustic(w, text, sr=SR)
        assert len(res) == len(text.split())
        for i in range(len(res) - 1):
            diff = round(res[i]["end"] - res[i + 1]["start"], 4)
            assert res[i]["end"] <= res[i + 1]["start"], (
                f"Overlap of {diff}s between word '{res[i]['word']}' ({res[i]['end']}) "
                f"and word '{res[i+1]['word']}' ({res[i+1]['start']})"
            )


# ---------------------------------------------------------------------------
# Functional Group 2: Sentence Unit Splitting (sentence_units)
# ---------------------------------------------------------------------------


class TestSentenceUnits:
    """Verifies sentence boundary splitting, quotation preservation, and decimal handling."""

    def test_sentence_units_splits_terminal_punctuation(self):
        """Splits on '.', '!', '?', '…' followed by whitespace."""
        text = "Câu một. Câu hai! Câu ba? Câu bốn… Câu năm."
        units = sentence_units(text)
        assert units == ["Câu một.", "Câu hai!", "Câu ba?", "Câu bốn…", "Câu năm."]

    def test_sentence_units_preserves_terminal_quotes(self):
        """Closing quotes stay attached to the preceding sentence."""
        text = 'Anh ấy nói: "Được thôi!" Rồi anh ấy bước đi.'
        units = sentence_units(text)
        assert units == ['Anh ấy nói: "Được thôi!"', "Rồi anh ấy bước đi."]

    def test_sentence_units_does_not_split_decimals_or_thousands(self):
        """Numbers with decimal points or thousands dots do not cause sentence splits."""
        text = "Mô hình 3.14 rất chuẩn. Tỷ lệ tăng 50.000 lần trong năm 2026."
        units = sentence_units(text)
        assert len(units) == 2
        assert units[0] == "Mô hình 3.14 rất chuẩn."
        assert units[1] == "Tỷ lệ tăng 50.000 lần trong năm 2026."

    def test_sentence_units_strips_pause_tags(self):
        """Explicit [pause:...] tags are cleanly converted to whitespace."""
        text = "Câu thứ nhất. [pause:800ms] Câu thứ hai."
        units = sentence_units(text)
        assert units == ["Câu thứ nhất.", "Câu thứ hai."]


# ---------------------------------------------------------------------------
# Functional Group 3: DP Phrase Chunking (phrase_chunks)
# ---------------------------------------------------------------------------


class TestDPPhraseChunking:
    """Verifies dynamic programming phrase chunking, orphan avoidance, and aspect ratio limits."""

    def test_aspect_ratio_limits_enforced(self):
        """Vertical 9:16 enforces max 54 chars; landscape 16:9 enforces max 84 chars."""
        long_sentence = (
            "Phương pháp luận tiếp cận từ nguyên lý đầu tiên giúp chúng ta "
            "phân tích bản chất của nhận thức mà không dựa dẫm vào các tiền giả định có sẵn."
        )
        chunks_9x16 = phrase_chunks(long_sentence, aspect_ratio="9:16")
        for c in chunks_9x16:
            assert len(c) <= 54, f"Chunk exceeded 54 chars in 9:16: '{c}' ({len(c)})"

        chunks_16x9 = phrase_chunks(long_sentence, aspect_ratio="16:9")
        for c in chunks_16x9:
            assert len(c) <= 84, f"Chunk exceeded 84 chars in 16:9: '{c}' ({len(c)})"

    def test_reassembly_integrity(self):
        """Rejoining phrase chunks preserves all original words."""
        text = "Tư duy nhận thức phản ánh bản chất của phương pháp khoa học."
        chunks = phrase_chunks(text, aspect_ratio="9:16")
        rejoined = " ".join(chunks)
        assert rejoined.split() == text.split()

    def test_no_orphan_punctuation(self):
        """Closing punctuation is never stranded as an isolated chunk."""
        text = 'Chúng ta khám phá câu hỏi: "Bản chất là gì?"'
        chunks = phrase_chunks(text, aspect_ratio="9:16")
        for c in chunks:
            assert any(ch.isalnum() for ch in c), f"Found orphan punctuation chunk: '{c}'"

    def test_weak_ending_avoidance(self):
        """DP penalizes breaking on weak words like 'và', 'là', 'của', 'với'."""
        text = "Chúng ta tìm kiếm câu trả lời và giải pháp thực tế."
        chunks = phrase_chunks(text, max_len=30)
        # Verify that chunk 1 does not end on 'và'
        for c in chunks[:-1]:
            last_word = c.split()[-1].strip(".,!?;:").lower()
            assert last_word != "và", f"Chunk ends on weak word 'và': '{c}'"

    def test_never_split_across_sentence_boundaries(self):
        """Two distinct sentences are never merged into a single chunk."""
        text = "Câu một ngắn. Câu hai cũng rất ngắn."
        chunks = phrase_chunks(text, aspect_ratio="16:9")
        # Even though combined length is under 84 chars, they must be partitioned separately
        assert any(c.strip() == "Câu một ngắn." for c in chunks)


# ---------------------------------------------------------------------------
# Functional Group 4: Phrase Two-Line Wrapping (wrap_phrase)
# ---------------------------------------------------------------------------


class TestWrapPhrase:
    """Verifies two-line wrapping, line balance, and weak word penalties."""

    def test_short_phrase_not_wrapped(self):
        """Phrases shorter than max_line remain a single line without newline."""
        short_phrase = "Tư duy phản biện"
        assert wrap_phrase(short_phrase, aspect_ratio="9:16") == short_phrase

    def test_long_phrase_wrapped_into_at_most_two_balanced_lines(self):
        """Long phrases are wrapped with newline into balanced lines under max_line."""
        phrase = "Phương pháp tiếp cận dựa trên nguyên lý đầu tiên"
        wrapped = wrap_phrase(phrase, aspect_ratio="9:16")
        lines = wrapped.splitlines()
        assert len(lines) == 2
        for line in lines:
            assert len(line) <= 28, f"Line '{line}' exceeds 9:16 max line limit 28"

    def test_wrap_phrase_avoids_weak_ending_on_first_line(self):
        """Line 1 avoids ending on weak words ('của', 'và', 'là') when alternative exists."""
        phrase = "Khám phá bản chất của hiện tượng tự nhiên"
        wrapped = wrap_phrase(phrase, max_len=25)
        lines = wrapped.splitlines()
        if len(lines) == 2:
            last_w1 = lines[0].split()[-1].strip(".,!?;:").lower()
            assert last_w1 != "của", f"Line 1 ends on weak word 'của': '{lines[0]}'"


# ---------------------------------------------------------------------------
# Functional Group 5: Anchor Timestamp Resolution (resolve_anchor_timestamp)
# ---------------------------------------------------------------------------


class TestAnchorTimestampResolution:
    """Verifies resolving spoken anchor timestamps from word_timestamps or character interpolation."""

    def test_resolve_anchor_timestamp_with_acoustic_word_timestamps(self):
        """Matches anchor quote against word_timestamps to resolve exact start time."""
        segment = {
            "start": 10.0,
            "content_end": 14.0,
            "end": 14.5,
            "text": "Đây là bản chất của tư duy nhận thức sâu sắc.",
            "word_timestamps": [
                {"word": "Đây", "start": 0.0, "end": 0.3},
                {"word": "là", "start": 0.3, "end": 0.5},
                {"word": "bản", "start": 0.5, "end": 0.8},
                {"word": "chất", "start": 0.8, "end": 1.2},
                {"word": "của", "start": 1.2, "end": 1.4},
                {"word": "tư", "start": 1.4, "end": 1.7},
                {"word": "duy", "start": 1.7, "end": 2.0},
                {"word": "nhận", "start": 2.0, "end": 2.4},
                {"word": "thức", "start": 2.4, "end": 2.8},
                {"word": "sâu", "start": 2.8, "end": 3.2},
                {"word": "sắc.", "start": 3.2, "end": 3.6},
            ],
        }
        # "nhận thức" starts at relative 2.0s -> segment start 10.0 + 2.0 = 12.0s
        ts = resolve_anchor_timestamp(segment, "nhận thức")
        assert ts == 12.0

    def test_resolve_anchor_timestamp_case_and_punctuation_insensitive(self):
        """Matches anchor quote regardless of uppercase or stripped terminal punctuation."""
        segment = {
            "start": 5.0,
            "content_end": 8.0,
            "end": 8.5,
            "text": "Khám phá khoa học.",
            "word_timestamps": [
                {"word": "Khám", "start": 0.0, "end": 0.4},
                {"word": "phá", "start": 0.4, "end": 0.8},
                {"word": "khoa", "start": 0.8, "end": 1.2},
                {"word": "học.", "start": 1.2, "end": 1.7},
            ],
        }
        ts = resolve_anchor_timestamp(segment, "KHOA HỌC")
        assert ts == round(5.0 + 0.8, 3)

    def test_resolve_anchor_timestamp_occurrence_indexing(self):
        """Supports matching the 2nd occurrence of repeated anchor words."""
        segment = {
            "start": 0.0,
            "content_end": 5.0,
            "end": 5.0,
            "text": "học và học nữa",
            "word_timestamps": [
                {"word": "học", "start": 0.2, "end": 0.6},
                {"word": "và", "start": 0.6, "end": 0.9},
                {"word": "học", "start": 1.2, "end": 1.6},
                {"word": "nữa", "start": 1.6, "end": 2.0},
            ],
        }
        ts1 = resolve_anchor_timestamp(segment, "học", occurrence=1)
        ts2 = resolve_anchor_timestamp(segment, "học", occurrence=2)
        assert ts1 == 0.2
        assert ts2 == 1.2

    def test_resolve_anchor_fallback_to_character_interpolation(self):
        """When word_timestamps is absent, falls back to proportional character interpolation."""
        segment = {
            "start": 10.0,
            "content_end": 20.0,
            "end": 21.0,
            "text": "ABCDEF GHIJKL",
        }
        # "GHIJKL" starts at character index 7 out of 13
        ts = resolve_anchor_timestamp(segment, "GHIJKL")
        expected = round(10.0 + (20.0 - 10.0) * (7 / 13), 3)
        assert ts == expected

    def test_resolve_anchor_not_found_returns_segment_start(self):
        """If anchor quote is not found in segment, returns segment['start']."""
        segment = {"start": 4.5, "content_end": 7.0, "end": 7.5, "text": "Lời thoại khác."}
        assert resolve_anchor_timestamp(segment, "không tồn tại") == 4.5


# ---------------------------------------------------------------------------
# Functional Group 6: Subtitle Cue Construction & Audit (subtitle_cues & audit_cues)
# ---------------------------------------------------------------------------


class TestSubtitleCuesAndAudit:
    """Verifies subtitle cue assembly, tail pause holding, and audit validation gates."""

    def test_full_cue_assembly_with_acoustic_word_timestamps(self):
        """Cues assembled from acoustic word timestamps have valid intervals and hold until end."""
        segments = [
            {
                "scene_id": "SC01",
                "start": 0.0,
                "content_end": 3.0,
                "end": 3.5,  # 0.5s tail pause
                "text": "Tư duy phản biện là năng lực phân tích vấn đề.",
                "word_timestamps": [
                    {"word": "Tư", "start": 0.0, "end": 0.3},
                    {"word": "duy", "start": 0.3, "end": 0.6},
                    {"word": "phản", "start": 0.6, "end": 0.9},
                    {"word": "biện", "start": 0.9, "end": 1.2},
                    {"word": "là", "start": 1.2, "end": 1.5},
                    {"word": "năng", "start": 1.5, "end": 1.8},
                    {"word": "lực", "start": 1.8, "end": 2.1},
                    {"word": "phân", "start": 2.1, "end": 2.4},
                    {"word": "tích", "start": 2.4, "end": 2.7},
                    {"word": "vấn", "start": 2.7, "end": 2.9},
                    {"word": "đề.", "start": 2.9, "end": 3.0},
                ],
            }
        ]
        cues = subtitle_cues(segments, aspect_ratio="9:16")
        assert len(cues) > 0
        assert cues[0]["start"] == 0.0
        # The last cue holds through the added silence to end (3.5s)
        assert cues[-1]["end"] == 3.5
        for c in cues:
            assert c["start"] < c["end"]
            assert c["scene_id"] == "SC01"

    def test_cue_assembly_fallback_without_word_timestamps(self):
        """Assembles valid cues using proportional character weights when word_timestamps absent."""
        segments = [
            {
                "scene_id": "SC02",
                "start": 5.0,
                "content_end": 8.0,
                "end": 8.5,
                "text": "Một phân đoạn ngắn.",
            }
        ]
        cues = subtitle_cues(segments, aspect_ratio="9:16")
        assert len(cues) > 0
        assert cues[0]["start"] == 5.0
        assert cues[-1]["end"] == 8.5

    def test_invalid_segment_intervals_raise_value_error(self):
        """Invalid time intervals (start >= end or start < 0) raise ValueError."""
        with pytest.raises(ValueError, match="Invalid caption segment interval"):
            subtitle_cues([{"start": 5.0, "end": 4.0, "text": "Lỗi"}])

        with pytest.raises(ValueError, match="Invalid caption segment interval"):
            subtitle_cues([{"start": -1.0, "end": 2.0, "text": "Lỗi"}])

    def test_audit_clean_cues_passes(self):
        """Valid non-overlapping cues produce 0 errors."""
        cues = [
            {"text": "Câu thứ nhất rất rõ ràng.", "start": 0.0, "end": 1.5, "scene_id": "SC01"},
            {"text": "Câu thứ hai tiếp nối.", "start": 1.6, "end": 3.0, "scene_id": "SC01"},
        ]
        report = audit_cues(cues, aspect_ratio="9:16")
        assert report["errors"] == []

    def test_audit_detects_timeline_errors(self):
        """Overlapping timecode or inverted interval produces CAPTION_TIMELINE error."""
        cues = [
            {"text": "Thẻ một", "start": 0.0, "end": 2.0, "scene_id": "SC01"},
            {"text": "Thẻ hai bị đè", "start": 1.5, "end": 3.0, "scene_id": "SC01"},  # start < last - 0.001
        ]
        report = audit_cues(cues, aspect_ratio="9:16")
        codes = [e["code"] for e in report["errors"]]
        assert "CAPTION_TIMELINE" in codes

    def test_audit_detects_orphan_punctuation(self):
        """Cue containing zero alphanumeric characters produces CAPTION_ORPHAN error."""
        cues = [
            {"text": "...", "start": 0.0, "end": 1.0, "scene_id": "SC01"},
        ]
        report = audit_cues(cues, aspect_ratio="9:16")
        codes = [e["code"] for e in report["errors"]]
        assert "CAPTION_ORPHAN" in codes

    def test_audit_detects_cross_sentence_cues(self):
        """Cue spanning multiple sentences produces CAPTION_CROSS_SENTENCE error."""
        cues = [
            {"text": "Câu một. Câu hai.", "start": 0.0, "end": 2.0, "scene_id": "SC01"},
        ]
        report = audit_cues(cues, aspect_ratio="9:16")
        codes = [e["code"] for e in report["errors"]]
        assert "CAPTION_CROSS_SENTENCE" in codes

    def test_audit_warnings_reading_rate_and_short_hold(self):
        """Cues with high character rate (>20cps) or short hold (<0.7s) emit warnings."""
        cues = [
            # High reading rate: 30 chars in 0.5s = 60 cps (> 20) AND short hold 0.5s (< 0.7s)
            {"text": "Đây là câu có mật độ ký tự rất cao.", "start": 0.0, "end": 0.5, "scene_id": "SC01"},
        ]
        report = audit_cues(cues, aspect_ratio="9:16")
        warn_codes = [w["code"] for w in report["warnings"]]
        assert "CAPTION_READING_RATE" in warn_codes
        assert "CAPTION_SHORT_HOLD" in warn_codes

    def test_subtitle_cues_and_audit_zero_caption_timeline_errors_on_rapid_speech(self):
        """Verifies that subtitle_cues() + audit_cues() produces 0 CAPTION_TIMELINE errors on rapid speech and multi-word sentences."""
        text = "Đây là một câu rất dài có tốc độ phát âm cực kỳ nhanh nhằm kiểm tra tính tương thích của phụ đề và kiểm toán mốc thời gian."
        dur_sec = 2.5  # ~5.6 words/sec rapid rate
        n_samples = round(dur_sec * SR)
        t = np.arange(n_samples) / SR
        w = (0.25 * np.sin(2 * np.pi * 220.0 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 4.0 * t))).astype(np.float32)

        word_ts = _extract_word_timestamps_acoustic(w, text, sr=SR)
        assert len(word_ts) == len(text.split())

        # Verify word timestamps non-overlapping
        for i in range(len(word_ts) - 1):
            assert word_ts[i]["end"] <= word_ts[i + 1]["start"], (
                f"Word timestamp overlap: {word_ts[i]} vs {word_ts[i+1]}"
            )

        segment = {
            "scene_id": "SC01",
            "start": 0.0,
            "content_end": dur_sec,
            "end": dur_sec + 0.3,
            "text": text,
            "word_timestamps": word_ts,
        }

        for aspect in ["9:16", "16:9"]:
            cues = subtitle_cues([segment], aspect_ratio=aspect)
            assert len(cues) > 1, f"Expected multi-chunk cues for aspect {aspect}"
            for c in cues:
                assert c["start"] < c["end"]
            for i in range(len(cues) - 1):
                assert cues[i]["end"] <= cues[i + 1]["start"] + 0.001, (
                    f"Cue overlap in aspect {aspect}: {cues[i]} vs {cues[i+1]}"
                )

            report = audit_cues(cues, aspect_ratio=aspect)
            timeline_errors = [e for e in report["errors"] if e["code"] == "CAPTION_TIMELINE"]
            assert timeline_errors == [], f"CAPTION_TIMELINE errors found in aspect {aspect}: {timeline_errors}"
            assert report["errors"] == [], f"Unexpected caption audit errors in aspect {aspect}: {report['errors']}"

    def test_subtitle_cues_defensive_monotonic_clamping(self):
        """Even if upstream word timestamps contain overlapping intervals, subtitle cues remain strictly non-overlapping."""
        dur = 0.5
        words = " ".join([f"từ_{i}" for i in range(25)])
        w = np.zeros(int(SR * dur), dtype=np.float32)
        w[len(w) // 4 : len(w) // 2] = 0.8
        # Simulate intentionally overlapping word timestamps
        word_ts = [
            {"word": f"từ_{i}", "start": round(i * 0.018, 3), "end": round(i * 0.018 + 0.025, 3)}
            for i in range(25)
        ]
        seg = {
            "scene_id": "SC01",
            "start": 0.0,
            "content_end": dur,
            "end": dur,
            "text": words,
            "word_timestamps": word_ts,
        }
        cues = subtitle_cues([seg], aspect_ratio="9:16")
        assert len(cues) > 1
        for i in range(len(cues) - 1):
            assert cues[i]["end"] <= cues[i + 1]["start"], f"Cue overlap: {cues[i]} vs {cues[i+1]}"
        report = audit_cues(cues, aspect_ratio="9:16")
        assert report["errors"] == []
