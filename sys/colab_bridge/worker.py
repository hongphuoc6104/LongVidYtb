"""Runs only on Colab: cached models/prompts, bounded T4 batches, measured WAVs.

Imported into the persistent Jupyter kernel, so subsequent jobs reuse weights.
No BetterBox, HTTP server, paid inference API, CPU fallback or torch.compile.
"""
import gc
import hashlib
import json
import re
import time
import zipfile
from pathlib import Path

_MODEL = None
_MODEL_KEY = None
_PROMPTS = {}
SR = 48000

_VI_ONES = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
_VI_LOANWORD_MAP = {
    '\\bRichard P\\. Feynman\\b': 'Ri-chát Phây-man',
    '\\bRichard Lee\\b': 'Ri-chát Li',
    '\\bRichard\\b': 'Ri-chát',
    '\\bFeynman\\b': 'Phây-man',
    '\\bLee\\b': 'Li',
    "\\bJu/'hoansi\\b": 'Giu-hoan-si',
    "\\bJu/'\\b": 'Giu',
    '\\bKalahari\\b': 'Ka-la-ha-ri',
    '\\bBotswana\\b': 'Bốt-xoa-na',
    '\\bHadza\\b': 'Hát-da',
    '\\bTanzania\\b': 'Tan-da-ni-a',
    '\\bAche\\b': 'A-sê',
    '\\bParaguay\\b': 'Pa-ra-goay',
    '\\bMartu\\b': 'Mác-tu',
    '\\bBlombos\\b': 'Bờ-lôm-bốt',
    '\\bPolly Wiessner\\b': 'Pô-li Uýt-nơ',
    '\\bPolly\\b': 'Pô-li',
    '\\bWiessner\\b': 'Uýt-nơ',
    '\\bJames Suzman\\b': 'Giêm Xút-man',
    '\\bJames\\b': 'Giêm',
    '\\bSuzman\\b': 'Xút-man',
    '\\bJeffrey D\\. Karpicke\\b': 'Giép-phri Ca-pích',
    '\\bKarpicke\\b': 'Ca-pích',
    '\\bHenry L\\. Roediger\\b': 'Hen-ri Rô-đi-gơ',
    '\\bRoediger\\b': 'Rô-đi-gơ',
    '\\bPaul Lockhart\\b': 'Pôn Lốc-hát',
    '\\bLockhart\\b': 'Lốc-hát',
    '\\bJohn Sweller\\b': 'Giôn Xoan-lơ',
    '\\bSweller\\b': 'Xoan-lơ',
    '\\bJohn M\\. Swales\\b': 'Giôn Xoeo',
    '\\bSwales\\b': 'Xoeo',
    '\\bSrinivasan Keshav\\b': 'Kê-sáp',
    '\\bKeshav\\b': 'Kê-sáp',
    '\\bCARS\\b': 'Ca',
    '\\bdopamine\\b': 'đô-pa-min',
    '\\bcortisol\\b': 'cóc-ti-dôn',
    '\\badrenaline\\b': 'a-đrê-na-lin',
    '\\bserotonin\\b': 'sê-rô-tô-nin',
    '\\boxytocin\\b': 'ô-xi-tô-xin',
    '\\bendorphin\\b': 'en-đô-phin',
    '\\bglucose\\b': 'glu-cô-dơ',
    '\\bprefrontal cortex\\b': 'vỏ não trước trán',
    '\\bamygdala\\b': 'hạch hạnh nhân',
    '\\bhippocampus\\b': 'hồi hải mã',
    '\\bSumer\\b': 'Su-me',
    '\\bEdubba\\b': 'Ê-đu-ba',
    '\\bMesopotamia\\b': 'Mê-sô-pô-ta-mi-a',
    '\\bPrussia\\b': 'Phổ',
    '\\bJaak Panksepp\\b': 'Giác Păng-xép',
    '\\bJaak\\b': 'Giác',
    '\\bPanksepp\\b': 'Păng-xép',
    '\\bTim Pychyl\\b': 'Tim Pi-chin',
    '\\bPychyl\\b': 'Pi-chin',
    '\\bFuschia Sirois\\b': 'Phu-si-a Si-roa',
    '\\bSirois\\b': 'Si-roa',
    '\\bYuval Noah Harari\\b': 'Giu-van Nô-a Ha-ra-ri',
    '\\bHarari\\b': 'Ha-ra-ri',
    '\\bDarwin\\b': 'Đác-uyn',
    '\\bNewton\\b': 'Niu-tơn',
    '\\bEinstein\\b': 'Anh-xtanh',
    '\\bAristotle\\b': 'A-ri-xtốt',
    '\\bSocrates\\b': 'Xô-crát',
    '\\bPlato\\b': 'Pla-tông',
    '\\bHomo sapiens\\b': 'Hô-mô sa-pi-en',
    '\\bNeanderthal\\b': 'Nê-an-đơ-than',
    '\\bsmartphone\\b': 'điện thoại thông minh',
    '\\bpodcast\\b': 'pót-cát',
    '\\bvideo\\b': 'vi-đê-ô',
    '\\bemail\\b': 'i-meo',
    '\\binternet\\b': 'in-tơ-nét',
    '\\bwifi\\b': 'oai-phai',
    '\\bQ1\\b': 'quy một',
    '\\bWord\\b': 'Guốc',
    '\\bExcel\\b': 'Ếch-xen',
    '\\bslide\\b': 'xờ-lai',
    '\\bhighlight\\b': 'hai-lai',
    '\\bdeadline\\b': 'đét-lai',
    '\\blaptop\\b': 'láp-tóp',
    '\\bTikTok\\b': 'Tích-tốc',
    '\\bYouTube\\b': 'Diu-túp',
    '\\bShopee\\b': 'Sóp-pi',
    '\\bblog\\b': 'bờ-lốc',
    '\\bweb\\b': 'uép',
}


