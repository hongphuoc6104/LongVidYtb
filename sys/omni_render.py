"""Colab-only standalone short assembly using verified parent narration segments."""
from __future__ import annotations

import copy
import shutil
import subprocess
import wave
from pathlib import Path

from omni_platform import short_plans
from scripts.camera_motion import select_semantic_camera_effect


def parent_span(segments: list[dict], parent_scene_id: str, text: str) -> dict:
    """Select an unambiguous contiguous run of complete sentence chunks."""
    candidates = [segment for segment in segments if segment['scene_id'] == parent_scene_id]
    matches = []
    for first in range(len(candidates)):
        combined = ''
        for last in range(first, len(candidates)):
            combined = (combined + ' ' + candidates[last]['text']).strip()
            if combined == ' '.join(text.split()):
                selected = candidates[first:last + 1]
                start = selected[0]['start']
                words = [dict(word=word['word'], start=segment['start'] - start + word['start'], end=segment['start'] - start + word['end']) for segment in selected for word in segment.get('word_timestamps', [])]
                matches.append(dict(scene_id=parent_scene_id, text=text, start=start, end=selected[-1]['end'], word_timestamps=words))
            if len(combined) >= len(text):
                break
    if len(matches) != 1:
        raise ValueError('OMNI_SEGMENT: body must identify one contiguous run of complete spoken chunks')
    return matches[0]


def prepare_shorts(brief: dict, content: dict, audio: dict, images: dict,
                   inputs: Path, public: Path, captions: object, parent_timeline: list[dict]) -> list[dict]:
    """Rebase selected speech chunks and acoustic words onto five standalone scenes."""
    plans = short_plans(brief, content)
    master = audio['tracks']['vi']
    hooks = {hook['id']: hook for hook in audio.get('spinoff_hooks', [])}
    assets = {(item.get('image_id'), item.get('ratio')): item for item in images['items']}
    deliveries = []
    for index, plan in enumerate(plans, 1):
        hook = hooks[plan['id']]
        cursor, scenes, segments, frames = 0., [], [], []
        pieces = [(hook, None)]
        for part in plan['body']:
            pieces.append((parent_span(master['segments'], part['parent_scene_id'], part['segment_text']), part))
        prev_short_eff = None
        for number, (piece, part) in enumerate(pieces, 1):
            scene_id = f'SC{number:02}'
            if part is None:
                path = inputs / hook['path']
                text, stamps = hook['text'], hook.get('word_timestamps', [])
                factor = 1.
            else:
                raw = public / f'short-{index}-{number}-raw.wav'
                with wave.open(str(inputs / master['wav'])) as source:
                    rate = source.getframerate()
                    source.setpos(round(piece['start'] * rate))
                    count = round(piece['end'] * rate) - round(piece['start'] * rate)
                    data = source.readframes(count)
                    with wave.open(str(raw), 'wb') as target:
                        target.setparams(source.getparams())
                        target.writeframes(data)
                factor = 1.0 / master.get('speed', 1.0)
                path = public / f'short-{index}-{number}.wav'
                if factor == 1:
                    shutil.copyfile(raw, path)
                else:
                    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(raw), '-af', f'atempo={factor}', '-ar', '48000', '-c:a', 'pcm_s16le', str(path)], check=True, timeout=90)
                raw.unlink()
                text, stamps = piece['text'], piece.get('word_timestamps', [])
            with wave.open(str(path)) as source:
                if (source.getnchannels(), source.getsampwidth(), source.getframerate()) != (1, 2, 48000):
                    raise ValueError('OMNI_AUDIO_FORMAT: PCM16/48k mono required')
                data = source.readframes(source.getnframes())
                duration = source.getnframes() / 48000
            frames.append(data)
            image_part = part or plan['body'][0]
            image = assets[(image_part['image_id'], '16:9')]
            name = Path(image['path']).name
            # Parent master has already copied this source to the public directory.
            if not (public / name).is_file():
                raise ValueError('OMNI_IMAGE: master image missing from public directory')
            first_eff = 'punch_in' if part is None else select_semantic_camera_effect(str(image.get('description', '') or text), prev_short_eff)
            prev_short_eff = first_eff
            beats = [{'src': name, 'at': 0, 'shot_type': 'full_scene', 'effect': first_eff, 'camera_motion': first_eff, 'focus': {'x': .5, 'y': .5}}]
            if part is not None:
                parent_scene = next(scene for scene in parent_timeline if scene['id'] == part['parent_scene_id'])
                beats += [dict(beat, at=(parent_scene['start'] + beat['at'] - piece['start']) / factor)
                          for beat in parent_scene['images'] if piece['start'] < parent_scene['start'] + beat['at'] < piece['end']]
                bounds = [beat['at'] for beat in beats] + [duration]
                if any(not .83 <= right - left <= 3.8 for left, right in zip(bounds, bounds[1:], strict=False)):
                    raise ValueError('OMNI_VISUAL_PACING: selected body requires 0.83–3.80s visual holds')
            scenes.append({'id': scene_id, 'title': plan['hook_title'], 'start': cursor, 'end': cursor + duration,
                           'image': name, 'images': beats})
            words = [dict(word=word['word'], start=word['start'] / factor, end=min(duration, word['end'] / factor)) for word in stamps]
            segments.append({'scene_id': scene_id, 'text': text, 'start': cursor, 'end': cursor + duration,
                             'content_end': cursor + duration, 'word_timestamps': words})
            cursor += duration
        if not 45 <= cursor <= 60:
            raise ValueError(f'OMNI_SHORT_DURATION: {plan["id"]} measured {cursor:.2f}s outside 45–60s')
        name = f'spinoff-{index:02}.wav'
        with wave.open(str(public / name), 'wb') as target:
            target.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
            target.writeframes(b''.join(frames))
        cues = captions.subtitle_cues(segments, aspect_ratio='9:16')
        words = [dict(word=word['word'], start=segment['start'] + word['start'], end=segment['start'] + word['end']) for segment in segments for word in segment['word_timestamps']]
        deliveries.append({'file': f'video_tiktok_short_{index:02}_9x16.mp4', 'props': {
            'aspect_ratio': '9:16', 'width': 1080, 'height': 1920, 'duration': cursor, 'scenes': scenes,
            'cues': cues, 'words': words, 'audioSrc': name, 'language': 'vi', 'hideSubtitles': False,
            'hook_title': plan['hook_title'], 'reframe_mode': True, 'modern_style': True,
            'cover_text': brief.get('thumbnail_spec', {}).get('text_overlay', ''), 'cover_duration': .15}})
    return copy.deepcopy(deliveries)
