#!/usr/bin/env python3
"""Video Pilot — OmniVoice Audition Runner & Voice Cloner.

Synthesizes and masters a real 15–25s human voice-cloned audition sample (sample.wav)
for any channel using Google Colab T4 OmniVoice (kjanh/KhanhTTS-OmniVoice) with
automatic failover across candidate accounts and cadence pauses (0.10s/0.18s/0.20s),
mastered to -14.0 LUFS / -1.5 dBTP (48kHz mono PCM16).
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import logging
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import audio_processing as ap
from colab_bridge.client import Client, ColabError
from colab_bridge.protocol import build_request
from tools.vn_text_normalizer import normalize_for_tts

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("audition_channel_voice")

CANDIDATE_ACCOUNTS: List[str] = [
    "account-01",
    "account-03",
    "account-04",
    "account-05",
    "account-06",
    "account-07",
    "account-08",
    "account-09",
    "account-10",
    "account-11",
    "account-12",
    "account-13",
    "account-14",
    "account-15",
    "account-16",
    "account-17",
    "account-18",
    "account-19",
    "account-20",
]

SENTENCE_RE = re.compile(r'(?<=[.!?…;])\s+|(?<=[.!?…;]["\'”’])\s+')
SENTENCE_END_CHARS = ('.', '!', '?', '…', ';', ':', '”', '"', '’', "'")

# Canonical full 5-sentence audition scripts (~18-22s duration, >= 60 words) for all channels
AUDITION_SCRIPTS: Dict[str, str] = {
    "ai_binh_dan": (
        "Đừng vội đặt bút ký hợp đồng, khi bạn chưa nhờ AI kiểm tra. "
        "Nhưng điều bất ngờ là, chỉ mất ba mươi giây để phát hiện các điều khoản gài bẫy. "
        "Đầu tiên bạn tải hợp đồng lên và dán câu lệnh rà soát rủi ro pháp lý. "
        "Khung lệnh thông minh sẽ phân tích từng câu chữ, và khoanh đỏ các điểm bất lợi. "
        "Tiếp theo, hệ thống tự động đối chiếu các mốc phạt, và gợi ý điều khoản sửa đổi an toàn."
    ),
    "co_the_ke": (
        "Nếu bạn cúi đầu nhìn điện thoại, cổ bạn phải gánh hai mươi bảy cân. "
        "Nhưng điều bất ngờ là, áp lực này tương đương bạn cõng một đứa trẻ tám tuổi trên vai suốt cả ngày. "
        "Khi đầu nghiêng sáu mươi độ, các đốt sống cổ lập tức phát tín hiệu đau buốt vì cơ bắp bị căng rách. "
        "Lượng máu dẫn lên não sụt giảm, khiến bạn nhanh chóng hoa mắt và giảm hiệu suất làm việc. "
        "Chỉ cần nâng điện thoại ngang tầm mắt là bạn đã cứu chiếc cổ của mình."
    ),
    "ho_so_ky_la": (
        "Bạn có biết bí mật rùng rợn về con tàu ma trôi dạt không một bóng người? "
        "Giữa đại dương mênh mông, con tàu Ma-ri Xê-lét được tìm thấy hoàn toàn nguyên vẹn. "
        "Thế nhưng mười người trên tàu đã biến mất mà không để lại bất kỳ dấu vết nào. "
        "Trên bàn ăn, thức ăn vẫn còn nguyên vẹn và ấm nóng. "
        "Quần áo của thủy thủ đoàn được xếp gọn gàng trong các khoang ngủ."
    ),
    "nao_luoi": (
        "Vì sao bạn thức tới hai giờ sáng dù mắt đã díp lại? "
        "Thế nhưng ngón tay vẫn tiếp tục lướt màn hình trong vô thức. "
        "Não bạn không hề muốn thức khuya để xem clip ngắn. "
        "Thực chất nó đang muốn đòi lại quyền kiểm soát cuộc sống. "
        "Khoa học gọi hiện tượng này là sự trì hoãn giấc ngủ để trả thù."
    ),
    "su_ke_lai": (
        "Năm chín trăm ba mươi tám, bạn có biết bí mật nào giúp Ngô Quyền thắng lớn? "
        "Một đạo quân phương Bắc hùng hậu vượt biển tiến vào nước ta. "
        "Nhưng điều bất ngờ là Ngô Quyền không hề chọn cách nghênh chiến trực diện ngoài biển. "
        "Ông nhận ra con sông Bạch Đằng có một quy luật tự nhiên vô cùng đặc biệt. "
        "Đó chính là biên độ thủy triều lên xuống chênh lệch tới gần bốn mét."
    ),
    "thuong_cho_kheo": (
        "Bạn đừng bao giờ trả lời câu này khi người yêu bảo em không sao. "
        "Bản năng của chúng ta thường là thở phào nhẹ nhõm rồi quay đi. "
        "Nhưng điều bất ngờ là câu nói đó chính là một tín hiệu cầu cứu. "
        "Người ấy không hề giận dỗi vô cớ, mà đang cảm thấy vô cùng cô đơn. "
        "Nếu bạn vội đáp vậy thì tốt rồi, khoảng cách giữa hai người sẽ lớn dần."
    ),
    "tui_tien": (
        "Ly trà sữa ba mươi lăm nghìn, bạn nghĩ chủ quán thật ra lời bao nhiêu? "
        "Nhưng con số thực tế trong sổ kế toán sẽ khiến bạn giật mình. "
        "Nhiều người nghĩ bán một ly trà sữa là siêu lợi nhuận. "
        "Thực tế tiền nguyên liệu gồm cốt trà, bột sữa và trân châu chỉ tốn sáu nghìn đồng. "
        "Chiếc ly nhựa, màng ép và ống hút cộng thêm một nghìn đồng nữa."
    ),
    "ua_sao_vay": (
        "Ủa, sao trong phòng đông người mà muỗi chỉ đốt mỗi mình bạn vậy? "
        "Ai cũng nghĩ do máu ngọt. "
        "Nhưng sự thật khoa học lại hoàn toàn khác. "
        "Muỗi bị thu hút bởi khí thở và lượng nhiệt tỏa ra từ cơ thể bạn. "
        "Người có thân nhiệt cao hoặc vừa vận động sẽ thành mục tiêu số một."
    ),
}


def resolve_channel_ids(raw_id: str) -> Tuple[str, str]:
    """Normalize user channel identifier into (channel_id, channel_slug)."""
    clean = raw_id.strip()
    if clean.startswith("channel-"):
        clean = clean[len("channel-"):]
    if clean.startswith("ch_"):
        clean = clean[len("ch_"):]
    channel_id = clean.replace("-", "_")
    channel_slug = clean.replace("_", "-")
    return channel_id, channel_slug


def find_voice_profile(sys_dir: Path, channel_id: str, channel_slug: str) -> Tuple[Path, Dict[str, Any]]:
    """Locate the channel's human voice profile or fall back to viet_narrator."""
    candidates = [
        sys_dir / f"assets/voices/ch_{channel_id}/profile.json",
        sys_dir / f"assets/voices/{channel_id}/profile.json",
        Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/assets/voices/ch_{channel_id}/profile.json"),
        Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/assets/voices/{channel_id}/profile.json"),
    ]
    for p in candidates:
        if p.is_file():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                ref_wav = p.parent / data.get("reference_wav", "")
                if ref_wav.is_file():
                    logger.info(f"Using channel voice profile: {p}")
                    return p, data
            except Exception as ex:
                logger.warning(f"Failed parsing candidate profile {p}: {ex}")

    fallback = sys_dir / "assets/voices/viet_narrator/profile.json"
    if not fallback.is_file():
        fallback = Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/assets/voices/viet_narrator/profile.json")
    logger.info(f"Using fallback canonical narrator profile: {fallback}")
    return fallback, json.loads(fallback.read_text(encoding="utf-8"))


