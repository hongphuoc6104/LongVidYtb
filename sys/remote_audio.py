"""Desktop control for explicit output contracts; all audio processing is remote."""
import copy
from pathlib import Path

from output_contract import languages, narration, primary_language, voice_settings


def primary_scene_request(scene: dict, text: str, language: str, pauses: dict,
                          retake: int, last: bool) -> dict:
    """Keep sentence chunks, explicit [pause:...] gaps, tone and bilingual spans aligned one-to-one."""
    from adapters import chunks_with_gaps, english_parts, is_english, scene_tail

    texts, gaps = chunks_with_gaps(text, pauses)
    item = {'scene_id': scene['id'], 'narration': text, 'texts': texts,
            'tone': scene.get('tone'), 'retake': retake,
            'gaps': gaps,
            'tail': scene_tail(scene, language, pauses, last)}
    if language == 'vi':
        words = [v['word'] for v in scene.get('vocabulary', []) if is_english(v.get('word', ''))]
        parts = [english_parts(part, words) for part in texts]
        if any(x['lang'] == 'en' for part in parts for x in part):
            item['parts'] = parts
    return item


def produce(pilot, job, out):
    from adapters import DEFAULT_PAUSE, config, retakes, scene_tail
    from colab_bridge.client import Client, ColabError, enabled
    from colab_bridge.protocol import build_request

    from pilot import Blocked, read, write

    brief = pilot.brief(job)[0]
    content = pilot.payload(job, 'content')
    cfg = copy.deepcopy(config(pilot))
    cfg.setdefault('colab_tts', {})['job_id'] = job
    import execution
    if execution.is_job(pilot, job):
        selection = execution.settings(pilot, job).get('management_session', {})
        cfg['colab_tts']['management_session'] = selection
        selected = selection.get('runtime_bindings', {}).get('colab', {}).get('account') or selection.get('defaults', {}).get('colab')
        if selected:
            cfg['colab_tts']['account'] = selected.removeprefix('colab:')
    if not enabled(cfg):
        raise Blocked('COLAB_REQUIRED: explicit output jobs never fall back to local TTS')
    requested = languages(brief)
    primary = primary_language(brief)
    for language in requested:
        settings = voice_settings(brief, language, cfg)
        # Resolve the chosen identity; a default for a different voice cannot win.
        matches = []
        for path in (pilot.root / 'assets/voices').glob('*/profile.json'):
            profile = read(path)
            allowed_langs = set(profile.get('languages') or [profile.get('language')])
            if language in allowed_langs and profile.get('voice', '').casefold() == settings['voice'].casefold():
                matches.append((path, profile))
        if len(matches) != 1:
            raise Blocked('VOICE_REFERENCE_REQUIRED: missing or ambiguous ' + settings['voice'])
        path, profile = matches[0]
        rel_path = str(path.relative_to(pilot.root))
        cfg.setdefault('voices', {})[language] = rel_path
        cfg.setdefault('colab_tts', {}).setdefault('voices', {})[language] = rel_path
        cfg['en_voice' if language == 'en' else 'tts_voice'] = profile['voice']
        cfg['en_speed' if language == 'en' else 'tts_speed'] = settings['speed']
    takes = retakes(pilot, job)
    gaps = cfg.get('tts_pause', DEFAULT_PAUSE)
    scenes = []
    for i, scene in enumerate(content['scenes']):
        text = narration(scene, primary)
        if not text.strip():
            raise Blocked('NARRATION_REQUIRED: ' + primary + '/' + scene['id'])
        item = primary_scene_request(scene, text, primary, gaps, takes.get(scene['id'], 0), i == len(content['scenes']) - 1)
        scenes.append(item)
    secondary = []
    if primary != 'en' and 'en' in requested:
        secondary = [{'scene_id': scene['id'], 'narration_en': narration(scene, 'en'),
                      'retake': takes.get(scene['id'], 0),
                      'tail': scene_tail(scene, 'en', gaps, i == len(content['scenes']) - 1)}
                     for i, scene in enumerate(content['scenes'])]
    secondary_vi = []
    if primary == 'en' and 'vi' in requested:
        secondary_vi = [{'scene_id': scene['id'], 'language': 'vi', 'text': narration(scene, 'vi'),
                         'retake': takes.get(scene['id'], 0),
                         'tail': scene_tail(scene, 'vi', gaps, i == len(content['scenes']) - 1)}
                        for i,scene in enumerate(content['scenes'])]
    from omni_platform import short_plans
    shorts = short_plans(brief, content)
    if shorts and primary != 'vi':
        raise Blocked('OMNI_LANGUAGE: Vietnamese primary narration required for reused spin-off audio')
    try:
        request = build_request(pilot.root, cfg, scenes, secondary,
                                primary_language=primary, assemble=True, secondary_scenes=secondary_vi, spinoff_hooks=shorts)
        write(out / 'request-colab.json', request)
        import execution
        guard = (lambda: execution.before_submit(pilot, job)) if execution.is_job(pilot, job) else None
        Client(pilot.root, cfg).synthesize(request, out, pilot.job(job) / 'cache/colab-tts', before_submit=guard)
        report = read(out / 'audio-result.json')
        if report.get('processing_location') != 'colab' or report.get('language') != primary:
            raise Blocked('COLAB_ASSEMBLY_REQUIRED: prepared remote result missing')
    except (ColabError, ValueError, OSError) as ex:
        raise Blocked(str(ex)) from ex
    payload = report['payload']

    def asset(name):
        if Path(name).name != name:
            raise Blocked('Unsafe remote audio path')
        return str((out / name).relative_to(pilot.job(job)))

    def convert(track):
        for key in ('wav', 'srt', 'generation_report'):
            if key in track:
                track[key] = asset(track[key])
        for field in ('segments', 'scenes'):
            for item in track.get(field, []):
                item['path'] = asset(item['path'])

    for hook in payload.get('spinoff_hooks', []):
        hook['path'] = asset(hook['path'])
    convert(payload)
    for track in payload['tracks'].values():
        convert(track)
    if payload.get('en'):
        convert(payload['en'])
    return payload


