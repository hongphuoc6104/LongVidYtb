#!/usr/bin/env python3
"""Build the master Vietnamese review gallery artifact for all 18 rebuilt English channels."""

from __future__ import annotations

import json
from pathlib import Path

BRAIN_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f")
COMP_DIR = BRAIN_DIR / "competitor_frames"
PILOTS_DIR = BRAIN_DIR / "rebuilt_pilots"
VIDEO_ROOT = Path("/home/hongphuoc6104/Desktop/vp-agent-core/video")

CHANNELS_ORDER = [
    ("en-first-principles", "Mô hình tư duy & Nghịch lý Vật lý (Mental Models & Physics Paradoxes)", "Veritasium"),
    ("en-scale-and-bone", "Động vật học & Tiến hóa Vòng đời (Zoology & Animal Life-Cycle Evolution)", "BBC Earth / PBS Eons"),
    ("en-pocket-cosmos", "Vật lý Thiên văn & Không gian sâu (Astrophysics & Deep Space)", "Melodysheep / Astrum"),
    ("en-deep-time-strata", "Địa chất học & Lịch sử Trái Đất cổ đại (Geology & Deep Earth History)", "History of the Earth"),
    ("en-inside-vessel", "Sinh lý học & Giải phẫu Y khoa 3D (Human Physiology & Medical 3D)", "Nucleus Medical Media"),
    ("en-macro-gears", "Kinh tế vĩ mô, Cảng biển & Kỹ thuật Hạ tầng (Macroeconomics & Engineering)", "Practical Engineering / Wendover"),
    ("en-fine-print", "Luật Tiêu dùng & Điều khoản Hợp đồng ẩn (Consumer Law & Hidden Contracts)", "CNBC Make It / LegalEagle"),
    ("en-crowd-strings", "Tâm lý Đám đông & Phóng sự Điều tra 3D (Mass Psychology & 3D Documentary)", "Fern / Academy of Ideas"),
    ("en-cold-case-ink", "Hồ sơ Bí ẩn & Trinh thám Hình sự (Forensic Mysteries & Unsolved Archives)", "LEMMiNO"),
    ("en-choke-point", "Địa chính trị Hàng hải & Bản đồ Vệ tinh Quỹ đạo (Maritime Geopolitics)", "RealLifeLore"),
    ("en-root-and-canopy", "Thực vật học & Hệ sinh thái Rừng (Botany & Forest Ecology)", "BBC Earth (The Green Planet)"),
    ("en-spawn-to-apex", "Vi sinh học & Vòng đời Côn trùng theo Thời gian (Chronological Insect Life-Cycle)", "Deep Look PBS"),
    ("en-second-arrow", "Triết học Khắc kỷ & Cổ điển (Stoicism & Classical Philosophy)", "Einzelgänger / Daily Stoic"),
    ("en-bamboo-marble", "Triết học Phương Đông & Chiêm nghiệm Sống (Eastern Philosophy & Life Lessons)", "Pursuit of Wonder / Aperture"),
    ("en-kindred-sketch", "Tâm lý Tình cảm & Gắn kết (Relationships & Attachment Psychology)", "Cinema Therapy / The School of Life"),
    ("en-lazy-brain", "Thần kinh học Dopamine, Thói quen & Sự tập trung (Neuroscience of Habits)", "Kurzgesagt / Huberman Lab"),
    ("en-career-leverage", "Chiến lược Sự nghiệp & Đàm phán (Workplace Strategy & Leverage)", "Wall Street Journal / HBR"),
    ("en-wallet-anatomy", "Tâm lý Định giá & Tài chính Tiêu dùng (Behavioral Pricing & Consumer Finance)", "Two Cents PBS / WSJ"),
]