def find_week1_content(sys_dir: Path, channel_slug: str, explicit_path: Optional[str] = None) -> Path:
    """Find Week-1 content.json for the channel."""
    if explicit_path and Path(explicit_path).is_file():
        return Path(explicit_path)

    candidates = [
        Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/runs/{channel_slug}-week1-9x16/content.json"),
        Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/runs/{channel_slug}-week1-16x9/content.json"),
        Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/runs/{channel_slug}-9x16-001/content.json"),
        sys_dir / "runs" / f"{channel_slug}-week1-9x16/content.json",
        sys_dir / "runs" / f"{channel_slug}-week1-16x9/content.json",
        sys_dir / "runs" / f"{channel_slug}-9x16-001/content.json",
    ]
    for c in candidates:
        if c.is_file():
            logger.info(f"Found week-1 content file: {c}")
            return c

    ch_dir = Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}")
    if ch_dir.is_dir():
        matches = list(ch_dir.glob("sys/runs/*week1*/content.json"))
        if matches:
            logger.info(f"Found globbed week-1 content file: {matches[0]}")
            return matches[0]
        all_contents = list(ch_dir.glob("sys/runs/*/content.json"))
        if all_contents:
            logger.info(f"Found fallback content file: {all_contents[0]}")
            return all_contents[0]

    raise FileNotFoundError(f"Cannot find week1 content.json for channel {channel_slug}")