def _num_to_vi(n: int) -> str:
    if n < 0:
        return "âm " + _num_to_vi(-n)
    if n < 10:
        return _VI_ONES[n]
    if n < 20:
        return "mười" if n == 10 else ("mười lăm" if n == 15 else "mười " + _VI_ONES[n % 10])
    if n < 100:
        tens, units = divmod(n, 10)
        t_str = (_VI_ONES[tens] + " mươi") if tens > 1 else "mười"
        if units == 0:
            return t_str
        if units == 1:
            return t_str + (" mốt" if tens > 1 else " một")
        if units == 4:
            return t_str + " tư"
        if units == 5:
            return t_str + " lăm"
        return f"{t_str} {_VI_ONES[units]}"
    if n < 1000:
        h, rem = divmod(n, 100)
        h_str = f"{_VI_ONES[h]} trăm"
        if rem == 0:
            return h_str
        return f"{h_str} lẻ {_VI_ONES[rem]}" if rem < 10 else f"{h_str} {_num_to_vi(rem)}"
    if n < 1_000_000:
        th, rem = divmod(n, 1000)
        th_str = f"{_num_to_vi(th)} nghìn"
        if rem == 0:
            return th_str
        if rem < 10:
            return f"{th_str} không trăm lẻ {_VI_ONES[rem]}"
        if rem < 100:
            return f"{th_str} không trăm {_num_to_vi(rem)}"
        return f"{th_str} {_num_to_vi(rem)}"
    if n < 1_000_000_000:
        m, rem = divmod(n, 1_000_000)
        m_str = f"{_num_to_vi(m)} triệu"
        return m_str if rem == 0 else f"{m_str} {_num_to_vi(rem)}"
    return str(n)


def _strip_inter_letter_hyphens(text: str) -> str:
    """Replace syllable-joining hyphens (e.g. 'vi-đê-ô') with spaces so OmniVoice never inserts dash pauses."""
    res = re.sub(r"(?<=[^\W\d_])-(?=[^\W\d_])", " ", text or "")
    return re.sub(r"\s+", " ", res).strip()


