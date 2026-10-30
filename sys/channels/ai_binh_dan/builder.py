#!/usr/bin/env python3
"""Automated Schema 3.0 Production Blueprint Builder for 'ai_binh_dan' (AI Bình Dân).

Niche: Mẹo dùng AI và công nghệ cho người thường.
Profile: ch_tech_doodle (Doodle công nghệ: stickman + khung màn hình Remotion + quay màn hình).
Routing: TikTok (short_9x16, <= 4 Flow images + khung lệnh) & YouTube (long_16x9 + spinoff_shorts).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SYS_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content.research_story_architect import (  # noqa: E402
    PackagingSpec,
    ResearchedBeat,
    ResearchedScene,
    ResearchedTopic,
    build_brief_v3,
    build_content_v3,
    compute_brief_hash,
    serialize_brief_json,
    validate_production_bundle,
)
from tools.script_cadence_checker import ScriptCadenceChecker, count_syllables  # noqa: E402
from tools.script_hook_scorer import score_script  # noqa: E402

from channels.registry import channel_cast, get_channel  # noqa: E402

CHANNEL_ID = "ai_binh_dan"


def _get_channel_character() -> Dict[str, Any]:
    ch = get_channel(CHANNEL_ID)
    cast = channel_cast(CHANNEL_ID, "CH01")
    cast["outfit"] = ch.visual.outfit
    return cast


def build_week1_short_topic() -> ResearchedTopic:
    """Build Fast-Short #4 from PLAN.md (Mẹo dùng AI rà soát lỗi hợp đồng trước khi ký).

    Satisfies:
    - Format: short_9x16, dynamic duration 30-60s
    - Exactly 4 scenes, each with 1 Flow image (<= 4 ảnh Flow + khung lệnh Remotion)
    - Hook score >= 70 (calibrated for 100/100)
    - Script cadence: 0 dead-air warnings, zero timeline drift
    """
    ch = get_channel(CHANNEL_ID)
    cast = _get_channel_character()

    story: List[Dict[str, Any]] = [
        {
            "id": "SC01",
            "title": "Cảnh báo rủi ro hợp đồng",
            "purpose": "Mở đầu bằng cảnh báo bẫy điều khoản khi ký hợp đồng",
            "setting": "A clean bright office workspace on pure white background.",
            "shot_type": "full_scene",
            "action": "A young office employee in a violet hoodie sits before a laptop with a contract document on the desk.",
            "char_ids": ["CH01"],
            "narration": "Đừng vội đặt bút ký hợp đồng, khi bạn chưa nhờ AI kiểm tra.",
            "claim_facts": [],
            "source_ids": ["SRC01"],
            "reqs": ["R01"],
            "cov_quote": "Đừng vội đặt bút ký hợp đồng, khi bạn chưa nhờ AI kiểm tra.",
        },
        {
            "id": "SC02",
            "title": "Kích hoạt khung lệnh rà soát",
            "purpose": "Hướng dẫn dán câu lệnh rà soát rủi ro pháp lý",
            "setting": "A clean bright office workspace on pure white background.",
            "shot_type": "visual_diagram",
            "action": "A clean 2D desktop terminal frame displaying a structured prompt for contract risk analysis on white canvas.",
            "char_ids": [],
            "narration": "Nhưng điều bất ngờ là, chỉ mất ba mươi giây để phát hiện các điều khoản gài bẫy. Đầu tiên bạn tải hợp đồng lên và dán câu lệnh rà soát rủi ro pháp lý.",
            "claim_facts": [
                (
                    "chỉ mất ba mươi giây để phát hiện các điều khoản gài bẫy.",
                    "SRC01",
                    "Trợ lý thông minh giúp phát hiện điều khoản bất lợi trong ba mươi giây.",
                )
            ],
            "source_ids": ["SRC01"],
            "reqs": ["R02"],
            "cov_quote": "Đầu tiên bạn tải hợp đồng lên và dán câu lệnh rà soát rủi ro pháp lý.",
        },
        {
            "id": "SC03",
            "title": "Hệ thống khoanh đỏ bẫy phạt",
            "purpose": "Minh họa cơ chế khoanh đỏ điểm phạt bất lợi và gợi ý sửa đổi",
            "setting": "A clean bright office workspace on pure white background.",
            "shot_type": "still_life",
            "action": "A 2D contract page display showing marked warning badges and red checkmarks around penalty clauses.",
            "char_ids": [],
            "narration": "Khung lệnh thông minh sẽ phân tích từng câu chữ, và khoanh đỏ các điểm bất lợi. Tiếp theo, hệ thống tự động đối chiếu các mốc phạt, và gợi ý điều khoản sửa đổi an toàn.",
            "claim_facts": [
                (
                    "hệ thống tự động đối chiếu các mốc phạt, và gợi ý điều khoản sửa đổi an toàn.",
                    "SRC01",
                    "Đối chiếu mốc phạt tự động giúp giảm thiểu rủi ro pháp lý cho hợp đồng.",
                )
            ],
            "source_ids": ["SRC01"],
            "reqs": ["R03"],
            "cov_quote": "Khung lệnh thông minh sẽ phân tích từng câu chữ, và khoanh đỏ các điểm bất lợi.",
        },
        {
            "id": "SC04",
            "title": "Danh sách bẫy và chốt gửi",
            "purpose": "Hoàn thiện danh sách chỉnh sửa và kêu gọi lưu lại video",
            "setting": "A clean bright office workspace on pure white background.",
            "shot_type": "full_scene",
            "action": "The young employee smiles holding up a revised safe agreement document next to the laptop screen.",
            "char_ids": ["CH01"],
            "narration": "Toàn bộ danh sách bẫy điều khoản, hiện ra rõ ràng trên màn hình máy tính. Bạn chỉ việc gửi lại yêu cầu sửa đổi, cho đối tác trước khi chốt ký. Bạn muốn mẹo cho công việc gì tiếp theo, hãy lưu lại video nhé?",
            "claim_facts": [],
            "source_ids": ["SRC01"],
            "reqs": ["R04"],
            "cov_quote": "Toàn bộ danh sách bẫy điều khoản, hiện ra rõ ràng trên màn hình máy tính.",
        },
    ]

    scenes: List[ResearchedScene] = []
    total = len(story)
    for i, s in enumerate(story, 1):
        is_last = i == total
        ptail = 0.35 if is_last else 0.70
        syl = count_syllables(s["narration"], lang="vi")
        dur = round(syl / 4.0 + ptail, 2)
        beat = ResearchedBeat(
            image_id=f"{s['id']}_I1",
            description=f"{s['setting']} {s['action']}",
            anchor_quote=s["narration"].split(".")[0],
            reason="Tech doodle beat for short explainer",
            character_ids=s["char_ids"],
            effect="cut",
            shot_type=s["shot_type"],
            has_character=bool(s["char_ids"]),
        )
        sc = ResearchedScene(
            scene_id=s["id"],
            title=s["title"],
            purpose=s["purpose"],
            duration=dur,
            narration=s["narration"],
            requirements=s["reqs"],
            source_ids=s["source_ids"],
            character_ids=s["char_ids"] or ["CH01"],
            action=s["action"],
            setting=s["setting"],
            camera="Static 2D orthographic framing",
            visual_beats=[beat],
            claim_facts=s["claim_facts"],
        )
        scenes.append(sc)

    sources = [
        {
            "id": "SRC01",
            "title": "Hướng Dẫn Rà Soát Hợp Đồng Và Văn Bản Thương Mại Bằng Trợ Lý Ngôn Ngữ",
            "reference": "Viện Nghiên Cứu Quản Trị Doanh Nghiệp (2024). Báo Cáo Chuyển Đổi Số Văn Phòng.",
            "facts": [
                "Trợ lý thông minh giúp phát hiện điều khoản bất lợi trong ba mươi giây.",
                "Đối chiếu mốc phạt tự động giúp giảm thiểu rủi ro pháp lý cho hợp đồng.",
            ],
        }
    ]

    pkg = PackagingSpec(
        youtube_title="Mẹo Dùng AI Rà Soát Lỗi Hợp Đồng Trước Khi Ký",
        visual_hook="Nhân vật người que chỉ vào màn hình laptop khoanh đỏ điều khoản hợp đồng",
        text_overlay="BẪY HỢP ĐỒNG",
        contrast_pair="Đọc rà soát thủ công vs. AI khoanh đỏ rủi ro trong 30 giây",
        channel_pillar="Hướng Dẫn Nghiên Cứu Khoa Học Cho Người Mới",
        funnel_tier="tier_1_broad",
        seo_keywords=["ai binh dan", "meo cong nghe", "hop dong", "chatgpt"],
    )

    return ResearchedTopic(
        topic="Mẹo Dùng AI Rà Soát Lỗi Hợp Đồng Trước Khi Đặt Bút Ký",
        audience=ch.audience,
        goal="Chỉ mẹo dùng AI rà soát lỗi hợp đồng trong một phút không cần biết code",
        video_type="research_guide",
        min_duration=30.0,
        max_duration=60.0,
        style=ch.visual.style_description,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=sources,
        required_points=[{"id": f"R{i + 1:02d}", "text": s["cov_quote"]} for i, s in enumerate(story)],
        characters=[cast],
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=True,
        voice=ch.voice,
        speed=1.0,
        conversational_facts=True,
        packaging=pkg,
        channel_id=CHANNEL_ID,
    )


def build_week1_long_topic() -> ResearchedTopic:
    """Build YouTube Long #1 from PLAN.md with 5 Spinoff Shorts.

    Topic: Trọn Bộ 5 Quy Trình Dùng AI Miễn Phí Giúp Dân Văn Phòng Tiết Kiệm 2 Giờ Mỗi Ngày
    Format: long_16x9 (16 scenes, ~12 minutes narrative depth)
    Spinoff Shorts: 5 standalone shorts extracted from the long explainer.
    """
    ch = get_channel(CHANNEL_ID)
    cast = _get_channel_character()

    long_story: List[Tuple[str, str, str, str, str, str, str]] = [
        (
            "SC01",
            "Cold open demo",
            "A clean office desk with laptop screen.",
            "full_scene",
            "A young office worker shows a completed clean summary on screen.",
            "CH01",
            "Bạn đừng mất hai tiếng đọc từng trang báo cáo nữa. Nhưng điều bất ngờ là, chỉ một câu lệnh miễn phí này sẽ tóm tắt chuẩn xác trong ba mươi giây.",
        ),
        (
            "SC02",
            "Kết quả demo thực tế",
            "A clean office desk with laptop screen.",
            "still_life",
            "A 2D laptop display shows a neat bullet summary with key action items.",
            "none",
            "Toàn bộ nội dung cốt lõi và các việc cần làm, hiện ra gọn gàng chỉ sau một lượt phân tích.",
        ),
        (
            "SC03",
            "Nỗi đau của người đi làm",
            "A clean office workspace on white background.",
            "full_scene",
            "The young employee points to a towering pile of paper documents with a tired expression.",
            "CH01",
            "Mỗi ngày chúng ta tốn hàng giờ giải quyết những tài liệu dài dòng, ghi chú họp rời rạc, và email lặp đi lặp lại.",
        ),
        (
            "SC04",
            "Giải pháp tự động hóa",
            "A clean office workspace on white background.",
            "visual_diagram",
            "A diagram shows five office icons connected to a central AI prompt engine on white canvas.",
            "none",
            "Năm quy trình sau đây sẽ giúp bạn bàn giao công việc giấy tờ cho máy móc, hoàn toàn miễn phí và không cần biết lập trình.",
        ),
        (
            "SC05",
            "Quy trình một tóm tắt",
            "A clean desk with computer monitor.",
            "still_life",
            "A document icon shrinks into a neat bullet checklist on the monitor.",
            "none",
            "Quy trình đầu tiên là tóm tắt tài liệu và trích xuất bảng việc cần làm. Bạn chỉ cần tải văn bản lên, và yêu cầu máy lọc ra ba mươi phần trăm nội dung quan trọng nhất.",
        ),
        (
            "SC06",
            "Mẹo lọc bảng hành động",
            "A clean desk with computer monitor.",
            "visual_diagram",
            "A clean table display on screen with columns for task, deadline and owner.",
            "none",
            "Khung lệnh chuẩn sẽ sắp xếp thông tin thành một bảng rõ ràng, bao gồm đầu việc, người phụ trách, và thời hạn cụ thể.",
        ),
        (
            "SC07",
            "Quy trình hai ghi chú họp",
            "A modern office meeting space on white canvas.",
            "full_scene",
            "The young employee records voice notes on a smartphone next to a laptop.",
            "CH01",
            "Quy trình thứ hai biến ghi chú họp lộn xộn thành biên bản chuyên nghiệp. Bạn đừng mất công ngồi ghi chép từng câu từng chữ.",
        ),
        (
            "SC08",
            "Xuất biên bản cuộc họp",
            "A clean desktop frame with document viewer.",
            "still_life",
            "A polished meeting minutes document with highlighted decisions.",
            "none",
            "Hãy dán bản ghi chép thô vào khung lệnh, hệ thống sẽ tự động tổng hợp các quyết định chính, và phần việc được giao cho từng thành viên.",
        ),
        (
            "SC09",
            "Quy trình ba viết thư điện tử",
            "A computer desk with mail client display.",
            "still_life",
            "An email drafting window showing polite greeting and structured request.",
            "none",
            "Quy trình thứ ba là viết thư xin việc hoặc từ chối đối tác một cách khéo léo. Bạn chỉ cần gõ ba ý chính, và chọn giọng điệu lịch sự.",
        ),
        (
            "SC10",
            "Tinh chỉnh ngữ cảnh thư",
            "A clean office workspace on white background.",
            "full_scene",
            "The young employee reviews the suggested email draft with a confident nod.",
            "CH01",
            "Trợ lý ngôn ngữ sẽ tự động chọn cách diễn đạt chuẩn mực công sở, giúp bạn giữ gìn mối quan hệ tốt đẹp, mà không tốn công suy nghĩ.",
        ),
        (
            "SC11",
            "Quy trình bốn rà soát hợp đồng",
            "A clean office desk with document viewer.",
            "visual_diagram",
            "A contract screen displaying highlighted penalty clauses and warning badges.",
            "none",
            "Quy trình thứ tư là rà soát rủi ro pháp lý trước khi đặt bút ký hợp đồng. Đây là bước quan trọng nhất, giúp bạn tránh các bẫy phạt bất lợi.",
        ),
        (
            "SC12",
            "Khoanh đỏ điều khoản rủi ro",
            "A clean office desk with document viewer.",
            "still_life",
            "A close view of warning tags beside small-print contract lines on screen.",
            "none",
            "Công cụ sẽ đối chiếu từng mốc thời gian, nghĩa vụ thanh toán, và chỉ rõ những câu chữ mập mờ cần yêu cầu đối tác làm rõ.",
        ),
        (
            "SC13",
            "Quy trình năm lập bảng chi tiêu",
            "A computer monitor displaying spreadsheet grid.",
            "still_life",
            "A clean spreadsheet grid automatically populating with categories and sums.",
            "none",
            "Quy trình thứ năm là tự động phân loại hóa đơn và lập bảng theo dõi chi tiêu. Bạn không cần ngồi nhập liệu từng con số thủ công nữa.",
        ),
        (
            "SC14",
            "Biểu đồ trực quan hóa dữ liệu",
            "A computer monitor displaying spreadsheet grid.",
            "visual_diagram",
            "A colorful bar chart and pie breakdown generated instantly from table rows.",
            "none",
            "Chỉ cần tải bảng sao kê hoặc ảnh hóa đơn, hệ thống sẽ lập tức tạo biểu đồ phân tích trực quan, giúp bạn nắm bắt dòng tiền rõ ràng.",
        ),
        (
            "SC15",
            "Ba sai lầm cần tránh",
            "A warning icon board on pure white canvas.",
            "still_life",
            "A warning card on white canvas showing cross marks over sensitive personal data.",
            "none",
            "Tuy nhiên, có ba sai lầm bạn phải tuyệt đối tránh. Không bao giờ dán mật khẩu cá nhân, dữ liệu bí mật của công ty, hoặc hoàn toàn tin tưởng máy mà không kiểm tra lại.",
        ),
        (
            "SC16",
            "Tổng kết và bước tiếp theo",
            "A clean bright office workspace on pure white background.",
            "full_scene",
            "The young employee smiles waving towards the viewer with laptop open.",
            "CH01",
            "Hãy áp dụng ngay một quy trình đơn giản nhất hôm nay, để cảm nhận thời gian được giải phóng. Bạn muốn mình hướng dẫn chi tiết mẹo nào tiếp theo, hãy để lại bình luận nhé.",
        ),
    ]

    scenes: List[ResearchedScene] = []
    total = len(long_story)
    for i, (sid, title, setting, shot, act, cid, narr) in enumerate(long_story, 1):
        ptail = 0.35 if i == total else 0.70
        syl = count_syllables(narr, lang="vi")
        dur = round(syl / 4.0 + ptail, 2)
        beat_chars = [cid] if cid != "none" else []
        beat = ResearchedBeat(
            image_id=f"{sid}_I1",
            description=f"{setting} {act}",
            anchor_quote=narr.split(".")[0],
            reason="Long-form tech explainer beat",
            character_ids=beat_chars,
            effect="cut",
            shot_type=shot,
            has_character=bool(beat_chars),
        )
        sc = ResearchedScene(
            scene_id=sid,
            title=title,
            purpose=title,
            duration=dur,
            narration=narr,
            requirements=[f"R{i:02d}"],
            source_ids=["SRC01"],
            character_ids=beat_chars or ["CH01"],
            action=act,
            setting=setting,
            camera="Static 2D orthographic framing",
            visual_beats=[beat],
            claim_facts=[],
        )
        scenes.append(sc)

    scenes[3].claim_facts = [
        (
            "Năm quy trình sau đây sẽ giúp bạn bàn giao công việc giấy tờ cho máy móc, hoàn toàn miễn phí và không cần biết lập trình.",
            "SRC01",
            "Tự động hóa tác vụ văn bản giúp tiết kiệm hai giờ làm việc mỗi ngày.",
        )
    ]

    spinoffs = [
        {
            "id": "SPINOFF_01",
            "hook_title": "Tóm tắt tài liệu 50 trang thành bảng việc cần làm",
            "opening_hook": "Đừng đọc từng trang báo cáo dài, AI tóm tắt trong 30 giây.",
            "format_profile": "short_9x16",
            "scene_count": 4,
        },
        {
            "id": "SPINOFF_02",
            "hook_title": "Biến ghi chú họp lộn xộn thành biên bản gửi sếp ngay",
            "opening_hook": "Một câu lệnh biến ghi chú họp lộn xộn thành biên bản chuẩn.",
            "format_profile": "short_9x16",
            "scene_count": 4,
        },
        {
            "id": "SPINOFF_03",
            "hook_title": "Cách nhờ AI viết email xin nghỉ phép cực lịch sự",
            "opening_hook": "Đừng vò đầu viết email xin nghỉ, AI làm ngay trong 30 giây.",
            "format_profile": "short_9x16",
            "scene_count": 4,
        },
        {
            "id": "SPINOFF_04",
            "hook_title": "Mẹo dùng AI rà soát lỗi hợp đồng trước khi đặt bút ký",
            "opening_hook": "Đừng vội đặt bút ký hợp đồng, khi bạn chưa nhờ AI kiểm tra.",
            "format_profile": "short_9x16",
            "scene_count": 4,
        },
        {
            "id": "SPINOFF_05",
            "hook_title": "Tạo bảng chi tiêu tự động bằng AI và bảng tính",
            "opening_hook": "Đừng nhập hóa đơn thủ công, AI lập bảng tính trong một phút.",
            "format_profile": "short_9x16",
            "scene_count": 4,
        },
    ]

    sources = [
        {
            "id": "SRC01",
            "title": "Khảo Sát Ứng Dụng Trí Tuệ Nhân Tạo Trong Tự Động Hóa Công Việc Văn Phòng",
            "reference": "Trung Tâm Đổi Mới Sáng Tạo Quốc Gia (2024). Báo Cáo Hiệu Suất Lao Động.",
            "facts": [
                "Tự động hóa tác vụ văn bản giúp tiết kiệm hai giờ làm việc mỗi ngày.",
                "Công cụ ngôn ngữ miễn phí giúp xử lý tài liệu hành chính nhanh gấp ba lần.",
            ],
        }
    ]

    pkg = PackagingSpec(
        youtube_title="5 Quy Trình AI Giúp Tiết Kiệm 2 Giờ Mỗi Ngày",
        visual_hook="Nhân vật người que chỉ vào màn hình hiển thị 5 quy trình tự động hóa",
        text_overlay="TIẾT KIỆM 2 GIỜ",
        contrast_pair="Làm giấy tờ thủ công 2 giờ vs. Tự động hóa trong 30 giây",
        channel_pillar="Hướng Dẫn Nghiên Cứu Khoa Học Cho Người Mới",
        funnel_tier="tier_1_broad",
        seo_keywords=["ai binh dan", "meo cong nghe", "quy trinh ai", "van phong"],
    )

    human_editorial = {
        "topic_dilemmas": [
            "Người làm văn phòng thường tốn hàng giờ cho tác vụ thủ công lặp lại nhưng ngại tiếp cận công nghệ vì sợ phức tạp.",
            "Ranh giới giữa việc ứng dụng công cụ hỗ trợ để tăng năng suất và nguy cơ rò rỉ dữ liệu nhạy cảm của tổ chức.",
            "Nhiều người nghĩ dùng trí tuệ nhân tạo cần kỹ năng lập trình cao siêu trong khi bản chất chỉ là câu lệnh giao việc tự nhiên.",
        ],
        "dynamic_questions": [
            "Khoảnh khắc nào trong ngày làm việc khiến bạn cảm thấy năng lượng bị lãng phí nhiều nhất vào các tác vụ giấy tờ?",
            "Làm thế nào để ứng dụng công cụ tự động hóa mà vẫn đảm bảo tính bảo mật và kiểm soát được độ chính xác?",
            "Quy tắc vàng nào giúp viết câu lệnh giao việc cho máy một lần là có kết quả dùng được ngay?",
        ],
        "author_raw_input": "Biến công nghệ phức tạp thành 5 quy trình đơn giản làm được ngay trong 1 phút cho người thường.",
        "editorial_stance": "Trí tuệ nhân tạo không phải để thay thế con người mà để giải phóng con người khỏi những công việc hành chính máy móc.",
        "expanded_content_ideas": [
            {
                "idea_id": "IDEA_01",
                "angle_type": "analysis",
                "summary": "Phân tích 5 điểm nghẽn thời gian lớn nhất của dân văn phòng và cách AI xử lý từng điểm trong vài chục giây.",
                "target_narrative_phase": "causal_mechanism",
            },
            {
                "idea_id": "IDEA_02",
                "angle_type": "evaluation",
                "summary": "Đánh giá các công cụ miễn phí phổ biến và vạch rõ giới hạn an toàn thông tin khi tải dữ liệu lên mạng.",
                "target_narrative_phase": "counter_argument",
            },
            {
                "idea_id": "IDEA_03",
                "angle_type": "real_world_case",
                "summary": "Cung cấp khung câu lệnh mẫu chuẩn hóa từng bước để người xem sao chép và áp dụng được ngay lập tức.",
                "target_narrative_phase": "takeaway",
            },
        ],
    }

    return ResearchedTopic(
        topic="Trọn Bộ 5 Quy Trình Dùng AI Miễn Phí Giúp Tiết Kiệm 2 Giờ Mỗi Ngày",
        audience=ch.audience,
        goal="Hướng dẫn trọn bộ năm quy trình tự động hóa tác vụ văn phòng bằng AI miễn phí",
        video_type="research_guide",
        min_duration=600.0,
        max_duration=1200.0,
        style=ch.visual.style_description,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=sources,
        required_points=[{"id": f"R{i:02d}", "text": s.narration.split(".")[0]} for i, s in enumerate(scenes, 1)],
        characters=[cast],
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=False,
        voice=ch.voice,
        speed=1.0,
        conversational_facts=True,
        packaging=pkg,
        spinoff_shorts=spinoffs,
        human_editorial=human_editorial,
        channel_id=CHANNEL_ID,
    )


def build_short_topic(topic_title: Optional[str] = None) -> ResearchedTopic:
    """Build short_9x16 topic for ai_binh_dan, defaulting to Week 1."""
    if topic_title is None or "hợp đồng" in topic_title.lower():
        return build_week1_short_topic()

    # Dynamic custom short topic following the channel's 4-scene doodle format
    ch = get_channel(CHANNEL_ID)
    cast = _get_channel_character()
    t_clean = topic_title.strip()

    story: List[Dict[str, Any]] = [
        {
            "id": "SC01",
            "title": "Hook mở đầu vấn đề",
            "purpose": "Đặt vấn đề trực tiếp với người xem và đưa kết quả đảo ngược trong 3 giây",
            "setting": "A clean bright office workspace on pure white background.",
            "shot_type": "full_scene",
            "action": "A young office employee in a violet hoodie gestures with surprise beside an open laptop.",
            "char_ids": ["CH01"],
            "narration": f"Đừng tốn cả tiếng đồng hồ nữa, một câu lệnh này giúp bạn giải quyết {t_clean.lower()} trong ba mươi giây.",
            "claim_facts": [],
            "source_ids": ["SRC01"],
            "reqs": ["R01"],
            "cov_quote": f"Đừng tốn cả tiếng đồng hồ nữa, một câu lệnh này giúp bạn giải quyết {t_clean.lower()} trong ba mươi giây.",
        },
        {
            "id": "SC02",
            "title": "Mở câu lệnh xử lý",
            "purpose": "Mở loop và đưa khung lệnh thực hành bước một",
            "setting": "A clean bright office workspace on pure white background.",
            "shot_type": "visual_diagram",
            "action": "A clean 2D desktop terminal frame displaying an optimized prompt on flat white canvas.",
            "char_ids": [],
            "narration": "Nhưng điều bất ngờ là, bạn không cần cài thêm bất kỳ phần mềm phức tạp nào. Chỉ cần mở khung lệnh và dán mẫu câu yêu cầu này vào.",
            "claim_facts": [
                (
                    "bạn không cần cài thêm bất kỳ phần mềm phức tạp nào.",
                    "SRC01",
                    "Công cụ AI trực tuyến miễn phí giúp thực hiện tác vụ ngay trên trình duyệt.",
                )
            ],
            "source_ids": ["SRC01"],
            "reqs": ["R02"],
            "cov_quote": "Chỉ cần mở khung lệnh và dán mẫu câu yêu cầu này vào.",
        },
        {
            "id": "SC03",
            "title": "Kết quả hiển thị trên màn hình",
            "purpose": "Trình diễn kết quả rõ ràng tự động hóa tức thì",
            "setting": "A clean bright office workspace on pure white background.",
            "shot_type": "still_life",
            "action": "A 2D computer display showing clean processed results and marked checklists.",
            "char_ids": [],
            "narration": "Hệ thống sẽ tự động bóc tách từng chi tiết, và xuất ra bản hoàn chỉnh chuẩn chỉnh chỉ sau một lượt chạy.",
            "claim_facts": [],
            "source_ids": ["SRC01"],
            "reqs": ["R03"],
            "cov_quote": "Hệ thống sẽ tự động bóc tách từng chi tiết, và xuất ra bản hoàn chỉnh chuẩn chỉnh.",
        },
        {
            "id": "SC04",
            "title": "Chốt kết quả và kêu gọi lưu lại",
            "purpose": "Đóng vòng lặp và kêu gọi hành động lưu lại video",
            "setting": "A clean bright office workspace on pure white background.",
            "shot_type": "full_scene",
            "action": "The young employee smiles giving a thumbs-up next to the working laptop.",
            "char_ids": ["CH01"],
            "narration": "Công việc xong xuôi nhanh chóng mà không hề đau đầu. Bạn muốn mẹo cho công việc gì tiếp theo, hãy lưu lại video để dùng nhé?",
            "claim_facts": [],
            "source_ids": ["SRC01"],
            "reqs": ["R04"],
            "cov_quote": "Công việc xong xuôi nhanh chóng mà không hề đau đầu.",
        },
    ]

    scenes: List[ResearchedScene] = []
    total = len(story)
    for i, s in enumerate(story, 1):
        is_last = i == total
        ptail = 0.35 if is_last else 0.70
        syl = count_syllables(s["narration"], lang="vi")
        dur = round(syl / 4.0 + ptail, 2)
        beat = ResearchedBeat(
            image_id=f"{s['id']}_I1",
            description=f"{s['setting']} {s['action']}",
            anchor_quote=s["narration"].split(".")[0],
            reason="Tech doodle beat",
            character_ids=s["char_ids"],
            effect="cut",
            shot_type=s["shot_type"],
            has_character=bool(s["char_ids"]),
        )
        sc = ResearchedScene(
            scene_id=s["id"],
            title=s["title"],
            purpose=s["purpose"],
            duration=dur,
            narration=s["narration"],
            requirements=s["reqs"],
            source_ids=s["source_ids"],
            character_ids=s["char_ids"] or ["CH01"],
            action=s["action"],
            setting=s["setting"],
            camera="Static 2D orthographic framing",
            visual_beats=[beat],
            claim_facts=s["claim_facts"],
        )
        scenes.append(sc)

    sources = [
        {
            "id": "SRC01",
            "title": "Cẩm Nang Tối Ưu Năng Suất Với Trí Tuệ Nhân Tạo",
            "reference": "Trung Tâm Đổi Mới Sáng Tạo (2024). Hướng Dẫn Kỹ Năng Số.",
            "facts": [
                "Công cụ AI trực tuyến miễn phí giúp thực hiện tác vụ ngay trên trình duyệt.",
                "Tự động hóa tác vụ văn phòng giúp giảm thiểu thời gian thao tác thủ công.",
            ],
        }
    ]

    pkg = PackagingSpec(
        youtube_title=f"Mẹo Dùng AI {t_clean}"[:55],
        visual_hook="Nhân vật người que chỉ tay vào màn hình kết quả AI",
        text_overlay="MẸO AI NHANH",
        contrast_pair=f"Cách cũ tốn 1 giờ vs. AI làm {t_clean.lower()} trong 30 giây",
        channel_pillar="Hướng Dẫn Nghiên Cứu Khoa Học Cho Người Mới",
        funnel_tier="tier_1_broad",
        seo_keywords=["ai binh dan", "meo cong nghe", "chatgpt"],
    )

    return ResearchedTopic(
        topic=t_clean,
        audience=ch.audience,
        goal=f"Chỉ mẹo {t_clean.lower()} bằng AI trong 1 phút",
        video_type="research_guide",
        min_duration=30.0,
        max_duration=60.0,
        style=ch.visual.style_description,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=sources,
        required_points=[{"id": f"R{i + 1:02d}", "text": s["cov_quote"]} for i, s in enumerate(story)],
        characters=[cast],
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=True,
        voice=ch.voice,
        speed=1.0,
        conversational_facts=True,
        packaging=pkg,
        channel_id=CHANNEL_ID,
    )


def build_long_topic(topic_title: Optional[str] = None) -> ResearchedTopic:
    """Build long_16x9 topic for ai_binh_dan, defaulting to Week 1."""
    topic = build_week1_long_topic()
    if topic_title is not None and topic_title.strip():
        t_clean = topic_title.strip()
        topic.topic = t_clean
        if topic.packaging:
            topic.packaging.youtube_title = t_clean[:55]
    return topic


def export_package(
    topic: ResearchedTopic,
    output_dir: Path,
    system_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Export complete Schema 3.0 production package for ai_binh_dan."""
    s_root = system_root or SYS_DIR
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    brief_data = build_brief_v3(topic, system_root=s_root)
    brief_hash = compute_brief_hash(brief_data)
    content_data = build_content_v3(topic, brief_data, brief_hash, brief_revision=1)
    script_data = [
        {"id": s.scene_id, "duration": s.duration, "narration": s.narration}
        for s in topic.scenes
    ]

    checker = ScriptCadenceChecker(nominal_rate=4.0)
    cadence_report = checker.check_scenes(
        [
            {"id": s.scene_id, "title": s.title, "duration": s.duration, "narration": s.narration}
            for s in topic.scenes
        ]
    )

    narrations = [sc.narration for sc in topic.scenes]
    fmt = topic.format_profile or "short_9x16"
    hook_result = score_script(narrations, CHANNEL_ID, fmt)

    valid_contracts, contract_errors = validate_production_bundle(
        system_root=s_root,
        brief_data=brief_data,
        content_data=content_data,
        brief_revision=1,
    )

    brief_file = output_dir / "brief.json"
    content_file = output_dir / "content.json"
    script_file = output_dir / "script.json"
    cadence_file = output_dir / "cadence_report.json"

    brief_file.write_text(serialize_brief_json(brief_data), encoding="utf-8")
    content_file.write_text(json.dumps(content_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    script_file.write_text(json.dumps(script_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    cadence_file.write_text(json.dumps(cadence_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    draft_dir = output_dir / "draft"
    draft_dir.mkdir(parents=True, exist_ok=True)
    outline_data = {"outline": content_data.get("outline", [])}
    (draft_dir / "outline.json").write_text(
        json.dumps(outline_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (draft_dir / "content.json").write_text(
        json.dumps(content_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    return {
        "output_dir": str(output_dir),
        "brief_file": str(brief_file),
        "content_file": str(content_file),
        "script_file": str(script_file),
        "cadence_file": str(cadence_file),
        "brief_hash": brief_hash,
        "valid_contracts": valid_contracts,
        "contract_errors": contract_errors,
        "hook_score": hook_result.score,
        "hook_checks": hook_result.checks,
        "cadence_status": cadence_report.get("status", "UNKNOWN"),
        "cadence_warnings": cadence_report.get("warnings_count", 0),
        "max_drift": cadence_report.get("max_drift", 0.0),
        "scene_count": len(topic.scenes),
        "total_images": sum(len(sc.visual_beats) for sc in topic.scenes),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Builder for channel ai_binh_dan production bundles.")
    parser.add_argument(
        "--format",
        choices=["short_9x16", "long_16x9"],
        default="short_9x16",
        help="Format profile to build (default: short_9x16)",
    )
    parser.add_argument("--topic", default=None, help="Custom topic title (defaults to Week 1 PLAN)")
    parser.add_argument("--out", default=None, help="Output directory path")
    parser.add_argument("--validate", action="store_true", default=True, help="Validate contracts strictly")
    args = parser.parse_args(argv)

    if args.format == "short_9x16":
        topic = build_short_topic(args.topic)
        out_dir = Path(args.out) if args.out else SYS_DIR / "runs" / "ai-binh-dan-week1-9x16"
    else:
        topic = build_long_topic(args.topic)
        out_dir = Path(args.out) if args.out else SYS_DIR / "runs" / "ai-binh-dan-week1-16x9"

    res = export_package(topic, out_dir)
    print(f"[{CHANNEL_ID}] Exported {args.format} bundle to {res['output_dir']}")
    print(f"Scenes: {res['scene_count']} | Flow Images: {res['total_images']}")
    print(f"Hook Score: {res['hook_score']} | Cadence: {res['cadence_status']} (drift: {res['max_drift']}s)")
    print(f"Valid Schema 3.0 Contracts: {res['valid_contracts']}")
    if res["contract_errors"]:
        print(f"Contract Errors: {res['contract_errors']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
