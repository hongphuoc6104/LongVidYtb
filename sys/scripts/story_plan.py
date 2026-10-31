"""Topic-independent story contracts, image prompts and narration-bound visual beats."""
import copy
import json
import math
import re

from output_contract import languages


def normalize_brief(brief):
    if brief.get('schema_version') not in ('2.0','3.0'):
        raise ValueError('Unsupported brief schema version')
    from format_profiles import default_text_style
    b = copy.deepcopy(brief)
    b['schema_version'] = '3.0'
    b.setdefault('planning', {
        'success_criteria': [b['goal']], 'avoid': [],
        'prior_knowledge': 'Chưa xác định; không giả định kiến thức chuyên môn.',
        'pacing': 'Theo lời dẫn tự nhiên; đủ thời gian quan sát hình và đọc chữ.',
        'domain_requirements': [],
        'assumptions': ['Tiêu chí ban đầu lấy từ mục tiêu; cần kiểm tra khi duyệt kịch bản.',
                        'Tốc độ giọng là ước lượng ban đầu, chưa phải số đo hiệu chỉnh.'],
        'text_style': default_text_style(b.get('aspect_ratio', '9:16')),
        'speech_rates': {lang: {'units_per_second': rate, 'uncertainty': .25,
                              'includes_pauses': False, 'source': 'initial estimate; replace with measured voice rate'}
                         for lang, rate in [('vi', 3.6), ('en', 2.5)]}})
    return b


def occurrence(text, anchor):
    if isinstance(anchor, str):
        pos = text.find(anchor)
        if pos < 0:
            raise ValueError('Anchor quote not in narration')
        return pos
    start = 0
    occ = anchor.get('occurrence', 1)
    quote = anchor.get('quote', '')
    for _ in range(occ):
        pos = text.find(quote, start)
        if pos < 0:
            raise ValueError('Anchor quote/occurrence not in narration')
        start = pos + len(quote)
    return pos


