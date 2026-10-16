"""Omni-platform routing, actual PCM assembly and asset reuse regressions."""
from __future__ import annotations

import copy
import json
import subprocess
import wave
from pathlib import Path

import pytest
from omni_platform import short_plans
from omni_render import prepare_shorts
from scripts import subtitles
from tools.social_pack_generator import social_post_kit

ROOT = Path(__file__).resolve().parents[1]


def fixture() -> tuple[dict, dict]:
    content = {'scenes': [{'id': 'P01', 'narration': 'A complete parent sentence.', 'images': [{'id': 'I01'}]}]}
    body = [{'parent_scene_id': 'P01', 'image_id': 'I01', 'segment_text': 'A complete parent sentence.'} for _ in range(4)]
    brief = {'omni_platform': True, 'reframe_mode': True, 'aspect_ratio': '16:9', 'youtube_title': 'A research paradox',
             'spinoff_shorts': [dict(id=f'S{i}', opening_hook='Knowledge can deceive you.', hook_title='Research paradox', body=copy.deepcopy(body)) for i in range(2)]}
    return brief, content


def test_short_plans_reject_raw_cut_and_missing_assets() -> None:
    brief, content = fixture()
    assert len(short_plans(brief, content)) == 2
    brief['spinoff_shorts'][0]['body'][0]['image_id'] = 'missing'
    with pytest.raises(ValueError, match='REFERENCE'):
        short_plans(brief, content)
    brief, content = fixture()
    brief['spinoff_shorts'][0]['body'].pop()
    with pytest.raises(ValueError, match='four independent'):
        short_plans(brief, content)


def test_short_assembly_rebases_five_scenes_and_pcm(tmp_path: Path) -> None:
    brief, content = fixture()
    public = tmp_path / 'public'
    public.mkdir()
    def wav(name: str, seconds: int) -> None:
        with wave.open(str(tmp_path / name), 'wb') as handle:
            handle.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
            handle.writeframes(b'\0\0' * (48000 * seconds))
    wav('parent.wav', 12)
    wav('hook.wav', 2)
    (public / 'parent.png').write_bytes(b'fixture-only-not-provider-evidence')
    segment = dict(scene_id='P01', text='A complete parent sentence.', start=0., end=12.)
    audio = {'tracks': {'vi': dict(wav='parent.wav', speed=1.26, segments=[segment])},
             'spinoff_hooks': [dict(id=f'S{i}', text='Knowledge can deceive you.', path='hook.wav') for i in range(2)]}
    images = {'items': [dict(image_id='I01', ratio='16:9', path='parent.png')]}
    timeline = [dict(id='P01', start=0, images=[dict(at=t, src='parent.png') for t in (0, 3, 6, 9)])]
    plans = prepare_shorts(brief, content, audio, images, tmp_path, public, subtitles, timeline)
    assert len(plans) == 2
    assert [scene['id'] for scene in plans[0]['props']['scenes']] == ['SC01', 'SC02', 'SC03', 'SC04', 'SC05']
    assert plans[0]['props']['duration'] == 50
    assert plans[0]['props']['scenes'][1]['start'] == 2
    with wave.open(str(public / plans[0]['props']['audioSrc'])) as handle:
        assert handle.getnframes() == 50 * 48000
    audio['tracks']['vi']['segments'][0]['text'] = 'Different.'
    with pytest.raises(ValueError, match='OMNI_SEGMENT'):
        prepare_shorts(brief, content, audio, images, tmp_path, public, subtitles, timeline)


def test_karaoke_repeat_words_and_safe_zone() -> None:
    script = """
      import {karaokeTokens, captionStyle} from './renderer/captions.mjs';
      const tokens = karaokeTokens({text:'học học',start:0,end:2}, [{word:'học',start:0,end:1},{word:'học',start:1,end:2}],1.2);
      console.log(JSON.stringify({tokens, style:captionStyle(1080,1920)}));
    """
    output = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', script], cwd=ROOT, text=True))
    assert [token['active'] for token in output['tokens']] == [False, True]
    assert output['style']['bottom'] == 400
    assert output['style']['left'] + output['style']['width'] <= 900


def test_social_kit_uses_measured_starts_and_sources() -> None:
    brief, _ = fixture()
    brief['sources'] = [dict(title='Actual paper', reference='doi:example')]
    text = social_post_kit(brief, [dict(id='CH01', title='Opening', start=0), dict(id='CH02', title='Evidence', start=79.9)], [dict(file='video_youtube_16x9.mp4')])
    assert '01:19 Evidence' in text
    assert 'Actual paper: doi:example' in text
    assert 'video_youtube_16x9.mp4' in text


def test_body_span_preserves_sentence_boundaries_and_word_offsets() -> None:
    from omni_render import parent_span
    pieces = [dict(scene_id='P', text='First sentence.', start=10, end=14,
                   word_timestamps=[dict(word='First', start=0, end=1)]),
              dict(scene_id='P', text='Second sentence.', start=14, end=18,
                   word_timestamps=[dict(word='Second', start=0, end=1)])]
    span = parent_span(pieces, 'P', 'First sentence. Second sentence.')
    assert (span['start'], span['end']) == (10, 18)
    assert span['word_timestamps'][1]['start'] == 4
    with pytest.raises(ValueError, match='OMNI_SEGMENT'):
        parent_span(pieces, 'P', 'sentence. Second')


def test_single_pass_reframe_preserves_legacy_dual_generation() -> None:
    from types import SimpleNamespace

    from image_pipeline import planned_units
    content = {'schema_version': '3.0', 'style': 'Full-frame illustration', 'characters': [],
               'scenes': [dict(id='P', images=[dict(id='I', character_ids=[], description='A laboratory', preserve='', change='', based_on=None, visible_text=[])])]}
    brief = dict(aspect_ratio='dual', reframe_mode=True, planning={'text_style': {}})
    pilot = SimpleNamespace(payload=lambda job, module: content, brief=lambda job: (brief,))
    units = planned_units(pilot, 'test')
    assert [unit['ratio'] for unit in units] == ['16:9']
    assert units[0]['image_id'] == 'I'
    brief['reframe_mode'] = False
    assert [unit['ratio'] for unit in planned_units(pilot, 'test')] == ['9:16', '16:9']


def test_renderer_plans_share_master_and_keep_caption_variants() -> None:
    script = """
      import {outputPlans} from './renderer/outputs.mjs';
      const props = {aspect_ratio:'16:9',omni_platform:true,outputs:[{aspect_ratio:'16:9',language:'vi',subtitles:false}], tracks:{vi:{audioSrc:'vi.wav',duration:50,cues:[],scenesByAspect:{'16:9':[{id:'P'}]}}},short_deliveries:[{file:'video_tiktok_short_01_9x16.mp4',props:{width:1080,height:1920}}]};
      console.log(JSON.stringify(outputPlans(props,false)));
    """
    plans = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', script], cwd=ROOT, text=True))
    assert plans[1]['file'] == 'video_youtube_16x9.mp4'
    assert plans[1]['props']['hideSubtitles'] is True
    assert plans[2]['props']['hideSubtitles'] is False
    assert plans[1]['props']['scenes'] == plans[2]['props']['scenes']
    assert plans[3]['props']['width'] == 1080