def split_long_sentence_at_middle_comma(sentence: str) -> List[str]:
    """If sentence has > 18 words and contains commas, split at the comma closest to the middle.

    Ensures sub-clauses stay within the optimal 6..16 word sweet spot for OmniVoice attention.
    """
    words = sentence.split()
    if len(words) <= 18 or "," not in sentence:
        return [sentence]

    comma_indices = [m.start() for m in re.finditer(r",", sentence)]
    if not comma_indices:
        return [sentence]

    target_mid = len(words) / 2.0
    best_idx = -1
    best_diff = float("inf")

    for idx in comma_indices:
        before = sentence[:idx].strip()
        after = sentence[idx + 1:].strip()
        w1 = len(before.split())
        w2 = len(after.split())
        if w1 == 0 or w2 == 0:
            continue
        diff = abs(w1 - target_mid)
        if diff < best_diff:
            best_diff = diff
            best_idx = idx

    if best_idx == -1:
        return [sentence]

    part1 = sentence[:best_idx].strip()
    part2 = sentence[best_idx + 1:].strip()

    res = [part1]
    if len(part2.split()) > 18 and "," in part2:
        res.extend(split_long_sentence_at_middle_comma(part2))
    else:
        res.append(part2)

    return res


def split_into_clauses(text: str) -> List[str]:
    """Split narration into natural spoken clauses/sentences for OmniVoice.

    1. First split on sentence boundaries (.?!;).
    2. If a sentence has <= 18 words, keep it intact as a single clause (never split on commas).
    3. If a sentence has > 18 words and contains a comma, split at the comma closest to the middle
       so each sub-clause stays in the optimal 6..16 word sweet spot for OmniVoice attention.
    """
    clean = text.strip()
    if not clean:
        return []

    raw_sentences = [s.strip() for s in SENTENCE_RE.split(clean) if s.strip()]
    clauses: List[str] = []
    for s in raw_sentences:
        clauses.extend(split_long_sentence_at_middle_comma(s))

    return [c for c in clauses if c]


def select_audition_scenes(
    scenes: List[Dict[str, Any]], target_sentences: int = 5, min_scenes: int = 2
) -> List[Dict[str, Any]]:
    """Select the first N scenes needed to form a balanced ~18–25s (>= 5 sentences) audition sample."""
    selected: List[Dict[str, Any]] = []
    total_sents = 0
    for sc in scenes:
        selected.append(sc)
        narr = sc.get("narration", "").strip()
        sents = [s for s in SENTENCE_RE.split(narr) if s.strip()]
        total_sents += len(sents)
        if total_sents >= target_sentences and len(selected) >= min_scenes:
            break
    return selected