def validate_plan(b, c):
    from content_contract import ContractError, error
    errors = []
    def fail(code, path, message):
        errors.append(error(code, path, message, 'Sửa bản nháp; không sửa revision đã lưu.'))
    scenes = c['scenes']; ids = [s['id'] for s in scenes]
    if [x['scene_id'] for x in c['outline']] != ids:
        fail('OUTLINE', 'outline', 'Dàn ý không khớp thứ tự cảnh')
    all_images = set(); all_beats = set()
    internal = ids + [x['id'] for x in c['characters']]
    internal += [im['id'] for s in scenes for im in s['images']]
    internal += [bt['id'] for s in scenes for bt in s['beats']]
    global_visible = c['style']+' '+json.dumps(b['planning']['text_style'],ensure_ascii=False)+' '+' '.join(x['appearance']+' '+x['outfit']+' '+x['name'] for x in c['characters'])
    if any(re.search(r'(?<!\w)'+re.escape(code)+r'(?!\w)', global_visible, re.I) for code in internal):
        fail('INTERNAL_LABEL','characters/style','Mã quản lý xuất hiện trong mô tả dùng tạo hình')
    try:
        from flow_prompts import find_visual_cliche
    except ImportError:
        find_visual_cliche = lambda text: None
    if c.get('style'):
        cliche = find_visual_cliche(c['style'])
        if cliche:
            fail('FLOW_CLICHE_FORBIDDEN', 'style', f"Style contains banned {cliche}")
    for ch in c.get('characters', []):
        for f in ('appearance', 'outfit', 'name'):
            val = ch.get(f)
            if val and isinstance(val, str):
                cliche = find_visual_cliche(val)
                if cliche:
                    fail('FLOW_CLICHE_FORBIDDEN', f"{ch.get('id', 'character')}/{f}", f"Character {f} contains banned {cliche}")
    all_seen = set()
    for s, outline in zip(scenes, c['outline']):
        if outline['purpose'] != s['purpose'] or outline['requirements'] != s['requirements']:
            fail('OUTLINE', s['id'], 'Mục đích hoặc ý của cảnh khác dàn ý')
        for f in ('setting', 'action', 'prompt', 'description', 'bg_description'):
            val = s.get(f)
            if val and isinstance(val, str):
                cliche = find_visual_cliche(val)
                if cliche:
                    fail('FLOW_CLICHE_FORBIDDEN', s['id'], f"{f.capitalize()} contains banned {cliche}")
        scene_images = set()
        for im in s['images']:
            if im['id'] in all_images: fail('IMAGE_ID', s['id'], 'Mã ảnh trùng')
            all_images.add(im['id'])
            if im['based_on'] is not None and im['based_on'] not in all_seen:
                fail('IMAGE_BASE', im['id'], 'Ảnh nền phải là ảnh trước đó trong cùng cảnh hoặc cảnh trước')
            if im['based_on'] and not im['preserve'].strip():
                fail('IMAGE_BASE', im['id'], 'Thiếu nội dung cần giữ nguyên')
            if not set(im['character_ids']) <= set(s['character_ids']):
                fail('CHARACTER_REF', im['id'], 'Nhân vật ảnh không thuộc cảnh')
            visible = ' '.join(im[k] for k in ['description','preserve','change'])
            visible += ' ' + ' '.join(x['text']+' '+x['placement']+' '+x['object'] for x in im['visible_text'])
            if any(re.search(r'(?<!\w)'+re.escape(code)+r'(?!\w)', visible, re.I) for code in internal):
                fail('INTERNAL_LABEL', im['id'], 'Mã nội bộ không được đưa vào mô tả hình/chữ')
            for field in ('description', 'preserve', 'change'):
                val = im.get(field)
                if val and isinstance(val, str):
                    cliche = find_visual_cliche(val)
                    if cliche:
                        fail('FLOW_CLICHE_FORBIDDEN', im['id'], f"{field.capitalize()} contains banned {cliche}")
            for vt in im.get('visible_text', []):
                if isinstance(vt, str):
                    cliche = find_visual_cliche(vt)
                    if cliche:
                        fail('FLOW_CLICHE_FORBIDDEN', im['id'], f"Visible text contains banned {cliche}")
                elif isinstance(vt, dict):
                    for subf in ('text', 'placement', 'object'):
                        subval = vt.get(subf)
                        if subval and isinstance(subval, str):
                            cliche = find_visual_cliche(subval)
                            if cliche:
                                fail('FLOW_CLICHE_FORBIDDEN', im['id'], f"Visible text {subf} contains banned {cliche}")
            scene_images.add(im['id'])
            all_seen.add(im['id'])
        kinds = {im['id']: im.get('kind', 'scene') for im in s['images']}
        if any(kind != 'scene' for kind in kinds.values()) or s.get('layers'):
            fail('LAYERING_DISABLED', s['id'], 'Ảnh background/sticker và layers không còn được hỗ trợ; dùng ảnh scene toàn khung và beats')
        if b.get('visual_pacing_profile') == 'full_frame_v1':
            from scripts.camera_motion import scene_camera_motions
            motions = scene_camera_motions(s)
            if len(motions) >= 2 and len(set(motions)) == 1:
                fail('CAMERA_MOTION_MONOTONY', s['id'], 'All beats use the same camera motion; vary authored intent.')
            for image in s['images']:
                if image.get('based_on') and image.get('has_character', True):
                    has_preserve_lock = bool(re.search(r'expression|facial|biểu cảm', image.get('preserve', ''), re.I))
                    has_explicit_shift = bool(
                        image.get('allow_expression_shift')
                        or re.search(
                            r'expression shift|facial shift|thay đổi biểu cảm|chuyển biểu cảm|biểu cảm chuyển sang',
                            image.get('change', ''),
                            re.I,
                        )
                    )
                    if not (has_preserve_lock or has_explicit_shift):
                        fail('EXPRESSION_LOCK_REQUIRED', image['id'], 'Preserve facial expression unless change explicitly requests a shift.')
        used = {x['image_id'] for x in s['beats']}
        valid_pool = scene_images | all_seen | {im['id'] for sc_all in scenes for im in sc_all['images']} | {'endcard', 'ENDCARD'}
        if not scene_images <= used or not used <= valid_pool:
            fail('IMAGE_USAGE', s['id'], 'Mỗi ảnh scene phải được dùng trong beats và mã ảnh tham chiếu phải tồn tại')
        for lang in languages(b):
            text = s.get('narration_en' if lang == 'en' else 'narration', '')
            positions = []
            for beat in s['beats']:
                try: positions.append(occurrence(text, beat['anchor'][lang]))
                except (ValueError, KeyError): fail('ANCHOR', beat['id'], 'Thiếu/sai điểm neo '+lang)
            if positions and (positions[0] != 0 or any(a >= z for a,z in zip(positions,positions[1:]))):
                fail('ANCHOR_ORDER', s['id'], 'Nhịp đầu bắt đầu lời dẫn; các nhịp sau tăng dần theo từng ngôn ngữ')
        for beat in s['beats']:
            if beat['id'] in all_beats: fail('BEAT_ID', s['id'], 'Mã nhịp trùng')
            all_beats.add(beat['id'])
    source = {x['id']: x for x in b['sources']}
    scene_by_id = {x['id']: x for x in scenes}
    for claim in c['claims']:
        sc = scene_by_id.get(claim['scene_id'], {})
        text = sc.get('narration_en' if claim['language']=='en' else 'narration','')
        src = source.get(claim['source_id'], {})
        if claim['quote'] not in text or claim['fact'] not in src.get('facts',[]) or claim['source_id'] not in sc.get('source_ids',[]):
            fail('CLAIM_SOURCE','claims','Phát biểu/nguồn/dữ kiện không khớp; đúng nghĩa vẫn cần đánh giá')
    if b['facts_required'] and not c['claims']:
        fail('CLAIM_SOURCE','claims','Nội dung yêu cầu dữ kiện phải có liên kết phát biểu và nguồn')
    valid_scenes=set(ids)
    for response in c['revision_response']:
        if not set(response['scene_ids'])<=valid_scenes: fail('REVISION_RESPONSE','revision_response','Phản hồi trỏ tới cảnh không tồn tại')
    if errors: raise ContractError(errors)


