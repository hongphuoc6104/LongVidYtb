"""Desktop control for explicit output contracts; all audio processing is remote."""
import copy
from pathlib import Path

from output_contract import languages, narration, primary_language, voice_settings


def configure_accounts(cfg: dict, selection: dict) -> None:
    """Exact bindings stay exact; an idle-pool policy must not become a preferred-account pin."""
    options = cfg['colab_tts']
    options['management_session'] = selection
    bound = selection.get('runtime_bindings', {}).get('colab', {}).get('account')
    if bound:
        options['account'] = bound.removeprefix('colab:')
    elif options.get('account') == 'auto-idle' or selection.get('selection') == 'auto':
        options['account'] = 'auto-idle'
    elif selected := selection.get('defaults', {}).get('colab'):
        options['account'] = selected.removeprefix('colab:')


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
    from colab_bridge.client import ColabError, enabled
    from colab_bridge.protocol import build_request

    from pilot import Blocked, read, write

    brief = pilot.brief(job)[0]
    content = pilot.payload(job, 'content')
    cfg = config(pilot, job)
    from format_profiles import audio_mastering_for_format, resolve_format_profile
    try:
        format_mastering = audio_mastering_for_format(resolve_format_profile(brief))
        cfg.update(format_mastering)
    except Exception:
        pass
    cfg.setdefault('colab_tts', {})['job_id'] = job
    import execution
    if execution.is_job(pilot, job):
        selection = execution.settings(pilot, job).get('management_session', {})
        configure_accounts(cfg, selection)
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
    secondary_segments = []
    if primary == 'en' and 'vi' in requested:
        secondary_segments = [{'scene_id': scene['id'], 'language': 'vi', 'text': narration(scene, 'vi'),
                         'retake': takes.get(scene['id'], 0),
                         'tail': scene_tail(scene, 'vi', gaps, i == len(content['scenes']) - 1)}
                        for i,scene in enumerate(content['scenes'])]
    pause_plan = None
    policy = cfg.get('tts_pause_policy', 'legacy')
    if policy not in ('legacy', 'format_v1'):
        raise Blocked('PAUSE_POLICY: unsupported tts_pause_policy')
    if policy == 'format_v1':
        from adapters import english_parts, is_english
        from narration_pauses import plan_tracks
        try:
            scenes, secondary_segments, pause_plan = plan_tracks(brief, content, takes, primary)
        except ValueError as ex:
            raise Blocked(str(ex)) from ex
        secondary = []
        if primary == 'vi':
            for scene, item in zip(content['scenes'], scenes, strict=True):
                words = [v['word'] for v in scene.get('vocabulary', []) if is_english(v.get('word', ''))]
                parts = [english_parts(text, words) for text in item['texts']]
                if any(part['lang'] == 'en' for group in parts for part in group):
                    item['parts'] = parts
    from omni_platform import short_plans
    shorts = short_plans(brief, content)
    if shorts and primary != 'vi':
        raise Blocked('OMNI_LANGUAGE: Vietnamese primary narration required for reused spin-off audio')
    try:
        request = build_request(pilot.root, cfg, scenes, secondary,
                                primary_language=primary, assemble=True, secondary_scenes=secondary_segments,
                                spinoff_hooks=shorts, pause_plan=pause_plan)
        write(out / 'request-colab.json', request)
        import execution
        guard = (lambda: execution.before_submit(pilot, job)) if execution.is_job(pilot, job) else None
        from colab_bridge.parallel_audio import synthesize
        synthesize(pilot.root, cfg, request, out, pilot.job(job) / 'cache/colab-tts', before_submit=guard)
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
    cfg = config(pilot, job)
    cfg.setdefault('colab_tts', {})['job_id'] = job
    import execution
    if execution.is_job(pilot, job):
        selection = execution.settings(pilot, job).get('management_session', {})
        configure_accounts(cfg, selection)
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


