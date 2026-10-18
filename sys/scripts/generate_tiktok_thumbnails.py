"""
Generate high-impact, prominent TikTok / Shorts 9:16 cover thumbnails for the 3 Feynman videos.
Ensures perfect Safe-Zone alignment for TikTok Profile Grid (3:4) and Search Feed.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_REGULAR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

THUMBNAIL_SPECS = [
    {
        "job": "feynman-jargon-trap-9x16",
        "base_image": "sys/runs/feynman-jargon-trap-9x16/revisions/images/3/SC01_I3_9x16.jpg",
        "alt_base": "sys/runs/feynman-jargon-trap-9x16/revisions/images/3/SC04_I2_9x16.jpg",
        "output_dir": "video/feynman-jargon-trap-9x16",
        "badge_text": "NGHỊCH LÝ HỌC THUẬT",
        "badge_color": (225, 29, 72),  # Crimson Red
        "headline_lines": [
            ("CÀNG DÙNG TỪ KHÓ", (255, 230, 0)),   # Bright Yellow
            ("CÀNG BỊ ĐÁNH GIÁ THẤP!", (255, 255, 255)) # White
        ],
        "sub_tag": "BẪY TƯ DUY KHOA HỌC • NGHIÊN CỨU DANIEL OPPENHEIMER",
        "accent_color": (255, 230, 0)
    },
    {
        "job": "feynman-jargon-trap-spinoff-02-9x16",
        "base_image": "sys/runs/feynman-jargon-trap-spinoff-02-9x16/revisions/images/3/SC03_I2_9x16.jpg",
        "alt_base": "sys/runs/feynman-jargon-trap-spinoff-02-9x16/revisions/images/3/SC04_I4_9x16.jpg",
        "output_dir": "video/feynman-jargon-trap-spinoff-02-9x16",
        "badge_text": "KỸ THUẬT FEYNMAN",
        "badge_color": (37, 99, 235),  # Royal Blue
        "headline_lines": [
            ("QUY TẮC 10 TUỔI:", (255, 230, 0)),
            ("KHÔNG GIẢI THÍCH NỔI", (255, 255, 255)),
            ("LÀ CHƯA HIỂU GÌ!", (255, 70, 70))  # Vivid Red-Orange
        ],
        "sub_tag": "BÍ QUYẾT HỌC SÂU CỦA NHÀ NOBEL VẬT LÝ",
        "accent_color": (59, 130, 246)
    },
    {
        "job": "feynman-jargon-trap-spinoff-03-9x16",
        "base_image": "sys/runs/feynman-jargon-trap-spinoff-03-9x16/revisions/images/2/SC04_I2_9x16.jpg",
        "alt_base": "sys/runs/feynman-jargon-trap-spinoff-03-9x16/revisions/images/2/SC05_I1_9x16.jpg",
        "output_dir": "video/feynman-jargon-trap-spinoff-03-9x16",
        "badge_text": "BẢO VỆ KHÓA LUẬN",
        "badge_color": (5, 150, 105),  # Emerald Green
        "headline_lines": [
            ("TEST TỜ GIẤY TRẮNG", (255, 230, 0)),
            ("120S HẠ GỤC HỘI ĐỒNG", (255, 255, 255))
        ],
        "sub_tag": "QUY TẮC 3 CÂU GIÚP BẠN QUA MÔN ĐIỂM A",
        "accent_color": (16, 185, 129)
    }
]

def draw_rounded_rect(draw, bbox, radius, fill, outline=None, width=1):
    x0, y0, x1, y1 = bbox
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def create_thumbnail(spec: dict) -> Path:
    base_path = Path(spec["base_image"])
    if not base_path.exists():
        base_path = Path(spec["alt_base"])

    # 1. Base Image Prep (1080x1920)
    with Image.open(base_path) as raw:
        # Resize/crop to exactly 1080x1920
        raw = raw.convert("RGBA")
        target_w, target_h = 1080, 1920
        # Calculate aspect ratios
        img_ratio = raw.width / raw.height
        target_ratio = target_w / target_h

        if img_ratio > target_ratio:
            # Source is wider, scale by height
            new_h = target_h
            new_w = int(new_h * img_ratio)
        else:
            # Source is taller, scale by width
            new_w = target_w
            new_h = int(new_w / img_ratio)

        scaled = raw.resize((new_w, new_h), Image.Resampling.LANCZOS)
        # Center crop
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        bg = scaled.crop((left, top, left + target_w, top + target_h))

    # Enhance contrast slightly
    enhancer = ImageEnhance.Contrast(bg)
    bg = enhancer.enhance(1.08)

    # 2. Add Top-to-Mid Dark Gradient Overlay (y=0 to y=850) for crystal clear text readability
    gradient = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gradient)

    # Gradient in upper region
    for y in range(0, 850):
        if y < 350:
            alpha = int(210)
        elif y < 700:
            # Fade from 210 to 120
            alpha = int(210 - (y - 350) * (90 / 350))
        else:
            # Fade to 0
            alpha = int(120 - (y - 700) * (120 / 150))
        g_draw.line([(0, y), (1080, y)], fill=(15, 23, 42, max(0, alpha)))

    # Subtle dark vignette at very bottom (y=1750 to 1920)
    for y in range(1750, 1920):
        alpha = int((y - 1750) * (140 / 170))
        g_draw.line([(0, y), (1080, y)], fill=(15, 23, 42, alpha))

    composed = Image.alpha_composite(bg, gradient)
    draw = ImageDraw.Draw(composed)

    # 3. Category Badge (Centered around y=240)
    badge_font = ImageFont.truetype(FONT_BOLD, 30)
    badge_text = f"  {spec['badge_text']}  "
    bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    badge_w = text_w + 36
    badge_h = 58
    badge_x0 = (1080 - badge_w) // 2
    badge_y0 = 230

    # Outer glow / shadow for badge
    draw_rounded_rect(draw, (badge_x0 - 2, badge_y0 - 2, badge_x0 + badge_w + 2, badge_y0 + badge_h + 2),
                      radius=16, fill=(0, 0, 0, 100))
    draw_rounded_rect(draw, (badge_x0, badge_y0, badge_x0 + badge_w, badge_y0 + badge_h),
                      radius=14, fill=spec["badge_color"], outline=(255, 255, 255, 200), width=2)

    draw.text((badge_x0 + 18, badge_y0 + (badge_h - text_h) // 2 - 2),
              spec["badge_text"], font=badge_font, fill=(255, 255, 255))

    # 4. Main Headline Lines (Safe Zone y=320 to y=650)
    font_headline = ImageFont.truetype(FONT_BOLD, 74)
    font_sub = ImageFont.truetype(FONT_BOLD, 26)

    curr_y = 320
    for line_text, color in spec["headline_lines"]:
        l_bbox = draw.textbbox((0, 0), line_text, font=font_headline)
        l_w = l_bbox[2] - l_bbox[0]
        l_h = l_bbox[3] - l_bbox[1]

        box_padding_x = 32
        box_padding_y = 16
        box_w = l_w + box_padding_x * 2
        box_h = l_h + box_padding_y * 2
        box_x = (1080 - box_w) // 2
        box_y = curr_y

        # Draw dark rounded pill backing behind headline line for maximum contrast
        draw_rounded_rect(draw, (box_x - 3, box_y - 2, box_x + box_w + 3, box_y + box_h + 4),
                          radius=18, fill=(0, 0, 0, 160))
        draw_rounded_rect(draw, (box_x, box_y, box_x + box_w, box_y + box_h),
                          radius=16, fill=(15, 23, 42, 235), outline=(255, 255, 255, 80), width=2)

        # Draw text with thick outline
        tx = box_x + box_padding_x
        ty = box_y + box_padding_y - 4

        # Shadow / outline
        for dx, dy in [(-3,0),(3,0),(0,-3),(0,3),(-2,-2),(2,2),(-2,2),(2,-2)]:
            draw.text((tx + dx, ty + dy), line_text, font=font_headline, fill=(0, 0, 0, 240))
        draw.text((tx, ty), line_text, font=font_headline, fill=color)

        curr_y += box_h + 16

    # 5. Sub-hook Pill Tag (y=curr_y + 10)
    sub_bbox = draw.textbbox((0, 0), spec["sub_tag"], font=font_sub)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_h = sub_bbox[3] - sub_bbox[1]
    sub_box_w = sub_w + 32
    sub_box_h = 44
    sub_box_x = (1080 - sub_box_w) // 2
    sub_box_y = curr_y + 10

    draw_rounded_rect(draw, (sub_box_x, sub_box_y, sub_box_x + sub_box_w, sub_box_y + sub_box_h),
                      radius=10, fill=(30, 41, 59, 230), outline=spec["accent_color"], width=2)
    draw.text((sub_box_x + 16, sub_box_y + (sub_box_h - sub_h) // 2 - 2),
              spec["sub_tag"], font=font_sub, fill=(241, 245, 249))

    # 6. Save final high-res PNG thumbnail
    out_dir = Path(spec["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    final_rgb = composed.convert("RGB")
    thumb_path = out_dir / "thumbnail.png"
    cover_path = out_dir / "cover_tiktok_9x16.png"

    final_rgb.save(thumb_path, "PNG", quality=98)
    final_rgb.save(cover_path, "PNG", quality=98)

    # Also save inside sys/runs/<job>/
    runs_dir = Path(f"sys/runs/{spec['job']}")
    if runs_dir.exists():
        final_rgb.save(runs_dir / "thumbnail.png", "PNG", quality=98)
        final_rgb.save(runs_dir / "cover_tiktok_9x16.png", "PNG", quality=98)

    print(f"Generated thumbnail for {spec['job']} -> {thumb_path}")
    return thumb_path

def main():
    for spec in THUMBNAIL_SPECS:
        create_thumbnail(spec)

if __name__ == "__main__":
    main()
