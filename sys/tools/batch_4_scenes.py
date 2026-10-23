"""90 Unique 2D Hand-Drawn Explainer Scene Blueprints for Batch 4 (SC101 - SC190).

Locked to Channel Pillar: 'Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức'.
Every scene is completely unique, following the 11 reference screenshots:
- Clean 2D flat hand-drawn illustration with bold black contours
- Pure white #FFFFFF background or flat warm solid fills (terracotta, sage green, sand, slate)
- Short uppercase Vietnamese labels with brackets, arrows, or dash lines
- Anti-repetition: 90 distinct concepts covering cognitive models, epistemology, and mental frameworks.
"""
from __future__ import annotations

from typing import Any

BATCH_4_BLUEPRINT_SPECS: dict[int, dict[str, Any]] = {
    101: {
        "slug": "learning-pyramid-retention",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["THỤ ĐỘNG", "CHỦ ĐỘNG"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A flat segmented triangle pyramid divided horizontally into two colored sections: "
            "the top light-gray section labeled 'THỤ ĐỘNG' with an icon of a closed book, "
            "and the large terracotta-orange base labeled 'CHỦ ĐỘNG' showing an open study easel with handwritten discussion cards. "
            "A bold black bracket on the right points to the base with '90% GHI NHỚ'. Bold black outlines, flat solid colors."
        ),
    },
    102: {
        "slug": "signal-vs-noise-prism",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["TÍN HIỆU", "NHIỄU LOẠN"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A thick gray beam of messy wavy lines enters a simple triangular glass prism from the left. "
            "From the right side emerge two separated distinct rays: a straight, crisp terracotta arrow pointing forward labeled 'TÍN HIỆU', "
            "and scattered faint gray dotted lines trailing downward labeled 'NHIỄU LOẠN'. Bold clean black contours, flat fills."
        ),
    },
    103: {
        "slug": "maslow-hammer-nail",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["CÔNG CỤ", "VẤN ĐỀ"],
        "description": (
            "Simple 2D hand-drawn explainer comparison on a pure white #FFFFFF background. "
            "In the center sits a large cartoon wooden hammer with a flat gray metal head labeled 'CÔNG CỤ'. "
            "To the right are three very different objects (a threaded metal bolt, a carved wooden peg, and a glass vase), but all three have "
            "flat gray nail heads drawn onto them labeled 'VẤN ĐỀ', showing the illusion of treating every problem like a nail. "
            "Bold black outer strokes, flat solid colors, pure white background."
        ),
    },
    104: {
        "slug": "dunning-kruger-curve",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["TỰ TIN ẢO", "HIỂU BIẾT THỰC"],
        "description": (
            "Simple 2D hand-drawn explainer graph on a pure white #FFFFFF background. "
            "Black coordinate axes with a hand-drawn curve that spikes sharply into a steep red-orange peak labeled 'TỰ TIN ẢO', "
            "then dips steeply into a valley, and slowly ascends up a steady sage-green slope on the right labeled 'HIỂU BIẾT THỰC'. "
            "A small cartoon dot marks the peak. Bold clean black lines, flat fills, generous whitespace."
        ),
    },
    105: {
        "slug": "chestertons-fence",
        "shot_type": "full_scene",
        "has_character": True,
        "allowed_text": ["ĐỪNG VỘI PHÁ"],
        "description": (
            "Simple 2D hand-drawn explainer scene with a flat warm sand background. "
            "Across the center stands a simple brown wooden picket fence with a locked gate. "
            "On the left, a simple 2D cartoon figure with a round tan head, dot eyes, and a sage-green shirt holds an axe, "
            "stopping to read a clean rectangular sign hanging on the fence post labeled 'ĐỪNG VỘI PHÁ'. "
            "Bold black outlines, flat solid colors, minimal hand-drawn aesthetic."
        ),
    },
    106: {
        "slug": "surface-phenomenon-deep-roots",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["HIỆN TƯỢNG", "BẢN CHẤT"],
        "description": (
            "Simple 2D hand-drawn explainer cross-section on a pure white #FFFFFF background. "
            "A horizontal black dashed ground line separates soil layers. A small green sprout with two leaves sticks above the surface labeled 'HIỆN TƯỢNG', "
            "while an extensive deep-terracotta network of taproots anchors deep underground occupying 85% of the frame labeled 'BẢN CHẤT'. "
            "Bold clean black outlines, flat solid colors, no complex gradients."
        ),
    },
    107: {
        "slug": "circle-of-competence",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["TRONG TẦM", "NGOÀI TẦM"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "Two concentric circles drawn with bold black brush strokes: the inner solid sage-green circle is labeled 'TRONG TẦM', "
            "and the outer dashed gray ring surrounding it is labeled 'NGOÀI TẦM' with small scattered question marks '?'. "
            "Bold contours, flat solid fills, clear intellectual contrast."
        ),
    },
    108: {
        "slug": "empirical-evidence-balance",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["ĐỊNH KIẾN", "DỮ LIỆU"],
        "description": (
            "Simple 2D hand-drawn explainer balance scale on a pure white #FFFFFF background. "
            "A flat black metal balance scale: the left pan carries a flimsy lightweight paper cloud labeled 'ĐỊNH KIẾN' tilted high up, "
            "while the right pan holds three heavy solid terracotta blocks stamped with checkmarks labeled 'DỮ LIỆU' pressing firmly down. "
            "Bold black outlines, flat solid fills."
        ),
    },
    109: {
        "slug": "cognitive-black-box",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["ĐẦU VÀO", "TƯ DUY", "ĐẦU RA"],
        "description": (
            "Simple 2D hand-drawn explainer flow on a pure white #FFFFFF background. "
            "From left to right: a flat sand-colored arrow labeled 'ĐẦU VÀO' points into a solid black cube with a subtle white question mark "
            "labeled 'TƯ DUY', and from the right of the cube emerges a crisp bright terracotta arrow labeled 'ĐẦU RA'. "
            "Bold outlines, flat solid fills, generous white space."
        ),
    },
    110: {
        "slug": "first-principles-blocks",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["THÁO RỜI", "TÁI TẠO"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "On the left, an assembled complex gray machine is broken into loose primitive geometric toy blocks (spheres, cubes, rods) labeled 'THÁO RỜI'. "
            "On the right, identical blocks are rebuilt into a clean, streamlined terracotta rocket labeled 'TÁI TẠO'. "
            "Bold black outlines, flat solid colors."
        ),
    },
    111: {
        "slug": "inversion-principle-path",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["TRÁNH THẤT BẠI"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A central straight pathway toward a golden goal flag. Instead of drawing the goal, five large red-orange X-marks and barricades "
            "block all dangerous side ravines and dead ends, with a bold uppercase black bracket labeled 'TRÁNH THẤT BẠI'. "
            "Bold clean outlines, flat fills, pure white background."
        ),
    },
    112: {
        "slug": "compass-vs-map",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["LA BÀN", "BẢN ĐỒ CŨ"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "On the left, a flat round brass compass with a crisp terracotta magnetic needle pointing North labeled 'LA BÀN'. "
            "On the right, a crumpled dusty gray parchment map with torn edges and faded paths labeled 'BẢN ĐỒ CŨ'. "
            "Bold black contours, flat solid fills, simple oval drop shadows."
        ),
    },
    113: {
        "slug": "pareto-80-20-balance",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["20% CỐT LÕI", "80% KẾT QUẢ"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "Two vertical rectangular bars: on the left a slim terracotta bar labeled '20% CỐT LÕI' connects via a thick curved black arrow "
            "to a massive wide sage-green bar on the right labeled '80% KẾT QUẢ'. Clean black outlines, flat solid fills, no cross-hatching."
        ),
    },
    114: {
        "slug": "productive-capacity-balance",
        "shot_type": "full_scene",
        "has_character": True,
        "allowed_text": ["NĂNG LỰC", "KẾT QUẢ"],
        "description": (
            "Simple 2D hand-drawn explainer scene with a flat warm sand background. "
            "A simple 2D cartoon character in a sage-green shirt feeds a calm white cartoon goose resting on a nest labeled 'NĂNG LỰC'. "
            "Beside the nest sits one solid golden egg labeled 'KẾT QUẢ'. A dashed black equal sign '=' balances the bird and egg. "
            "Bold black outlines, flat solid colors."
        ),
    },
    115: {
        "slug": "sunk-cost-trap",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["CHI PHÍ CHÌM", "DỪNG LẠI"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A deep black vertical pit in the ground filled with buried gold coins labeled 'CHI PHÍ CHÌM'. "
            "Above the pit, a hand holds a shovel in mid-air, with a bold red stop-sign hand pointing away toward an open green field labeled 'DỪNG LẠI'. "
            "Bold clean outlines, flat solid fills."
        ),
    },
    116: {
        "slug": "occams-razor-scissor",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["ĐƠN GIẢN NHẤT"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A tangle of eight redundant messy gray wires being snipped by a pair of sharp black cartoon scissors, leaving only one clean, "
            "direct terracotta wire connecting node A to node B under the uppercase label 'ĐƠN GIẢN NHẤT'. Bold black outlines, flat fills."
        ),
    },
    117: {
        "slug": "confirmation-bias-filter",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["BỘ LỌC ĐỊNH KIẾN"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A wooden sorter box labeled 'BỘ LỌC ĐỊNH KIẾN' receives various wooden blocks (spheres, prisms, cubes). "
            "The slotted top panel only lets through circular discs that match its own cut slot, while bouncing all angular blocks away. "
            "Bold clean black outlines, terracotta and sage-green flat colors."
        ),
    },
    118: {
        "slug": "eisenhower-matrix",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["QUAN TRỌNG", "KHẨN CẤP"],
        "description": (
            "Simple 2D hand-drawn explainer 2x2 grid on a pure white #FFFFFF background. "
            "Four quadrant boxes: the top-left quadrant is highlighted in vibrant terracotta-orange with a bold star labeled 'LÀM NGAY', "
            "while the axes are labeled 'QUAN TRỌNG' vertically and 'KHẨN CẤP' horizontally with black arrows. Bold outlines, flat solid fills."
        ),
    },
    119: {
        "slug": "cognitive-domino",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["QUAN ĐIỂM ĐÚNG"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A row of five standing dominoes in escalating sizes from left to right. The smallest domino on the far left is painted terracotta-orange "
            "labeled 'QUAN ĐIỂM ĐÚNG', tipping forward to topple the giant gray obstacles behind it. Bold contours, flat solid fills."
        ),
    },
    120: {
        "slug": "correlation-not-causation",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["TRÙNG HỢP", "NHÂN QUẢ"],
        "description": (
            "Simple 2D hand-drawn explainer comparison on a pure white #FFFFFF background. "
            "Two parallel wavy line graphs rising together labeled 'TRÙNG HỢP' crossed out by a large red hand-drawn 'X'. "
            "Below it, a wooden rocker bar directly tips a standing wooden block labeled 'NHÂN QUẢ' with a green checkmark. "
            "Bold black outlines, flat solid colors."
        ),
    },
    121: {
        "slug": "feynman-simple-explanation",
        "shot_type": "full_scene",
        "has_character": True,
        "allowed_text": ["ĐƠN GIẢN HÓA"],
        "description": (
            "Simple 2D hand-drawn explainer scene with a flat warm sand background. "
            "A simple 2D cartoon adult with round head and sage-green shirt kneels down to explain an open sketchpad to a small cartoon child. "
            "The sketchpad shows a simple sun and flower. Above them floats the uppercase black label 'ĐƠN GIẢN HÓA'. "
            "Bold black contours, flat solid colors, minimal expressive characters."
        ),
    },
    122: {
        "slug": "double-loop-learning",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["QUY TRÌNH", "GIẢ ĐỊNH"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "Two nested circular feedback loops: an inner gray loop cycling between 'HÀNH ĐỘNG' and 'KẾT QUẢ' labeled 'QUY TRÌNH', "
            "and a larger bold terracotta outer loop that questions the underlying foundation labeled 'GIẢ ĐỊNH'. Bold outlines, flat solid fills."
        ),
    },
    123: {
        "slug": "logical-fallacy-lens",
        "shot_type": "macro_prop",
        "has_character": False,
        "allowed_text": ["NGỤY BIỆN"],
        "description": (
            "Simple 2D hand-drawn explainer close-up on a pure white #FFFFFF background. "
            "A large flat black magnifying glass placed over a paragraph of neat mock text. Inside the lens glass, an invisible crack in the logic "
            "is highlighted in sharp terracotta-orange with an exclamation mark '!' labeled 'NGỤY BIỆN'. Bold outlines, flat solid colors."
        ),
    },
    124: {
        "slug": "seed-to-ecosystem",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["MẦM MỐNG", "HỆ SINH THÁI"],
        "description": (
            "Simple 2D hand-drawn explainer progression on a pure white #FFFFFF background. "
            "On the left, a single small brown seed in soil labeled 'MẦM MỐNG'. A black dashed arrow leads to the right, showing three mature "
            "flat green trees with interconnected root networks beneath the ground labeled 'HỆ SINH THÁI'. Bold black outlines, flat solid fills."
        ),
    },
    125: {
        "slug": "curse-of-knowledge-bridge",
        "shot_type": "visual_diagram",
        "has_character": True,
        "allowed_text": ["KHOẢNG CÁCH", "GIAO TIẾP"],
        "description": (
            "Simple 2D hand-drawn explainer scene on a pure white #FFFFFF background. "
            "Two cliffs separated by a wide canyon labeled 'KHOẢNG CÁCH'. On the left cliff stands a mentor holding an intricate rolled map; "
            "on the right cliff stands an ordinary listener with open hands. A flat wooden suspension bridge labeled 'GIAO TIẾP' connects both sides. "
            "Bold black outlines, flat solid colors."
        ),
    },
    126: {
        "slug": "cognitive-filter-mesh",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["MẮT LƯỚI", "CHỌN LỌC"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A woven wire sieve held horizontally labeled 'MẮT LƯỚI'. Small fine sand falls through completely, while three large solid terracotta "
            "nuggets of genuine insight remain trapped at the top labeled 'CHỌN LỌC'. Bold black outlines, flat solid fills."
        ),
    },
    127: {
        "slug": "archimedes-lever",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["ĐIỂM TỰA", "ĐÒN BẨY"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A long black lever beam resting on a solid brown triangular fulcrum labeled 'ĐIỂM TỰA'. "
            "A tiny feather-light hand presses the long end labeled 'ĐÒN BẨY', effortlessly lifting a giant heavy boulder on the short end. "
            "Bold clean outlines, flat fills, pure white background."
        ),
    },
    128: {
        "slug": "attention-hourglass",
        "shot_type": "macro_prop",
        "has_character": False,
        "allowed_text": ["SỰ TẬP TRUNG"],
        "description": (
            "Simple 2D hand-drawn explainer close-up on a pure white #FFFFFF background. "
            "A classic hourglass with clean black contours. The upper bulb contains vibrant terracotta sand trickling down through a narrow "
            "glass neck into the lower bulb, with a horizontal black bracket labeled 'SỰ TẬP TRUNG'. Bold black outlines, flat solid fills."
        ),
    },
    129: {
        "slug": "map-is-not-territory",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["BẢN ĐỒ", "THỰC TẠI"],
        "description": (
            "Simple 2D hand-drawn explainer comparison on a pure white #FFFFFF background. "
            "On the left, a flat square paper map with simplified straight lines labeled 'BẢN ĐỒ'. "
            "In the center, a bold black not-equal sign '!='. On the right, a rich 3D-perspective landscape with mountains, rivers, and trees "
            "drawn in flat 2D lines labeled 'THỰC TẠI'. Bold black outlines, flat solid colors."
        ),
    },
    130: {
        "slug": "false-dilemma-spectrum",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["PHỔ MÀU", "ĐEN TRẮNG"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "At the bottom, two stark rigid blocks: pure black and pure white labeled 'ĐEN TRẮNG' crossed with a red line. "
            "Above them arches a broad horizontal spectrum of five warm tones (sand, ochre, terracotta, sage green, slate) labeled 'PHỔ MÀU'. "
            "Bold black outlines, flat solid fills."
        ),
    },
    131: {
        "slug": "trojan-horse-bias",
        "shot_type": "full_scene",
        "has_character": False,
        "allowed_text": ["ẨN HỌA"],
        "description": (
            "Simple 2D hand-drawn explainer illustration with a flat warm sand background. "
            "A cartoon wooden horse on small wheels standing outside a fortified gate. A small cutaway hatch on the horse's flank reveals "
            "a glowing red-orange exclamation mark '!' inside labeled 'ẨN HỌA'. Bold clean black contours, flat solid fills."
        ),
    },
    132: {
        "slug": "decision-tree-branches",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["LỰA CHỌN", "KẾT QUẢ"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A trunk on the left labeled 'LỰA CHỌN' splits into three clean branches, each branch splitting into two leaves at the right "
            "labeled 'KẾT QUẢ'. One optimal path is highlighted in solid terracotta with a green checkmark. Bold outlines, flat solid fills."
        ),
    },
    133: {
        "slug": "ooda-loop-cycle",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["QUAN SÁT", "HÀNH ĐỘNG"],
        "description": (
            "Simple 2D hand-drawn explainer circle on a pure white #FFFFFF background. "
            "Four curved arrows forming a continuous circle with clean uppercase labels: 'QUAN SÁT' at 12 o'clock, 'ĐỊNH HƯỚNG' at 3 o'clock, "
            "'QUYẾT ĐỊNH' at 6 o'clock, and 'HÀNH ĐỘNG' at 9 o'clock. Bold black outlines, flat solid colors."
        ),
    },
    134: {
        "slug": "blind-spot-mirror",
        "shot_type": "macro_prop",
        "has_character": False,
        "allowed_text": ["ĐIỂM MÙ"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A car side-view mirror with bold black outlines. A dashed cone of vision extends backward, leaving an empty hatched gray zone "
            "at the bottom labeled 'ĐIỂM MÙ' containing an unspotted red triangle. Bold contours, flat solid fills, pure white background."
        ),
    },
    135: {
        "slug": "thought-experiment-train",
        "shot_type": "full_scene",
        "has_character": True,
        "allowed_text": ["THỬ NGHIỆM"],
        "description": (
            "Simple 2D hand-drawn explainer scene with a flat warm sand background. "
            "A simple 2D cartoon figure sits at a wooden table with eyes closed in contemplation. Above their head floats a clean thought bubble "
            "containing a speeding flat cartoon train with a lightning bolt striking its front and back labeled 'THỬ NGHIỆM'. "
            "Bold black outlines, flat solid colors."
        ),
    },
    136: {
        "slug": "parkinsons-law-balloon",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["TRÌ HOÃN", "GIỚI HẠN"],
        "description": (
            "Simple 2D hand-drawn explainer comparison on a pure white #FFFFFF background. "
            "On the left, a giant loose air balloon expanding to fill an entire large glass box labeled 'TRÌ HOÃN'. "
            "On the right, an identical amount of air compressed inside a small, tight terracotta box with a timer labeled 'GIỚI HẠN'. "
            "Bold black outlines, flat solid fills."
        ),
    },
    137: {
        "slug": "goodharts-law-metric",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["CHỈ SỐ", "BẢN CHẤT"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A pointer on a dashboard dial pegged all the way to maximum '100%' labeled 'CHỈ SỐ', but behind the dial, the engine "
            "is smoking and disconnected labeled 'BẢN CHẤT'. Bold black contours, terracotta and gray flat fills."
        ),
    },
    138: {
        "slug": "bandwagon-sheep-flock",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["ĐÁM ĐÔNG", "ĐỘC LẬP"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A large cluster of identical white cartoon sheep all running blindly toward the left cliff edge labeled 'ĐÁM ĐÔNG'. "
            "On the right, a single terracotta sheep calmly walks up a green hill in the opposite direction labeled 'ĐỘC LẬP'. "
            "Bold black contours, flat solid fills."
        ),
    },
    139: {
        "slug": "weakest-link-chain",
        "shot_type": "macro_prop",
        "has_character": False,
        "allowed_text": ["MẮT XÍCH YẾU"],
        "description": (
            "Simple 2D hand-drawn explainer close-up on a pure white #FFFFFF background. "
            "A horizontal chain of five thick iron links under tension. The middle link is made of thin brittle terracotta pottery and "
            "has a visible crack running down its side labeled 'MẮT XÍCH YẾU'. Bold black outlines, flat solid fills."
        ),
    },
    140: {
        "slug": "zettelkasten-slipbox",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["MẠNG LƯỚI THẺ"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "An open wooden desktop card file drawer. Six index cards hover above the drawer in mid-air, connected to one another by crisp "
            "black dotted lines forming an interconnected web labeled 'MẠNG LƯỚI THẺ'. Bold clean outlines, flat solid colors."
        ),
    },
    141: {
        "slug": "syntopical-reading-prism",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["ĐỐI CHIẾU", "TỔNG HỢP"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "Four different open books in a circle, each shooting a colored ray toward a central glowing terracotta core. "
            "A horizontal label at the top reads 'ĐỐI CHIẾU', and an arrow from the core points down to 'TỔNG HỢP'. Bold black outlines, flat fills."
        ),
    },
    142: {
        "slug": "spaced-repetition-curve",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["ÔN TẬP ĐÚNG LÚC"],
        "description": (
            "Simple 2D hand-drawn explainer chart on a pure white #FFFFFF background. "
            "Ebbinghaus forgetting curve graph. A steep falling curve is bumped upward by three successive green upward arrows representing reviews, "
            "flattening the memory curve near 100% retention labeled 'ÔN TẬP ĐÚNG LÚC'. Bold black outlines, flat solid fills."
        ),
    },
    143: {
        "slug": "system-1-system-2",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["TRỰC GIÁC", "SUY NGẪM"],
        "description": (
            "Simple 2D hand-drawn explainer comparison on a pure white #FFFFFF background. "
            "Two side-by-side study desks: on the left desk an energetic yellow hare dashes forward making a quick leap labeled 'TRỰC GIÁC', "
            "and on the right desk a steady green tortoise solves step-by-step formulas in an open notebook labeled 'SUY NGẪM'. Bold black contours, flat solid fills."
        ),
    },
    144: {
        "slug": "anchoring-bias-anchor",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["MỎ NEO ẢO"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A hot-air balloon trying to ascend into the sky, but held firmly to the ground by a heavy concrete mooring weight labeled 'MỎ NEO ẢO' "
            "engraved with arbitrary starting numbers. Bold clean black outlines, flat solid colors, pure white background."
        ),
    },
    145: {
        "slug": "framing-effect-frames",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["GÓC NHÌN"],
        "description": (
            "Simple 2D hand-drawn explainer comparison on a pure white #FFFFFF background. "
            "Two identical glasses filled with liquid to the exact 50% midpoint. The left glass is in a dark somber frame labeled 'VƠI MỘT NỬA', "
            "while the right glass is in a bright terracotta frame labeled 'ĐẦY MỘT NỬA'. Above both is the label 'GÓC NHÌN'. Bold black outlines."
        ),
    },
    146: {
        "slug": "loss-aversion-scale",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["NỖI SỢ MẤT"],
        "description": (
            "Simple 2D hand-drawn explainer balance on a pure white #FFFFFF background. "
            "A balance scale where losing a single 100$ coin on the left pan weighs down twice as heavily as gaining two 100$ coins on the right pan, "
            "with a large warning symbol and the label 'NỖI SỢ MẤT'. Bold clean black contours, flat solid fills."
        ),
    },
    147: {
        "slug": "survivorship-bias-plane",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["DỮ LIỆU THIẾU"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A top-down silhouette of a cartoon WW2 bomber plane with red dots on the wings and fuselage. A dashed green circle highlights "
            "the completely unmarked engines and cockpit with an arrow labeled 'DỮ LIỆU THIẾU' (bọc giáp nơi không có vết đạn). Bold black outlines."
        ),
    },
    148: {
        "slug": "rube-goldberg-complexity",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["RẮM RỐI"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "An absurdly over-complicated contraption of ramps, pulleys, bowling balls, and candles spanning the entire frame just to flip a single "
            "light switch, labeled 'RẮM RỐI' with a red 'X'. Bold clean black outlines, flat solid colors."
        ),
    },
    149: {
        "slug": "socratic-question-spiral",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["TẠI SAO?", "BẢN CHẤT?"],
        "description": (
            "Simple 2D hand-drawn explainer spiral on a pure white #FFFFFF background. "
            "A downward spiral arrow drilling through surface layers into the deep bedrock. At each tier of the spiral, a small speech bubble asks "
            "'TẠI SAO?' leading to the glowing bedrock core labeled 'BẢN CHẤT?'. Bold black contours, flat solid fills."
        ),
    },
    150: {
        "slug": "johari-window-grid",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["VÙNG MÙ", "THẤU CẢM"],
        "description": (
            "Simple 2D hand-drawn explainer 4-pane window on a pure white #FFFFFF background. "
            "A four-pane window frame: 'CÔNG KHAI', 'VÙNG MÙ' (bạn không thấy nhưng người khác thấy), 'VÙNG KÍN', và 'CHƯA BIẾT'. "
            "The blind spot pane is highlighted in terracotta with the label 'THẤU CẢM'. Bold black outlines, flat solid fills."
        ),
    },
    151: {
        "slug": "hanlons-razor-shield",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["BAO DUNG"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A protective flat sage-green shield deflecting dark stormy lightning bolts. Behind the shield sits a calm smiling face with the "
            "label 'BAO DUNG', showing an understanding that clumsiness is not malice. Bold clean black contours, flat fills."
        ),
    },
    152: {
        "slug": "peak-end-rule-graph",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["ĐỈNH CAO", "KẾT THÚC"],
        "description": (
            "Simple 2D hand-drawn explainer graph on a pure white #FFFFFF background. "
            "A timeline curve of an experience: two points are highlighted with bright stars: the highest emotional peak labeled 'ĐỈNH CAO', "
            "and the final moment labeled 'KẾT THÚC', showing how memory selectively retains only these two anchors. Bold black lines, flat fills."
        ),
    },
    153: {
        "slug": "local-maxima-hills",
        "shot_type": "visual_diagram",
        "has_character": True,
        "allowed_text": ["ĐỈNH THẤP", "ĐỈNH CAO"],
        "description": (
            "Simple 2D hand-drawn explainer landscape on a pure white #FFFFFF background. "
            "A small cartoon figure stands atop a small hill labeled 'ĐỈNH THẤP'. To reach the majestic mountain peak in the distance labeled 'ĐỈNH CAO', "
            "the figure must first descend through a dark valley. Bold black outlines, flat terracotta and sage-green fills."
        ),
    },
    154: {
        "slug": "hedonic-treadmill",
        "shot_type": "white_isolated",
        "has_character": True,
        "allowed_text": ["VÒNG QUAY"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A simple 2D cartoon character walking continuously along a circular stone garden track labeled 'VÒNG QUAY', "
            "chasing a golden marker that remains at the exact same distance. Bold black contours, flat solid fills."
        ),
    },
    155: {
        "slug": "cognitive-flexibility-tree",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["LINH HOẠT", "CỨNG NHẮC"],
        "description": (
            "Simple 2D hand-drawn explainer comparison on a pure white #FFFFFF background. "
            "On the left, a stiff brittle wooden post snapped in half by the wind labeled 'CỨNG NHẮC'. "
            "On the right, a slender green bamboo stalk gracefully bowing to the gale and springing back intact labeled 'LINH HOẠT'. Bold outlines."
        ),
    },
    156: {
        "slug": "ladder-of-abstraction",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["CỤ THỂ", "TRỪU TƯỢNG"],
        "description": (
            "Simple 2D hand-drawn explainer vertical ladder on a pure white #FFFFFF background. "
            "A 4-rung wooden ladder: the bottom rung shows a specific red apple labeled 'CỤ THỂ'; the top rung shows an abstract mathematical symbol "
            "labeled 'TRỪU TƯỢNG', with a double-headed arrow connecting the spectrum. Bold clean black outlines, flat solid fills."
        ),
    },
    157: {
        "slug": "overfitting-mental-model",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["GƯỢNG ÉP"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A round wooden peg being violently hammered into a square hole, causing splinters and deformation, under the uppercase label 'GƯỢNG ÉP'. "
            "Bold black outlines, flat solid colors, pure white background."
        ),
    },
    158: {
        "slug": "epistemic-humility-drop",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["KHIÊM TỐN"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A single glowing water drop falling onto a vast, calm ocean surface, sending concentric ripple rings expanding outward labeled 'KHIÊM TỐN'. "
            "Minimalist, poetic, bold clean black contours, flat slate-blue and sand fills."
        ),
    },
    159: {
        "slug": "tragedy-of-the-commons",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["LỢI ÍCH CHUNG"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A central circular green pasture labeled 'LỢI ÍCH CHUNG' being overgrazed down to barren dry dirt by too many cartoon cattle grazing from all sides, "
            "showing depleted collective resources. Bold black outlines, flat solid fills."
        ),
    },
    160: {
        "slug": "lindy-effect-hourglass",
        "shot_type": "macro_prop",
        "has_character": False,
        "allowed_text": ["TRƯỜNG TỒN"],
        "description": (
            "Simple 2D hand-drawn explainer close-up on a pure white #FFFFFF background. "
            "An ancient weathered stone tablet carved with timeless geometric truths sitting undamaged beside a pile of broken modern digital gadgets, "
            "labeled 'TRƯỜNG TỒN'. Bold black contours, flat solid fills, pure white background."
        ),
    },
    161: {
        "slug": "strawman-fallacy",
        "shot_type": "full_scene",
        "has_character": True,
        "allowed_text": ["NGƯỜI RƠM"],
        "description": (
            "Simple 2D hand-drawn explainer scene with a flat warm sand background. "
            "A cartoon debater fiercely attacking a flimsy scarecrow made of straw and burlap labeled 'NGƯỜI RƠM', "
            "while the actual intellectual opponent stands calmly to the side watching with folded arms. Bold black outlines, flat fills."
        ),
    },
    162: {
        "slug": "black-swan-event",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["BẤT NGỜ"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A flock of twenty identical white swans swimming in a pond, with a single striking, elegant black swan in the foreground with "
            "terracotta beak spreading its wings labeled 'BẤT NGỜ'. Bold clean black contours, flat solid fills."
        ),
    },
    163: {
        "slug": "antifragile-hydra-crystal",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["CHỐNG GÃY VỠ"],
        "description": (
            "Simple 2D hand-drawn explainer comparison on a pure white #FFFFFF background. "
            "Three items struck by a hammer: a fragile glass teacup shatters; a robust stone resists; but an antifragile geometric crystal "
            "grows larger and sprouts two new facets labeled 'CHỐNG GÃY VỠ'. Bold black outlines, flat solid colors."
        ),
    },
    164: {
        "slug": "red-queen-running",
        "shot_type": "full_scene",
        "has_character": True,
        "allowed_text": ["TIẾN HÓA"],
        "description": (
            "Simple 2D hand-drawn explainer scene with a flat warm sand background. "
            "A 2D cartoon figure sprinting at full speed on a moving conveyor belt, maintaining position relative to a static landmark tree, "
            "illustrating the need to adapt continuously just to survive labeled 'TIẾN HÓA'. Bold black contours, flat solid fills."
        ),
    },
    165: {
        "slug": "tunnel-vision-cone",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["TẦM NHÌN RỘNG"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "Two eyes: one looks through a narrow pipe seeing only a tiny red dot; the other has an expansive 180-degree wide-angle cone "
            "revealing the entire vibrant landscape labeled 'TẦM NHÌN RỘNG'. Bold black outlines, flat solid fills."
        ),
    },
    166: {
        "slug": "second-order-thinking",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["HỆ QUẢ PHỤ"],
        "description": (
            "Simple 2D hand-drawn explainer progression on a pure white #FFFFFF background. "
            "Step 1: 'HÀNH ĐỘNG' -> Step 2: 'KẾT QUẢ ĐẦU' -> Step 3: a large unexpected secondary consequence labeled 'HỆ QUẢ PHỤ' "
            "curving back to create a new challenge. Bold clean black contours, flat solid colors."
        ),
    },
    167: {
        "slug": "cognitive-load-gauge",
        "shot_type": "macro_prop",
        "has_character": False,
        "allowed_text": ["QUÁ TẢI"],
        "description": (
            "Simple 2D hand-drawn explainer dial on a pure white #FFFFFF background. "
            "A pressure gauge dial divided into green (optimal), yellow (working memory), and a flashing red-orange zone labeled 'QUÁ TẢI' "
            "where the needle is vibrating violently. Bold black outlines, flat solid fills, pure white background."
        ),
    },
    168: {
        "slug": "feedback-loop-spiral",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["PHẢN HỒI KÉP"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A spiral vortex of alternating black and terracotta arrows feeding into each other, demonstrating compounding momentum "
            "labeled 'PHẢN HỒI KÉP'. Bold clean black contours, flat solid fills, generous white space."
        ),
    },
    169: {
        "slug": "deconstruction-scalpel",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["BÓC TÁCH"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A clean surgical cartoon scalpel peeling back the decorative outer veneer of a complex argument box to reveal its raw skeletal "
            "mathematical structure labeled 'BÓC TÁCH'. Bold black outlines, flat solid colors."
        ),
    },
    170: {
        "slug": "measurement-yardstick",
        "shot_type": "macro_prop",
        "has_character": False,
        "allowed_text": ["CHUẨN MỰC"],
        "description": (
            "Simple 2D hand-drawn explainer close-up on a pure white #FFFFFF background. "
            "A crisp wooden carpenter ruler with millimeter tick marks laid alongside three irregular wavy sticks, showing standard objective "
            "calibration labeled 'CHUẨN MỰC'. Bold contours, flat solid fills, pure white background."
        ),
    },
    171: {
        "slug": "explanatory-depth-bicycle",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["TƯỞNG ĐÃ BIẾT"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A cartoon bicycle where the chain is accidentally drawn connecting the front wheel to the handlebar, illustrating the illusion "
            "of explanatory depth labeled 'TƯỞNG ĐÃ BIẾT'. Bold black outlines, flat terracotta and sage fills."
        ),
    },
    172: {
        "slug": "inertia-heavy-boulder",
        "shot_type": "visual_diagram",
        "has_character": True,
        "allowed_text": ["QUÁN TÍNH"],
        "description": (
            "Simple 2D hand-drawn explainer scene on a pure white #FFFFFF background. "
            "A simple 2D stick-figure leaning their whole body against a massive round stone boulder at rest labeled 'QUÁN TÍNH'. "
            "Once rolling, the boulder is unstoppable. Bold clean black outlines, flat solid colors."
        ),
    },
    173: {
        "slug": "social-bias-glasses",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["GÁC LẠI ĐỊNH KIẾN"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A pair of retro spectacles resting folded on a table. The lenses are tinted dark murky purple, but through the clear space above the frame, "
            "the world is bright and true labeled 'GÁC LẠI ĐỊNH KIẾN'. Bold contours, flat solid colors."
        ),
    },
    174: {
        "slug": "bottleneck-flow-pipe",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["ĐIỂM NGHẼN"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A wide pipe carrying a thick flow of blue water suddenly constricting into an ultra-narrow throat labeled 'ĐIỂM NGHẼN', "
            "causing water to backup and trickle slowly out the other side. Bold black outlines, flat solid fills."
        ),
    },
    175: {
        "slug": "phase-shift-boiling",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["BƯỚC NGOẶT"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A simple cartoon kettle on a stove. From 0 to 99 degrees, water stays liquid; at 100 degrees, steam bursts powerfully upward "
            "labeled 'BƯỚC NGOẶT' (sự tích lũy lượng biến thành chất). Bold black outlines, flat solid fills."
        ),
    },
    176: {
        "slug": "cognitive-blueprint-roll",
        "shot_type": "macro_prop",
        "has_character": False,
        "allowed_text": ["BẢN THIẾT KẾ"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "An unrolled blueprint scroll on a desk showing clean white technical schematics and arrows labeled 'BẢN THIẾT KẾ', "
            "with a pencil and compass resting on the border. Bold black contours, flat slate-blue and sand fills."
        ),
    },
    177: {
        "slug": "counter-intuitive-buoy",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["PHẢN TRỰC GIÁC"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A bright orange ring buoy floating steadily against a turbulent opposing current labeled 'PHẢN TRỰC GIÁC', "
            "showing that the most effective solution is often opposite to initial instincts. Bold black contours, flat solid fills."
        ),
    },
    178: {
        "slug": "intrinsic-value-scale",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["THỰC CHẤT", "BỀ NGOÀI"],
        "description": (
            "Simple 2D hand-drawn explainer comparison on a pure white #FFFFFF background. "
            "On the left, a solid nugget of pure gold wrapped in plain brown butcher paper labeled 'THỰC CHẤT'. "
            "On the right, an empty cardboard box covered in glossy glitter and giant ribbons labeled 'BỀ NGOÀI'. Bold black outlines."
        ),
    },
    179: {
        "slug": "double-edged-sword",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["HAI MẶT"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A symmetric cartoon broadsword standing vertically in the center. The left edge cuts through confusion labeled 'KHAI SÁNG'; "
            "the right edge poses a risk of misuse labeled 'NGUY CƠ'. Center label reads 'HAI MẶT'. Bold contours, flat solid colors."
        ),
    },
    180: {
        "slug": "overton-window-slider",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["RANH GIỚI"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A horizontal spectrum of ideas from 'KHÔNG TƯỞNG' to 'PHỔ BIẾN'. A rectangular slider window highlights the middle section "
            "currently accepted by society labeled 'RANH GIỚI'. Bold clean black contours, flat solid colors."
        ),
    },
    181: {
        "slug": "mental-first-aid-kit",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["TỈNH THỨC"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "An open red first-aid case containing mental clarity tools: a notebook, a breathing timer, and an emergency stop button "
            "labeled 'TỈNH THỨC'. Bold clean black contours, flat solid fills, pure white background."
        ),
    },
    182: {
        "slug": "micro-macro-telescope",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["VI MÔ", "VĨ MÔ"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A dual optical instrument: looking through one eyepiece reveals tiny bacteria labeled 'VI MÔ'; looking through the other "
            "reveals vast galaxy spirals labeled 'VĨ MÔ'. Bold clean black outlines, flat solid colors."
        ),
    },
    183: {
        "slug": "boiling-frog-thermometer",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["TIỆM TIẾN"],
        "description": (
            "Simple 2D hand-drawn explainer comparison on a pure white #FFFFFF background. "
            "A cartoon pot of warm water with a thermometer mercury column creeping imperceptibly upward millimeter by millimeter "
            "labeled 'TIỆM TIẾN', showing slow erosion that escapes notice until too late. Bold black outlines, flat solid colors."
        ),
    },
    184: {
        "slug": "quantitative-qualitative-axis",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["ĐỊNH LƯỢNG", "ĐỊNH TÍNH"],
        "description": (
            "Simple 2D hand-drawn explainer coordinate plane on a pure white #FFFFFF background. "
            "Horizontal axis labeled 'ĐỊNH LƯỢNG' (số liệu, thước đo) intersects vertical axis labeled 'ĐỊNH TÍNH' (chiều sâu, cảm nhận). "
            "In the optimal top-right quadrant shines a bright terracotta badge. Bold clean black outlines, flat solid fills."
        ),
    },
    185: {
        "slug": "information-filter-bins",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["RÁC THÔNG TIN", "TINH HOA"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "Two side-by-side recycling bins: a dull gray bin overflowing with clickbait papers labeled 'RÁC THÔNG TIN', "
            "and a clean terracotta chest holding three bound leather volumes labeled 'TINH HOA'. Bold black contours, flat solid fills."
        ),
    },
    186: {
        "slug": "flywheel-momentum",
        "shot_type": "visual_diagram",
        "has_character": True,
        "allowed_text": ["BÁNH ĐÀ TRI THỨC"],
        "description": (
            "Simple 2D hand-drawn explainer diagram on a pure white #FFFFFF background. "
            "A heavy circular stone potter's wheel with black rotation arrows. A cartoon artisan leans forward pushing the stone rim "
            "with deliberate effort at the start, gradually building sustained rotational momentum labeled 'BÁNH ĐÀ TRI THỨC'. "
            "Bold clean outlines, flat solid fills."
        ),
    },
    187: {
        "slug": "latticework-interconnect",
        "shot_type": "visual_diagram",
        "has_character": False,
        "allowed_text": ["ĐA MÔ HÌNH"],
        "description": (
            "Simple 2D hand-drawn explainer lattice grid on a pure white #FFFFFF background. "
            "A network of nine circular nodes (Vật lý, Sinh học, Tâm lý, Kinh tế...) all interconnected by bold black lines like a woven hammock, "
            "supporting a solid sphere labeled 'ĐA MÔ HÌNH'. Bold black outlines, flat solid colors."
        ),
    },
    188: {
        "slug": "storm-anchor-steadfast",
        "shot_type": "full_scene",
        "has_character": False,
        "allowed_text": ["VỮNG VÀNG"],
        "description": (
            "Simple 2D hand-drawn explainer scene with a flat slate-gray sky. "
            "A sturdy terracotta foundation pillar embedded firmly into deep bedrock seabed, holding a small boat tranquil despite howling winds "
            "labeled 'VỮNG VÀNG'. Bold clean black contours, flat solid fills, generous clear space."
        ),
    },
    189: {
        "slug": "atomic-thinking-core",
        "shot_type": "white_isolated",
        "has_character": False,
        "allowed_text": ["HẠT NHÂN"],
        "description": (
            "Simple 2D hand-drawn explainer illustration on a pure white #FFFFFF background. "
            "A stylized Bohr atomic model with three orbiting elliptical rings. In the center glows a solid terracotta nucleus emitting "
            "subtle radiating energy pulses labeled 'HẠT NHÂN'. Bold clean black outlines, flat solid fills, pure white background."
        ),
    },
    190: {
        "slug": "lighthouse-epistemic-fog",
        "shot_type": "full_scene",
        "has_character": False,
        "allowed_text": ["CHÂN LÝ DẪN ĐƯỜNG"],
        "description": (
            "Simple 2D hand-drawn explainer scene with a flat warm sand and twilight slate sky. "
            "On a sturdy rocky outcrop on the left stands a tall black-and-white striped lighthouse projecting a broad, clean triangular "
            "beam of light through murky clouds labeled 'CHÂN LÝ DẪN ĐƯỜNG'. Bold black outlines, flat solid colors."
        ),
    },
}