def image_units(c):
    if c.get('schema_version') != '3.0': return c['scenes']
    chars = {x['id']: x for x in c['characters']}
    units = []
    for scene in c['scenes']:
        for im in scene['images']:
            # Never serialize IDs or metadata into visible prompt prose.
            people = [chars[x]['appearance'] + '; trang phục: ' + chars[x]['outfit'] for x in im['character_ids']]
            prompt = '\n'.join([c['style'], im['description'], 'Nhân vật: '+'; '.join(people),
                                'Giữ nguyên: '+im['preserve'], 'Thay đổi: '+im['change']])
            units.append({'id': im['id'], 'scene_id': scene['id'], 'prompt': prompt,
                          'character_ids': im['character_ids'], 'based_on': im['based_on'],
                          'visible_text': im['visible_text'], 'kind': im.get('kind', 'scene'),
                          **({'shot_type': im['shot_type']} if 'shot_type' in im else {})})
    return units


def text_prompt(prompt, allowed, style):
    policy = ('Chỉ được vẽ đúng các chữ trong danh sách này: '+json.dumps(allowed, ensure_ascii=False)
              if allowed else 'Không có bất kỳ chữ hoặc số nào trong hình.')
    return prompt + '\n' + policy + '\nKhông thêm nhãn, mã quản lý, logo, watermark, tiêu đề hay chữ trang trí ngoài danh sách.\nPhong cách chữ chung: '+json.dumps(style,ensure_ascii=False)


def estimates(b, c):
    result = {'languages': {}, 'warnings': [], 'status': 'estimated_not_measured'}
    for lang in languages(b):
        rate = b['planning']['speech_rates'][lang]; rows = []
        elapsed = 0.0
        for sc in c['scenes']:
            text = sc['narration_en' if lang=='en' else 'narration']
            units = len(text.split())
            seconds = units/rate['units_per_second'] + (0 if rate.get('includes_pauses') else len(re.findall(r'[.!?;,]',text))*.15 + .3)
            learner_pause = sc.get('audio_direction', {}).get(lang, {}).get('learner_pause_seconds', 0)
            seconds += learner_pause
            rows.append({'scene_id':sc['id'], 'units':units, 'seconds':round(seconds,2),
                         'min':round(seconds*(1-rate['uncertainty']),2), 'max':round(seconds*(1+rate['uncertainty']),2)})
            beat_times = []
            for index, beat in enumerate(sc['beats']):
                try:
                    offset = occurrence(text, beat['anchor'][lang])
                except (KeyError, ValueError):
                    continue
                at = offset/max(1, len(text))*seconds
                beat_times.append(0.0 if index == 0 else at)
            if len(beat_times) == len(sc['beats']):
                for index, at in enumerate(beat_times):
                    following = beat_times[index + 1] if index + 1 < len(beat_times) else seconds
                    hold = max(0.0, following - at)
                    danger_zone = elapsed + at < 15.0
                    low, high = (1.0, 1.8) if danger_zone else (0.83, 3.8)
                    if hold < low or hold > high:
                        zone = 'cold open' if danger_zone else 'body'
                        result['warnings'].append(
                            f"{sc['id']}: beat hold {hold:.2f}s outside {zone} target {low:.2f}–{high:.2f}s ({lang})"
                        )
            elapsed += seconds
        lo=sum(x['min'] for x in rows);hi=sum(x['max'] for x in rows)
        result['languages'][lang]={'scenes':rows,'min':round(lo,2),'max':round(hi,2),'rate':rate}
        if b.get('duration') and (lo>b['duration']['max_seconds'] or hi<b['duration']['min_seconds']):
            result['warnings'].append(lang+': khoảng ước tính không giao với thời lượng yêu cầu')
    return result


