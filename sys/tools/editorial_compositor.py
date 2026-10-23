"""Simple 2D Hand-Drawn Explainer Blueprint & Clean Watermark Healer.

Aligned strictly with the 11 user-supplied reference screenshots:
1. Pure 2D flat explainer aesthetic:
   - Bold, clean black outer contours with slight hand-drawn warmth (no cross-hatching or complex shading).
   - Pure white (#FFFFFF) backgrounds for isolated objects, quantities, and comparisons.
   - Simple flat solid color backgrounds (warm sand, terracotta, sage green, amber) for contextual scenes.
   - Simple contextual 2D cartoon characters (round head with skin tone, dot eyes, thin black stick limbs,
     flat clothing fills) only when a person is needed.
   - Short uppercase Vietnamese hand-drawn labels with simple brackets `{`, dashed lines `---`, arrows, or `=`.
2. Clean Post-Processing (`apply_editorial_overlay`):
   - Zero artificial HUD boxes, zero computer frames, zero paper yellowing/aging.
   - Seamless corner healing + subtle edge trim to completely remove the bottom-right AI sparkle watermark
     while keeping pure white (#FFFFFF) and flat color backgrounds 100% clean.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from flow_prompts import compile as compile_prompt
from PIL import Image, ImageDraw, ImageFilter

# 15 Simple 2D Hand-Drawn Explainer scenes modeled directly after the 11 reference screenshots
EDITORIAL_BLUEPRINT_SPECS: list[dict[str, Any]] = [
    {
        "slug": "column-comparison-illusion",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["HIỂU THẬT", "ẢO TƯỞNG"],
        "description": (
            "Simple 2D hand-drawn explainer comparison on a pure white #FFFFFF background. "
            "Two vertical rectangular bars side by side with bold clean black outlines and flat solid fills: "
            "a short sage-green bar on the left with a horizontal black dashed line across its top labeled 'HIỂU THẬT', "
            "and a tall terracotta-orange bar on the right rising far above the dashed line with a vertical double-headed "
            "black arrow on the right side labeled 'ẢO TƯỞNG'. No shading, no gradients, no hatching, generous white space."
        ),
    },
    {
        "slug": "three-notebooks-bracket-collector",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["TẢI VỀ", "BỎ ĐÓ", "QUÊN SẠCH"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "Three flat study folders sitting side by side in a row: on the left a terracotta folder with a bold black downward download arrow "
            "labeled 'TẢI VỀ', in the middle a closed dusty gray folder with a small cobweb on its corner labeled 'BỎ ĐÓ', and on the right "
            "an open folder with completely blank empty white pages labeled 'QUÊN SẠCH'. Above all three folders is one large horizontal black "
            "hand-drawn curly bracket grouping them together. Bold black outlines, flat solid colors, simple oval grounding shadows."
        ),
    },
    {
        "slug": "wooden-scale-evidence",
        "shot_type": "full_scene",
        "has_character": True,
        "allowed_text": ["LỜI ĐỒN", "BẰNG CHỨNG"],
        "description": (
            "Simple 2D hand-drawn explainer scene with a flat warm sand background and a flat sky-blue upper band. "
            "On the left stands a simple brown wooden balance scale: the left pan holds a pile of hollow white speech bubbles labeled 'LỜI ĐỒN' "
            "tilted high up in the air, while the right pan holds one solid terracotta document stamped with a red seal labeled 'BẰNG CHỨNG' "
            "weighing heavily down. On the right stands one simple 2D cartoon figure with a round tan-skinned head, two small black dot eyes, "
            "simple natural cartoon arms and hands, and a flat slate-blue shirt and brown pants looking calmly at the scale. "
            "Bold black outlines, flat solid colors, no shading lines, no bottom subtitle bars."
        ),
    },
    {
        "slug": "three-cutaway-books-rote",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["TÓM TẮT", "SAO CHÉP", "HỌC VẸT"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "Three closed study notebooks arranged horizontally in flat sage green, warm sand, and terracotta covers. "
            "Each notebook has a clean cutaway window on its front cover revealing an empty hollow interior with only a single small black "
            "question mark '?' inside, showing they lack core understanding. Below each notebook is a clean uppercase black hand-drawn label: "
            "'TÓM TẮT', 'SAO CHÉP', 'HỌC VẸT'. Bold black outlines, flat solid fills, pure white background."
        ),
    },
    {
        "slug": "quantity-not-equal-understanding",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["ĐỌC NHIỀU", "HIỂU SÂU"],
        "description": (
            "Simple 2D hand-drawn explainer comparison on a pure white #FFFFFF background. "
            "On the left sits a tall messy stack of eight closed gray and beige books labeled 'ĐỌC NHIỀU'. "
            "In the center is a large bold black not-equal sign '!=' drawn with thick clean brush strokes. "
            "On the right sits one open terracotta notebook showing three connected nodes linked by clear black arrows labeled 'HIỂU SÂU'. "
            "Bold clean black outlines, flat solid colors, simple oval grounding shadows, no hatching."
        ),
    },
    {
        "slug": "stopwatch-120s-attention",
        "shot_type": "macro_prop",
        "has_character": False,
        "allowed_text": ["120 GIÂY ĐẦU"],
        "description": (
            "Simple 2D hand-drawn explainer close-up on a pure white #FFFFFF background. "
            "A simple flat round analog stopwatch with bold black outlines in the center of the frame. The first two-minute wedge at the top-right "
            "of the clock face is filled with bright terracotta-orange, pointed to by a horizontal black measurement bracket labeled '120 GIÂY ĐẦU', "
            "while the rest of the clock face is flat light gray. Flat solid fills, bold black contours, pure white background."
        ),
    },
    {
        "slug": "mindmap-missing-core-idea",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["Ý TƯỞNG GỐC"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "An open research notebook on a study table mapping three hand-drawn branch lines from note cards at the left, right, and bottom "
            "toward an empty highlighted center box, with a bold black curved arrow pointing to the highlighted center box labeled 'Ý TƯỞNG GỐC'. "
            "Bold black outlines, flat solid colors."
        ),
    },
    {
        "slug": "character-connecting-mechanism",
        "shot_type": "full_scene",
        "has_character": True,
        "allowed_text": ["CƠ CHẾ CỐT LÕI"],
        "description": (
            "Simple 2D hand-drawn explainer scene with a uniform flat warm sand background. "
            "A simple 2D cartoon person with a round warm-brown head, simple dark hair, two black dot eyes, natural cartoon arms, "
            "and a flat sage-green shirt holds two interlocking wooden joinery blocks with mortise and tenon that click together in the center, surrounded by "
            "six short black radial emphasis ticks and the uppercase black label 'CƠ CHẾ CỐT LÕI' above. Bold clean black outlines, flat solid colors."
        ),
    },
    {
        "slug": "skimming-vs-deep-reading-pages",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["ĐỌC LƯỚT", "ĐỌC SÂU"],
        "description": (
            "Simple 2D hand-drawn explainer comparison on a pure white #FFFFFF background. "
            "On the left under the uppercase black label 'ĐỌC LƯỚT', an open white book page shows a dashed black arrow skimming across the surface "
            "and bouncing off without touching the text lines. On the right under the uppercase black label 'ĐỌC SÂU', an identical open book page "
            "shows a solid black arrow connecting three highlighted terracotta key points into a clear chain. Bold black outlines, flat solid colors."
        ),
    },
    {
        "slug": "single-brick-vs-wall",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["RỜI RẠC", "HỆ THỐNG"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "On the left under the uppercase black label 'RỜI RẠC', four flat terracotta bricks lie scattered apart on the floor. "
            "On the right under the uppercase black label 'HỆ THỐNG', four identical terracotta bricks are stacked neatly into a "
            "stable step pyramid. Bold clean black outlines, flat solid fills, pure white background."
        ),
    },
    {
        "slug": "wicker-sieve-three-stones",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["CHỌN LỌC"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A woven wicker sieve filtering raw field pebbles to reveal three polished terracotta stones resting on top beside the uppercase black label 'CHỌN LỌC'. "
            "Bold black outlines, flat solid colors, pure white background."
        ),
    },
    {
        "slug": "scale-two-weights",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["SỐ LƯỢNG", "CHẤT LƯỢNG"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A simple wooden balance beam on a central pivot: the left pan holds ten tiny hollow white circles and tilts upward "
            "labeled 'SỐ LƯỢNG'; the right pan holds one solid terracotta-orange sphere and tilts firmly downward labeled 'CHẤT LƯỢNG'. "
            "Bold clean black outlines, flat solid colors."
        ),
    },
    {
        "slug": "magnifying-glass-spot",
        "shot_type": "macro_prop",
        "has_character": False,
        "allowed_text": ["LỖ HỔNG"],
        "description": (
            "Simple 2D hand-drawn explainer close-up on a pure white #FFFFFF background. "
            "A simple flat warm-ochre magnifying glass with a bold black rim frames a row of three connected chain links where the "
            "middle link is open, pointed to by a short black arrow labeled 'LỖ HỔNG'. Bold black outlines, flat solid colors."
        ),
    },
    {
        "slug": "two-paths-arrow",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["LỐI MÒN", "HƯỚNG MỚI"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A flat sand-colored path splits into two branches: a wide crowded gray branch curving left into a dead-end wall labeled "
            "'LỐI MÒN', and a clean terracotta-orange branch curving right with a bold black arrow pointing forward labeled 'HƯỚNG MỚI'. "
            "Bold black outlines, flat solid colors."
        ),
    },
    {
        "slug": "three-steps-ladder",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["QUAN SÁT", "ĐẶT CÂU HỎI", "KIỂM CHỨNG"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "Three flat wooden step blocks rising from left to right in warm sand, sage green, and terracotta orange. "
            "A bold black curved arrow hops from step 1 to step 2 to step 3, with clean uppercase black labels below each step: "
            "'QUAN SÁT', 'ĐẶT CÂU HỎI', 'KIỂM CHỨNG'. Bold black outlines, flat solid colors."
        ),
    },
]


try:
    from tools.batch_4_scenes import BATCH_4_BLUEPRINT_SPECS
except ImportError:
    try:
        from sys.tools.batch_4_scenes import BATCH_4_BLUEPRINT_SPECS
    except ImportError:
        BATCH_4_BLUEPRINT_SPECS = {}


def build_editorial_task_spec(idx: int, batch_num: int, out_dir: Path) -> dict[str, Any]:
    """Compile a Registry 1.7.0 Simple 2D Explainer prompt matching the 11 reference screenshots."""
    if idx in BATCH_4_BLUEPRINT_SPECS:
        spec_item = BATCH_4_BLUEPRINT_SPECS[idx]
    else:
        spec_item = EDITORIAL_BLUEPRINT_SPECS[(idx - 1) % len(EDITORIAL_BLUEPRINT_SPECS)]
    shot_id = f"batch_{batch_num}_sc{idx:03d}"

    visual_data = {
        "description": (
            spec_item["description"].rstrip()
            + " Never render any white-on-black subtitle boxes, bottom video caption bars, or browser player controls."
        ),
        "aspect_ratio": "16:9",
        "shot_type": spec_item["shot_type"],
        "has_character": spec_item["has_character"],
        "allowed_text": spec_item["allowed_text"],
    }
    compiled = compile_prompt("NanoBanana2", "scene", visual_data, "1.7.0")

    return {
        "index": f"{idx:03d}",
        "id": shot_id,
        "jobId": shot_id,
        "filename": f"SC{idx:03d}.jpg",
        "prompt": compiled["prompt"],
        "ratio": "16:9",
        "shot_type": spec_item["shot_type"],
        "out_dir": str(out_dir),
        "max_retries": 3,
        "editorial_overlay": {
            "enabled": True,
            "overscan_crop": 0.015,
        },
    }


def apply_editorial_overlay(
    image_path: Path | str,
    overlay_cfg: dict[str, Any] | Path | str | None = None,
    target_path: Path | str | None = None,
) -> Path:
    """Cleanly heal the bottom-right provider watermark using row-wise boundary interpolation."""
    if isinstance(overlay_cfg, (str, Path)):
        target_path = overlay_cfg
        cfg = {}
    elif isinstance(overlay_cfg, dict):
        cfg = overlay_cfg
    else:
        cfg = {}

    p = Path(image_path)
    dest_p = Path(target_path) if target_path else p
    if not p.is_file():
        return dest_p

    if not cfg.get("enabled", True):
        return dest_p

    with Image.open(p) as im:
        im.load()
        orig_w, orig_h = im.size
        rgb = im.convert("RGB")

    # 1. Heal the bottom-right 4-point sparkle watermark by interpolating across clean left/right row boundaries
    sx = orig_w / 1376.0
    sy = orig_h / 768.0
    wm_x1 = max(8, orig_w - int(round(115 * sx)))
    wm_x2 = min(orig_w - 4, orig_w - int(round(24 * sx)))
    wm_y1 = max(8, orig_h - int(round(115 * sy)))
    wm_y2 = min(orig_h - 4, orig_h - int(round(24 * sy)))

    if wm_x2 > wm_x1 and wm_y2 > wm_y1:
        wm_w = wm_x2 - wm_x1
        wm_h = wm_y2 - wm_y1
        patch = Image.new("RGB", (wm_w, wm_h))
        for dy in range(wm_h):
            y = wm_y1 + dy
            # Sample clean pixels just outside the left and right edges of the watermark box on the same row
            l_rgb = rgb.getpixel(( max(0, wm_x1 - 4), y ))
            r_rgb = rgb.getpixel(( min(orig_w - 1, wm_x2 + 2), y ))
            for dx in range(wm_w):
                t = dx / max(1, wm_w - 1)
                c = (
                    int(round(l_rgb[0] * (1.0 - t) + r_rgb[0] * t)),
                    int(round(l_rgb[1] * (1.0 - t) + r_rgb[1] * t)),
                    int(round(l_rgb[2] * (1.0 - t) + r_rgb[2] * t)),
                )
                if c[0] >= 248 and c[1] >= 248 and c[2] >= 248:
                    c = (255, 255, 255)
                patch.putpixel((dx, dy), c)

        mask = Image.new("L", (wm_w, wm_h), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.rounded_rectangle([3, 3, wm_w - 4, wm_h - 4], radius=max(4, int(round(8 * sx))), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=max(2, int(round(3 * sx)))))
        rgb.paste(patch, (wm_x1, wm_y1), mask)

    # 2. Subtle overscan trim (1.5%) to guarantee crisp full-bleed edges at exact original resolution
    crop_frac = float(cfg.get("overscan_crop", 0.015))
    if 0.005 <= crop_frac <= 0.06:
        dx = int(round(orig_w * crop_frac))
        dy = int(round(orig_h * crop_frac))
        cropped = rgb.crop((dx, dy, orig_w - dx, orig_h - dy))
        rgb = cropped.resize((orig_w, orig_h), Image.Resampling.LANCZOS)

    out_fmt = "PNG" if dest_p.suffix.lower() == ".png" else "JPEG"
    if out_fmt == "PNG":
        rgb.save(dest_p, format="PNG")
    else:
        rgb.save(dest_p, format="JPEG", quality=95, optimize=True)

    return dest_p