def _normalize_vi_tts_text(text: str) -> str:
    """Sanitize pause tags, numbers, and loanwords for Vietnamese OmniVoice synthesis only."""
    try:
        from vn_text_normalizer import normalize_for_tts
        norm = _strip_inter_letter_hyphens(normalize_for_tts(text or ""))
        return norm or text
    except ImportError:
        pass
    res = re.sub(r"\[pause:[^\]]+\]", " , ", text or "", flags=re.IGNORECASE)
    for pat, repl in _VI_LOANWORD_MAP.items():
        res = re.sub(pat, repl, res, flags=re.IGNORECASE)
    res = re.sub(r"(Năm|năm)\s+(\d{4})\b", lambda m: f"{m.group(1)} {_num_to_vi(int(m.group(2)))}", res)
    res = re.sub(r"\b(\d+)%", lambda m: f"{_num_to_vi(int(m.group(1)))} phần trăm", res)
    res = re.sub(r"\b\d{1,3}(?:\.\d{3})+\b", lambda m: _num_to_vi(int(m.group(0).replace(".", ""))), res)
    res = re.sub(r"\b(\d+),(\d+)\b", lambda m: f"{_num_to_vi(int(m.group(1)))} phẩy {_num_to_vi(int(m.group(2)))}", res)
    res = re.sub(r"\b\d+\b", lambda m: _num_to_vi(int(m.group(0))) if len(m.group(0)) <= 9 else m.group(0), res)
    res = res.replace("...", ",").replace("…", ",").replace("—", ",").replace("–", ",").replace(":", ",").replace(";", ",")
    res = re.sub(r",\s*,", ",", res)
    res = _strip_inter_letter_hyphens(res)
    return res or text


