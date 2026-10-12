import json
import time
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
from huggingface_hub import snapshot_download
from omnivoice import OmniVoice

CH1_REWRITTEN_SENTENCES = [
    ("Sáng nay, vừa mới mở mắt, một cỗ máy đã inh ỏi giục bạn phải rời giường.", 0.35),
    ("Bạn vội với tay bấm tắt chuông.", 0.35),
    ("Thế nhưng từ giây phút đó, ngày hôm nay coi như đã bị xếp lịch xong xuôi.", 0.35),
    ("Mấy giờ phải có mặt, phải làm những việc gì, và bao nhiêu tiếng đồng hồ phải cày cuốc cho người khác.", 0.45),
    ("Để rồi tối nay, trước khi chợp mắt, bạn lại ngoan ngoãn hẹn chính cỗ máy ấy... để sáng mai nó réo mình dậy tiếp.", 0.55),
    ("Bây giờ, hãy thử quay ngược đồng hồ về 50.000 năm trước.", 0.45),
    ("Một người thức giấc cùng ánh bình minh: không chuông báo thức, không lịch trình, và chẳng có việc gì phải vội.", 0.45),
    ("Tài sản duy nhất chỉ là một ngọn giáo, hai tấm da thú, và một đống lửa sưởi ấm.", 0.40),
    ("Anh ngồi dậy, khoan khoái vươn vai, rồi tự hỏi một câu mà cả đời này bạn chưa từng đủ tự do để hỏi: Hôm nay mình thích làm gì nhỉ?", 0.55),
    ("Não bạn lúc này hẳn đang bật còi báo động: Làm sao có chuyện đó được!", 0.40),
    ("Đời xưa đói khổ, ngắn ngủi và khốn cùng, từng giây từng phút đều là cuộc chiến sinh tồn cơ mà!", 0.45),
    ("Suốt nhiều thế kỷ qua, ai trong chúng ta cũng đinh ninh như vậy.", 0.45),
    ("Thế nhưng, bằng chứng lật ngược tất cả... lại đang nằm yên sâu dưới lòng đất.", 0.45),
    ("Và khi các nhà khảo cổ đào nó lên, sự thật đã khiến giới khoa học phải sững sờ.", 0.55),
    ("Đây chính là một nghịch lý kỳ lạ nhất của loài người.", 0.40),
    ("Bạn đang sống giữa muôn vàn cỗ máy sinh ra để tiết kiệm thời gian: từ máy giặt, lò vi sóng, đến xe hơi...", 0.45),
    ("Vậy cớ sao, một người tiền sử tay không tấc sắt... lại có nhiều thời gian rảnh rỗi hơn cả bạn?", 0.45),
    ("Suốt cả ngày, người đó đã làm những gì mà bạn không thể làm?", 0.40),
    ("Và toàn bộ thời gian của chúng ta... rốt cuộc đã biến đi đâu mất?", 0.70),
]

SR = 48000
out_dir = Path("/content/output_audio")
out_dir.mkdir(parents=True, exist_ok=True)

print("Loading cached OmniVoice...")
local = snapshot_download('kjanh/KhanhTTS-OmniVoice', revision='20d056b8ea5d8d578b4cbaf1f703012fa3798a84')
model = OmniVoice.from_pretrained(local, device_map='cuda:0', dtype=torch.float16)
print("OmniVoice ready on GPU!")

VOICES = [
    {
        "name": "minhquan",
        "label": "Minh Quân Pro (+22%)",
        "ref_audio": "/content/voices/minh-quan-pro/reference.wav",
        "ref_text": "Vừa xỏ giày định ra ngoài đi dạo thì trời bỗng kéo mây đen kịt.",
        "speed": 1.22 / 0.92,
    },
    {
        "name": "adam",
        "label": "Adam (+22%)",
        "ref_audio": "/content/voices/adam/reference.wav",
        "ref_text": "A predator is an animal that hunts other animals for food.",
        "speed": 1.22 / 1.0,
    }
]

texts = [s[0] for s in CH1_REWRITTEN_SENTENCES]
pauses = [s[1] for s in CH1_REWRITTEN_SENTENCES]

for v in VOICES:
    print(f"\n==================== Synthesizing {v['label']} ====================")
    prompt = model.create_voice_clone_prompt(ref_audio=v['ref_audio'], ref_text=v['ref_text'])
    
    # Generate sentences
    generated = model.generate(
        text=texts,
        language=["vi"] * len(texts),
        voice_clone_prompt=[prompt] * len(texts),
        speed=[v['speed']] * len(texts),
        num_step=32
    )
    
    segments = []
    cues = []
    current_time = 0.0
    
    for idx, (gen_w, pause_sec) in enumerate(zip(generated, pauses)):
        # Normalize to float32 1D numpy array
        if isinstance(gen_w, torch.Tensor):
            w = gen_w.detach().cpu().numpy().squeeze().astype(np.float32)
        else:
            w = np.asarray(gen_w, dtype=np.float32).squeeze()
            
        # Ensure sample rate is 48000 (resample if model output is 24000)
        # Check model native sr or len
        # OmniVoice native sr is typically 24000
        # Let's resample from 24000 to 48000 if needed:
        # Note: OmniVoice outputs at 24000Hz
        from scipy.signal import resample_poly
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
        
        # Convert mono to stereo
        stereo_w = np.column_stack([w_48k, w_48k])
        segments.append(stereo_w)
        current_time = end_time
        
        if idx < len(texts) - 1 and pause_sec > 0:
            pause_samples = int(pause_sec * SR)
            pause_arr = np.zeros((pause_samples, 2), dtype=np.float32)
            segments.append(pause_arr)
            current_time += pause_sec
            
    full_audio = np.concatenate(segments, axis=0)
    total_dur = len(full_audio) / SR
    
    wav_path = out_dir / f"ch1_{v['name']}_p22.wav"
    sf.write(str(wav_path), full_audio, SR, subtype="PCM_16")
    
    cues_path = out_dir / f"ch1_{v['name']}_p22_cues.json"
    with open(cues_path, "w", encoding="utf-8") as f:
        json.dump(cues, f, ensure_ascii=False, indent=2)
        
    print(f"SUCCESS: {v['name']} duration: {total_dur:.2f}s | Saved to {wav_path}")

print("\nALL VOICES SYNTHESIS FINISHED ON COLAB!")
