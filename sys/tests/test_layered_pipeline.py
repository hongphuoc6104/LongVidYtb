"""Full-frame beat contracts replacing the former cut-out sticker workflow."""
import copy
import re
import tempfile
import unittest
from pathlib import Path

import colab_bridge.job_protocol as job_protocol
from content_contract import ContractError, validate_brief, validate_content
from flow_prompts import PromptError
from flow_prompts import compile as compile_prompt
from scripts.story_plan import image_units, languages, timeline

from pilot import ROOT, read


def fixture():
    brief = read(ROOT / 'examples/story-v3/brief.json')
    content = read(ROOT / 'examples/story-v3/content.json')
    content['brief_hash'] = 'TEST'
    return brief, content


def quote_at(text, fraction):
    words = list(re.finditer(r'\S+', text))
    start = min(len(words) - 1, int((len(words) - 1) * fraction))
    for index in range(start, max(start - 8, -1), -1):
        left = words[index].start()
        right = words[min(index + 3, len(words) - 1)].end()
        quote = text[left:right]
        if text.find(quote) == left:
            return {'quote': quote, 'occurrence': 1}
    raise AssertionError('could not find a unique narration anchor')


def make_variation(brief, content):
    scene = content['scenes'][0]
    base = copy.deepcopy(scene['images'][0])
    base.update({'id': 'SC01_BASE', 'kind': 'scene', 'based_on': None, 'preserve': '', 'change': 'Establish the scene.'})
    variation = copy.deepcopy(base)
    variation.update({
        'id': 'SC01_VARIANT',
        'description': 'The same room and camera, with the character reaching for a phone.',
        'based_on': 'SC01_BASE',
        'preserve': 'Keep the same room, bed, clock, and camera position.',
        'change': 'Show the character raising a phone.',
    })
    scene['images'] = [base, variation]
    scene['beats'] = [
        {'id': 'SC01_B1', 'image_id': 'SC01_BASE', 'purpose': scene['purpose'],
         'anchor': {lang: quote_at(scene.get('narration_en' if lang == 'en' else 'narration', ''), 0.0) for lang in languages(brief)},
         'effect': 'hold', 'focus': {'x': 0.5, 'y': 0.5}},
        {'id': 'SC01_B2', 'image_id': 'SC01_VARIANT', 'purpose': scene['purpose'],
         'anchor': {lang: quote_at(scene.get('narration_en' if lang == 'en' else 'narration', ''), 0.65) for lang in languages(brief)},
         'effect': 'cut', 'focus': {'x': 0.5, 'y': 0.5}},
    ]
    scene['layers'] = []
    return content


class FullFramePromptTests(unittest.TestCase):
    data = {'description': 'A complete kitchen scene with a person at the open refrigerator.', 'aspect_ratio': '9:16'}

    def test_full_frame_scene_and_variation_prompts_compile(self):
        scene = compile_prompt('NanoBanana2Lite', 'scene', dict(self.data), '1.2.0')
        variation = compile_prompt(
            'NanoBanana2Lite', 'variation',
            dict(self.data, preserve=['Keep the room and camera.'], change=['Raise the phone.'], base_reference={'media_id': 'de94a39b-155f-4afe-acbb-d9d4b59ad532', 'sha256': 'a' * 64}),
            '1.2.0',
        )
        self.assertEqual(scene['purpose'], 'scene')
        self.assertEqual(variation['purpose'], 'variation')

    def test_cutout_prompt_purposes_are_disabled(self):
        for purpose in ('layer_background', 'layer_sticker'):
            with self.subTest(purpose=purpose), self.assertRaisesRegex(PromptError, 'FLOW_LAYERING_DISABLED'):
                compile_prompt('NanoBanana2Lite', purpose, dict(self.data), '1.2.0')

    def test_legacy_scene_prompt_versions_remain_stable(self):
        before = compile_prompt('NanoBanana2', 'scene', dict(self.data), '1.1.0')
        again = compile_prompt('NanoBanana2', 'scene', dict(self.data), '1.1.0')
        self.assertEqual(before['sha256'], again['sha256'])


