"""Behavioral regression checks for the director upgrade; no external services."""
import copy
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import adapters
from pilot import ROOT, Blocked, read
from content_contract import validate_content, ContractError
from scripts.subtitles import subtitle_cues, audit_cues, has_words
from scripts.director_context import context
from scripts.editorial_audit import audit
from scripts.story_plan import estimates
from tools.vn_text_normalizer import normalize_for_tts
import numpy as np
import soundfile as sf


class CaptionRegressionTests(unittest.TestCase):
    def check_text(self, text, duration=4):
        segments = [dict(text=text, start=0, end=duration, scene_id='SC01')]
        cues = subtitle_cues(segments)
        self.assertEqual(' '.join(' '.join(c['text'] for c in cues).split()), ' '.join(text.split()))
        self.assertTrue(all(has_words(c['text']) for c in cues))
        self.assertEqual(cues[0]['start'], 0)
        self.assertEqual(cues[-1]['end'], duration)
        self.assertTrue(all(a['end'] == b['start'] for a, b in zip(cues, cues[1:])))
        self.assertFalse(audit_cues(cues)['errors'])
        return cues

    def test_real_quoted_example_no_orphan(self):
        for text in ['Chủ nhật ngủ nướng đã đời: "I usually get up late on Sundays."',
                     'Đứa bạn thì chạy bộ từ năm giờ: "He gets up at five to exercise."',
                     '“Don’t get up yet,” she said. “It is 6:30, not 7:00.”',
                     'Đến khi bạn chịu thò chân xuống sàn... khoảnh khắc ấy mới là: get up!']:
            cues = self.check_text(text)
            self.assertFalse(any(c['text'].strip() in ('"', 'Sundays.', 'sàn...') for c in cues))

    def test_two_line_layout_preserves_english_sentence(self):
        cues = self.check_text('I usually get up late on Sundays.')
        self.assertEqual(len(cues), 1)
        self.assertEqual(len(cues[0]['text'].splitlines()), 2)
        self.assertIn('I usually', cues[0]['text'])

    def test_punctuation_in_adjacent_segment_attaches_without_losing_time(self):
        cues = subtitle_cues([dict(text='Say "hello', start=0, end=2, scene_id='SC01'),
                              dict(text='"', start=2, end=2.3, scene_id='SC01')])
        self.assertEqual(len(cues), 1)
        self.assertEqual(cues[0]['end'], 2.3)
        self.assertIn('"', cues[0]['text'])

    def test_never_merge_across_scene_or_silence(self):
        for second in [dict(text='"', start=2, end=3, scene_id='SC02'),
                       dict(text='"', start=2.5, end=3, scene_id='SC01')]:
            cues = subtitle_cues([dict(text='Hello', start=0, end=2, scene_id='SC01'), second])
            self.assertEqual(len(cues), 2)
            self.assertTrue(audit_cues(cues)['errors'])

    def test_invalid_times_rejected_and_fast_reading_reported_not_approved(self):
        for end in [0, -1, math.nan, math.inf]:
            with self.assertRaises(ValueError):
                subtitle_cues([dict(text='Hello', start=0, end=end)])
        report = audit_cues(self.check_text('I usually get up late on Sundays.', .3))
        self.assertTrue(report['warnings'])
        self.assertFalse(report['quality_approval'])

    def test_horizontal_does_not_audit_invisible_vietnamese_cues(self):
        report = audit({'aspect_ratio': '16:9', 'cues': [dict(text='"', start=0, end=1)]})
        self.assertFalse(report['captions_applicable'])
        self.assertFalse(report['errors'])

    def test_added_practice_silence_does_not_delay_earlier_caption_changes(self):
        text = 'This is the first part of a longer model. This is the second part to repeat.'
        base = dict(text=text, start=0, end=4, scene_id='SC01')
        original = subtitle_cues([base])
        extended = subtitle_cues([dict(base, end=7, content_end=4)])
        self.assertGreater(len(original), 1)
        self.assertEqual(original[:-1], extended[:-1])
        self.assertEqual(original[-1]['start'], extended[-1]['start'])
        self.assertEqual(extended[-1]['end'], 7)


