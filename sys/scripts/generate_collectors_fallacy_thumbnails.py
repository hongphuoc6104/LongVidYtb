#!/usr/bin/env python3
"""Generate high-CTR thumbnails for collectors-fallacy-16x9 and collectors-fallacy-9x16.

Adheres strictly to Video Pilot Rule 6:
- Thumbnail text overlay: 2-4 uppercase words: LƯU ĐẦY KHÔNG ĐỌC
- 16:9 YouTube landscape (1920x1080)
- 9:16 TikTok / Shorts vertical (1080x1920) with 400px bottom safe zone
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def draw_text_with_shadow(draw, pos, text, font, fill, shadow_fill=(0, 0, 0, 240), offset=6):
    x, y = pos
    for dx in range(-offset, offset + 1):
        for dy in range(-offset, offset + 1):
            if dx * dx + dy * dy <= offset * offset and (dx != 0 or dy != 0):
                draw.text((x + dx, y + dy), text, font=font, fill=shadow_fill)
    draw.text((x, y), text, font=font, fill=fill)


def create_16x9_thumbnail():
    out_dir = Path("video/collectors-fallacy-16x9")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "thumbnail.png"
    target_w, target_h = 1920, 1080

    # Base background: Dark navy academic aesthetic with subtle blueprint grid
    bg = Image.new("RGBA", (target_w, target_h), (14, 20, 32, 255))
    draw = ImageDraw.Draw(bg)

    # Grid pattern
    for x in range(0, target_w, 60):
        draw.line([(x, 0), (x, target_h)], fill=(24, 34, 52, 255), width=1)
    for y in range(0, target_h, 60):
        draw.line([(0, y), (target_w, y)], fill=(24, 34, 52, 255), width=1)

    # Top accent bar (Vivid Amber Gold)
    draw.rectangle([0, 0, target_w, 14], fill=(245, 158, 11, 255))

    # Badge: NGHỊCH LÝ TRI THỨC
    font_badge = ImageFont.truetype(FONT_BOLD, 32)
    badge_text = "NGHỊCH LÝ TRI THỨC"
    badge_x, badge_y = 90, 120
    bbox = font_badge.getbbox(badge_text)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 26, 12
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + bw + pad_x * 2, badge_y + bh + pad_y * 2],
        radius=10,
        fill=(225, 29, 72, 255),
    )
    draw.text((badge_x + pad_x, badge_y + pad_y - 2), badge_text, font=font_badge, fill=(255, 255, 255, 255))

    # Hero Overlay (Exactly 4 Uppercase Words per spec): LƯU ĐẦY KHÔNG ĐỌC
    font_hero = ImageFont.truetype(FONT_BOLD, 120)
    draw_text_with_shadow(draw, (90, 230), "LƯU ĐẦY KHÔNG ĐỌC", font_hero, fill=(255, 230, 0, 255), offset=8)

    # Secondary punch lines
    font_sub = ImageFont.truetype(FONT_BOLD, 62)
    draw_text_with_shadow(draw, (90, 385), "TẢI HÀNG TRĂM CUỐN SÁCH...", font_sub, fill=(255, 255, 255, 255), offset=6)
    draw_text_with_shadow(draw, (90, 475), "CHỈ LÀ ẢO GIÁC HỌC!", font_sub, fill=(255, 75, 75, 255), offset=6)

    # Supporting Card at bottom left
    card_y = 650
    card_w = 820
    card_h = 220
    draw.rounded_rectangle(
        [90, card_y, 90 + card_w, card_y + card_h],
        radius=18,
        fill=(18, 26, 42, 240),
        outline=(245, 158, 11, 220),
        width=3,
    )

    font_card_title = ImageFont.truetype(FONT_BOLD, 30)
    font_card_body = ImageFont.truetype(FONT_REGULAR, 26)

    draw.text((120, card_y + 25), "⚖  THE COLLECTOR'S FALLACY (TÂM LÝ HỌC)", font=font_card_title, fill=(255, 230, 0, 255))
    draw.text((120, card_y + 75), "• Tải file về máy: Phóng ra Dopamine giả tạo", font=font_card_body, fill=(240, 240, 240, 255))
    draw.text((120, card_y + 115), "• Ôm đống PDF chết: Não lầm tưởng đã hiểu bài", font=font_card_body, fill=(255, 120, 120, 255))
    draw.text((120, card_y + 155), "• Quy tắc cứu nguy: Đọc 1 trả 1 & Test giấy trắng", font=font_card_body, fill=(52, 211, 153, 255))

    # Right side: Visual contrast diagram (Storage vs Retrieval)
    diag_x = 1040
    diag_y = 200
    diag_w = 780
    diag_h = 670
    draw.rounded_rectangle(
        [diag_x, diag_y, diag_x + diag_w, diag_y + diag_h],
        radius=24,
        fill=(10, 16, 28, 220),
        outline=(59, 130, 246, 180),
        width=2,
    )

    font_diag_header = ImageFont.truetype(FONT_BOLD, 34)
    draw.text((diag_x + 40, diag_y + 35), "ĐỐI ĐẦU 2 LỐI HỌC THUẬT", font=font_diag_header, fill=(59, 130, 246, 255))

    # Box 1: Storage Hoarding
    b1_y = diag_y + 100
    draw.rounded_rectangle([diag_x + 40, b1_y, diag_x + diag_w - 40, b1_y + 220], radius=14, fill=(225, 29, 72, 35), outline=(225, 29, 72, 150), width=2)
    font_box_title = ImageFont.truetype(FONT_BOLD, 28)
    font_box_text = ImageFont.truetype(FONT_REGULAR, 24)
    draw.text((diag_x + 65, b1_y + 20), "❌  THỢ SĂN TÀI LIỆU (500GB Drive)", font=font_box_title, fill=(255, 100, 100, 255))
    draw.text((diag_x + 65, b1_y + 65), "• Bấm tải về trong 3 giây để trốn tránh việc đọc", font=font_box_text, fill=(230, 230, 230, 255))
    draw.text((diag_x + 65, b1_y + 105), "• Tốn 80% thời gian tìm tệp, xếp thư mục", font=font_box_text, fill=(230, 230, 230, 255))
    draw.text((diag_x + 65, b1_y + 145), "• Kết quả: Điểm kiểm tra chạm đáy, đầu rỗng", font=font_box_text, fill=(255, 150, 150, 255))

    # Box 2: Active Synthesis
    b2_y = diag_y + 350
    draw.rounded_rectangle([diag_x + 40, b2_y, diag_x + diag_w - 40, b2_y + 220], radius=14, fill=(16, 185, 129, 35), outline=(16, 185, 129, 150), width=2)
    draw.text((diag_x + 65, b2_y + 20), "✅  TIÊU HÓA TRI THỨC (1 Bài duy nhất)", font=font_box_title, fill=(52, 211, 153, 255))
    draw.text((diag_x + 65, b2_y + 65), "• Đọc sâu, ghi chép văn nói theo Zettelkasten", font=font_box_text, fill=(230, 230, 230, 255))
    draw.text((diag_x + 65, b2_y + 105), "• Tự truy xuất chủ động bằng tờ giấy trắng", font=font_box_text, fill=(230, 230, 230, 255))
    draw.text((diag_x + 65, b2_y + 145), "• Kết quả: Nắm trọn bản chất, tư duy sắc bén", font=font_box_text, fill=(167, 243, 208, 255))

    final_img = bg.convert("RGB")
    final_img.save(out_path, "PNG", quality=95)
    print(f"Generated 16:9 thumbnail: {out_path} ({out_path.stat().st_size} bytes)")


def create_9x16_thumbnail():
    out_dir = Path("video/collectors-fallacy-9x16")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "cover_tiktok_9x16.png"
    target_w, target_h = 1080, 1920

    # Vertical background
    bg = Image.new("RGBA", (target_w, target_h), (12, 18, 30, 255))
    draw = ImageDraw.Draw(bg)

    # Subtle grid lines
    for x in range(0, target_w, 60):
        draw.line([(x, 0), (x, target_h)], fill=(22, 32, 50, 255), width=1)
    for y in range(0, target_h, 60):
        draw.line([(0, y), (target_w, y)], fill=(22, 32, 50, 255), width=1)

    # Top accent bar
    draw.rectangle([0, 0, target_w, 16], fill=(225, 29, 72, 255))

    # Badge: BẪY DI ĐỘNG (Safe Zone: Top 150px)
    font_badge = ImageFont.truetype(FONT_BOLD, 36)
    badge_text = "ẢO TƯỞNG TRI THỨC"
    bbox = font_badge.getbbox(badge_text)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 28, 14
    badge_x = (target_w - (bw + pad_x * 2)) // 2
    badge_y = 220
    draw.rounded_rectangle([badge_x, badge_y, badge_x + bw + pad_x * 2, badge_y + bh + pad_y * 2], radius=12, fill=(225, 29, 72, 255))
    draw.text((badge_x + pad_x, badge_y + pad_y - 2), badge_text, font=font_badge, fill=(255, 255, 255, 255))

    # Hero Title (Exactly 4 Uppercase Words): LƯU ĐẦY KHÔNG ĐỌC
    font_hero = ImageFont.truetype(FONT_BOLD, 92)
    bbox_hero = font_hero.getbbox("LƯU ĐẦY KHÔNG ĐỌC")
    hw = bbox_hero[2] - bbox_hero[0]
    draw_text_with_shadow(draw, ((target_w - hw) // 2, 360), "LƯU ĐẦY KHÔNG ĐỌC", font_hero, fill=(255, 230, 0, 255), offset=8)

    # Subtitles in Grid Zone
    font_sub = ImageFont.truetype(FONT_BOLD, 52)
    s1 = "VÒNG LẶP LƯU BÀI XEM SAU"
    bbox_s1 = font_sub.getbbox(s1)
    draw_text_with_shadow(draw, ((target_w - (bbox_s1[2] - bbox_s1[0])) // 2, 480), s1, font_sub, fill=(255, 255, 255, 255), offset=6)

    s2 = "BỎ QUÊN TRÊN ĐIỆN THOẠI!"
    bbox_s2 = font_sub.getbbox(s2)
    draw_text_with_shadow(draw, ((target_w - (bbox_s2[2] - bbox_s2[0])) // 2, 555), s2, font_sub, fill=(255, 80, 80, 255), offset=6)

    # Center Visual Infographic (Safe Zone y: 680 to 1400)
    card_x = 70
    card_y = 690
    card_w = target_w - 140
    card_h = 720
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=24, fill=(18, 26, 42, 240), outline=(245, 158, 11, 200), width=3)

    font_info_title = ImageFont.truetype(FONT_BOLD, 36)
    font_info_line = ImageFont.truetype(FONT_REGULAR, 30)

    draw.text((card_x + 40, card_y + 40), "📱  BẢN CHẤT CỦA NÚT LƯU", font=font_info_title, fill=(255, 230, 0, 255))
    draw.text((card_x + 40, card_y + 110), "1. Bấm lưu mất đúng 3 giây", font=font_info_line, fill=(230, 230, 230, 255))
    draw.text((card_x + 40, card_y + 160), "2. Não tự phóng Dopamine thỏa mãn giả", font=font_info_line, fill=(255, 130, 130, 255))
    draw.text((card_x + 40, card_y + 210), "3. Ngỡ rằng mình đã học xong", font=font_info_line, fill=(255, 130, 130, 255))
    draw.text((card_x + 40, card_y + 260), "4. Hàng ngàn bài viết thành 'file chết'", font=font_info_line, fill=(230, 230, 230, 255))

    # Divider
    draw.line([(card_x + 40, card_y + 330), (card_x + card_w - 40, card_y + 330)], fill=(50, 65, 90, 255), width=2)

    draw.text((card_x + 40, card_y + 360), "⚡  CÁCH PHÁ VỠ VÒNG LẶP", font=font_info_title, fill=(52, 211, 153, 255))
    draw.text((card_x + 40, card_y + 430), "• Quy tắc: Đọc một, trả một", font=font_info_line, fill=(240, 240, 240, 255))
    draw.text((card_x + 40, card_y + 480), "• Xóa 1 tệp cũ trước khi lưu tệp mới", font=font_info_line, fill=(240, 240, 240, 255))
    draw.text((card_x + 40, card_y + 530), "• Tắt máy, tự giải thích bằng giấy trắng", font=font_info_line, fill=(240, 240, 240, 255))
    draw.text((card_x + 40, card_y + 580), "• Đọc trang đầu tiên ngay tối nay!", font=font_info_line, fill=(255, 230, 0, 255))

    # Safe Zone note at bottom (Above 400px bottom safe zone)
    font_bottom = ImageFont.truetype(FONT_BOLD, 30)
    b_text = "HỌC THUẬT SÂU • VIDEO PILOT"
    bbox_b = font_bottom.getbbox(b_text)
    draw.text(((target_w - (bbox_b[2] - bbox_b[0])) // 2, 1460), b_text, font=font_bottom, fill=(148, 163, 184, 255))

    final_img = bg.convert("RGB")
    final_img.save(out_path, "PNG", quality=95)
    # Also save as thumbnail.png
    final_img.save(out_dir / "thumbnail.png", "PNG", quality=95)
    print(f"Generated 9:16 thumbnail: {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    create_16x9_thumbnail()
    create_9x16_thumbnail()
