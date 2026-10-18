"""
Generate a high-CTR, 16:9 (1920x1080) YouTube thumbnail for reviewer-2-novelty-bias-16x9.
Follows Video Pilot Rule 6 (thumbnail_spec: 2-4 uppercase words, high-contrast visual hook).
Title: Vì sao ý tưởng đột phá luôn bị phản biện từ chối?
Thumbnail Overlay: BẪY REVIEWER 2 (3 uppercase words).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_REGULAR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def create_youtube_thumbnail():
    base_path = Path("sys/runs/reviewer-2-novelty-bias-16x9/revisions/render/2/SC01.png")
    if not base_path.exists():
        base_path = Path("sys/runs/reviewer-2-novelty-bias-16x9/revisions/images/6/SC01_I1_16x9.jpg")

    out_dir = Path("video/reviewer-2-novelty-bias-16x9")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "thumbnail.png"

    target_w, target_h = 1920, 1080
    with Image.open(base_path) as raw:
        raw = raw.convert("RGBA")
        raw = raw.resize((target_w, target_h), Image.Resampling.LANCZOS)
        bg = raw

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(bg)
    bg = enhancer.enhance(1.08)

    # Dark gradient on the left side (from x=0 to x=1180) for crisp typography
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    o_draw = ImageDraw.Draw(overlay)

    for x in range(0, 1180):
        if x < 420:
            alpha = int(230 * 0.94)
        elif x < 880:
            factor = 1.0 - ((x - 420) / 460.0)
            alpha = int(215 * factor)
        else:
            factor = 1.0 - ((x - 880) / 300.0)
            alpha = int(110 * (factor ** 1.5))
        o_draw.line([(x, 0), (x, target_h)], fill=(10, 15, 26, alpha))

    # Top accent bar (Crimson Red / Academic Flame)
    o_draw.rectangle([0, 0, target_w, 14], fill=(225, 29, 72, 255))

    # Badge: LUẬT NGẦM HỌC THUẬT
    font_badge = ImageFont.truetype(FONT_BOLD, 32)
    badge_text = "LUẬT NGẦM HỌC THUẬT"
    badge_x, badge_y = 90, 130
    bbox = font_badge.getbbox(badge_text)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 24, 12
    o_draw.rounded_rectangle([badge_x, badge_y, badge_x + bw + pad_x*2, badge_y + bh + pad_y*2], radius=10, fill=(225, 29, 72, 255))
    o_draw.text((badge_x + pad_x, badge_y + pad_y - 2), badge_text, font=font_badge, fill=(255, 255, 255, 255))

    # Fonts
    font_hero = ImageFont.truetype(FONT_BOLD, 120)
    font_sub = ImageFont.truetype(FONT_BOLD, 64)

    # Shadow helper
    def draw_text_with_shadow(draw, pos, text, font, fill, shadow_fill=(0, 0, 0, 240), offset=7):
        x, y = pos
        for dx in range(-offset, offset + 1):
            for dy in range(-offset, offset + 1):
                if dx*dx + dy*dy <= offset*offset and (dx != 0 or dy != 0):
                    draw.text((x + dx, y + dy), text, font=font, fill=shadow_fill)
        draw.text((x, y), text, font=font, fill=fill)

    # 3-word primary hook: BẪY REVIEWER 2 (Per user prompt specification)
    draw_text_with_shadow(o_draw, (90, 240), "BẪY REVIEWER 2", font_hero, fill=(255, 230, 0, 255), offset=8)

    # Subtitles
    draw_text_with_shadow(o_draw, (90, 395), "CÀNG ĐỘT PHÁ...", font_sub, fill=(255, 255, 255, 255), offset=6)
    draw_text_with_shadow(o_draw, (90, 485), "CÀNG BỊ TỪ CHỐI!", font_sub, fill=(255, 75, 75, 255), offset=6)

    # Supporting Card at bottom
    card_y = 660
    card_w = 780
    card_h = 190
    o_draw.rounded_rectangle([90, card_y, 90 + card_w, card_y + card_h], radius=16, fill=(18, 24, 38, 220), outline=(255, 230, 0, 180), width=3)

    font_bullet = ImageFont.truetype(FONT_BOLD, 29)
    font_source = ImageFont.truetype(FONT_REGULAR, 26)

    o_draw.text((120, card_y + 28), "🔍  ĐỊNH KIẾN CHỐNG ĐỘT PHÁ (NOVELTY BIAS)", font=font_bullet, fill=(255, 230, 0, 255))
    o_draw.text((120, card_y + 75), "• Khái niệm an toàn: Dễ được hội đồng thông qua", font=font_source, fill=(240, 240, 240, 255))
    o_draw.text((120, card_y + 115), "• Ý tưởng cấp tiến: Bị gạt bỏ đầu tiên", font=font_source, fill=(255, 120, 120, 255))

    # Composite overlay on background
    final_img = Image.alpha_composite(bg, overlay)
    final_img = final_img.convert("RGB")
    final_img.save(out_path, "PNG", quality=95)
    print(f"YouTube 16:9 thumbnail generated successfully: {out_path} ({out_path.stat().st_size} bytes)")

if __name__ == "__main__":
    create_youtube_thumbnail()
