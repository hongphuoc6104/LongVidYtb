#!/usr/bin/env python3
"""Adversarial stress-test suite for sys/tools/vn_text_normalizer.py.
Authored by Challenger M1-1 to empirically verify edge cases, fuzzy formats,
nested slashes, complex punctuation, pause tags, and gatekeeper integrity.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from vn_text_normalizer import (
    FOREIGN_NAMES_MAP,
    detect_unnormalized_tokens,
    enforce_tts_normalization_gate,
    normalize_for_tts,
    num_to_vn_words,
    split_utterances_by_pause,
)


class TestAdversarialMandatedCases:
    """Tests specifically requested by Dispatch M1-1."""

    def test_comma_thousands_mixed_with_comma_decimals(self):
        """Sentence mixing comma thousands and comma percentage decimals."""
        text = "Có 50,000 người nhưng chỉ 2,4% đồng ý."
        norm = normalize_for_tts(text)
        assert norm == "Có năm mươi nghìn người nhưng chỉ hai phẩy bốn phần trăm đồng ý."
        gate = enforce_tts_normalization_gate(text)
        assert gate == norm

    def test_comma_thousands_mixed_with_standalone_comma_decimal(self):
        """Sentence mixing comma thousands and comma decimal quantity."""
        text = "Có 50,000 người nhưng chỉ 2,4 tấn gạo."
        norm = normalize_for_tts(text)
        assert norm == "Có năm mươi nghìn người nhưng chỉ hai phẩy bốn tấn gạo."
        gate = enforce_tts_normalization_gate(text)
        assert gate == norm

    def test_dot_decimals_mixed_with_dot_thousands(self):
        """Sentence mixing dot decimal and dot thousands."""
        text = "Nặng 2.4 kg và giá 50.000 đồng."
        norm = normalize_for_tts(text)
        assert norm == "Nặng hai phẩy bốn kg và giá năm mươi nghìn đồng."
        gate = enforce_tts_normalization_gate(text)
        assert gate == norm

    def test_complex_slashes_spaced_metric(self):
        """Complex slashes when metric unit is spaced."""
        text = "Tốc độ 100 km/h, làm việc 24/7 trong 17 giờ/tuần."
        norm = normalize_for_tts(text)
        assert norm == "Tốc độ một trăm ki-lô-mét trên giờ, làm việc hai mươi tư trên bảy trong mười bảy giờ trên tuần."
        gate = enforce_tts_normalization_gate(text)
        assert gate == norm

    def test_explicit_pauses_inside_complex_sentence_with_foreign_names(self):
        """Sentence with foreign proper noun, ellipsis, pause tag, em-dash, colon, and thousands."""
        text = "Richard Feynman nói... [pause:800ms] — điều này rất quan trọng: 50.000 người đã nghe."
        # When preserve_pauses=True
        norm_pres = normalize_for_tts(text, preserve_pauses=True)
        assert norm_pres == "Ri-chát Phây-man nói [pause:800ms] điều này rất quan trọng, năm mươi nghìn người đã nghe."
        gate_pres = enforce_tts_normalization_gate(text, preserve_pauses=True)
        assert gate_pres == norm_pres

        # When preserve_pauses=False
        norm_no_pres = normalize_for_tts(text, preserve_pauses=False)
        assert norm_no_pres == "Ri-chát Phây-man nói, điều này rất quan trọng, năm mươi nghìn người đã nghe."
        gate_no_pres = enforce_tts_normalization_gate(text, preserve_pauses=False)
        assert gate_no_pres == norm_no_pres


class TestAdversarialFailingCases:
    """Adversarial stress-tests exposing edge-case defects and gatekeeper issues."""

    def test_unspaced_metric_unit_retains_raw_digits_and_bypasses_gate(self):
        """Fix 2: Unspaced metric unit '100km/h' normalizes cleanly into words."""
        text = "Tốc độ 100km/h, làm việc 24/7 trong 17 giờ/tuần"
        norm = normalize_for_tts(text)
        assert norm == "Tốc độ một trăm ki-lô-mét trên giờ, làm việc hai mươi tư trên bảy trong mười bảy giờ trên tuần"
        gate = enforce_tts_normalization_gate(text)
        assert gate == norm
        # Gate also catches raw leftover unspaced digits
        assert len(detect_unnormalized_tokens("100km trên h")) == 1

    def test_foreign_names_map_self_blocking_analysis(self):
        """Fix 1: Zero entries in FOREIGN_NAMES_MAP trigger detect_unnormalized_tokens."""
        blocking = []
        for pat, rep in FOREIGN_NAMES_MAP.items():
            issues = detect_unnormalized_tokens(f"Thử nghiệm {rep}")
            if issues:
                blocking.append((pat, rep, issues[0]["reason"]))
        assert len(blocking) == 0

    def test_gatekeeper_self_rejection_glucose(self):
        """Fix 1: glucose -> glu-cô-dơ passes gatekeeper cleanly."""
        text = "Nồng độ glucose trong máu tăng lên."
        assert enforce_tts_normalization_gate(text) == "Nồng độ glu-cô-dơ trong máu tăng lên."

    def test_gatekeeper_self_rejection_socrates(self):
        """Fix 1: Socrates -> Xô-crát passes gatekeeper cleanly."""
        text = "Socrates là một triết gia cổ đại."
        assert enforce_tts_normalization_gate(text) == "Xô-crát là một triết gia cổ đại."

    def test_gatekeeper_self_rejection_plato(self):
        """Fix 1: Plato -> Pla-tông passes gatekeeper cleanly."""
        text = "Plato là học trò của Socrates."
        assert enforce_tts_normalization_gate(text) == "Pla-tông là học trò của Xô-crát."

    def test_broken_word_boundary_regex_ju_apostrophe(self):
        """Fix 3: Ju/' transliterates to Giu before whitespace and punctuation."""
        text = "Người Ju/' sống ở sa mạc."
        assert enforce_tts_normalization_gate(text) == "Người Giu sống ở sa mạc."

    def test_billion_scale_numbers_return_digits_and_crash_gate(self):
        """Fix 4: num_to_vn_words supports billions ('tỷ') up to 999,999,999,999."""
        assert num_to_vn_words(1_000_000_000) == "một tỷ"
        text = "Dân số là 1,000,000,000 người."
        assert enforce_tts_normalization_gate(text) == "Dân số là một tỷ người."

    def test_negative_percentage_retains_raw_minus(self):
        """Fix 5: Negative percentage converts minus to 'âm '."""
        text = "Tăng trưởng giảm -5% trong quý này."
        assert enforce_tts_normalization_gate(text) == "Tăng trưởng giảm âm năm phần trăm trong quý này."

    def test_negative_decimal_retains_raw_minus(self):
        """Fix 5: Negative decimal converts minus to 'âm '."""
        text = "Nhiệt độ là -2.4 độ C."
        assert enforce_tts_normalization_gate(text) == "Nhiệt độ là âm hai phẩy bốn độ C."


