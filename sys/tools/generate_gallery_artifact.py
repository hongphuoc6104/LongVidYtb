"""Generate Video Pilot Style v2 Gallery Artifact.
"""
from pathlib import Path
from tools.generate_style_v2_90 import CHANNELS_DATA

def main():
    brain_dir = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/style_v2")
    out_lines = []
    
    out_lines.append("# Video Pilot Style v2 Gallery — 18 English Channels (90 Images)\n")
    out_lines.append("> [!NOTE]")
    out_lines.append("> Bộ sưu tập 90 hình ảnh Style v2 được tạo hoàn toàn trên Google Flow CDP (Beluga / Imagen 3) theo đúng 4 quy tắc cốt lõi: tỷ lệ 9:16 dọc full-bleed, tuyệt đối không nền xanh navy/teal/xanh lam, không chữ/ký tự/logo, không bàn tay người, và diện tích âm thư thái >=60%. Mỗi kênh gồm 5 beat tạo thành một câu chuyện ngắn 20 giây (Hook -> Mechanism -> Payoff).\n")

    for ch in CHANNELS_DATA:
        num = ch["number"]
        c_name = ch["channel"]
        style_vi = ch["style_vi"]
        palette = ch["palette"]
        topic = ch["topic"]

        out_lines.append(f"## {num}. {c_name} — {style_vi}")
        out_lines.append(f"- **Topic**: {topic}")
        out_lines.append(f"- **Palette**: `{palette}`\n")
        out_lines.append("````carousel")

        for b in range(1, 6):
            img_label = f"{num}.{b}"
            img_path = brain_dir / f"{c_name}_0{b}.jpg"
            beat_info = ch["beats"][b - 1]
            role = beat_info["role"]
            out_lines.append(f"![Beat {img_label} ({role})]({img_path})")
            if b < 5:
                out_lines.append("<!-- slide -->")

        out_lines.append("````\n")

    out_path = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/style_v2_gallery.md")
    out_path.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"Artifact successfully written to {out_path} ({len(out_lines)} lines, {out_path.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