def feedback(p, job):
    rows = p.db.execute("SELECT id,detail FROM events WHERE job=? AND module='content' AND event='rejected' ORDER BY id", (job,)).fetchall()
    return [{'request_id':str(row['id']), 'note':row['detail']} for row in rows]


def check_revision(p, job, payload):
    if payload.get('schema_version') != '3.0': return
    from pilot import Blocked, read
    requests = feedback(p,job)
    responses = payload['revision_response']
    if {x['request_id'] for x in responses} != {x['request_id'] for x in requests} or len(responses)!=len(requests):
        raise Blocked('REVISION_RESPONSE: phải xử lý đúng phản hồi hiện tại')
    if requests:
        old = p.rows(job)['content']['envelope']
        if old:
            previous = read(p.path(job,old))['payload']
            if all(previous.get(k)==v for k,v in payload.items() if k not in ('revision_response','open_questions')):
                raise Blocked('UNCHANGED_DRAFT: có yêu cầu sửa nhưng nội dung chưa thay đổi')


def review_plan(b, c, previous=None, requests=()):
    timing=estimates(b,c); plan=b['planning']
    def bullets(values): return '\n'.join('- '+str(x) for x in values) or 'Không có.'
    lines=['## Mục tiêu và người xem', b['goal'], 'Người xem: '+b['audience'],
           'Kiến thức đầu vào: '+plan['prior_knowledge'], 'Tiêu chí đạt:\n'+bullets(plan['success_criteria']),
           'Cần tránh:\n'+bullets(plan['avoid']), 'Yêu cầu chuyên biệt:\n'+bullets(plan['domain_requirements']),
           'Nhịp kể: '+plan['pacing'], 'Giả định cần kiểm tra:\n'+bullets(plan['assumptions']),
           f"{len(c['scenes'])} cảnh · {sum(len(s['images']) for s in c['scenes'])} hình logic · {sum(len(s['beats']) for s in c['scenes'])} nhịp",
           'Dual tạo hai bộ hình riêng cho hai tỷ lệ.' if b['aspect_ratio']=='dual' else 'Tỷ lệ: '+b['aspect_ratio'],
           '## Thời lượng dự kiến (chưa phải WAV)']
    for lang, data in timing['languages'].items():
        lines.append(f"{lang.upper()}: {data['min']}–{data['max']} giây. Cơ sở: {data['rate']['source']}")
        lines.append('| Cảnh | Khoảng giây dự kiến |\n|---|---|\n'+'\n'.join(f"| {r['scene_id']} | {r['min']}–{r['max']} |" for r in data['scenes']))
    lines.append('Cảnh báo thời lượng/nhịp:\n'+bullets(timing['warnings']))
    style=plan['text_style']
    lines += ['## Chữ tạo cùng hình', f"Kiểu: {style['font']}. Màu: {style['color']}. Viền/nền: {style['outline']}. Cỡ: {style['size']}. Vị trí: {style['placement']}.",
              'Chỉ những chữ liệt kê ở từng hình được phép xuất hiện; danh sách rỗng nghĩa là không chữ hoặc số.']
    for scene in c['scenes']:
        lines += ['## '+scene['id']+' — '+scene['title'], 'Mục đích: '+scene['purpose'], scene['narration']]
        if scene.get('narration_en'): lines.append('EN: '+scene['narration_en'])
        for lang, direction in scene.get('audio_direction', {}).items():
            lines.append(f"Chỉ đạo âm thanh {lang}: {direction['intent']} · Lưu ý phát âm: {direction['pronunciation_notes'] or 'Không có'} · Khoảng chờ học viên cuối cảnh: {direction['learner_pause_seconds']} giây (chưa xác minh WAV). Ý đồ giọng chưa phải điều khiển TTS.")
        for im in scene['images']:
            words='; '.join('“'+x['text']+'” — '+x['placement']+'; đối tượng: '+x['object'] for x in im['visible_text']) or 'Không có chữ/số'
            lines.append('**Hình '+im['id']+'** — '+im['description']+'\n\nẢnh gốc: '+str(im['based_on'] or 'Tạo mới')+'; giữ: '+(im['preserve'] or 'Không áp dụng')+'; đổi: '+im['change']+'\n\nLý do: '+im['reason']+'\n\nChữ được phép: '+words)
        for beat in scene['beats']:
            anchors='; '.join(lang+': “'+a['quote']+'” (lần '+str(a['occurrence'])+')' for lang,a in beat['anchor'].items())
            lines.append('Nhịp '+beat['id']+' → '+beat['image_id']+' · '+beat['effect']+' · '+anchors+' · '+beat['purpose'])
    lines += ['## Nhân vật', bullets(x['name']+': '+x['appearance']+'; '+x['outfit'] for x in c['characters'])]
    if any(x.get('quote_en') for x in c['coverage']):
        lines += ['## Đối chiếu ý bắt buộc (Việt / Anh)',
                  '| Ý | Cảnh | Lời dẫn Việt | Lời dẫn Anh |\n|---|---|---|---|\n' +
                  '\n'.join(f"| {x['requirement_id']} | {x['scene_id']} | {x['quote']} | {x.get('quote_en','—')} |" for x in c['coverage'])]
    else:
        lines += ['## Đối chiếu ý bắt buộc', bullets(x['requirement_id']+' → '+x['scene_id']+': '+x['quote'] for x in c['coverage'])]
    lines += ['## Phát biểu và nguồn', bullets(x['scene_id']+': “'+x['quote']+'” → '+x['source_id']+': '+x['fact'] for x in c['claims']),
              '## Nguồn', bullets(x['id']+' — '+x['title']+'; '+x['reference'] for x in b['sources']),
              '## Phản hồi cần xử lý', bullets(x['request_id']+': '+x['note'] for x in requests),
              '## Kết quả sửa', bullets(x['request_id']+' — '+x['status']+': '+x['explanation']+'; cảnh: '+', '.join(x['scene_ids']) for x in c['revision_response']),
              '## Vấn đề còn lại', bullets(c['open_questions'])]
    if previous:
        changed=[s['id'] for s in c['scenes'] if s not in previous.get('scenes',[])]
        lines += ['## Thay đổi so với bản trước', 'Cảnh thay đổi: '+', '.join(changed),
                  'Trường thay đổi: '+', '.join(k for k in c if c[k]!=previous.get(k))]
    return '\n\n'.join(lines)