def render(pilot, job, out):
    """Control/collect only; remote worker owns timeline, captions, media and encoding."""
    from adapters import config
    from colab_bridge.client import Client, ColabError, enabled
    from colab_bridge.job_protocol import build_render_request

    from pilot import Blocked, read, write
    cfg = copy.deepcopy(config(pilot))
    cfg.setdefault('colab_tts', {})['job_id'] = job
    import execution
    if execution.is_job(pilot, job):
        selection = execution.settings(pilot, job).get('management_session', {})
        cfg['colab_tts']['management_session'] = selection
        selected = selection.get('runtime_bindings', {}).get('colab', {}).get('account') or selection.get('defaults', {}).get('colab')
        if selected:
            cfg['colab_tts']['account'] = selected.removeprefix('colab:')
    if not enabled(cfg):
        raise Blocked('COLAB_REQUIRED: explicit outputs never render locally')
    try:
        request = build_render_request(pilot.root, pilot.brief(job)[0], pilot.payload(job, 'content'),
                                       pilot.payload(job, 'images'), pilot.payload(job, 'audio'),
                                       lambda name: pilot.path(job, name))
        write(out / 'request-colab-render.json', request)
        import execution
        guard = (lambda: execution.before_submit(pilot, job)) if execution.is_job(pilot, job) else None
        Client(pilot.root, cfg).render(request, out, pilot.job(job) / 'cache/colab-render', before_submit=guard)
        report = read(out / 'render-result.json')
    except (ColabError, ValueError, OSError) as ex:
        raise Blocked(str(ex)) from ex
    def path(name): return str((out / name).relative_to(pilot.job(job)))
    result = {'video': path('video.mp4'), 'stills': [path(name) for name in report['files'] if name.endswith('.png')],
              'layout_report': path('layout.json'), 'editorial_report': path('editorial-audit.json'),
              'remote_report': path('render-result.json'), 'language': report['outputs'][0]['language'],
              'duration': report['outputs'][0]['duration']}
    for delivery in report['outputs']:
        if len(report['outputs']) > 1:
            result['video_9x16' if delivery['aspect_ratio'] == '9:16' else 'video_16x9'] = path(delivery['file'])
    if pilot.brief(job)[0].get('omni_platform'):
        result['social_assets'] = {name: path(name) for name in report['files'] if name in {'video_youtube_16x9.mp4', 'video_facebook_16x9.mp4', 'thumbnail_youtube_16x9.png', 'cover_tiktok_reels_9x16.png', 'SOCIAL_POST_KIT.md'} or name.startswith('subtitles_') or name.startswith('video_tiktok_short_')}
    return result