def concat_mono_pcm16_wavs(wav_paths: List[Path], out_wav: Path) -> None:
    """Concatenate 48kHz mono PCM16 WAV files without transcoding loss."""
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_wav), "wb") as outfile:
        outfile.setnchannels(1)
        outfile.setsampwidth(2)
        outfile.setframerate(48000)
        for p in wav_paths:
            with wave.open(str(p), "rb") as infile:
                if (infile.getnchannels(), infile.getsampwidth(), infile.getframerate()) != (1, 2, 48000):
                    # Ensure audio format strictly matches 48kHz mono PCM16
                    tmp_conv = p.with_name(f"conv_{p.name}")
                    cmd = [
                        "ffmpeg", "-y", "-i", str(p),
                        "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le",
                        str(tmp_conv)
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    with wave.open(str(tmp_conv), "rb") as cin:
                        outfile.writeframes(cin.readframes(cin.getnframes()))
                    tmp_conv.unlink(missing_ok=True)
                else:
                    outfile.writeframes(infile.readframes(infile.getnframes()))


def measure_audio(wav_path: Path) -> Tuple[float, float, float, int]:
    """Measure duration, integrated LUFS, True Peak dBTP, and RMS amplitude."""
    with wave.open(str(wav_path), "rb") as w:
        frames = w.getnframes()
        sr = w.getframerate()
        raw_bytes = w.readframes(frames)
    dur = frames / sr

    arr = np.frombuffer(raw_bytes, dtype=np.int16)
    rms_val = int(np.sqrt(np.mean(arr.astype(np.float64) ** 2))) if len(arr) > 0 else 0

    cmd = [
        "ffmpeg", "-v", "info", "-i", str(wav_path),
        "-af", "loudnorm=print_format=json",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    m_json: Dict[str, Any] = {}
    try:
        start_idx = res.stderr.rindex("{")
        end_idx = res.stderr.rindex("}") + 1
        m_json = json.loads(res.stderr[start_idx:end_idx])
    except Exception:
        pass

    lufs = float(m_json.get("input_i", -11.0))
    tp = float(m_json.get("input_tp", -1.0))
    return dur, lufs, tp, rms_val


def audition_channel(
    channel_arg: str,
    target_account: Optional[str] = None,
    explicit_content: Optional[str] = None,
    retake: int = 0,
    target_lufs: Optional[float] = None,
    true_peak_db: Optional[float] = None,
) -> Dict[str, Any]:
    """Run full audition voice cloning, mastering, and report generation."""
    channel_id, channel_slug = resolve_channel_ids(channel_arg)
    logger.info(f"=== Auditioning Voice for Channel '{channel_id}' (slug: {channel_slug}) ===")

    # 1. Voice profile resolution
    profile_path, profile = find_voice_profile(SYS_DIR, channel_id, channel_slug)
    voice_name = profile.get("voice", "VietNarrator")

    # Ensure profile and reference are present inside SYS_DIR/assets/voices/ch_<channel_id>
    target_voice_dir = SYS_DIR / f"assets/voices/ch_{channel_id}"
    target_voice_dir.mkdir(parents=True, exist_ok=True)

    local_profile_path = target_voice_dir / "profile.json"
    ref_wav_name = profile.get("reference_wav", "reference.wav")
    src_ref_wav = profile_path.parent / ref_wav_name

    if profile_path.resolve() != local_profile_path.resolve():
        target_voice_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(profile_path, local_profile_path)
        if src_ref_wav.is_file():
            shutil.copy2(src_ref_wav, target_voice_dir / ref_wav_name)

    # 2. Week-1 Content resolution & Scene selection (balanced ~18–25s, >= 5 sentences)
    scenes: List[Dict[str, Any]] = []
    try:
        content_path = find_week1_content(SYS_DIR, channel_slug, explicit_content)
        content = json.loads(content_path.read_text(encoding="utf-8"))
        scenes = content.get("scenes", [])
    except Exception as ex_content:
        logger.warning(f"Could not load week1 content for {channel_slug}: {ex_content}. Using AUDITION_SCRIPTS fallback.")

    if len(scenes) >= 2:
        selected_scenes = select_audition_scenes(scenes, target_sentences=5, min_scenes=2)
    else:
        # Fallback to canonical AUDITION_SCRIPTS
        script_text = AUDITION_SCRIPTS.get(channel_id, AUDITION_SCRIPTS.get("ai_binh_dan", ""))
        sents = [s.strip() for s in SENTENCE_RE.split(script_text) if s.strip()]
        selected_scenes = [
            {"id": "SC01", "narration": sents[0] if sents else script_text, "tone": "narrative_warm"},
            {"id": "SC02", "narration": " ".join(sents[1:3]) if len(sents) >= 3 else (sents[1] if len(sents) > 1 else ""), "tone": "narrative_warm"},
            {"id": "SC03", "narration": " ".join(sents[3:]) if len(sents) >= 4 else "", "tone": "narrative_warm"},
        ]
        selected_scenes = [s for s in selected_scenes if s["narration"]]

    # 3. Vietnamese text normalization & scenes plan
    scenes_plan = []
    for sc_idx, sc in enumerate(selected_scenes):
        sc_id = sc.get("id", f"SC{sc_idx + 1:02d}")
        sc_raw = sc.get("narration", "").strip()
        sc_norm = normalize_for_tts(sc_raw)
        sc_clauses = split_into_clauses(sc_norm)
        if not sc_clauses:
            continue
        # Snappy short-video cadence pauses: 0.10s if split at comma, 0.18s between sentences, 0.20s scene tail
        gaps = [0.10 if not c.endswith(SENTENCE_END_CHARS) else 0.18 for c in sc_clauses[:-1]]
        scenes_plan.append({
            "scene_id": sc_id,
            "texts": sc_clauses,
            "gaps": gaps,
            "tail": 0.20,
            "tone": None,
            "retake": int(retake),
        })

    logger.info(f"Built scenes plan with {len(scenes_plan)} scenes:")
    for sp in scenes_plan:
        logger.info(f"  {sp['scene_id']}: texts={sp['texts']} gaps={sp['gaps']} tail={sp['tail']}")

    # 4. Colab Configuration & Request
    base_cfg_path = SYS_DIR / "config.json"
    cfg: Dict[str, Any] = json.loads(base_cfg_path.read_text(encoding="utf-8")) if base_cfg_path.is_file() else {}

    rel_profile = str(local_profile_path.relative_to(SYS_DIR))
    cfg["voices"] = {"vi": rel_profile, "en": rel_profile}
    cfg["tts_voice"] = voice_name
    cfg["en_voice"] = voice_name
    cfg["tts_speed"] = float(profile.get("recommended_speed", profile.get("source_speed", 1.0)))
    target_lufs_val = float(target_lufs) if target_lufs is not None else float(profile.get("audio_lufs", -14.0))
    true_peak_val = float(true_peak_db) if true_peak_db is not None else float(profile.get("audio_peak_db", -1.5))
    voice_chain_val = profile.get("audio_voice_chain") or ap.VOICE_CHAIN

    cfg["audio_lufs"] = target_lufs_val
    cfg["audio_peak_db"] = true_peak_val
    cfg["audio_voice_chain"] = voice_chain_val

    cfg.setdefault("colab_tts", {})
    cfg["colab_tts"]["session"] = "video-pilot-tts"
    cfg["colab_tts"]["_session_explicit"] = True
    cfg["colab_tts"]["batch_size"] = 1
    cfg["colab_tts"]["num_step"] = 32
    cfg["colab_tts"]["timeout_seconds"] = 1800
    cfg["colab_tts"]["models"] = {
        "vi": {
            "id": "kjanh/KhanhTTS-OmniVoice",
            "revision": "20d056b8ea5d8d578b4cbaf1f703012fa3798a84",
        },
        "en": {
            "id": "kjanh/KhanhTTS-OmniVoice",
            "revision": "20d056b8ea5d8d578b4cbaf1f703012fa3798a84",
        },
    }

    request = build_request(SYS_DIR, cfg, scenes_plan, assemble=False)
    logger.info(f"Built Colab TTS request ID: {request['request_id']} with {len(request.get('items', []))} items")

    # 5. Colab Pool Synthesis with Automatic Failover
    accounts_to_try: List[str] = []
    if target_account:
        accounts_to_try.append(target_account)
    for a in CANDIDATE_ACCOUNTS:
        if a not in accounts_to_try:
            accounts_to_try.append(a)

    account_used: Optional[str] = None
    staging_base = Path(tempfile.mkdtemp(prefix="audition_staging_"))

    try:
        for acc in accounts_to_try:
            logger.info(f"Trying Colab synthesis on {acc}...")
            acc_cfg = copy.deepcopy(cfg)
            acc_cfg["colab_tts"]["account"] = acc
            acc_cfg["colab_tts"]["job_id"] = f"audition-{channel_id}-r{retake}" if retake else f"audition-{channel_id}"

            out_dir = staging_base / acc / "out"
            cache_dir = staging_base / acc / "cache"
            out_dir.mkdir(parents=True, exist_ok=True)
            cache_dir.mkdir(parents=True, exist_ok=True)

            try:
                client = Client(SYS_DIR, acc_cfg)
                client.account = acc
                client.session = "video-pilot-tts"

                # Check / reconcile before submission
                try:
                    client.reconcile()
                except Exception:
                    pass

                try:
                    client._ready(auto_start=True)
                except Exception as ex_ready:
                    logger.warning(f"Account {acc} _ready failed: {ex_ready}")

                client.synthesize(request, out_dir, cache_dir)
                account_used = acc
                logger.info(f"Synthesis successful on account: {acc}")
                break
            except (ColabError, Exception) as ex:
                logger.warning(f"Synthesis on {acc} failed ({type(ex).__name__}): {ex}. Failing over...")
                continue

        if not account_used:
            raise RuntimeError(f"All candidate Colab accounts failed for channel {channel_id}: {accounts_to_try}")

        # 6. Concatenate synthesized segments with format_v1 pauses
        active_out = staging_base / account_used / "out"
        tts_result_file = active_out / "tts-result.json"
        if not tts_result_file.is_file():
            raise FileNotFoundError(f"Missing {tts_result_file} from synthesis output")

        tts_res = json.loads(tts_result_file.read_text(encoding="utf-8"))
        segment_paths = [active_out / seg["path"] for seg in tts_res.get("segments", [])]

        raw_unmastered = staging_base / "raw_unmastered.wav"
        concat_mono_pcm16_wavs(segment_paths, raw_unmastered)

        # 7. Audio Mastering at target LUFS / dBTP via audio_processing.master()
        temp_work = staging_base / "master_work_tmp.wav"
        master_cfg = {
            "audio_lufs": target_lufs_val,
            "audio_peak_db": true_peak_val,
            "audio_voice_chain": voice_chain_val,
        }
        ap.master(raw_unmastered, temp_work, master_cfg)

        # 8. Save mastered sample.wav (raw_unmastered is overwritten in-place with mastered audio by ap.master)
        final_sample_wav = target_voice_dir / "sample.wav"
        shutil.copy2(raw_unmastered, final_sample_wav)

        # Copy to orchestrator artifact directory if present
        orchestrator_dir = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f")
        if orchestrator_dir.is_dir():
            shutil.copy2(final_sample_wav, orchestrator_dir / f"voice_sample_{channel_id}.wav")

        # 9. Measurement & Audition Report
        dur, lufs, tp, rms_val = measure_audio(final_sample_wav)
        sha256_hash = hashlib.sha256(final_sample_wav.read_bytes()).hexdigest()
        full_text = " ".join([seg["text"] for seg in tts_res.get("segments", [])])

        report_data = {
            "channel_id": channel_id,
            "voice": voice_name,
            "duration_seconds": round(dur, 3),
            "integrated_lufs": round(lufs, 2),
            "true_peak_dbtp": round(tp, 2),
            "rms": rms_val,
            "sha256": sha256_hash,
            "retake": int(retake),
            "text": full_text,
            "engine": "colab-omnivoice",
            "account_used": account_used,
        }

        report_file = target_voice_dir / "audition-report.json"
        report_file.write_text(json.dumps(report_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # Sync to channel worktree if present
        wt_voice_dir = Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/assets/voices/ch_{channel_id}")
        if wt_voice_dir.is_dir():
            shutil.copy2(final_sample_wav, wt_voice_dir / "sample.wav")
            shutil.copy2(report_file, wt_voice_dir / "audition-report.json")

        logger.info(f"Audition completed successfully for channel {channel_id}!")
        logger.info(f"  [+] Sample WAV: {final_sample_wav}")
        logger.info(f"  [+] Audition Report: {report_file}")
        logger.info(f"  [+] Measured: {dur:.2f}s | {lufs:.2f} LUFS | {tp:.2f} dBTP | RMS: {rms_val} | Account: {account_used}")

        return report_data
    finally:
        shutil.rmtree(staging_base, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="OmniVoice Audition Runner & Voice Cloner")
    parser.add_argument("--channel", required=True, help="Channel identifier (e.g. nao_luoi, tui_tien, ai_binh_dan)")
    parser.add_argument("--account", default=None, help="Initial Colab account to attempt (defaults to account-01 with pool failover)")
    parser.add_argument("--content", default=None, help="Explicit path to Week-1 content.json")
    parser.add_argument("--retake", type=int, default=0, help="Retake index (default: 0) to bypass cache and force fresh synthesis")
    parser.add_argument("--target-lufs", type=float, default=None, help="Target integrated LUFS (defaults to profile.audio_lufs or -14.0)")
    parser.add_argument("--true-peak-db", type=float, default=None, help="Target True Peak dBTP (defaults to profile.audio_peak_db or -1.5)")
    args = parser.parse_args()

    try:
        report = audition_channel(
            args.channel,
            target_account=args.account,
            explicit_content=args.content,
            retake=args.retake,
            target_lufs=args.target_lufs,
            true_peak_db=args.true_peak_db,
        )
        print(json.dumps(report, indent=2, ensure_ascii=False))
    except Exception as ex:
        logger.error(f"Audition failed: {ex}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