def _word_anchor_time(segment: dict, offset: int) -> float | None:
    """Resolve a character offset using segment-relative acoustic word timestamps.

    Never infer whether timestamps are absolute from their numeric magnitude.
    The worker emits relative seconds; malformed or unmatched data uses fallback.
    """
    tokens = list(re.finditer(r'\S+', segment.get('text', '')))
    stamps = segment.get('word_timestamps')
    if not isinstance(stamps, list) or len(stamps) != len(tokens):
        return None
    duration = float(segment.get('content_end', segment['end'])) - float(segment['start'])
    previous_end = 0.0
    previous_start = 0.0
    for token, stamp in zip(tokens, stamps, strict=True):
        if not isinstance(stamp, dict) or stamp.get('word') != token.group():
            return None
        try:
            left, right = float(stamp['start']), float(stamp['end'])
        except (KeyError, TypeError, ValueError):
            return None
        if (not all(math.isfinite(value) for value in (left, right))
                or not 0 <= previous_start <= left < right <= duration + .002
                or left + .02 < previous_end):
            return None
        previous_start = left
        previous_end = right
    for index, token in enumerate(tokens):
        if token.start() <= offset < token.end():
            return float(segment['start']) + float(stamps[index]['start'])
    return None


TEMPO_HOLD_WINDOWS = {
    'short_9x16': {
        'fast': (0.9, 1.8),
        'normal': (2.0, 3.5),
        'slow': (3.5, 5.5),
        'hold': (1.5, 3.0),
    },
    'long_16x9': {
        'fast': (2.0, 4.0),
        'normal': (4.0, 7.0),
        'slow': (7.0, 10.0),
        'hold': (5.0, 20.0),
    },
}


