#!/usr/bin/env python3
"""
Synthesizes Chapter 1 Adam (+22% speed) using OmniVoice on Colab Tesla T4 GPU.
Uses 100% Vietnamese phonetic normalized text (no numbers, no English words).
Outputs broadcast-grade 48kHz Stereo WAV and generates cues JSON.
"""
import os
import subprocess
import json
import shutil
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_DIR = PROJ_ROOT / "sys" / "exports" / "ancient_humans_bundle"
AUDIO_DIR = BUNDLE_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
ART_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/ebb9330c-b49f-4fbc-930b-c1c2129f2704")

ACCOUNT_CLI = str(PROJ_ROOT / "sys" / "colab_bridge" / "account_cli.py")
ACCOUNT_DIR = f"{os.path.expanduser('~')}/.config/video-pilot/colab/profiles/account-01"
PY_BIN = f"{os.path.expanduser('~')}/.local/share/uv/tools/google-colab-cli/bin/python"

COLAB_SCRIPT = """
import json, time
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
from huggingface_hub import snapshot_download
from omnivoice import OmniVoice
from scipy.signal import resample_poly

SR = 48000
out_dir = Path("/content/output_audio")
out_dir.mkdir(parents=True, exist_ok=True)

print("Loading cached OmniVoice on Colab T4...")
local = snapshot_download('kjanh/KhanhTTS-OmniVoice', revision='20d056b8ea5d8d578b4cbaf1f703012fa3798a84')
model = OmniVoice.from_pretrained(local, device_map='cuda:0', dtype=torch.float16)
print("OmniVoice model ready!")

ref_audio = "/content/voices/adam/reference.wav"
ref_text = "A predator is an animal that hunts other animals for food."
speed = 1.22

# 100% PHONETIC NORMALIZED VIETNAMESE (No Arabic digits, no English tokens)
CH1_PHONETIC_SENTENCES = [
    ("Sáng nay, vừa mới mở mắt, một cỗ máy đã inh ỏi giục bạn phải rời giường.", 0.35),
    ("Bạn vội với tay bấm tắt chuông.", 0.35),
    ("Thế nhưng từ giây phút đó, ngày hôm nay coi như đã bị xếp lịch xong xuôi.", 0.35),
    ("Mấy giờ phải có mặt, phải làm những việc gì, và bao nhiêu tiếng đồng hồ phải cày cuốc cho người khác.", 0.45),
    ("Để rồi tối nay, trước khi chợp mắt, bạn lại ngoan ngoãn hẹn chính cỗ máy ấy, để sáng mai nó réo mình dậy tiếp.", 0.55),
    ("Bây giờ, hãy thử quay ngược đồng hồ về năm mươi nghìn năm trước.", 0.45),
    ("Một người thức giấc cùng ánh bình minh, không chuông báo thức, không lịch trình, và chẳng có việc gì phải vội.", 0.45),
    ("Tài sản duy nhất chỉ là một ngọn giáo, hai tấm da thú, và một đống lửa sưởi ấm.", 0.40),
    ("Anh ngồi dậy, khoan khoái vươn vai, rồi tự hỏi một câu mà cả đời này bạn chưa từng đủ tự do để hỏi, Hôm nay mình thích làm gì nhỉ?", 0.55),
    ("Não bạn lúc này hẳn đang bật còi báo động, Làm sao có chuyện đó được!", 0.40),
    ("Đời xưa đói khổ, ngắn ngủi và khốn cùng, từng giây từng phút đều là cuộc chiến sinh tồn cơ mà!", 0.45),
    ("Suốt nhiều thế kỷ qua, ai trong chúng ta cũng đinh ninh như vậy.", 0.45),
    ("Thế nhưng, bằng chứng lật ngược tất cả, lại đang nằm yên sâu dưới lòng đất.", 0.45),
    ("Và khi các nhà khảo cổ đào nó lên, sự thật đã khiến giới khoa học phải sững sờ.", 0.55),
    ("Đây chính là một nghịch lý kỳ lạ nhất của loài người.", 0.40),
    ("Bạn đang sống giữa muôn vàn cỗ máy sinh ra để tiết kiệm thời gian, từ máy giặt, lò vi sóng, đến xe hơi,", 0.45),
    ("Vậy cớ sao, một người tiền sử tay không tấc sắt, lại có nhiều thời gian rảnh rỗi hơn cả bạn?", 0.45),
    ("Suốt cả ngày, người đó đã làm những gì mà bạn không thể làm?", 0.40),
    ("Và toàn bộ thời gian của chúng ta, rốt cuộc đã biến đi đâu mất?", 0.70)
]

texts = [s[0] for s in CH1_PHONETIC_SENTENCES]
pauses = [s[1] for s in CH1_PHONETIC_SENTENCES]

print(f"Creating voice clone prompt for Adam (+22%)...")
prompt = model.create_voice_clone_prompt(ref_audio=ref_audio, ref_text=ref_text)

print(f"Synthesizing {len(texts)} sentences...")
t0 = time.time()
generated = model.generate(
    text=texts,
    language=["vi"] * len(texts),
    voice_clone_prompt=[prompt] * len(texts),
    speed=[speed] * len(texts),
    num_step=32
)
t_gen = time.time() - t0
print(f"Generation completed in {t_gen:.2f}s!")

segments = []
cues = []
current_time = 0.0

for idx, (gen_w, pause_sec) in enumerate(zip(generated, pauses)):
    if isinstance(gen_w, torch.Tensor):
        w = gen_w.detach().cpu().numpy().squeeze().astype(np.float32)
    else:
        w = np.asarray(gen_w, dtype=np.float32).squeeze()

    # Resample 24kHz -> 48kHz
    w_48k = resample_poly(w, 2, 1).astype(np.float32)
    sent_dur = len(w_48k) / SR
    start_time = current_time
    end_time = start_time + sent_dur

    cues.append({
        "index": idx + 1,
        "text": texts[idx],
        "start": round(start_time, 3),
        "end": round(end_time, 3),
        "duration": round(sent_dur, 3)
    })

    segments.append(w_48k)
    current_time = end_time

    if pause_sec > 0:
        pause_samples = int(pause_sec * SR)
        segments.append(np.zeros(pause_samples, dtype=np.float32))
        current_time += pause_sec

full_audio_mono = np.concatenate(segments)
full_audio_stereo = np.column_stack([full_audio_mono, full_audio_mono])

out_wav = out_dir / "ch1_adam_p22_phonetic.wav"
out_cues = out_dir / "ch1_adam_p22_phonetic_cues.json"

sf.write(str(out_wav), full_audio_stereo, SR, subtype='PCM_16')
with open(out_cues, 'w', encoding='utf-8') as f:
    json.dump(cues, f, ensure_ascii=False, indent=2)

print(f"SAVED: {out_wav} (Duration: {current_time:.2f}s, Samples: {len(full_audio_mono)})")
print(f"SAVED: {out_cues} ({len(cues)} cues)")
"""

