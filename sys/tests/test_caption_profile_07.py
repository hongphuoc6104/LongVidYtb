"""Regression coverage for centered, compact portrait captions."""
import json
import subprocess
from pathlib import Path


def test_profile_07_preserves_words_and_uses_measured_group_boundaries() -> None:
    script = """
import {portraitCaptionTokens, captionStyle, PORTRAIT_CAPTION_ACTIVE_COLOR} from './renderer/captions.mjs';
const text = 'Bạn đọc rất nhiều nhưng vẫn chưa hiểu bản chất vấn đề.';
const words = text.split(' ').map((word, i) => ({word, start:i, end:i+0.8}));
const cue = {text, start:0, end:words.length};
const groups = words.map(w => portraitCaptionTokens(cue, words, w.start+0.1));
console.log(JSON.stringify({groups, fallback:portraitCaptionTokens(cue, [], 3),
  empty:portraitCaptionTokens({text:' ',start:0,end:1}, [], 0),
  mismatch:portraitCaptionTokens(cue, [{word:'wrong',start:0,end:1}], 0),
  before:portraitCaptionTokens(cue, words, -0.1),
  styles:[captionStyle(1080,1920), captionStyle(540,960)],
  color:PORTRAIT_CAPTION_ACTIVE_COLOR}));
"""
    data = json.loads(subprocess.check_output(
        ['node', '--input-type=module', '-e', script],
        cwd=Path(__file__).resolve().parents[1], text=True))
    original = 'Bạn đọc rất nhiều nhưng vẫn chưa hiểu bản chất vấn đề.'.split()
    unique_groups = []
    for index, group in enumerate(data['groups']):
        words = [token['text'] for token in group]
        assert len(words) <= 6
        assert len(' '.join(words)) <= 28
        assert [token['text'] for token in group if token['active']] == [original[index]]
        if not unique_groups or unique_groups[-1] != words:
            unique_groups.append(words)
    assert [word for group in unique_groups for word in group] == original
    assert [token['text'] for token in data['fallback']] == original
    assert [token['text'] for token in data['mismatch']] == original
    assert not any(token['active'] for token in data['before'])
    assert data['color'] == '#FBBF24'
    assert data['empty'] == []
    for style in data['styles']:
        assert style['left'] == '50%'
        assert style['transform'] == 'translateX(-50%)'
        assert style['background'] == 'transparent'
        assert style['border'] == 'none'
        assert style['boxShadow'] == 'none'
        assert style['padding'] == '0px'


def test_output_plan_preserves_alignment_for_profile_07() -> None:
    script = """
import {outputPlans} from './renderer/outputs.mjs';
import {portraitCaptionTokens, PORTRAIT_CAPTION_ACTIVE_COLOR} from './renderer/captions.mjs';
const cue = {text:'Bạn đã thực sự hiểu?',start:0,end:3};
const words = cue.text.split(' ').map((word,i)=>({word,start:i*0.5,end:(i+1)*0.5}));
const props = {aspect_ratio:'9:16', outputs:[{aspect_ratio:'9:16',language:'vi',subtitles:true}],
  tracks:{vi:{audioSrc:'vi.wav',duration:3,cues:[cue],words,
    scenesByAspect:{'9:16':[{id:'SC01',start:0,end:3}]}}}};
const output = outputPlans(props, false)[0].props;
console.log(JSON.stringify({output, tokens:portraitCaptionTokens(output.cues[0],output.words,2.1),
  color:PORTRAIT_CAPTION_ACTIVE_COLOR}));
"""
    data = json.loads(subprocess.check_output(
        ['node', '--input-type=module', '-e', script],
        cwd=Path(__file__).resolve().parents[1], text=True))
    assert data['output']['hideSubtitles'] is False
    assert (data['output']['width'], data['output']['height']) == (1080, 1920)
    assert [token['text'] for token in data['tokens'] if token['active']] == ['hiểu?']
    assert data['color'] == '#FBBF24'