def _check_tempo_windows(beats, scene_duration, format_profile='short_9x16'):
    import logging
    log = logging.getLogger('story_plan')
    windows = TEMPO_HOLD_WINDOWS.get(format_profile, TEMPO_HOLD_WINDOWS['short_9x16'])
    for i, beat in enumerate(beats):
        tempo = beat.get('tempo')
        if not tempo or tempo not in windows:
            continue
        next_at = beats[i + 1]['at'] if i + 1 < len(beats) else scene_duration
        hold = next_at - beat['at']
        nom_low, nom_high = windows[tempo]
        min_allowed = nom_low * 0.85
        max_allowed = nom_high * 1.15
        if hold < min_allowed or hold > max_allowed:
            log.warning(
                f"Tempo violation: beat {beat['id']} tempo='{tempo}' hold={hold:.2f}s "
                f"outside window {nom_low:.1f}–{nom_high:.1f}s (tolerance {min_allowed:.2f}–{max_allowed:.2f}s)"
            )


def timeline(c, images, audio, language, ratio):
    """Prefer acoustic word starts, recording interpolation fallbacks per beat."""
    by_id={(im.get('image_id') or im.get('scene_id'), im.get('ratio', ratio)): im for im in images['items']}
    output=[]
    for sc in c['scenes']:
        track = audio.get('tracks', {}).get(language)
        track_segments = track['segments'] if track else (audio['segments'] if audio.get('language', 'vi') == language else audio['en']['scenes'])
        spans = [x for x in track_segments if x['scene_id']==sc['id']]
        start=spans[0]['start'];end=spans[-1]['end']
        if c.get('schema_version')!='3.0':
            im=by_id[(sc['id'],ratio)];output.append({'id':sc['id'],'title':sc['title'],'image':im['path'],'start':start,'end':end});continue
        text=sc['narration_en' if language=='en' else 'narration'];beats=[]
        from scripts.camera_motion import scene_camera_motions
        motions = scene_camera_motions(sc)

        # Index segments in narration text
        seg_spans = []
        cursor = 0
        for seg in spans:
            stext = seg.get('text', '')
            pos = text.find(stext, cursor)
            if pos < 0:
                pos = text.find(stext)
            if pos >= 0:
                seg_spans.append((seg, pos, pos + len(stext)))
                cursor = pos + len(stext)
            else:
                clean_stext = re.sub(r'[^\w\s]', '', stext).strip()
                clean_text = re.sub(r'[^\w\s]', '', text)
                clean_pos = clean_text.find(clean_stext)
                if clean_pos >= 0:
                    seg_spans.append((seg, clean_pos, clean_pos + len(stext)))
                else:
                    seg_spans.append((seg, -1, -1))

        for idx, (bt, motion) in enumerate(zip(sc['beats'], motions, strict=True)):
            offset=occurrence(text,bt['anchor'][language])
            timing_method = 'narration_anchor_interpolated'
            at = None
            if idx == 0 or offset == 0:
                at = start
                timing_method = 'measured_sentence_anchor'
            elif seg_spans:
                for seg, p_start, p_end in seg_spans:
                    if p_start >= 0 and p_start <= offset < p_end:
                        if offset == p_start:
                            at = float(seg['start'])
                            timing_method = 'measured_sentence_anchor'
                        else:
                            measured = _word_anchor_time(seg, offset - p_start)
                            if measured is not None:
                                at = measured
                                timing_method = 'acoustic_word_timestamps'
                            else:
                                prefix = seg['text'][:offset - p_start]
                                prefix_syl = len(prefix.strip().split()) if prefix.strip() else 0
                                total_syl = max(1, len(seg['text'].strip().split()))
                                syllable_ratio = prefix_syl / total_syl
                                seg_content_dur = float(seg.get('content_end', seg['end'])) - float(seg['start'])
                                at = float(seg['start']) + syllable_ratio * seg_content_dur
                                timing_method = 'syllable_interpolated'
                        break

            if at is None:
                # Syllable-proportional fallback across the scene
                prefix = text[:offset]
                prefix_syl = len(prefix.strip().split()) if prefix.strip() else 0
                total_syl = max(1, len(text.strip().split()))
                syllable_ratio = prefix_syl / total_syl
                at = start + syllable_ratio * (spans[-1].get('content_end', end) - start)
                timing_method = 'syllable_interpolated'

            rel_at = round(at - start, 4)
            if beats and rel_at <= beats[-1]['at']:
                rel_at = round(beats[-1]['at'] + 1.0 / 30.0, 4)

            im=by_id.get((bt['image_id'],ratio))
            if im is None and images.get('reframe_mode'):
                im=by_id[(bt['image_id'],'16:9')]
            if im is None:
                raise ValueError('Missing requested image aspect: '+bt['image_id'])
            image_item = next((image for image in sc.get('images', []) if image['id'] == bt['image_id']), {})
            is_endcard_beat = bool(bt.get('is_endcard') or image_item.get('is_endcard') or bt.get('spec') == 'endcard' or image_item.get('spec') == 'endcard')
            emphasis_text_beat = bt.get('emphasis_text') or image_item.get('emphasis_text')
            beats.append({'id':bt['id'],'src':im['path'],'at':rel_at,'tempo':bt.get('tempo'),'effect':motion,'camera_motion':motion,'transition':'cut','focus':bt.get('focus'),
                          'emphasis_text': emphasis_text_beat,
                          'is_endcard': is_endcard_beat,
                          'timing_method': timing_method,
                          'shot_type': image_item.get('shot_type', 'full_scene')})

        # Only apply smoothing if all beats are purely unmeasured/legacy interpolation
        if all(beat.get('timing_method') == 'narration_anchor_interpolated' for beat in beats):
            from visual_pacing import smooth_interpolated_beats
            smooth_interpolated_beats(beats, start, end)
        beats[0]['at']=0
        for i in range(len(beats) - 1):
            if round(beats[i]['at'] * 30) >= round(beats[i + 1]['at'] * 30):
                beats[i + 1]['at'] = round((round(beats[i]['at'] * 30) + 1) / 30.0, 4)

        format_profile = 'long_16x9' if ratio == '16:9' and (end - start > 120.0 or len(c['scenes']) > 10) else 'short_9x16'
        _check_tempo_windows(beats, end - start, format_profile)

        has_any_words = any(s[0].get('word_timestamps') for s in seg_spans) if seg_spans else False
        methods = {beat['timing_method'] for beat in beats}
        if not has_any_words:
            scene_timing_method = 'narration_anchor_interpolated'
        elif methods <= {'measured_sentence_anchor', 'acoustic_word_timestamps'}:
            scene_timing_method = 'acoustic_word_timestamps'
        elif len(methods) == 1:
            scene_timing_method = next(iter(methods))
        else:
            scene_timing_method = 'mixed_word_timestamps_and_interpolation'
        scene_out={'id':sc['id'],'title':sc['title'],'start':start,'end':end,'image':beats[0]['src'],'images':beats,
                   'timing_method': scene_timing_method}
        output.append(scene_out)
    return output