def _extract_word_timestamps_acoustic(w, text, sr=SR):
    """Computes word-level timestamps from the waveform energy envelope.

    Detects voiced syllable energy nuclei and distributes word boundaries across
    actual acoustic speech activity rather than naive character-count interpolation.
    """
    import numpy as np
    clean_text = re.sub(r"\[pause:[^\]]+\]", " ", text or "")
    words = [tok for tok in clean_text.split() if tok.strip()]
    w = np.asarray(w, dtype=np.float32).reshape(-1)
    total_dur = len(w) / float(sr) if len(w) > 0 else 0.0
    if not words or total_dur <= 0.0:
        return []
    # Compute 10ms RMS energy envelope
    hop = max(1, sr // 100)
    n_frames = len(w) // hop
    if n_frames < len(words):
        step = total_dur / len(words)
        return [
            {"word": wd, "start": round(idx * step, 3), "end": round((idx + 1) * step, 3)}
            for idx, wd in enumerate(words)
        ]
    trimmed = w[: n_frames * hop].reshape(n_frames, hop)
    rms = np.sqrt(np.mean(trimmed * trimmed, axis=1) + 1e-12)
    # Cumulative acoustic energy distribution (weighted 70% energy + 30% time floor)
    norm_rms = rms / (np.max(rms) + 1e-9)
    weights = 0.7 * (norm_rms > 0.04).astype(np.float32) * (norm_rms + 0.1) + 0.3
    cum_energy = np.concatenate([[0.0], np.cumsum(weights)])
    total_energy = float(cum_energy[-1])
    # Weight each word by phonetic length
    word_weights = [max(1, len(re.sub(r"[^A-Za-zÀ-ỹ0-9]", "", wd))) for wd in words]
    total_w = float(sum(word_weights))
    timestamps = []
    used_w = 0.0
    prev_end = 0.0
    for wd, ww in zip(words, word_weights, strict=True):
        e_start = (used_w / total_w) * total_energy
        used_w += ww
        e_end = (used_w / total_w) * total_energy
        f_start = int(np.searchsorted(cum_energy, e_start, side="left"))
        f_end = int(np.searchsorted(cum_energy, e_end, side="left"))
        t0 = round(min(total_dur, max(prev_end, f_start * hop / float(sr))), 3)
        t1 = round(min(total_dur, max(t0 + 0.01, f_end * hop / float(sr))), 3)
        if t1 < t0:
            t1 = t0
        prev_end = t1
        timestamps.append({"word": wd, "start": t0, "end": t1})
    return timestamps


def _strip_leading_prompt_bleed(w, sr=SR):
    """Strip residual voice-prompt boundary click or syllable bleed (<=240ms) + dead silence (>=120ms) at utterance start."""
    import numpy as np
    hop = max(1, sr // 100)
    nf = len(w) // hop
    if nf < 45:
        return w
    rms = np.sqrt(np.mean(w[: nf * hop].reshape(nf, hop) ** 2, axis=1))
    sample_idx = np.where(np.abs(w) >= 0.010)[0]
    if not len(sample_idx):
        return w
    b_start = int(sample_idx[0]) // hop
    if b_start > 25:
        return w
    for g_start in range(b_start + 1, min(b_start + 25, nf - 22)):
        if rms[g_start] < 0.011:
            s_candidates = np.where(rms[g_start:] >= 0.014)[0]
            if not len(s_candidates):
                return w
            s_start = g_start + int(s_candidates[0])
            if (s_start - g_start) >= 12:
                win = rms[s_start : min(nf, s_start + 25)]
                if int(np.sum(win >= 0.015)) >= 10:
                    cut = max(0, (s_start - 3) * hop)
                    return w[cut:]
    return w


def _utterance_acoustic_score(w, synth_text: str, sr: int = SR) -> tuple[bool, float]:
    """Verify trimmed Vietnamese waveform speaks expected syllables without mid-clause stalls."""
    import numpy as np
    w = np.asarray(w, dtype=np.float32).reshape(-1)
    if not w.size:
        return False, 0.0
    words = re.findall(r"[^\W\d_]+", synth_text or "")
    n_words = len(words)
    dur = len(w) / float(sr)
    if n_words <= 2:
        return dur >= 0.20, dur
    hop = max(1, sr // 100)
    nf = len(w) // hop
    if nf < 10:
        return False, 0.0
    rms = np.sqrt(np.mean(w[: nf * hop].reshape(nf, hop) ** 2, axis=1))
    voiced_s = float(np.sum(rms >= 0.008)) * (hop / float(sr))
    min_voiced = max(0.42, n_words * 0.142)
    v_idx = np.where(rms >= 0.008)[0]
    max_gap = float(np.max(np.diff(v_idx) - 1)) * (hop / float(sr)) if len(v_idx) > 1 else 0.0
    has_internal_punct = bool(re.search(r"[,.;:!?]", (synth_text or "").strip()[:-1]))
    gap_limit = 0.55 if has_internal_punct else 0.36
    ok = (voiced_s >= min_voiced) and (max_gap <= gap_limit)
    score = (voiced_s / max(1, n_words)) - max(0.0, max_gap - gap_limit)
    return ok, score


def _trim_silence(w, sr=SR, threshold=0.012, lead_ms=25, trail_ms=30, fade_ms=8):
    import numpy as np
    w = np.asarray(w, dtype=np.float32).reshape(-1)
    if not w.size:
        return w
    w = _strip_leading_prompt_bleed(w, sr=sr)
    idx = np.where(np.abs(w) >= threshold)[0]
    if not idx.size:
        return w
    soft_coda = np.where(np.abs(w[int(idx[-1]) : min(len(w), int(idx[-1]) + round(0.09 * sr))]) >= min(threshold, 0.006))[0]
    last_voiced = int(idx[-1]) + (int(soft_coda[-1]) if soft_coda.size else 0)
    lead = round(lead_ms * sr / 1000)
    trail = round(trail_ms * sr / 1000)
    start = max(0, int(idx[0]) - lead)
    end = min(len(w), last_voiced + 1 + trail)
    if start == 0 and end == len(w) and int(idx[0]) <= lead and len(w) - 1 - last_voiced <= trail:
        return w
    trimmed = w[start:end].copy()
    fade = min(round(fade_ms * sr / 1000), len(trimmed) // 4)
    fade_in = min(fade, int(idx[0]) - start)
    fade_out = min(fade, end - 1 - last_voiced)
    if fade_in > 1:
        trimmed[:fade_in] *= np.linspace(0.0, 1.0, fade_in, dtype=np.float32)
    if fade_out > 1:
        trimmed[-fade_out:] *= np.linspace(1.0, 0.0, fade_out, dtype=np.float32)
    return trimmed


def assemble_prepared(request_path, output_dir):
    """Assemble checked shard bytes on the GPU host without loading the TTS model."""
    import importlib.util
    import shutil
    import subprocess

    req = json.loads(Path(request_path).read_text())
    parent, output = Path(request_path).parent, Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    device = subprocess.check_output(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], text=True)
    if 'T4' not in device:
        raise RuntimeError('COLAB_GPU_REQUIRED: expected an actual NVIDIA T4')
    if req.get('worker_sha256') != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
        raise RuntimeError('Remote TTS worker checksum mismatch')
    targets = set()
    for item in req.get('support_files', []) + req['prepared_audio']:
        name = item['name']
        path = parent / name
        if (Path(name).name != name or path.is_symlink() or not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']):
            raise RuntimeError('Remote processing source checksum mismatch')
    for item in req['prepared_audio']:
        target = item['target']
        if (Path(target).name != target or target in targets
                or not (target.endswith('.wav') or target in {'tts-result.json', 'en-result.json', 'secondary-result.json'})):
            raise ValueError('Unsafe prepared audio target')
        targets.add(target)
        dest = output / target
        shutil.copyfile(parent / item['name'], dest)
        if target.endswith('.json'):
            meta = json.loads(dest.read_text())
            meta['request_id'] = req['request_id']
            dest.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    spec = importlib.util.spec_from_file_location('vp_media_packaging', parent / 'media_packaging.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.assemble(req, output, parent)
    with zipfile.ZipFile(output.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in output.iterdir():
            if path.suffix in {'.json', '.wav', '.srt'}:
                archive.write(path, path.name)


def run(request_path, output_dir):
    if json.loads(Path(request_path).read_text()).get('prepared_audio'):
        return assemble_prepared(request_path, output_dir)
    import numpy as np
    import soundfile as sf
    import torch
    from huggingface_hub import snapshot_download
    from omnivoice import OmniVoice
    from scipy.signal import resample_poly
    global _MODEL, _MODEL_KEY, _PROMPTS
    req = json.loads(Path(request_path).read_text())
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    if not torch.cuda.is_available() or 'T4' not in torch.cuda.get_device_name(0):
        raise RuntimeError('COLAB_GPU_REQUIRED: expected an actual NVIDIA T4')
    start = time.monotonic()
    raw = output.parent.parent / 'audio-cache'
    raw.mkdir(exist_ok=True)
    waves, stats = {}, []
    worker_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if req.get('worker_sha256') and req['worker_sha256'] != worker_hash:
        raise RuntimeError('Remote TTS worker checksum mismatch')
    for support in req.get('support_files', []):
        path = Path(request_path).parent / support['name']
        if Path(support['name']).name != support['name'] or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != support['sha256']:
            raise RuntimeError('Remote processing source checksum mismatch')
    for lang in sorted(req['profiles']):
        spec = req['models'][lang]
        profile = req['profiles'][lang]
        ref = Path(profile['remote_wav'])
        if hashlib.sha256(ref.read_bytes()).hexdigest() != profile['sha256']:
            raise RuntimeError('Voice reference checksum mismatch')
        model_key = (spec['id'], spec['revision'])
        pending = []
        for i, item in enumerate(req['items']):
            if item['language'] != lang:
                continue
            identity = dict(item=item, model=spec, profile={k: v for k, v in profile.items() if k != 'remote_wav'},
                            seed=req['seed'], steps=req['num_step'], worker=worker_hash)
            key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
            cached = raw / (key + '.wav')
            if cached.is_file():
                w, sr = sf.read(cached, dtype='float32')
                if sr != SR or not w.size or not np.isfinite(w).all():
                    raise RuntimeError('Invalid cached waveform')
                waves[i] = w
            else:
                pending.append((i, item, cached))
        if not pending:
            continue
        if _MODEL_KEY != model_key:
            _MODEL = None
            _PROMPTS = {}
            gc.collect()
            torch.cuda.empty_cache()
            local = snapshot_download(spec['id'], revision=spec['revision'])
            _MODEL = OmniVoice.from_pretrained(local, device_map='cuda:0', dtype=torch.float16)
            _MODEL_KEY = model_key
        prompt_key = (profile['sha256'], profile['reference_text'])
        if prompt_key not in _PROMPTS:
            _PROMPTS[prompt_key] = _MODEL.create_voice_clone_prompt(ref_audio=str(ref), ref_text=profile['reference_text'])
        prompt = _PROMPTS[prompt_key]
        # Group retakes so their random seeds differ and their cache cannot collide.
        for take in sorted({x[1]['retake'] for x in pending}):
            group = [x for x in pending if x[1]['retake'] == take]
            size = req['batch_size']
            offset = 0
            while offset < len(group):
                batch = group[offset:offset + size]
                torch.manual_seed(req['seed'] + take)
                try:
                    synth_texts = [
                        _normalize_vi_tts_text(x[1]['text']) if lang == 'vi' else x[1]['text']
                        for x in batch
                    ]
                    generated = _MODEL.generate(
                        text=synth_texts, language=[lang] * len(batch),
                        voice_clone_prompt=[prompt] * len(batch),
                        speed=[x[1]['speed'] / profile['source_speed'] for x in batch],
                        num_step=req['num_step'])
                except torch.cuda.OutOfMemoryError as err:
                    if size == 1:
                        raise RuntimeError('COLAB_GPU_OOM: exhausted bounded batch reduction') from err
                    size = max(1, size // 2)
                    gc.collect()
                    torch.cuda.empty_cache()
                    continue
                if len(generated) != len(batch):
                    raise RuntimeError('Model returned incomplete batch')
                def _postprocess_wave(raw_w):
                    arr = np.asarray(raw_w, dtype=np.float32).reshape(-1)
                    if not arr.size or not np.isfinite(arr).all() or np.max(np.abs(arr)) < 1e-5:
                        raise RuntimeError('Model returned empty/nonfinite/silent audio')
                    arr = resample_poly(arr, 2, 1).astype(np.float32)  # OmniVoice: 24 kHz
                    pk = float(np.max(np.abs(arr)))
                    if pk > .89:
                        arr *= .89 / pk
                    return _trim_silence(arr, sr=SR)

                for (i, _item, cached), w_raw, s_txt in zip(batch, generated, synth_texts, strict=False):
                    w = _postprocess_wave(w_raw)
                    if lang == 'vi':
                        ok, best_score = _utterance_acoustic_score(w, s_txt, sr=SR)
                        if not ok:
                            best_w = w
                            for attempt in (1, 2):
                                torch.manual_seed(req['seed'] + take + attempt * 31)
                                retry_gen = _MODEL.generate(
                                    text=[s_txt],
                                    language=[lang],
                                    voice_clone_prompt=[prompt],
                                    speed=[_item['speed'] / profile['source_speed']],
                                    num_step=req['num_step'],
                                )
                                if retry_gen:
                                    cand_w = _postprocess_wave(retry_gen[0])
                                    cand_ok, cand_score = _utterance_acoustic_score(cand_w, s_txt, sr=SR)
                                    if cand_ok:
                                        best_w = cand_w
                                        break
                                    if cand_score > best_score:
                                        best_w = cand_w
                                        best_score = cand_score
                            w = best_w
                    tmp = cached.with_suffix('.tmp.wav')
                    sf.write(tmp, w, SR, subtype='PCM_16')
                    tmp.replace(cached)
                    waves[i] = sf.read(cached, dtype='float32')[0]
                stats.append(dict(language=lang, batch_size=len(batch), retake=take))
                offset += len(batch)
    def save(name, pieces, pause):
        w = np.concatenate(pieces)
        content = len(w) / SR
        w = np.concatenate([w, np.zeros(round(pause * SR), dtype=np.float32)])
        sf.write(output / name, w, SR, subtype='PCM_16')
        return content
    segments, spans = [], []
    for n, part in enumerate(req['segments']):
        pieces = []
        for i in part['items']:
            if pieces:
                pieces.append(np.zeros(round(req['span_gap'] * SR), dtype=np.float32))
            pieces.append(waves[i])
            item = req['items'][i]
            if item['language'] == 'en':
                spans.append(dict(scene_id=part['scene_id'], text=item['text'], voice=req['profiles']['en']['voice'],
                                  engine='omnivoice', seed=req['seed'] + item['retake'], rate=item['speed'], retake=item['retake'], duration=len(waves[i]) / SR))
        name = f'segment-{n:04d}.wav'
        duration = save(name, pieces, part['pause'])
        combined_voiced = np.concatenate(pieces) if pieces else np.zeros(0, dtype=np.float32)
        word_ts = _extract_word_timestamps_acoustic(combined_voiced, part['text'], sr=SR)
        segments.append(dict(scene_id=part['scene_id'], text=part['text'], path=name, content_duration=duration, word_timestamps=word_ts))
    engine = dict(backend='colab-omnivoice', precision='float16', device=torch.cuda.get_device_name(0),
                  models=req['models'], batch_size=req['batch_size'], num_step=req['num_step'])
    result = dict(request_id=req['request_id'], voice=req['profiles'][req.get('primary_language','vi')]['voice'], engine=engine,
                  segments=segments, english_spans=spans, batches=stats,
                  voice_references={k: dict(voice=v['voice'], sha256=v['sha256'], source_speed=v['source_speed']) for k,v in req['profiles'].items()}, elapsed_seconds=time.monotonic() - start)
    (output / 'tts-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    if req['english']:
        scenes = []
        for sc in req['english']:
            name = f'en-{sc["scene_id"]}.wav'
            duration = save(name, [waves[sc['item']]], sc['pause'])
            scenes.append(dict(scene_id=sc['scene_id'], path=name, content_duration=duration,
                               word_timestamps=_extract_word_timestamps_acoustic(waves[sc['item']], req['items'][sc['item']]['text'], sr=SR),
                               take=dict(retake=sc['retake'], seed=req['seed'] + sc['retake'])))
        en = dict(request_id=req['request_id'], voice=req['profiles']['en']['voice'], engine='colab-omnivoice', scenes=scenes)
        (output / 'en-result.json').write_text(json.dumps(en, ensure_ascii=False, indent=2))
    if req.get('secondary'):
        extra = []
        for n, part in enumerate(req['secondary']):
            name = f'secondary-{n:04d}.wav'
            duration = save(name, [waves[i] for i in part['items']], part['pause'])
            extra.append(dict(scene_id=part['scene_id'], language=part['language'], text=part['text'], path=name, content_duration=duration,
                              word_timestamps=_extract_word_timestamps_acoustic(np.concatenate([waves[i] for i in part['items']]), part['text'], sr=SR)))
        (output / 'secondary-result.json').write_text(json.dumps({'request_id': req['request_id'], 'segments': extra}, ensure_ascii=False, indent=2))
    if req.get('spinoff_hooks'):
        hooks = []
        for index, hook in enumerate(req['spinoff_hooks']):
            name = f'spinoff-hook-{index:02d}.wav'
            duration = save(name, [waves[hook['item']]], 0)
            if duration > 3:
                raise ValueError('OMNI_HOOK_DURATION: independent hook exceeds 3 seconds')
            hooks.append(dict(id=hook['id'], text=hook['text'], path=name, duration=duration,
                              word_timestamps=_extract_word_timestamps_acoustic(waves[hook['item']], hook['text'], sr=SR)))
        result['spinoff_hooks'] = hooks
        (output / 'tts-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    if req.get('assemble'):
        import importlib.util
        module_path = Path(request_path).parent / 'media_packaging.py'
        spec = importlib.util.spec_from_file_location('vp_media_packaging', module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.assemble(req, output, Path(request_path).parent)
    archive = output.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in output.iterdir():
            if path.suffix in (('.json', '.wav', '.srt') if req.get('assemble') else ('.json', '.wav')):
                z.write(path, path.name)
    print(json.dumps({'request_id': req['request_id'], 'archive': str(archive), 'elapsed_seconds': result['elapsed_seconds']}), flush=True)
