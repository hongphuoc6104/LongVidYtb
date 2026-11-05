import json
import os
from pathlib import Path

base_dir = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f")
specs_dir = base_dir / "style_proofs/specs"
refs_dir = base_dir / "competitor_refs"
catalog_file = base_dir / "style_proofs_benchmark_catalog.md"

spec_files = sorted(specs_dir.glob("*.json"))

lines = []
lines.append("# Danh Mục Đối Chiếu Phong Cách Kênh Đối Thủ Thực Tế (18 Kênh EN - 4 Phong Cách / Kênh)\n")
lines.append("> [!IMPORTANT]")
lines.append("> **Hướng Dẫn Duyệt & Lựa Chọn Phong Cách Chuẩn**:")
lines.append("> - Toàn bộ phong cách được bóc tách trực tiếp từ **ảnh thumbnail và khung hình thực tế của các kênh triệu view quốc tế** trong từng ngách.")
lines.append("> - Tích hợp phong cách **Prussian Blue Editorial Technical Blueprint** (kỹ sư compa vẽ quỹ đạo trắng trên nền xanh đậm Prussian với xe vàng leo dốc) từ ảnh mẫu bạn vừa cung cấp.")
lines.append("> - Toàn bộ 4 phong cách trên mỗi kênh đều có **bối cảnh phong phú, ánh sáng điện ảnh, chất liệu thật** — loại bỏ triệt để phong cách sticker/khoảng trắng rỗng trơ trọi cũ.")
lines.append("> - Bạn hãy xem hình ảnh thực tế của đối thủ và chọn phong cách bạn ưng ý nhất cho từng kênh (Ví dụ: `en-first-principles: Style 1 (Blueprint)`, `en-scale-and-bone: Style 1 (TierZoo RPG)`, v.v.).\n")
lines.append("---\n")

for idx, sf in enumerate(spec_files, 1):
    try:
        with open(sf, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        continue
    
    ch_slug = data.get("channel", sf.stem)
    niche = data.get("niche", "")
    scene = data.get("scene_description", "")
    styles = data.get("styles", {})
    
    lines.append(f"## {idx}. `{ch_slug}` — {niche}\n")
    if scene:
        lines.append(f"**Ý tưởng cảnh mẫu (Scene Context)**: *{scene}*\n")
    
    # Check competitor ref images
    c_ref_dir = refs_dir / ch_slug
    ref_imgs = []
    if c_ref_dir.is_dir():
        for ext in ("*.webp", "*.jpg", "*.png"):
            ref_imgs.extend(list(c_ref_dir.glob(ext)))
    
    # Filter for real video thumbnails (avoid avatar square icons if possible)
    video_thumbs = [img for img in ref_imgs if not img.name.endswith("_UC.jpg") and "_UC" not in img.stem]
    if not video_thumbs:
        video_thumbs = ref_imgs
    
    if video_thumbs:
        lines.append("### 📸 Ảnh Thật Tham Chiếu Từ Kênh Đối Thủ:\n")
        lines.append("````carousel")
        display_thumbs = video_thumbs[:4]
        for i, img in enumerate(display_thumbs):
            comp_name = img.stem.split("_")[0].capitalize()
            lines.append(f"![Ảnh thật đối thủ: {comp_name}]({img.resolve()})")
            if i < len(display_thumbs) - 1:
                lines.append("<!-- slide -->")
        lines.append("````\n")
    
    lines.append("### 🎨 4 Phong Cách Đề Xuất Dành Riêng Cho Kênh:\n")
    lines.append("| Phong cách | Đối thủ / Nguồn cảm hứng | Thẩm mỹ thị giác & Bảng màu |")
    lines.append("| :--- | :--- | :--- |")
    
    for sk, sdata in styles.items():
        sname = sdata.get("style_name", sk)
        comp = sdata.get("competitor", "")
        reason = sdata.get("reason", "")
        prompt = sdata.get("prompt", "")
        desc = reason if reason else prompt[:120] + "..."
        lines.append(f"| **{sk.upper()}**: {sname} | {comp} | {desc} |")
    
    lines.append("\n<details>")
    lines.append(f"<summary>🔍 Xem chi tiết Prompt đầy đủ của 4 styles kênh {ch_slug}</summary>\n")
    for sk, sdata in styles.items():
        lines.append(f"**{sk.upper()} ({sdata.get('style_name', sk)})**:\n```text\n{sdata.get('prompt', '')}\n```\n")
    lines.append("</details>\n")
    lines.append("---\n")

catalog_content = "\n".join(lines)
catalog_file.write_text(catalog_content, encoding="utf-8")
print(f"Successfully generated catalog: {len(catalog_content)} chars to {catalog_file}")
