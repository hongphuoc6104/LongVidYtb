import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sys"))

from channels.registry import channel_cast, channel_profile_stamp, get_channel


def build_tui_tien_16x9():
    job_id = "tui-tien-batch3-16x9"
    ch = get_channel("tui_tien")

    brief = {
        "schema_version": "3.0",
        "topic": "Giải Phẫu Kinh Tế Quán Cà Phê: Vì Sao Khách Ngồi Cả Ngày Vẫn Lãi Đậm?",
        "audience": "Sinh viên, người mới đi làm thu nhập 7-20 triệu",
        "goal": "Bóc tách chi tiết định phí biến phí và chiến lược tối ưu hóa doanh thu quán cà phê từ khách ngồi lâu",
        "video_type": "research_guide",
        "duration": {
            "min_seconds": 180.0,
            "max_seconds": 240.0
        },
        "scene_count": 11,
        "required_points": [
            {"id": f"R{i:02d}", "text": t} for i, t in enumerate([
                "Nghịch lý khách ngồi cắm sạc laptop 8 tiếng với một ly nước 45k",
                "Bóc tách biến phí nguyên liệu thực tế cho một phần cà phê",
                "Hóa đơn tiền điện thực tế của một chiếc máy tính xách tay",
                "Gánh nặng định phí tiền thuê mặt bằng và lương nhân viên",
                "Hiệu ứng chim mồi tạo dựng niềm tin và lời nhắc lưu lại video",
                "Tâm lý e ngại quán vắng người và sức hút của không gian đông đúc",
                "Nguồn thu biên lợi nhuận cao từ tệp khách hàng mua mang đi",
                "Bản chất mô hình kinh doanh bất động sản chia nhỏ theo giờ",
                "Chiến lược phân vùng bàn ghế thông minh để tối ưu vòng quay",
                "Cân bằng điểm hòa vốn và bài học quản trị dòng tiền cho chủ quán",
                "Đúc kết kinh tế thực chiến và lời mời thảo luận tương tác"
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
                "title": "Cost Structure and Break-Even Dynamics in Modern Coffee Retail",
                "reference": "Vietnam F&B Industry Report (2024). Operational Economics of Independent Cafes.",
                "facts": [
                    "Giá vốn nguyên liệu cà phê chỉ chiếm khoảng 12% đến 15% giá bán lẻ một ly nước."
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
                "Bóc tách từng khoản tiền chi tiết giúp người xem hiểu thấu đáo mô hình kinh doanh F&B"
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Không đòi hỏi thuật ngữ tài chính chuyên sâu.",
            "pacing": "Rõ ràng, tính nhẩm từng bước dứt khoát trên nền giấy kẻ ô.",
            "speech_rates": {
                "vi": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.1,
                    "source": "Acoustic calibrated cadence"
                }
            }
        },
        "packaging": {
            "youtube_title": "Khách Ngồi Cả Ngày, Quán Cà Phê Kiếm Lời Thế Nào?",
            "thumbnail_spec": {
                "visual_hook": "Người que đeo kính chỉ vào bảng tính doanh thu quán cà phê chia đôi giữa ly nước 45 nghìn và cọc tiền lãi",
                "text_overlay": "NGỒI CẢ NGÀY VẪN LÃI",
                "contrast_pair": "Khách ngồi 8 tiếng vs Cọc tiền doanh thu",
                "thumbnail_prompt": "Simple 2D doodle stickman with round glasses holding a coin-gold marker pointing at a large ledger board divided into costs and revenue. A steaming cup of coffee with a 45.000 Đ tag sits next to a growing stack of green VND banknotes on flat grid-paper canvas (#FAF6E9 with faint #E3DCC8 square grid). Bold hand-lettered text in upper third: 'NGỒI CẢ NGÀY VẪN LÃI'. Minimalist orthographic 2D, >=60% empty grid space, no 3D, no gradients.",
                "layout_mode": "split_contrast"
            },
            "editorial_stance": {
                "myth_debunked": "Khách gọi một ly cà phê ngồi làm việc cả buổi là kẻ phá đám làm quán lỗ tiền điện.",
                "why_generic_advice_fails": "Tư duy đuổi khéo khách chỉ làm quán vắng hoe như chùa bà đanh và mất sạch khách vãng lai.",
                "channel_verdict": "Thực chất quán cà phê không sống nhờ tiền nước mà bán không gian làm việc và tận dụng bạn làm mồi câu đám đông.",
                "tradeoff_or_blindspot": "Chấp nhận khách ngồi lâu tốn thêm vài trăm đồng tiền điện nhưng đổi lại hiệu ứng quán đông đúc thu hút khách mang đi."
            },
            "actionable_value": {
                "core_mechanism": "Phân bổ định phí mặt bằng trên dòng khách vãng lai và biến khách ngồi làm việc thành mồi câu uy tín tự nhiên.",
                "practical_rule_of_thumb": "Quy tắc mồi câu đám đông: Quán có ba bàn sáng đèn laptop luôn hút khách vãng lai gấp bốn lần quán trống trơn.",
                "real_world_scenario": "Chủ quán sẵn sàng mời thêm nước lọc cho khách ngồi làm việc vì mỗi giờ ngồi lại làm tăng xác suất gọi thêm đĩa bánh ngọt."
            }
        },
        "youtube_title": "Khách Ngồi Cả Ngày, Quán Cà Phê Kiếm Lời Thế Nào?",
        "thumbnail_spec": {
            "visual_hook": "Người que đeo kính chỉ vào bảng tính doanh thu quán cà phê chia đôi giữa ly nước 45 nghìn và cọc tiền lãi",
            "text_overlay": "NGỒI CẢ NGÀY VẪN LÃI",
            "contrast_pair": "Khách ngồi 8 tiếng vs Cọc tiền doanh thu",
            "thumbnail_prompt": "Simple 2D doodle stickman with round glasses holding a coin-gold marker pointing at a large ledger board divided into costs and revenue. A steaming cup of coffee with a 45.000 Đ tag sits next to a growing stack of green VND banknotes on flat grid-paper canvas (#FAF6E9 with faint #E3DCC8 square grid). Bold hand-lettered text in upper third: 'NGỒI CẢ NGÀY VẪN LÃI'. Minimalist orthographic 2D, >=60% empty grid space, no 3D, no gradients.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Tiền và kinh tế đời sống",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": [
            "tui tien",
            "kinh te quan ca phe",
            "tai chinh",
            "kinh doanh",
            "fnb",
            "kinhte"
        ],
        "cta_plan": {
            "mid_cta": "Nếu bạn cũng thích quan sát các con số kinh doanh đời thường, hãy lưu lại video để đối chiếu nhé.",
            "close": "Mỗi lần đi cà phê bạn thường gọi món gì và ngồi bao lâu, hãy bình luận cho Túi Tiền Biết Nói nghe nhé.",
            "endcard_text": "TÚI TIỀN BIẾT NÓI"
        },
        "channel_profile": channel_profile_stamp("tui_tien"),
        "engagement": {
            "cta_voice": "Mê con số",
            "bridge_templates": [
                "Bản dài mình mổ xẻ trên YouTube."
            ],
            "close_templates": [
                "Lưu lại, lần sau tính nhẩm trước khi quẹt thẻ."
            ],
            "endcard_text": "TÚI TIỀN BIẾT NÓI",
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
            "myth_debunked": "Khách gọi một ly cà phê ngồi làm việc cả buổi là kẻ phá đám làm quán lỗ tiền điện.",
            "why_generic_advice_fails": "Tư duy đuổi khéo khách chỉ làm quán vắng hoe như chùa bà đanh và mất sạch khách vãng lai.",
            "channel_verdict": "Thực chất quán cà phê không sống nhờ tiền nước mà bán không gian làm việc và tận dụng bạn làm mồi câu đám đông.",
            "tradeoff_or_blindspot": "Chấp nhận khách ngồi lâu tốn thêm vài trăm đồng tiền điện nhưng đổi lại hiệu ứng quán đông đúc thu hút khách mang đi."
        },
        "actionable_value": {
            "core_mechanism": "Phân bổ định phí mặt bằng trên dòng khách vãng lai và biến khách ngồi làm việc thành mồi câu uy tín tự nhiên.",
            "practical_rule_of_thumb": "Quy tắc mồi câu đám đông: Quán có ba bàn sáng đèn laptop luôn hút khách vãng lai gấp bốn lần quán trống trơn.",
            "real_world_scenario": "Chủ quán sẵn sàng mời thêm nước lọc cho khách ngồi làm việc vì mỗi giờ ngồi lại làm tăng xác suất gọi thêm đĩa bánh ngọt."
        },
        "video_engine": "flow_video"
    }

    outline = {
        "outline": [
            {"scene_id": f"SC{i:02d}", "purpose": f"Triển khai bước {i}: {brief['required_points'][i-1]['text'].lower()}", "requirements": [f"R{i:02d}"], "transition": "Tiếp tục theo trình tự phân tích kinh tế"}
            for i in range(1, 12)
        ]
    }

    competitor = {
        "channel_id": "tui_tien",
        "job_id": job_id,
        "topic": brief["topic"],
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Học Viện Bò và Gấu",
                    "top_performing_videos": [
                        {
                            "title": "Kinh tế học quán cà phê: Khách ngồi cả ngày quán sống bằng gì?",
                            "views": "1.8M views",
                            "hook_technique": "Bóc tách tờ hóa đơn 45k thành các thành phần định phí và biến phí.",
                            "pacing_structure": "Tình huống ngồi lì 8 tiếng -> Bóc tách giá vốn -> Phân tích định phí mặt bằng -> Nghệ thuật mồi câu.",
                            "retention_driver": "Sự bất ngờ khi biết khách ngồi lâu lại là động lực giúp quán bán được nhiều đơn mang đi."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Dùng bảng tính vẽ tay trên giấy kẻ ô để giải thích chi phí cố định.",
                        "Minh họa hiệu ứng mồi câu đám đông bằng hình ảnh nam châm hút khách đi đường."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Ly cà phê 45k bên cạnh máy tính cắm sạc đối lập với cọc tiền doanh thu cuối ngày.",
                "counter_intuitive_truth_slap": "Quán cà phê không bán nước giải khát, họ bán không gian và tận dụng bạn làm phông nền uy tín kéo khách mang đi."
            },
            "narrative_progression_arc": [
                {"phase": "hook_shock", "purpose": "Khách ngồi cắm sạc từ sáng đến chiều với một ly nước."},
                {"phase": "story_action", "purpose": "Tính nhẩm biến phí nguyên liệu thực tế chưa tới 7 nghìn."},
                {"phase": "mechanism_step", "purpose": "Tiền điện laptop 8 tiếng chỉ tốn đúng 1 nghìn đồng."},
                {"phase": "mechanism_step", "purpose": "Gánh nặng định phí khổng lồ: mặt bằng và nhân sự."},
                {"phase": "editorial_commentary", "purpose": "Bình luận phản biện về hiệu ứng chim mồi và mid CTA."},
                {"phase": "before_after_contrast", "purpose": "Đối chiếu tâm lý sợ quán vắng với sức hút quán đông."},
                {"phase": "rapid_examples", "purpose": "Doanh thu béo bở từ khách mua mang đi chớp nhoáng."},
                {"phase": "editorial_commentary", "purpose": "Bản chất bán bất động sản chia nhỏ theo giờ."},
                {"phase": "story_action", "purpose": "Chiến lược phân bổ bàn ghế dài và bàn tròn tối ưu."},
                {"phase": "mechanism_step", "purpose": "Điểm hòa vốn định phí và dòng tiền thuần túy."},
                {"phase": "cliffhanger_peak", "purpose": "Đúc kết kinh tế thực chiến và lời mời tương tác cuối video."}
            ]
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Tiền và kinh tế đời sống",
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

    # 11 scenes calibrated to ~731 words total
    scenes_raw = [
        {
            "id": "SC01",
            "title": "Khách ngồi cắm sạc cả ngày",
            "situation": "hook_shock",
            "narration": "Một ly cà phê bốn mươi lăm nghìn đồng, nhưng bạn ngồi cắm sạc máy tính từ chín giờ sáng đến tận năm giờ chiều muộn. Bạn dùng wifi tốc độ cao, máy lạnh phà mát rượi và xin thêm ba lần nước lọc mát lạnh. Bạn nghĩ người chủ quán đang ấm ức nhìn bạn như kẻ phá hoại công việc kinh doanh của họ?",
            "tempos": ["burst", "burst", "fast", "fast", "normal", "normal"],
            "anchors": [
                "Một ly cà phê bốn mươi lăm nghìn đồng,",
                "nhưng bạn ngồi cắm sạc máy tính từ chín giờ sáng đến tận năm giờ chiều muộn.",
                "Bạn dùng wifi tốc độ cao, máy lạnh phà mát rượi",
                "và xin thêm ba lần nước lọc mát lạnh.",
                "Bạn nghĩ người chủ quán đang ấm ức nhìn bạn",
                "như kẻ phá hoại công việc kinh doanh của họ?"
            ]
        },
        {
            "id": "SC02",
            "title": "Bóc tách biến phí thực tế",
            "situation": "story_action",
            "narration": "Để hiểu rõ bài toán này, hãy cùng đặt bút tính nhẩm từng con số chi phí thực tế. Một ly nước bán bốn mươi lăm ngàn, tiền hạt Robusta nguyên chất loại ngon chỉ tốn ba ngàn đồng. Thêm sữa đặc, đá lạnh, ống hút và ly nhựa tiện lợi, tổng giá vốn hàng bán cho mỗi phần chưa tới bảy ngàn đồng.",
            "tempos": ["fast", "fast", "normal", "normal", "fast", "fast"],
            "anchors": [
                "Để hiểu rõ bài toán này,",
                "hãy cùng đặt bút tính nhẩm từng con số chi phí thực tế.",
                "Một ly nước bán bốn mươi lăm ngàn,",
                "tiền hạt Robusta nguyên chất loại ngon chỉ tốn ba ngàn đồng.",
                "Thêm sữa đặc, đá lạnh, ống hút và ly nhựa tiện lợi,",
                "tổng giá vốn hàng bán cho mỗi phần chưa tới bảy ngàn đồng."
            ]
        },
        {
            "id": "SC03",
            "title": "Hóa đơn tiền điện thực tế",
            "situation": "mechanism_step",
            "narration": "Nhiều người nghĩ khách cắm sạc laptop làm tốn bộn tiền điện của cửa hàng. Thực tế, một chiếc máy tính xách tay văn phòng thông dụng tiêu thụ khoảng năm mươi oát mỗi giờ. Bạn cắm sạc liên tục suốt ngày dài tiêu tốn chưa tới nửa số điện, tương đương khoảng một nghìn đồng theo giá điện kinh doanh hiện nay.",
            "tempos": ["normal", "normal", "normal", "fast", "fast", "normal"],
            "anchors": [
                "Nhiều người nghĩ khách cắm sạc laptop làm tốn bộn tiền điện của cửa hàng.",
                "Thực tế, một chiếc máy tính xách tay văn phòng thông dụng",
                "tiêu thụ khoảng năm mươi oát mỗi giờ.",
                "Bạn cắm sạc liên tục suốt ngày dài",
                "tiêu tốn chưa tới nửa số điện,",
                "tương đương khoảng một nghìn đồng theo giá điện kinh doanh hiện nay."
            ]
        },
        {
            "id": "SC04",
            "title": "Gánh nặng định phí khổng lồ",
            "situation": "mechanism_step",
            "narration": "Khoản biến phí này rất nhỏ bé, người chủ quán vẫn còn giữ lại ba mươi bảy ngàn tiền lời gộp. Số tiền dôi ra đó dùng để trang trải định phí khổng lồ: năm mươi triệu tiền thuê mặt bằng phố, bốn mươi triệu tiền lương nhân viên pha chế và chi phí khấu hao máy móc trang thiết bị mỗi tháng.",
            "tempos": ["normal", "fast", "fast", "normal", "normal", "normal"],
            "anchors": [
                "Khoản biến phí này rất nhỏ bé,",
                "người chủ quán vẫn còn giữ lại ba mươi bảy ngàn tiền lời gộp.",
                "Số tiền dôi ra đó dùng để trang trải định phí khổng lồ:",
                "năm mươi triệu tiền thuê mặt bằng phố,",
                "bốn mươi triệu tiền lương nhân viên pha chế",
                "và chi phí khấu hao máy móc trang thiết bị mỗi tháng."
            ]
        },
        {
            "id": "SC05",
            "title": "Hiệu ứng chim mồi và lời nhắc",
            "situation": "editorial_commentary",
            "narration": "Chủ quán kinh doanh thông thái không bao giờ nhìn vào số giờ bạn ngồi. Họ nhìn vào giá trị bạn mang lại cho bầu không khí làm việc chung. Nếu bạn cũng thích quan sát các con số kinh doanh đời thường, hãy lưu lại video để đối chiếu nhé. Khách hàng ngồi kín bàn chính là tấm biển quảng cáo sống động nhất.",
            "tempos": ["slow", "slow", "slow", "normal", "normal", "slow"],
            "anchors": [
                "Chủ quán kinh doanh thông thái không bao giờ nhìn vào số giờ bạn ngồi.",
                "Họ nhìn vào giá trị bạn mang lại cho bầu không khí làm việc chung.",
                "Nếu bạn cũng thích quan sát các con số kinh doanh đời thường, hãy lưu lại video để đối chiếu nhé.",
                "Khách hàng ngồi kín bàn",
                "chính là tấm biển quảng cáo",
                "sống động nhất."
            ]
        },
        {
            "id": "SC06",
            "title": "Tâm lý e ngại quán vắng",
            "situation": "before_after_contrast",
            "narration": "Hãy tưởng tượng bạn đi tìm một điểm hẹn lý tưởng để bàn thảo công việc đối tác. Nhìn vào một cửa tiệm vắng tanh không một bóng người, phản xạ tự nhiên là bạn sẽ nghi ngờ đồ uống dở hoặc dịch vụ kém cỏi. Ngược lại, quán có nhiều người ngồi làm việc chăm chú tạo cảm giác cực kỳ uy tín và tin cậy.",
            "tempos": ["fast", "burst", "fast", "burst", "normal", "normal"],
            "anchors": [
                "Hãy tưởng tượng bạn đi tìm một điểm hẹn lý tưởng để bàn thảo công việc đối tác.",
                "Nhìn vào một cửa tiệm vắng tanh không một bóng người,",
                "phản xạ tự nhiên là bạn sẽ nghi ngờ đồ uống dở hoặc dịch vụ kém cỏi.",
                "Ngược lại,",
                "quán có nhiều người ngồi làm việc chăm chú",
                "tạo cảm giác cực kỳ uy tín và tin cậy."
            ]
        },
        {
            "id": "SC07",
            "title": "Nguồn thu từ khách mang đi",
            "situation": "rapid_examples",
            "narration": "Chính sự tấp nập bạn tạo ra đã kéo theo dòng người vãng lai ghé mua mang đi liên tục mỗi ngày. Khách hàng vội vã mua ly nước trong hai phút mà không tốn chỗ ngồi, không tốn điện quạt gió hay giấy lau. Dòng doanh thu mang đi chớp nhoáng này mới là nguồn mang lại biên lợi nhuận ròng cao nhất.",
            "tempos": ["burst", "burst", "fast", "fast", "normal", "normal"],
            "anchors": [
                "Chính sự tấp nập bạn tạo ra đã kéo theo dòng người vãng lai ghé mua mang đi liên tục mỗi ngày.",
                "Khách hàng vội vã mua ly nước trong hai phút",
                "mà không tốn chỗ ngồi,",
                "không tốn điện quạt gió hay giấy lau.",
                "Dòng doanh thu mang đi chớp nhoáng này",
                "mới là nguồn mang lại biên lợi nhuận ròng cao nhất."
            ]
        },
        {
            "id": "SC08",
            "title": "Bán bất động sản theo giờ",
            "situation": "editorial_commentary",
            "narration": "Kinh doanh cà phê hiện đại thực chất là ngành kinh doanh bất động sản chia nhỏ theo từng khung giờ. Nơi đây bán không gian làm việc, sự yên tĩnh và nguồn cảm hứng tập trung sáng tạo. Khách ngồi làm việc lâu thường phát sinh nhu cầu gọi thêm ly nước thứ hai hoặc gọi thêm đĩa bánh ngọt ăn lót dạ.",
            "tempos": ["slow", "slow", "normal", "slow", "slow", "normal"],
            "anchors": [
                "Kinh doanh cà phê hiện đại thực chất là ngành kinh doanh bất động sản",
                "chia nhỏ theo từng khung giờ.",
                "Nơi đây bán không gian làm việc, sự yên tĩnh và nguồn cảm hứng tập trung sáng tạo.",
                "Khách ngồi làm việc lâu",
                "thường phát sinh nhu cầu gọi thêm ly nước thứ hai",
                "hoặc gọi thêm đĩa bánh ngọt ăn lót dạ."
            ]
        },
        {
            "id": "SC09",
            "title": "Chiến lược phân vùng bàn ghế",
            "situation": "story_action",
            "narration": "Các chuỗi thương hiệu lớn luôn khéo léo thiết kế những chiếc bàn gỗ dài có nhiều ổ cắm điện ở góc trong cùng dành riêng cho dân văn phòng. Còn khu vực mặt tiền gần cửa kính được bố trí bàn tròn nhỏ ghế thấp để phục vụ nhóm khách trò chuyện nhanh, tối ưu hóa vòng quay chỗ ngồi hiệu quả.",
            "tempos": ["normal", "fast", "fast", "normal", "normal", "fast"],
            "anchors": [
                "Các chuỗi thương hiệu lớn luôn khéo léo thiết kế những chiếc bàn gỗ dài",
                "có nhiều ổ cắm điện ở góc trong cùng dành riêng cho dân văn phòng.",
                "Còn khu vực mặt tiền gần cửa kính",
                "được bố trí bàn tròn nhỏ ghế thấp",
                "để phục vụ nhóm khách trò chuyện nhanh,",
                "tối ưu hóa vòng quay chỗ ngồi hiệu quả."
            ]
        },
        {
            "id": "SC10",
            "title": "Cân bằng điểm hòa vốn",
            "situation": "mechanism_step",
            "narration": "Bài toán then chốt là cân bằng giữa lượng khách ngồi lâu tạo phông nền và tốc độ phục vụ các đơn hàng mang về mang đi. Khi doanh thu vượt qua điểm hòa vốn tiền mặt bằng, mỗi ly nước bán thêm cho người đi đường đều đem lại dòng tiền thuần túy giúp cơ sở kinh doanh bỏ túi lợi nhuận ròng.",
            "tempos": ["normal", "normal", "fast", "fast", "normal", "normal"],
            "anchors": [
                "Bài toán then chốt là cân bằng giữa lượng khách ngồi lâu tạo phông nền",
                "và tốc độ phục vụ các đơn hàng mang về mang đi.",
                "Khi doanh thu vượt qua điểm hòa vốn tiền mặt bằng,",
                "mỗi ly nước bán thêm cho người đi đường",
                "đều đem lại dòng tiền thuần túy",
                "giúp cơ sở kinh doanh bỏ túi lợi nhuận ròng."
            ]
        },
        {
            "id": "SC11",
            "title": "Đúc kết kinh tế và lời chào",
            "situation": "cliffhanger_peak",
            "narration": "Lần tới khi ngồi quán cả buổi, bạn hãy nhớ mình đang là một cộng tác viên truyền thông thầm lặng của tiệm. Mỗi lần đi cà phê bạn thường gọi món gì và ngồi bao lâu, hãy bình luận cho Túi Tiền Biết Nói nghe nhé. Hẹn gặp lại bạn trong các bài phân tích kinh tế tiếp theo trên kênh.",
            "tempos": ["fast", "fast", "normal", "slow", "hold", "hold"],
            "anchors": [
                "Lần tới khi ngồi quán cả buổi,",
                "bạn hãy nhớ mình đang là một cộng tác viên truyền thông thầm lặng của tiệm.",
                "Mỗi lần đi cà phê bạn thường gọi món gì và ngồi bao lâu, hãy bình luận cho Túi Tiền Biết Nói nghe nhé.",
                "Hẹn gặp lại bạn",
                "trong các bài phân tích kinh tế tiếp theo trên kênh.",
                "Chúc bạn luôn đầu tư thông minh cho bản thân."
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
                "description": f"Simple 2D doodle stickman with round glasses wearing flat coin-gold T-shirt (#F2C14E) and navy trousers (#24364F) holding a pencil on flat warm grid-paper canvas (#FAF6E9 with faint #E3DCC8 square grid), wobbly #1F1F1F marker linework, money green fills (#2F9E5B), illustrating scene {sc_id} beat {b_idx}: {anchor_text[:50]}, >=60% negative space, zero 3D, zero gradients.",
                "character_ids": ["CH01"],
                "preserve": "stickman with glasses, coin-gold T-shirt, navy trousers, warm grid-paper canvas",
                "change": f"stickman action for beat {b_idx}",
                "reason": f"Narration-locked full-frame beat {im_id}",
                "visible_text": [{"text": "TÚI TIỀN BIẾT NÓI", "placement": "upper_third", "object": "logo"}] if is_end else [],
                "kind": "scene",
                "shot_type": "full_scene",
                "tempo": tempo,
                "narrative_situation": sit,
                "emphasis_text": "TÚI TIỀN BIẾT NÓI" if is_end else None,
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": True,
                "motion_prompt": f"Smooth 2D hand-drawn doodle explainer animation on grid-paper canvas illustrating beat {b_idx} of scene {sc_id}, silent visual storytelling, no talking, no lip movement"
            }
            beats.append(beat)
            images.append(image)

        scene = {
            "id": sc_id,
            "title": sc_raw["title"],
            "purpose": f"Triển khai bước {sc_idx}: {brief['required_points'][sc_idx-1]['text'].lower()}",
            "action": f"The doodle accountant stickman analyzes FnB economics for {sc_raw['title']}.",
            "setting": "Minimalist ledger board or coffee shop counter on warm grid-paper canvas #FAF6E9.",
            "camera": f"Semantic camera: establishing shot transitioning into focus on {sc_raw['title']}",
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
        "characters": [channel_cast("tui_tien", "CH01")],
        "scenes": scenes,
        "coverage": [
            {"requirement_id": f"R{i:02d}", "scene_id": f"SC{i:02d}", "quote": sc["narration"][:50]}
            for i, sc in enumerate(scenes, 1)
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC02",
                "quote": "Thêm sữa đặc, đá lạnh, ống hút và ly nhựa tiện lợi, tổng giá vốn hàng bán cho mỗi phần chưa tới bảy ngàn đồng.",
                "language": "vi",
                "source_id": "SRC01",
                "fact": "Giá vốn nguyên liệu cà phê chỉ chiếm khoảng 12% đến 15% giá bán lẻ một ly nước."
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
    build_tui_tien_16x9()
