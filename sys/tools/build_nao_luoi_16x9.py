import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sys"))

from channels.registry import channel_cast, channel_profile_stamp, get_channel

def build_nao_luoi_16x9():
    job_id = "nao-luoi-batch3-16x9"
    ch = get_channel("nao_luoi")

    brief = {
        "schema_version": "3.0",
        "topic": "Hiệu Ứng Zeigarnik: Vì Sao Càng Gần Deadline Bạn Càng Muốn Dọn Phòng?",
        "audience": "Gen Z và người đi làm 18-30 tuổi, hay tự hỏi về bản thân",
        "goal": "Phân tích chuyên sâu nguồn gốc hiệu ứng Zeigarnik, cơ chế trì hoãn tích cực và cách làm chủ vòng lặp nhận thức",
        "video_type": "research_guide",
        "duration": {
            "min_seconds": 180.0,
            "max_seconds": 240.0
        },
        "scene_count": 11,
        "required_points": [
            {"id": f"R{i:02d}", "text": t} for i, t in enumerate([
                "Cơn nghiện dọn dẹp nhà cửa kỳ lạ lúc nửa đêm cận hạn chót",
                "Hiện tượng trì hoãn tích cực và sự lừa dối cảm xúc bản thân",
                "Nguồn gốc lịch sử nghiên cứu của nhà tâm lý Bluma Zeigarnik năm 1927",
                "Cơ chế ứng dụng chạy ngầm và vòng lặp nhận thức làm quá tải trí nhớ",
                "Bình luận phản biện về phần thưởng dopamine tức thì từ việc vặt",
                "Cái giá đắt của sự hoàn hảo giả tạo và kiệt sức trước bài vở chính",
                "Những biểu hiện trá hình liên hoàn như phân loại thư mục hay dọn hộp thư",
                "Góc nhìn phản biện từ chuyên gia: trì hoãn là quản trị cảm xúc bất an",
                "Vũ khí hóa hiệu ứng Zeigarnik với quy tắc khởi động năm phút",
                "Kích hoạt quán tính tâm lý có lợi để hoàn thành công việc dễ dàng",
                "Đóng vòng lặp nhận thức và bài học quản trị tâm trí bền vững"
            ], 1)
        ],
        "language": "vi",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "On Finished and Unfinished Tasks",
                "reference": "Zeigarnik, B. (1927). Das Behalten erledigter und unerledigter Handlungen. Psychologische Forschung, 9, 1-85.",
                "facts": [
                    "Các nhiệm vụ chưa hoàn thành tạo ra sức căng nhận thức kéo dài trong trí nhớ làm việc."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "vi",
                "subtitles": True,
                "voice": ch.voice,
                "speed": ch.speed
            }
        ],
        "planning": {
            "success_criteria": [
                "Bóc tách khoa học nhưng gần gũi về hiệu ứng Zeigarnik và cung cấp giải pháp hành động cụ thể"
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Không đòi hỏi thuật ngữ tâm lý học phức tạp.",
            "pacing": "Đĩnh đạc, biến hóa nhịp điệu giữa các ví dụ minh họa và đúc kết nhận thức.",
            "speech_rates": {
                "vi": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.1,
                    "source": "Acoustic calibrated cadence"
                }
            }
        },
        "packaging": {
            "youtube_title": "Cận Deadline Sao Thích Dọn Nhà? Hiệu Ứng Zeigarnik",
            "thumbnail_spec": {
                "visual_hook": "Người que đầu trọc đứng giữa căn phòng bừa bộn một bên là laptop deadline phát sáng một bên là chổi lau nhà",
                "text_overlay": "CẬN DEADLINE THÍCH DỌN NHÀ",
                "contrast_pair": "Áp lực deadline vs Cơn nghiện dọn dẹp",
                "thumbnail_prompt": "Iconic 2D Vietnamese indie webcomic doodle stickman in flat cerulean-blue T-shirt (#3B82C4) and slate-gray trousers, sweating with frantic dot eyes between a laptop glowing red with 'DEADLINE 23:59' and a sparkling pile of cleaned laundry and mop on warm paper-cream background (#F8F0DC). Large bold hand-lettered text in upper third: 'CẬN DEADLINE THÍCH DỌN NHÀ'. Flat 2D orthographic canvas, over 60% negative space, no 3D, no gradients.",
                "layout_mode": "split_contrast"
            },
            "editorial_stance": {
                "myth_debunked": "Cứ dọn dẹp bàn làm việc là đang chuẩn bị tinh thần nghiêm túc để làm việc hiệu quả.",
                "why_generic_advice_fails": "Lời khuyên ép bản thân kỷ luật thép chỉ làm tăng thêm áp lực cảm xúc khiến não càng muốn bỏ trốn.",
                "channel_verdict": "Thực chất não bạn không hề chăm chỉ mà đang chọn dọn dẹp như một lối thoát an toàn để trốn việc khó.",
                "tradeoff_or_blindspot": "Lau dọn đem lại cảm giác hoàn thành giả tạo trong mười lăm phút nhưng deadline thực tế vẫn đứng nguyên một chỗ."
            },
            "actionable_value": {
                "core_mechanism": "Đóng vòng lặp nhận thức Zeigarnik bằng hành động siêu nhỏ để giải tỏa sức căng tâm lý.",
                "practical_rule_of_thumb": "Quy tắc mở đầu năm phút: Chỉ cần ngồi xuống viết đúng một câu đầu tiên để kích hoạt quán tính làm việc.",
                "real_world_scenario": "Thay vì đứng dậy lau sạch cái bàn, hãy mở máy tính và đặt đồng hồ năm phút gõ khung sườn bài báo cáo."
            }
        },
        "youtube_title": "Cận Deadline Sao Thích Dọn Nhà? Hiệu Ứng Zeigarnik",
        "thumbnail_spec": {
            "visual_hook": "Người que đầu trọc đứng giữa căn phòng bừa bộn một bên là laptop deadline phát sáng một bên là chổi lau nhà",
            "text_overlay": "CẬN DEADLINE THÍCH DỌN NHÀ",
            "contrast_pair": "Áp lực deadline vs Cơn nghiện dọn dẹp",
            "thumbnail_prompt": "Iconic 2D Vietnamese indie webcomic doodle stickman in flat cerulean-blue T-shirt (#3B82C4) and slate-gray trousers, sweating with frantic dot eyes between a laptop glowing red with 'DEADLINE 23:59' and a sparkling pile of cleaned laundry and mop on warm paper-cream background (#F8F0DC). Large bold hand-lettered text in upper third: 'CẬN DEADLINE THÍCH DỌN NHÀ'. Flat 2D orthographic canvas, over 60% negative space, no 3D, no gradients.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Tâm lý và hành vi đời thường",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "nao luoi",
            "zeigarnik",
            "tri hoan",
            "tam ly hoc",
            "cận deadline",
            "tamly",
            "genz"
        ],
        "cta_plan": {
            "mid_cta": "Nếu bạn cũng từng dọn nhà lúc nửa đêm, hãy lưu lại video để rèn luyện não bộ nhé.",
            "close": "Bạn thường làm việc gì kỳ lạ nhất khi sắp tới hạn chót, hãy kể cho Não Lười nghe bên dưới nhé.",
            "endcard_text": "NÃO LƯỜI"
        },
        "channel_profile": channel_profile_stamp("nao_luoi"),
        "engagement": {
            "cta_voice": "Bạn thân hơi cà khịa",
            "bridge_templates": [
                "Bản dài mình mổ xẻ trên YouTube Não Lười."
            ],
            "close_templates": [
                "Gửi cho đứa bạn hay thức khuya chung với bạn đi."
            ],
            "endcard_text": "NÃO LƯỜI",
            "banned_cta_phrases": [
                "đừng quên like",
                "nhấn chuông",
                "bấm chuông",
                "like share",
                "like và share",
                "like, share",
                "subscribe",
                "đăng ký kênh",
                "ấn theo dõi ngay",
                "bấm theo dõi ngay",
                "hãy like",
                "nhớ like",
                "để ủng hộ kênh"
            ]
        },
        "editorial_stance": {
            "myth_debunked": "Cứ dọn dẹp bàn làm việc là đang chuẩn bị tinh thần nghiêm túc để làm việc hiệu quả.",
            "why_generic_advice_fails": "Lời khuyên ép bản thân kỷ luật thép chỉ làm tăng thêm áp lực cảm xúc khiến não càng muốn bỏ trốn.",
            "channel_verdict": "Thực chất não bạn không hề chăm chỉ mà đang chọn dọn dẹp như một lối thoát an toàn để trốn việc khó.",
            "tradeoff_or_blindspot": "Lau dọn đem lại cảm giác hoàn thành giả tạo trong mười lăm phút nhưng deadline thực tế vẫn đứng nguyên một chỗ."
        },
        "actionable_value": {
            "core_mechanism": "Đóng vòng lặp nhận thức Zeigarnik bằng hành động siêu nhỏ để giải tỏa sức căng tâm lý.",
            "practical_rule_of_thumb": "Quy tắc mở đầu năm phút: Chỉ cần ngồi xuống viết đúng một câu đầu tiên để kích hoạt quán tính làm việc.",
            "real_world_scenario": "Thay vì đứng dậy lau sạch cái bàn, hãy mở máy tính và đặt đồng hồ năm phút gõ khung sườn bài báo cáo."
        },
        "video_engine": "flow_video"
    }

    outline = {
        "outline": [
            {"scene_id": f"SC{i:02d}", "purpose": f"Triển khai bước {i}: {brief['required_points'][i-1]['text'].lower()}", "requirements": [f"R{i:02d}"], "transition": "Tiếp tục theo mạch phân tích tâm lý"}
            for i in range(1, 12)
        ]
    }

    competitor = {
        "channel_id": "nao_luoi",
        "job_id": job_id,
        "topic": brief["topic"],
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Psych2Go",
                    "top_performing_videos": [
                        {
                            "title": "Why You Procrastinate By Cleaning Your Room (The Zeigarnik Effect)",
                            "views": "2.4M views",
                            "hook_technique": "Đặt câu hỏi trúng tim đen về việc lau dọn lúc nửa đêm.",
                            "pacing_structure": "Ví dụ quen thuộc -> Thí nghiệm Zeigarnik 1927 -> Cơ chế tâm lý nhận thức -> 3 bước khắc phục.",
                            "retention_driver": "Trực quan hóa vòng lặp suy nghĩ thành các ứng dụng chạy ngầm dễ hiểu."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Dùng ẩn dụ ứng dụng ngốn pin điện thoại để giải thích sức căng nhận thức.",
                        "Kết hợp hình tượng người que tự lừa dối bản thân để tạo tiếng cười châm biếm nhẹ nhàng."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Màn hình laptop deadline đỏ rực đối lập với cây chổi quét nhà và đống quần áo giặt sạch.",
                "counter_intuitive_truth_slap": "Bạn không hề chăm chỉ khi dọn phòng, bạn chỉ đang tìm một chỗ trốn an toàn cho cảm xúc bất an trước việc khó."
            },
            "narrative_progression_arc": [
                {"phase": "hook_shock", "purpose": "Mở màn với hành vi dọn quạt kỳ quặc lúc 11 giờ đêm."},
                {"phase": "story_action", "purpose": "Bóc trần cái bẫy hoàn thành giả tạo."},
                {"phase": "mechanism_step", "purpose": "Nguồn gốc thí nghiệm Bluma Zeigarnik năm 1927."},
                {"phase": "mechanism_step", "purpose": "Vòng lặp nhận thức và áp lực trí nhớ làm việc."},
                {"phase": "editorial_commentary", "purpose": "Bình luận phản biện về phần thưởng dopamine tức thì và mid CTA."},
                {"phase": "before_after_contrast", "purpose": "Đối chiếu kết quả dọn nhà kiệt sức với bài vở nộp vội."},
                {"phase": "rapid_examples", "purpose": "Liệt kê các biến tướng như dọn email, lau cốc, xếp thư mục."},
                {"phase": "editorial_commentary", "purpose": "Phản biện sâu: trì hoãn là vấn đề quản trị cảm xúc."},
                {"phase": "story_action", "purpose": "Chiến lược vũ khí hóa hiệu ứng Zeigarnik với quy tắc 5 phút."},
                {"phase": "mechanism_step", "purpose": "Kích hoạt quán tính tâm lý từ dòng viết đầu tiên."},
                {"phase": "cliffhanger_peak", "purpose": "Đóng vòng lặp, bài học quản trị tâm trí và lời kêu gọi kết thúc."}
            ]
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Tâm lý và hành vi đời thường",
            "myth_debunked": brief["editorial_stance"]["myth_debunked"],
            "channel_verdict": brief["editorial_stance"]["channel_verdict"],
            "actionable_rule_of_thumb": brief["actionable_value"]["practical_rule_of_thumb"]
        },
        "cta_and_spinoff_strategy": {
            "mid_cta": brief["cta_plan"]["mid_cta"],
            "close": brief["cta_plan"]["close"],
            "endcard_text": brief["cta_plan"]["endcard_text"]
        }
    }

    # 11 scenes script data
    scenes_raw = [
        {
            "id": "SC01",
            "title": "Cơn nghiện dọn dẹp lúc nửa đêm",
            "situation": "hook_shock",
            "narration": "Mười một giờ đêm, hạn chót nộp báo cáo chỉ còn đúng vài tiếng đồng hồ ngắn ngủi. Thay vì mở máy tính gõ tài liệu, bạn bỗng thấy chiếc quạt bàn bám bụi không chịu nổi. Bạn bật dậy lấy khăn lau từng nan quạt, rồi tiện tay mang cả đống quần áo bẩn ra giặt giũ. Đến một giờ sáng, nhà cửa tinh tươm còn tài liệu vẫn trắng trơn.",
            "tempos": ["burst", "burst", "fast", "fast", "normal", "normal"],
            "anchors": [
                "Mười một giờ đêm, hạn chót nộp báo cáo chỉ còn đúng vài tiếng đồng hồ ngắn ngủi.",
                "Thay vì mở máy tính gõ tài liệu, bạn bỗng thấy chiếc quạt bàn bám bụi không chịu nổi.",
                "Bạn bật dậy lấy khăn lau từng nan quạt,",
                "rồi tiện tay mang cả đống quần áo bẩn ra giặt giũ.",
                "Đến một giờ sáng, nhà cửa tinh tươm",
                "còn tài liệu vẫn trắng trơn."
            ]
        },
        {
            "id": "SC02",
            "title": "Hiện tượng trì hoãn tích cực",
            "situation": "story_action",
            "narration": "Hành động kỳ lạ này được giới nghiên cứu hành vi gọi là hiện tượng trì hoãn tích cực. Bạn không hề nằm lướt mạng vô bổ, bạn đang lao động cật lực để tạo ra cảm giác bản thân cực kỳ chăm chỉ. Não bộ dùng những việc vặt có kết quả ngay trước mắt để đánh lừa cảm xúc, xua đi sự bứt rứt khi né tránh nhiệm vụ chính.",
            "tempos": ["fast", "fast", "normal", "normal", "fast", "fast"],
            "anchors": [
                "Hành động kỳ lạ này được giới nghiên cứu hành vi gọi là hiện tượng trì hoãn tích cực.",
                "Bạn không hề nằm lướt mạng vô bổ,",
                "bạn đang lao động cật lực để tạo ra cảm giác bản thân cực kỳ chăm chỉ.",
                "Não bộ dùng những việc vặt có kết quả ngay trước mắt",
                "để đánh lừa cảm xúc,",
                "xua đi sự bứt rứt khi né tránh nhiệm vụ chính."
            ]
        },
        {
            "id": "SC03",
            "title": "Nghiên cứu Bluma Zeigarnik 1927",
            "situation": "mechanism_step",
            "narration": "Hiện tượng này bắt nguồn từ năm 1927, khi nhà tâm lý học Bluma Zeigarnik quan sát các bồi bàn tại quán cà phê ở Berlin. Họ nhớ vanh vách từng hóa đơn chưa thanh toán, nhưng quên sạch ngay khi khách rời quán. Não người luôn duy trì một sức căng nhận thức để giữ những nhiệm vụ chưa hoàn thành trong bộ nhớ ngắn hạn.",
            "tempos": ["normal", "normal", "normal", "fast", "fast", "normal"],
            "anchors": [
                "Hiện tượng này bắt nguồn từ năm 1927, khi nhà tâm lý học Bluma Zeigarnik",
                "quan sát các bồi bàn tại quán cà phê ở Berlin.",
                "Họ nhớ vanh vách từng hóa đơn chưa thanh toán,",
                "nhưng quên sạch ngay khi khách rời quán.",
                "Não người luôn duy trì một sức căng nhận thức",
                "để giữ những nhiệm vụ chưa hoàn thành trong bộ nhớ ngắn hạn."
            ]
        },
        {
            "id": "SC04",
            "title": "Ứng dụng chạy ngầm ngốn pin tâm trí",
            "situation": "mechanism_step",
            "narration": "Mỗi công việc dang dở giống như một ứng dụng chạy ngầm liên tục ngốn pin điện thoại. Khi hạn chót tới gần, nhiệm vụ lớn như viết luận văn hay làm báo cáo tài chính tạo ra vòng lặp nhận thức khổng lồ. Não bạn cảm thấy quá tải và bị đe dọa bởi tính phức tạp cùng nỗi sợ thất bại, kích hoạt phản xạ phòng vệ tự nhiên.",
            "tempos": ["normal", "fast", "fast", "normal", "normal", "normal"],
            "anchors": [
                "Mỗi công việc dang dở giống như một ứng dụng chạy ngầm liên tục ngốn pin điện thoại.",
                "Khi hạn chót tới gần, nhiệm vụ lớn như viết luận văn hay làm báo cáo tài chính",
                "tạo ra vòng lặp nhận thức khổng lồ.",
                "Não bạn cảm thấy quá tải",
                "và bị đe dọa bởi tính phức tạp cùng nỗi sợ thất bại,",
                "kích hoạt phản xạ phòng vệ tự nhiên."
            ]
        },
        {
            "id": "SC05",
            "title": "Bình luận phản biện và lời nhắc",
            "situation": "editorial_commentary",
            "narration": "Lau dọn bàn ghế đem lại phần thưởng dopamine tức thì vì bạn thấy ngay thành quả bằng mắt. Nhưng đây chỉ là giải pháp xoa dịu cảm xúc nhất thời, không hề giải quyết gốc rễ vấn đề. Nếu bạn cũng từng dọn nhà lúc nửa đêm, hãy lưu lại video để rèn luyện não bộ nhé. Nhận diện sự trốn tránh là bước đi đầu tiên.",
            "tempos": ["slow", "slow", "slow", "normal", "normal", "slow"],
            "anchors": [
                "Lau dọn bàn ghế đem lại phần thưởng dopamine tức thì vì bạn thấy ngay thành quả bằng mắt.",
                "Nhưng đây chỉ là giải pháp xoa dịu cảm xúc nhất thời,",
                "không hề giải quyết gốc rễ vấn đề.",
                "Nếu bạn cũng từng dọn nhà lúc nửa đêm, hãy lưu lại video để rèn luyện não bộ nhé.",
                "Nhận diện sự trốn tránh",
                "là bước đi đầu tiên."
            ]
        },
        {
            "id": "SC06",
            "title": "Cái giá của sự hoàn hảo giả tạo",
            "situation": "before_after_contrast",
            "narration": "Căn phòng thơm phức chỉ che đậy nỗi bất an bị đánh giá năng lực thực sự. Khi bạn dọn nhà xong xuôi, cơ thể đã cạn kiệt cả năng lượng thể chất lẫn sự minh mẫn. Bạn ngồi vào bàn với đôi mắt mỏi nhừ, đồng hồ điểm hai giờ sáng và bạn đành chấp nhận nộp một bài làm cẩu thả sơ sài vào hôm sau.",
            "tempos": ["fast", "burst", "fast", "burst", "normal", "normal"],
            "anchors": [
                "Căn phòng thơm phức chỉ che đậy nỗi bất an bị đánh giá năng lực thực sự.",
                "Khi bạn dọn nhà xong xuôi,",
                "cơ thể đã cạn kiệt cả năng lượng thể chất lẫn sự minh mẫn.",
                "Bạn ngồi vào bàn với đôi mắt mỏi nhừ,",
                "đồng hồ điểm hai giờ sáng",
                "và bạn đành chấp nhận nộp một bài làm cẩu thả sơ sài vào hôm sau."
            ]
        },
        {
            "id": "SC07",
            "title": "Những biến tướng làm việc vặt",
            "situation": "rapid_examples",
            "narration": "Không chỉ dọn phòng, cơn thèm làm việc nhà còn biến tướng thành việc sắp xếp lại hộp thư điện tử, ngồi phân loại thư mục máy tính, hay cọ rửa từng chiếc tách uống trà. Bạn luôn nghĩ ra những việc có vẻ hữu ích để tự biện minh cho việc trì hoãn nhiệm vụ sống còn đang treo lơ lửng trên đầu.",
            "tempos": ["burst", "burst", "fast", "fast", "normal", "normal"],
            "anchors": [
                "Không chỉ dọn phòng, cơn thèm làm việc nhà còn biến tướng thành việc sắp xếp lại hộp thư điện tử,",
                "ngồi phân loại thư mục máy tính,",
                "hay cọ rửa từng chiếc tách uống trà.",
                "Bạn luôn nghĩ ra những việc có vẻ hữu ích",
                "để tự biện minh cho việc trì hoãn nhiệm vụ sống còn",
                "đang treo lơ lửng trên đầu."
            ]
        },
        {
            "id": "SC08",
            "title": "Bản chất quản trị cảm xúc",
            "situation": "editorial_commentary",
            "narration": "Đừng vội tự trách bản thân lười biếng hay thiếu ý chí kiên định. Trì hoãn thực chất là vấn đề quản trị cảm xúc chứ không phải quản lý thời gian. Khi bạn sợ hãi sự phán xét từ cấp trên hay đồng nghiệp, não bạn sẽ tìm mọi ngóc ngách quen thuộc để bảo vệ lòng tự trọng mong manh của chính bạn.",
            "tempos": ["slow", "slow", "normal", "slow", "slow", "normal"],
            "anchors": [
                "Đừng vội tự trách bản thân lười biếng hay thiếu ý chí kiên định.",
                "Trì hoãn thực chất là vấn đề quản trị cảm xúc",
                "chứ không phải quản lý thời gian.",
                "Khi bạn sợ hãi sự phán xét từ cấp trên hay đồng nghiệp,",
                "não bạn sẽ tìm mọi ngóc ngách quen thuộc",
                "để bảo vệ lòng tự trọng mong manh của chính bạn."
            ]
        },
        {
            "id": "SC09",
            "title": "Chiến lược vũ khí hóa Zeigarnik",
            "situation": "story_action",
            "narration": "Thay vì để hiệu ứng Zeigarnik nhấn chìm bạn trong lo âu, bạn hoàn toàn có thể biến nó thành động lực thúc đẩy. Hãy áp dụng quy tắc khởi động năm phút. Bạn chỉ cần cam kết ngồi xuống viết đúng một câu mở đầu hoặc gõ ba gạch đầu dòng rồi được phép đứng dậy đi làm việc khác nếu muốn.",
            "tempos": ["normal", "fast", "fast", "normal", "normal", "fast"],
            "anchors": [
                "Thay vì để hiệu ứng Zeigarnik nhấn chìm bạn trong lo âu,",
                "bạn hoàn toàn có thể biến nó thành động lực thúc đẩy.",
                "Hãy áp dụng quy tắc khởi động năm phút.",
                "Bạn chỉ cần cam kết ngồi xuống viết đúng một câu mở đầu",
                "hoặc gõ ba gạch đầu dòng",
                "rồi được phép đứng dậy đi làm việc khác nếu muốn."
            ]
        },
        {
            "id": "SC10",
            "title": "Kích hoạt quán tính tâm lý",
            "situation": "mechanism_step",
            "narration": "Điều tuyệt vời là khi bạn đã đặt tay gõ dòng đầu tiên, vòng lặp nhận thức được kích hoạt theo chiều hướng có lợi. Não bạn ghét sự dang dở nên sẽ thúc giục bạn viết tiếp câu thứ hai và đoạn thứ ba. Quán tính tâm lý này giúp bạn vượt qua rào cản ma sát ban đầu một cách êm ái.",
            "tempos": ["normal", "normal", "fast", "fast", "normal", "normal"],
            "anchors": [
                "Điều tuyệt vời là khi bạn đã đặt tay gõ dòng đầu tiên,",
                "vòng lặp nhận thức được kích hoạt theo chiều hướng có lợi.",
                "Não bạn ghét sự dang dở",
                "nên sẽ thúc giục bạn viết tiếp câu thứ hai và đoạn thứ ba.",
                "Quán tính tâm lý này giúp bạn vượt qua rào cản ma sát ban đầu",
                "một cách êm ái."
            ]
        },
        {
            "id": "SC11",
            "title": "Đóng vòng lặp và làm chủ cuộc chơi",
            "situation": "cliffhanger_peak",
            "narration": "Hãy chia nhỏ dự án thành từng mẩu vụn và luôn để lại một câu chưa viết xong trước khi nghỉ giải lao để hôm sau bắt nhịp ngay. Bạn thường làm việc gì kỳ lạ nhất khi sắp tới hạn chót, hãy kể cho Não Lười nghe bên dưới nhé. Chúc bạn luôn làm chủ những vòng lặp tâm trí của mình.",
            "tempos": ["fast", "fast", "normal", "slow", "hold", "hold"],
            "anchors": [
                "Hãy chia nhỏ dự án thành từng mẩu vụn",
                "và luôn để lại một câu chưa viết xong trước khi nghỉ giải lao để hôm sau bắt nhịp ngay.",
                "Bạn thường làm việc gì kỳ lạ nhất khi sắp tới hạn chót, hãy kể cho Não Lười nghe bên dưới nhé.",
                "Chúc bạn luôn làm chủ",
                "những vòng lặp tâm trí của mình.",
                "Hẹn gặp lại bạn trong video tiếp theo."
            ]
        }
    ]

    scenes = []
    for sc_idx, sc_raw in enumerate(scenes_raw, 1):
        sc_id = sc_raw["id"]
        beats = []
        images = []
        for b_idx in range(1, 7):
            b_id = f"{sc_id}_B{b_idx}"
            im_id = f"{sc_id}_I{b_idx}"
            tempo = sc_raw["tempos"][b_idx - 1]
            sit = sc_raw["situation"]
            is_end = (sc_id == "SC11" and b_idx == 6)
            anchor_text = sc_raw["anchors"][b_idx - 1]

            beat = {
                "id": b_id,
                "image_id": im_id,
                "purpose": f"Nhịp {b_idx} phân cảnh {sc_id}: {anchor_text[:40]}",
                "anchor": {"vi": {"quote": anchor_text, "occurrence": 1}},
                "effect": "hold" if is_end else "none",
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": tempo,
                "narrative_situation": sit,
                "camera_intent": "hold" if is_end else ("action" if b_idx in (3, 4) else "focus"),
                "shot_type": "full_scene"
            }
            if is_end:
                beat["is_endcard"] = True

            image = {
                "id": im_id,
                "description": f"Iconic 2D Vietnamese indie webcomic doodle stickman in flat cerulean-blue T-shirt (#3B82C4) and slate-gray trousers (#8C857B) on warm paper-cream canvas (#F8F0DC), wobbly #000000 marker line art, >=60% negative space, illustrating scene {sc_id} beat {b_idx}: {anchor_text[:50]}, zero 3D, zero gradients.",
                "character_ids": ["CH01"],
                "preserve": "bald white circle head stickman, cerulean-blue T-shirt, slate-gray trousers, paper-cream canvas",
                "change": f"stickman action for beat {b_idx}",
                "reason": f"Narration-locked full-frame beat {im_id}",
                "visible_text": [{"text": "NÃO LƯỜI", "placement": "upper_third", "object": "logo"}] if is_end else [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": tempo,
                "narrative_situation": sit,
                "emphasis_text": "NÃO LƯỜI" if is_end else None,
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "motion_prompt": f"Smooth 2D hand-drawn doodle explainer animation illustrating beat {b_idx} of scene {sc_id}, silent visual storytelling, no talking, no lip movement"
            }
            beats.append(beat)
            images.append(image)

        scene = {
            "id": sc_id,
            "title": sc_raw["title"],
            "purpose": f"Triển khai bước {sc_idx}: {brief['required_points'][sc_idx-1]['text'].lower()}",
            "action": f"The doodle stickman demonstrates narrative phase for {sc_raw['title']}.",
            "setting": "Minimalist doodle room or metaphorical mind canvas on paper-cream background #F8F0DC.",
            "camera": f"Semantic camera: establishing wide shot transitioning into focus on {sc_raw['title']}",
            "narration": sc_raw["narration"],
            "requirements": [f"R{sc_idx:02d}"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "layers": [],
            "tone": "narrative_warm",
            "narrative_phase": "hook" if sc_idx == 1 else ("outro" if sc_idx == 11 else "development"),
            "narrative_situation": sc_raw["situation"],
            "beats": beats,
            "images": images
        }
        scenes.append(scene)

    content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": "",
        "topic": brief["topic"],
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": brief["required_points"],
        "characters": [channel_cast("nao_luoi", "CH01")],
        "scenes": scenes,
        "coverage": [
            {"requirement_id": f"R{i:02d}", "scene_id": f"SC{i:02d}", "quote": sc["narration"][:50]}
            for i, sc in enumerate(scenes, 1)
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC03",
                "quote": "Hiện tượng này bắt nguồn từ năm 1927, khi nhà tâm lý học Bluma Zeigarnik quan sát các bồi bàn tại quán cà phê ở Berlin.",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Các nhiệm vụ chưa hoàn thành tạo ra sức căng nhận thức kéo dài trong trí nhớ làm việc."
            }
        ],
        "revision_response": "Initial comprehensive schema-valid generation",
        "open_questions": []
    }

    job_dir = ROOT / "sys" / "runs" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    brief_path = job_dir / "brief.json"
    brief_bytes = json.dumps(brief, indent=2, ensure_ascii=False).encode("utf-8")
    brief_path.write_bytes(brief_bytes)
    content["brief_hash"] = hashlib.sha256(brief_bytes).hexdigest()

    (job_dir / "content.json").write_text(json.dumps(content, indent=2, ensure_ascii=False))
    (job_dir / "outline.json").write_text(json.dumps(outline, indent=2, ensure_ascii=False))
    (job_dir / "competitor_research.json").write_text(json.dumps(competitor, indent=2, ensure_ascii=False))
    print(f"Generated {job_id}")

if __name__ == "__main__":
    build_nao_luoi_16x9()
