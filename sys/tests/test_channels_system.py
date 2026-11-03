"""Unit tests for the 8-channel TikTok (short_9x16) + YouTube (long_16x9) system."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import pytest
from analytics.channel_metrics import VideoMetric, judge, judge_all, load_metrics
from channels.registry import (
     apply_channel,
    channel_cast,
    channel_for_style,
    channel_ids,
    channel_profile_stamp,
    channels,
    get_channel,
    writer_brief,
)
from flow_prompts.compiler import find_visual_cliche
from tools.generate_channel_plans import WEEK1_BUNDLES, generate_all_plans, render_channel_plan
from tools.script_hook_scorer import score_script
from tools.setup_channel_workspaces import build_channel_config
from visual_style import render_style

WAVE1_IDS = [
    "nao_luoi",
    "tui_tien",
    "ua_sao_vay",
    "su_ke_lai",
    "thuong_cho_kheo",
    "ho_so_ky_la",
    "co_the_ke",
    "ai_binh_dan",
]

WAVE2_IDS = [
    "luat_ngam",
    "ban_do_quyen_luc",
    "dia_com",
    "luat_doi_thuong",
    "banh_rang",
    "vu_tru_ti_hon",
    "nghe_song_sot",
    "la_ban_hoc_thuat",
]

WAVE3_IDS = [
    "chanh_niem_ke",
    "loi_sang_soi",
    "minh_triet_song",
    "tam_tinh_dem",
]

WAVE4_IDS = [
    "en_lazy_brain",
    "en_crowd_strings",
    "en_kindred_sketch",
    "en_first_principles",
    "en_wallet_anatomy",
    "en_macro_gears",
    "en_plain_sight_ai",
    "en_career_leverage",
    "en_fine_print",
    "en_inside_vessel",
    "en_kitchen_molecules",
    "en_wait_how",
    "en_cold_case_ink",
    "en_choke_point",
    "en_pocket_cosmos",
    "en_second_arrow",
    "en_parable_lamp",
    "en_bamboo_marble",
]

EXPECTED_IDS = WAVE1_IDS + WAVE2_IDS + WAVE3_IDS + WAVE4_IDS

# Register Wave 2 bundles in WEEK1_BUNDLES for plan generation testing
WAVE2_WEEK1_BUNDLES: Dict[str, Dict[str, object]] = {
    "luat_ngam": {
        "youtube_long": {
            "title": "Bóc Tách 5 Mẹo Thao Túng Tâm Lý Đám Đông Khiến Bạn Mất Tiền & Bị Dẫn Dắt (Kèm Cách Tự Vệ)",
            "duration": "12 phút (24 cảnh)",
            "hook": "Bạn có bao giờ bước vào một quán ăn chỉ vì thấy ngoài cửa đông người xếp hàng, dù trước đó bạn chưa từng nghe tên quán?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "chọn theo đám đông", "45s"),
            ("Spin-off #2 (0 ảnh mới)", "Bẫy khan hiếm nhân tạo: mánh khóe khiến bạn chốt đơn trong 10 giây.", "40s"),
            ("Spin-off #3 (0 ảnh mới)", "Hiệu ứng người ngoài cuộc: vì sao giữa đám đông không ai chịu giúp đỡ?", "45s"),
            ("Fast-Short #4 (6 ảnh Flow)", "Thao túng bằng cảm giác tội lỗi trong đàm phán đời thường.", "50s"),
        ],
    },
    "ban_do_quyen_luc": {
        "youtube_long": {
            "title": "Bàn Cờ Địa Chính Trị: 4 Điểm Nghẽn Hàng Hải Quyết Định Dòng Chảy Kinh Tế & Năng Lượng Toàn Cầu",
            "duration": "14 phút (26 cảnh)",
            "hook": "Nếu một chiếc tàu container bị kẹt ngang một con kênh hẹp chỉ vài trăm mét, toàn bộ chuỗi cung ứng thế giới sẽ thiệt hại hàng tỷ USD mỗi ngày.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "xem bản đồ thế giới", "50s"),
            ("Spin-off #2 (0 ảnh mới)", "Kênh đào Suez: vì sao một con tàu kẹt làm cả thế giới chao đảo?", "45s"),
            ("Spin-off #3 (0 ảnh mới)", "Bản đồ đất hiếm: cuộc chiến ngầm đằng sau mọi chiếc điện thoại thông minh.", "50s"),
            ("Fast-Short #4 (5 ảnh Flow)", "Kênh đào Panama khô hạn: giá hàng hóa toàn cầu bị bóp nghẹt ra sao?", "50s"),
        ],
    },
    "dia_com": {
        "youtube_long": {
            "title": "Hóa Học Trong Mâm Cơm Việt: 5 Bí Quyết Nấu Ăn Ngon & 4 Sai Lầm An Toàn Thực Phẩm Thường Gặp",
            "duration": "11 phút (24 cảnh)",
            "hook": "Ai cũng nghĩ rã đông thịt bằng nước nóng cho nhanh, nhưng bạn có biết vi khuẩn đang nhân đôi sau mỗi 20 phút ở nhiệt độ ấm?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "nấu ăn tại nhà", "45s"),
            ("Spin-off #2 (0 ảnh mới)", "Vì sao rã đông thịt bằng nước nóng là sai lầm nguy hiểm cho sức khỏe?", "40s"),
            ("Spin-off #3 (0 ảnh mới)", "Hóa học của nồi nước dùng phở trong veo không bị đục ngầu.", "45s"),
            ("Fast-Short #4 (6 ảnh Flow)", "Cơm nguội hâm lại: cách bảo quản đúng để không sinh độc tố vi khuẩn.", "45s"),
        ],
    },
    "luat_doi_thuong": {
        "youtube_long": {
            "title": "Trọn Bộ Cẩm Nang Pháp Lý Đời Thường: Thuê Nhà, Đặt Cọc, Cho Vay Tiền & Hợp Đồng Lao Động",
            "duration": "12 phút (26 cảnh)",
            "hook": "Trước khi đặt bút ký vào bất kỳ bản hợp đồng thuê nhà nào, có 3 cái bẫy câu chữ nếu không đọc kỹ sẽ khiến bạn mất trắng tiền cọc.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "đọc kỹ hợp đồng", "50s"),
            ("Spin-off #2 (0 ảnh mới)", "Chuyển khoản cho vay tiền: ghi nội dung gì để có giá trị pháp lý trước tòa?", "45s"),
            ("Spin-off #3 (0 ảnh mới)", "Thử việc xong bị công ty cho nghỉ không lý do: bạn được bồi thường gì?", "45s"),
            ("Fast-Short #4 (6 ảnh Flow)", "Chủ nợ có được quyền nhắn tin đòi người thân của con nợ hay không?", "50s"),
        ],
    },
    "banh_rang": {
        "youtube_long": {
            "title": "Cỗ Máy Kinh Tế Vận Hành Ra Sao: Lạm Phát, Lãi Suất Ngân Hàng & Tác Động Tới Túi Tiền Của Bạn",
            "duration": "13 phút (26 cảnh)",
            "hook": "Khi Cục Dự trữ Liên bang Mỹ quyết định tăng lãi suất, vì sao giá bát phở và tiền lãi vay mua nhà của bạn ở Việt Nam lại thay đổi?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "lo lắng tiền bạc", "50s"),
            ("Spin-off #2 (0 ảnh mới)", "Cơ chế lãi suất ngân hàng: chiếc phanh hãm cỗ máy kinh tế hoạt động ra sao?", "45s"),
            ("Spin-off #3 (0 ảnh mới)", "Vòng xoáy giảm phát: vì sao giá hàng hóa hạ lại là cơn ác mộng kinh tế?", "45s"),
            ("Fast-Short #4 (5 ảnh Flow)", "Chuỗi cung ứng bán dẫn: bánh răng nhỏ quyết định nền công nghệ thế giới.", "50s"),
        ],
    },
    "vu_tru_ti_hon": {
        "youtube_long": {
            "title": "Vũ Trụ Trong Lòng Bàn Tay: 5 Nghịch Lý Không-Thời Gian Kỳ Thú Nhất Giải Thích Kiểu Feynman",
            "duration": "13 phút (24 cảnh)",
            "hook": "Nếu vũ trụ chứa hàng trăm tỷ thiên hà với vô số ngôi sao rực sáng, tại sao khi nhìn lên bầu trời đêm chúng ta chỉ thấy một màu đen thẳm?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "ngắm nhìn bầu trời", "45s"),
            ("Spin-off #2 (0 ảnh mới)", "Hiệu ứng giãn nở thời gian: vì sao phi hành gia già chậm hơn người ở Trái Đất?", "45s"),
            ("Spin-off #3 (0 ảnh mới)", "Bên trong đường chân trời sự kiện của lỗ đen thực sự có những gì?", "50s"),
            ("Fast-Short #4 (6 ảnh Flow)", "Thí nghiệm khe đôi: một hạt có thể đi qua cả hai khe cùng lúc như thế nào?", "45s"),
        ],
    },
    "nghe_song_sot": {
        "youtube_long": {
            "title": "Quy Luật Ngầm Chốn Công Sở: Chiến Lược Nâng Cao Vị Thế & Đàm Phán Lương Không Bao Giờ Lép Vế",
            "duration": "12 phút (24 cảnh)",
            "hook": "Người chăm chỉ nhất công ty thường là người dễ bị thay thế nhất, nếu bạn không nắm được đòn bẩy giá trị mà sếp thật sự cần.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "đi làm chăm chỉ", "45s"),
            ("Spin-off #2 (0 ảnh mới)", "3 dấu hiệu công ty sắp thanh lọc nhân sự mà bạn cần nhận ra trước 3 tháng.", "45s"),
            ("Spin-off #3 (0 ảnh mới)", "Cách nói chuyện với sếp khó tính mà không bị mất lòng hay lép vế.", "45s"),
            ("Fast-Short #4 (6 ảnh Flow)", "Quy luật ngầm tăng lương: không phải làm thêm giờ, mà là nắm mắt xích này.", "50s"),
        ],
    },
    "la_ban_hoc_thuat": {
        "youtube_long": {
            "title": "Làm Chủ Mọi Kiến Thức Khó: Kỹ Thuật Feynman & Quy Trình Đọc Hiểu Tài Liệu Nghiên Cứu Chuyên Sâu",
            "duration": "12 phút (24 cảnh)",
            "hook": "Đừng bao giờ đọc một bài báo khoa học từ đầu đến cuối như đọc tiểu thuyết: chỉ cần áp dụng phương pháp 3 bước này, bạn sẽ nắm trọn ý cốt lõi trong 15 phút.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "ghi chép cẩn thận", "45s"),
            ("Spin-off #2 (0 ảnh mới)", "Kỹ thuật Feynman 4 bước giúp bạn làm chủ mọi kiến thức khó sau một buổi tối.", "40s"),
            ("Spin-off #3 (0 ảnh mới)", "Phương pháp ghi chú Zettelkasten: biến tài liệu rời rạc thành mạng lưới tư duy.", "45s"),
            ("Fast-Short #4 (5 ảnh Flow)", "Cách đặt câu hỏi nghiên cứu sắc bén cho luận văn tốt nghiệp đại học.", "45s"),
        ],
    },
}

WAVE3_WEEK1_BUNDLES: Dict[str, Dict[str, object]] = {
    "chanh_niem_ke": {
        "youtube_long": {
            "title": "Ẩn Dụ Mũi Tên Thứ Hai: Vì Sao Nỗi Đau Là Bắt Buộc Nhưng Khổ Đau Là Tự Chọn? (Thiền Phật Giáo Ứng Dụng)",
            "duration": "12 phút (24 cảnh)",
            "hook": "Khi một chuyện tồi tệ xảy ra, nỗi đau thực tế chỉ là mũi tên thứ nhất, chính cách tâm trí bạn suy diễn mới là mũi tên thứ hai gây ra đau khổ.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "lắng dịu tâm trí", "45s"),
            ("Spin-off #2 (0 ảnh mới)", "Khi cơn giận bốc lên: cách ôm ấp tâm mình theo tinh thần Thiền sư Thích Nhất Hạnh.", "40s"),
            ("Spin-off #3 (0 ảnh mới)", "Câu chuyện chiếc thuyền rỗng: vì sao ta luôn giận người khác dù họ vô tình?", "45s"),
            ("Fast-Short #4 (5 ảnh Flow)", "Nghệ thuật dừng lại 3 hơi thở khi tâm trí quá tải giữa đêm.", "50s"),
        ],
    },
    "loi_sang_soi": {
        "youtube_long": {
            "title": "Dụ Ngôn Nén Bạc: Bài Học Quản Trị Cuộc Đời & Nghệ Thuật Tha Thứ Để Giải Thoát Cho Chính Mình",
            "duration": "12 phút (24 cảnh)",
            "hook": "Dụ ngôn về những nén bạc cách đây 2000 năm không chỉ là câu chuyện đức tin, mà là bài học kinh điển về cách đầu tư cuộc đời mình.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "tha thứ bao dung", "45s"),
            ("Spin-off #2 (0 ảnh mới)", "Vì sao tha thứ cho người làm tổn thương mình lại là giải thoát cho chính ta?", "40s"),
            ("Spin-off #3 (0 ảnh mới)", "Dụ ngôn người con hoang đàng: khi nào cánh cửa bao dung vẫn mở đợi bạn về?", "45s"),
            ("Fast-Short #4 (5 ảnh Flow)", "5 lời khuyên về tiền bạc và sự khôn ngoan trong sách Châm Ngôn Salômôn.", "50s"),
        ],
    },
    "minh_triet_song": {
        "youtube_long": {
            "title": "Triết Lý Vô Vi Của Lão Tử & Bản Lĩnh Khắc Kỷ: Giữ Tâm Bất Biến Giữa Dòng Đời Vạn Biến",
            "duration": "13 phút (24 cảnh)",
            "hook": "Càng cố nắm chặt một nắm cát thì cát càng chảy qua kẽ tay: triết lý Vô Vi của Lão Tử giúp bạn làm chủ nghịch lý cuộc đời ra sao?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "giữ tâm điềm tĩnh", "45s"),
            ("Spin-off #2 (0 ảnh mới)", "Cái dũng của người điềm tĩnh: khi im lặng mạnh hơn vạn lời tranh cãi.", "40s"),
            ("Spin-off #3 (0 ảnh mới)", "Định luật con ngựa của Tái Ông: vì sao xui xẻo hôm nay có thể là may mắn ngày mai?", "45s"),
            ("Fast-Short #4 (5 ảnh Flow)", "Cách tách biệt thứ kiểm soát được và thứ phải buông bỏ theo triết học Khắc kỷ.", "50s"),
        ],
    },
    "tam_tinh_dem": {
        "youtube_long": {
            "title": "Gác Lại Âu Lo Trước Khi Ngủ: 3 Câu Chuyện Ngụ Ngôn Nhân Sinh Giúp Bạn Ngủ Thật Bình An",
            "duration": "14 phút (24 cảnh)",
            "hook": "Đêm nay trước khi nhắm mắt ngủ, có một câu chuyện ngắn về chiếc bình nứt và những đóa hoa nở rộ bên đường mình muốn gửi đến bạn.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "nghĩ về lòng biết ơn", "45s"),
            ("Spin-off #2 (0 ảnh mới)", "Ba chiếc sàng của Socrates: quy tắc lọc lời đồn trước khi để tâm trí tổn thương.", "40s"),
            ("Spin-off #3 (0 ảnh mới)", "Câu chuyện chiếc bình nứt và bài học chấp nhận những khiếm khuyết của chính mình.", "45s"),
            ("Fast-Short #4 (5 ảnh Flow)", "Trước khi đi ngủ đêm nay: 3 thứ cần đặt xuống để sáng mai thức dậy nhẹ lòng.", "50s"),
        ],
    },
}
WAVE4_WEEK1_BUNDLES: Dict[str, Dict[str, object]] = {
    "en_lazy_brain": {
        "youtube_long": {
            "title": "Why Your Brain Loves Procrastinating on Important Goals (And How to Trick It)",
            "duration": "12 minutes (24 scenes)",
            "hook": "Why does cleaning your desk feel intensely urgent only when an important deadline hits?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "procrastination loop", "45s"),
            ("Spin-off #2 (0 new images)", "The 2-minute dopamine reset that stops doomscrolling instantly.", "40s"),
            ("Spin-off #3 (0 new images)", "Why perfectionism paralyzes your prefrontal cortex.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "How micro-habits bypass your brain's threat detector.", "50s"),
        ],
    },
    "en_crowd_strings": {
        "youtube_long": {
            "title": "7 Psychological Traps Stores Use to Empty Your Wallet Without You Noticing",
            "duration": "12 minutes (24 scenes)",
            "hook": "Have you ever entered a store to buy one item and walked out with five you never planned on?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "consumer compliance trap", "45s"),
            ("Spin-off #2 (0 new images)", "The anchoring trick that makes you overpay every single time.", "40s"),
            ("Spin-off #3 (0 new images)", "Why good people do terrible things inside an anonymous crowd.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "The Benjamin Franklin effect: how a tiny favor builds instant trust.", "50s"),
        ],
    },
    "en_kindred_sketch": {
        "youtube_long": {
            "title": "Why Anxious and Avoidant Partners Always Attract Each Other (And How to Heal)",
            "duration": "13 minutes (26 scenes)",
            "hook": "Why do the very qualities that drew you together in the beginning become the exact triggers in arguments?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "attachment loop", "45s"),
            ("Spin-off #2 (0 new images)", "Why the silent treatment hurts the brain like physical pain.", "40s"),
            ("Spin-off #3 (0 new images)", "4 subtle signs of emotional burnout in long-term relationships.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "How one phrasing shift stops arguments before they escalate.", "50s"),
        ],
    },
    "en_first_principles": {
        "youtube_long": {
            "title": "Mental Models That Change How You Think: Second-Order Thinking & Game Theory",
            "duration": "13 minutes (26 scenes)",
            "hook": "Why do well-intentioned solutions so often create problems far worse than the original crisis?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "mental model logic", "45s"),
            ("Spin-off #2 (0 new images)", "The Prisoner's Dilemma: why being purely selfish always backfires.", "40s"),
            ("Spin-off #3 (0 new images)", "Survivorship bias: the WWII airplane bullet holes everyone misunderstood.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "Goodhart's Law: what happens when a measure becomes the target.", "50s"),
        ],
    },
    "en_wallet_anatomy": {
        "youtube_long": {
            "title": "Why Earning More Money Rarely Makes You Rich: The Psychology of Money Traps",
            "duration": "12 minutes (24 scenes)",
            "hook": "Why do people who double their income often feel just as financially stressed as before?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "lifestyle creep trap", "45s"),
            ("Spin-off #2 (0 new images)", "How Buy Now Pay Later quietly rewires your brain's pain receptor.", "40s"),
            ("Spin-off #3 (0 new images)", "Why busy coffee shops still go bankrupt: hidden unit economics.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "The sunk cost trap that keeps you pouring money into bad choices.", "50s"),
        ],
    },
    "en_macro_gears": {
        "youtube_long": {
            "title": "How the Economic Machine Actually Works in 12 Minutes (Without the Jargon)",
            "duration": "13 minutes (26 scenes)",
            "hook": "When a central bank changes interest rates, how does that decision ripple into your grocery bill?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "economic engine flow", "45s"),
            ("Spin-off #2 (0 new images)", "Who actually gets poorer first when a central bank prints new money?", "45s"),
            ("Spin-off #3 (0 new images)", "The Cantillon Effect: why inflation never hits everyone equally.", "40s"),
            ("Fast-Short #4 (5 Flow images)", "How one tiny semiconductor fab holds the global economy together.", "50s"),
        ],
    },
    "en_plain_sight_ai": {
        "youtube_long": {
            "title": "From Egg to Cannibal Forest: How a Baby Komodo Dragon Survives Its First 5 Years",
            "duration": "13 minutes (26 scenes)",
            "hook": "The moment a baby Komodo dragon slices through its leathery egg, its biggest predator is waiting right outside the nest: its own mother.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "Komodo hatchling tree sprint", "45s"),
            ("Spin-off #2 (0 new images)", "How snakes lost their legs and evolved infrared thermal vision instead.", "45s"),
            ("Spin-off #3 (0 new images)", "Inside the leathery egg: how reptiles broke free from the ocean.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "Why the crocodile body plan survived two mass extinctions unchanged.", "50s"),
        ],
    },
    "en_career_leverage": {
        "youtube_long": {
            "title": "The Peter Principle: Why the Hardest Worker in the Office Rarely Gets Promoted",
            "duration": "12 minutes (24 scenes)",
            "hook": "Working twelve hours a day is often the fastest way to get trapped in the exact same role.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "career leverage balance", "45s"),
            ("Spin-off #2 (0 new images)", "3 quiet signs your company is preparing for layoffs.", "40s"),
            ("Spin-off #3 (0 new images)", "Why visibility beats raw effort inside large organizations every time.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "How to negotiate your salary using anchors without sounding greedy.", "50s"),
        ],
    },
    "en_fine_print": {
        "youtube_long": {
            "title": "The Hidden Clauses in Everyday Contracts That Cost You Thousands Every Year",
            "duration": "12 minutes (24 scenes)",
            "hook": "Before you sign any lease or employment contract, look for these three predatory clauses.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "read the fine print", "45s"),
            ("Spin-off #2 (0 new images)", "Security deposit vs non-refundable fee: why the words matter legally.", "40s"),
            ("Spin-off #3 (0 new images)", "Subscription dark patterns: how apps make canceling intentionally hard.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "5 lease clauses you should always check before signing an apartment lease.", "50s"),
        ],
    },
    "en_inside_vessel": {
        "youtube_long": {
            "title": "What Happens Inside Your Organs During 24 Hours Without Sleep (Hour by Hour)",
            "duration": "13 minutes (26 scenes)",
            "hook": "When you pull an all-nighter, your internal organs trigger an escalating chemical alarm cascade.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "body sleep signals", "45s"),
            ("Spin-off #2 (0 new images)", "Why high stress makes your brain crave sugar uncontrollably.", "40s"),
            ("Spin-off #3 (0 new images)", "How your gut microbiome secretly sends mood signals to your brain.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "What caffeine actually does to adenosine receptors in your brain.", "50s"),
        ],
    },
    "en_kitchen_molecules": {
        "youtube_long": {
            "title": "Year 1 to Year 200: How a Strangler Fig Slowly Devours a Rainforest Giant",
            "duration": "13 minutes (26 scenes)",
            "hook": "It begins as a single sticky seed dropped by a bird high in the canopy, and ends two centuries later as a hollow cage around a dead forest giant.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "strangler fig time-lapse", "45s"),
            ("Spin-off #2 (0 new images)", "Why some pine cones refuse to open until a wildfire burns the forest alive.", "45s"),
            ("Spin-off #3 (0 new images)", "The 60-million-year hostage pact between a fig tree and a dying wasp.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "How carnivorous pitcher plants lure, drown, and digest insects in acid water.", "50s"),
        ],
    },
    "en_wait_how": {
        "youtube_long": {
            "title": "Inside the Chrysalis: How a Caterpillar Dissolves into Liquid and Rebuilds Its Brain",
            "duration": "13 minutes (26 scenes)",
            "hook": "If you cut open a monarch chrysalis on Day 4, you will not find a half-formed butterfly—you will find digestive enzymes dissolving the caterpillar into soup.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "chrysalis metamorphosis cutaway", "45s"),
            ("Spin-off #2 (0 new images)", "Why every freshwater eel on Earth swims 4,000 miles to the Sargasso Sea to die.", "45s"),
            ("Spin-off #3 (0 new images)", "17 years underground: how periodical cicadas count tree sap cycles in the dark.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "The immortal jellyfish: how Turritopsis dohrnii reverses its own life cycle.", "50s"),
        ],
    },
    "en_cold_case_ink": {
        "youtube_long": {
            "title": "The Dyatlov Pass Incident: How Avalanche Physics Solved the 1959 Mystery",
            "duration": "14 minutes (28 scenes)",
            "hook": "In 1959, nine experienced hikers fled their tent in sub-zero cold without shoes or coats.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "forensic mystery files", "50s"),
            ("Spin-off #2 (0 new images)", "Why did the Mary Celeste crew abandon a perfectly safe ship full of food?", "45s"),
            ("Spin-off #3 (0 new images)", "The Flannan Isles lighthouse: what happened to the three keepers?", "45s"),
            ("Fast-Short #4 (5 Flow images)", "The Dancing Plague of 1518: mass hysteria or ergot poisoning?", "50s"),
        ],
    },
    "en_choke_point": {
        "youtube_long": {
            "title": "Why One Narrow Strait Controls the Price of Everything You Buy (Maritime Choke Points)",
            "duration": "14 minutes (26 scenes)",
            "hook": "If a single narrow body of water closes tomorrow, global energy and grain markets halt in hours.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "strategic map check", "50s"),
            ("Spin-off #2 (0 new images)", "Why commercial planes almost never fly over the Tibetan plateau.", "45s"),
            ("Spin-off #3 (0 new images)", "How geography turned Panama and Suez into global economic bottlenecks.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "Why Russia's warm-water port obsession explains centuries of history.", "50s"),
        ],
    },
    "en_pocket_cosmos": {
        "youtube_long": {
            "title": "If the Sun Disappeared Right Now, How Long Would Earth Actually Survive?",
            "duration": "13 minutes (26 scenes)",
            "hook": "If the Sun vanished this second, Earth would stay in light and gravitational orbit for eight minutes.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "cosmic spacetime scale", "45s"),
            ("Spin-off #2 (0 new images)", "Why one hour near a black hole equals seven years on Earth.", "45s"),
            ("Spin-off #3 (0 new images)", "Fermi's Paradox: where is everybody in a galaxy of billions of stars?", "40s"),
            ("Fast-Short #4 (5 Flow images)", "Quantum entanglement explained without mysticism or jargon.", "50s"),
        ],
    },
    "en_second_arrow": {
        "youtube_long": {
            "title": "The Parable of the Second Arrow: Why Pain Is Inevitable, But Suffering Is Optional",
            "duration": "13 minutes (24 scenes)",
            "hook": "When pain strikes your life, the first arrow is unavoidable, but the second arrow is the story you tell.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "mindful stillness", "45s"),
            ("Spin-off #2 (0 new images)", "The empty boat story: how to stop taking everything personally.", "40s"),
            ("Spin-off #3 (0 new images)", "Thich Nhat Hanh on anger: holding difficult emotions without exploding.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "Impermanence explained: why accepting change dissolves anxiety.", "50s"),
        ],
    },
    "en_parable_lamp": {
        "youtube_long": {
            "title": "When Giant 30-Foot Fungi Ruled the Continents Before Trees Evolved (Deep Time Strata)",
            "duration": "14 minutes (26 scenes)",
            "hook": "Four hundred million years ago, before a single tree existed on dry land, towering twenty-six-foot spires of living fungus dominated every coastline on Earth.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "prehistoric giant fungi", "45s"),
            ("Spin-off #2 (0 new images)", "The Great Dying: how one burrowing creature survived the Permian extinction.", "45s"),
            ("Spin-off #3 (0 new images)", "Why evolution keeps turning unrelated crustaceans into crabs (carcinisation).", "45s"),
            ("Fast-Short #4 (5 Flow images)", "How the Carboniferous forest fire era created all the coal on Earth.", "50s"),
        ],
    },
    "en_bamboo_marble": {
        "youtube_long": {
            "title": "Stoic Strength Meets Taoist Calm: Timeless Parables to End Overthinking at Night",
            "duration": "14 minutes (26 scenes)",
            "hook": "Be like bamboo that bends with the wind, anchored by the unyielding marble of inner virtue.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 new images)", "evening stillness reflection", "45s"),
            ("Spin-off #2 (0 new images)", "Lao Tzu's Wu Wei: why forcing your life only makes it fall apart.", "40s"),
            ("Spin-off #3 (0 new images)", "Socrates' three sieves: the 10-second rule before rumors disturb peace.", "45s"),
            ("Fast-Short #4 (5 Flow images)", "The Chinese farmer parable: why bad luck today might save you tomorrow.", "50s"),
        ],
    },
}

WEEK1_BUNDLES.update(WAVE2_WEEK1_BUNDLES)
WEEK1_BUNDLES.update(WAVE3_WEEK1_BUNDLES)
WEEK1_BUNDLES.update(WAVE4_WEEK1_BUNDLES)


def test_twenty_channels_registered_and_complete() -> None:
    assert channel_ids() == EXPECTED_IDS
    all_channels = channels()
    assert len(all_channels) == 38
    for cid, ch in all_channels.items():
        assert ch.id == cid
        assert ch.git_branch == f"channel/{cid.replace('_', '-')}"
        assert ch.workspace_dirname == f"channel-{cid.replace('_', '-')}"
        assert ch.platform_routing == {"tiktok": "short_9x16", "youtube": "long_16x9"}
        assert ch.short_spec.format_profile == "short_9x16"
        assert ch.long_spec.format_profile == "long_16x9"
        assert ch.speed_optimization is not None
        assert ch.speed_optimization.fast_short_max_images <= 8
        assert ch.speed_optimization.spinoff_shorts_per_long >= 4
        assert any(r.format == "short" for r in ch.references)
        assert any(r.format == "long" for r in ch.references)
        assert find_visual_cliche(ch.visual.style_description) is None


def test_visual_style_recognizes_all_channel_styles() -> None:
    for ch in channels().values():
        resolved = render_style({"style": ch.visual.style_description})
        assert resolved == ch.visual.profile_id
        if ch.visual.profile_id.startswith("ch_"):
            matched = channel_for_style(ch.visual.style_description)
            assert matched is not None and matched.id == ch.id


def test_apply_channel_and_provenance_stamp() -> None:
    base_brief = {
        "schema_version": "3.0",
        "topic": "Test topic",
        "outputs": [{"aspect_ratio": "9:16", "language": "vi", "subtitles": True}],
        "seo_keywords": ["test"],
    }
    updated = apply_channel(base_brief, "tui_tien")
    stamp = channel_profile_stamp("tui_tien")
    assert updated["channel_profile"] == stamp
    assert len(stamp["sha256"]) == 64
    assert "grid-paper" in updated["style"]
    assert updated["outputs"][0]["voice"] == "VietNarrator"
    assert "taichinhcanhan" in updated["seo_keywords"]
    cast = channel_cast("tui_tien", "CH01")
    assert cast["id"] == "CH01"
    assert "glasses" in cast["appearance"]


def test_writer_brief_and_plan_generation(tmp_path: Path) -> None:
    wb = writer_brief("ai_binh_dan", "short_9x16")
    assert "channel/ai-binh-dan" in wb
    assert "screen_capture_hybrid" in wb
    assert set(WEEK1_BUNDLES.keys()) == set(EXPECTED_IDS)
    written = generate_all_plans(tmp_path)
    assert len(written) == 38
    for p in written:
        text = p.read_text(encoding="utf-8")
        assert "TikTok (`short_9x16`" in text
        assert "YouTube (`long_16x9`" in text
        assert "Tối Ưu Thời Gian Sản Xuất" in text


def test_channel_plans_committed_in_repo() -> None:
    channels_dir = Path(__file__).resolve().parents[1] / "channels"
    for cid in EXPECTED_IDS:
        plan_file = channels_dir / cid / "PLAN.md"
        assert plan_file.is_file(), f"Missing {plan_file}"
        content = render_channel_plan(get_channel(cid))
        assert len(content) > 1000


def test_script_hook_scorer_distinguishes_strong_and_weak_scripts() -> None:
    strong = [
        "Vì sao bạn luôn lướt điện thoại tới 2 giờ sáng?",
        "Nhưng điều bất ngờ là não bạn không hề nghiện màn hình.",
        "Nó đang cố đòi lại tự do sau một ngày bị ép làm việc.",
        "Hiện tượng này gọi là trả thù giờ đi ngủ.",
        "Bạn có đang bị như vậy mỗi tối không, bình luận số 1 nhé?",
    ]
    res_good = score_script(strong, "nao_luoi", "short_9x16")
    assert res_good.score >= 70
    assert not res_good.needs_rewrite

    weak = [
        "Trong nghiên cứu khoa học hiện đại có rất nhiều khái niệm phức tạp cần được phân tích kỹ lưỡng qua nhiều bước dài dòng.",
        "Chúng ta sẽ cùng tìm hiểu tổng quan lịch sử phát triển của lĩnh vực này.",
    ]
    res_bad = score_script(weak, "nao_luoi", "short_9x16")
    assert res_bad.score < 60
    assert res_bad.needs_rewrite
    assert len(res_bad.suggestions) >= 3


def test_channel_metrics_kill_iterate_scale(tmp_path: Path) -> None:
    csv_path = tmp_path / "metrics.csv"
    csv_path.write_text(
        "channel_id,platform,video_id,format,views,avg_watch_pct,completion_pct,shares,new_followers,ctr_pct\n"
        "nao_luoi,tiktok,v1,short_9x16,8500,55,48,120,45,0\n"
        "tui_tien,tiktok,v2,short_9x16,700,32,28,5,2,0\n"
        "su_ke_lai,tiktok,v3,short_9x16,120,15,10,0,0,0\n"
        "su_ke_lai,tiktok,v4,short_9x16,150,18,12,0,0,0\n"
        "su_ke_lai,tiktok,v5,short_9x16,90,14,9,0,0,0\n"
        "su_ke_lai,tiktok,v6,short_9x16,110,16,11,0,0,0\n"
        "su_ke_lai,tiktok,v7,short_9x16,130,17,10,0,0,0\n"
        "su_ke_lai,tiktok,v8,short_9x16,140,15,11,0,0,0\n",
        encoding="utf-8",
    )
    rows = load_metrics(csv_path)
    verdicts = {v.channel_id: v for v in judge_all(rows)}
    assert verdicts["nao_luoi"].decision == "scale"
    assert verdicts["tui_tien"].decision == "iterate"
    assert verdicts["su_ke_lai"].decision == "kill"

    long_win = judge(
        "ho_so_ky_la",
        [VideoMetric("ho_so_ky_la", "youtube", "yt1", "long_16x9", views=2000, avg_watch_pct=42.0, ctr_pct=5.5)],
    )
    assert long_win.decision == "scale"


def test_build_channel_config_structure() -> None:
    cfg = build_channel_config(get_channel("ua_sao_vay"))
    assert cfg["git_branch"] == "channel/ua-sao-vay"
    assert cfg["platform_routing"] == {"tiktok": "short_9x16", "youtube": "long_16x9"}
    assert cfg["speed_optimization"]["spinoff_shorts_per_long"] == 6
    with pytest.raises(ValueError):
        get_channel("non_existent_channel")
    raw = json.dumps(cfg, ensure_ascii=False)
    assert "channel/ua-sao-vay" in raw


def test_ten_visual_archetypes_and_stickman_limits() -> None:
    from collections import Counter

    from channels.registry import get_visual_archetype

    all_channels = channels()
    assert len(all_channels) == 38

    upgraded_26 = {
        "luat_ngam", "ban_do_quyen_luc", "dia_com", "luat_doi_thuong", "banh_rang", "vu_tru_ti_hon", "la_ban_hoc_thuat",
        "chanh_niem_ke", "loi_sang_soi", "minh_triet_song", "tam_tinh_dem",
        "en_crowd_strings", "en_kindred_sketch", "en_first_principles", "en_wallet_anatomy",
        "en_macro_gears", "en_fine_print", "en_inside_vessel", "en_kitchen_molecules", "en_wait_how",
        "en_cold_case_ink", "en_choke_point", "en_pocket_cosmos", "en_second_arrow", "en_parable_lamp", "en_bamboo_marble",
    }
    assert len(upgraded_26) == 26

    allowed_stickman_channels = {
        "nao_luoi", "tui_tien", "ai_binh_dan", "nghe_song_sot", "en_lazy_brain", "en_plain_sight_ai", "en_career_leverage",
    }

    stickman_found = []
    archetypes = {}

    for cid, ch in all_channels.items():
        arch = get_visual_archetype(cid)
        archetypes[cid] = arch["id"]

        # Check stickman in cast_appearance
        if "stickman" in ch.visual.cast_appearance.lower():
            stickman_found.append(cid)

        # 26 upgraded channels must have ZERO stickman, bald circle head, wire arms, or Nguệch Ngoạc
        if cid in upgraded_26:
            for term in ("stickman", "bald circle head", "wire arms", "nguệch ngoạc"):
                assert term not in ch.visual.cast_appearance.lower(), f"Forbidden '{term}' in {cid}.cast_appearance"
                assert term not in ch.visual.style_description.lower(), f"Forbidden '{term}' in {cid}.style_description"

    assert len(stickman_found) <= 7
    assert set(stickman_found) == allowed_stickman_channels
    assert not any(cid in upgraded_26 for cid in stickman_found)

    # 10 Archetype balance distribution
    counts = Counter(archetypes.values())
    expected_distribution = {
        "stickman_doodle": 6,
        "noir_dossier": 4,
        "kawaii_sticker": 6,
        "pastel_duo": 2,
        "tactical_atlas": 2,
        "cosmos_vector": 2,
        "blueprint_ledger": 6,
        "editorial_risograph": 2,
        "zen_sumie": 3,
        "woodcut_gouache": 5,
    }
    assert counts == expected_distribution
    assert counts["stickman_doodle"] / 38 == pytest.approx(6 / 38, 0.001)

