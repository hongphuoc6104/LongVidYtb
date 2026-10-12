#!/usr/bin/env python3
"""
12-Minute (Safe Range: 8-16m / 480s-960s) Research & Production Blueprint Builder:
Topic 6: 'Vì sao con người từng là quái vật đáng sợ nhất hành tinh?'
Why Ancient Humans Were The Most Terrifying Animal Alive (Ink Explainer xmQk_oLVau0).

Produces:
  1. Official SSOT Run Package in sys/runs/terrifying-humans-16x9-12m/:
     - brief.json, content.json, script.json, cadence_report.json
  2. Synchronized Bundle Manifest in sys/exports/terrifying_humans_bundle/manifest/:
     - brief.json, content.json
"""

from __future__ import annotations

import json
import os
import re
import sys
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

from research_story_architect import (
    ResearchedScene,
    ResearchedSticker,
    ResearchedTopic,
    write_production_package,
)
from script_cadence_checker import count_syllables, extract_pauses


def get_academic_sources() -> List[Dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "Endurance running and the evolution of Homo",
            "reference": "Bramble, D. M., & Lieberman, D. E. (2004). Nature, 432(7015), 345-352.",
            "facts": [
                "Người có hàng triệu tuyến mồ hôi tự làm mát.",
                "Thú bốn chân bị khóa nhịp thở khi phi nước đại.",
                "Tổ tiên săn mồi giữa trưa nắng thiêu đốt.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Elastic energy storage in the shoulder and high-speed throwing",
            "reference": "Roach, N. T., et al. (2013). Nature, 498(7455), 483-487.",
            "facts": [
                "Vai người co giãn tích trữ thế năng như dây cung.",
                "Ném đá và giáo vượt một trăm bốn mươi cây số giờ.",
                "Vượn không thể ném xa chính xác như con người.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Unique morphology of the human eye and cooperative eye hypothesis",
            "reference": "Kobayashi, H., & Kohshima, S. (2001). Journal of Human Evolution, 40(5), 419-435.",
            "facts": [
                "Chỉ con người có tròng trắng mắt lộ rõ.",
                "Động vật săn mồi có mắt sẫm giấu hướng nhìn.",
                "Bầy thợ săn ra hiệu bằng ánh mắt trong im lặng.",
            ],
        },
        {
            "id": "SRC04",
            "title": "Global late Quaternary megafauna extinctions linked to humans",
            "reference": "Sandom, C., et al. (2014). Proceedings of the Royal Society B, 281(1787), 20133254.",
            "facts": [
                "Hơn bảy mươi phần trăm thú lớn tuyệt chủng.",
                "Dấu chân người tới đâu thú khổng lồ biến mất.",
            ],
        },
    ]


def get_required_points() -> List[Dict[str, str]]:
    return [
        {"id": "R01", "text": "Thú săn mồi chỉ chạy nước rút ba mươi giây đầu tiên"},
        {"id": "R02", "text": "Nghịch lý: thú bốn chân bị khóa nhịp thở và không thể vừa chạy vừa thở dốc"},
        {"id": "R03", "text": "Khớp vai tiến hóa thành máy phóng đàn hồi cho phép phóng giáo từ xa"},
        {"id": "R04", "text": "Tròng trắng mắt cho phép toán thợ săn phối hợp gọng kìm trong im lặng tuyệt đối"},
        {"id": "R05", "text": "Khép vòng lặp và trách nhiệm bảo tồn Trái Đất ngày nay"},
    ]


RAW_SCENES_METADATA = [
    # CH1: Đường Chân Trời Thảo Nguyên
    {
        "id": "SC01",
        "title": "Luật chơi trên thảo nguyên",
        "purpose": "Thú săn mồi chỉ chạy nước rút ba mươi giây đầu tiên",
        "narration": "Hãy tưởng tượng bạn là một con linh dương đang gặm cỏ trên thảo nguyên châu Phi. [pause:800ms] Thảo nguyên đầy rẫy hiểm nguy nhưng bạn hiểu luật chơi của thế giới này. [pause:800ms] Nếu báo hoa mai lao ra, bạn chỉ cần chạy thục mạng trong ba mươi giây đầu tiên. [pause:800ms] Thoát khỏi cú vồ đó, kẻ săn mồi sẽ kiệt sức, thở dốc và lập tức bỏ cuộc. [pause:800ms] Bạn an toàn và có thể thong thả cúi xuống gặm cỏ tiếp.",
        "requirements": ["R01"],
        "source_ids": ["SRC01"],
        "claim": None,
        "action": "Linh dương gặm cỏ ngẩng đầu nhìn về phía xa",
        "setting": "Thảo nguyên mênh mông dưới ánh nắng sớm",
        "camera": "Toàn cảnh góc rộng",
        "bg": "Thảo nguyên châu Phi với cây keo cô đơn và đường chân trời xa xăm",
        "sticker": "Hình tượng người que stick-figure đứng thẳng trên đường chân trời",
        "anchor": "bạn là một con linh dương",
    },
    {
        "id": "SC02",
        "title": "Bóng ma hai chân xuất hiện",
        "purpose": "Sinh vật kỳ dị đứng thẳng trên hai chân xuất hiện ở chân trời",
        "narration": "Nhưng một ngày, một sinh vật kỳ dị xuất hiện ở chân trời. [pause:800ms] Nó đứng thẳng trên hai chân, trần trụi không lông và không có nanh nhọn. [pause:800ms] Nó không gầm thét, không chạy nước rút mà chỉ lẳng lặng bước đi từng bước về phía bạn.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Bóng đen hai chân xuất hiện chậm rãi ở phía xa",
        "setting": "Đường chân trời sa mạc cát vàng",
        "camera": "Góc máy trung toàn cảnh",
        "bg": "Đường chân trời xa xôi với bóng dáng hai chân lững thững bước đi",
        "sticker": "Người que bước từng bước điềm tĩnh không vội vã",
        "anchor": "Nó đứng thẳng trên hai chân",
    },
    {
        "id": "SC03",
        "title": "Kẻ không bao giờ dừng lại",
        "purpose": "Cuộc rượt đuổi không ngừng nghỉ của sinh vật hai chân",
        "narration": "Bạn phóng vút đi bỏ xa nó cả cây số trong chớp mắt rồi thở phào. [pause:800ms] Thế nhưng mười lăm phút sau, bóng dáng hai chân ấy lại lững thững hiện ra. [pause:800ms] Bạn lại chạy, nó lại đến, bạn trốn vào bụi rậm nó vẫn tìm ra. [pause:800ms] Không nhanh hơn bạn nhưng sinh vật ấy dường như không bao giờ dừng lại.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Linh dương chạy trốn rồi ngoái lại nhìn thấy bóng người kiên trì tiến tới",
        "setting": "Bụi rậm xavan giữa ban trưa",
        "camera": "Góc lia theo hướng di chuyển",
        "bg": "Khung cảnh bụi cây thấp nơi linh dương ẩn nấp",
        "sticker": "Người que kiên trì chạy bước nhỏ theo dấu vết",
        "anchor": "bóng dáng hai chân ấy lại lững thững",
    },
    {
        "id": "SC04",
        "title": "Cơn ác mộng của muôn loài",
        "purpose": "Định kiến con người yếu ớt bị lật ngược",
        "narration": "Suốt hàng vạn năm qua, ta vẫn tự nhủ rằng con người tiền sử yếu ớt và mong manh. [pause:800ms] Thế nhưng đối với muôn loài, tổ tiên chúng ta chính là cơn ác mộng kinh hoàng nhất từng tồn tại!",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Biểu tượng người thợ săn tiền sử đứng hiên ngang",
        "setting": "Hoàng hôn rực rỡ trên đỉnh đồi",
        "camera": "Cận cảnh nhấn mạnh biểu cảm",
        "bg": "Vầng sáng hoàng hôn chiếu rọi hình bóng thợ săn",
        "sticker": "Người que cầm giáo giương cao biểu thị sức mạnh",
        "anchor": "tổ tiên chúng ta chính là cơn ác mộng",
    },

    # CH2: Vũ Khí Sinh Học Bí Mật (Nhiệt Học & Tuyến Mồ Hôi)
    {
        "id": "SC05",
        "title": "Nghịch lý vũ khí sinh học",
        "purpose": "Vũ khí tản nhiệt ẩn giấu dưới làn da",
        "narration": "Làm thế nào một loài vượn không vuốt sắc lại trở thành kẻ săn mồi tối thượng? [pause:800ms] Câu trả lời nằm ở vũ khí sinh học ẩn giấu dưới làn da. [pause:800ms] Hầu hết thú bốn chân chạy rất nhanh nhưng mang điểm yếu chí mạng ở khả năng làm mát. [pause:800ms] Lớp lông dày giữ nhiệt như chiếc áo khoác bông giữa trưa hè.",
        "requirements": [],
        "source_ids": ["SRC01"],
        "claim": None,
        "action": "So sánh lớp lông thú dày và làn da trần",
        "setting": "Không gian giải phẫu minh họa 2D",
        "camera": "Cận cảnh phân tích",
        "bg": "Bản vẽ cấu tạo da và lông động vật săn mồi",
        "sticker": "Hình tượng thú bốn chân bốc khói nhiệt",
        "anchor": "vũ khí sinh học ẩn giấu dưới làn da",
    },
    {
        "id": "SC06",
        "title": "Chiếc bẫy thở dốc của thú bốn chân",
        "purpose": "Nghịch lý: thú bốn chân bị khóa nhịp thở và không thể vừa chạy vừa thở dốc",
        "narration": "Quan trọng hơn, Thú bốn chân bị khóa nhịp thở khi phi nước đại. [pause:800ms] Mỗi bước nhảy nén lồng ngực ép con thú phải thở ra, khiến chúng chỉ có thể làm mát bằng cách thở dốc. [pause:800ms] Khi đang phi nước đại, chúng tuyệt đối không thể vừa thở dốc vừa phi nước đại được! [pause:800ms] Nhiệt lượng cứ thế tăng vọt như nồi áp suất bị bịt kín.",
        "requirements": ["R02"],
        "source_ids": ["SRC01"],
        "claim": ("Thú bốn chân bị khóa nhịp thở khi phi nước đại.", "SRC01", "Thú bốn chân bị khóa nhịp thở khi phi nước đại."),
        "action": "Sơ đồ chuyển động nén ép phổi khi thú bốn chân chạy nước rút",
        "setting": "Biểu đồ sinh học vận động",
        "camera": "Đặc tả lồng ngực và sải chân",
        "bg": "Biểu đồ cơ học chuyển động bốn chân bị khóa nhịp thở",
        "sticker": "Người que chỉ vào biểu đồ áp suất nhiệt tăng vọt",
        "anchor": "Thú bốn chân bị khóa nhịp thở",
    },
    {
        "id": "SC07",
        "title": "Cơ chế tản nhiệt bằng mồ hôi",
        "purpose": "Người có hàng triệu tuyến mồ hôi tự làm mát",
        "narration": "Còn con người thì sao? [pause:600ms] Ta đứng thẳng trên hai chân, giải phóng lồng ngực khỏi bước chạy. [pause:800ms] Bạn có thể thở theo bất kỳ nhịp độ nào dù đang đi bộ hay chạy bền. [pause:800ms] Người có hàng triệu tuyến mồ hôi tự làm mát. [pause:800ms] Nước bốc hơi từ da cuốn phăng nhiệt lượng thừa ra ngoài.",
        "requirements": [],
        "source_ids": ["SRC01"],
        "claim": ("Người có hàng triệu tuyến mồ hôi tự làm mát.", "SRC01", "Người có hàng triệu tuyến mồ hôi tự làm mát."),
        "action": "Hình minh họa hàng triệu giọt mồ hôi bốc hơi tản nhiệt",
        "setting": "Mặt cắt vi mô lớp biểu bì người",
        "camera": "Cận cảnh tuyến mồ hôi tiết giọt nước",
        "bg": "Cấu tạo tuyến mồ hôi li ti dưới da người",
        "sticker": "Người que chạy bền bỉ với luồng khí mát bao quanh",
        "anchor": "Người có hàng triệu tuyến mồ hôi",
    },
    {
        "id": "SC08",
        "title": "Cuộc săn giữa trưa thiêu đốt",
        "purpose": "Tổ tiên săn mồi giữa trưa nắng thiêu đốt",
        "narration": "Ta là loài duy nhất vừa di chuyển liên tục vừa tự làm mát hoàn hảo. [pause:800ms] Tổ tiên săn mồi giữa trưa nắng thiêu đốt. [pause:800ms] Đúng vào lúc không một dã thú nào dám rời bóng râm!",
        "requirements": [],
        "source_ids": ["SRC01"],
        "claim": ("Tổ tiên săn mồi giữa trưa nắng thiêu đốt.", "SRC01", "Tổ tiên săn mồi giữa trưa nắng thiêu đốt."),
        "action": "Mặt trời rực lửa giữa trưa chiếu xuống thợ săn đơn độc",
        "setting": "Sa mạc bỏng rát mười hai giờ trưa",
        "camera": "Toàn cảnh góc thấp nhìn lên mặt trời",
        "bg": "Mặt trời chói chang trên nền trời vàng rực",
        "sticker": "Người que kiên cường sải bước dưới nắng gắt",
        "anchor": "Tổ tiên săn mồi giữa trưa nắng thiêu đốt",
    },

    # CH3: Cuộc Săn Kiên Trì (Persistence Hunting)
    {
        "id": "SC09",
        "title": "Bắt đầu cuộc săn việt dã",
        "purpose": "Khởi đầu cuộc săn kiên trì giữa nắng 40 độ",
        "narration": "Hãy quan sát cuộc săn kiên trì diễn ra giữa trưa nắng bốn mươi độ. [pause:800ms] Khi sư tử và báo trốn sâu vào bóng râm tránh sốc nhiệt, con người bắt đầu lên đường. [pause:800ms] Mục tiêu là linh dương khỏe mạnh có thể chạy tám mươi cây số một giờ. [pause:800ms] Người thợ săn chỉ duy trì tốc độ chạy việt dã đều đặn mười cây số mỗi giờ.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Thợ săn chạy bước nhỏ nhịp nhàng qua cồn cát",
        "setting": "Thảo nguyên nắng gắt 40 độ C",
        "camera": "Góc quay ngang theo bước chạy đều đặn",
        "bg": "Cồn cát và sóng nhiệt bập bùng trên đường chân trời",
        "sticker": "Người que chạy nhịp nhàng với đồng hồ đếm tốc độ",
        "anchor": "chạy việt dã đều đặn mười cây số",
    },
    {
        "id": "SC10",
        "title": "Cuộc chạy trốn và bóng đen lừng lững",
        "purpose": "Sự dồn ép liên tục khiến con thú không kịp hạ nhiệt",
        "narration": "Con linh dương hoảng loạn phóng vụt đi như một mũi tên xé gió. [pause:800ms] Nhưng chạy nước rút giữa trưa khiến thân nhiệt nó tăng vọt lên mức báo động. [pause:800ms] Nó phải dừng lại thở dốc, nhưng mười lăm phút sau thợ săn lại lừng lững xuất hiện. [pause:800ms] Không được nghỉ ngơi, linh dương phải bỏ chạy lần thứ hai, thứ ba rồi thứ tư.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Linh dương kiệt sức thở dốc dưới gốc cây rồi lại phải bật dậy chạy",
        "setting": "Gốc cây khô héo giữa trưa hè",
        "camera": "Góc lia chuyển tiếp giữa con mồi và thợ săn",
        "bg": "Gốc cây keo trơ trụi với bóng râm ít ỏi",
        "sticker": "Linh dương thè lưỡi thở dốc trong tuyệt vọng",
        "anchor": "thợ săn lại lừng lững xuất hiện",
    },
    {
        "id": "SC11",
        "title": "Sụp đổ vì sốc nhiệt 42 độ",
        "purpose": "Thân nhiệt con thú vượt ngưỡng 42 độ dẫn tới tê liệt",
        "narration": "Sau ba đến bốn tiếng triền miên bị bám đuổi, bi kịch sinh học ập đến. [pause:800ms] Thân nhiệt vượt ngưỡng bốn mươi hai độ khiến nội tạng rơi vào trạng thái sốc nhiệt tê liệt. [pause:800ms] Đôi chân run rẩy, mắt mờ đi và con thú gục ngã xuống đất bỏng rát.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Con thú loạng choạng gục ngã xuống nền đất",
        "setting": "Bãi đất nứt nẻ vì nắng hạn",
        "camera": "Cận cảnh chân run rẩy rồi gục ngã",
        "bg": "Mặt đất nứt nẻ và vạch nhiệt kế chỉ 42 độ C đỏ rực",
        "sticker": "Linh dương nằm gục hoàn toàn mất khả năng phản kháng",
        "anchor": "gục ngã xuống đất bỏng rát",
    },
    {
        "id": "SC12",
        "title": "Chiến thắng bằng sự kiên trì",
        "purpose": "Kết thúc cuộc săn bằng sự bền bỉ vô tận",
        "narration": "Người thợ săn thong thả bước tới không hề kiệt sức và kết liễu con mồi. [pause:800ms] Đó chính là cuộc săn tàn nhẫn và hiệu quả nhất hành tinh: đánh bại đối thủ bằng sự bền bỉ vô tận!",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Thợ săn tiến lại gần con mồi một cách bình thản",
        "setting": "Khung cảnh tĩnh lặng sau cuộc săn",
        "camera": "Toàn cảnh trang nghiêm",
        "bg": "Bầu trời quang đãng và thảm cỏ xavan tĩnh lặng",
        "sticker": "Người que đứng cúi đầu tôn kính con mồi",
        "anchor": "bằng sự bền bỉ vô tận",
    },

    # CH4: Cỗ Máy Phóng Đạn Đàn Hồi (Khớp Vai & Ngọn Giáo)
    {
        "id": "SC13",
        "title": "Sức mạnh vượn người vs con người",
        "purpose": "So sánh lực cánh tay vượn và người",
        "narration": "Sự bền bỉ mới chỉ là một nửa của câu chuyện kinh hoàng này. [pause:800ms] Thứ biến con người thành cỗ máy hủy diệt từ xa chính là đôi cánh tay. [pause:800ms] Tinh tinh khỏe gấp ba lần người nhưng không thể ném xa. [pause:800ms] Vượn không thể ném xa chính xác như con người. [pause:800ms] Ở tổ tiên loài người, các nhà khoa học phát hiện sự biến đổi giải phẫu kỳ diệu.",
        "requirements": [],
        "source_ids": ["SRC02"],
        "claim": ("Vượn không thể ném xa chính xác như con người.", "SRC02", "Vượn không thể ném xa chính xác như con người."),
        "action": "Đối chiếu khớp vai vượn người và khớp vai người đứng thẳng",
        "setting": "Phòng thí nghiệm giải phẫu tiến hóa 2D",
        "camera": "So sánh đối xứng hai nửa khung hình",
        "bg": "Sơ đồ so sánh giải phẫu xương vai vượn và người",
        "sticker": "Người que so sánh tư thế vung tay",
        "anchor": "Vượn không thể ném xa chính xác",
    },
    {
        "id": "SC14",
        "title": "Cỗ máy phóng đạn đàn hồi sinh học",
        "purpose": "Khớp vai tiến hóa thành máy phóng đàn hồi cho phép phóng giáo từ xa",
        "narration": "Khớp vai hạ thấp, xương đòn kéo dài và phần thân trên linh hoạt tuyệt đối. [pause:800ms] Toàn bộ cơ thể con người tiến hóa thành một chiếc máy phóng đạn đàn hồi sinh học. [pause:800ms] Vai người co giãn tích trữ thế năng như dây cung. [pause:800ms] Ném đá và giáo vượt một trăm bốn mươi cây số giờ hạ gục con thú từ khoảng cách ba mươi mét.",
        "requirements": ["R03"],
        "source_ids": ["SRC02"],
        "claim": ("Vai người co giãn tích trữ thế năng như dây cung.", "SRC02", "Vai người co giãn tích trữ thế năng như dây cung."),
        "action": "Thợ săn kéo căng khớp vai như dây cung rồi phóng giáo",
        "setting": "Bìa rừng thời tiền sử",
        "camera": "Đặc tả động tác vung tay tích trữ thế năng",
        "bg": "Các đường cung lực thế năng đàn hồi quanh khớp vai",
        "sticker": "Người que vung tay phóng giáo cực mạnh",
        "anchor": "Vai người co giãn tích trữ thế năng",
    },
    {
        "id": "SC15",
        "title": "Giáo Schöningen và cái chết vô hình",
        "purpose": "Vũ khí phóng từ xa gây bất ngờ cho dã thú",
        "narration": "Tại Đức, khảo cổ khai quật ngọn giáo Schöningen ba trăm nghìn năm tuổi gọt đẽo cân bằng trọng tâm như giáo thi đấu. [pause:800ms] Đặt mình vào vị trí con thú quen giáp lá cà bằng móng và răng: [pause:800ms] từ cự ly ba mươi mét ngoài tầm với, một ngọn giáo sắc lẹm xé gió bay tới găm thẳng tim bạn! [pause:800ms] Cái chết từ cự ly xa ấy chẳng khác nào một phép thuật tàn khốc!",
        "requirements": [],
        "source_ids": ["SRC02"],
        "claim": None,
        "action": "Ngọn giáo gỗ xé gió bay qua không trung găm trúng hồng tâm",
        "setting": "Khu khảo cổ Schöningen nước Đức",
        "camera": "Chuyển động camera theo đường bay ngọn giáo",
        "bg": "Bản vẽ khảo cổ ngọn giáo gỗ Schöningen",
        "sticker": "Mũi giáo gỗ bay thẳng theo đường đạn đạo chuẩn xác",
        "anchor": "ngọn giáo Schöningen ba trăm nghìn năm tuổi",
    },

    # CH5: Tròng Trắng Mắt & Chiến Thuật Bầy Đàn (Cooperative Eye)
    {
        "id": "SC16",
        "title": "Sức mạnh bầy đàn con người",
        "purpose": "Con người tụ họp thành bầy thợ săn nguy hiểm",
        "narration": "Một thợ săn đơn độc đã vô cùng nguy hiểm, nhưng khi tụ họp thành bầy họ là lực lượng không thể ngăn cản. [pause:800ms] Hãy nhìn thẳng vào gương và quan sát đôi mắt của bạn. [pause:800ms] Chỉ con người có tròng trắng mắt lộ rõ. [pause:800ms] Tròng trắng bao quanh con ngươi tạo nên điểm khác biệt.",
        "requirements": ["R04"],
        "source_ids": ["SRC03"],
        "claim": ("Chỉ con người có tròng trắng mắt lộ rõ.", "SRC03", "Chỉ con người có tròng trắng mắt lộ rõ."),
        "action": "Cận cảnh đôi mắt người với tròng trắng sáng rõ",
        "setting": "Khung hình cận cảnh đôi mắt",
        "camera": "Macro đặc tả ánh mắt",
        "bg": "Đồ họa phân tích cấu trúc củng mạc mắt người",
        "sticker": "Người que chỉ tay vào ánh mắt sáng",
        "anchor": "Chỉ con người có tròng trắng mắt",
    },
    {
        "id": "SC17",
        "title": "Bí mật tròng trắng mắt linh trưởng",
        "purpose": "Động vật săn mồi có mắt sẫm giấu hướng nhìn",
        "narration": "Ở loài sói hay sư tử, toàn bộ mắt của chúng đều có màu sẫm tối tăm. [pause:800ms] Động vật săn mồi có mắt sẫm giấu hướng nhìn. [pause:800ms] Nhưng con người chọn tiến hóa ngược lại: tròng trắng biến hướng nhìn thành tín hiệu thị giác rõ mồn một! [pause:800ms] Tại sao lại như vậy?",
        "requirements": [],
        "source_ids": ["SRC03"],
        "claim": ("Động vật săn mồi có mắt sẫm giấu hướng nhìn.", "SRC03", "Động vật săn mồi có mắt sẫm giấu hướng nhìn."),
        "action": "So sánh mắt tối của chó sói và mắt có tròng trắng của người",
        "setting": "Bảng đối chiếu thị giác săn mồi",
        "camera": "Đối chiếu hai cặp mắt",
        "bg": "Bản vẽ mắt chó sói màu nâu đen giấu ánh nhìn",
        "sticker": "Người que nghiêng đầu thắc mắc",
        "anchor": "Động vật săn mồi có mắt sẫm",
    },
    {
        "id": "SC18",
        "title": "Giả thuyết Mắt Hợp tác",
        "purpose": "Bầy thợ săn ra hiệu bằng ánh mắt trong im lặng",
        "narration": "Nhân chủng học gọi đây là Giả thuyết Mắt Hợp tác. [pause:800ms] Trong phục kích, toán thợ săn tiền sử không bao giờ huýt sáo làm kinh động thú rừng. [pause:800ms] Bầy thợ săn ra hiệu bằng ánh mắt trong im lặng. [pause:800ms] Họ phối hợp góc ném giáo chuẩn xác trong im lặng.",
        "requirements": [],
        "source_ids": ["SRC03"],
        "claim": ("Bầy thợ săn ra hiệu bằng ánh mắt trong im lặng.", "SRC03", "Bầy thợ săn ra hiệu bằng ánh mắt trong im lặng."),
        "action": "Ba người thợ săn liếc mắt nhìn nhau phối hợp sau tảng đá",
        "setting": "Tảng đá che chắn vị trí phục kích",
        "camera": "Góc máy trung ba nhân vật",
        "bg": "Tảng đá lớn nơi nhóm thợ săn ẩn nấp",
        "sticker": "Ba người que nhìn nhau qua ánh mắt đồng thuận",
        "anchor": "Bầy thợ săn ra hiệu bằng ánh mắt",
    },
    {
        "id": "SC19",
        "title": "Gọng kìm tử thần trong im lặng",
        "purpose": "Thế trận gọng kìm khép chặt con mồi",
        "narration": "Họ giăng ra thế trận gọng kìm, phục kích đón đầu và bao vây con mồi trong im lặng tuyệt đối. [pause:800ms] Con mồi chỉ nhận ra mình lọt vào bẫy khi những mũi giáo từ bốn phương tám hướng đồng loạt phóng tới!",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Vòng vây khép chặt con thú từ các hướng",
        "setting": "Thung lũng hẹp",
        "camera": "Góc nhìn từ trên cao bao quát thế trận",
        "bg": "Bản đồ chiến thuật gọng kìm vây kín con mồi",
        "sticker": "Các mũi tên chiến thuật vây tròn con thú",
        "anchor": "phục kích đón đầu và bao vây",
    },

    # CH6: Thuần Hóa Ngọn Lửa & Vũ Khí Diệt Đàn
    {
        "id": "SC20",
        "title": "Bóng đêm từng thuộc về dã thú",
        "purpose": "Bóng đêm từng là lãnh địa bất khả xâm phạm của dã thú",
        "narration": "Suốt hàng triệu năm, bóng đêm luôn là lãnh địa bất khả xâm phạm của kẻ săn mồi đỉnh tháp. [pause:800ms] Khứu giác và đôi mắt nhìn đêm của mèo răng kiếm biến mọi sinh vật thành con mồi bất lực.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Đôi mắt mèo răng kiếm phát sáng trong đêm tối",
        "setting": "Rừng đêm u ám thời tiền sử",
        "camera": "Cận cảnh đôi mắt lóe sáng trong bóng tối",
        "bg": "Bóng tối bao trùm với ánh trăng lờ mờ",
        "sticker": "Hình tượng mèo răng kiếm rình rập",
        "anchor": "bóng đêm luôn là lãnh địa",
    },
    {
        "id": "SC21",
        "title": "Thuần hóa ngọn lửa",
        "purpose": "Con người thuần hóa lửa, biến bóng đêm thành pháo đài",
        "narration": "Thế rồi, con người thuần hóa ngọn lửa làm thay đổi vĩnh viễn trật tự tự nhiên. [pause:800ms] Lửa mang lại hơi ấm và biến thịt sống thành năng lượng dồi dào nuôi dưỡng bộ não phát triển. [pause:800ms] Ngọn lửa đã tước đoạt vũ khí tối thượng của bóng đêm khỏi tay các loài dã thú. [pause:800ms] Đốm lửa bập bùng thắp sáng hang đá, biến màn đêm mù mịt thành pháo đài phòng thủ kiên cố. [pause:800ms] Dã thú giờ đây phải co rúm sợ hãi trước ngọn đuốc rực sáng xua tan bóng tối.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Ngọn lửa bùng lên trong hang đá xua tan thú dữ",
        "setting": "Cửa hang đá ấm cúng bập bùng ánh lửa",
        "camera": "Toàn cảnh ánh lửa ấm áp đối lập bóng tối ngoài hang",
        "bg": "Đống lửa trại rực rỡ chiếu sáng vách đá hang",
        "sticker": "Người que cầm đuốc xua đuổi bóng đen ngoài cửa hang",
        "anchor": "con người thuần hóa ngọn lửa",
    },
    {
        "id": "SC22",
        "title": "Bức tường lửa và hẻm núi tử thần",
        "purpose": "Biến lửa thành vũ khí săn mồi diện rộng",
        "narration": "Con người nhanh chóng biến ngọn lửa thành thứ vũ khí hủy diệt diện rộng. [pause:800ms] Họ châm lửa đốt vạt cỏ khô trên thảo nguyên tạo thành những bức tường lửa khổng lồ gầm rú. [pause:800ms] Đàn thú hoảng loạn dẫm đạp chạy trốn và rơi thẳng vào bẫy vực sâu con người đã giăng sẵn. [pause:800ms] Lần đầu tiên, một loài sinh vật có thể xóa sổ cả một đàn thú lớn chỉ bằng ngọn lửa của tự nhiên!",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Bức tường lửa dồn bầy thú về phía hẻm vực sâu",
        "setting": "Vạt cỏ thảo nguyên bốc cháy ngùn ngụt",
        "camera": "Toàn cảnh hoành tráng bức tường lửa",
        "bg": "Bức tường lửa đỏ rực đẩy đàn thú chạy tán loạn",
        "sticker": "Đàn thú chạy về phía hẻm núi dưới sự điều hướng của lửa",
        "anchor": "bức tường lửa khổng lồ gầm rú",
    },

    # CH7: Cuộc Đại Tuyệt Chủng Megafauna
    {
        "id": "SC23",
        "title": "Bắt đầu cuộc đại di cư khỏi châu Phi",
        "purpose": "Cuộc đại di cư và sóng tuyệt chủng bắt đầu",
        "narration": "Khi sở hữu sức bền, phóng giáo sát thủ, bầy đàn câm lặng và ngọn lửa, loài người bắt đầu rời khỏi châu Phi. [pause:800ms] Đó là lúc cuộc đại tuyệt chủng kinh hoàng nhất trong lịch sử động vật có vú bắt đầu. [pause:800ms] Hãy nhìn vào những gì đã xảy ra với những loài thú khổng lồ từng thống trị Kỷ Băng Hà.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Bản đồ các tuyến di cư của loài người tỏa ra khắp thế giới",
        "setting": "Bản đồ địa lý thế giới cổ đại",
        "camera": "Lia toàn cảnh các mũi tên di cư",
        "bg": "Bản đồ các lục địa với các tuyến đường di cư",
        "sticker": "Người que bước đi mang theo ngọn đuốc tiến vào vùng đất mới",
        "anchor": "loài người bắt đầu rời khỏi châu Phi",
    },
    {
        "id": "SC24",
        "title": "Voi ma mút và những gã khổng lồ",
        "purpose": "Dấu chân người tới đâu thú khổng lồ biến mất",
        "narration": "Voi ma mút ngà lớn, hổ răng kiếm, lười đất bốn tấn từng kiên cường vượt qua muôn vàn đợt biến đổi khí hậu khắc nghiệt. [pause:800ms] Dấu chân người tới đâu thú khổng lồ biến mất. [pause:800ms] Toàn bộ những gã khổng lồ ấy đều biến mất không dấu vết chỉ trong chớp mắt khi bóng dáng chúng ta xuất hiện!",
        "requirements": [],
        "source_ids": ["SRC04"],
        "claim": ("Dấu chân người tới đâu thú khổng lồ biến mất.", "SRC04", "Dấu chân người tới đâu thú khổng lồ biến mất."),
        "action": "Bóng voi ma mút khổng lồ dần tan biến thành hư không",
        "setting": "Cánh đồng tuyết trắng Kỷ Băng Hà",
        "camera": "Toàn cảnh gã khổng lồ đơn độc",
        "bg": "Cánh đồng băng tuyết với dấu chân người que in sâu",
        "sticker": "Voi ma mút lông dài sừng sững",
        "anchor": "Dấu chân người tới đâu thú khổng lồ biến mất",
    },
    {
        "id": "SC25",
        "title": "Sóng tuyệt chủng Megafauna toàn cầu",
        "purpose": "Hơn bảy mươi phần trăm thú lớn tuyệt chủng",
        "narration": "Tại châu Úc, hơn tám mươi phần trăm động vật khổng lồ bị xóa sổ sau khi loài người di cư đến. [pause:800ms] Hơn bảy mươi phần trăm thú lớn tuyệt chủng. [pause:800ms] Thú khổng lồ vùng đất mới chưa từng có ký ức tiến hóa để biết sợ hãi sinh vật hai chân nhỏ thó không lông. [pause:800ms] Chúng đứng yên nhìn kẻ lạ tiến lại gần và đó là sai lầm chết người cuối cùng của cả một giống loài.",
        "requirements": [],
        "source_ids": ["SRC04"],
        "claim": ("Hơn bảy mươi phần trăm thú lớn tuyệt chủng.", "SRC04", "Hơn bảy mươi phần trăm thú lớn tuyệt chủng."),
        "action": "Biểu đồ sụt giảm thảm khốc của các loài động vật khổng lồ",
        "setting": "Biểu đồ thống kê tuyệt chủng toàn cầu",
        "camera": "Lướt qua các cột mốc tuyệt chủng",
        "bg": "Biểu đồ đường cong tuyệt chủng dốc đứng sau khi người xuất hiện",
        "sticker": "Người que đứng trên đỉnh ngọn đồi nhìn cảnh tượng hoang tàn",
        "anchor": "Hơn bảy mươi phần trăm thú lớn tuyệt chủng",
    },

    # CH8: Chiếc Gương Lịch Sử & Sứ Mệnh Bảo Tồn
    {
        "id": "SC26",
        "title": "Nhìn vào căn phòng hiện đại",
        "purpose": "Sự tương phản giữa đời sống hiện đại và bản năng săn mồi",
        "narration": "Ngồi trong phòng máy lạnh ngắm thế giới qua màn hình kính, ta rất dễ quên nguồn gốc thực sự của mình. [pause:800ms] Sâu thẳm trong từng tế bào của bạn vẫn là dòng máu của kẻ săn mồi đáng sợ nhất hành tinh.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Người que ngồi làm việc trong văn phòng hiện đại với bóng phản chiếu",
        "setting": "Căn phòng làm việc hiện đại với màn hình máy tính",
        "camera": "Góc máy trung từ sau lưng nhân vật",
        "bg": "Căn phòng hiện đại với cửa kính phản chiếu bóng thợ săn cổ xưa",
        "sticker": "Người que hiện đại nhìn bóng mình trong gương",
        "anchor": "Sâu thẳm trong từng tế bào của bạn",
    },
    {
        "id": "SC27",
        "title": "Bản năng của kẻ săn mồi đỉnh tháp",
        "purpose": "Chiến thắng bằng sự kiên trì, gắn kết và trí tuệ",
        "narration": "Tổ tiên ta chiến thắng không phải bằng nanh nhọn hay nọc độc chết người. [pause:800ms] Họ chiến thắng bằng sự kiên trì không bao giờ bỏ cuộc, bằng phối hợp gắn kết và trí tuệ thấu hiểu quy luật tự nhiên. [pause:800ms] Khi không còn con mãnh thú nào đe dọa ta nữa, câu hỏi lớn nhất lại được đặt ra.",
        "requirements": [],
        "source_ids": [],
        "claim": None,
        "action": "Hình tượng tổ tiên truyền ngọn đuốc tri thức cho thế hệ hôm nay",
        "setting": "Không gian chuyển giao giữa quá khứ và hiện tại",
        "camera": "Toàn cảnh ấm áp",
        "bg": "Sự hòa quyện giữa thảo nguyên xưa và bầu trời sao hiện tại",
        "sticker": "Hai người que cổ xưa và hiện đại bắt tay nhau",
        "anchor": "Họ chiến thắng bằng sự kiên trì",
    },
    {
        "id": "SC28",
        "title": "Chiếc gương và sứ mệnh bảo vệ Trái Đất",
        "purpose": "Khép vòng lặp và trách nhiệm bảo tồn Trái Đất ngày nay",
        "narration": "Liệu con người có thể học cách chung sống hòa bình với muôn loài còn sót lại hay không? [pause:800ms] Kẻ thù lớn nhất của ta hôm nay không còn là hổ răng kiếm hay màn đêm tăm tối ngoài hang đá. [pause:800ms] Kẻ thù lớn nhất chính là lòng tham và sự tàn phá không điểm dừng của chính chúng ta. [pause:800ms] Khép vòng lặp và trách nhiệm bảo tồn Trái Đất ngày nay thuộc về bạn, khi ta chọn trở thành người bảo vệ muôn loài!",
        "requirements": ["R05"],
        "source_ids": [],
        "claim": None,
        "action": "Người que nâng niu mầm cây xanh biểu tượng của sự sống và bảo tồn",
        "setting": "Cánh đồng xanh tươi ngập tràn ánh nắng",
        "camera": "Góc quay tĩnh ấm áp tràn đầy hy vọng",
        "bg": "Bầu trời xanh bao la và Trái Đất tươi đẹp",
        "sticker": "Người que nâng niu mầm cây xanh mọc trên lòng bàn tay",
        "anchor": "Khép vòng lặp và trách nhiệm bảo tồn Trái Đất",
    },
]


def create_terrifying_humans_28scenes_topic() -> ResearchedTopic:
    sources = get_academic_sources()
    required_points = get_required_points()

    characters = [
        {
            "id": "CH01",
            "name": "Thợ săn tiền sử & Người kể chuyện",
            "appearance": "Hình tượng stick-figure tối giản chuẩn mực, đầu tròn trắng viền đen dày, mắt chấm oval, thân nét mực mảnh",
            "outfit": "Trang phục nét vẽ mực đen tối giản trên nền sáng",
        }
    ]

    researched_scenes: List[ResearchedScene] = []
    total_scenes = len(RAW_SCENES_METADATA)

    for i, meta in enumerate(RAW_SCENES_METADATA):
        is_last = (i == total_scenes - 1)
        p_tail = 0.35 if is_last else 0.70
        pause_sec, _, _ = extract_pauses(meta["narration"])
        syl = count_syllables(meta["narration"])
        calibrated_dur = round(pause_sec + (syl / 4.0) + p_tail, 2)

        claim_facts = []
        if meta.get("claim"):
            quote, src_id, fact = meta["claim"]
            claim_facts.append((quote, src_id, fact))

        stickers = [
            ResearchedSticker(
                id=f"{meta['id']}_ST1",
                description=meta["sticker"],
                character_ids=["CH01"],
                anchor_quote=meta["anchor"],
                anchor_quote_en="Ancient human persistence hunter",
                fx="pop" if i % 2 == 0 else "bounce",
                x=0.35 if i % 2 == 0 else 0.64,
                y=0.65,
                w=0.35,
                z=2,
            )
        ]

        sc = ResearchedScene(
            scene_id=meta["id"],
            title=meta["title"],
            purpose=meta["purpose"],
            duration=calibrated_dur,
            narration=meta["narration"],
            narration_en=f"Chapter scene {meta['id']} explainer about terrifying human evolution.",
            requirements=meta["requirements"],
            source_ids=meta["source_ids"],
            character_ids=["CH01"],
            action=meta["action"],
            setting=meta["setting"],
            camera=meta["camera"],
            bg_description=meta["bg"],
            stickers=stickers,
            claim_facts=claim_facts,
        )
        researched_scenes.append(sc)

    return ResearchedTopic(
        topic="Vì sao con người từng là quái vật đáng sợ nhất hành tinh?",
        audience="Khán giả yêu thích khoa học tiến hóa, nhân chủng học và tự nhiên",
        goal="Lật ngược định kiến con người yếu ớt, khám phá những vũ khí tiến hóa đỉnh cao",
        video_type="long_explainer_16x9",
        min_duration=480.0,
        max_duration=960.0,
        style="Hand-drawn 2D explainer illustration in bold black marker-pen outline, flat warm earthy fills, 16:9 widescreen",
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=sources,
        required_points=required_points,
        characters=characters,
        scenes=researched_scenes,
        tone="Điềm đạm, cuốn hút, thông tuệ, giàu kịch tính khoa học",
        conversational_facts=True,
    )


def main():
    print("=" * 75)
    print("Building 28-Scene Production Package for Topic 6: Terrifying Humans")
    print("=" * 75)

    topic = create_terrifying_humans_28scenes_topic()

    # 1. Official SSOT run package
    ssot_run_dir = SYS_DIR / "runs" / "terrifying-humans-16x9-12m"
    result = write_production_package(
        output_dir=ssot_run_dir,
        topic=topic,
        system_root=SYS_DIR,
        brief_revision=1,
    )

    print(f"✓ SSOT Package written to: {ssot_run_dir}")
    print(f"  - brief.json: {result['brief_file']}")
    print(f"  - content.json: {result['content_file']}")
    print(f"  - script.json: {result['script_file']}")
    print(f"  - cadence_report.json: {result['cadence_file']}")
    print(f"  - Brief hash: {result['brief_hash']}")
    print(f"  - Valid contracts: {result['valid_contracts']}")
    if result["contract_errors"]:
        print("  - Contract errors:", result["contract_errors"])
        sys.exit(1)

    cadence = result["cadence_report"]
    print(f"✓ Cadence Report: {cadence['total_scenes']} scenes, status={cadence['status']}, "
          f"max_drift={cadence['max_drift']}s, warnings={cadence['warnings_count']}")

    # 2. Synchronize to exports bundle manifest
    bundle_manifest_dir = SYS_DIR / "exports" / "terrifying_humans_bundle" / "manifest"
    bundle_manifest_dir.mkdir(parents=True, exist_ok=True)

    with open(ssot_run_dir / "brief.json", "r", encoding="utf-8") as f:
        brief_data = json.load(f)
    with open(ssot_run_dir / "content.json", "r", encoding="utf-8") as f:
        content_data = json.load(f)

    with open(bundle_manifest_dir / "brief.json", "w", encoding="utf-8") as f:
        json.dump(brief_data, f, ensure_ascii=False, indent=2)
    with open(bundle_manifest_dir / "content.json", "w", encoding="utf-8") as f:
        json.dump(content_data, f, ensure_ascii=False, indent=2)

    import shutil
    shutil.copy2(ssot_run_dir / "script.json", bundle_manifest_dir / "script.json")
    shutil.copy2(ssot_run_dir / "cadence_report.json", bundle_manifest_dir / "cadence_report.json")

    print(f"✓ Synchronized brief, content, script, and cadence report to {bundle_manifest_dir}")
    print("=" * 75)


if __name__ == "__main__":
    main()