class TestAdversarialBoundaryRobustness:
    """Stress tests on boundaries and edge conditions."""

    def test_multi_digit_decimals(self):
        assert normalize_for_tts("Số pi là 3.14159.") == "Số pi là ba phẩy mười bốn nghìn một trăm năm mươi chín."
        assert normalize_for_tts("Nồng độ 0.005%") == "Nồng độ không phẩy không không năm phần trăm"
        assert normalize_for_tts("Nồng độ 0.0001") == "Nồng độ không phẩy không không không một"

    def test_zero_decimals(self):
        assert normalize_for_tts("Điểm số 0.0") == "Điểm số không phẩy không"
        assert normalize_for_tts("Điểm số 0,00") == "Điểm số không phẩy không không"

    def test_nested_multiple_slashes(self):
        assert normalize_for_tts("Làm việc 24/7/365") == "Làm việc hai mươi tư trên bảy trên ba trăm sáu mươi lăm"
        assert normalize_for_tts("Chọn A/B/C") == "Chọn A trên B trên C"

    def test_pause_tags_with_adjacent_punctuation(self):
        text = "Trước đó,... [pause:800ms] — sau đó: 100 người."
        norm = normalize_for_tts(text, preserve_pauses=True)
        assert norm == "Trước đó [pause:800ms] sau đó, một trăm người."

    def test_pause_splitting_summation(self):
        text = "Cụm một [pause:500ms][pause:300ms] cụm hai"
        parts = split_utterances_by_pause(text)
        assert len(parts) == 2
        assert parts[0]["text"] == "Cụm một"
        assert parts[0]["pause_after"] == 0.8
        assert parts[1]["text"] == "cụm hai"