def calibrate_rates(c, audio, source):
    """Measured narration units per WAV second, including the actual voice pauses."""
    rates = {}
    for lang, duration in ([(lang, track['duration']) for lang,track in audio['tracks'].items()] if audio.get('tracks') else [('vi',audio['duration'])] + ([('en',audio['en']['duration'])] if audio.get('en') else [])):
        units = sum(len(sc['narration_en' if lang=='en' else 'narration'].split()) for sc in c['scenes'])
        rates[lang] = {'units_per_second':round(units/duration,4), 'uncertainty':.2,
                       'includes_pauses':True, 'source':source+'; measured WAV including pauses'}
    return rates


def safe_corrections(c, note):
    """Keep verbatim feedback in journals; translate management IDs only for the model prompt."""
    if c.get('schema_version') != '3.0': return note
    replacements={x['id']:x['name'] for x in c['characters']}
    for sc in c['scenes']:
        replacements[sc['id']]='cảnh đang được sửa'
        replacements.update({x['id']:'the specified image' for x in sc['images']})
        replacements.update({x['id']:'nhịp đang được sửa' for x in sc['beats']})
    pattern=r'(?<!\w)('+ '|'.join(re.escape(k) for k in sorted(replacements,key=len,reverse=True))+r')(?!\w)'
    return re.sub(pattern,lambda m:replacements[m.group()],note) if replacements else note