class FullFramePlanTests(unittest.TestCase):
    def check(self, brief, content):
        validate_brief(ROOT, brief)
        validate_content(ROOT, brief, 1, 'TEST', content)

    def test_standard_example_uses_full_frame_images_only(self):
        brief, content = fixture()
        self.check(brief, content)
        units = image_units(content)
        self.assertTrue(all(unit['kind'] == 'scene' for unit in units))
        for scene in content['scenes']:
            self.assertEqual(scene.get('layers', []), [])
            self.assertEqual({image['id'] for image in scene['images']}, {beat['image_id'] for beat in scene['beats']})

    def test_based_on_variation_is_valid_and_stays_a_scene_beat(self):
        brief, content = fixture()
        make_variation(brief, content)
        self.check(brief, content)
        first = content['scenes'][0]
        self.assertEqual(first['images'][1]['based_on'], 'SC01_BASE')
        self.assertTrue(first['images'][1]['preserve'])
        self.assertTrue(first['images'][1]['change'])
        self.assertEqual(first['layers'], [])

    def test_layered_content_is_rejected(self):
        brief, content = fixture()
        content['scenes'][0]['images'][0]['kind'] = 'background'
        with self.assertRaisesRegex(ContractError, 'LAYERING_DISABLED'):
            self.check(brief, content)

    def test_nonempty_layers_are_rejected(self):
        brief, content = fixture()
        scene = content['scenes'][0]
        scene['layers'] = [{
            'id': 'old-layer',
            'image_id': scene['images'][0]['id'],
            'anchor': copy.deepcopy(scene['beats'][0]['anchor']),
            'fx': 'pop',
            'x': 0.35,
            'y': 0.6,
            'w': 0.35,
        }]
        with self.assertRaisesRegex(ContractError, 'LAYERING_DISABLED'):
            self.check(brief, content)

    def test_timeline_preserves_multiple_full_frame_beats(self):
        brief, content = fixture()
        make_variation(brief, content)
        lang = languages(brief)[0]
        items = []
        segments = []
        at = 0.0
        for scene in content['scenes']:
            text = scene.get('narration_en' if lang == 'en' else 'narration', '')
            segments.append({'scene_id': scene['id'], 'start': at, 'end': at + 10.0, 'text': text})
            at += 10.0
            for image in scene['images']:
                items.append({'scene_id': scene['id'], 'image_id': image['id'], 'ratio': '9:16', 'path': f"assets/{image['id']}.jpg"})
        audio = {'tracks': {lang: {'segments': segments, 'duration': at}}}
        scenes = timeline(content, {'items': items}, audio, lang, '9:16')
        self.assertEqual([beat['id'] for beat in scenes[0]['images']], ['SC01_B1', 'SC01_B2'])
        self.assertLess(scenes[0]['images'][0]['at'], scenes[0]['images'][1]['at'])
        self.assertNotIn('layers', scenes[0])


class FullFrameRenderProtocolTests(unittest.TestCase):
    def test_layered_content_is_blocked_before_remote_bundle_creation(self):
        _, content = fixture()
        content['scenes'][0]['layers'] = [{'id': 'old-layer'}]
        with self.assertRaisesRegex(ValueError, 'LAYERING_DISABLED'):
            job_protocol.build_render_request(ROOT, {}, content, {}, {}, lambda _: '')

    def test_remote_bundle_does_not_include_matte_tool(self):
        _, content = fixture()
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_file = Path(temp_dir) / 'audio.wav'
            audio_file.write_bytes(b'fixture')
            request = job_protocol.build_render_request(
                ROOT, {}, content, {'items': []}, {'wav': 'audio.wav', 'tracks': {}}, lambda _: audio_file
            )
        names = {source['name'] for source in request['files']}
        self.assertNotIn('source/tools/matte_sticker.py', names)

    def test_standard_render_workers_do_not_import_or_run_matte(self):
        worker = (ROOT / 'colab_bridge/job_worker.py').read_text()
        adapters = (ROOT / 'adapters.py').read_text()
        self.assertNotIn('tools/matte_sticker.py', worker)
        self.assertNotIn('tools.matte_sticker', adapters)


if __name__ == '__main__':
    unittest.main()
