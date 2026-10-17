#!/usr/bin/env python3
"""13-Minute (~780s, Safe Range: 9–16m / 540s–960s) Research & Production Blueprint Builder:
Giải Mã Tư Duy Nghiên Cứu, Bản Chất Tri Thức & Luật Ngầm Học Thuật (8 Chapters / 48 Scenes).

Nối tiếp trực tiếp chuỗi video Thịnh Hành 22.1K & 16.8K view ('Nghịch lý tri thức', 'Academic Pyramid',
'Biết tính != Hiểu', 'Bài báo khoa học không bắt đầu ở Word', 'Tâm lý Hội đồng 120s') theo Phễu 3 Tầng:
  - Chương 1 (0:00 - 1:30): Ảo Giác Năng Lực Lúc 2 Giờ Sáng & Cái Bẫy Tô Màu Giáo Trình (Việt hóa 100%)
  - Chương 2 (1:30 - 3:15): Giải Phẫu 4 Cấp Độ Tiếp Cận Tri Thức & Nghịch Lý "Biết Tính != Hiểu Bản Chất"
  - Chương 3 (3:15 - 5:00): Kỹ Thuật Feynman & Cái Bẫy Thuật Ngữ Hàn Lâm (Lý Thuyết Gốc vs. Sao Chép Cơ Học)
  - Chương 4 (5:00 - 6:45): Tháp Học Thuật 9 Tầng (Academic Pyramid) & Cơn Bão Thông Tin Phân Mảnh
  - Chương 5 (6:45 - 8:30): Bài Báo Khoa Học Không Bắt Đầu Ở Word: Chuỗi Quyết Định Question -> Gap -> Method -> Evidence
  - Chương 6 (8:30 - 10:15): Giải Phẫu 1 Bài Báo Q1: Vì Sao Các Giáo Sư Luôn Đọc Theo Thứ Tự Ngược Lại?
  - Chương 7 (10:15 - 11:45): Vũ Khí Tư Duy Học Thuật: Biến 30 Bài Báo Thành Ma Trận Khoảng Trống Nghiên Cứu (Research Gap Matrix)
  - Chương 8 (11:45 - 13:00): Tâm Lý Học Phòng Bảo Vệ: Làm Chủ Cửa Sổ 120 Giây Đầu Trước Hội Đồng & Khép Vòng Lặp
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
venv_py = SYS_DIR / ".venv/bin/python"
if __name__ == "__main__" and venv_py.is_file() and Path(sys.executable).resolve() != venv_py.resolve():
    os.execv(str(venv_py), [str(venv_py), str(Path(__file__).resolve())] + sys.argv[1:])

if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))
if str(SYS_DIR / "tools") not in sys.path:
    sys.path.insert(0, str(SYS_DIR / "tools"))

from research_story_architect import (  # noqa: E402
    DEFAULT_CHANNEL_PILLAR,
    PackagingSpec,
    ResearchedScene,
    compose_full_frame_description,
    ResearchedTopic,
    assign_scene_camera_effects,
    write_production_package,
)
from script_cadence_checker import count_syllables, extract_pauses  # noqa: E402
from vn_text_normalizer import normalize_for_tts  # noqa: E402

PAUSE_TAG_RE = re.compile(r"\[pause:\s*(\d+(?:\.\d+)?)\s*(ms|s)?\s*\]", re.IGNORECASE)
STYLE_PREFIX = (
    "Editorial 2D full-frame explainer illustration in clean architectural linework on warm cream editorial paper, "
    "high-contrast slate ink geometry, anonymous stick-figure character integrated into the physical environment, "
    "16:9 widescreen composition, no detached cutout, no sticker border, no decorative clutter"
)


def strip_pause_tags(text: str) -> str:
    cleaned = PAUSE_TAG_RE.sub(" ", text)
    return re.sub(r"\s+", " ", cleaned).strip()


def split_narration_with_pauses(narration: str) -> List[Tuple[str, float]]:
    raw = narration.strip()
    pattern = re.compile(
        r"([^.!?…]+[.!?…]+)\s*(?:\[pause:\s*(\d+(?:\.\d+)?)\s*(ms|s)?\s*\])?",
        re.IGNORECASE,
    )
    results: List[Tuple[str, float]] = []
    for match in pattern.finditer(raw):
        sent_raw = match.group(1)
        pause_val = match.group(2)
        pause_unit = (match.group(3) or "").lower()
        clean_sent = strip_pause_tags(sent_raw)
        if not clean_sent:
            continue
        explicit_sec = 0.0
        if pause_val is not None:
            val = float(pause_val)
            explicit_sec = val / 1000.0 if (pause_unit == "ms" or (not pause_unit and val > 10)) else val
        results.append((clean_sent, round(explicit_sec, 3)))
    if not results:
        results.append((strip_pause_tags(raw), 0.0))
    return results


CHAPTER_METADATA: List[Dict[str, Any]] = [
    {
        "chapter": 1,
        "title": "Ảo Giác Năng Lực Lúc 2 Giờ Sáng & Cái Bẫy Tô Màu Giáo Trình",
        "time_span": "0:00 - 1:30",
        "scene_ids": ["SC01", "SC02", "SC03", "SC04", "SC05", "SC06"],
        "requirement_id": "R01",
    },
    {
        "chapter": 2,
        "title": "Giải Phẫu 4 Cấp Độ Tiếp Cận Tri Thức & Nghịch Lý Biết Tính Khác Hiểu Bản Chất",
        "time_span": "1:30 - 3:15",
        "scene_ids": ["SC07", "SC08", "SC09", "SC10", "SC11", "SC12"],
        "requirement_id": "R02",
    },
    {
        "chapter": 3,
        "title": "Kỹ Thuật Feynman & Cái Bẫy Thuật Ngữ Hàn Lâm (Lý Thuyết Gốc vs. Sao Chép Cơ Học)",
        "time_span": "3:15 - 5:00",
        "scene_ids": ["SC13", "SC14", "SC15", "SC16", "SC17", "SC18"],
        "requirement_id": "R03",
    },
    {
        "chapter": 4,
        "title": "Tháp Học Thuật 9 Tầng (Academic Pyramid) & Cơn Bão Thông Tin Phân Mảnh",
        "time_span": "5:00 - 6:45",
        "scene_ids": ["SC19", "SC20", "SC21", "SC22", "SC23", "SC24"],
        "requirement_id": "R04",
    },
    {
        "chapter": 5,
        "title": "Bài Báo Khoa Học Không Bắt Đầu Ở Word: Chuỗi Quyết Định Question -> Gap -> Method -> Evidence",
        "time_span": "6:45 - 8:30",
        "scene_ids": ["SC25", "SC26", "SC27", "SC28", "SC29", "SC30"],
        "requirement_id": "R05",
    },
    {
        "chapter": 6,
        "title": "Giải Phẫu 1 Bài Báo Q1: Vì Sao Các Giáo Sư Luôn Đọc Theo Thứ Tự Ngược Lại?",
        "time_span": "8:30 - 10:15",
        "scene_ids": ["SC31", "SC32", "SC33", "SC34", "SC35", "SC36"],
        "requirement_id": "R06",
    },
    {
        "chapter": 7,
        "title": "Vũ Khí Tư Duy Học Thuật: Biến 30 Bài Báo Thành Ma Trận Khoảng Trống Nghiên Cứu (Research Gap Matrix)",
        "time_span": "10:15 - 11:45",
        "scene_ids": ["SC37", "SC38", "SC39", "SC40", "SC41", "SC42"],
        "requirement_id": "R07",
    },
    {
        "chapter": 8,
        "title": "Tâm Lý Học Phòng Bảo Vệ: Làm Chủ Cửa Sổ 120 Giây Đầu Trước Hội Đồng & Khép Vòng Lặp",
        "time_span": "11:45 - 13:00",
        "scene_ids": ["SC43", "SC44", "SC45", "SC46", "SC47", "SC48"],
        "requirement_id": "R08",
    },
]


def get_academic_sources() -> List[Dict[str, Any]]:
    """8 peer-reviewed / classic academic sources with 16 spoken facts (strictly <= 20 syllables each)."""
    return [
        {
            "id": "SRC01",
            "title": "The Critical Importance of Retrieval for Learning",
            "reference": "Jeffrey D. Karpicke & Henry L. Roediger (2008). Science, 319(5865), 966-968. DOI: 10.1126/science.1152408",
            "facts": [
                "Đọc lại giáo trình nhiều lần chỉ tạo ra ảo giác hiểu bài.",
                "Não bộ chỉ thực sự nắm bản chất khi tự truy xuất thông tin.",
            ],
        },
        {
            "id": "SRC02",
            "title": "A Mathematician's Lament: How School Cheats Us Out of Our Most Fascinating Imaginative Art Form",
            "reference": "Paul Lockhart (2009). Bellevue Literary Press. ISBN: 978-1934137178",
            "facts": [
                "Giải nhanh công thức có sẵn hoàn toàn khác với hiểu bản chất.",
                "Sao chép lời giải mẫu làm tê liệt khả năng tự đặt câu hỏi.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Surely You're Joking, Mr. Feynman! (The Feynman Mental Model of Understanding)",
            "reference": "Richard P. Feynman (1985). W. W. Norton & Company. ISBN: 978-0393316049",
            "facts": [
                "Dùng thuật ngữ phức tạp thường là vỏ bọc của việc chưa hiểu.",
                "Hiểu bản chất là giải thích được cơ chế bằng ngôn từ giản dị.",
            ],
        },
        {
            "id": "SRC04",
            "title": "Cognitive Load During Problem Solving: Effects on Learning",
            "reference": "John Sweller (1988). Cognitive Science, 12(2), 257-285. DOI: 10.1207/s15516709cog1202_4",
            "facts": [
                "Nhồi nhét tài liệu phân mảnh làm sập bộ nhớ làm việc của não.",
                "Tháp học thuật chín tầng giúp lọc bỏ nguồn rác ngay từ đầu.",
            ],
        },
        {
            "id": "SRC05",
            "title": "Genre Analysis: English in Academic and Research Settings (CARS Model)",
            "reference": "John M. Swales (1990). Cambridge University Press. ISBN: 978-0521338134",
            "facts": [
                "Bài báo quốc tế bắt đầu từ khoảng trống tri thức chứ không phải Word.",
                "Mọi công trình chuẩn mực đều đi từ câu hỏi đến bằng chứng thực nghiệm.",
            ],
        },
        {
            "id": "SRC06",
            "title": "How to Read a Paper: The Three-Pass Approach for Researchers",
            "reference": "Srinivasan Keshav (2007). ACM SIGCOMM Computer Communication Review, 37(3), 83-84. DOI: 10.1145/1273445.1273458",
            "facts": [
                "Các nhà nghiên cứu kỳ cựu không bao giờ đọc bài báo theo thứ tự xuôi.",
                "Họ soi câu hỏi và kết luận trước khi kiểm tra bảng dữ liệu.",
            ],
        },
        {
            "id": "SRC07",
            "title": "The Craft of Research (4th Edition)",
            "reference": "Wayne C. Booth, Gregory G. Colomb & Joseph M. Williams (2016). University of Chicago Press. ISBN: 978-0226239736",
            "facts": [
                "Dùng trí tuệ nhân tạo viết hộ tổng quan luôn lộ lỗi sáo rỗng.",
                "Ma trận đối chiếu giúp gom ba mươi bài báo thành khoảng trống rõ nét.",
            ],
        },
        {
            "id": "SRC08",
            "title": "The Elaboration Likelihood Model of Persuasion in Academic Evaluation",
            "reference": "Richard E. Petty & John T. Cacioppo (1986). Advances in Experimental Social Psychology, 19, 123-205.",
            "facts": [
                "Hội đồng bảo vệ định hình phán quyết ngay trong hai phút đầu tiên.",
                "Trình bày rõ khoảng trống và phương pháp giúp bạn làm chủ hội đồng.",
            ],
        },
    ]


def get_required_points() -> List[Dict[str, str]]:
    return [
        {"id": "R01", "text": "Ảo giác năng lực lúc hai giờ sáng khi tô màu kín giáo trình nhưng không hiểu bản chất"},
        {"id": "R02", "text": "Bốn cấp độ tiếp cận tri thức và nghịch lý biết tính toán khác xa hiểu bản chất"},
        {"id": "R03", "text": "Kỹ thuật Feynman lật tẩy cái bẫy thuật ngữ hàn lâm và sao chép cơ học"},
        {"id": "R04", "text": "Tháp học thuật chín tầng giúp vượt qua cơn bão thông tin phân mảnh"},
        {"id": "R05", "text": "Bài báo khoa học không bắt đầu ở Word mà theo chuỗi câu hỏi, khoảng trống, phương pháp, bằng chứng"},
        {"id": "R06", "text": "Chiến lược giải phẫu bài báo chuẩn quốc tế theo thứ tự ngược của các giáo sư"},
        {"id": "R07", "text": "Biến ba mươi bài báo rời rạc thành ma trận khoảng trống nghiên cứu thay vì nhờ viết hộ"},
        {"id": "R08", "text": "Tâm lý học phòng bảo vệ khóa luận trong một trăm hai mươi giây đầu và khép vòng lặp"},
    ]


RAW_SCENES_DATA: List[Dict[str, Any]] = [
    # ==================== CHAPTER 1: Ảo Giác Năng Lực Lúc 2 Giờ Sáng ====================
    {
        "scene_id": "SC01",
        "chapter": 1,
        "title": "Cú tát sự thật: Đọc lại giáo trình năm lần lúc hai giờ sáng",
        "purpose": "Ảo giác năng lực lúc hai giờ sáng khi tô màu kín giáo trình nhưng không hiểu bản chất",
        "narration": "Đọc lại giáo trình nhiều lần chỉ tạo ra ảo giác hiểu bài. Hai giờ sáng trước kỳ bảo vệ khóa luận, cuốn sách của bạn phủ kín bút dạ quang vàng rực. Thế nhưng khi gấp trang giấy lại, đầu óc bạn bỗng trống rỗng.",
        "requirements": ["R01"],
        "source_ids": ["SRC01"],
        "claim": ("Đọc lại giáo trình nhiều lần chỉ tạo ra ảo giác hiểu bài.", "SRC01", "Đọc lại giáo trình nhiều lần chỉ tạo ra ảo giác hiểu bài."),
        "action": "Nhân vật người que nghiên cứu ngồi trước cuốn giáo trình highlight vàng rực nhưng ôm đầu bối rối khi gấp sách lại",
        "setting": "Bàn học sinh viên Việt Nam lúc hai giờ sáng dưới ánh đèn bàn vàng ấm",
        "camera": "Đặc tả trang giáo trình tô màu rồi kéo rộng ra nhân vật ôm đầu",
        "scene_description": "Đồ họa Editorial Graphic vẽ bàn học đêm khuya với cuốn giáo trình phủ kín vệt bút dạ quang và đồng hồ chỉ hai giờ sáng trên nền giấy kem, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày khép kín, hai tay ôm đầu hoang mang nhìn cuốn sách gấp lại trong cùng không gian bối cảnh",
        "anchor_quote": "ảo giác hiểu bài",
        "fx": "pop",
        "x": 0.35,
    },
    {
        "scene_id": "SC02",
        "chapter": 1,
        "title": "Trang Word trắng tinh và nỗi sợ khóa luận",
        "purpose": "Mô tả tình cảnh mở Word lúc nửa đêm nhưng không viết nổi một dòng lập luận",
        "narration": "Trên màn hình máy tính, con trỏ chuột nhấp nháy lạnh lùng suốt ba tiếng đồng hồ. Bạn đã tải về hàng chục tài liệu tham khảo, và chép đầy ba cuốn sổ tay. Vậy mà đứng trước trang soạn thảo trắng tinh, bạn không biết phải bắt đầu từ đâu.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu nhìn chằm chằm vào con trỏ chuột nhấp nháy trên trang Word trắng tinh",
        "setting": "Màn hình laptop mở trang Word trống rỗng bên cạnh chồng sổ ghi chép dày",
        "camera": "Trung cảnh đẩy dần vào màn hình trắng tinh",
        "scene_description": "Màn hình máy tính hiển thị giao diện trang soạn thảo trắng tinh với dòng tiêu đề Chương 1 bỏ dở bên cạnh ba cuốn sổ ghi chép, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày ngồi chống cằm thở dài trước bàn phím trong cùng không gian bối cảnh",
        "anchor_quote": "con trỏ chuột nhấp nháy",
        "fx": "slide_left",
        "x": 0.64,
    },
    {
        "scene_id": "SC03",
        "chapter": 1,
        "title": "Nghịch lý của sự chăm chỉ cơ học",
        "purpose": "Chỉ ra mâu thuẫn giữa số giờ ngồi cày cuốc và năng lực tư duy độc lập",
        "narration": "Bạn không hề lười biếng, thậm chí bạn là người thức khuya nhất trong khu ký túc xá. Bạn thuộc lòng từng định nghĩa trong sách, và nhớ rõ từng dạng bài tập quen thuộc. Nhưng chỉ cần đề bài đổi đi một biến số nhỏ, mọi công thức lập tức sụp đổ.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu xếp chồng sách cao ngất nhưng sững sờ khi gặp một câu hỏi biến thiên",
        "setting": "Không gian học tập đối lập giữa chồng sách chép tay và dấu hỏi lớn trên bảng",
        "camera": "Lia ngang từ chồng sách sang biểu đồ dấu hỏi",
        "scene_description": "Sơ đồ Editorial Graphic đối chiếu chồng vở ghi chép dày cộp bên trái với biểu tượng dấu hỏi lớn chặn ngang lối đi bên phải, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày giơ hai tay bất lực trước tấm biển câu hỏi lạ trong cùng không gian bối cảnh",
        "anchor_quote": "mọi công thức lập tức sụp đổ",
        "fx": "bounce",
        "x": 0.35,
    },
    {
        "scene_id": "SC04",
        "chapter": 1,
        "title": "Cơ chế nhận diện mặt chữ đánh lừa bộ não",
        "purpose": "Giải thích hiện tượng sự quen thuộc bề mặt bị nhầm lẫn với sự thông hiểu",
        "narration": "Đó là ảo giác năng lực. Khi mắt bạn lướt qua một trang viết tới lần thứ năm, vùng thị giác báo hiệu sự quen thuộc. Bộ não liền đánh tráo cảm giác quen mắt đó, khiến bạn tưởng mình đã làm chủ kiến thức.",
        "requirements": [],
        "source_ids": ["SRC01"],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu cầm kính lúp soi vào hai đường tín hiệu Nhận diện quen mắt vs Nắm giữ cấu trúc",
        "setting": "Sơ đồ hai đường cong nhận thức: Đường quen mặt chữ tăng vọt và đường hiểu bản chất đi ngang",
        "camera": "Cận cảnh biểu đồ hai đường cong phân kỳ",
        "scene_description": "Biểu đồ Editorial Graphic vẽ hai đường cong phân kỳ: đường nét đứt Cảm giác quen mắt đi lên và đường nét liền Năng lực tự giải quyết đi ngang, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày chỉ thước vào khoảng cách giữa hai đường đồ thị trong cùng không gian bối cảnh",
        "anchor_quote": "ảo giác năng lực trong học tập",
        "fx": "pop",
        "x": 0.64,
    },
    {
        "scene_id": "SC05",
        "chapter": 1,
        "title": "Thí nghiệm truy xuất chủ động đối đầu đọc thụ động",
        "purpose": "Chứng minh não bộ chỉ hiểu sâu khi buộc phải tự mình truy xuất thông tin",
        "narration": "Các thực nghiệm về trí nhớ đã đặt hai nhóm sinh viên lên bàn cân kiểm chứng. Nhóm đầu tiên xem đi xem lại tài liệu bốn lần liên tiếp. Nhóm thứ hai chỉ xem một lần, rồi gấp sách tự vẽ lại sơ đồ. Não bộ chỉ thực sự nắm bản chất khi tự truy xuất thông tin.",
        "requirements": [],
        "source_ids": ["SRC01"],
        "claim": ("Não bộ chỉ thực sự nắm bản chất khi tự truy xuất thông tin.", "SRC01", "Não bộ chỉ thực sự nắm bản chất khi tự truy xuất thông tin."),
        "action": "Đối sánh nhóm đọc lại bốn lần bị quên sạch và nhóm tự vẽ sơ đồ giữ vững kiến thức",
        "setting": "Bảng kết quả thực nghiệm đối chiếu tỷ lệ ghi nhớ sau một tuần",
        "camera": "Toàn cảnh bảng đối sánh hai cột thực nghiệm",
        "scene_description": "Đồ họa Editorial Graphic hiển thị hai cột kết quả thực nghiệm: cột Đọc thụ động 4 lần tụt thấp và cột Tự truy xuất sơ đồ vươn cao, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm bút tự vẽ sơ đồ nhánh cây trên bảng trắng",
        "anchor_quote": "tự truy xuất thông tin",
        "fx": "pop_wobble",
        "x": 0.35,
    },
    {
        "scene_id": "SC06",
        "chapter": 1,
        "title": "Bước ngoặt nhận thức: Từ người tiêu thụ sang người kiến tạo",
        "purpose": "Chốt lại Chương 1 bằng câu hỏi lật ngược toàn bộ cách học truyền thống",
        "narration": "Chừng nào bạn còn mở sách ra để chép lại, bộ não của bạn vẫn đang ngủ đông. [pause:800ms] Muốn bước qua cánh cửa nghiên cứu thực thụ, bạn phải đập vỡ ảo giác quen thuộc này. Hãy nhìn thẳng vào bốn cấp độ của tri thức.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu bước qua tấm kính ảo giác vỡ vụn để tiến tới Tháp 4 Cấp Độ Tri Thức",
        "setting": "Hành lang chuyển tiếp dẫn tới sơ đồ 4 bậc thang tri thức phát sáng",
        "camera": "Góc máy mở rộng tạo chiều sâu kịch tính",
        "scene_description": "Bậc thang kiến trúc 4 tầng đại diện cho 4 cấp độ tiếp cận tri thức vươn lên trên nền giấy biên tập sắc nét, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm đèn pin chiếu thẳng lên bậc thang bốn tầng trong cùng không gian bối cảnh",
        "anchor_quote": "bốn cấp độ của tri thức",
        "fx": "bounce",
        "x": 0.64,
    },

    # ==================== CHAPTER 2: 4 Cấp Độ Tri Thức & Biết Tính != Hiểu ====================
    {
        "scene_id": "SC07",
        "chapter": 2,
        "title": "Nghịch lý người giải toán nhanh nhất lớp",
        "purpose": "Bốn cấp độ tiếp cận tri thức và nghịch lý biết tính toán khác xa hiểu bản chất",
        "narration": "Vì sao người giải bài tập nhanh nhất lớp, lại thường lúng túng khi bước vào nghiên cứu khoa học? Ở phổ thông, chúng ta được thưởng điểm tối đa khi áp dụng thật nhanh một công thức có sẵn. Giải nhanh công thức có sẵn hoàn toàn khác với hiểu bản chất.",
        "requirements": ["R02"],
        "source_ids": ["SRC02"],
        "claim": ("Giải nhanh công thức có sẵn hoàn toàn khác với hiểu bản chất.", "SRC02", "Giải nhanh công thức có sẵn hoàn toàn khác với hiểu bản chất."),
        "action": "Nhân vật người que nghiên cứu đứng trên đồ thị hàm số đặt câu hỏi Biết tính có bằng Hiểu bản chất?",
        "setting": "Đồ thị hàm số toán học kết hợp thẻ đối sánh Biết tính != Hiểu",
        "camera": "Đặc tả biểu tượng dấu khác biệt trên đồ thị",
        "scene_description": "Đồ họa Editorial Graphic vẽ đường cong đồ thị đạo hàm tích phân sắc nét cùng ký hiệu Biết tính khác Hiểu trên nền sáng, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày đứng trên trục tọa độ tay chỉ vào dấu khác biệt trong cùng không gian bối cảnh",
        "anchor_quote": "hoàn toàn khác với hiểu bản chất",
        "fx": "pop",
        "x": 0.35,
    },
    {
        "scene_id": "SC08",
        "chapter": 2,
        "title": "Cấp độ 1 và 2: Thu thập thông tin và Sao chép quy trình",
        "purpose": "Giải phẫu hai bậc thấp nhất trong thước đo 4 cấp độ tiếp cận tri thức",
        "narration": "Hãy nhìn vào thước đo bốn cấp độ tiếp cận tri thức trên sơ đồ. Ở cấp độ một, bạn chỉ gom nhặt các mảnh dữ liệu rời rạc như một chiếc ổ cứng lưu trữ. Lên cấp độ hai, bạn bắt chước quy trình tính toán của người đi trước, mà không biết vì sao quy trình đó tồn tại.",
        "requirements": [],
        "source_ids": ["SRC02"],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu soi đèn vào bậc 1 (Lưu trữ thô) và bậc 2 (Bắt chước cơ học)",
        "setting": "Thước đo 4 cấp độ tri thức với hai tầng đáy được tô màu xám cảnh báo",
        "camera": "Lia dọc từ bậc 1 lên bậc 2 của thước đo",
        "scene_description": "Thước đo phân cấp 4 tầng Editorial Graphic với tầng 1 Lưu trữ dữ liệu và tầng 2 Sao chép quy trình nổi bật ở nửa dưới, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm bảng kiểm đánh dấu hai tầng dưới cùng trong cùng không gian bối cảnh",
        "anchor_quote": "thước đo bốn cấp độ tiếp cận",
        "fx": "slide_left",
        "x": 0.64,
    },
    {
        "scene_id": "SC09",
        "chapter": 2,
        "title": "Hệ lụy của việc học theo văn mẫu và lời giải mẫu",
        "purpose": "Chỉ ra cách lời giải mẫu phá hủy năng lực phát hiện vấn đề mới",
        "narration": "Khi bạn chỉ dừng lại ở tầng sao chép cơ học, bộ não bị đóng khung vào những con đường mòn. Sao chép lời giải mẫu làm tê liệt khả năng tự đặt câu hỏi. Bạn giải được hàng trăm bài toán có đáp án sẵn, nhưng lại bất lực trước một hiện tượng thực tế chưa có lời giải.",
        "requirements": [],
        "source_ids": ["SRC02"],
        "claim": ("Sao chép lời giải mẫu làm tê liệt khả năng tự đặt câu hỏi.", "SRC02", "Sao chép lời giải mẫu làm tê liệt khả năng tự đặt câu hỏi."),
        "action": "Nhân vật người que nghiên cứu bước đi trong đường ray khép kín của lời giải mẫu",
        "setting": "Sơ đồ đường ray vòng tròn khép kín đối lập với vùng đất tri thức mở rộng bên ngoài",
        "camera": "Góc máy từ trên cao nhìn xuống đường ray khép kín",
        "scene_description": "Sơ đồ Editorial Graphic vẽ đường ray hình tròn khép kín biểu trưng cho lối mòn bài tập mẫu bên cạnh không gian mở, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày dừng lại nhìn ra ngoài đường ray với ánh mắt suy tư trong cùng không gian bối cảnh",
        "anchor_quote": "tê liệt khả năng tự đặt câu hỏi",
        "fx": "pop",
        "x": 0.35,
    },
    {
        "scene_id": "SC10",
        "chapter": 2,
        "title": "Cấp độ 3: Nắm bắt cấu trúc nhân quả gốc rễ",
        "purpose": "Giải thích bước nhảy vọt từ biết tính toán sang hiểu mô hình nhân quả",
        "narration": "Bước nhảy vọt chỉ xảy ra khi bạn vươn lên cấp độ ba, tức là giải phẫu cấu trúc nhân quả gốc rễ. Thay vì học thuộc công thức, bạn truy ngược về câu hỏi tại sao công thức đó lại được sinh ra. Bạn nhìn thấy mối liên hệ ngầm giữa các biến số, và biết rõ giới hạn nơi lý thuyết cũ bắt đầu sai lệch.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu mở nắp hộp đen công thức để lộ mạng lưới bánh răng nhân quả bên trong",
        "setting": "Tầng 3 của Thước đo Tri thức hiển thị mạng lưới liên kết nguyên nhân và hệ quả",
        "camera": "Đẩy cận vào mạng lưới liên kết nhân quả",
        "scene_description": "Sơ đồ mạng lưới nút giao nhân quả sắc nét nối các biến số gốc rễ ở tầng 3 của thước đo tri thức, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày nối hai điểm nút sơ đồ bằng cây bút sáng trong cùng không gian bối cảnh",
        "anchor_quote": "cấu trúc nhân quả gốc rễ",
        "fx": "bounce",
        "x": 0.64,
    },
    {
        "scene_id": "SC11",
        "chapter": 2,
        "title": "Cấp độ 4: Kiến tạo tri thức mới từ khoảng trống",
        "purpose": "Định nghĩa đỉnh cao nhất của nghiên cứu khoa học là tạo ra tri thức mới",
        "narration": "Đỉnh cao nhất của thước đo là cấp độ bốn, nơi bạn bắt đầu kiến tạo tri thức mới. Tại đây, tri thức không còn nằm ở số lượng trang giấy bạn đã đọc qua. Nó nằm ở khả năng phát hiện ra chỗ khuyết của bức tranh khoa học. Từ đó, bạn tự thiết kế phép đo để lấp đầy vùng khuyết ấy.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu đặt mảnh ghép mới phát sáng vào đỉnh Tháp 4 Cấp Độ Tri Thức",
        "setting": "Tầng 4 đỉnh tháp tri thức tỏa sáng với mảnh ghép hoàn thiện bức tranh khoa học",
        "camera": "Toàn cảnh tôn vinh tầng 4 đỉnh cao",
        "scene_description": "Đỉnh thước đo 4 cấp độ tri thức với ô trống phát sáng chờ mảnh ghép phát kiến mới hoàn thiện, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày nâng cao mảnh ghép phát sáng đặt vào đỉnh sơ đồ trong cùng không gian bối cảnh",
        "anchor_quote": "kiến tạo tri thức mới",
        "fx": "pop_wobble",
        "x": 0.35,
    },
    {
        "scene_id": "SC12",
        "chapter": 2,
        "title": "Phép thử phân biệt học vẹt và hiểu thật sự",
        "purpose": "Dẫn dắt từ thước đo 4 cấp độ sang phép thử Feynman ở Chương 3",
        "narration": "Làm sao biết bạn hiểu thật? Lịch sử khoa học có một phép thử cực kỳ tàn nhẫn, nhưng chính xác tuyệt đối. Nó bắt đầu bằng việc tước bỏ lớp từ ngữ bóng bẩy, thứ bạn vẫn dùng làm lá chắn.",
        "requirements": [],
        "source_ids": ["SRC03"],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu gỡ bỏ lớp mặt nạ chữ nghĩa hàn lâm phức tạp",
        "setting": "Bàn làm việc tối giản với tấm bảng phép thử ngôn từ giản dị",
        "camera": "Trung cảnh đẩy vào tấm bảng phép thử",
        "scene_description": "Đồ họa Editorial Graphic vẽ một tấm khiên chữ nghĩa rườm rà đang tách mở để lộ lõi nguyên lý tối giản bên trong, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm chiếc chổi nhỏ quét sạch lớp chữ rườm rà trong cùng không gian bối cảnh",
        "anchor_quote": "tước bỏ lớp từ ngữ bóng bẩy",
        "fx": "slide_left",
        "x": 0.64,
    },

    # ==================== CHAPTER 3: Kỹ Thuật Feynman & Cái Bẫy Thuật Ngữ ====================
    {
        "scene_id": "SC13",
        "chapter": 3,
        "title": "Cái bẫy thuật ngữ hàn lâm trong khóa luận",
        "purpose": "Kỹ thuật Feynman lật tẩy cái bẫy thuật ngữ hàn lâm và sao chép cơ học",
        "narration": "Rất nhiều bài khóa luận nghe cực kỳ uyên bác, với hàng loạt thuật ngữ ngoại lai nối đuôi nhau. Thế nhưng khi hội đồng hỏi một câu giản dị rằng cơ chế đó vận hành thế nào, tác giả lại đứng hình. Dùng thuật ngữ phức tạp thường là vỏ bọc của việc chưa hiểu.",
        "requirements": ["R03"],
        "source_ids": ["SRC03"],
        "claim": ("Dùng thuật ngữ phức tạp thường là vỏ bọc của việc chưa hiểu.", "SRC03", "Dùng thuật ngữ phức tạp thường là vỏ bọc của việc chưa hiểu."),
        "action": "Nhân vật người que nghiên cứu đứng sau bức tường thuật ngữ cao ngất nhưng lúng túng trước câu hỏi trực diện",
        "setting": "Sơ đồ đối sánh vỏ bọc thuật ngữ rỗng và lõi cơ chế thực chất",
        "camera": "Cận cảnh vết nứt trên khối thuật ngữ hàn lâm",
        "scene_description": "Đồ họa Editorial Graphic vẽ một khối hộp lớn dán nhãn Thuật ngữ phức tạp nhưng bên trong rỗng tuếch trên nền sáng, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày gõ nhẹ vào khối hộp rỗng với vẻ mặt giật mình trong cùng không gian bối cảnh",
        "anchor_quote": "vỏ bọc của việc chưa hiểu",
        "fx": "pop",
        "x": 0.35,
    },
    {
        "scene_id": "SC14",
        "chapter": 3,
        "title": "Sự khác biệt giữa biết tên gọi và hiểu sự vật",
        "purpose": "Minh họa câu chuyện kinh điển về việc biết tên con chim bằng năm thứ tiếng nhưng không biết gì về nó",
        "narration": "Bạn có thể biết tên một loài chim bằng năm thứ tiếng khác nhau trên thế giới. Nhưng điều đó hoàn toàn không giúp bạn biết con chim ấy kiếm ăn ra sao, hay bay lượn theo cơ chế nào. Trong nghiên cứu cũng vậy, gọi tên một khái niệm không đồng nghĩa với việc bạn đã nắm được quy luật của nó.",
        "requirements": [],
        "source_ids": ["SRC03"],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu nhìn năm tấm thẻ tên ngoại ngữ đối lập với sơ đồ cơ học đôi cánh chim",
        "setting": "Bảng đối sánh Nhãn dán ngôn từ vs Cơ chế vận hành thực tế",
        "camera": "Lia ngang từ các thẻ nhãn dán sang bản vẽ cơ chế",
        "scene_description": "Sơ đồ Editorial Graphic đặt năm thẻ nhãn chữ bên trái đối diện bản vẽ giải phẫu khí động học sắc nét bên phải, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày đặt thẻ tên xuống và chỉ tay vào bản vẽ cơ chế trong cùng không gian bối cảnh",
        "anchor_quote": "nắm được quy luật của nó",
        "fx": "bounce",
        "x": 0.64,
    },
    {
        "scene_id": "SC15",
        "chapter": 3,
        "title": "Quy trình 4 bước của Kỹ thuật Feynman",
        "purpose": "Trình bày 4 bước thực hành giải mã kiến thức phức tạp",
        "narration": "Để tự kiểm tra độ hiểu sâu, hãy đặt một tờ giấy trắng lên bàn và thực hiện bốn bước. Hãy viết lại khái niệm đó như thể bạn đang giải thích cho một học sinh đầu cấp. Hiểu bản chất là giải thích được cơ chế bằng ngôn từ giản dị.",
        "requirements": [],
        "source_ids": ["SRC03"],
        "claim": ("Hiểu bản chất là giải thích được cơ chế bằng ngôn từ giản dị.", "SRC03", "Hiểu bản chất là giải thích được cơ chế bằng ngôn từ giản dị."),
        "action": "Nhân vật người que nghiên cứu viết sơ đồ 4 bước Feynman ngắn gọn trên tờ giấy trắng",
        "setting": "Sơ đồ 4 bước Feynman: Viết giản dị -> Phát hiện điểm vấp -> Quay lại nguồn gốc -> Tinh gọn ẩn dụ",
        "camera": "Toàn cảnh sơ đồ 4 bước rõ ràng",
        "scene_description": "Sơ đồ vòng lặp 4 bước Kỹ thuật Feynman vẽ bằng nét mực đen sắc nét trên nền giấy kem thoáng đãng, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm bút mực vẽ mũi tên nối 4 bước trong cùng không gian bối cảnh",
        "anchor_quote": "ngôn từ giản dị",
        "fx": "pop",
        "x": 0.35,
    },
    {
        "scene_id": "SC16",
        "chapter": 3,
        "title": "Khoảnh khắc vấp ngã trên trang giấy trắng",
        "purpose": "Chỉ ra rằng điểm bạn bị khựng khi giải thích chính là lỗ hổng nhận thức quý giá",
        "narration": "Ngay tại câu chữ mà ngòi bút của bạn bị khựng lại, lỗ hổng nhận thức đã lộ diện. Đó là nơi bạn từng dùng từ ngữ sách vở để lấp liếm, cho một mắt xích nhân quả chưa thông suốt. Thay vì né tránh, nhà nghiên cứu coi điểm vấp đó là tọa độ vàng cần đào sâu.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu khoanh tròn đỏ vào đúng mắt xích bị đứt trên dòng lập luận",
        "setting": "Trang giấy lập luận với một mắt xích đứt đoạn được khoanh tròn đỏ nổi bật",
        "camera": "Đặc tả vòng tròn đỏ tại điểm đứt mạch logic",
        "scene_description": "Sơ đồ chuỗi mắt xích logic với một mắt xích trung tâm đang hở được đánh dấu vòng tròn đỏ biên tập, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm kính lúp soi vào mắt xích hở với ánh mắt tập trung trong cùng không gian bối cảnh",
        "anchor_quote": "lỗ hổng nhận thức đã lộ diện",
        "fx": "slide_left",
        "x": 0.64,
    },
    {
        "scene_id": "SC17",
        "chapter": 3,
        "title": "Thước đo Lý thuyết gốc đối đầu Sao chép cơ học",
        "purpose": "Làm rõ sự khác biệt giữa người nắm lý thuyết gốc và người chỉ biết sao chép",
        "narration": "Người sao chép cơ học luôn sợ bị hỏi vặn, vào giả định nền tảng của mô hình. Ngược lại, người nắm lý thuyết gốc hiểu rõ mô hình đứng trên trụ cột nào. Họ biết chính xác khi nào kết cấu đó sẽ sụp đổ. Đó là ranh giới giữa thợ chép bài và nhà khoa học.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Đối sánh hai nhân vật ở hai đầu thước đo Sao chép cơ học (x=0.35) và Lý thuyết gốc (x=0.64)",
        "setting": "Thước đo phân cấp Lý thuyết gốc vs Sao chép cơ học chuẩn Editorial Graphic",
        "camera": "Trung cảnh đối xứng theo Quy tắc 1/3",
        "scene_description": "Thước đo đối sánh hai cột: bên trái Khung sao chép mong manh và bên phải Kết cấu trụ cột lý thuyết gốc vững chãi, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày đứng vững bên trụ cột lý thuyết gốc tay cầm bản thiết kế trong cùng không gian bối cảnh",
        "anchor_quote": "người nắm lý thuyết gốc",
        "fx": "pop_wobble",
        "x": 0.64,
    },
    {
        "scene_id": "SC18",
        "chapter": 3,
        "title": "Từ hiểu sâu một khái niệm đến đối mặt biển tài liệu",
        "purpose": "Chuyển cảnh từ kỹ thuật hiểu sâu đơn lẻ sang bài toán lọc nguồn trong cơn bão thông tin",
        "narration": "Khi đã biết cách bóc tách bản chất từng khái niệm, bạn lại bước vào một thử thách lớn hơn. Giữa hàng triệu bài viết trôi nổi trên mạng mỗi ngày, đâu mới là nguồn tri thức đáng để bạn bỏ công giải phẫu? Nếu chọn sai nguyên liệu đầu vào, mọi nỗ lực tư duy phía sau đều trở nên vô nghĩa.",
        "requirements": [],
        "source_ids": ["SRC04"],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu đứng trước ngã ba đường ngập tràn các luồng tài liệu hỗn loạn",
        "setting": "Không gian chuyển tiếp từ bàn học cá nhân ra thư viện dữ liệu khổng lồ",
        "camera": "Kéo rộng toàn cảnh biển dữ liệu",
        "scene_description": "Đồ họa Editorial Graphic vẽ hàng trăm luồng dữ liệu phân mảnh đổ về một phễu lọc trung tâm, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm bộ lọc phân tầng đứng trước luồng dữ liệu trong cùng không gian bối cảnh",
        "anchor_quote": "chọn sai nguyên liệu đầu vào",
        "fx": "bounce",
        "x": 0.35,
    },

    # ==================== CHAPTER 4: Tháp Học Thuật 9 Tầng & Cơn Bão Thông Tin ====================
    {
        "scene_id": "SC19",
        "chapter": 4,
        "title": "Cơn bão thông tin và sự quá tải bộ nhớ làm việc",
        "purpose": "Tháp học thuật chín tầng giúp vượt qua cơn bão thông tin phân mảnh",
        "narration": "Mở trình duyệt tìm kiếm đề tài, bạn lập tức bị bao vây bởi hàng ngàn kết quả hỗn độn. Từ bài đăng mạng xã hội, trang tin tổng hợp cho tới các báo cáo chưa qua kiểm chứng đều hiện ra cùng lúc. Nhồi nhét tài liệu phân mảnh làm sập bộ nhớ làm việc của não.",
        "requirements": ["R04"],
        "source_ids": ["SRC04"],
        "claim": ("Nhồi nhét tài liệu phân mảnh làm sập bộ nhớ làm việc của não.", "SRC04", "Nhồi nhét tài liệu phân mảnh làm sập bộ nhớ làm việc của não."),
        "action": "Nhân vật người que nghiên cứu bị vây quanh bởi các mảnh dữ liệu rời rạc gây quá tải nhận thức",
        "setting": "Sơ đồ bộ nhớ làm việc bị tràn bởi các mảnh thông tin không phân loại",
        "camera": "Cận cảnh đồng hồ đo tải nhận thức vượt vạch đỏ",
        "scene_description": "Sơ đồ Editorial Graphic minh họa phễu bộ nhớ làm việc bị tắc nghẽn bởi hàng chục mảnh thông tin rời rạc, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày giơ tay chặn các mảnh giấy hỗn loạn bay tới trong cùng không gian bối cảnh",
        "anchor_quote": "sập bộ nhớ làm việc của não",
        "fx": "pop",
        "x": 0.35,
    },
    {
        "scene_id": "SC20",
        "chapter": 4,
        "title": "Sai lầm đánh đồng mọi nguồn trích dẫn",
        "purpose": "Chỉ ra lỗi phổ biến của sinh viên khi trích dẫn blog và web không bình duyệt vào khóa luận",
        "narration": "Đừng coi mọi nguồn ngang nhau. Nhiều người mới bắt đầu đưa cả bài viết cá nhân, hoặc nguồn khuyết danh vào cơ sở lý thuyết. Chỉ cần một trích dẫn rác xuất hiện, uy tín của toàn bộ khóa luận sẽ sụp đổ.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu rút một viên gạch mục nát ở đáy làm nghiêng cả tòa tháp lập luận",
        "setting": "Sơ đồ khối lập luận bị nghiêng do đặt trên nền tảng nguồn trích dẫn yếu",
        "camera": "Trung cảnh góc nghiêng nhấn mạnh sự mất cân bằng",
        "scene_description": "Đồ họa Editorial Graphic vẽ một cấu trúc cột trụ học thuật bị nghiêng vì viên gạch đáy ghi Nguồn trôi nổi bị nứt vỡ, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày chỉ tay cảnh báo vào viên gạch nứt ở chân cột trong cùng không gian bối cảnh",
        "anchor_quote": "uy tín của toàn bộ khóa luận",
        "fx": "slide_left",
        "x": 0.64,
    },
    {
        "scene_id": "SC21",
        "chapter": 4,
        "title": "Giải phẫu Tháp Học Thuật 9 Tầng: Ba tầng đáy cần loại bỏ",
        "purpose": "Giới thiệu cấu trúc Tháp Học Thuật 9 tầng và phân tích 3 tầng thấp nhất",
        "narration": "Để thoát khỏi mê cung dữ liệu, giới học thuật sử dụng kim chỉ nam là Tháp Học Thuật chín tầng. Tháp học thuật chín tầng giúp lọc bỏ nguồn rác ngay từ đầu. Ba tầng đáy gồm tin đồn truyền miệng, mạng xã hội và bách khoa thư mở. Chúng chỉ dùng để gợi mở ý tưởng, chứ tuyệt đối không được trích dẫn.",
        "requirements": [],
        "source_ids": ["SRC04"],
        "claim": ("Tháp học thuật chín tầng giúp lọc bỏ nguồn rác ngay từ đầu.", "SRC04", "Tháp học thuật chín tầng giúp lọc bỏ nguồn rác ngay từ đầu."),
        "action": "Nhân vật người que nghiên cứu gạch ranh giới phân tách 3 tầng đáy của Tháp Học Thuật 9 tầng",
        "setting": "Sơ đồ Tháp Học Thuật 9 tầng (Academic Pyramid) với 3 tầng đáy được khoanh vùng cảnh báo",
        "camera": "Toàn cảnh Tháp Học Thuật rồi zoom vào 3 tầng đáy",
        "scene_description": "Sơ đồ Tháp Học Thuật 9 tầng sắc nét theo phong cách Editorial Graphic với 3 tầng đáy được tô sắc độ xám nhạt tách biệt, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm thanh chắn đặt ngang phía trên tầng thứ ba của tháp trong cùng không gian bối cảnh",
        "anchor_quote": "lọc bỏ nguồn rác ngay từ đầu",
        "fx": "bounce",
        "x": 0.35,
    },
    {
        "scene_id": "SC22",
        "chapter": 4,
        "title": "Ba tầng giữa: Sách giáo trình, Luận văn và Kỷ yếu hội nghị",
        "purpose": "Phân tích vai trò của 3 tầng giữa trong việc nắm tổng quan nền tảng",
        "narration": "Tiến lên ba tầng giữa của tháp, bạn gặp sách giáo trình đại học, luận văn tốt nghiệp và bài báo hội nghị. Sách giáo trình giúp bạn nắm hệ thống khái niệm nền tảng đã được đóng gói ổn định. Trong khi đó, các kỷ yếu hội nghị cho bạn thấy những ý tưởng mới đang được thử nghiệm.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu bước lên tầng 4, 5, 6 của Tháp Học Thuật cầm cuốn sách chuyên khảo",
        "setting": "Ba tầng giữa của Tháp Học Thuật 9 tầng phát sáng màu xanh lam học thuật",
        "camera": "Lia dọc theo ba tầng giữa của tháp",
        "scene_description": "Phần thân giữa của Tháp Học Thuật 9 tầng hiển thị rõ biểu tượng Sách chuyên khảo, Luận văn và Kỷ yếu hội nghị, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày ôm cuốn sách chuyên khảo đứng bên tầng giữa của tháp trong cùng không gian bối cảnh",
        "anchor_quote": "ba tầng giữa của tháp",
        "fx": "pop",
        "x": 0.64,
    },
    {
        "scene_id": "SC23",
        "chapter": 4,
        "title": "Ba tầng đỉnh vàng: Bài báo Q1, Tổng quan hệ thống và Phân tích gộp",
        "purpose": "Khẳng định 3 tầng đỉnh cao nhất mang lại bằng chứng khoa học vững chắc nhất",
        "narration": "Vũ khí thật nằm ở đỉnh tháp. Đó là các bài báo thực nghiệm trên tạp chí chuẩn quốc tế, các bài tổng quan hệ thống và phân tích gộp. Mỗi bài phân tích gộp ở tầng cao nhất, đã chắt lọc kết quả từ hàng trăm công trình độc lập.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu chỉ ngọn cờ vào 3 tầng đỉnh vàng của Tháp Học Thuật",
        "setting": "Ba tầng đỉnh của Tháp Học Thuật 9 tầng tỏa sáng sắc nét",
        "camera": "Đẩy cận cảnh vào đỉnh Tháp Học Thuật",
        "scene_description": "Ba tầng đỉnh của Tháp Học Thuật 9 tầng nổi bật với biểu tượng Tạp chí Q1, Tổng quan hệ thống và Phân tích gộp, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày giơ cao kính lúp soi vào tầng đỉnh tháp trong cùng không gian bối cảnh",
        "anchor_quote": "ba tầng đỉnh của tháp học thuật",
        "fx": "pop_wobble",
        "x": 0.35,
    },
    {
        "scene_id": "SC24",
        "chapter": 4,
        "title": "Có nguồn tài liệu chuẩn rồi thì bắt đầu từ đâu?",
        "purpose": "Tạo bước ngoặt chuyển sang Chương 5 về quy trình chuỗi quyết định Q1",
        "narration": "Khi đã lọc được hai mươi tài liệu đỉnh tháp về máy, hầu hết sinh viên liền vội mở trình soạn thảo. [pause:800ms] Và đó chính là khoảnh khắc sai lầm, khi họ tự đẩy mình vào ngõ cụt của một bài viết rỗng.",
        "requirements": [],
        "source_ids": ["SRC05"],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu dừng tay trước biểu tượng Word để nhìn sang bản thiết kế kiến trúc nghiên cứu",
        "setting": "Ngã rẽ giữa thói quen mở Word gõ ngay và sơ đồ thiết kế nghiên cứu",
        "camera": "Góc máy kéo lùi mở ra chuỗi quyết định",
        "scene_description": "Đồ họa Editorial Graphic đặt biểu tượng trình soạn thảo bị khóa bên cạnh bản vẽ quy trình nghiên cứu 5 bước, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày giơ tay ra hiệu dừng lại trước biểu tượng soạn thảo trong cùng không gian bối cảnh",
        "anchor_quote": "tự đẩy mình vào ngõ cụt",
        "fx": "slide_left",
        "x": 0.64,
    },

    # ==================== CHAPTER 5: Bài Báo Không Bắt Đầu Ở Word (Question -> Gap -> Method -> Evidence) ====================
    {
        "scene_id": "SC25",
        "chapter": 5,
        "title": "Luật ngầm Q1: Bài báo không bao giờ bắt đầu ở Word",
        "purpose": "Bài báo khoa học không bắt đầu ở Word mà theo chuỗi câu hỏi, khoảng trống, phương pháp, bằng chứng",
        "narration": "Hãy nhớ một quy luật bất biến. Bài báo quốc tế bắt đầu từ khoảng trống tri thức chứ không phải Word. Trình soạn thảo chỉ là nơi ghi lại kết quả cuối cùng, khi chuỗi quyết định đã hoàn tất.",
        "requirements": ["R05"],
        "source_ids": ["SRC05"],
        "claim": ("Bài báo quốc tế bắt đầu từ khoảng trống tri thức chứ không phải Word.", "SRC05", "Bài báo quốc tế bắt đầu từ khoảng trống tri thức chứ không phải Word."),
        "action": "Nhân vật người que nghiên cứu gạch chéo mũi tên Mở Word đầu tiên và đặt nó về vị trí thứ 5 cuối chuỗi",
        "setting": "Sơ đồ Flowchart 5 bước: Question -> Gap -> Method -> Evidence -> Paper",
        "camera": "Toàn cảnh chuỗi Flowchart 5 bước ngang màn hình",
        "scene_description": "Sơ đồ Flowchart 5 khối rõ nét trên nền sáng: Câu hỏi -> Khoảng trống -> Phương pháp -> Bằng chứng -> Bài báo hoàn chỉnh, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày chỉ thước dọc theo 5 mắt xích của sơ đồ trong cùng không gian bối cảnh",
        "anchor_quote": "khoảng trống tri thức chứ không phải Word",
        "fx": "pop",
        "x": 0.35,
    },
    {
        "scene_id": "SC26",
        "chapter": 5,
        "title": "Mắt xích 1 và 2: Từ Câu hỏi nghiên cứu đến Khoảng trống tri thức",
        "purpose": "Giải thích cách định hình Research Question và Research Gap theo mô hình CARS",
        "narration": "Mắt xích đầu tiên luôn là một câu hỏi nghiên cứu sắc bén, nhắm vào nghịch lý chưa có lời giải. Ngay sau đó là mắt xích thứ hai, mang tên vùng trống nhận thức. Bạn phải chỉ ra được người đi trước đã làm tới đâu, và còn bỏ sót điểm mù nào.",
        "requirements": [],
        "source_ids": ["SRC05"],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu rọi đèn vào hai khối đầu tiên Question và Gap trên Flowchart",
        "setting": "Cận cảnh hai khối Question và Gap nối với nhau bằng mũi tên nhân quả",
        "camera": "Đẩy cận cảnh vào khối Khoảng trống tri thức",
        "scene_description": "Đồ họa Editorial Graphic phóng lớn hai khối đầu của Flowchart: Câu hỏi cốt lõi và Khoảng trống nghiên cứu phát sáng, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm kính lúp soi vào khe hở giữa các khối lý thuyết trong cùng không gian bối cảnh",
        "anchor_quote": "vùng trống nhận thức",
        "fx": "bounce",
        "x": 0.64,
    },
    {
        "scene_id": "SC27",
        "chapter": 5,
        "title": "Mắt xích 3: Thiết kế Phương pháp đo đạc chuẩn xác",
        "purpose": "Làm rõ vai trò của Method trong việc khóa chặt tính khách quan của nghiên cứu",
        "narration": "Khi điểm mù đã hiện rõ, bạn mới bước sang mắt xích thứ ba là thiết kế phương pháp. Phương pháp không phải là đoạn văn chép lại từ sách vở. Đó là bộ công cụ đo đạc bạn chọn, để giải quyết đúng điểm mù kia. Nếu chọn sai thước đo, mọi số liệu thu về đều bị bác bỏ.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu lắp bộ thước đo chuẩn xác vào khối thứ ba Method",
        "setting": "Khối thứ ba Phương pháp nghiên cứu với các tiêu chuẩn kiểm soát biến số",
        "camera": "Lia ngang từ khối Khoảng trống sang khối Phương pháp",
        "scene_description": "Sơ đồ Editorial Graphic vẽ khối Phương pháp đo đạc với cân chuẩn và sơ đồ kiểm soát biến số độc lập, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm compa và thước đo kiểm tra sơ đồ trong cùng không gian bối cảnh",
        "anchor_quote": "thiết kế phương pháp",
        "fx": "slide_left",
        "x": 0.35,
    },
    {
        "scene_id": "SC28",
        "chapter": 5,
        "title": "Mắt xích 4: Bằng chứng thực nghiệm không thể chối cãi",
        "purpose": "Khẳng định Evidence là trụ đỡ cho toàn bộ luận điểm khoa học",
        "narration": "Mắt xích thứ tư chính là dữ liệu thực tế thu được từ phép đo đó. Mọi công trình chuẩn mực đều đi từ câu hỏi đến bằng chứng thực nghiệm. Bảng biểu và đồ thị lúc này tự nó cất tiếng nói, trả lời thẳng cho nghi vấn ban đầu. Bạn không cần bất kỳ lời lẽ hoa mỹ nào để che đậy.",
        "requirements": [],
        "source_ids": ["SRC05"],
        "claim": ("Mọi công trình chuẩn mực đều đi từ câu hỏi đến bằng chứng thực nghiệm.", "SRC05", "Mọi công trình chuẩn mực đều đi từ câu hỏi đến bằng chứng thực nghiệm."),
        "action": "Nhân vật người que nghiên cứu đặt khối Bằng chứng thực nghiệm khớp hoàn hảo với Câu hỏi ban đầu",
        "setting": "Khối thứ tư Bằng chứng hiển thị biểu đồ dữ liệu thực nghiệm sắc nét",
        "camera": "Cận cảnh khối Bằng chứng thực nghiệm",
        "scene_description": "Đồ họa Editorial Graphic vẽ khối Bằng chứng thực nghiệm với biểu đồ phân tán và đường hồi quy chuẩn xác, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày chỉ tay vào điểm hội tụ trên biểu đồ dữ liệu trong cùng không gian bối cảnh",
        "anchor_quote": "bằng chứng thực nghiệm",
        "fx": "pop",
        "x": 0.64,
    },
    {
        "scene_id": "SC29",
        "chapter": 5,
        "title": "Mắt xích 5: Khi việc viết bài báo chỉ còn là lắp ghép",
        "purpose": "Chứng minh khi có đủ 4 mắt xích đầu thì việc viết Paper trên Word diễn ra tự nhiên",
        "narration": "Bốn mắt xích đã khóa chặt. Lúc này bạn mới bước tới khâu soạn thảo, không còn phải vắt óc bịa chữ cho đủ số trang. Bạn chỉ đơn giản là người dẫn đường, thuật lại toàn bộ lộ trình khám phá một cách mạch lạc.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu ung dung ghép 4 khối đã hoàn chỉnh thành bản thảo bài báo",
        "setting": "Toàn bộ chuỗi 5 mắt xích phát sáng đồng bộ dẫn tới bản thảo hoàn chỉnh",
        "camera": "Toàn cảnh chuỗi 5 mắt xích hoàn tất",
        "scene_description": "Chuỗi Flowchart 5 bước hoàn chỉnh tỏa sáng liền mạch dẫn tới biểu tượng bài báo khoa học xuất bản, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày mỉm cười tự tin đặt bút ký hoàn tất bản thảo trong cùng không gian bối cảnh",
        "anchor_quote": "bốn mắt xích trên đã khóa chặt",
        "fx": "pop_wobble",
        "x": 0.35,
    },
    {
        "scene_id": "SC30",
        "chapter": 5,
        "title": "Bí mật cách đọc bài báo của các giáo sư phản biện",
        "purpose": "Mở đường sang Chương 6 về chiến thuật đọc ngược bài báo khoa học Q1",
        "narration": "Hiểu được chuỗi năm mắt xích này, bạn sẽ giải mã được một bí mật thú vị khác. Tám mươi phần trăm người mới đọc tài liệu từ trang đầu đến trang cuối, đều nhanh chóng bỏ cuộc. Trong khi đó, giới học giả kỳ cựu luôn đọc theo một thứ tự hoàn toàn ngược lại.",
        "requirements": [],
        "source_ids": ["SRC06"],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu lật ngược chiều mũi tên đọc bài báo khoa học",
        "setting": "Sơ đồ cấu trúc một bài báo Q1 với các mũi tên nhảy cóc chiến lược",
        "camera": "Đẩy cận cảnh vào sơ đồ thứ tự đọc ngược",
        "scene_description": "Đồ họa Editorial Graphic vẽ một bài báo khoa học với đường mũi tên nhảy từ Tiêu đề xuống Kết luận rồi vòng lên Phương pháp, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm bút vẽ đường vòng cung đảo chiều đọc trong cùng không gian bối cảnh",
        "anchor_quote": "thứ tự hoàn toàn ngược lại",
        "fx": "bounce",
        "x": 0.64,
    },

    # ==================== CHAPTER 6: Giải Phẫu 1 Bài Báo Q1 Theo Thứ Tự Ngược ====================
    {
        "scene_id": "SC31",
        "chapter": 6,
        "title": "Vì sao đọc bài báo từ trang một đến trang cuối là tự sát?",
        "purpose": "Chiến lược giải phẫu bài báo chuẩn quốc tế theo thứ tự ngược của các giáo sư",
        "narration": "Một bài báo khoa học không phải là cuốn tiểu thuyết trinh thám, để bạn đọc tuần tự từng dòng. Nếu lao ngay vào phần lý thuyết và công thức ở trang hai, bạn sẽ kiệt sức rất nhanh. Các nhà nghiên cứu kỳ cựu không bao giờ đọc bài báo theo thứ tự xuôi.",
        "requirements": ["R06"],
        "source_ids": ["SRC06"],
        "claim": ("Các nhà nghiên cứu kỳ cựu không bao giờ đọc bài báo theo thứ tự xuôi.", "SRC06", "Các nhà nghiên cứu kỳ cựu không bao giờ đọc bài báo theo thứ tự xuôi."),
        "action": "Nhân vật người que nghiên cứu gạch bỏ mũi tên đọc thẳng từ trang 1 đến trang 20",
        "setting": "Sơ đồ đối sánh Cách đọc tuyến tính kiệt sức vs Chiến lược đọc 3 vòng (Three-Pass Approach)",
        "camera": "Toàn cảnh đối sánh hai cách đọc bài báo",
        "scene_description": "Đồ họa Editorial Graphic đối chiếu đường thẳng đọc tuần tự bị đứt gãy với sơ đồ 3 vòng quét chiến lược, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm tấm bảng chiến thuật 3 vòng đọc trong cùng không gian bối cảnh",
        "anchor_quote": "không bao giờ đọc bài báo theo thứ tự xuôi",
        "fx": "pop",
        "x": 0.35,
    },
    {
        "scene_id": "SC32",
        "chapter": 6,
        "title": "Vòng quét 1 (5 phút): Tiêu đề, Tóm tắt và nhảy thẳng xuống Kết luận",
        "purpose": "Hướng dẫn vòng đọc đầu tiên để nắm khung xương bài báo trong 5 phút",
        "narration": "Trong vòng quét đầu tiên kéo dài đúng năm phút, họ chỉ đọc tiêu đề, đoạn tóm tắt và các đề mục lớn. Ngay sau đó, họ lật thẳng về trang cuối cùng để đọc phần kết luận. Họ soi câu hỏi và kết luận trước khi kiểm tra bảng dữ liệu.",
        "requirements": [],
        "source_ids": ["SRC06"],
        "claim": ("Họ soi câu hỏi và kết luận trước khi kiểm tra bảng dữ liệu.", "SRC06", "Họ soi câu hỏi và kết luận trước khi kiểm tra bảng dữ liệu."),
        "action": "Nhân vật người que nghiên cứu nối trực tiếp đoạn Mở đầu với phần Kết luận ở trang cuối",
        "setting": "Sơ đồ Vòng quét 1 làm nổi bật 3 điểm chạm: Title/Abstract -> Section Headings -> Conclusions",
        "camera": "Lia nhanh từ trang đầu xuống trang cuối bài báo",
        "scene_description": "Sơ đồ Editorial Graphic làm sáng rõ 3 vùng trên bản thiết kế bài báo: Tóm tắt đầu trang, Tiêu đề mục và Kết luận cuối bài, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm đồng hồ bấm giờ năm phút chỉ vào trang cuối trong cùng không gian bối cảnh",
        "anchor_quote": "soi câu hỏi và kết luận trước",
        "fx": "slide_left",
        "x": 0.64,
    },
    {
        "scene_id": "SC33",
        "chapter": 6,
        "title": "Vòng quét 2 (15 phút): Đọc biểu đồ, bảng biểu và soi Phương pháp",
        "purpose": "Hướng dẫn vòng đọc thứ hai tập trung vào bằng chứng trực quan và thiết kế thực nghiệm",
        "narration": "Nếu bài báo thực sự liên quan đến đề tài, họ mới bước vào vòng quét thứ hai trong mười lăm phút. Lúc này họ chưa đọc lời bình, mà phóng to toàn bộ các đồ thị và bảng số liệu thực nghiệm. Một nhà khoa học giỏi sẽ tự đọc được câu chuyện từ biểu đồ, trước khi nghe tác giả giải thích.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu dùng kính lúp kiểm tra các trục tọa độ và cỡ mẫu trên biểu đồ bài báo",
        "setting": "Cận cảnh các bảng biểu và đồ thị thực nghiệm được tách riêng khỏi khối chữ",
        "camera": "Đặc tả vào biểu đồ kết quả thực nghiệm",
        "scene_description": "Đồ họa Editorial Graphic phóng lớn các biểu đồ cột, đường sai số chuẩn và bảng thông số thực nghiệm trên trang báo, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm kính lúp soi kỹ trục tọa độ đồ thị trong cùng không gian bối cảnh",
        "anchor_quote": "đọc được câu chuyện từ biểu đồ",
        "fx": "bounce",
        "x": 0.35,
    },
    {
        "scene_id": "SC34",
        "chapter": 6,
        "title": "Soi phần Thảo luận và Giới hạn nghiên cứu để tìm mỏ vàng",
        "purpose": "Chỉ ra rằng mục Limitations cuối bài báo chính là nơi ẩn giấu đề tài mới",
        "narration": "Mỏ vàng nằm ở cuối bài. Tại mục giới hạn nghiên cứu, chính các tác giả sẽ thú nhận những gì công trình chưa làm được. Mỗi giới hạn được chỉ ra trong một ấn phẩm đỉnh cao, chính là gợi ý đắt giá cho đề tài mới.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu tìm thấy viên kim cương ý tưởng ngay tại mục Giới hạn nghiên cứu (Limitations)",
        "setting": "Mục Limitations & Future Work cuối bài báo phát sáng như kho báu",
        "camera": "Đẩy cận cảnh vào ô Limitations & Future Work",
        "scene_description": "Đồ họa Editorial Graphic làm nổi bật khung Giới hạn nghiên cứu ở cuối bài báo với biểu tượng tia sáng ý tưởng mới, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày mỉm cười nâng mảnh ghép phát sáng lấy ra từ ô giới hạn trong cùng không gian bối cảnh",
        "anchor_quote": "mỏ vàng gợi mở đề tài mới",
        "fx": "pop",
        "x": 0.64,
    },
    {
        "scene_id": "SC35",
        "chapter": 6,
        "title": "Vòng quét 3 (60 phút): Tái dựng giả định và phản biện ngược",
        "purpose": "Giải thích vòng đọc sâu nhất dành cho 3-5 bài báo trụ cột của khóa luận",
        "narration": "Chỉ với ba đến năm bài báo trụ cột quan trọng nhất, bạn mới thực hiện vòng quét thứ ba. Ở vòng này, bạn đặt mình vào vị trí tác giả để tự tái dựng lại toàn bộ chuỗi lập luận. Bạn tự hỏi nếu giữ nguyên dữ liệu đó nhưng đổi một giả định gốc, kết quả sẽ thay đổi ra sao.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu tháo lắp lại từng khối giả định của bài báo trụ cột trên bàn thiết kế",
        "setting": "Bàn thiết kế tư duy phân rã bài báo gốc thành các khối giả định để thử nghiệm",
        "camera": "Trung cảnh góc nhìn ngang bàn thiết kế",
        "scene_description": "Sơ đồ Editorial Graphic vẽ cấu trúc giải phẫu 3D của một bài báo trụ cột đang được tháo rời từng tầng giả định, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm cờ-lê tư duy điều chỉnh khối giả định gốc trong cùng không gian bối cảnh",
        "anchor_quote": "tái dựng lại toàn bộ chuỗi lập luận",
        "fx": "pop_wobble",
        "x": 0.35,
    },
    {
        "scene_id": "SC36",
        "chapter": 6,
        "title": "Bài toán tổng hợp 30 bài báo cùng lúc",
        "purpose": "Chuyển cảnh sang Chương 7 về cách dùng AI và Research Gap Matrix để xử lý 30 bài báo",
        "narration": "Giải phẫu một ấn phẩm đơn lẻ đã rõ, nhưng khi làm luận văn, bạn phải xử lý hàng chục tài liệu cùng lúc. Làm sao để kết nối những mảnh ghép rời rạc đó, thành một bức tranh thống nhất mà không loạn trí? Đây là lúc bạn cần đến vũ khí tư duy của kỷ nguyên mới.",
        "requirements": [],
        "source_ids": ["SRC07"],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu đứng trước 30 bài báo Q1 xếp thành hàng chờ được đưa vào Ma trận",
        "setting": "Không gian chuyển giao từ 1 bài báo đơn lẻ sang mạng lưới 30 bài báo Q1",
        "camera": "Kéo rộng toàn cảnh 30 bài báo liên kết thành lưới",
        "scene_description": "Đồ họa Editorial Graphic vẽ 30 thẻ bài báo Q1 đang hội tụ về một bảng ma trận trung tâm lớn, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày đứng trước bảng điều khiển ma trận phân tích trong cùng không gian bối cảnh",
        "anchor_quote": "vũ khí tư duy của kỷ nguyên mới",
        "fx": "slide_left",
        "x": 0.64,
    },

    # ==================== CHAPTER 7: Vũ Khí Tư Duy Học Thuật & Research Gap Matrix ====================
    {
        "scene_id": "SC37",
        "chapter": 7,
        "title": "Vì sao nhờ AI viết hộ tổng quan tài liệu luôn bị phát hiện?",
        "purpose": "Biến ba mươi bài báo rời rạc thành ma trận khoảng trống nghiên cứu thay vì nhờ viết hộ",
        "narration": "Đứng trước hàng chục tập tài liệu tiếng Anh dày đặc, nhiều người liền bảo máy viết hộ mục tổng quan. Kết quả trả về là những đoạn văn trơn tru, nhưng liệt kê vô hồn kiểu người này nói gì, người kia nói gì. Dùng trí tuệ nhân tạo viết hộ tổng quan luôn lộ lỗi sáo rỗng.",
        "requirements": ["R07"],
        "source_ids": ["SRC07"],
        "claim": ("Dùng trí tuệ nhân tạo viết hộ tổng quan luôn lộ lỗi sáo rỗng.", "SRC07", "Dùng trí tuệ nhân tạo viết hộ tổng quan luôn lộ lỗi sáo rỗng."),
        "action": "Nhân vật người que nghiên cứu cầm bút đỏ gạch chéo văn bản tổng quan liệt kê rời rạc A nói - B nói - C nói",
        "setting": "Sơ đồ bóc tách lỗi liệt kê vô hồn khi dùng AI viết hộ tổng quan tài liệu",
        "camera": "Đặc tả các dòng liệt kê bị gạch đỏ",
        "scene_description": "Đồ họa Editorial Graphic hiển thị trang văn bản liệt kê rời rạc Tác giả A, Tác giả B bị đóng dấu Lỗi sáo rỗng, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày lắc đầu gạch chéo tờ văn bản liệt kê trong cùng không gian bối cảnh",
        "anchor_quote": "luôn lộ lỗi sáo rỗng",
        "fx": "pop",
        "x": 0.35,
    },
    {
        "scene_id": "SC38",
        "chapter": 7,
        "title": "Bản chất của mục Tổng quan tài liệu không phải là tóm tắt",
        "purpose": "Khẳng định Literature Review là cuộc đối thoại và phản biện giữa các trường phái",
        "narration": "Tổng quan không phải tóm tắt. Hội đồng phát hiện ngay văn viết hộ, vì bạn chỉ liệt kê rời rạc từng bài. Bản chất của mục này là đặt các nhóm học giả lên bàn tròn, chỉ ra họ đang tranh luận và mâu thuẫn ở đâu.",
        "requirements": [],
        "source_ids": ["SRC07"],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu điều phối cuộc đối thoại phản biện chéo giữa ba nhóm trường phái lý thuyết",
        "setting": "Sơ đồ bàn tròn phản biện chéo giữa Trường phái A, Trường phái B và Thực nghiệm C",
        "camera": "Toàn cảnh sơ đồ giao thoa và xung đột lý thuyết",
        "scene_description": "Sơ đồ Editorial Graphic vẽ ba vòng tròn trường phái lý thuyết giao nhau với các mũi tên phản biện chéo tại tâm, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày chỉ tay vào vùng giao thoa trung tâm của ba vòng tròn trong cùng không gian bối cảnh",
        "anchor_quote": "tranh luận với nhau",
        "fx": "bounce",
        "x": 0.64,
    },
    {
        "scene_id": "SC39",
        "chapter": 7,
        "title": "Kiến trúc Ma trận Khoảng trống Nghiên cứu (Research Gap Matrix)",
        "purpose": "Hướng dẫn cấu trúc 5 cột của Research Gap Matrix để gom 30 bài báo Q1",
        "narration": "Hãy dựng bảng ma trận ngay. Ma trận đối chiếu giúp gom ba mươi bài báo thành khoảng trống rõ nét. Thay vì đọc rời rạc từng tệp, bạn chuẩn hóa toàn bộ nguồn tài liệu vào một bảng năm cột chiến lược.",
        "requirements": [],
        "source_ids": ["SRC07"],
        "claim": ("Ma trận đối chiếu giúp gom ba mươi bài báo thành khoảng trống rõ nét.", "SRC07", "Ma trận đối chiếu giúp gom ba mươi bài báo thành khoảng trống rõ nét."),
        "action": "Nhân vật người que nghiên cứu dựng bảng Ma trận Khoảng trống Nghiên cứu 5 cột sắc nét",
        "setting": "Bảng Research Gap Matrix 5 cột: Bối cảnh mẫu, Biến độc lập, Phương pháp đo, Kết quả chính, Giới hạn bỏ ngỏ",
        "camera": "Đẩy cận cảnh vào cấu trúc 5 cột của Ma trận",
        "scene_description": "Bảng Ma trận Khoảng trống Nghiên cứu 5 cột kẻ ô chuẩn mực theo phong cách Editorial Graphic với cột thứ 5 Giới hạn bỏ ngỏ phát sáng, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm thước chỉ dọc cột Giới hạn bỏ ngỏ của bảng ma trận trong cùng không gian bối cảnh",
        "anchor_quote": "thành khoảng trống rõ nét",
        "fx": "pop",
        "x": 0.35,
    },
    {
        "scene_id": "SC40",
        "chapter": 7,
        "title": "Cách dùng AI phản biện chéo lý thuyết thay vì viết hộ",
        "purpose": "Hướng dẫn quy trình nạp cụm tài liệu dài để truy vấn điểm mâu thuẫn phương pháp",
        "narration": "Khi nạp trọn bộ hồ sơ học thuật vào bộ nhớ ngữ cảnh lớn, bạn tuyệt đối không ra lệnh viết hộ chương hai. Bạn đặt câu hỏi truy vấn rằng giữa các nghiên cứu này, những giả định nào đang xung đột trực tiếp với nhau. Ngay lập tức, các đứt gãy về phương pháp và mẫu khảo sát sẽ hiện lên rõ mồn một.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu chiếu tia sáng truy vấn làm bật lên các điểm xung đột giữa 30 bài báo",
        "setting": "Giao diện sơ đồ ngữ cảnh lớn kết nối 30 tài liệu và làm nổi bật các nút xung đột",
        "camera": "Lia ngang qua mạng lưới truy vấn chéo",
        "scene_description": "Đồ họa Editorial Graphic vẽ mạng lưới 30 tài liệu được quét qua lăng kính phân tích làm sáng lên 3 điểm đứt gãy phương pháp, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm kính lúp lớn khóa mục tiêu vào điểm đứt gãy trong cùng không gian bối cảnh",
        "anchor_quote": "xung đột trực tiếp với nhau",
        "fx": "slide_left",
        "x": 0.64,
    },
    {
        "scene_id": "SC41",
        "chapter": 7,
        "title": "Ba loại khoảng trống nghiên cứu đắt giá nhất",
        "purpose": "Phân loại 3 dạng Research Gap: Khoảng trống bằng chứng, Khoảng trống phương pháp và Khoảng trống bối cảnh",
        "narration": "Từ bảng tổng hợp đó, bạn dễ dàng khoanh vùng được một trong ba loại khoảng trống đắt giá nhất. Một là khoảng trống bằng chứng, khi các kết quả thực nghiệm trước đó trái ngược nhau. Hai là khoảng trống phương pháp khi thước đo cũ bị lệch, và ba là khoảng trống bối cảnh tại Việt Nam.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu chỉ vào 3 nhánh khoảng trống: Bằng chứng (Evidence Gap), Phương pháp (Method Gap), Bối cảnh (Context Gap)",
        "setting": "Sơ đồ 3 trụ cột Research Gap tách ra từ Ma trận Khoảng trống Nghiên cứu",
        "camera": "Toàn cảnh 3 trụ cột Khoảng trống nghiên cứu",
        "scene_description": "Sơ đồ Editorial Graphic chia 3 nhánh rõ nét: Khoảng trống bằng chứng, Khoảng trống phương pháp và Khoảng trống bối cảnh thực tiễn, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày đánh dấu tích chọn nhánh khoảng trống phù hợp trong cùng không gian bối cảnh",
        "anchor_quote": "ba loại khoảng trống đắt giá nhất",
        "fx": "pop_wobble",
        "x": 0.35,
    },
    {
        "scene_id": "SC42",
        "chapter": 7,
        "title": "Tấm bản đồ hoàn chỉnh trước giờ bước vào phòng bảo vệ",
        "purpose": "Khép lại Chương 7 bằng sự tự tin khi nắm trọn Ma trận Khoảng trống và dẫn sang Chương 8",
        "narration": "Khi trong tay đã có tấm bản đồ tổng hợp sắc bén, bạn không còn sợ bất kỳ câu hỏi vặn nào về tính mới. [pause:800ms] Giờ là lúc bước vào thử thách cuối cùng, nơi thời khắc mở màn sẽ định đoạt kết quả phòng bảo vệ.",
        "requirements": [],
        "source_ids": ["SRC08"],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu cầm tấm bản đồ Ma trận Khoảng trống tiến thẳng tới cánh cửa Phòng Bảo Vệ",
        "setting": "Cánh cửa phòng bảo vệ khóa luận mở ra với đồng hồ đếm ngược 120 giây",
        "camera": "Đẩy thẳng qua cánh cửa phòng bảo vệ",
        "scene_description": "Cánh cửa phòng hội đồng bảo vệ khóa luận mở rộng với đồng hồ 120 giây nổi bật phía trên bục thuyết trình, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày cầm tập hồ sơ ma trận bước đi đĩnh đạc trong cùng không gian bối cảnh",
        "anchor_quote": "thời khắc mở màn sẽ định đoạt",
        "fx": "bounce",
        "x": 0.64,
    },

    # ==================== CHAPTER 8: Tâm Lý Học Phòng Bảo Vệ 120 Giây & Khép Vòng Lặp ====================
    {
        "scene_id": "SC43",
        "chapter": 8,
        "title": "Cửa sổ 120 giây đầu tiên dưới góc nhìn Hội đồng bảo vệ",
        "purpose": "Tâm lý học phòng bảo vệ khóa luận trong một trăm hai mươi giây đầu và khép vòng lặp",
        "narration": "Hai phút đầu quyết định tất cả. Khi bạn bước lên bục, giám khảo không hề nghe những dòng định nghĩa sách giáo khoa trên màn chiếu. Hội đồng bảo vệ định hình phán quyết ngay trong hai phút đầu tiên.",
        "requirements": ["R08"],
        "source_ids": ["SRC08"],
        "claim": ("Hội đồng bảo vệ định hình phán quyết ngay trong hai phút đầu tiên.", "SRC08", "Hội đồng bảo vệ định hình phán quyết ngay trong hai phút đầu tiên."),
        "action": "Góc nhìn từ bàn Hội đồng bảo vệ lật nhanh tập khóa luận trong cửa sổ 120 giây đầu",
        "setting": "Phòng bảo vệ khóa luận với đồng hồ 120 giây và góc nhìn trực diện từ bàn giám khảo",
        "camera": "Góc nhìn qua vai hội đồng hướng lên bục bảo vệ",
        "scene_description": "Đồ họa Editorial Graphic vẽ bàn hội đồng phản biện với tập khóa luận đang mở ở trang Danh mục tài liệu và đồng hồ 120 giây, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày đứng thẳng tự tin trên bục thuyết trình trong cùng không gian bối cảnh",
        "anchor_quote": "ngay trong hai phút đầu tiên",
        "fx": "pop",
        "x": 0.35,
    },
    {
        "scene_id": "SC44",
        "chapter": 8,
        "title": "Ba điểm hội đồng lật xem đầu tiên trong cuốn khóa luận",
        "purpose": "Tiết lộ 3 vị trí giám khảo kiểm tra ngay khi cầm cuốn khóa luận",
        "narration": "Ngay khi bạn vừa cất lời chào, tay của giám khảo đã lật thẳng về trang danh mục tài liệu tham khảo. Họ nhìn xem bạn đứng trên vai những công trình chuẩn quốc tế nào, hay chỉ toàn trích dẫn nguồn thứ cấp cũ kỹ. Tiếp đó, mắt họ quét thẳng vào câu hỏi nghiên cứu và mô hình phương pháp.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu chỉ vào 3 điểm kiểm tra của giám khảo: Tài liệu tham khảo Q1 -> Câu hỏi & Gap -> Mô hình đo đạc",
        "setting": "Sơ đồ X-quang cuốn khóa luận làm sáng 3 vị trí quyết định",
        "camera": "Cận cảnh 3 điểm sáng trên sơ đồ cuốn khóa luận",
        "scene_description": "Sơ đồ Editorial Graphic cắt lớp cuốn khóa luận làm nổi bật 3 vùng: Nguồn trích dẫn Q1, Khoảng trống nghiên cứu và Thiết kế phương pháp, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày chỉ cây bút vào ba điểm kiểm định trong cùng không gian bối cảnh",
        "anchor_quote": "danh mục tài liệu tham khảo",
        "fx": "slide_left",
        "x": 0.64,
    },
    {
        "scene_id": "SC45",
        "chapter": 8,
        "title": "Sai lầm trả lời câu hỏi 'Đề tài này có gì mới?' bằng số liệu rời rạc",
        "purpose": "Chỉ ra sai lầm của sinh viên khi đốt mất 2 phút đầu vào giới thiệu lan man",
        "narration": "Phần lớn người thuyết trình đánh mất thiện cảm của hội đồng, vì đốt năm phút đầu để đọc lại lý thuyết cơ bản. Khi bị hỏi đề tài này có gì mới, họ lại cuống cuồng liệt kê hàng loạt bảng số liệu chi tiết. Số liệu nhiều đến mấy cũng vô nghĩa, nếu bạn không chỉ ra được lỗ hổng mà nó lấp đầy.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu đổ mồ hôi khi chiếu slide chữ dày đặc trước câu hỏi Đề tài có gì mới?",
        "setting": "Đối sánh Slide chữ dày đặc gây ngợp vs Sơ đồ định vị khoảng trống gọn sắc",
        "camera": "Trung cảnh đối chiếu phản ứng phòng bảo vệ",
        "scene_description": "Đồ họa Editorial Graphic đặt khung trình chiếu nhồi nhét chữ bị gạch chéo bên cạnh khung định vị khoảng trống 3 bước tinh gọn, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày lau mồ hôi trước tấm bảng nhồi nhét chữ trong cùng không gian bối cảnh",
        "anchor_quote": "đề tài này có gì mới",
        "fx": "bounce",
        "x": 0.35,
    },
    {
        "scene_id": "SC46",
        "chapter": 8,
        "title": "Cấu trúc 3 bước làm chủ câu hỏi phản biện của Hội đồng",
        "purpose": "Cung cấp công thức 3 bước trả lời hội đồng: Các nghiên cứu trước đã làm A -> Còn bỏ ngỏ B -> Đề tài giải quyết B bằng C",
        "narration": "Để chinh phục hội đồng ngay trong một trăm hai mươi giây đầu, hãy dùng cấu trúc phản biện ba bước. Bước một khẳng định các nghiên cứu trước đã giải quyết được phần nào, bước hai chỉ thẳng vào lỗ hổng họ còn bỏ ngỏ. Trình bày rõ khoảng trống và phương pháp giúp bạn làm chủ hội đồng.",
        "requirements": [],
        "source_ids": ["SRC08"],
        "claim": ("Trình bày rõ khoảng trống và phương pháp giúp bạn làm chủ hội đồng.", "SRC08", "Trình bày rõ khoảng trống và phương pháp giúp bạn làm chủ hội đồng."),
        "action": "Nhân vật người que nghiên cứu trình bày rõ 3 khối: (1) Đã biết -> (2) Khoảng trống bỏ ngỏ -> (3) Đóng góp mới của đề tài",
        "setting": "Sơ đồ Cấu trúc Phản biện 3 Bước hiển thị sắc nét trên màn chiếu phòng bảo vệ",
        "camera": "Đẩy cận cảnh vào sơ đồ 3 bước phản biện",
        "scene_description": "Sơ đồ 3 bước phản biện chuẩn Editorial Graphic: Bước 1 Nền tảng đi trước -> Bước 2 Lỗ hổng bỏ ngỏ -> Bước 3 Giải pháp đo đạc mới, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày chỉ tay dứt khoát vào Bước 3 Giải pháp mới trong cùng không gian bối cảnh",
        "anchor_quote": "làm chủ hội đồng",
        "fx": "pop",
        "x": 0.64,
    },
    {
        "scene_id": "SC47",
        "chapter": 8,
        "title": "Sự chuyển hóa từ người học vẹt sang nhà nghiên cứu độc lập",
        "purpose": "Tổng kết toàn bộ hành trình 4 trụ cột: Phá ảo giác năng lực -> Feynman -> Tháp Q1 & Gap Matrix -> Phòng bảo vệ",
        "narration": "Nhìn lại toàn bộ hành trình vừa qua, bạn sẽ thấy nghiên cứu khoa học không phải là một nghi thức xa vời. Nó bắt đầu từ lúc bạn dám gấp cuốn sách lại, để tự kiểm tra bản chất bằng ngôn từ giản dị. Nó trưởng thành khi bạn biết lọc nguồn qua tháp học thuật, và dựng ma trận khoảng trống trước khi mở Word.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Toàn cảnh 4 sơ đồ trụ cột kết nối thành hệ thống Tư Duy Nghiên Cứu hoàn chỉnh",
        "setting": "Bản đồ tổng kết 4 trụ cột: Truy xuất chủ động -> Kỹ thuật Feynman -> Tháp Học Thuật & Gap Matrix -> Cấu trúc 120s",
        "camera": "Toàn cảnh mở rộng bốn trụ cột tư duy",
        "scene_description": "Bản đồ tổng hợp 4 trụ cột Tư Duy Nghiên Cứu vẽ bằng đường nét kiến trúc sắc sảo trên nền giấy biên tập ấm áp, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày đứng ở vị trí trung tâm kết nối bốn trụ cột trong cùng không gian bối cảnh",
        "anchor_quote": "ma trận khoảng trống trước khi mở Word",
        "fx": "pop_wobble",
        "x": 0.35,
    },
    {
        "scene_id": "SC48",
        "chapter": 8,
        "title": "Khép vòng lặp lúc hai giờ sáng: Trang giấy trắng trở thành bản thiết kế",
        "purpose": "Khép vòng lặp hoàn hảo về hình ảnh bàn học đêm khuya ở SC01 với tâm thế hoàn toàn mới",
        "narration": "Đêm nay mọi thứ đã khác. Ngồi trước bàn học, bạn không còn tô màu kín sách trong nỗi hoang mang nữa. Trang giấy trắng giờ đây là nơi bạn tự tin vẽ nên, khoảng trống tri thức của riêng mình.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Nhân vật người que nghiên cứu mỉm cười đặt bút vẽ sơ đồ Question -> Gap -> Method lên trang giấy dưới ánh đèn bàn ấm áp",
        "setting": "Bàn học sinh viên Việt Nam ấm áp khép lại vòng lặp với sơ đồ nghiên cứu sáng rõ",
        "camera": "Từ cận cảnh ngòi bút kéo lùi nhẹ nhàng kết thúc",
        "scene_description": "Bàn học tĩnh lặng dưới ánh đèn vàng ấm áp với cuốn giáo trình đã gấp gọn và tờ sơ đồ khoảng trống nghiên cứu hoàn chỉnh, không có nhân vật",
        "figure_action": "Hình tượng Nhân vật người que nghiên cứu đầu tròn trắng viền đen dày mỉm cười thư thái đặt bút hoàn tất sơ đồ trong cùng không gian bối cảnh",
        "anchor_quote": "khoảng trống tri thức của riêng mình",
        "fx": "pop",
        "x": 0.64,
    },
]


def create_academic_research_13m_topic(
    aspect_ratio: str = "16:9",
    subtitles: bool = False,
) -> ResearchedTopic:
    """Build the 8-chapter, 48-scene Schema 3.0 ResearchedTopic for the Academic Research & Knowledge Decoding niche."""
    sources = get_academic_sources()
    required_points = get_required_points()
    characters = [
        {
            "id": "CH01",
            "name": "Nhân vật người que nghiên cứu",
            "appearance": "Hình tượng người que đầu tròn trắng viền đen dày khép kín, mắt chấm oval tối giản, thân nét mực mảnh, tạo hình thống nhất trong các ảnh toàn khung",
            "outfit": "Trang phục học thuật tối giản nét vẽ mực đen, tạo hình thống nhất giữa các ảnh toàn khung",
        }
    ]

    scenes: List[ResearchedScene] = []
    total_scenes = len(RAW_SCENES_DATA)
    for idx, item in enumerate(RAW_SCENES_DATA):
        s_id = item["scene_id"]
        is_last = (idx == total_scenes - 1)
        p_tail = 0.35 if is_last else 0.70
        pause_sec, _, _ = extract_pauses(item["narration"])
        syl = count_syllables(item["narration"], lang="vi")
        calibrated_dur = round(pause_sec + (syl / 4.0) + p_tail, 2)

        claim_facts = [item["claim"]] if item["claim"] is not None else []
        scenes.append(
            ResearchedScene(
                scene_id=s_id,
                title=item["title"],
                purpose=item["purpose"],
                duration=calibrated_dur,
                narration=item["narration"],
                requirements=list(item["requirements"]),
                source_ids=list(item["source_ids"]),
                character_ids=["CH01"],
                action=item["action"],
                setting=item["setting"],
                camera=item["camera"],
                scene_description=compose_full_frame_description(item["scene_description"], item["figure_action"]),
                foley_cue="Tiếng bút dạ quang gạch giấy, tiếng lật trang tài liệu, tiếng tích tắc đồng hồ phòng bảo vệ và âm thanh khóa mục tiêu",
                claim_facts=claim_facts,
                tone="reflective_slow" if s_id in ("SC06", "SC24", "SC42", "SC48") else ("narrative_warm" if item["chapter"] in (1, 8) else "analytical_crisp"),
            )
        )

    return ResearchedTopic(
        topic="Giải Mã Tư Duy Nghiên Cứu, Bản Chất Tri Thức & Luật Ngầm Học Thuật: Vì Sao Học Vẹt & Mở Word Gõ Ngay Luôn Thất Bại, Cách Giải Phẫu Bài Báo Q1 & Ma Trận Khoảng Trống Nghiên Cứu",
        audience="Sinh viên, học viên cao học, giảng viên trẻ, kỹ sư và người tự học tại Việt Nam muốn bóc tách bản chất tri thức và làm chủ quy trình nghiên cứu chuẩn quốc tế Q1",
        goal="Phá vỡ ảo giác năng lực khi đọc thụ động, nắm vững 4 cấp độ tri thức, kỹ thuật Feynman, Tháp Học Thuật 9 tầng, chuỗi Question -> Gap -> Method -> Evidence, cách đọc ngược bài báo Q1, Ma trận Khoảng trống Nghiên cứu và tâm lý 120s phòng bảo vệ",
        video_type="science_history_explainer",
        min_duration=480.0,
        max_duration=960.0,
        style="Minh hoạ Editorial Graphic 2D toàn khung, nhân vật người que tương tác vật lý với Sơ đồ Tháp Học Thuật, Flowchart Question -> Gap -> Method -> Evidence và Ma trận Khoảng trống trong cùng bố cục ngang 16:9; không tách sticker.",
        aspect_ratio=aspect_ratio,
        format_profile="long_16x9" if aspect_ratio == "16:9" else None,
        sources=sources,
        required_points=required_points,
        characters=characters,
        scenes=scenes,
        tone="Điềm đạm, sắc sảo, thông tuệ, chạm trúng tâm lý học thuật như người đàn anh hướng dẫn nghiên cứu",
        language="vi",
        subtitles=subtitles,
        voice="Adam",
        speed=1.22,
        conversational_facts=True,
        packaging=PackagingSpec(
            youtube_title="Nghịch Lý Tri Thức: Vì Sao Học Chăm Vẫn Bế Tắc Ở NCKH?",
            visual_hook="Nhân vật người que dùng bút đỏ gạch chéo trang Word lúc 2 giờ sáng trước Sơ đồ Tháp Học Thuật 9 tầng",
            text_overlay="BIẾT TÍNH ≠ HIỂU!",
            contrast_pair="Học vẹt mở Word gõ ngay vs. Ma trận Khoảng trống Q1",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_1_broad",
            seo_keywords=[
                "tư duy nghiên cứu khoa học",
                "nghịch lý tri thức",
                "ảo giác năng lực",
                "cách đọc bài báo Q1",
                "ma trận khoảng trống nghiên cứu",
                "bảo vệ khóa luận tốt nghiệp",
            ],
        ),
    )


def _semantic_full_frame_shot(
    scene: ResearchedScene,
    cue_text: str,
    shot_index: int,
    shots_in_cue: int,
) -> Tuple[str, str]:
    """Choose a complete-frame view from the spoken concept, without a fixed shot cycle."""
    cue = cue_text.casefold()
    action = re.sub(r"(?i)sticker\s+nghiên\s+cứu|sticker", "nhân vật người que", scene.action)
    environment = re.sub(r"(?i)(?:,?\s*)(?:không có nhân vật(?: nào)?|no characters(?: anywhere)?)\.?$", "", scene.scene_description)
    if shot_index > 0 and shots_in_cue > 1:
        framing = "In-place Action Variation"
        focus = "Keep the same setting and camera relationship; change the visible hand action, expression, or focal prop for this spoken beat."
    elif re.search(r"\d|\b(giờ|phút|lần|tầng|số|năm)\b", cue):
        framing = "Macro Prop Close-up"
        focus = "Use a close full-frame view of the concrete number-bearing object or diagram detail in this phrase."
    elif any(term in cue for term in ("?", "là gì", "what is", "vs", "khác biệt", "nghịch lý")):
        framing = "White Concept Card"
        focus = "Use a complete, uncluttered white-background scene card to isolate the concept; do not create a cutout or sticker element."
    elif any(term in cue for term in ("question", "gap", "method", "evidence", "tháp", "ma trận", "sơ đồ", "bằng chứng")):
        framing = "Diagram Detail in Full Scene"
        focus = "Make the named diagram node or relationship the clear focal point, with the figure still part of the same scene."
    else:
        framing = "Wide Full-frame Scene"
        focus = "Show the complete physical setting and integrate the figure, furniture, and props naturally in it."
    if framing == "White Concept Card":
        description = (
            f"Full-frame white concept card for the idea in this spoken phrase: {cue_text}. "
            f"Use simple editorial symbols related to {scene.title}; {focus} "
            "The white background fills the whole image; do not add a detached cutout, sticker border, or narration lettering."
        )
    else:
        description = (
            f"{environment}. Setting: {scene.setting}. Action: {action}. "
            f"Visual focus from this spoken phrase: {cue_text}. {focus} "
            "Render one cohesive full-frame illustration; do not isolate any foreground subject, add a white sticker border, or draw the narration as text."
        )
    return framing, description


def build_multi_chapter_bundle(
    bundle_dir: Path,
    topic: ResearchedTopic,
) -> Dict[str, Any]:
    """Generate the 8-chapter execution bundle in `sys/exports/academic_research_paradox_bundle/`
    with narration-anchored full-frame beat timing and no background/sticker layers.
    """
    manifest_dir = bundle_dir / "manifest"
    scripts_dir = bundle_dir / "scripts"
    templates_dir = bundle_dir / "templates"
    audio_dir = bundle_dir / "audio"
    generated_images_dir = bundle_dir / "generated_images"
    rendered_chapters_dir = bundle_dir / "rendered_chapters"

    for d in (manifest_dir, scripts_dir, templates_dir, audio_dir, generated_images_dir, rendered_chapters_dir):
        d.mkdir(parents=True, exist_ok=True)

    scene_by_id = {s.scene_id: s for s in topic.scenes}
    danger_zone_max_hold = 1.75  # 0:00 - 0:15 (SC01-SC02 in Ch1): 1.2s - 1.8s fast visual beats
    body_zone_max_hold = 3.70    # After 0:15 (SC03..SC48): <= 3.80s standard Cue-Window Allocation

    all_shots: List[Dict[str, Any]] = []
    all_cue_records: List[Dict[str, Any]] = []
    chapter_manifests: List[Dict[str, Any]] = []
    global_shot_idx = 1

    for ch_meta in CHAPTER_METADATA:
        ch_num = ch_meta["chapter"]
        ch_scenes: List[ResearchedScene] = [scene_by_id[sid] for sid in ch_meta["scene_ids"]]
        ch_shots: List[Dict[str, Any]] = []
        ch_cues: List[Dict[str, Any]] = []
        remotion_scenes: List[Dict[str, Any]] = []

        accum_scene = 0.0
        cue_counter = 1
        for sc in ch_scenes:
            sc_start = round(accum_scene, 3)
            sc_dur = sc.duration
            sent_tuples = split_narration_with_pauses(sc.narration)

            raw_weights = []
            for sent, pause_s in sent_tuples:
                syl = max(1, count_syllables(sent, lang="vi"))
                p_dur = pause_s if pause_s > 0 else 0.28
                raw_weights.append((syl / 4.0) + p_dur)
            total_w = sum(raw_weights) if raw_weights else 1.0

            cur_sc_cursor = sc_start
            for s_i, (sent, pause_s) in enumerate(sent_tuples):
                dur_fraction = (raw_weights[s_i] / total_w) * sc_dur
                s_start = round(cur_sc_cursor, 3)
                w_end = round(sc_start + sc_dur, 3) if s_i == len(sent_tuples) - 1 else round(cur_sc_cursor + dur_fraction, 3)
                p_dur = pause_s if pause_s > 0 else 0.28
                s_end = round(max(s_start + 0.5, w_end - p_dur), 3)
                clean_sent = strip_pause_tags(sent)
                ch_cues.append({
                    "index": cue_counter,
                    "scene_id": sc.scene_id,
                    "text": clean_sent if clean_sent.endswith((".", "?", "!")) else clean_sent + ".",
                    "start": s_start,
                    "end": s_end,
                    "win_start": s_start,
                    "win_end": w_end,
                    "win_dur": round(w_end - s_start, 3),
                })
                cur_sc_cursor = w_end
                cue_counter += 1
            accum_scene = round(accum_scene + sc_dur, 3)
        ch_duration = round(accum_scene, 2)

        for sc_pos, sc in enumerate(ch_scenes):
            sc_cues = [c for c in ch_cues if c["scene_id"] == sc.scene_id]
            sc_start = 0.0 if sc_pos == 0 else sc_cues[0]["win_start"]
            sc_end = ch_duration if sc_pos == len(ch_scenes) - 1 else sc_cues[-1]["win_end"]

            cue_shot_counts = []
            for cue in sc_cues:
                cue_in_cold_open = ch_num == 1 and cue["win_start"] < 15.0
                max_hold = danger_zone_max_hold if cue_in_cold_open else body_zone_max_hold
                cue_shot_counts.append(max(1, math.ceil(cue["win_dur"] / max_hold)))
            semantic_shots = [
                _semantic_full_frame_shot(sc, cue["text"], shot_index, shot_count)
                for cue, shot_count in zip(sc_cues, cue_shot_counts, strict=False)
                for shot_index in range(shot_count)
            ]
            semantic_effects = assign_scene_camera_effects([framing for framing, _ in semantic_shots])
            sc_beat_images: List[Dict[str, Any]] = []
            sc_root_shot_idx = global_shot_idx
            b_cursor = 0
            semantic_cursor = 0

            for c_obj, k_shots in zip(sc_cues, cue_shot_counts, strict=False):
                w_start = c_obj["win_start"]
                w_end = c_obj["win_end"]
                w_dur = c_obj["win_dur"]
                step = w_dur / k_shots
                cue_shot_entries: List[Dict[str, Any]] = []

                for s_i in range(k_shots):
                    framing_label, beat_desc = semantic_shots[semantic_cursor]
                    eff = semantic_effects[semantic_cursor]
                    semantic_cursor += 1
                    b_idx = b_cursor + 1
                    b_cursor += 1

                    abs_at = w_start if s_i == 0 else round(w_start + s_i * step, 3)
                    next_abs = w_end if s_i == k_shots - 1 else round(w_start + (s_i + 1) * step, 3)
                    hold_dur = round(next_abs - abs_at, 3)
                    rel_at = 0.0 if not sc_beat_images else round(abs_at - sc_start, 3)
                    shot_in_cold_open = ch_num == 1 and abs_at < 15.0

                    shot_id = f"CH{ch_num:02d}_{sc.scene_id}_B{b_idx:02d}"
                    img_filename = f"ch{ch_num}_{sc.scene_id.lower()}_b{b_idx:02d}.jpg"
                    full_prompt = f"{STYLE_PREFIX}. {framing_label}: {beat_desc}."
                    parent_shot = None if b_idx == 1 or framing_label == "White Concept Card" else sc_root_shot_idx

                    shot_entry = {
                        "shot_index": global_shot_idx,
                        "shot_id": shot_id,
                        "chapter": ch_num,
                        "scene_id": sc.scene_id,
                        "beat_index": b_idx,
                        "filename": img_filename,
                        "target_filename": img_filename,
                        "scene_start": sc_start,
                        "scene_end": sc_end,
                        "beat_offset_seconds": rel_at,
                        "abs_at_seconds": abs_at,
                        "duration_seconds": hold_dur,
                        "hold_duration": hold_dur,
                        "pacing_zone": "danger_zone_15s" if shot_in_cold_open else "body_zone",
                        "effect": eff,
                        "framing": framing_label,
                        "prompt": full_prompt,
                        "aspect_ratio": "16:9",
                        "based_on_shot_index": parent_shot,
                    }
                    all_shots.append(shot_entry)
                    ch_shots.append(shot_entry)
                    sc_beat_images.append({
                        "id": shot_id,
                        "src": img_filename,
                        "at": rel_at,
                        "effect": eff,
                    })
                    cue_shot_entries.append({
                        "shot_index": global_shot_idx,
                        "target_filename": img_filename,
                        "abs_at": abs_at,
                        "rel_at": rel_at,
                        "hold": hold_dur,
                        "effect": eff,
                    })
                    global_shot_idx += 1

                all_cue_records.append({
                    "chapter_number": ch_num,
                    "cue_index": c_obj["index"],
                    "scene_id": sc.scene_id,
                    "cue_start": c_obj["start"],
                    "cue_end": c_obj["end"],
                    "window_start": w_start,
                    "window_end": w_end,
                    "window_duration": w_dur,
                    "text": c_obj["text"],
                    "shots": cue_shot_entries,
                })

            remotion_scenes.append({
                "id": sc.scene_id,
                "title": sc.title,
                "start": sc_start,
                "end": sc_end,
                "image": sc_beat_images[0]["src"],
                "images": sc_beat_images,
            })

        tpl_cues = [{"text": c["text"], "start": c["start"], "end": c["end"]} for c in ch_cues]
        tpl_payload = {
            "aspect_ratio": "16:9",
            "primary_language": "vi",
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "duration": ch_duration,
            "outputs": [{"aspect_ratio": "16:9", "language": "vi", "subtitles": False}],
            "scenesByAspect": {"16:9": remotion_scenes},
            "tracks": {
                "vi": {
                    "audioSrc": "narration.wav",
                    "duration": ch_duration,
                    "cues": tpl_cues,
                    "scenesByAspect": {"16:9": remotion_scenes},
                }
            },
        }
        tpl_path = templates_dir / f"ch{ch_num}_props_template.json"
        tpl_path.write_text(json.dumps(tpl_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        chapter_manifests.append({
            "chapter": ch_num,
            "title": ch_meta["title"],
            "time_span": ch_meta["time_span"],
            "duration_seconds": ch_duration,
            "scene_count": len(ch_scenes),
            "shot_count": len(ch_shots),
            "scenes": [
                {
                    "scene_id": s.scene_id,
                    "title": s.title,
                    "duration": s.duration,
                    "narration": strip_pause_tags(s.narration),
                    "raw_narration": s.narration,
                    "source_ids": s.source_ids,
                }
                for s in ch_scenes
            ],
            "shots": ch_shots,
        })

    total_measured_sec = round(sum(c["duration_seconds"] for c in chapter_manifests), 2)
    manifest_json_path = manifest_dir / "manifest_academic_research_8ch.json"
    manifest_payload = {
        "project": "academic-research-paradox-16x9-13m",
        "topic": topic.topic,
        "packaging": topic.packaging.to_dict() if topic.packaging else {},
        "video_aspect_ratio": "16:9",
        "resolution": "1920x1080",
        "fps": 30,
        "measured_duration_seconds": total_measured_sec,
        "total_chapters": len(CHAPTER_METADATA),
        "total_scenes": len(topic.scenes),
        "total_shots": len(all_shots),
        "sources": topic.sources,
        "chapters": chapter_manifests,
        "shots": all_shots,
    }
    manifest_json_path.write_text(json.dumps(manifest_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    phonetic_script_path = manifest_dir / "phonetic_normalized_script_8ch.json"
    phonetic_payload = {"version": "1.0", "project": "academic-research-paradox-16x9-13m", "chapters": []}
    for ch_m in chapter_manifests:
        ch_items = []
        for sc in ch_m["scenes"]:
            for sent_text, pause_sec in split_narration_with_pauses(sc["raw_narration"]):
                ch_items.append({
                    "scene_id": sc["scene_id"],
                    "original_text": sent_text,
                    "normalized_text": normalize_for_tts(sent_text),
                    "pause_after": pause_sec,
                })
        phonetic_payload["chapters"].append({
            "chapter": ch_m["chapter"],
            "title": ch_m["title"],
            "sentences": ch_items,
        })
    phonetic_script_path.write_text(json.dumps(phonetic_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    cue_map_path = manifest_dir / "cue_shot_mapping_8ch.json"
    cue_map_payload = {
        "version": "2.1-dual-zone-cue-anchored",
        "total_chapters": len(CHAPTER_METADATA),
        "total_cues": len(all_cue_records),
        "total_shots": len(all_shots),
        "danger_zone_max_hold_seconds": danger_zone_max_hold,
        "body_zone_max_hold_seconds": body_zone_max_hold,
        "cues": all_cue_records,
    }
    cue_map_path.write_text(json.dumps(cue_map_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "bundle_dir": str(bundle_dir),
        "manifest_json": str(manifest_json_path),
        "phonetic_script": str(phonetic_script_path),
        "cue_map": str(cue_map_path),
        "templates_dir": str(templates_dir),
        "total_shots": len(all_shots),
        "total_cues": len(all_cue_records),
        "total_duration": total_measured_sec,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and validate the 8-chapter / 48-scene Academic Research & Knowledge Decoding 13m blueprint + 3-Tier Spin-offs."
    )
    parser.add_argument("--job-id", default="academic-research-paradox-16x9-13m", help="Job ID under sys/runs/")
    parser.add_argument("--output-dir", default=None, help="Explicit output directory for Schema 3.0 files")
    parser.add_argument("--bundle-dir", default=None, help="Explicit directory for 8-chapter export bundle")
    parser.add_argument("--spinoff-shorts", action="store_true", default=True, help="Generate 3-Tier short_9x16 spin-offs")
    args = parser.parse_args()

    out_dir = Path(args.output_dir) if args.output_dir else (SYS_DIR / "runs" / args.job_id)
    bundle_dir = Path(args.bundle_dir) if args.bundle_dir else (SYS_DIR / "exports" / "academic_research_paradox_bundle")

    topic = create_academic_research_13m_topic(aspect_ratio="16:9", subtitles=False)
    pkg_res = write_production_package(out_dir, topic, system_root=SYS_DIR, include_spinoffs=args.spinoff_shorts)
    bundle_res = build_multi_chapter_bundle(bundle_dir, topic)

    cadence = pkg_res["cadence_report"]
    print(f"[*] Đã đóng gói hồ sơ Schema 3.0 (8 chương / 48 cảnh) tại: {pkg_res['output_dir']}")
    print(f"    - YouTube Title ({len(topic.packaging.youtube_title)} chars): {topic.packaging.youtube_title}")
    print(f"    - Thumbnail Overlay: {topic.packaging.text_overlay}")
    print(f"    - Tổng thời lượng:   {cadence['total_duration']:.1f}s ({cadence['total_duration'] / 60.0:.1f} phút)")
    print(f"    - Tổng số shots:     {bundle_res['total_shots']} shots trên {bundle_res['total_cues']} câu thoại")
    print(f"    - Spin-off Shorts:   {len(pkg_res.get('spinoff_packages', []))} kịch bản short_9x16 độc lập (Phễu 3 Tầng)")
    print(f"    - Trạng thái âm học: [{cadence['status']}] (Warnings: {cadence['warnings_count']}, Max Drift: {cadence['max_drift']:.2f}s)")

    if not pkg_res["valid_contracts"] or cadence["warnings_count"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