def produce_parallel(
    root: Path,
    cfg: dict,
    scenes: list[dict],
    out: Path,
    cache: Path,
    *,
    max_concurrency: int = 3,
    scenes_per_shard: int = 4,
    primary_language: str = 'vi',
    pool_manager=None,
    auto_teardown: bool = True,
) -> dict:
    """Partition multi-scene synthesis across multiple idle Colab T4 accounts in parallel.

    Dispatches shards concurrently via `ColabPoolDispatcher` (work-stealing failover),
    deterministically merges segment waveforms, word timestamps, and metadata in
    exact scene sequence order, and automatically tears down used Colab T4 sessions
    and temporary shard directories upon completion.
    """
    import shutil
    import threading
    import wave

    from colab_bridge.client import Client
    from colab_bridge.pool_manager import ColabPoolDispatcher, ColabPoolManager
    from colab_bridge.protocol import build_request

    from pilot import read, write

    out, cache = Path(out), Path(cache)
    out.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)

    shard_size = max(1, int(scenes_per_shard))
    shards = [scenes[i : i + shard_size] for i in range(0, len(scenes), shard_size)]
    tasks = [
        {
            'id': f'audio-shard-{idx:03d}',
            'shard_index': idx,
            'scenes': shard,
        }
        for idx, shard in enumerate(shards)
    ]

    mgr = pool_manager or ColabPoolManager()
    dispatcher = ColabPoolDispatcher(mgr)
    used_accounts: set[str] = set()
    used_lock = threading.Lock()
    teardown_report = None

    def _run_shard(worker, task: dict) -> dict:
        s_idx = int(task['shard_index'])
        shard_out = out / 'shards' / f'shard-{s_idx:03d}'
        shard_cache = cache / f'shard-{s_idx:03d}'
        shard_out.mkdir(parents=True, exist_ok=True)
        shard_cache.mkdir(parents=True, exist_ok=True)

        shard_cfg = copy.deepcopy(cfg)
        shard_cfg.setdefault('colab_tts', {})['account'] = worker.account_id
        shard_cfg['colab_tts']['session'] = worker.session_name
        with used_lock:
            used_accounts.add(worker.account_id)

        req = build_request(
            root,
            shard_cfg,
            task['scenes'],
            primary_language=primary_language,
            assemble=False,
        )
        Client(root, shard_cfg).synthesize(req, shard_out, shard_cache)
        res = read(shard_out / 'tts-result.json')
        return {
            'shard_index': s_idx,
            'account': worker.account_id,
            'shard_out': shard_out,
            'request': req,
            'result': res,
        }

    try:
        shard_outputs = dispatcher.dispatch_all(
            tasks,
            _run_shard,
            max_concurrency=max_concurrency,
            role='tts',
        )

        merged_segments = []
        merged_spans = []
        merged_batches = []
        global_seg_idx = 0
        cursor = 0.0
        combined_frames = bytearray()
        wav_params = None

        for item in sorted(shard_outputs, key=lambda x: x['shard_index']):
            s_out = item['shard_out']
            res = item['result']
            merged_spans.extend(res.get('english_spans', []))
            merged_batches.extend(res.get('batches', []))
            for seg in res.get('segments', []):
                src_wav = s_out / seg['path']
                dst_name = f'segment-{global_seg_idx:04d}.wav'
                dst_wav = out / dst_name
                shutil.copy2(src_wav, dst_wav)
                with wave.open(str(dst_wav), 'rb') as wf:
                    wav_params = wf.getparams()
                    dur = wf.getnframes() / wf.getframerate()
                    combined_frames.extend(wf.readframes(wf.getnframes()))
                seg_entry = dict(
                    seg,
                    path=dst_name,
                    start=round(cursor, 3),
                    end=round(cursor + dur, 3),
                    content_end=round(cursor + float(seg.get('content_duration', dur)), 3),
                    worker_account=item['account'],
                )
                cursor += dur
                merged_segments.append(seg_entry)
                global_seg_idx += 1

        narration_wav = out / 'narration.wav'
        if wav_params is not None:
            with wave.open(str(narration_wav), 'wb') as wf:
                wf.setparams((wav_params.nchannels, wav_params.sampwidth, wav_params.framerate, 0, 'NONE', 'not compressed'))
                wf.writeframes(combined_frames)
    finally:
        shutil.rmtree(out / 'shards', ignore_errors=True)
        if auto_teardown and used_accounts:
            teardown_report = mgr.teardown_job_resources(
                account_ids=sorted(used_accounts),
                close_chrome=False,
            )

    merged_report = {
        'voice': shard_outputs[0]['result']['voice'] if shard_outputs else cfg.get('tts_voice', 'VietNarrator'),
        'backend': 'colab-omnivoice',
        'wav': 'narration.wav',
        'duration': round(cursor, 3),
        'segments': merged_segments,
        'english_spans': merged_spans,
        'batches': merged_batches,
        'shards_dispatched': len(shard_outputs),
        'worker_accounts': [x['account'] for x in shard_outputs],
        'teardown': teardown_report,
    }
    write(out / 'tts-result.json', merged_report)
    return merged_report