def main() -> None:
    lines = [
        "# Báo Cáo & Thư Viện Duyệt 18 Dự Án Video Tiếng Anh (Đập Đi Xây Lại Từ 20 Khung Hình 1-FPS Của Kênh Đối Thủ Thật)",
        "",
        "> [!IMPORTANT]",
        "> **Quy chuẩn đã áp dụng đồng bộ trên toàn bộ 18/18 kênh:**",
        "> 1. **Không gán cứng (Zero Hardcoded AI Slop):** Mỗi kênh được trích xuất **20 khung hình liên tiếp theo từng giây (`1 FPS`: `frame_01s.jpg` $\\rightarrow$ `frame_20s.jpg`)** từ đoạn video thực tế của kênh đối thủ lớn nhất trong ngách.",
        "> 2. **Học trực tiếp ánh sáng, chất liệu & chuyển động máy quay từng giây (`t=1s -> t=20s`):** Đội 4 Subagents Gemini 3.8 Flash (`16 workers` song song) đọc trực tiếp từng khung hình để thiết kế 8 nhịp hình ảnh và chuyển động máy quay (`push_in`, `zoom_out`, `pan_left`, `pan_right`, `tilt_up`, `tilt_down`) sát thực tế đối thủ.",
        "> 3. **Chuẩn khung hiển thị Tiếng Việt (`9:16` & `16:9`):**",
        ">    - **`9:16` Short:** Phụ đề trắng viền đen chuẩn kênh Việt (`Arial Bold, FontSize=48, MarginV=400, Outline=3`), logo bo góc `100x100` góc dưới phải (`W-w-24:H-h-50`), âm thanh `-11.0 LUFS / -1.0 dBTP`.",
        ">    - **`16:9` Long Explainer:** Khung 16:9 sạch kèm phụ đề rời `.srt`, logo bo góc `100x100` tại `W-w-36:H-h-36`, âm thanh `-11.0 LUFS / -1.0 dBTP`.",
        "",
        "## Bảng Tổng Hợp 18 Kênh & Link Xem Nhanh Video Pilot (9:16 & 16:9)",
        "",
        "| # | Mã Kênh | Ngách Nội Dung | Kênh Đối Thủ Thật (Học 20 Frame 1-FPS) | Video Pilot 9:16 (Chuẩn Khung VN) | Video Pilot 16:9 (Chuẩn Khung VN) |",
        "| :---: | :--- | :--- | :--- | :--- | :--- |",
    ]

    for idx, (slug, niche, comp) in enumerate(CHANNELS_ORDER, 1):
        short_mp4 = VIDEO_ROOT / f"{slug}-test-20s-9x16/{slug}-test-20s-9x16.mp4"
        long_mp4 = VIDEO_ROOT / f"{slug}-pilot-16x9/{slug}-pilot-16x9.mp4"
        lines.append(
            f"| {idx} | `{slug}` | {niche} | **{comp}** | "
            f"[{slug}-9x16.mp4](file://{short_mp4}) | [{slug}-16x9.mp4](file://{long_mp4}) |"
        )

    lines.append("")

    for idx, (slug, niche, comp) in enumerate(CHANNELS_ORDER, 1):
        pilot_dir = PILOTS_DIR / slug
        spec_file = pilot_dir / f"{slug}_rebuilt_spec.json"
        report_file = pilot_dir / "pilot_build_report.json"

        spec = {}
        if spec_file.is_file():
            try:
                spec = json.loads(spec_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        report = {}
        if report_file.is_file():
            try:
                report = json.loads(report_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        dur = report.get("duration_sec", "N/A")
        short_mp4 = VIDEO_ROOT / f"{slug}-test-20s-9x16/{slug}-test-20s-9x16.mp4"
        long_mp4 = VIDEO_ROOT / f"{slug}-pilot-16x9/{slug}-pilot-16x9.mp4"
        comp_clip = COMP_DIR / slug / "competitor_segment_20s.mp4"

        obs_vi = spec.get("frame_by_frame_observations_vi", "")
        if isinstance(obs_vi, (dict, list)):
            obs_vi = json.dumps(obs_vi, ensure_ascii=False, indent=2)
        learned_vi = spec.get("learned_style_summary_vi", "")
        if isinstance(learned_vi, (dict, list)):
            learned_vi = json.dumps(learned_vi, ensure_ascii=False, indent=2)

        lines.extend([
            "---",
            f"## {idx}. `{slug}` — {niche}",
            f"- **Kênh đối thủ lấy mẫu thực tế:** **{comp}** ([Đoạn video gốc 20s của đối thủ](file://{comp_clip}))",
            f"- **Video Pilot 9:16 (Burned-in Sub + Watermark chuẩn VN, `{dur}s`):** [{slug}-test-20s-9x16.mp4](file://{short_mp4})",
            f"- **Video Pilot 16:9 (Widescreen + Sidecar SRT + Watermark chuẩn VN, `{dur}s`):** [{slug}-pilot-16x9.mp4](file://{long_mp4})",
            f"- **Phong cách hình ảnh & chuyển động học từ 20 frame đối thủ:** {learned_vi}",
            f"- **Quan sát chi tiết từng khung hình 1 giây (`1s..20s`):** {obs_vi}",
            "",
        ])

        # Embed carousel of Competitor sample frames + Rebuilt Pilot rendered frames
        comp_f02 = COMP_DIR / slug / "frame_02s.jpg"
        comp_f10 = COMP_DIR / slug / "frame_10s.jpg"
        rendered_dir = pilot_dir / "rendered_frames_9x16"
        p_frames = sorted(rendered_dir.glob("pilot_frame_*s.jpg"))
        selected_pilot_frames = []
        for target_idx in (1, 4, 8, 12):
            cand = rendered_dir / f"pilot_frame_{target_idx:02d}s.jpg"
            if cand.is_file():
                selected_pilot_frames.append((cand, f"Pilot 9:16 tại giây {target_idx}s"))
        if not selected_pilot_frames and p_frames:
            for pf in p_frames[:4]:
                selected_pilot_frames.append((pf, f"Pilot 9:16 ({pf.name})"))

        carousel_items = []
        if comp_f02.is_file():
            carousel_items.append((comp_f02, f"[Đối thủ {comp}] Khung hình thực tế giây 02s"))
        if comp_f10.is_file():
            carousel_items.append((comp_f10, f"[Đối thủ {comp}] Khung hình thực tế giây 10s"))
        carousel_items.extend(selected_pilot_frames)

        if carousel_items:
            lines.append("````carousel")
            for c_idx, (img_p, cap) in enumerate(carousel_items):
                if c_idx > 0:
                    lines.append("<!-- slide -->")
                lines.append(f"![{cap}]({img_p})")
            lines.append("````")
            lines.append("")

    out_md = BRAIN_DIR / "rebuilt_18_channels_gallery.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_md} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