class DirectionContractTests(unittest.TestCase):
    def fixture(self):
        b = read(ROOT / 'examples/story-v3/brief.json')
        c = read(ROOT / 'examples/story-v3/content.json')
        c['brief_hash'] = 'TEST'
        return b, c

    def test_optional_practice_hold_valid_and_counted_in_estimate(self):
        b, c = self.fixture()
        before = estimates(b, c)['languages']['vi']['scenes'][0]['seconds']
        c['scenes'][0]['audio_direction'] = {'vi': dict(intent='Invite a response', pronunciation_notes='', learner_pause_seconds=2)}
        validate_content(ROOT, b, 1, 'TEST', c)
        after = estimates(b, c)['languages']['vi']['scenes'][0]['seconds']
        self.assertAlmostEqual(after - before, 2)

    def test_invalid_practice_hold_and_unimplemented_controls_rejected(self):
        for value in [-1, 9, True, '2']:
            b, c = self.fixture()
            c['scenes'][0]['audio_direction'] = {'vi': dict(intent='Repeat', pronunciation_notes='', learner_pause_seconds=value)}
            with self.assertRaises(ContractError):
                validate_content(ROOT, b, 1, 'TEST', c)
            with self.assertRaises(Blocked):
                adapters.scene_tail(c['scenes'][0], 'vi', {}, False)
        b, c = self.fixture()
        c['scenes'][0]['audio_direction'] = {'vi': dict(intent='Repeat', pronunciation_notes='', learner_pause_seconds=1, emotion='happy')}
        with self.assertRaises(ContractError):
            validate_content(ROOT, b, 1, 'TEST', c)

    def test_holds_are_language_specific(self):
        scene = {'audio_direction': {'vi': {'learner_pause_seconds': 2}, 'en': {'learner_pause_seconds': 3}}}
        self.assertEqual(adapters.scene_tail(scene, 'vi', {}, False), 2)
        self.assertEqual(adapters.scene_tail(scene, 'en', {}, True), 3)
        self.assertEqual(adapters.scene_tail({}, 'vi', {}, True), adapters.DEFAULT_PAUSE['tail'])

    def test_vocabulary_references_explicitly_loaded_only_when_relevant(self):
        general = context(ROOT, 'outline', {'topic': 'Sửa xe', 'goal': 'Hiểu cách kiểm tra lốp'})
        vocab = context(ROOT, 'outline', {'topic': 'Học từ vựng get up'})
        reference = (ROOT / '.agents/skills/vp-production/references/vocabulary.md').read_text()
        self.assertIn(reference, vocab)
        self.assertNotIn(reference, general)
        self.assertIn((ROOT / '.agents/skills/vp-production/references/script.md').read_text(), general)
        self.assertNotIn((ROOT / '.agents/skills/vp-production/references/audio.md').read_text(), general)


class SynthesisOnlyTests(unittest.TestCase):
    def test_pronunciation_does_not_mutate_script_or_caption_text(self):
        text = 'I get up at 7. I\'m ready. AI và VIP.'
        normalized = normalize_for_tts(text)
        self.assertIn('bảy', normalized)
        cues = subtitle_cues([dict(text=text, start=0, end=6, scene_id='SC01')])
        self.assertEqual(' '.join(' '.join(c['text'] for c in cues).split()), text)

    def test_colab_protocol_preserves_learner_pause_tail_in_request(self):
        from colab_bridge.protocol import build_request
        cfg = read(ROOT / 'config.json')
        scenes = [{'scene_id': 'SC01', 'narration': 'I get up.', 'texts': ['I get up.'], 'gaps': [], 'tail': 2.0, 'retake': 0}]
        req = build_request(ROOT, cfg, scenes, [])
        self.assertEqual(req['segments'][0]['pause'], 2.0)
        self.assertEqual(req['profiles']['vi']['voice'], 'Adam')


if __name__ == '__main__':
    unittest.main()
