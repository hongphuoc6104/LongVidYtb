"""Regression coverage for acoustic beat timing and short spoken sentences."""
import copy

import pytest
from scripts.story_plan import _word_anchor_time, timeline
from scripts.subtitles import resolve_anchor_timestamp
from tools.script_cadence_checker import ScriptCadenceChecker
from visual_pacing import check_see_say_beat_density


def segment() -> dict:
    return {
        'scene_id': 'SC01', 'text': 'A phone then a phone',
        'start': .5, 'content_end': 4.5, 'end': 5.,
        'word_timestamps': [
            {'word': word, 'start': left, 'end': left + .3}
            for word, left in zip('A phone then a phone'.split(), (0., .4, 1., 1.6, 2.7), strict=True)
        ],
    }


def test_segment_relative_timestamps_never_use_absolute_magnitude() -> None:
    seg = segment()
    assert _word_anchor_time(seg, seg['text'].rfind('phone')) == 3.2
    assert resolve_anchor_timestamp(seg, 'phone', occurrence=2) == 3.2


@pytest.mark.parametrize('bad', [float('nan'), -1., 10.])
def test_invalid_acoustic_boundaries_use_explicit_fallback(bad: float) -> None:
    seg = segment()
    seg['word_timestamps'][1]['start'] = bad
    assert _word_anchor_time(seg, 2) is None


def test_interpolated_repeated_anchor_advances_occurrence() -> None:
    seg = segment()
    del seg['word_timestamps']
    assert resolve_anchor_timestamp(seg, 'phone', occurrence=2) == 3.5


def test_timeline_prefers_acoustic_time_and_labels_fallback() -> None:
    seg = segment()
    beat = {'id': 'B1', 'image_id': 'I1', 'effect': 'cut', 'focus': {'x': .5, 'y': .5},
            'anchor': {'vi': {'quote': 'A phone', 'occurrence': 1}}}
    second = copy.deepcopy(beat)
    second.update(id='B2', image_id='I2', anchor={'vi': {'quote': 'phone', 'occurrence': 2}})
    content = {'schema_version': '3.0', 'scenes': [
        {'id': 'SC01', 'title': 'Phone', 'narration': seg['text'], 'beats': [beat, second]},
    ]}
    images = {'items': [{'image_id': key, 'scene_id': 'SC01', 'ratio': '16:9', 'path': key + '.png'}
                        for key in ('I1', 'I2')]}
    audio = {'tracks': {'vi': {'segments': [seg]}}}
    result = timeline(content, images, audio, 'vi', '16:9')[0]
    assert result['images'][1]['at'] == 2.7
    assert result['timing_method'] == 'acoustic_word_timestamps'
    assert result['images'][0]['transition'] == 'cut'
    assert result['images'][0]['camera_motion'] != 'cut'
    assert result['images'][0]['camera_motion'] != result['images'][1]['camera_motion']
    del seg['word_timestamps']
    fallback = timeline(content, images, audio, 'vi', '16:9')[0]
    assert fallback['images'][1]['at'] != 2.7
    assert fallback['timing_method'] == 'narration_anchor_interpolated'


def test_concrete_short_sentences_do_not_trigger_fragmentation() -> None:
    result = ScriptCadenceChecker(max_sentences=8).check_scenes([
        {'id': 'SC01', 'duration': 5., 'narration': 'Bạn gấp sách. Bạn cầm bút. Bạn viết xuống.'},
    ])
    assert not any('SENTENCE_FRAGMENTATION' in warning
                   for scene in result['scenes'] for warning in scene['warnings'])


def test_missing_visuals_are_reported_when_beats_are_supplied() -> None:
    result = ScriptCadenceChecker().check_scenes([
        {'id': 'SC01', 'duration': 12., 'narration': 'Bạn đặt sách xuống bàn.', 'beats': []},
    ])
    assert any('LOW_VISUAL_BEAT_DENSITY' in warning
               for scene in result['scenes'] for warning in scene['warnings'])


def test_density_uses_absolute_times_across_scene_boundaries() -> None:
    scenes = [
        {'id': 'SC01', 'start': 0., 'end': 6., 'images': [
            {'id': str(index), 'at': at} for index, at in enumerate((0., 1.3, 2.6, 3.9, 5.2))]},
        {'id': 'SC02', 'start': 6., 'end': 13., 'images': [
            {'id': str(index), 'at': at} for index, at in enumerate((0., 1.5, 3., 5.))]},
    ]
    assert check_see_say_beat_density(scenes) == []
    scenes[0]['images'] = scenes[0]['images'][:1]
    assert any('OPENING_VISUAL_DENSITY' in error for error in check_see_say_beat_density(scenes))


def test_white_card_prompt_uses_versioned_full_frame_contract() -> None:
    from flow_prompts import compile

    result = compile('NanoBanana2Lite', 'scene', {
        'description': 'A closed textbook beside a blank sheet.', 'aspect_ratio': '16:9',
        'shot_type': 'white_card', 'caption_clearance': None,
    }, '1.3.0')
    assert 'clean pure white #FFFFFF concept card' in result['prompt']
    assert 'full-bleed environment background that fills the frame' not in result['prompt']
    assert result['version'] == '1.3.0'


def test_acceptance_package_has_valid_anchors_and_meets_estimated_density(tmp_path) -> None:
    from scripts.story_plan import timeline
    from tools.build_full_frame_acceptance import build_topic
    from tools.research_story_architect import write_production_package

    topic = build_topic()
    result = write_production_package(tmp_path, topic)
    assert result['valid_contracts'], result['contract_errors']
    assert result['cadence_report']['status'] == 'PASS'
    assert 300 <= result['cadence_report']['total_duration'] <= 480
    import json
    content = json.loads((tmp_path / 'content.json').read_text())
    segments, items = [], []
    cursor = 0.
    for scene, authored in zip(content['scenes'], topic.scenes, strict=True):
        segments.append({'scene_id': scene['id'], 'text': scene['narration'],
                         'start': cursor, 'end': cursor + authored.duration})
        cursor += authored.duration
        items.extend({'scene_id': scene['id'], 'image_id': image['id'], 'ratio': '16:9', 'path': image['id'] + '.png'}
                     for image in scene['images'])
    measured_shape = timeline(content, {'items': items}, {'tracks': {'vi': {'segments': segments}}}, 'vi', '16:9')
    assert check_see_say_beat_density(measured_shape) == []


def test_ci_requires_actual_successful_runs_for_the_current_revision() -> None:
    from conveyor.ci_evidence import validate_ci_runs

    assert not validate_ci_runs([], 'abc')
    run = {'id': 1, 'head_sha': 'abc', 'status': 'completed', 'conclusion': 'success', 'html_url': 'https://github.com/example/run/1'}
    assert validate_ci_runs([run], 'abc')
    assert not validate_ci_runs([run], 'other')
    assert not validate_ci_runs([{**run, 'status': 'in_progress'}], 'abc')
    assert not validate_ci_runs([{**run, 'conclusion': 'skipped'}], 'abc')
