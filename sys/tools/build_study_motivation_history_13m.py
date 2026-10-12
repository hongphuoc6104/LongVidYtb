#!/usr/bin/env python3
"""13-Minute (~780s, Permitted Safe Window: 9–16m / 540s–960s) Research & Production Blueprint Builder:
Giải Mã Cảm Hứng Học Tập Qua Lịch Sử (Study Motivation History Explainer).

Đề tài: "Giải Mã Cảm Hứng Học Tập Qua Lịch Sử: Vì Sao Ta Mất Cảm Hứng Học, Đôi Lúc Lại Rất Hứng Thú,
Là Do Gia Đình, Xã Hội Hay Bản Thân, Và Con Người Qua Các Thời Kỳ Có Bị Như Vậy Không?"

Architectural Features:
  1. Conversational Spoken Fact Protocol: All 16 academic facts in `brief.json` (`sources[].facts`) are concise,
     natural spoken Vietnamese (15–18 syllables, strictly <= 20) passing the Coffee Table Test and embedded
     100% verbatim in `content.json` narration (`claim['quote'] == claim['fact']`).
  2. Natural Spoken Cadence & Calibrated Breath Pauses: All 48 scenes authored with explicit `[pause:800ms]` breath tags,
     achieving 100% PASS (0 warnings, |drift| <= 0.25s) on `ScriptCadenceChecker`.
  3. Editorial Graphic Visual Beats (`study_motivation_en_visuals.py`): Editorial ink compositions on warm cream paper,
     anonymous stick-figure cast invariant, Rule-of-Thirds sticker staging, zero text in images.
  4. Semantic Camera Motion Director: Semantic camera effects (`zoom_out`, `zoom_in`, `punch_in`, `pan_right`, `pan_left`)
     with zero consecutive duplicate motions inside any scene.
  5. Schema 3.0 Compliance: Produces fully validated `brief.json` and `content.json`.

Outputs:
  1. Job package in `sys/runs/study-motivation-16x9-13m/`:
     - `brief.json`, `content.json`, `script.json`, `cadence_report.json`
  2. Multi-chapter bundle in `sys/exports/study_motivation_bundle/`:
     - `manifest/manifest_study_motivation_8ch.json`
     - `manifest/phonetic_normalized_script_8ch.json`
     - `manifest/cue_shot_mapping_8ch.json`
     - `manifest/manifest_study_motivation_8ch.md`
     - `templates/ch{1..8}_props_template.json`
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import wave
from pathlib import Path
from typing import Any, Dict, List

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
    ResearchedScene,
    ResearchedSticker,
    ResearchedTopic,
    write_production_package,
)
from study_motivation_en_visuals import STYLE_PREFIX, get_scene_beats_v2  # noqa: E402
from vn_text_normalizer import normalize_for_tts  # noqa: E402

PAUSE_TAG_RE = re.compile(r"\[pause:\s*(\d+(?:\.\d+)?)\s*(ms|s)?\s*\]", re.IGNORECASE)


def strip_pause_tags(text: str) -> str:
    """Remove [pause:...] markers and normalize whitespace for TTS and subtitle cues."""
    cleaned = PAUSE_TAG_RE.sub(" ", text)
    return re.sub(r"\s+", " ", cleaned).strip()


def split_narration_with_pauses(narration: str) -> List[tuple[str, float]]:
    """Split a scene narration into (clean_sentence, explicit_pause_after_sec) tuples."""
    raw = narration.strip()
    pattern = re.compile(
        r"([^.!?…]+[.!?…]+)\s*(?:\[pause:\s*(\d+(?:\.\d+)?)\s*(ms|s)?\s*\])?",
        re.IGNORECASE,
    )
    results: List[tuple[str, float]] = []
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
        "title": "Cơn ác mộng bàn học & Nghịch lý cảm hứng trồi sụt",
        "time_span": "0:00 - 1:30",
        "duration": 90.0,
        "scene_ids": ["SC01", "SC02", "SC03", "SC04", "SC05", "SC06"],
        "requirement_id": "R01",
    },
    {
        "chapter": 2,
        "title": "Bộ não 300.000 năm & Hệ thống SEEKING dopamine",
        "time_span": "1:30 - 3:15",
        "duration": 105.0,
        "scene_ids": ["SC07", "SC08", "SC09", "SC10", "SC11", "SC12"],
        "requirement_id": "R02",
    },
    {
        "chapter": 3,
        "title": "Thời Tiền sử: Bản năng học qua trò chơi tự do",
        "time_span": "3:15 - 5:00",
        "duration": 105.0,
        "scene_ids": ["SC13", "SC14", "SC15", "SC16", "SC17", "SC18"],
        "requirement_id": "R03",
    },
    {
        "chapter": 4,
        "title": "Thời Cổ đại: Đòn roi trường đất sét Sumer Edubba",
        "time_span": "5:00 - 6:45",
        "duration": 105.0,
        "scene_ids": ["SC19", "SC20", "SC21", "SC22", "SC23", "SC24"],
        "requirement_id": "R04",
    },
    {
        "chapter": 5,
        "title": "Thời Phong kiến: Gánh nặng dòng tộc & Bẫy khoa cử",
        "time_span": "6:45 - 8:30",
        "duration": 105.0,
        "scene_ids": ["SC25", "SC26", "SC27", "SC28", "SC29", "SC30"],
        "requirement_id": "R05",
    },
    {
        "chapter": 6,
        "title": "Thời Công nghiệp: Mô hình trường học nhà máy Phổ",
        "time_span": "8:30 - 10:15",
        "duration": 105.0,
        "scene_ids": ["SC31", "SC32", "SC33", "SC34", "SC35", "SC36"],
        "requirement_id": "R06",
    },
    {
        "chapter": 7,
        "title": "Kỷ nguyên Số & Chiếc bẫy ba phía (Bản thân - Gia đình - Xã hội)",
        "time_span": "10:15 - 11:45",
        "duration": 90.0,
        "scene_ids": ["SC37", "SC38", "SC39", "SC40", "SC41", "SC42"],
        "requirement_id": "R07",
    },
    {
        "chapter": 8,
        "title": "Đánh thức người tiền sử: 3 chìa khóa để yêu lại việc học",
        "time_span": "11:45 - 13:00",
        "duration": 75.0,
        "scene_ids": ["SC43", "SC44", "SC45", "SC46", "SC47", "SC48"],
        "requirement_id": "R08",
    },
]

# Canonical 285-shot distribution across 48 scenes
CANONICAL_SCENE_SHOT_COUNTS: Dict[str, int] = {
    "SC01": 6, "SC02": 5, "SC03": 6, "SC04": 6, "SC05": 5, "SC06": 6,
    "SC07": 7, "SC08": 7, "SC09": 7, "SC10": 7, "SC11": 6, "SC12": 6,
    "SC13": 6, "SC14": 7, "SC15": 5, "SC16": 6, "SC17": 6, "SC18": 7,
    "SC19": 6, "SC20": 6, "SC21": 6, "SC22": 6, "SC23": 7, "SC24": 6,
    "SC25": 6, "SC26": 6, "SC27": 6, "SC28": 6, "SC29": 6, "SC30": 5,
    "SC31": 6, "SC32": 6, "SC33": 6, "SC34": 6, "SC35": 6, "SC36": 6,
    "SC37": 6, "SC38": 6, "SC39": 6, "SC40": 6, "SC41": 6, "SC42": 6,
    "SC43": 5, "SC44": 5, "SC45": 5, "SC46": 5, "SC47": 5, "SC48": 5,
}


def get_academic_sources() -> List[Dict[str, Any]]:
    """Return the 8 academic and historical sources with Conversational Spoken Facts (<= 20 syllables each)."""
    return [
        {
            "id": "SRC01",
            "title": "Naming the Mind: How Psychology Found Its Language",
            "reference": "Kurt Danziger (1997). Naming the Mind: How Psychology Found Its Language. SAGE Publications. ISBN: 978-0803977631",
            "facts": [
                "Trước cuối thế kỷ mười chín, khái niệm động lực học tập hoàn toàn chưa từng tồn tại.",
                "Khái niệm động lực chỉ bùng nổ khi trường học công nghiệp ép học sinh ngồi bất động.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Affective Neuroscience: The Foundations of Human and Animal Emotions & The Role of Dopamine",
            "reference": "Jaak Panksepp (1998). Affective Neuroscience: The Foundations of Human and Animal Emotions. Oxford University Press. ISBN: 978-0195096736; Kent C. Berridge & Terry E. Robinson (1998). Brain Research Reviews, 28(3), 309-369",
            "facts": [
                "Bộ não không hề lười biếng mà được lập trình để tò mò khám phá.",
                "Dopamine không phải chất hưởng thụ, mà là ngọn lửa thôi thúc tìm kiếm hiểu biết.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Free to Learn: Why Unleashing the Instinct to Play Will Make Our Children Happier",
            "reference": "Peter Gray (2013). Free to Learn: Why Unleashing the Instinct to Play Will Make Our Children Happier, More Self-Reliant, and Better Students for Life. Basic Books. ISBN: 978-0465025992",
            "facts": [
                "Trẻ em tiền sử học mọi kỹ năng sinh tồn thông qua trò chơi tự do.",
                "Bộ lạc săn hái không bao giờ bắt ép hay chấm điểm con trẻ học tập.",
            ],
        },
        {
            "id": "SRC04",
            "title": "History Begins at Sumer: Thirty-Nine Firsts in Recorded History & Sumerian Tablet House",
            "reference": "Samuel Noah Kramer (1956). History Begins at Sumer: Thirty-Nine Firsts in Recorded History. University of Pennsylvania Press. ISBN: 978-0812212761",
            "facts": [
                "Bốn nghìn năm trước ở Sumer, học sinh bị đánh đòn nếu viết sai chữ nêm.",
                "Trường học đất sét cổ đại ra đời để phục vụ ghi chép thuế khóa cho đền thờ.",
            ],
        },
        {
            "id": "SRC05",
            "title": "A Cultural History of Civil Examinations in Late Imperial China",
            "reference": "Benjamin A. Elman (2000). A Cultural History of Civil Examinations in Late Imperial China. University of California Press. ISBN: 978-0520215092",
            "facts": [
                "Thời phong kiến, việc học bị biến thành công cụ tiến thân cho cả dòng tộc.",
                "Học sinh xưa phải học vẹt hàng vạn câu kinh điển để đi thi làm quan.",
            ],
        },
        {
            "id": "SRC06",
            "title": "Dumbing Us Down: The Hidden Curriculum of Compulsory Schooling",
            "reference": "John Taylor Gatto (1992). Dumbing Us Down: The Hidden Curriculum of Compulsory Schooling. New Society Publishers. ISBN: 978-0865714489",
            "facts": [
                "Mô hình trường học chia theo độ tuổi được sao chép từ nhà máy quân sự Phổ.",
                "Tiếng chuông trường học được thiết kế để rèn thói quen tuân lệnh dây chuyền.",
            ],
        },
        {
            "id": "SRC07",
            "title": "Self-Determination Theory and the Facilitation of Intrinsic Motivation",
            "reference": "Edward L. Deci & Richard M. Ryan (2000). Self-Determination Theory and the Facilitation of Intrinsic Motivation, Social Development, and Well-Being. American Psychologist, 55(1), 68-78",
            "facts": [
                "Cảm hứng học tập sụp đổ khi con người mất quyền tự chủ và sự gắn kết.",
                "Kỳ vọng gia đình và áp lực điểm số bóp nghẹt động lực nội tại của bạn.",
            ],
        },
        {
            "id": "SRC08",
            "title": "A Mind for Numbers: How to Excel at Math and Science & Mindset",
            "reference": "Barbara Oakley (2014). A Mind for Numbers. TarcherPerigee. ISBN: 978-0399165245; Carol S. Dweck (2006). Mindset. Random House. ISBN: 978-0345472328",
            "facts": [
                "Chỉ cần chia nhỏ việc học thành từng chặng ngắn, não bộ sẽ tự vào guồng.",
                "Bộ não sẽ yêu việc học khi ta được tự do thử sai và làm chủ tiến trình.",
            ],
        },
    ]


def get_required_points() -> List[Dict[str, str]]:
    """Return the 8 required points corresponding to the 8 narrative chapters."""
    return [
        {
            "id": "R01",
            "text": "Cơn ác mộng bàn học, nghịch lý mất cảm hứng học và sự ra đời muộn màng của thuật ngữ động lực học tập",
        },
        {
            "id": "R02",
            "text": "Bộ não 300.000 năm với hệ thống dopamine thôi thúc tò mò tìm kiếm điều mới mẻ",
        },
        {
            "id": "R03",
            "text": "Thời tiền sử học tập tự nhiên qua trò chơi tự do không có bài tập hay ép buộc",
        },
        {
            "id": "R04",
            "text": "Trường học đất sét Sumer Edubba thời cổ đại dùng đòn roi để ép học sinh ghi chép thuế",
        },
        {
            "id": "R05",
            "text": "Thời phong kiến biến học tập thành gánh nặng dòng tộc và bẫy khoa cử thi đỗ làm quan",
        },
        {
            "id": "R06",
            "text": "Cách mạng công nghiệp áp dụng mô hình trường học nhà máy Phổ rèn luyện tính phục tùng",
        },
        {
            "id": "R07",
            "text": "Kỷ nguyên số bóp nghẹt động lực nội tại bởi chiếc bẫy ba phía bản thân, gia đình và xã hội",
        },
        {
            "id": "R08",
            "text": "Đánh thức người tiền sử bằng ba chìa khóa tự chủ, mục tiêu ngắn hạn và kết nối để yêu lại việc học",
        },
    ]


RAW_SCENES_DATA: List[Dict[str, Any]] = [
    {
        "scene_id": "SC01",
        "chapter": 1,
        "duration": 15.0,
        "title": "Cơn ác mộng trước bàn học khuya",
        "purpose": "Nghịch lý mất cảm hứng học tập trước bàn học và sự ra đời muộn màng của thuật ngữ động lực",
        "narration": "Sức nặng vô hình đang đè trĩu lên đôi vai bạn. [pause:800ms] Cuốn sách mở rộng nhưng tâm trí hoàn toàn đóng chặt. Từng dòng chữ nhảy múa hỗn loạn trên trang giấy trắng. Bạn rất muốn tập trung học tập thật tử tế. Nhưng đầu ngón tay không sao điều khiển nổi cây bút.",
        "requirements": ["R01"],
        "source_ids": [],
        "action": "Nhân vật người que ngồi bất động trước cuốn sách mở sẵn bên cạnh chiếc bút bi lăn lóc",
        "setting": "Góc bàn học hiện đại đêm muộn với ánh đèn bàn vàng ấm và khoảng trống tĩnh lặng",
        "camera": "Toàn cảnh góc bàn học đêm khuya rồi đẩy nhẹ vào cuốn sách mở",
        "bg_description": "Bàn học gỗ hiện đại đêm muộn với cuốn sách giáo khoa mở sẵn và chiếc bút bi mực nằm ngang trên trang giấy trắng, nét vẽ mực đen tối giản trên nền giấy kem sáng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày ngồi chùng vai nhìn trang sách với ánh mắt mệt mỏi bế tắc",
        "anchor_quote": "Sức nặng vô hình đang",
        "fx": "pop",
        "x": 0.36,
        "y": 0.62,
        "w": 0.38,
        "claim": None,
    },
    {
        "scene_id": "SC02",
        "chapter": 1,
        "duration": 15.0,
        "title": "Ảo tưởng về ngọn lửa cảm hứng trước khi mở sách",
        "purpose": "Phá vỡ ảo tưởng rằng phải có cảm hứng rực cháy mới mở sách ra học được",
        "narration": "Sự bất lực này nhanh chóng biến thành nỗi tự trách nặng nề. [pause:800ms] Bạn tin rằng bản thân lười biếng và thiếu nghị lực trầm trọng. Thực chất thể xác của bạn hoàn toàn khỏe mạnh bình thường. Não bộ không hề cần cảm hứng bùng nổ mới chịu mở sách ra học.",
        "requirements": [],
        "source_ids": ["SRC02"],
        "action": "Nhân vật người que dừng lướt điện thoại khi nét cọ đỏ gạch bỏ định kiến tự trách bản thân thiếu ý chí",
        "setting": "Không gian phòng học tối giản với kệ sách và giá để tài liệu",
        "camera": "Chuyển động ngang theo tay lướt rồi nhấn cận cảnh dứt khoát",
        "bg_description": "Kệ sách gỗ với những tập tài liệu học tập và tấm bảng trắng có nét cọ mực đỏ gạch ngang đám mây tự trách trên nền giấy kem thoáng đãng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày đứng thẳng điềm tĩnh đưa tay giải thích với ánh mắt sáng rõ",
        "anchor_quote": "Sự bất lực này nhanh",
        "fx": "slide_left",
        "x": 0.64,
        "y": 0.6,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC03",
        "chapter": 1,
        "duration": 15.0,
        "title": "Bí mật lịch sử của từ động lực học tập",
        "purpose": "Chứng minh thuật ngữ động lực học tập chưa từng tồn tại trước cuối thế kỷ 19",
        "narration": "Hãy nhìn sâu vào dòng chảy lịch sử ngôn ngữ. Trước cuối thế kỷ mười chín, khái niệm động lực học tập hoàn toàn chưa từng tồn tại. [pause:800ms] Từ điển cổ xưa không hề ghi nhận thuật ngữ này. Tri thức từng được con người đón nhận một cách rất tự nhiên và thoải mái.",
        "requirements": [],
        "source_ids": ["SRC01"],
        "action": "Nhà nghiên cứu người que soi kính lúp vào cuốn từ điển cổ và đường biểu đồ xuất hiện muộn của thuật ngữ",
        "setting": "Thư viện lưu trữ cổ kính với những cuốn bách khoa toàn thư bọc da",
        "camera": "Toàn cảnh thư viện mở rộng kết hợp cận cảnh trang từ điển cổ",
        "bg_description": "Khung cảnh thư viện cổ với bục đọc sách bằng gỗ sồi và biểu đồ nét mực đen nằm ngang suốt nhiều thế kỷ trên nền giấy sáng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày cầm kính lúp soi vào trang sách cổ với vẻ mặt ngạc nhiên",
        "anchor_quote": "Hãy nhìn sâu vào dòng",
        "fx": "pop",
        "x": 0.35,
        "y": 0.63,
        "w": 0.36,
        "claim": (
            "Trước cuối thế kỷ mười chín, khái niệm động lực học tập hoàn toàn chưa từng tồn tại.",
            "SRC01",
            "Trước cuối thế kỷ mười chín, khái niệm động lực học tập hoàn toàn chưa từng tồn tại.",
        ),
    },
    {
        "scene_id": "SC04",
        "chapter": 1,
        "duration": 15.0,
        "title": "Tổ tiên học hỏi và sáng tạo không cần sách truyền lửa",
        "purpose": "Khám phá cách người xưa học nghề và truyền thụ tri thức tự nhiên",
        "narration": "Suốt hàng nghìn năm, nhân loại dựng xây triết học, nghệ thuật và thiên văn học rực rỡ. [pause:800ms] Các bậc hiền triết phương xưa say sưa khám phá bí ẩn vũ trụ ngày đêm. Họ miệt mài sáng tạo mà không cần bất kỳ cuốn cẩm nang kích thích tinh thần nào nâng đỡ.",
        "requirements": [],
        "source_ids": ["SRC01"],
        "action": "Toàn cảnh ba phát minh lớn thời cổ gồm ngọn lửa trại, phiến đá khắc chữ và bánh xe gỗ lăn trên đường",
        "setting": "Bức tranh toàn cảnh lịch sử nối liền bếp lửa hang động, xưởng gốm và công trình cổ đại",
        "camera": "Toàn cảnh quét ngang mượt mà qua các kỳ tích học hỏi của tổ tiên",
        "bg_description": "Bức tranh biên tập nối liền bếp lửa nguyên thủy, phiến đá cổ khắc hình và chiếc bánh xe gỗ mộc mạc bằng nét mực đen thanh thoát, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày đứng bên phiến đá khắc họa với dáng vẻ tự hào",
        "anchor_quote": "Suốt hàng nghìn năm, nhân",
        "fx": "bounce",
        "x": 0.65,
        "y": 0.61,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC05",
        "chapter": 1,
        "duration": 15.0,
        "title": "Bộ não người săn hái bị giam cầm bên bàn học",
        "purpose": "Chỉ ra mâu thuẫn giữa bản năng học hỏi qua vận động và chiếc ghế ngồi học bất động",
        "narration": "Nguồn cơn sâu xa của sự mệt mỏi nằm ở không gian sống gò bó. [pause:800ms] Một cơ thể sống tràn đầy năng lượng tươi trẻ bị nhốt vào bốn bức tường chật hẹp. Con người bị ép ngồi yên hàng giờ để nghe giảng những lý thuyết trừu tượng xa vời thực tế.",
        "requirements": [],
        "source_ids": ["SRC01"],
        "action": "Người thợ săn tiền sử với bộ lông thú đơn sơ đứng ngơ ngác giữa lớp học hiện đại với dãy bàn thẳng tắp",
        "setting": "Sự đối lập không gian giữa phòng học đóng kín và thiên nhiên rộng mở ngoài cửa sổ",
        "camera": "Trung cảnh đẩy nhẹ vào sự bối rối của người thợ săn giữa lớp học",
        "bg_description": "Dãy bàn ghế học sinh hiện đại bằng gỗ thẳng tắp đối lập với tán cây xanh mát và ánh nắng tự nhiên ngoài khung cửa sổ lớn, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày trong trang phục săn hái ngơ ngác nhìn quanh lớp học",
        "anchor_quote": "Nguồn cơn sâu xa của",
        "fx": "pop_wobble",
        "x": 0.35,
        "y": 0.63,
        "w": 0.37,
        "claim": None,
    },
    {
        "scene_id": "SC06",
        "chapter": 1,
        "duration": 15.0,
        "title": "Hành trình giải mã cảm hứng học tập qua các thời kỳ",
        "purpose": "Mở ra chuyến hành trình khám phá 4 thời đại lớn của việc học",
        "narration": "Sự cưỡng ép này bắt nguồn từ một cuộc chuyển mình lớn trong lịch sử. [pause:800ms] Khái niệm động lực chỉ bùng nổ khi trường học công nghiệp ép học sinh ngồi bất động. Muốn khơi lại ngọn lửa say mê, ta cần thấu hiểu cội nguồn sinh học tự nhiên của sự tò mò.",
        "requirements": [],
        "source_ids": ["SRC01"],
        "action": "Con đường đá uốn lượn nối liền bốn thời kỳ học tập từ lửa trại thảo nguyên, trường đất sét Sumer, trường thi khoa cử đến lớp học ngày nay",
        "setting": "Trục đường lịch sử trải dài trên nền giấy kem ấm áp qua bốn cột mốc văn minh",
        "camera": "Toàn cảnh mở rộng dẫn dắt người xem bước vào hành trình lịch sử học tập",
        "bg_description": "Con đường lát đá uốn lượn trên nền giấy kem nối liền bốn biểu tượng học tập gồm đống lửa thảo nguyên, phiến đất sét cổ, cuộn sách thi cử và chiếc bàn học hiện đại, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày sải bước bên cột mốc đá cổ xưa với cử chỉ mời gọi",
        "anchor_quote": "Sự cưỡng ép này bắt",
        "fx": "slide_left",
        "x": 0.63,
        "y": 0.62,
        "w": 0.36,
        "claim": (
            "Khái niệm động lực chỉ bùng nổ khi trường học công nghiệp ép học sinh ngồi bất động.",
            "SRC01",
            "Khái niệm động lực chỉ bùng nổ khi trường học công nghiệp ép học sinh ngồi bất động.",
        ),
    },
    {
        "scene_id": "SC07",
        "chapter": 2,
        "duration": 17.5,
        "title": "Bộ não ba trăm nghìn năm và cỗ máy sinh tồn",
        "purpose": "Bộ não 300.000 năm với hệ thống dopamine thôi thúc tò mò tìm kiếm điều mới mẻ",
        "narration": "Vùng vỏ não trước trán của con người quản lý nguồn năng lượng tập trung có hạn định. [pause:800ms] Việc liên tục giải mã hàng loạt ký hiệu và công thức trừu tượng tiêu tốn lượng lớn đường glucose trong máu. Khi nguồn năng lượng này suy giảm, hệ thần kinh phát tín hiệu đình công để ép cơ thể bạn phải nghỉ ngơi.",
        "requirements": ["R02"],
        "source_ids": ["SRC02"],
        "action": "Thanh thời gian tiến hóa ba trăm nghìn năm với 99% không gian thảo nguyên và vạch mỏng của trường học",
        "setting": "Không gian biên tập tối giản với thanh tỷ lệ tiến hóa và kính lúp soi vạch nhỏ cuối cùng",
        "camera": "Toàn cảnh quét dọc thanh tỷ lệ rồi thu phóng vào lát cắt trường học nhỏ bé",
        "bg_description": "Thanh biểu đồ ngang dài trên nền giấy kem với chín mươi chín phần trăm tô màu vàng đất thảo nguyên và một vạch xanh lam cực mảnh ở tận cùng bên phải dưới kính lúp, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày cúi người cầm kính lúp quan sát vạch thời gian",
        "anchor_quote": "Vùng vỏ não trước trán",
        "fx": "pop",
        "x": 0.36,
        "y": 0.6,
        "w": 0.37,
        "claim": None,
    },
    {
        "scene_id": "SC08",
        "chapter": 2,
        "duration": 17.5,
        "title": "Hệ thống SEEKING: Bản năng tò mò nguyên bản",
        "purpose": "Trình bày nghiên cứu thần kinh học về hệ thống tìm kiếm tri thức của bộ não",
        "narration": "Các công trình nghiên cứu khoa học thần kinh hiện đại ngày nay khẳng định một chân lý rất bất ngờ. [pause:800ms] Bộ não không hề lười biếng mà được lập trình để tò mò khám phá. Mạch dẫn truyền thần kinh tự nhiên luôn thôi thúc con người không ngừng tìm kiếm lời giải đáp thỏa đáng trước những ẩn số mới lạ xung quanh.",
        "requirements": [],
        "source_ids": ["SRC02"],
        "action": "Chiếc la bàn đồng chỉ hướng trên tấm bản đồ địa hình dẫn lên đỉnh đồi khám phá điều mới lạ",
        "setting": "Bản đồ thực địa với chiếc la bàn đồng và con đường mòn dẫn lên đỉnh đồi ngắm cảnh",
        "camera": "Cận cảnh kim la bàn xoay mạnh rồi lia máy theo hướng đi khám phá",
        "bg_description": "Chiếc la bàn bằng đồng đặt trên tấm bản đồ giấy kem với mũi kim chỉ thẳng về phía rặng đồi xanh ngát dưới ánh nắng sớm, nét mực đen thanh mảnh, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày sải bước hào hứng hướng về phía ngọn đồi xa",
        "anchor_quote": "Các công trình nghiên cứu",
        "fx": "slide_left",
        "x": 0.64,
        "y": 0.62,
        "w": 0.38,
        "claim": (
            "Bộ não không hề lười biếng mà được lập trình để tò mò khám phá.",
            "SRC02",
            "Bộ não không hề lười biếng mà được lập trình để tò mò khám phá.",
        ),
    },
    {
        "scene_id": "SC09",
        "chapter": 2,
        "duration": 17.5,
        "title": "Dopamine là ngọn lửa săn lùng tri thức",
        "purpose": "Giải mã bản chất của dopamine trong học tập là động lực khám phá điều mới",
        "narration": "Chất dẫn truyền dopamine giữ vai trò đặc biệt then chốt ở đây. Dopamine không phải chất hưởng thụ, mà là ngọn lửa thôi thúc tìm kiếm hiểu biết. [pause:800ms] Nó chỉ bùng phát khi tâm trí nhìn thấy tín hiệu của một phần thưởng cụ thể ngay trước mắt. Mất phương hướng hành động rõ ràng, ngọn lửa tò mò ấy sẽ lụi tàn.",
        "requirements": [],
        "source_ids": ["SRC02"],
        "action": "Đường sáng nối liền từ ánh mắt tò mò tới dấu vết con mồi và chùm quả chín trên cành",
        "setting": "Góc rừng sáng thoáng với chùm quả chín và dấu vết chân thú in trên đất ẩm",
        "camera": "Cận cảnh ánh mắt tập trung rồi lia dọc theo đường sáng tới mục tiêu hữu hình",
        "bg_description": "Khung cảnh thiên nhiên sáng thoáng với đường kẻ chấm vàng ấm nối thẳng tới chùm quả chín mọng trên cành cây cổ thụ, nét vẽ mực đen biên tập tinh tế, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày đưa tay che nắng nhìn thẳng về phía mục tiêu trước mắt",
        "anchor_quote": "Chất dẫn truyền dopamine giữ",
        "fx": "pop",
        "x": 0.34,
        "y": 0.62,
        "w": 0.36,
        "claim": (
            "Dopamine không phải chất hưởng thụ, mà là ngọn lửa thôi thúc tìm kiếm hiểu biết.",
            "SRC02",
            "Dopamine không phải chất hưởng thụ, mà là ngọn lửa thôi thúc tìm kiếm hiểu biết.",
        ),
    },
    {
        "scene_id": "SC10",
        "chapter": 2,
        "duration": 17.5,
        "title": "Bàn cân năng lượng sinh tồn của trí óc",
        "purpose": "Giải thích vì sao não bộ ngắt kết nối trước những bài học trừu tượng xa vời",
        "narration": "Tâm trí luôn vận hành theo bài toán cân đong năng lượng sinh tồn vô cùng chuẩn xác. [pause:800ms] Khi phải nhồi nhét những định lý trừu tượng mà không thấy ứng dụng thực tiễn, não bộ đánh giá đây là việc vô bổ. Nó sẽ chủ động dập tắt sự tập trung để bảo toàn dưỡng chất quý giá cho cơ thể bạn.",
        "requirements": [],
        "source_ids": ["SRC02"],
        "action": "Chiếc cân gỗ trên phiến đá nghiêng hẳn về phía nỗ lực nặng nề so với phần thưởng vô hình nhỏ xíu",
        "setting": "Phiến đá phẳng bên bờ suối với chiếc cân cán gỗ mộc mạc",
        "camera": "Trung cảnh cân đối ghi lại chuyển động nghiêng của chiếc cân sinh tồn",
        "bg_description": "Chiếc cân gỗ mộc mạc đặt trên phiến đá phẳng: một bên là khối đá nặng trĩu sức lực, bên kia chỉ là đám mây công thức mờ ảo trên nền giấy kem, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày đứng suy xét chỉ tay vào chiếc cân gỗ",
        "anchor_quote": "Tâm trí luôn vận hành",
        "fx": "bounce",
        "x": 0.65,
        "y": 0.62,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC11",
        "chapter": 2,
        "duration": 17.5,
        "title": "Chán học là cơ chế phanh bảo vệ tự nhiên",
        "purpose": "Làm rõ cảm giác chán nản là phản xạ phòng vệ sinh học chứ không phải suy thoái đạo đức",
        "narration": "Cảm giác uể oải trước trang vở thực chất là một phản xạ phòng vệ tự nhiên. [pause:800ms] Bạn không hề yếu đuối về ý chí hay sa sút về năng lực cá nhân. Bộ não đang kéo phanh hãm lại vì chưa tìm thấy ý nghĩa thiết thực của bài học. Hiểu được điều này, bạn sẽ trút bỏ được sự dằn vặt bấy lâu.",
        "requirements": [],
        "source_ids": ["SRC02"],
        "action": "Chiếc phanh gỗ xe ngựa tự động hạ xuống giữ chặt bánh xe trước đoạn đường mù sương",
        "setting": "Đoạn đường mòn với chiếc xe gỗ dừng lại an toàn trước ngã rẽ sương mù",
        "camera": "Cận cảnh chiếc phanh gỗ hãm lại rồi mở rộng ra vẻ mặt thấu hiểu của nhân vật",
        "bg_description": "Chiếc xe kéo bằng gỗ mộc với cần phanh gỗ hạ xuống giữ chặt vành bánh xe trên nền đường đất giấy sáng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày đứng bên chiếc xe với nụ cười nhẹ nhõm thấu hiểu",
        "anchor_quote": "Cảm giác uể oải trước",
        "fx": "pop_wobble",
        "x": 0.36,
        "y": 0.61,
        "w": 0.37,
        "claim": None,
    },
    {
        "scene_id": "SC12",
        "chapter": 2,
        "duration": 17.5,
        "title": "Bước ra thảo nguyên của người tiền sử",
        "purpose": "Chuyển tiếp bối cảnh sang thời kỳ tiền sử để quan sát việc học diễn ra tự nhiên ra sao",
        "narration": "Để chứng kiến cách thức tâm trí tiếp thu tri thức say mê khi không bị giam hãm trong phòng học kín, chúng ta cần tìm về buổi bình minh của nhân loại. [pause:800ms] Đó là giai đoạn mà toàn bộ việc học hành hòa quyện trọn vẹn vào nhịp sống tự do giữa không gian đại ngàn khoáng đạt ngập tràn ánh nắng ấm.",
        "requirements": [],
        "source_ids": ["SRC02"],
        "action": "Bức tường phòng học mở bung sang hai bên như cánh cửa giấy hé lộ thảo nguyên ngập nắng",
        "setting": "Không gian chuyển tiếp nghệ thuật từ căn phòng hiện đại ra thảo nguyên bao la",
        "camera": "Toàn cảnh kéo lùi rộng mở ra chân trời thảo nguyên rực nắng",
        "bg_description": "Hai bức tường phòng học gấp mở sang hai bên như cánh cửa bình phong để lộ thảo nguyên xanh ngát với cây keo cổ thụ và bình minh ấm áp, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày bước qua ngưỡng cửa hướng ra thảo nguyên rộng lớn",
        "anchor_quote": "Để chứng kiến cách thức",
        "fx": "slide_left",
        "x": 0.62,
        "y": 0.63,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC13",
        "chapter": 3,
        "duration": 17.5,
        "title": "Trường học không tường của trẻ em tiền sử",
        "purpose": "Thời tiền sử học tập tự nhiên qua trò chơi tự do không có bài tập hay ép buộc",
        "narration": "Thời tiền sử không có giảng đường, bảng đen hay sách giáo khoa. [pause:800ms] Trẻ nhỏ thức giấc cùng ánh nắng sớm và tự do chạy nhảy khắp núi rừng hoang sơ. Chúng không phải đối mặt với giáo án hay bài kiểm tra điểm số nào. Ấy vậy mà ngày nào chúng cũng thuần thục thêm vô số kỹ năng sống phức tạp.",
        "requirements": ["R03"],
        "source_ids": ["SRC03"],
        "action": "Những đứa trẻ tiền sử chạy nhảy nô đùa bên dòng suối trong vắt và quan sát người lớn đan giỏ",
        "setting": "Khu trại săn hái nguyên thủy buổi sáng sớm với những túp lều da thú đơn sơ",
        "camera": "Toàn cảnh rộng mở ra thiên nhiên khoáng đạt của khu trại tiền sử",
        "bg_description": "Khu trại nguyên thủy bình yên bên bờ suối với những túp lều da thú, bếp lửa tro tàn và hàng cây rợp bóng mát trên nền giấy kem, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày nhỏ nhắn tung tăng chạy nhảy với nụ cười hồn nhiên",
        "anchor_quote": "Thời tiền sử không có",
        "fx": "pop",
        "x": 0.35,
        "y": 0.62,
        "w": 0.37,
        "claim": None,
    },
    {
        "scene_id": "SC14",
        "chapter": 3,
        "duration": 17.5,
        "title": "Học qua trò chơi tự do: Bí mật của bản năng",
        "purpose": "Phân tích phát hiện nhân chủng học về việc học qua trò chơi tự do",
        "narration": "Giới nhân chủng học hiện đại nhận thấy điều kỳ diệu về cách học thuở xưa. [pause:800ms] Trẻ em tiền sử học mọi kỹ năng sinh tồn thông qua trò chơi tự do. Chúng tập bắn cung, rình nấp sau bụi cây và cùng nhau dựng lều lá. Việc học và vui chơi hòa làm một, luôn tràn ngập tiếng cười sảng khoái mỗi ngày.",
        "requirements": [],
        "source_ids": ["SRC03"],
        "action": "Trẻ em người que tập bắn chiếc cung gỗ nhỏ vào bia rơm và cùng nhau lợp chiếc lều lá nhỏ",
        "setting": "Bãi cỏ xanh rì bìa rừng với chiếc bia cỏ khô và những cành cây dựng lều",
        "camera": "Toàn cảnh mở rộng bãi cỏ rồi đẩy cận cảnh vào chiếc cung gỗ nhỏ",
        "bg_description": "Bãi cỏ xanh ngập nắng với chiếc bia cỏ khô đan tròn và khung lều nhỏ bằng cành liễu uốn cong trên nền giấy sáng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày giương chiếc cung gỗ đồ chơi với ánh mắt thích thú",
        "anchor_quote": "Giới nhân chủng học hiện",
        "fx": "pop_wobble",
        "x": 0.62,
        "y": 0.58,
        "w": 0.38,
        "claim": (
            "Trẻ em tiền sử học mọi kỹ năng sinh tồn thông qua trò chơi tự do.",
            "SRC03",
            "Trẻ em tiền sử học mọi kỹ năng sinh tồn thông qua trò chơi tự do.",
        ),
    },
    {
        "scene_id": "SC15",
        "chapter": 3,
        "duration": 17.5,
        "title": "Không điểm số, không la mắng, không so sánh",
        "purpose": "Chứng minh người tiền sử tôn trọng tính tự chủ và không dùng hình phạt học tập",
        "narration": "Thế hệ đi trước trao cho con trẻ quyền tự chủ trọn vẹn trong mọi hoạt động. [pause:800ms] Bộ lạc săn hái không bao giờ bắt ép hay chấm điểm con trẻ học tập. Người lớn chỉ làm mẫu khi đan giỏ hay ghè đẽo đá, và con trẻ chủ động quan sát rồi làm theo bằng tất cả niềm say mê thuần khiết.",
        "requirements": [],
        "source_ids": ["SRC03"],
        "action": "Người thợ tiền sử đục chiếc rìu đá khéo léo, đứa trẻ ngồi bên cạnh quan sát rồi tự tay gọt đẽo thử",
        "setting": "Gốc cây râm mát nơi người lớn chế tác công cụ lao động hàng ngày",
        "camera": "Trung cảnh ấm áp ghi lại sự kiên nhẫn làm mẫu của người lớn",
        "bg_description": "Khung cảnh bóng mát dưới tán cây lớn với những phiến đá mài rìu và những thanh gỗ gọt dở nằm gọn gàng trên nền giấy kem, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày chăm chú quan sát cử động tay của người đi trước",
        "anchor_quote": "Thế hệ đi trước trao",
        "fx": "pop",
        "x": 0.35,
        "y": 0.62,
        "w": 0.36,
        "claim": (
            "Bộ lạc săn hái không bao giờ bắt ép hay chấm điểm con trẻ học tập.",
            "SRC03",
            "Bộ lạc săn hái không bao giờ bắt ép hay chấm điểm con trẻ học tập.",
        ),
    },
    {
        "scene_id": "SC16",
        "chapter": 3,
        "duration": 17.5,
        "title": "Phản hồi tức thì: Động lực tối thượng của việc học",
        "purpose": "Giải thích cơ chế phản hồi ngay lập tức giúp củng cố hứng thú học hỏi",
        "narration": "Mọi bài học nơi hoang dã đều mang lại kết quả thực tế tức thì. [pause:800ms] Học cách nhóm lửa, bạn nhận ngay hơi ấm xua tan giá lạnh đêm sương. Học cách nhận biết quả lành, bạn có bữa trưa ngon lành no bụng. Não bộ đón nhận phần thưởng hữu hình liền tay, khiến ngọn lửa hứng thú không bao giờ nguội tắt.",
        "requirements": [],
        "source_ids": ["SRC03"],
        "action": "Đứa trẻ thổi nhẹ vào bùi nhùi khô, đốm lửa bùng lên sưởi ấm cả bàn tay lạnh",
        "setting": "Bếp lửa nhỏ vừa nhóm lên tỏa ánh sáng ấm áp trong buổi chiều tà",
        "camera": "Cận cảnh đốm lửa bùng sáng từ bùi nhùi khô rồi mở rộng ra nụ cười rạng rỡ",
        "bg_description": "Đống củi khô nhỏ với ngọn lửa vàng cam ấm áp vừa bùng lên xua tan bóng tối chiều tà trên nền giấy sáng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày tươi cười xòe tay đón nhận hơi ấm của ngọn lửa mới nhóm",
        "anchor_quote": "Mọi bài học nơi hoang",
        "fx": "bounce",
        "x": 0.64,
        "y": 0.6,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC17",
        "chapter": 3,
        "duration": 17.5,
        "title": "Đêm kể chuyện bên lửa trại và tri thức cộng đồng",
        "purpose": "Tái hiện không gian học tập cộng đồng ấm áp bên ánh lửa trại",
        "narration": "Khi hoàng hôn buông xuống, cả bộ tộc sum vầy bên đống lửa ấm áp bập bùng. [pause:800ms] Già làng kể lại truyền thuyết các vì sao và kinh nghiệm vượt qua bão tuyết hiểm nghèo. Đám trẻ háo hức chăm chú lắng nghe từng lời chia sẻ. Tri thức sinh tồn được khắc sâu vào tâm trí tự nhiên qua những câu chuyện kể.",
        "requirements": [],
        "source_ids": ["SRC03"],
        "action": "Vòng tròn bộ lạc quây quần bên đống lửa lớn nghe người già chỉ tay lên các chòm sao trên trời",
        "setting": "Vòm trời đêm đầy sao lấp lánh bên đống lửa trại rực rỡ của bộ tộc",
        "camera": "Toàn cảnh vòng tròn lửa trại dưới bầu trời đêm ngập tràn ánh sao",
        "bg_description": "Bầu trời đêm đầy sao với đống lửa trại bập bùng ở trung tâm tỏa ra vòng sáng ấm áp tròn trịa trên nền giấy kem, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày ngồi vòng tay quanh gối ngước nhìn bầu trời sao chăm chú",
        "anchor_quote": "Khi hoàng hôn buông xuống,",
        "fx": "pop",
        "x": 0.36,
        "y": 0.62,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC18",
        "chapter": 3,
        "duration": 17.5,
        "title": "Thời kỳ hoàng kim của niềm vui học hỏi",
        "purpose": "Khép lại chương tiền sử và chuẩn bị bước vào bước ngoặt định mệnh thời cổ đại",
        "narration": "Niềm say mê học tập tự nhiên đã nuôi dưỡng giống loài suốt nhiều thế hệ. Không một ai cảm thấy việc học là gánh nặng khi nó gắn liền với quyền tự do và sinh kế hàng ngày. [pause:800ms] Sự ra đời của nền nông nghiệp định cư đã tạo nên bước ngoặt làm biến đổi vĩnh viễn việc học của con người.",
        "requirements": [],
        "source_ids": ["SRC03"],
        "action": "Hình ảnh thảo nguyên xanh ngát dần chuyển sang cánh đồng lúa nước và những bức tường thành bằng đất nung",
        "setting": "Khung cảnh chuyển tiếp từ thiên nhiên hoang dã sang những rãnh cày và thành quách sơ khai",
        "camera": "Toàn cảnh kéo lùi từ thảo nguyên hoang sơ sang công trường xây dựng thành lũy cổ",
        "bg_description": "Cánh đồng phù sa màu mỡ với những rãnh mương dẫn nước thẳng tắp dẫn tới chân tường thành bằng đất nung cổ kính, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày đứng nhìn về phía công trình thành quách mới xuất hiện",
        "anchor_quote": "Niềm say mê học tập",
        "fx": "slide_left",
        "x": 0.63,
        "y": 0.62,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC19",
        "chapter": 4,
        "duration": 17.5,
        "title": "Cú đứt gãy nông nghiệp và sự ra đời của trường học",
        "purpose": "Trường học đất sét Sumer Edubba thời cổ đại dùng đòn roi để ép học sinh ghi chép thuế",
        "narration": "Hơn năm nghìn năm trước, những đô thị sơ khai mọc lên dọc đôi bờ sông Lưỡng Hà. [pause:800ms] Các kho ngũ cốc của đền thờ đòi hỏi phương thức ghi chép số lượng lương thực và gia súc thu nộp. Chữ viết ra đời, và cùng với đó là sự xuất hiện lần đầu tiên của những lớp học có kỷ luật nghiêm ngặt.",
        "requirements": ["R04"],
        "source_ids": ["SRC04"],
        "action": "Kho thóc đền thờ Sumer với những bao ngũ cốc chất cao và viên quan ghi chép cầm thẻ đất",
        "setting": "Bên ngoài ngôi đền Ziggurat cổ đại bên dòng sông Lưỡng Hà ngập nắng",
        "camera": "Toàn cảnh công trình đền thờ cổ kính và kho thóc lớn",
        "bg_description": "Kiến trúc đền thờ Sumer bằng gạch đất nung bên dòng sông lớn với những kho thóc hình tháp và thuyền chở ngũ cốc, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày cầm phiến đất nung đứng kiểm kê bao lúa mì",
        "anchor_quote": "Hơn năm nghìn năm trước,",
        "fx": "pop",
        "x": 0.35,
        "y": 0.62,
        "w": 0.37,
        "claim": None,
    },
    {
        "scene_id": "SC20",
        "chapter": 4,
        "duration": 17.5,
        "title": "Trường đất sét Edubba và nỗi sợ đòn roi",
        "purpose": "Tái hiện ngôi trường Edubba ở Lưỡng Hà cổ đại và sự ra đời của kỷ luật đòn roi",
        "narration": "Ngôi trường Edubba được dựng lên để đào tạo đội ngũ thư lại chuyên nghiệp. Bốn nghìn năm trước ở Sumer, học sinh bị đánh đòn nếu viết sai chữ nêm. [pause:800ms] Những đứa trẻ phải ngồi khoanh chân từ sáng sớm tới nhá nhem tối trên nền đất, nắn nót từng nét vạch dưới cái nhìn giám sát lạnh lùng của thầy giáo.",
        "requirements": [],
        "source_ids": ["SRC04"],
        "action": "Học trò ngồi khoanh chân trên sàn đất nắn nót viết chữ nêm lên phiến sét ướt dưới bóng cây roi mây của thầy giáo",
        "setting": "Lớp học Edubba bằng tường đất nung mộc mạc bốn nghìn năm trước",
        "camera": "Trung cảnh lớp học cổ xưa rồi lia cận cảnh cây roi mây trên bàn giảng",
        "bg_description": "Phòng học tường đất nung với những chiếc ghế đất thấp và rổ đựng que sậy khắc chữ bên cạnh cây roi mây nghiêm khắc, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày ngồi cúi đầu nắn nót từng nét chữ nêm trên phiến đất",
        "anchor_quote": "Ngôi trường Edubba được dựng",
        "fx": "pop_wobble",
        "x": 0.63,
        "y": 0.6,
        "w": 0.38,
        "claim": (
            "Bốn nghìn năm trước ở Sumer, học sinh bị đánh đòn nếu viết sai chữ nêm.",
            "SRC04",
            "Bốn nghìn năm trước ở Sumer, học sinh bị đánh đòn nếu viết sai chữ nêm.",
        ),
    },
    {
        "scene_id": "SC21",
        "chapter": 4,
        "duration": 17.5,
        "title": "Học vì sổ sách thuế khóa chứ không vì tò mò",
        "purpose": "Chỉ ra mục đích ban đầu của trường học cổ đại là phục vụ bộ máy hành chính nhà nước",
        "narration": "Ý nghĩa nguyên bản của việc học đã biến đổi sâu sắc tại đây. Trường học đất sét cổ đại ra đời để phục vụ ghi chép thuế khóa cho đền thờ. [pause:800ms] Trẻ nhỏ không còn được tìm hiểu những gì mình tò mò. Chúng bị ép học danh mục tài sản khô khốc phục vụ guồng máy hành chính của giới cai trị.",
        "requirements": [],
        "source_ids": ["SRC04"],
        "action": "Bảng chữ nêm liệt kê danh sách cừu, dầu oliu và ngũ cốc khô khan thay cho những câu chuyện kỳ thú",
        "setting": "Bàn học đất sét phủ đầy những phiến gạch ghi số liệu thuế khóa đơn điệu",
        "camera": "Cận cảnh bảng số liệu thuế khóa chữ nêm rồi kéo lùi ra toàn cảnh phòng học ngột ngạt",
        "bg_description": "Những phiến đất sét khắc đầy ký tự chữ nêm hình tam giác khô khốc ghi danh mục thuế khóa xếp chồng lên nhau trên bàn đất, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày ngồi thở dài trước chồng phiến đất số liệu dày đặc",
        "anchor_quote": "Ý nghĩa nguyên bản của",
        "fx": "pop",
        "x": 0.34,
        "y": 0.62,
        "w": 0.36,
        "claim": (
            "Trường học đất sét cổ đại ra đời để phục vụ ghi chép thuế khóa cho đền thờ.",
            "SRC04",
            "Trường học đất sét cổ đại ra đời để phục vụ ghi chép thuế khóa cho đền thờ.",
        ),
    },
    {
        "scene_id": "SC22",
        "chapter": 4,
        "duration": 17.5,
        "title": "Tấm thẻ đất sét ghi lại tiếng than thở đầu tiên",
        "purpose": "Trích dẫn bằng chứng khảo cổ về bức tâm thư than thở đi học của học sinh Sumer",
        "narration": "Một phiến đất sét cổ nghìn năm còn lưu giữ bức tâm thư thấm đẫm cay đắng. [pause:800ms] Cậu học trò Sumer ghi lại rằng mình bị phạt roi vì đi học muộn, và lại ăn đòn khi viết sai ký tự. Tiếng thở dài ngao ngán trước áp lực bài vở đã bắt đầu vang lên từ những căn phòng đất nung ấy.",
        "requirements": [],
        "source_ids": ["SRC04"],
        "action": "Phiến đất sét khảo cổ cổ xưa được trưng bày dưới ánh đèn bảo tàng với các vết nứt lịch sử",
        "setting": "Tủ kính bảo tàng hiện đại soi rọi phiến đất sét Sumer bốn nghìn năm tuổi",
        "camera": "Cận cảnh những dòng chữ nêm than thở khắc sâu trên phiến đất sét cổ",
        "bg_description": "Tủ kính trưng bày bảo tàng với phiến đất sét cổ màu nâu vàng có các vết nứt thời gian và ánh đèn tiêu điểm dịu nhẹ, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày nghiêng đầu đọc bản dịch với ánh mắt đầy đồng cảm",
        "anchor_quote": "Một phiến đất sét cổ",
        "fx": "bounce",
        "x": 0.65,
        "y": 0.62,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC23",
        "chapter": 4,
        "duration": 17.5,
        "title": "Khi việc học trở thành nghĩa vụ cưỡng bức",
        "purpose": "Phân tích sự rạn nứt tâm lý khi động lực học tập chuyển từ nội tại sang ngoại tại",
        "narration": "Sự tò mò tự nhiên bị thay thế bằng nỗi kinh hoàng trước hình phạt đòn roi đau đớn. [pause:800ms] Học trò cặm cụi viết vì sợ những vết lằn roi rát bỏng da thịt. Não bộ gắn liền trang sách với trạng thái căng thẳng và âu lo triền miên. Nỗi sợ hãi trường lớp chính thức cắm rễ sâu vào tâm thức con người.",
        "requirements": [],
        "source_ids": ["SRC04"],
        "action": "Đứa trẻ người que ôm phiến đất bước ra khỏi cổng trường với những vết lằn roi mờ trên cánh tay",
        "setting": "Cổng trường Edubba buổi chiều tà phủ bóng dài trên con hẻm đất bụi bặm",
        "camera": "Toàn cảnh bóng chiều đổ dài trước cổng trường học đất nung",
        "bg_description": "Cổng vòm đất nung cổ kính mở ra con hẻm nhỏ với bóng nắng chiều tà vàng vọt trải dài trên mặt đất nứt nẻ, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày lầm lũi ôm túi thẻ đất bước đi với bước chân nặng trĩu",
        "anchor_quote": "Sự tò mò tự nhiên",
        "fx": "pop_wobble",
        "x": 0.36,
        "y": 0.61,
        "w": 0.37,
        "claim": None,
    },
    {
        "scene_id": "SC24",
        "chapter": 4,
        "duration": 17.5,
        "title": "Mầm mống của sự kháng cự bên trong trí não",
        "purpose": "Tổng kết thời cổ đại và mở đường sang thời phong kiến phương Đông",
        "narration": "Học tập bị tách rời khỏi dòng chảy đời thường và biến thành một nghĩa vụ cưỡng bức nặng nề. Trí não non nớt phải tự dựng nên rào chắn phòng vệ trước những mệnh lệnh hà khắc áp đặt từ bên ngoài. [pause:800ms] Ở các triều đại phong kiến phương Đông, cái bẫy học hành tiếp tục bị siết chặt bởi danh phận gia tộc.",
        "requirements": [],
        "source_ids": ["SRC04"],
        "action": "Hình tượng phiến đất sét Lưỡng Hà dần chuyển biến thành những cuộn sách tre và ống bút lông phương Đông",
        "setting": "Không gian chuyển tiếp từ thành lũy Sumer sang mái đình cong vút của trường thi Á Đông",
        "camera": "Toàn cảnh mở rộng chuyển tiếp văn minh từ Lưỡng Hà sang phương Đông cổ kính",
        "bg_description": "Không gian chuyển tiếp nghệ thuật nối liền phiến đất chữ nêm sang cuộn thẻ tre khắc chữ Hán và nghiên mực đen trên nền giấy sáng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày bước qua cây cầu đá cổ nối liền hai nền văn minh",
        "anchor_quote": "Học tập bị tách rời",
        "fx": "slide_left",
        "x": 0.62,
        "y": 0.63,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC25",
        "chapter": 5,
        "duration": 17.5,
        "title": "Ánh đèn dầu leo lét của sĩ tử phong kiến",
        "purpose": "Thời phong kiến biến học tập thành gánh nặng dòng tộc và bẫy khoa cử thi đỗ làm quan",
        "narration": "Ánh đèn dầu leo lét soi bóng người học trò thức trắng thâu đêm bên án thư. [pause:800ms] Chồng sách kinh viện dày cộp cao ngút ngàn che khuất khung cửa sổ mờ sương. Đè nặng lên đôi vai gầy không chỉ là bài thi, mà là niềm hy vọng đổi đời mãnh liệt của cha mẹ và toàn thể bà con làng xóm.",
        "requirements": ["R05"],
        "source_ids": ["SRC05"],
        "action": "Sĩ tử ngồi dùi mài kinh sử bên ngọn đèn dầu le lói giữa đêm khuya thanh vắng",
        "setting": "Gian nhà tranh vách đất đơn sơ với khung cửa sổ mở nhìn ra đêm trăng lạnh",
        "camera": "Toàn cảnh căn phòng tranh đơn sơ rồi tiến vào ngọn đèn dầu le lói",
        "bg_description": "Bàn gỗ mộc kê bên cửa sổ nhà tranh với chiếc đĩa đèn dầu lạc thắp bấc tim leo lét bên chồng sách đóng chỉ cổ điển, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày đội khăn xếp ngồi khom lưng đọc sách dưới ánh đèn",
        "anchor_quote": "Ánh đèn dầu leo lét",
        "fx": "pop",
        "x": 0.35,
        "y": 0.62,
        "w": 0.37,
        "claim": None,
    },
    {
        "scene_id": "SC26",
        "chapter": 5,
        "duration": 17.5,
        "title": "Gánh nặng danh vọng dòng tộc trên vai sĩ tử",
        "purpose": "Phân tích áp lực xã hội và gia đình đè nặng lên người học thời phong kiến",
        "narration": "Đỗ đạt bảng vàng là con đường duy nhất để rạng danh tổ tông và thoát khỏi cảnh bần hàn. Thời phong kiến, việc học bị biến thành công cụ tiến thân cho cả dòng tộc. [pause:800ms] Đèn sách không còn là hành trình đi tìm tri thức, mà trở thành chiếc cầu độc đạo để chen chân vào hàng ngũ quan lại quyền quý.",
        "requirements": [],
        "source_ids": ["SRC05"],
        "action": "Cả dòng tộc đứng tiễn sĩ tử lên kinh ứng thí với chiếc hòm gỗ đựng sách và những lời dặn dò khuyên răn",
        "setting": "Cổng làng cổ kính với cây đa bến nước rộn ràng cảnh chia tay",
        "camera": "Toàn cảnh cổng làng cổ rồi thu hẹp vào gánh sách trên vai sĩ tử",
        "bg_description": "Cổng làng đá rêu phong dưới bóng cây đa cổ thụ với con đường đất đỏ dẫn ra quan lộ thênh thang trên nền giấy kem, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày gánh đôi bồ sách trĩu nặng trên vai bước đi ngập ngừng",
        "anchor_quote": "Đỗ đạt bảng vàng là",
        "fx": "slide_left",
        "x": 0.64,
        "y": 0.62,
        "w": 0.38,
        "claim": (
            "Thời phong kiến, việc học bị biến thành công cụ tiến thân cho cả dòng tộc.",
            "SRC05",
            "Thời phong kiến, việc học bị biến thành công cụ tiến thân cho cả dòng tộc.",
        ),
    },
    {
        "scene_id": "SC27",
        "chapter": 5,
        "duration": 17.5,
        "title": "Cái bẫy học vẹt và kỳ thi khoa cử ngột ngạt",
        "purpose": "Mô tả phương pháp học vẹt kinh thư Khổng giáo và trường thi khoa cử",
        "narration": "Phương pháp thi cử thời bấy giờ bóp nghẹt mọi mầm mống sáng tạo cá nhân. Học sinh xưa phải học vẹt hàng vạn câu kinh điển để đi thi làm quan. [pause:800ms] Họ phải tụng niệm từng lời của tiền nhân mà không được phép hoài nghi. Một góc nhìn khác biệt có thể làm sụp đổ toàn bộ tương lai trong chớp mắt.",
        "requirements": [],
        "source_ids": ["SRC05"],
        "action": "Lớp học chữ Nho với những sĩ tử lắc lư đầu đọc đồng thanh từng câu kinh thư đóng khung",
        "setting": "Nhà học lợp ngói âm dương với bàn dài và nghiên mực tàu đen nhánh",
        "camera": "Trung cảnh hàng ghế học trò đung đưa đầu đọc sách kinh điển",
        "bg_description": "Lớp học chữ Nho truyền thống với những chiếc bàn dài bằng gỗ gụ, nghiên mực đá và các cuộn giấy điều treo trên vách gỗ, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày tay cầm cuốn sách ngửa đầu đọc thuộc lòng từng câu chữ",
        "anchor_quote": "Phương pháp thi cử thời",
        "fx": "pop",
        "x": 0.34,
        "y": 0.62,
        "w": 0.36,
        "claim": (
            "Học sinh xưa phải học vẹt hàng vạn câu kinh điển để đi thi làm quan.",
            "SRC05",
            "Học sinh xưa phải học vẹt hàng vạn câu kinh điển để đi thi làm quan.",
        ),
    },
    {
        "scene_id": "SC28",
        "chapter": 5,
        "duration": 17.5,
        "title": "Lều chõng trường thi: Chiếc lồng giam cầm trí tuệ",
        "purpose": "Mô tả trường thi khoa cử và tâm lý hoảng loạn của thí sinh",
        "narration": "Mỗi mùa khoa cử, hàng vạn thí sinh chen chúc trong những gian lều chõng ngột ngạt. [pause:800ms] Họ bị cách ly suốt nhiều ngày để gò ép câu chữ vào khuôn mẫu bát cổ cứng nhắc. Tỷ lệ đỗ đạt vô cùng khắc nghiệt và hiếm hoi. Phần lớn sĩ tử dành trọn tuổi xuân ứng thí rồi ngậm ngùi tay trắng trở về.",
        "requirements": [],
        "source_ids": ["SRC05"],
        "action": "Hàng ngàn chiếc lều bạt nhỏ xếp san sát nhau như mê cung trong trường thi với cờ xí nghiêm ngặt",
        "setting": "Bãi đất rộng của trường thi khoa cử với chòi canh gác của quan trường",
        "camera": "Toàn cảnh từ trên cao nhìn xuống mê cung lều chõng trường thi",
        "bg_description": "Trường thi mênh mông với hàng trăm ô lều bạt vải bạt trắng thẳng hàng dưới chòi canh cao vút và cờ lệnh bay trong gió, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày ngồi co ro trong chiếc lều nhỏ chăm chú mài mực viết văn",
        "anchor_quote": "Mỗi mùa khoa cử, hàng",
        "fx": "bounce",
        "x": 0.65,
        "y": 0.62,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC29",
        "chapter": 5,
        "duration": 17.5,
        "title": "Nghịch lý: Học để làm quan hay học để hiểu biết?",
        "purpose": "Làm rõ sự biến dạng của tri thức khi bị trói chặt vào thi cử",
        "narration": "Người ta lao vào sách vở vì sợ miệng đời chê cười, chứ chẳng còn chút rung động say mê đích thực. [pause:800ms] Trạng thái ganh đua danh vị biến tri thức thành món hàng đổi chác lạnh lùng. Thay vì mở rộng tầm nhìn, con người tự giam mình trong chiếc lồng áp lực do chính định kiến xã hội tạo dựng nên.",
        "requirements": [],
        "source_ids": ["SRC05"],
        "action": "Bảng vàng vinh quy bái tổ rực rỡ lọng vàng đối lập với bóng lưng già nua của người sĩ tử thi trượt",
        "setting": "Cảnh tượng đối lập giữa đoàn rước trạng nguyên và góc phố vắng của người thi hỏng",
        "camera": "Chuyển động đối lập từ đám rước cờ hoa sang góc tối của người thi hỏng",
        "bg_description": "Bức tranh đối lập nghệ thuật: một bên là chiếc lọng vàng rực rỡ của trạng nguyên, bên kia là chiếc lều chõng cũ kỹ rách nát trên nền giấy kem, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày tóc bạc buông thõng hai tay thở dài lặng lẽ",
        "anchor_quote": "Người ta lao vào sách",
        "fx": "pop_wobble",
        "x": 0.36,
        "y": 0.61,
        "w": 0.37,
        "claim": None,
    },
    {
        "scene_id": "SC30",
        "chapter": 5,
        "duration": 17.5,
        "title": "Di sản áp lực gia đình kéo dài đến hôm nay",
        "purpose": "Liên hệ áp lực thi cử phong kiến với tâm lý học hành vì kỳ vọng gia đình hiện đại",
        "narration": "Trái ngược với chốn trường thi, các phường thủ công mỹ nghệ dạy nghề rất trực quan qua đôi bàn tay khéo léo. [pause:800ms] Người thợ học việc được tự tay tạo tác sản phẩm và nhìn thấy ngay thành quả. Thế nhưng cuộc cách mạng công nghiệp sau đó đã xóa sổ cách học thực nghiệm bằng cỗ máy trường lớp rập khuôn.",
        "requirements": [],
        "source_ids": ["SRC05"],
        "action": "Chiếc áo dài Nho sinh biến đổi thành bộ đồng phục học sinh nhà máy với chiếc cặp sách vuông vức",
        "setting": "Sự chuyển tiếp từ trường ốc Nho học sang những nhà máy công nghiệp khổng lồ thế kỷ 19",
        "camera": "Toàn cảnh quét mượt mà từ trường học phương Đông sang còi xưởng phương Tây",
        "bg_description": "Khung cảnh chuyển tiếp nối liền mái đình cong cổ kính với những cột ống khói nhà máy bằng gạch đỏ bốc khói xám nhạt, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày xách chiếc cặp vuông bước về phía tòa nhà gạch đỏ",
        "anchor_quote": "Trái ngược với chốn trường",
        "fx": "slide_left",
        "x": 0.62,
        "y": 0.63,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC31",
        "chapter": 6,
        "duration": 17.5,
        "title": "Tiếng còi nhà máy và cuộc cách mạng công nghiệp",
        "purpose": "Cách mạng công nghiệp áp dụng mô hình trường học nhà máy Phổ rèn luyện tính phục tùng",
        "narration": "Khói bụi nhà máy che phủ bầu trời châu Âu khi động cơ hơi nước vận hành ầm ĩ. [pause:800ms] Guồng quay kinh tế mới đòi hỏi hàng triệu lao động biết đọc bảng chỉ dẫn và tuân thủ kỷ luật nghiêm ngặt. Hệ thống giáo dục cưỡng bức quy mô lớn được thiết lập nhằm cung ứng nhân lực cho các xưởng chế tạo.",
        "requirements": ["R06"],
        "source_ids": ["SRC06"],
        "action": "Dây chuyền máy dệt nước Anh và tiếng còi hơi xưởng máy thổi vang báo hiệu giờ làm",
        "setting": "Khu công nghiệp thế kỷ 19 với những nhà máy dệt gạch đỏ và ống khói cao ngút",
        "camera": "Toàn cảnh thành phố công nghiệp sầm uất với bánh răng và dây chuyền",
        "bg_description": "Thành phố công nghiệp châu Âu thế kỷ mười chín với những ống khói gạch đỏ cao vút, bánh răng khổng lồ và chiếc còi hơi phun khói trắng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày mặc áo công nhân đứng nghiêm cạnh bánh răng lớn",
        "anchor_quote": "Khói bụi nhà máy che",
        "fx": "pop",
        "x": 0.35,
        "y": 0.62,
        "w": 0.37,
        "claim": None,
    },
    {
        "scene_id": "SC32",
        "chapter": 6,
        "duration": 17.5,
        "title": "Mô hình trường học nhà máy của nước Phổ",
        "purpose": "Vạch trần nguồn gốc mô hình giáo dục Phổ phân chia học sinh theo độ tuổi như lô hàng",
        "narration": "Kiến trúc trường học hiện nay phản chiếu rõ nét nguồn gốc quân sự thời trước. Mô hình trường học chia theo độ tuổi được sao chép từ nhà máy quân sự Phổ. [pause:800ms] Trẻ em bị phân chia thành các lô đồng nhất theo năm sinh, ngồi thẳng hàng ngay ngắn, chăm chú nhìn lên bục giảng như những người thợ bên dây chuyền.",
        "requirements": [],
        "source_ids": ["SRC06"],
        "action": "Lớp học Phổ với những dãy bàn gỗ đóng cố định thẳng tắp và những học sinh ngồi cùng độ tuổi",
        "setting": "Lớp học kiểu mẫu thế kỷ 19 với bục giảng cao và bảng đen chữ trắng",
        "camera": "Toàn cảnh góc rộng ghi lại những dãy bàn thẳng thớm như dây chuyền sản xuất",
        "bg_description": "Lớp học kiểu mẫu thời kỳ công nghiệp với các dãy bàn học gỗ gắn chặt xuống sàn nhà thẳng tắp và bục giảng gỗ cao ở phía trước, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày ngồi ngay ngắn hai tay đặt lên bàn thẳng lối",
        "anchor_quote": "Kiến trúc trường học hiện",
        "fx": "slide_left",
        "x": 0.64,
        "y": 0.62,
        "w": 0.38,
        "claim": (
            "Mô hình trường học chia theo độ tuổi được sao chép từ nhà máy quân sự Phổ.",
            "SRC06",
            "Mô hình trường học chia theo độ tuổi được sao chép từ nhà máy quân sự Phổ.",
        ),
    },
    {
        "scene_id": "SC33",
        "chapter": 6,
        "duration": 17.5,
        "title": "Tiếng chuông báo giờ và phản xạ dây chuyền",
        "purpose": "Giải thích mục đích thực sự của tiếng chuông trường học và thời khóa biểu cứng nhắc",
        "narration": "Tiếng chuông trường học được thiết kế để rèn thói quen tuân lệnh dây chuyền. [pause:800ms] Chuông reo báo vào lớp, chuông giục tan giờ, chuông định đoạt phút giây giải lao. Nó huấn luyện não bộ phản xạ tuân lệnh mà không cần thắc mắc. Kỷ luật đồng loạt của nhà máy đã hoàn toàn thay thế cho tính tự chủ của mỗi học sinh.",
        "requirements": [],
        "source_ids": ["SRC06"],
        "action": "Chiếc chuông đồng trường học rung lên bần bật trên tường cạnh chiếc đồng hồ tròn chỉ từng giây",
        "setting": "Hành lang trường học với chiếc chuông đồng lớn và chiếc đồng hồ treo tường",
        "camera": "Cận cảnh quả chuông đồng rung mạnh phát ra các vòng sóng âm thanh",
        "bg_description": "Chiếc chuông đồng trường học gắn trên vách tường gạch bên cạnh chiếc đồng hồ tròn có kim giây giật từng nhịp chính xác trên nền giấy sáng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày giật mình đứng phắt dậy khi tiếng chuông vừa dứt",
        "anchor_quote": "Tiếng chuông trường học được",
        "fx": "pop",
        "x": 0.34,
        "y": 0.62,
        "w": 0.36,
        "claim": (
            "Tiếng chuông trường học được thiết kế để rèn thói quen tuân lệnh dây chuyền.",
            "SRC06",
            "Tiếng chuông trường học được thiết kế để rèn thói quen tuân lệnh dây chuyền.",
        ),
    },
    {
        "scene_id": "SC34",
        "chapter": 6,
        "duration": 17.5,
        "title": "Sự đồng hóa và triệt tiêu tính sáng tạo cá nhân",
        "purpose": "Phân tích tác hại của việc áp dụng tiêu chuẩn một kích cỡ cho mọi học sinh",
        "narration": "Trong môi trường đồng dạng của nhà máy, tính hiếu kỳ cá nhân bị coi là sự phiền toái. [pause:800ms] Mọi học sinh đều phải tiếp thu cùng một nội dung giáo trình, theo đúng tốc độ đã được định sẵn. Những tâm hồn yêu thích tìm tòi khác biệt thường bị xem là thiếu tập trung và phải uốn mình vào khuôn khổ chung.",
        "requirements": [],
        "source_ids": ["SRC06"],
        "action": "Khuôn ép kim loại vuông vức đè lên những khối đất sét tròn trịa để biến tất cả thành những khối gạch giống hệt nhau",
        "setting": "Không gian trừu tượng thể hiện sự đóng khuôn cơ học của nền giáo dục hàng loạt",
        "camera": "Trung cảnh chiếc khuôn kim loại dập xuống dãy khối đất sét đa sắc",
        "bg_description": "Chiếc khuôn kim loại hình vuông lớn đang dập xuống hàng khối hình tròn tự nhiên trên nền giấy kem tối giản, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày đứng nhìn chiếc khuôn với ánh mắt băn khoăn",
        "anchor_quote": "Trong môi trường đồng dạng",
        "fx": "bounce",
        "x": 0.65,
        "y": 0.62,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC35",
        "chapter": 6,
        "duration": 17.5,
        "title": "Điểm số và xếp hạng: Sự ra đời của động lực nhân tạo",
        "purpose": "Giải thích sự xuất hiện của điểm số, phần thưởng và hình phạt nhân tạo",
        "narration": "Thang điểm và bảng vàng danh dự được phát minh để duy trì trật tự phòng học suốt nhiều giờ. [pause:800ms] Điểm cao là phần thưởng, điểm kém là nỗi sỉ nhục. Giá trị con người bị đóng khung vào những con số vô hồn, thổi bùng lên nỗi ám ảnh thi trượt cùng tâm lý sợ hãi thất bại triền miên trong đời học sinh.",
        "requirements": [],
        "source_ids": ["SRC06"],
        "action": "Bảng điểm với con dấu đỏ và bảng xếp hạng thứ bậc treo cao giữa lớp học gây áp lực",
        "setting": "Tấm bảng đen với danh sách xếp hạng thi đua từ cao xuống thấp",
        "camera": "Cận cảnh bảng xếp hạng thứ bậc rồi lia xuống ánh mắt lo âu của học sinh",
        "bg_description": "Tấm bảng đen vẽ bảng phân hạng học sinh với những con số từ một đến năm mươi và con dấu mực đỏ trên nền giấy sáng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày nhìn vào bảng điểm với đôi vai trĩu nặng âu lo",
        "anchor_quote": "Thang điểm và bảng vàng",
        "fx": "pop_wobble",
        "x": 0.36,
        "y": 0.61,
        "w": 0.37,
        "claim": None,
    },
    {
        "scene_id": "SC36",
        "chapter": 6,
        "duration": 17.5,
        "title": "Khi việc học trở thành lao động khổ sai",
        "purpose": "Tổng kết mô hình trường học công nghiệp và bước sang kỷ nguyên số hiện đại",
        "narration": "Mô hình giáo dục dây chuyền biến việc học thành chuỗi thao tác đơn điệu buồn chán. Nó rèn luyện tính phục tùng nhiều hơn là năng lực tư duy độc lập sắc bén. [pause:800ms] Khi di sản công nghiệp cũ kỹ này va chạm với làn sóng công nghệ số hôm nay, nó đã đẩy khủng hoảng ý chí học tập lên mức đỉnh điểm.",
        "requirements": [],
        "source_ids": ["SRC06"],
        "action": "Cánh cửa lớp học nhà máy mở ra không gian phòng học hiện đại với màn hình máy tính và điện thoại thông minh",
        "setting": "Không gian chuyển tiếp từ trường học thế kỷ 19 sang phòng ngủ với thiết bị số ngày nay",
        "camera": "Toàn cảnh kéo lùi từ bảng đen lớp học công nghiệp vào màn hình điện thoại rực rỡ",
        "bg_description": "Khung cảnh chuyển tiếp từ bức tường gạch trường học cổ sang góc phòng hiện đại với ánh sáng xanh từ các màn hình điện tử, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày bước vào căn phòng ngập tràn ánh sáng màn hình",
        "anchor_quote": "Mô hình giáo dục dây",
        "fx": "slide_left",
        "x": 0.62,
        "y": 0.63,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC37",
        "chapter": 7,
        "duration": 15.0,
        "title": "Chiếc bẫy ba phía trong kỷ nguyên số",
        "purpose": "Kỷ nguyên số bóp nghẹt động lực nội tại bởi chiếc bẫy ba phía bản thân, gia đình và xã hội",
        "narration": "Hãy nhìn lại góc bàn học rất đỗi quen thuộc của bạn giữa đêm khuya lúc này. [pause:800ms] Sự kiệt sức bạn đang gánh chịu hoàn toàn không phải là điều ngẫu nhiên. Bạn đang mắc kẹt giữa chiếc bẫy ba phía: sự tự trách, kỳ vọng người thân và áp lực ngoài xã hội.",
        "requirements": ["R07"],
        "source_ids": ["SRC07"],
        "action": "Ba mũi tên lớn đại diện cho bản thân, gia đình và xã hội cùng chỉ về phía bàn học chật hẹp",
        "setting": "Không gian phòng học hiện đại với ba áp lực vô hình bủa vây xung quanh",
        "camera": "Toàn cảnh căn phòng với ba hướng áp lực bao vây lấy bàn học",
        "bg_description": "Góc phòng học hiện đại với ba hướng mũi tên nét mực đen chỉ thẳng về chiếc bàn học đơn côi ở góc phòng trên nền giấy kem, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày ngồi thu mình giữa tâm điểm của ba hướng mũi tên",
        "anchor_quote": "Hãy nhìn lại góc bàn",
        "fx": "pop",
        "x": 0.36,
        "y": 0.62,
        "w": 0.38,
        "claim": None,
    },
    {
        "scene_id": "SC38",
        "chapter": 7,
        "duration": 15.0,
        "title": "Thuyết tự quyết: Ba trụ cột bị đánh cắp",
        "purpose": "Trình bày Thuyết Tự Quyết (Self-Determination Theory) của Deci & Ryan",
        "narration": "Cảm hứng học tập sụp đổ khi con người mất quyền tự chủ và sự gắn kết. [pause:800ms] Khi bị ép học những kiến thức xa lạ mà không được tự do chọn lựa, thiếu vắng sự sẻ chia chân thành từ người thân, ngọn lửa tò mò bên trong bạn sẽ tự lụi tàn.",
        "requirements": [],
        "source_ids": ["SRC07"],
        "action": "Ba cột trụ tự chủ, năng lực và gắn kết bị nứt toác khiến mái vòm cảm hứng sụp đổ",
        "setting": "Mô hình ba cột trụ kiến trúc nâng đỡ ngọn lửa cảm hứng học tập",
        "camera": "Trung cảnh ba cột trụ nứt vỡ rồi lia cận vào ngọn lửa dần lụi tàn",
        "bg_description": "Ba cột trụ cổ điển bằng nét mực đen nâng đỡ mái vòm biểu tượng, hai cột bị nứt rạn và ngọn lửa nhỏ ở giữa dần tàn lụi trên nền giấy sáng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày đứng buồn bã nhìn ngọn lửa cảm hứng tắt dần",
        "anchor_quote": "Cảm hứng học tập sụp",
        "fx": "slide_left",
        "x": 0.64,
        "y": 0.6,
        "w": 0.36,
        "claim": (
            "Cảm hứng học tập sụp đổ khi con người mất quyền tự chủ và sự gắn kết.",
            "SRC07",
            "Cảm hứng học tập sụp đổ khi con người mất quyền tự chủ và sự gắn kết.",
        ),
    },
    {
        "scene_id": "SC39",
        "chapter": 7,
        "duration": 15.0,
        "title": "Phía gia đình: Tình thương hóa thành áp lực",
        "purpose": "Phân tích tác động của kỳ vọng phụ huynh lên tâm lý người học",
        "narration": "Những người thân yêu luôn kỳ vọng bạn gặt hái thành công chói lọi. Kỳ vọng gia đình và áp lực điểm số bóp nghẹt động lực nội tại của bạn. [pause:800ms] Lời so sánh vô tình biến bài vở thành món nợ ân tình, tạo nỗi sợ hãi mỗi khi bạn ngồi vào bàn học.",
        "requirements": [],
        "source_ids": ["SRC07"],
        "action": "Bữa cơm gia đình với ánh mắt dò xét điểm số và những câu so sánh con nhà người ta",
        "setting": "Bàn ăn gia đình với cuốn sổ liên lạc và bảng điểm đặt bên cạnh",
        "camera": "Trung cảnh bàn ăn gia đình với bầu không khí căng thẳng",
        "bg_description": "Bàn ăn gia đình ấm cúng nhưng có bảng điểm thi mở sẵn đặt cạnh chiếc ly nước, nét vẽ mực đen tối giản trên nền giấy kem, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày cúi gằm mặt xuống bàn ăn với tâm trạng ngột ngạt",
        "anchor_quote": "Những người thân yêu luôn",
        "fx": "pop",
        "x": 0.35,
        "y": 0.63,
        "w": 0.36,
        "claim": (
            "Kỳ vọng gia đình và áp lực điểm số bóp nghẹt động lực nội tại của bạn.",
            "SRC07",
            "Kỳ vọng gia đình và áp lực điểm số bóp nghẹt động lực nội tại của bạn.",
        ),
    },
    {
        "scene_id": "SC40",
        "chapter": 7,
        "duration": 15.0,
        "title": "Phía xã hội: Cuộc đua bằng cấp không hồi kết",
        "purpose": "Phân tích áp lực thành tích từ xã hội và thị trường lao động",
        "narration": "Màn hình điện thoại liên tục phô diễn những tấm gương thủ khoa tài năng xuất chúng. [pause:800ms] Nỗi sợ bị tụt lại phía sau khiến tâm trí của bạn luôn căng thẳng như dây đàn. Bạn học tập trong tâm trạng bất an lo âu hơn là niềm say mê tri thức thuần khiết.",
        "requirements": [],
        "source_ids": ["SRC07"],
        "action": "Màn hình điện thoại hiển thị hàng loạt bài đăng khoe thành tích, học bổng và bảng điểm mười",
        "setting": "Góc phòng tối với ánh sáng lấp lánh của các trang mạng xã hội",
        "camera": "Cận cảnh dòng cấp tin tràn ngập biểu tượng cúp vàng và bằng khen",
        "bg_description": "Màn hình điện thoại lớn với những biểu tượng cúp vàng, giấy khen và đồ thị điểm số vọt cao trên nền giấy kem sáng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày nhìn màn hình điện thoại với vẻ mặt mệt mỏi tự ti",
        "anchor_quote": "Màn hình điện thoại liên",
        "fx": "bounce",
        "x": 0.65,
        "y": 0.61,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC41",
        "chapter": 7,
        "duration": 15.0,
        "title": "Cám dỗ màn hình: Cuộc chiến dopamine không cân sức",
        "purpose": "Chỉ ra mâu thuẫn giữa kích thích dopamine tức thì của điện thoại và sách vở",
        "narration": "Bên cạnh cuốn sách là chiếc điện thoại luôn rung chuông hấp dẫn. [pause:800ms] Nó mang lại nguồn dopamine tức thì sau mỗi cái vuốt chạm ngón tay. Trong khi đó, trang sách đòi hỏi sự kiên nhẫn tích lũy sâu sắc. Tâm trí đương nhiên nghiêng về sự lôi cuốn dễ dàng trước mắt.",
        "requirements": [],
        "source_ids": ["SRC07"],
        "action": "Bàn cân giữa chiếc điện thoại phát ra luồng sáng hấp dẫn và trang sách giáo khoa dày cộp",
        "setting": "Mặt bàn học với sự cạnh tranh khốc liệt giữa thiết bị số và sách vở",
        "camera": "Trung cảnh đối đầu trực diện giữa màn hình phát sáng và trang sách giấy",
        "bg_description": "Chiếc điện thoại thông minh phát ra luồng hào quang rực rỡ đối lập với cuốn sách giấy nằm yên tĩnh bên cạnh trên mặt bàn gỗ, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày lưỡng lự nhìn qua lại giữa hai lựa chọn",
        "anchor_quote": "Bên cạnh cuốn sách là",
        "fx": "pop_wobble",
        "x": 0.35,
        "y": 0.63,
        "w": 0.37,
        "claim": None,
    },
    {
        "scene_id": "SC42",
        "chapter": 7,
        "duration": 15.0,
        "title": "Bạn không hề hỏng hóc, hãy tha thứ cho chính mình",
        "purpose": "Giải tỏa gánh nặng tâm lý và cởi trói sự tự trách bản thân",
        "narration": "Giờ thì bạn đã nhìn thấy toàn cảnh bức tranh sáng tỏ rồi đấy. Bạn kiệt sức không phải vì bản thân kém cỏi hay lười nhác. [pause:800ms] Bạn chỉ là nạn nhân của môi trường học thiếu lành mạnh. Hãy trút bỏ sự tự trách để bắt đầu hồi sinh nguồn năng lượng mới.",
        "requirements": [],
        "source_ids": ["SRC07"],
        "action": "Nhân vật người que trút bỏ chiếc ba lô tảng đá nặng trĩu sau lưng và mỉm cười nhẹ nhõm",
        "setting": "Căn phòng ngập tràn ánh nắng ban mai rực rỡ sau cơn bão đêm",
        "camera": "Toàn cảnh mở rộng đón nhận luồng không khí trong lành",
        "bg_description": "Cửa sổ phòng học mở toang đón nhận luồng gió sớm mát lành và ánh nắng ấm áp chiếu rọi xuống mặt bàn gỗ sạch sẽ, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày đứng thẳng lưng hít thở sâu với nụ cười nhẹ nhõm",
        "anchor_quote": "Giờ thì bạn đã nhìn",
        "fx": "slide_left",
        "x": 0.63,
        "y": 0.62,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC43",
        "chapter": 8,
        "duration": 12.5,
        "title": "Đánh thức người tiền sử bên trong bạn",
        "purpose": "Đánh thức người tiền sử bằng ba chìa khóa tự chủ, mục tiêu ngắn hạn và kết nối để yêu lại việc học",
        "narration": "Đã đến lúc bạn làm chủ lại không gian học tập của chính mình. [pause:800ms] Hãy đánh thức bản năng tò mò thuần khiết bên trong tâm trí bạn. Nắm vững ba giải pháp sau, bạn sẽ tìm lại niềm say mê đích thực.",
        "requirements": ["R08"],
        "source_ids": ["SRC08"],
        "action": "Ba chiếc chìa khóa vàng xuất hiện trên bàn học tượng trưng cho ba nguyên lý học tập",
        "setting": "Góc bàn học sáng sủa với ba chiếc chìa khóa biểu trưng",
        "camera": "Toàn cảnh ba chiếc chìa khóa vàng trên mặt bàn gỗ",
        "bg_description": "Mặt bàn gỗ sáng màu với ba chiếc chìa khóa bằng đồng thau chạm khắc tinh xảo đặt cạnh nhau trên nền giấy kem, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày đưa tay nâng chiếc chìa khóa với vẻ mặt tự tin",
        "anchor_quote": "Đã đến lúc bạn làm",
        "fx": "pop",
        "x": 0.36,
        "y": 0.62,
        "w": 0.38,
        "claim": None,
    },
    {
        "scene_id": "SC44",
        "chapter": 8,
        "duration": 12.5,
        "title": "Chìa khóa 1: Chia nhỏ cuộc đi săn ba mươi phút",
        "purpose": "Áp dụng kỹ thuật chia nhỏ mục tiêu cụ thể để kích hoạt dopamine",
        "narration": "Bí quyết đầu tiên là chia nhỏ mục tiêu hành động. Chỉ cần chia nhỏ việc học thành từng chặng ngắn, não bộ sẽ tự vào guồng. [pause:800ms] Đừng ôm đồm cả cuốn giáo trình dày. Hãy đặt thử thách hai mươi phút vừa sức.",
        "requirements": [],
        "source_ids": ["SRC08"],
        "action": "Chiếc đồng hồ cát hai mươi phút nhỏ nhắn bên cạnh tấm thẻ ghi một nhiệm vụ duy nhất",
        "setting": "Góc bàn học với chiếc đồng hồ cát nhỏ và tờ giấy ghi chú ngắn gọn",
        "camera": "Cận cảnh chiếc đồng hồ cát đang chảy những hạt cát mịn màng",
        "bg_description": "Chiếc đồng hồ cát thủy tinh nhỏ giọt cát vàng mịn đặt cạnh tấm thẻ ghi chú một mục tiêu duy nhất trên mặt bàn gỗ, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày gật đầu quyết đoán đặt tay lên bàn phím",
        "anchor_quote": "Bí quyết đầu tiên là",
        "fx": "slide_left",
        "x": 0.64,
        "y": 0.6,
        "w": 0.36,
        "claim": (
            "Chỉ cần chia nhỏ việc học thành từng chặng ngắn, não bộ sẽ tự vào guồng.",
            "SRC08",
            "Chỉ cần chia nhỏ việc học thành từng chặng ngắn, não bộ sẽ tự vào guồng.",
        ),
    },
    {
        "scene_id": "SC45",
        "chapter": 8,
        "duration": 12.5,
        "title": "Chìa khóa 2: Khôi phục quyền tự chủ và thử sai",
        "purpose": "Khôi phục quyền tự chủ và tinh thần chơi đùa trong học tập",
        "narration": "Bí quyết thứ hai là chủ động sáng tạo và thực hành. Bộ não sẽ yêu việc học khi ta được tự do thử sai và làm chủ tiến trình. [pause:800ms] Hãy tự vẽ sơ đồ và tóm tắt theo cách của riêng bạn.",
        "requirements": [],
        "source_ids": ["SRC08"],
        "action": "Trang giấy vẽ sơ đồ tư duy sinh động với các nét vẽ nguệch ngoạc hài hước",
        "setting": "Trang giấy vẽ sơ đồ tư duy đầy màu sắc và hình minh họa ngộ nghĩnh",
        "camera": "Cận cảnh bàn tay phác thảo sơ đồ tư duy vui nhộn",
        "bg_description": "Tờ giấy vẽ sơ đồ tư duy rực rỡ với các nhánh cây uốn lượn và hình vẽ minh họa ngộ nghĩnh trên nền giấy sáng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày tươi cười cầm bút dạ vẽ những nét ngộ nghĩnh",
        "anchor_quote": "Bí quyết thứ hai là",
        "fx": "pop",
        "x": 0.35,
        "y": 0.63,
        "w": 0.36,
        "claim": (
            "Bộ não sẽ yêu việc học khi ta được tự do thử sai và làm chủ tiến trình.",
            "SRC08",
            "Bộ não sẽ yêu việc học khi ta được tự do thử sai và làm chủ tiến trình.",
        ),
    },
    {
        "scene_id": "SC46",
        "chapter": 8,
        "duration": 12.5,
        "title": "Chìa khóa 3: Tìm lại ngọn lửa trại kết nối bạn bè",
        "purpose": "Tái tạo môi trường học tập cộng đồng có sự chia sẻ và gắn kết",
        "narration": "Bí quyết thứ ba là chia sẻ tri thức cùng bạn bè. [pause:800ms] Hãy giải thích lại khái niệm mới mẻ cho một người bạn thân thiết. Khi được trao đổi qua lại, bài học sẽ sống động và sâu sắc hơn gấp bội phần.",
        "requirements": [],
        "source_ids": ["SRC08"],
        "action": "Hai người bạn cùng ngồi bên ly trà ấm đàm đạo say sưa về một phát hiện mới",
        "setting": "Góc quán cà phê sách ấm áp với ánh đèn vàng và hai tách trà bốc khói",
        "camera": "Trung cảnh cuộc trò chuyện sôi nổi giữa hai người bạn",
        "bg_description": "Bàn gỗ nhỏ bên cửa sổ quán cà phê sách với hai tách trà nóng bốc khói nghi ngút và cuốn sổ mở sẵn, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày hào hứng vung tay giảng giải điều mình vừa hiểu",
        "anchor_quote": "Bí quyết thứ ba là",
        "fx": "bounce",
        "x": 0.65,
        "y": 0.61,
        "w": 0.36,
        "claim": None,
    },
    {
        "scene_id": "SC47",
        "chapter": 8,
        "duration": 12.5,
        "title": "Biến bàn học thành cuộc phiêu lưu tri thức",
        "purpose": "Chuyển hóa góc bàn học thành không gian khám phá tích cực",
        "narration": "Hãy dọn sạch chiếc bàn học của bạn ngay bây giờ. Cất chiếc điện thoại sang phòng khác và bật ánh đèn ấm áp lên. [pause:800ms] Bàn học là bệ phóng cho trí tuệ sáng tạo chứ không phải là căn phòng giam cầm ước mơ.",
        "requirements": [],
        "source_ids": ["SRC08"],
        "action": "Chiếc bàn học gọn gàng ngăn nắp với ngọn đèn bàn ấm áp và cuốn sổ ghi chú mở sẵn",
        "setting": "Góc bàn học tinh tươm thoáng đãng ngập tràn sinh khí mới",
        "camera": "Toàn cảnh góc bàn học gọn gàng ấm áp đầy cảm hứng",
        "bg_description": "Góc bàn học gỗ sáng bóng sạch sẽ tinh tươm với chậu cây xanh nhỏ và chiếc đèn bàn ánh sáng vàng dịu trên nền giấy kem, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày ngồi vào bàn với phong thái đĩnh đạc thư thái",
        "anchor_quote": "Hãy dọn sạch chiếc bàn",
        "fx": "pop_wobble",
        "x": 0.35,
        "y": 0.63,
        "w": 0.37,
        "claim": None,
    },
    {
        "scene_id": "SC48",
        "chapter": 8,
        "duration": 12.5,
        "title": "Mở trang sách đầu tiên với nụ cười nhẹ nhõm",
        "purpose": "Khép lại vòng lặp câu chuyện bằng sự bình thản, tập trung và yêu lại việc học",
        "narration": "Bạn hãy cầm cây bút lên, hít sâu và mỉm cười nhẹ nhõm. Bạn không cần đợi cảm hứng ghé thăm mới bắt đầu học. [pause:800ms] Hãy bắt tay vào hành động, và niềm vui tri thức sẽ lập tức bừng sáng trong tâm trí bạn.",
        "requirements": [],
        "source_ids": ["SRC08"],
        "action": "Nhân vật người que nhẹ nhàng đặt ngòi bút xuống trang giấy và bắt đầu viết những dòng đầu tiên với nụ cười thanh thản",
        "setting": "Góc bàn học tràn ngập ánh nắng bình minh ấm áp khép lại hành trình 13 phút",
        "camera": "Cận cảnh ngòi bút lướt nhẹ trên trang giấy rồi kéo lùi toàn cảnh rực rỡ",
        "bg_description": "Trang giấy mở rộng với những dòng chữ đen nắn nót đầu tiên dưới ánh nắng sớm vàng rực rỡ ngập tràn căn phòng trên nền giấy sáng, không có nhân vật",
        "sticker_description": "Hình tượng người que đầu tròn trắng viền đen dày mỉm cười nhẹ nhõm đặt bút viết với tâm thế say mê tự do",
        "anchor_quote": "Bạn hãy cầm cây bút",
        "fx": "slide_left",
        "x": 0.63,
        "y": 0.62,
        "w": 0.36,
        "claim": None,
    },
]


def create_study_motivation_13m_topic(aspect_ratio: str = "16:9", subtitles: bool = False) -> ResearchedTopic:
    """Build the 13-minute (780s), 8-chapter, 48-scene ResearchedTopic object for Study Motivation History."""
    sources = get_academic_sources()
    required_points = get_required_points()
    characters = [
        {
            "id": "CH01",
            "name": "Nhân vật người que dẫn chuyện và trải nghiệm lịch sử học tập",
            "appearance": "Hình tượng người que tối giản chuẩn mực, đầu tròn trắng viền đen dày khép kín, mắt chấm tròn biểu cảm, thân mình một nét mực thanh mảnh",
            "outfit": "Thay đổi linh hoạt theo bối cảnh lịch sử từ áo da thú tiền sử, áo vải cổ đại Lưỡng Hà, khăn xếp phong kiến đến trang phục học sinh hiện đại trên nền sáng",
        }
    ]

    scenes: List[ResearchedScene] = []
    for item in RAW_SCENES_DATA:
        s_id = item["scene_id"]
        sticker = ResearchedSticker(
            id=f"{s_id}_ST1",
            description=item["sticker_description"],
            character_ids=["CH01"],
            anchor_quote=item["anchor_quote"],
            fx=item["fx"],
            x=float(item.get("x", 0.42)),
            y=float(item.get("y", 0.62)),
            w=float(item.get("w", 0.36)),
            z=2,
        )
        claim_facts = [item["claim"]] if item["claim"] is not None else []
        scenes.append(
            ResearchedScene(
                scene_id=s_id,
                title=item["title"],
                purpose=item["purpose"],
                duration=float(item["duration"]),
                narration=item["narration"],
                requirements=list(item["requirements"]),
                source_ids=list(item["source_ids"]),
                character_ids=["CH01"],
                action=item["action"],
                setting=item["setting"],
                camera=item["camera"],
                bg_description=item["bg_description"],
                stickers=[sticker],
                reused_sticker_ids=[],
                foley_cue="Tiếng lật trang sách nhẹ nhàng, tiếng bút sậy Sumer trên đất sét, tiếng còi xưởng và âm thanh môi trường lịch sử",
                claim_facts=claim_facts,
            )
        )

    return ResearchedTopic(
        topic="Giải Mã Cảm Hứng Học Tập Qua Lịch Sử: Vì Sao Ta Mất Cảm Hứng Học, Đôi Lúc Lại Rất Hứng Thú, Là Do Gia Đình, Xã Hội Hay Bản Thân, Và Con Người Qua Các Thời Kỳ Có Bị Như Vậy Không?",
        audience="Học sinh, sinh viên, người đi làm và quý khán giả muốn giải mã tâm lý học hành vi, lịch sử giáo dục và tìm lại niềm say mê học tập tự nhiên",
        goal="Hiểu rõ bản chất thần kinh học của cảm hứng học tập, nguồn gốc lịch sử của các hình thái trường học từ Sumer, phong kiến đến công nghiệp, và nắm vững 3 chiếc chìa khóa để yêu lại việc học",
        video_type="science_history_explainer",
        min_duration=540.0,
        max_duration=960.0,
        style="Minh hoạ biên tập 2D vẽ tay phong cách Ink Explainer, nhân vật người que đầu tròn trắng viền đen dày tối giản, màu pastel ấm áp trên nền giấy sáng, khung hình 16:9 ngang toàn cảnh, không có chữ trong ảnh.",
        aspect_ratio=aspect_ratio,
        sources=sources,
        required_points=required_points,
        characters=characters,
        scenes=scenes,
        tone="Điềm đạm, ấm áp, sâu sắc, giàu tính khám phá như cuộc trò chuyện bên tách cà phê",
        language="vi",
        subtitles=subtitles,
        voice="Adam",
        speed=1.22,
    )


def build_multi_chapter_bundle(
    bundle_dir: Path,
    topic: ResearchedTopic,
) -> Dict[str, str]:
    """Generate the 8-chapter execution bundle in `sys/exports/study_motivation_bundle/`."""
    manifest_dir = bundle_dir / "manifest"
    scripts_dir = bundle_dir / "scripts"
    templates_dir = bundle_dir / "templates"
    audio_dir = bundle_dir / "audio"
    generated_images_dir = bundle_dir / "generated_images"
    rendered_chapters_dir = bundle_dir / "rendered_chapters"

    for d in (manifest_dir, scripts_dir, templates_dir, audio_dir, generated_images_dir, rendered_chapters_dir):
        d.mkdir(parents=True, exist_ok=True)

    scene_by_id = {s.scene_id: s for s in topic.scenes}
    max_hold_sec = 3.70

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

        # Check if measured spoken audio & cues exist for this chapter
        spoken_wav = audio_dir / f"ch{ch_num}_narration_spoken.wav"
        spoken_cues_path = audio_dir / f"ch{ch_num}_spoken_cues.json"
        ch_duration = float(ch_meta["duration"])
        measured_cues: List[Dict[str, Any]] | None = None

        if spoken_cues_path.is_file():
            try:
                measured_cues = json.loads(spoken_cues_path.read_text(encoding="utf-8"))
                if spoken_wav.is_file() and spoken_wav.stat().st_size > 44:
                    with wave.open(str(spoken_wav), "rb") as wf:
                        ch_duration = round(wf.getnframes() / float(wf.getframerate()), 2)
            except Exception:
                measured_cues = None

        if measured_cues:
            # Build cue windows directly from measured TTS timestamps
            for idx_c, mc in enumerate(measured_cues):
                w_start = 0.0 if idx_c == 0 else round(float(mc["start"]), 3)
                w_end = (
                    round(float(measured_cues[idx_c + 1]["start"]), 3)
                    if idx_c + 1 < len(measured_cues)
                    else ch_duration
                )
                ch_cues.append({
                    "index": idx_c + 1,
                    "scene_id": mc["scene_id"],
                    "text": strip_pause_tags(mc["text"]),
                    "start": round(float(mc["start"]), 3),
                    "end": round(float(mc["end"]), 3),
                    "win_start": w_start,
                    "win_end": w_end,
                    "win_dur": round(w_end - w_start, 3),
                })
        else:
            # Estimate cue windows anchored to planned scene durations (ch_duration = 780s total)
            accum_scene = 0.0
            cue_counter = 1
            for sc in ch_scenes:
                sc_start = round(accum_scene, 3)
                sc_dur = sc.duration
                sent_tuples = split_narration_with_pauses(sc.narration)

                raw_weights = []
                for sent, pause_s in sent_tuples:
                    syl = max(1, len(sent.split()))
                    p_dur = pause_s if pause_s > 0 else 0.35
                    raw_weights.append((syl / 4.0) + p_dur)
                total_w = sum(raw_weights) if raw_weights else 1.0

                cur_sc_cursor = sc_start
                for s_i, (sent, pause_s) in enumerate(sent_tuples):
                    dur_fraction = (raw_weights[s_i] / total_w) * sc_dur
                    s_start = round(cur_sc_cursor, 3)
                    w_end = round(sc_start + sc_dur, 3) if s_i == len(sent_tuples) - 1 else round(cur_sc_cursor + dur_fraction, 3)
                    p_dur = pause_s if pause_s > 0 else 0.35
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
            ch_duration = float(ch_meta["duration"])

        # Group chapter cues by scene_id and apply Cue-Window Allocation
        ch_shot_pos = 1
        for sc_pos, sc in enumerate(ch_scenes):
            sc_cues = [c for c in ch_cues if c["scene_id"] == sc.scene_id]
            sc_start = 0.0 if sc_pos == 0 else sc_cues[0]["win_start"]
            sc_end = ch_duration if sc_pos == len(ch_scenes) - 1 else sc_cues[-1]["win_end"]

            # Allocate shots per cue window so every shot hold <= max_hold_sec (3.70s)
            target_sc_shots = CANONICAL_SCENE_SHOT_COUNTS.get(sc.scene_id, 0)
            cue_shot_counts = [max(1, math.ceil(c["win_dur"] / max_hold_sec)) for c in sc_cues]
            while sum(cue_shot_counts) < target_sc_shots:
                best_i = max(range(len(sc_cues)), key=lambda i: sc_cues[i]["win_dur"] / cue_shot_counts[i])
                cue_shot_counts[best_i] += 1

            total_sc_shots = sum(cue_shot_counts)
            beat_variants = get_scene_beats_v2(sc.scene_id, count=total_sc_shots)

            sc_beat_images: List[Dict[str, Any]] = []
            sc_root_shot_idx = global_shot_idx
            b_cursor = 0
            prev_eff: str | None = None

            for c_obj, k_shots in zip(sc_cues, cue_shot_counts, strict=False):
                w_start = c_obj["win_start"]
                w_end = c_obj["win_end"]
                w_dur = c_obj["win_dur"]
                step = w_dur / k_shots
                cue_shot_entries: List[Dict[str, Any]] = []

                for s_i in range(k_shots):
                    framing_label, beat_desc, semantic_eff = beat_variants[b_cursor]
                    b_idx = b_cursor + 1
                    b_cursor += 1

                    eff = semantic_eff
                    if prev_eff is not None and eff == prev_eff:
                        eff = "pan_right" if eff != "pan_right" else "zoom_in"
                    prev_eff = eff

                    abs_at = w_start if s_i == 0 else round(w_start + s_i * step, 3)
                    next_abs = w_end if s_i == k_shots - 1 else round(w_start + (s_i + 1) * step, 3)
                    hold_dur = round(next_abs - abs_at, 3)
                    rel_at = 0.0 if not sc_beat_images else round(abs_at - sc_start, 3)

                    shot_id = f"CH{ch_num:02d}_{sc.scene_id}_B{b_idx:02d}"
                    img_filename = f"ch{ch_num}_{sc.scene_id.lower()}_b{b_idx:02d}.jpg"
                    full_prompt = f"{STYLE_PREFIX} {framing_label}: {beat_desc}."
                    parent_shot = None if b_idx == 1 else sc_root_shot_idx

                    shot_entry = {
                        "shot_index": global_shot_idx,
                        "shot_id": shot_id,
                        "chapter": ch_num,
                        "chapter_number": ch_num,
                        "chapter_title": ch_meta["title"],
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
                        "effect": eff,
                        "remotion_effect": eff,
                        "framing": framing_label,
                        "prompt": full_prompt,
                        "visual_description": beat_desc,
                        "aspect_ratio": "16:9",
                        "image_file": f"generated_images/ch{ch_num}/{img_filename}",
                        "based_on_shot_index": parent_shot,
                        "timing": {
                            "start_seconds_original": abs_at,
                            "end_seconds_original": next_abs,
                            "duration_seconds": hold_dur,
                            "remotion_at_seconds": rel_at,
                        },
                        "script": {
                            "voiceover_vi": c_obj["text"],
                        },
                        "visual_direction": {
                            "action_description": f"{framing_label}: {beat_desc}",
                            "ai_prompt": full_prompt,
                            "based_on_shot_index": parent_shot,
                        },
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
                        "action_description": f"{framing_label}: {beat_desc}",
                    })
                    global_shot_idx += 1
                    ch_shot_pos += 1

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

        for idx_s, s_entry in enumerate(ch_shots, start=1):
            s_entry["shot_in_chapter"] = f"{idx_s}/{len(ch_shots)}"

        tpl_cues = [{"text": c["text"], "start": c["start"], "end": c["end"]} for c in ch_cues]
        tpl_payload = {
            "aspect_ratio": "16:9",
            "primary_language": "vi",
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "duration": ch_duration,
            "outputs": [
                {
                    "aspect_ratio": "16:9",
                    "language": "vi",
                    "subtitles": False,
                }
            ],
            "scenesByAspect": {
                "16:9": remotion_scenes,
            },
            "tracks": {
                "vi": {
                    "audioSrc": "narration.wav",
                    "duration": ch_duration,
                    "cues": tpl_cues,
                    "scenesByAspect": {
                        "16:9": remotion_scenes,
                    },
                }
            },
        }
        tpl_path = templates_dir / f"ch{ch_num}_props_template.json"
        tpl_str = json.dumps(tpl_payload, indent=2, ensure_ascii=False) + "\n"
        if not (tpl_path.is_file() and tpl_path.read_text(encoding="utf-8") == tpl_str):
            tpl_path.write_text(tpl_str, encoding="utf-8")

        chapter_manifests.append({
            "chapter": ch_num,
            "title": ch_meta["title"],
            "time_span": ch_meta["time_span"],
            "duration_seconds": ch_duration,
            "target_duration_seconds": float(ch_meta["duration"]),
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

    # Write JSON manifest
    manifest_json_path = manifest_dir / "manifest_study_motivation_8ch.json"
    manifest_payload = {
        "project": "study-motivation-16x9-13m",
        "topic": topic.topic,
        "video_aspect_ratio": "16:9",
        "resolution": "1920x1080",
        "fps": 30,
        "target_duration_seconds": 780.0,
        "min_allowed_duration_seconds": topic.min_duration,
        "max_allowed_duration_seconds": topic.max_duration,
        "total_duration_seconds": 780.0,
        "measured_duration_seconds": total_measured_sec,
        "total_chapters": len(CHAPTER_METADATA),
        "total_scenes": len(topic.scenes),
        "total_shots": len(all_shots),
        "sources": topic.sources,
        "chapters": chapter_manifests,
        "shots": all_shots,
    }
    manifest_str = json.dumps(manifest_payload, indent=2, ensure_ascii=False) + "\n"
    if not (manifest_json_path.is_file() and manifest_json_path.read_text(encoding="utf-8") == manifest_str):
        manifest_json_path.write_text(manifest_str, encoding="utf-8")

    # Write Phonetic Normalized Script for OmniVoice TTS (ERR-20261010-08)
    phonetic_script_path = manifest_dir / "phonetic_normalized_script_8ch.json"
    phonetic_script_payload = {
        "version": "1.0",
        "project": "study-motivation-16x9-13m",
        "chapters": [],
    }
    for ch_m in chapter_manifests:
        ch_items = []
        for sc in ch_m["scenes"]:
            for sent_text, pause_sec in split_narration_with_pauses(sc["raw_narration"]):
                norm_text = normalize_for_tts(sent_text)
                ch_items.append({
                    "scene_id": sc["scene_id"],
                    "original_text": sent_text,
                    "normalized_text": norm_text,
                    "pause_after": pause_sec,
                })
        phonetic_script_payload["chapters"].append({
            "chapter": ch_m["chapter"],
            "title": ch_m["title"],
            "sentences": ch_items,
        })
    phonetic_str = json.dumps(phonetic_script_payload, indent=2, ensure_ascii=False) + "\n"
    if not (phonetic_script_path.is_file() and phonetic_script_path.read_text(encoding="utf-8") == phonetic_str):
        phonetic_script_path.write_text(phonetic_str, encoding="utf-8")

    # Write Cue-Shot Mapping
    cue_map_path = manifest_dir / "cue_shot_mapping_8ch.json"
    cue_map_payload = {
        "version": "2.0-cue-anchored",
        "total_chapters": len(CHAPTER_METADATA),
        "total_cues": len(all_cue_records),
        "total_shots": len(all_shots),
        "max_hold_limit_seconds": 3.80,
        "cues": all_cue_records,
    }
    cue_map_str = json.dumps(cue_map_payload, indent=2, ensure_ascii=False) + "\n"
    if not (cue_map_path.is_file() and cue_map_path.read_text(encoding="utf-8") == cue_map_str):
        cue_map_path.write_text(cue_map_str, encoding="utf-8")

    # Write human-readable Markdown manifest
    manifest_md_path = manifest_dir / "manifest_study_motivation_8ch.md"
    md_lines = [
        "# Hồ Sơ Nghiên Cứu & Kịch Bản Sản Xuất (~13 Phút, Khoảng Cho Phép 9–16 Phút): Giải Mã Cảm Hứng Học Tập Qua Lịch Sử",
        "",
        f"- **Chủ đề:** {topic.topic}",
        "- **Định dạng:** `16:9` Widescreen (`1920x1080` @ 30fps)",
        "- **Thời lượng mục tiêu:** `780.0s` (**13 phút**, dải an toàn cho phép **9–16 phút** / `540.0s–960.0s`)",
        f"- **Tổng thời lượng thực tế:** `{total_measured_sec:.2f}s` (**{int(total_measured_sec // 60)} phút {total_measured_sec % 60:04.1f} giây**)",
        f"- **Cấu trúc:** `{len(CHAPTER_METADATA)}` Chương | `{len(topic.scenes)}` Phân cảnh (`SC01`–`SC48`) | `{len(all_shots)}` Nhịp hình ảnh (`Visual Beats`)",
        "",
        "---",
        "",
        "## 1. Nguồn Cứ Liệu Học Thuật & Lịch Sử (8 Nguồn Học Thuật, 16 Dữ Kiện Văn Nói <= 20 Âm Tiết)",
        "",
    ]
    for src in topic.sources:
        md_lines.append(f"### `{src['id']}` — {src['title']}")
        md_lines.append(f"- **Trích dẫn:** {src['reference']}")
        for f_txt in src["facts"]:
            md_lines.append(f"  - *Dữ kiện nói (Spoken Fact):* {f_txt}")
        md_lines.append("")

    md_lines.append("---")
    md_lines.append("")
    md_lines.append("## 2. Kịch Bản Chi Tiết 8 Chương — 48 Phân Cảnh")
    md_lines.append("")

    for ch in chapter_manifests:
        md_lines.append(
            f"### Chương {ch['chapter']}: {ch['title']} (`{ch['time_span']}` — `{ch['duration_seconds']:.1f}s`)"
        )
        md_lines.append("")
        md_lines.append("| Cảnh | Thời lượng | Tiêu đề | Lời dẫn (Conversational Essayist + Breath Tags) |")
        md_lines.append("|---|---:|---|---|")
        for sc_item in ch["scenes"]:
            md_lines.append(
                f"| **{sc_item['scene_id']}** | `{sc_item['duration']:.1f}s` | {sc_item['title']} | {sc_item['raw_narration']} |"
            )
        md_lines.append("")

    md_str = "\n".join(md_lines) + "\n"
    if not (manifest_md_path.is_file() and manifest_md_path.read_text(encoding="utf-8") == md_str):
        manifest_md_path.write_text(md_str, encoding="utf-8")

    return {
        "bundle_dir": str(bundle_dir),
        "manifest_json": str(manifest_json_path),
        "phonetic_script": str(phonetic_script_path),
        "manifest_md": str(manifest_md_path),
        "templates_dir": str(templates_dir),
        "total_shots": str(len(all_shots)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and validate the 13-minute (780s) Study Motivation History research & production blueprint."
    )
    parser.add_argument("--job-id", default="study-motivation-16x9-13m", help="Job ID under sys/runs/")
    parser.add_argument("--output-dir", default=None, help="Explicit output directory for Schema 3.0 files")
    parser.add_argument("--bundle-dir", default=None, help="Explicit directory for 8-chapter export bundle")
    parser.add_argument("--subtitles", action="store_true", help="Enable burned-in subtitles on 16:9 output")
    parser.add_argument("--validate", action="store_true", help="Run full schema and cadence validation")
    args = parser.parse_args()

    out_dir = Path(args.output_dir) if args.output_dir else (SYS_DIR / "runs" / args.job_id)
    bundle_dir = Path(args.bundle_dir) if args.bundle_dir else (SYS_DIR / "exports" / "study_motivation_bundle")

    topic = create_study_motivation_13m_topic(aspect_ratio="16:9", subtitles=args.subtitles)
    pkg_res = write_production_package(out_dir, topic, system_root=SYS_DIR)
    bundle_res = build_multi_chapter_bundle(bundle_dir, topic)

    cadence = pkg_res["cadence_report"]
    print(f"[*] Đã đóng gói hồ sơ Schema 3.0 tại: {pkg_res['output_dir']}")
    print(f"    - brief.json:   {pkg_res['brief_file']}")
    print(f"    - content.json: {pkg_res['content_file']}")
    print(f"    - Brief Hash:   {pkg_res['brief_hash']}")
    print(f"[*] Đã xuất gói thực thi 8 chương ({bundle_res['total_shots']} shots) tại: {bundle_res['bundle_dir']}")
    print(f"    - Manifest JSON:   {bundle_res['manifest_json']}")
    print(f"    - Phonetic Script: {bundle_res['phonetic_script']}")
    print(f"    - Manifest MD:     {bundle_res['manifest_md']}")
    print("\n[*] Kết quả kiểm định âm học (Script Cadence Checker — 48 Scenes):")
    print(f"    - Tổng số cảnh:   {cadence['total_scenes']}")
    print(f"    - Tổng thời lượng: {cadence['total_duration']:.1f}s ({cadence['total_duration'] / 60.0:.1f} phút)")
    print(f"    - Tổng âm tiết:    {cadence['total_actual_syllables']}/{cadence['total_target_syllables']} (target)")
    print(f"    - Max Drift:       {cadence['max_drift']:.2f}s (Ngưỡng chuẩn: <= 0.25s)")
    print(f"    - Số cảnh báo:     {cadence['warnings_count']}")
    print(f"    - Trạng thái:      [{cadence['status']}]")

    if not pkg_res["valid_contracts"]:
        print("\n[FAIL] Lỗi xác thực hợp đồng Schema 3.0:")
        for err in pkg_res["contract_errors"]:
            print(f"  - {err}")
        return 1

    print("  [PASS] Xác thực hợp đồng Schema 3.0 (validate_brief & validate_content): 100% HỢP LỆ.")

    if cadence["warnings_count"] > 0 or cadence["max_drift"] > 0.25:
        print("\n[WARN] Các cảnh cần tinh chỉnh âm tiết (|drift| > 0.25s hoặc có cảnh báo):")
        for sc in cadence["scenes"]:
            if abs(sc["drift"]) > 0.25 or sc["warnings"]:
                print(
                    f"  - {sc['scene_id']}: dur={sc['duration']}s, target={sc['target_syllables']}, "
                    f"actual={sc['actual_syllables']}, drift={sc['drift']:+.2f}s, warnings={sc['warnings']}"
                )
        return 1

    print("\n★ HOÀN TẤT KIẾN TRÚC & KIỂM ĐỊNH 100% CHO CHỦ ĐỀ GIẢI MÃ CẢM HỨNG HỌC TẬP 13 PHÚT (780S)! ★")
    return 0


if __name__ == "__main__":
    sys.exit(main())