def main():
    print("=== SYNTHESIZING ADAM (+22%) WITH 100% PHONETIC VIETNAMESE ===")
    
    # 1. Run synthesis on Colab
    argv = [PY_BIN, ACCOUNT_CLI, ACCOUNT_DIR, "exec", "-s", "video-pilot-tts", "--timeout", "300"]
    res = subprocess.run(argv, input=COLAB_SCRIPT, capture_output=True, text=True, check=True)
    print("Colab output:\n", res.stdout)

    # 2. Download WAV and cues
    colab_wav = "/content/output_audio/ch1_adam_p22_phonetic.wav"
    colab_cues = "/content/output_audio/ch1_adam_p22_phonetic_cues.json"
    
    local_wav = AUDIO_DIR / "ch1_adam_p22.wav"
    local_cues = AUDIO_DIR / "ch1_adam_p22_cues.json"
    local_mp3 = AUDIO_DIR / "ch1_adam_p22.mp3"

    print("Downloading updated WAV...")
    subprocess.run([PY_BIN, ACCOUNT_CLI, ACCOUNT_DIR, "download", "-s", "video-pilot-tts", colab_wav, str(local_wav)], check=True)
    
    print("Downloading updated cues...")
    subprocess.run([PY_BIN, ACCOUNT_CLI, ACCOUNT_DIR, "download", "-s", "video-pilot-tts", colab_cues, str(local_cues)], check=True)

    # 3. Convert to MP3
    print("Converting to MP3...")
    subprocess.run(["ffmpeg", "-y", "-i", str(local_wav), "-b:a", "192k", str(local_mp3)], check=True, capture_output=True)

    # 4. Mirror to artifact directory
    art_audio_dir = ART_DIR / "audio"
    art_audio_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(local_wav, art_audio_dir / "ch1_adam_p22.wav")
    shutil.copy2(local_cues, art_audio_dir / "ch1_adam_p22_cues.json")
    shutil.copy2(local_mp3, art_audio_dir / "ch1_adam_p22.mp3")

    print("\nSUCCESS! Adam (+22%) with 100% phonetic Vietnamese recreated:")
    print(f" - WAV: {local_wav} ({local_wav.stat().st_size / (1024*1024):.2f} MB)")
    print(f" - MP3: {local_mp3} ({local_mp3.stat().st_size / (1024*1024):.2f} MB)")
    print(f" - Cues: {local_cues}")

if __name__ == "__main__":
    main()
