#!/usr/bin/env python3
"""Build and update all 3 short 9:16 spin-offs with user review suggestions."""

import sys
from pathlib import Path

sys.path.insert(0, "sys")
sys.path.insert(0, "sys/tools")

from tools.research_story_architect import (
    PackagingSpec,
    ResearchedBeat,
    ResearchedScene,
    ResearchedTopic,
    write_production_package,
)
from tools.script_cadence_checker import SceneCadenceReport


def build_and_validate():
    # -------------------------------------------------------------
    # 1. SPINOFF 01: feynman-jargon-trap-9x16
    # -------------------------------------------------------------
    sources_1 = [
        {
            "id": "SRC01",
            "title": "Consequences of Erudite Vernacular Utilized Irrespective of Necessity: Problems with Using Long Words Needlessly",
            "reference": "Dr. Daniel M. Oppenheimer (2006). Applied Cognitive Psychology, 20(2), 139-156. DOI: 10.1002/acp.1178",
            "facts": [
                "Càng dùng từ ngữ khó hiểu càng bị đánh giá là kém thông minh.",
                "Từ ngữ rườm rà chỉ là tấm khiên che đậy sự mơ hồ trong tư duy.",
            ],
        },
        {
            "id": "SRC02",
            "title": "The Feynman Technique: The Best Way to Learn Anything",
            "reference": "Dr. Richard P. Feynman (1965). The Pleasure of Finding Things Out. Basic Books. ISBN: 978-0465023950",
            "facts": [
                "Nếu không giải thích được cho một đứa trẻ nghĩa là bạn chưa hiểu.",
                "Điểm phải dùng từ hàn lâm chính là nơi kiến thức bị đứt gãy.",
            ],
        },
    ]

    reqs_1 = [
        {"id": "R01", "text": "Ảo giác uyên bác khi lạm dụng từ ngữ đao to búa lớn"},
        {"id": "R02", "text": "Thói quen nhồi nhét thuật ngữ hàn lâm vào tiểu luận đêm khuya"},
        {"id": "R03", "text": "Thực nghiệm Princeton chứng minh tác hại của việc dùng từ rườm rà"},
        {"id": "R04", "text": "Kỹ thuật Feynman giải thích bản chất cho một đứa trẻ mười tuổi"},
        {"id": "R05", "text": "Khép vòng lặp nhận diện lỗ hổng kiến thức nơi buộc phải dùng từ hàn lâm"},
    ]

    chars = [{
        "id": "CH01",
        "name": "Nhân vật người que học thuật",
        "appearance": "Hình tượng người que đầu tròn trắng viền đen dày, mắt oval tối giản, tạo hình thống nhất trong ảnh toàn khung dọc",
        "outfit": "Áo sơ mi học thuật tối giản nét mực đen",
    }]

    pack_1 = PackagingSpec(
        youtube_title="Càng Dùng Từ Phức Tạp, Bạn Càng Chưa Hiểu Gì",
        visual_hook="Nhân vật người que đứng trước bảng chi chít chữ học thuật nhưng bong bóng suy nghĩ chỉ có dấu hỏi trống rỗng",
        text_overlay="TỪ NGỮ BẪY NÃO",
        contrast_pair="Thuật ngữ đao to búa lớn vs. Bản chất đời thường",
        funnel_tier="tier_1_broad",
        seo_keywords=["kỹ thuật feynman", "cái bẫy thuật ngữ", "học sâu", "tư duy nghiên cứu"],
    )

    scenes_1_defs = [
        (
            "SC01",
            "Ảo giác uyên bác khi lạm dụng từ ngữ đao to búa lớn",
            "Mở màn bằng cú tát sự thật vạch trần thói quen dùng từ ngữ phức tạp để che giấu sự mơ hồ",
            "Càng dùng từ ngữ phức tạp nghĩa là bạn càng chưa hiểu gì. Đằng sau những từ hoa mỹ thường chỉ là một đầu óc trống rỗng.",
            ["R01"],
            ["SRC01"],
            "Nhân vật người que đứng trước bảng đen chi chít chữ học thuật nhưng đầu óc trống rỗng",
            "Giảng đường đại học với bảng đen viết đầy chữ thuật ngữ đao to búa lớn",
            "analytical_crisp",
            [
                ("Càng dùng từ ngữ phức tạp nghĩa là bạn càng chưa hiểu gì", "SRC01", "Càng dùng từ ngữ khó hiểu càng bị đánh giá là kém thông minh."),
            ],
            [
                ResearchedBeat(
                    image_id="SC01_I1",
                    description="Một bàn tay người que cầm bút đen viết lên trang giấy trắng, ngòi bút lướt nhanh tạo thành những dòng chữ nguệch ngoạc trừu tượng, góc nhìn cận cảnh từ trên xuống.",
                    anchor_quote="Càng dùng từ ngữ phức tạp",
                    reason="Cận cảnh ngòi bút tạo ra các từ ngữ phức tạp.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC01_I2",
                    description="Nhân vật người que đứng lúng túng giữa giảng đường lớn trước tấm bảng đen phủ kín các phương trình và thuật ngữ đao to búa lớn, hai tay buông thõng bối rối.",
                    anchor_quote="nghĩa là bạn càng chưa hiểu gì",
                    reason="Toàn cảnh nhân vật đứng trước khối thuật ngữ đồ sộ.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC01_I3",
                    description="Nhân vật người que đứng trước bảng đen, phía trên đầu là một bong bóng suy nghĩ bọc lớp vỏ chữ nghĩa hoa mỹ lấp lánh, nhưng bị cây kim chọc thủng xì hơi để lộ ra bên trong hoàn toàn rỗng tuếch.",
                    anchor_quote="Đằng sau những từ hoa mỹ thường chỉ là một đầu óc trống rỗng",
                    reason="Bong bóng chữ nghĩa bị kim chọc thủng xì hơi lộ ra bên trong rỗng tuếch.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="variation",
                    based_on="SC01_I2",
                    preserve="Keep the exact lecture hall, black board with dense equations, camera framing and stick figure appearance from the base scene. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Above the stick figure's head, an ornate thought bubble covered in shimmering academic words is pierced by a sharp needle, deflating to reveal an empty void inside.",
                ),
            ],
        ),
        (
            "SC02",
            "Thói quen nhồi nhét thuật ngữ hàn lâm vào tiểu luận đêm khuya",
            "Mô tả ma sát thực tế khi viết tiểu luận và cú sốc khi bị yêu cầu diễn đạt bằng tiếng Việt bình dân",
            "Đêm làm tiểu luận, bạn cố nhồi những từ ngữ hàn lâm để bài viết có vẻ uyên bác. [pause:900ms] Nhưng khi giảng viên yêu cầu giải thích bằng tiếng Việt đời thường, bạn lập tức đứng hình.",
            ["R02"],
            ["SRC01"],
            "Nhân vật người que gõ bàn phím tự đắc đêm khuya nhưng đứng hình trước câu hỏi của giảng viên",
            "Góc học tập ban đêm chuyển cảnh sang phòng hội thảo đại học",
            "narrative_warm",
            [
                ("bạn cố nhồi những từ ngữ hàn lâm", "SRC01", "Từ ngữ rườm rà chỉ là tấm khiên che đậy sự mơ hồ trong tư duy."),
            ],
            [
                ResearchedBeat(
                    image_id="SC02_I1",
                    description="Góc học tập ban đêm tĩnh mịch, đèn bàn vàng chiếu sáng một góc phòng, nhân vật người que ngồi chăm chú gõ bàn phím laptop trong tư thế tự đắc.",
                    anchor_quote="Đêm làm tiểu luận",
                    reason="Thiết lập bối cảnh bàn học quen thuộc lúc đêm muộn.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC02_I2",
                    description="Góc nhìn cận cảnh màn hình laptop hiển thị trang soạn thảo văn bản với dòng tiêu đề lớn phương pháp luận biện chứng được tô đậm màu mực đen.",
                    anchor_quote="bạn cố nhồi những từ ngữ hàn lâm để bài viết có vẻ uyên bác",
                    reason="Cận cảnh màn hình bài viết cố tỏ ra uyên bác.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC02_I3",
                    description="Phòng hội thảo sáng trưng, một vị giảng viên đeo kính đứng khoanh tay, chỉ ngón tay về phía nhân vật người que với ánh mắt đặt câu hỏi chất vấn nghiêm túc.",
                    anchor_quote="Nhưng khi giảng viên yêu cầu giải thích bằng tiếng Việt đời thường",
                    reason="Chuyển bối cảnh sang phòng hội thảo và câu hỏi phản biện đời thường.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="variation",
                    based_on="SC02_I1",
                    preserve="Keep room layout, window geometry, furniture, props and figure design. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Show the described full-frame scene.",
                ),
                ResearchedBeat(
                    image_id="SC02_I4",
                    description="Nhân vật người que đứng sau bục thuyết trình, hai mắt mở to bối rối, những giọt mồ hôi rơi xuống, chiếc micro trước mặt im bặt không thể phát ra lời giải thích.",
                    anchor_quote="bạn lập tức đứng hình",
                    reason="Biến thể cận cảnh trạng thái đông cứng của nhân vật khi không dùng được thuật ngữ.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="variation",
                    based_on="SC02_I3",
                    preserve="Keep the conference room lighting, wall backdrop and general atmosphere from the base scene. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Focus on the stick figure behind the presentation podium sweating nervously with wide dot eyes, unable to speak into the microphone.",
                ),
            ],
        ),
        (
            "SC03",
            "Thực nghiệm Princeton chứng minh tác hại của việc dùng từ rườm rà",
            "Dẫn chứng nghiên cứu khoa học Q1 của Oppenheimer vạch trần việc lạm dụng từ khó làm giảm uy tín",
            "Thực nghiệm tại Đại học Princeton đã chứng minh một sự thật rất bất ngờ. Những bài viết càng lạm dụng từ đao to búa lớn lại càng bị đánh giá là kém thông minh hơn.",
            ["R03"],
            ["SRC01"],
            "Bàn thực nghiệm đối chiếu hai văn bản và biểu đồ đánh giá trí thông minh",
            "Phòng thực nghiệm tâm lý học tại Đại học Princeton",
            "analytical_crisp",
            [
                ("Những bài viết càng lạm dụng từ đao to búa lớn lại càng bị đánh giá là kém thông minh hơn", "SRC01", "Càng dùng từ ngữ khó hiểu càng bị đánh giá là kém thông minh."),
            ],
            [
                ResearchedBeat(
                    image_id="SC03_I1",
                    description="Phòng thực nghiệm tâm lý học với chiếc bàn gỗ lớn, trên bàn đặt hai tập hồ sơ tài liệu được gắn nhãn đối chứng nghiên cứu khoa học rõ ràng.",
                    anchor_quote="Thực nghiệm tại Đại học Princeton",
                    reason="Thiết lập không gian phòng thí nghiệm Princeton.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC03_I2",
                    description="Góc nhìn cận cảnh chiếc phong bì hồ sơ dán tem niêm phong thực nghiệm nghiên cứu nhận thức của Đại học Princeton.",
                    anchor_quote="đã chứng minh một sự thật rất bất ngờ",
                    reason="Cận cảnh hồ sơ thực nghiệm tạo tính xác thực học thuật.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC03_I3",
                    description="Góc nhìn cận cảnh tập hồ sơ bên phải phủ đầy các dòng chữ hàn lâm rườm rà bị một chiếc bút lông đỏ gạch một dấu chéo lớn cảnh báo.",
                    anchor_quote="Những bài viết càng lạm dụng từ đao to búa lớn",
                    reason="Cận cảnh tập hồ sơ dùng từ rườm rà bị đánh dấu phê bình.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC03_I4",
                    description="Tấm bảng trắng thực nghiệm với biểu đồ hai cột đối chiếu: cột văn bản giản dị vươn cao với ngôi sao sáng, cột văn bản dùng từ phức tạp tụt sâu xuống đáy.",
                    anchor_quote="lại càng bị đánh giá là kém thông minh hơn",
                    reason="Minh họa biểu đồ kết quả thực nghiệm tâm lý học.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="white_card",
                ),
            ],
        ),
        (
            "SC04",
            "Kỹ thuật Feynman giải thích bản chất cho một đứa trẻ mười tuổi",
            "Hướng dẫn phương pháp Feynman: giải thích cho một đứa trẻ để kiểm tra độ sâu của hiểu biết",
            "Để phá vỡ cái bẫy này, hãy dùng ngay kỹ thuật Feynman kinh điển. Bạn phải giải thích sao cho một đứa trẻ mười tuổi cũng hiểu được, mà cấm dùng từ chuyên môn.",
            ["R04"],
            ["SRC02"],
            "Nhân vật người que ngồi đối thoại với đứa trẻ và vẽ sơ đồ trực quan đơn giản",
            "Phòng học sáng sủa với bảng đen và bàn gỗ nhỏ",
            "narrative_warm",
            [
                ("Bạn phải giải thích sao cho một đứa trẻ mười tuổi cũng hiểu được", "SRC02", "Nếu không giải thích được cho một đứa trẻ nghĩa là bạn chưa hiểu."),
            ],
            [
                ResearchedBeat(
                    image_id="SC04_I1",
                    description="Nhân vật người que đứng cạnh chiếc bảng xanh học thuật, cầm phấn viết tên nguyên lý Feynman lên góc trên bên trái của bảng.",
                    anchor_quote="Để phá vỡ cái bẫy này",
                    reason="Giới thiệu kỹ thuật tư duy Feynman.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC04_I2",
                    description="Chiếc bảng xanh học thuật nổi bật dòng chữ viết phấn trắng mô hình 4 bước đơn giản hóa của nhà vật lý Feynman.",
                    anchor_quote="hãy dùng ngay kỹ thuật Feynman kinh điển",
                    reason="Cận cảnh mô hình 4 bước Feynman trên bảng.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC04_I3",
                    description="Nhân vật người que ngồi trên ghế gỗ đối diện một đứa trẻ mười tuổi mắt tròn xoe lắng nghe, ở giữa là chiếc bàn tròn nhỏ đặt cuốn sổ tay mở sẵn.",
                    anchor_quote="Bạn phải giải thích sao cho một đứa trẻ mười tuổi cũng hiểu được",
                    reason="Cảnh đối thoại giữa người học và một đứa trẻ mười tuổi.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="variation",
                    based_on="SC04_I1",
                    preserve="Keep room layout, window geometry, furniture, props and figure design. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Show the described full-frame scene.",
                ),
                ResearchedBeat(
                    image_id="SC04_I4",
                    description="Trên bảng đen phía sau, người que dùng phấn trắng vẽ sơ đồ hình quả táo mộc mạc chia đôi với các mũi tên minh họa đơn giản không chứa chữ viết.",
                    anchor_quote="mà cấm dùng từ chuyên môn",
                    reason="Minh họa cơ chế bằng hình vẽ đời thường thay vì từ ngữ chuyên môn.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="variation",
                    based_on="SC04_I3",
                    preserve="Keep the room, wooden chairs, round table, stick figure and child from the base scene. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Focus towards the blackboard behind where the stick figure draws a simple split-apple diagram with intuitive arrows without any text.",
                ),
            ],
        ),
        (
            "SC05",
            "Khép vòng lặp nhận diện lỗ hổng kiến thức nơi buộc phải dùng từ hàn lâm",
            "Đúc kết quy luật cốt lõi và gửi gắm thông điệp tinh giản hóa để làm chủ tri thức",
            "Điểm nào bạn buộc phải viện đến từ ngữ hoa mỹ, chính là nơi bạn chưa hiểu bản chất. [pause:500ms] Hãy đơn giản hóa câu từ để thực sự làm chủ tri thức.",
            ["R05"],
            ["SRC02"],
            "Nhân vật người que khoanh vùng điểm đứt gãy và mỉm cười cầm tờ giấy kết luận giản dị",
            "Góc học tập sáng sủa với ánh nắng ban mai",
            "reflective_slow",
            [
                ("Điểm nào bạn buộc phải viện đến từ ngữ hoa mỹ, chính là nơi bạn chưa hiểu bản chất", "SRC02", "Điểm phải dùng từ hàn lâm chính là nơi kiến thức bị đứt gãy."),
            ],
            [
                ResearchedBeat(
                    image_id="SC05_I1",
                    description="Cận cảnh sơ đồ tư duy trên mặt giấy, bàn tay người que cầm bút đỏ khoanh một vòng tròn nổi bật quanh một điểm nối bị đứt gãy giữa hai ý niệm.",
                    anchor_quote="Điểm nào bạn buộc phải viện đến từ ngữ hoa mỹ",
                    reason="Cận cảnh điểm đứt gãy kiến thức nơi người học phải dựa vào từ ngữ hoa mỹ.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC05_I2",
                    description="Tờ giấy trắng tinh với ba dòng chữ tóm tắt cốt lõi ngắn gọn sáng rõ, không chứa bất kỳ từ ngữ thuật ngữ hàn lâm trừu tượng nào.",
                    anchor_quote="chính là nơi bạn chưa hiểu bản chất",
                    reason="Cận cảnh tờ giấy kết luận giản dị trần trụi.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="white_card",
                ),
                ResearchedBeat(
                    image_id="SC05_I3",
                    description="Bàn tay người que cầm bút gạch bỏ những từ ngữ hoa mỹ rườm rà, thay bằng cách diễn đạt ngắn gọn dễ hiểu.",
                    anchor_quote="Hãy đơn giản hóa câu từ",
                    reason="Cận cảnh hành động đơn giản hóa câu từ để thấu suốt bản chất.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC05_I4",
                    description="Góc học tập sáng sủa với ánh nắng ban mai rọi qua cửa sổ, nhân vật người que mỉm cười thư thái, hai tay cầm tờ giấy trắng tinh chỉ ghi một kết luận sáng rõ.",
                    anchor_quote="để thực sự làm chủ tri thức",
                    reason="Khép vòng lặp với cảm giác tự tin làm chủ bản chất tri thức.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="full_scene",
                ),
            ],
        ),
    ]

    scenes_1 = []
    for sc_id, title, purp, narr, req, src, act, sett, tone, clms, beats in scenes_1_defs:
        is_last = (sc_id == "SC05")
        rep = SceneCadenceReport(sc_id, 10.0, narr, is_last=is_last)
        scenes_1.append(
            ResearchedScene(
                scene_id=sc_id,
                title=title,
                purpose=purp,
                duration=rep.estimated_audio_duration,
                narration=narr,
                requirements=req,
                source_ids=src,
                character_ids=["CH01"],
                action=act,
                setting=sett,
                camera="Semantic full-frame sequence",
                tone=tone,
                claim_facts=clms,
                visual_beats=beats,
            )
        )

    topic_1 = ResearchedTopic(
        topic="Kỹ Thuật Feynman và Cái Bẫy Thuật Ngữ Hàn Lâm: Giải mã cơ chế ảo giác uyên bác khi dùng từ ngữ đao to búa lớn",
        audience="Sinh viên, học viên cao học và người tự học tại Việt Nam",
        goal="Phá vỡ cái bẫy từ ngữ hàn lâm, áp dụng kỹ thuật Feynman giải thích bản chất vấn đề cho đứa trẻ 10 tuổi",
        video_type="science",
        min_duration=45.0,
        max_duration=60.0,
        style="Minh hoạ Editorial Graphic 2D toàn khung, nhân vật người que viền đen dày tương tác trực tiếp với bảng vẽ và trang giấy trong cùng bố cục, khung dọc 9:16.",
        aspect_ratio="9:16",
        format_profile="short_9x16",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        packaging=pack_1,
        characters=chars,
        sources=sources_1,
        required_points=reqs_1,
        scenes=scenes_1,
    )

    # -------------------------------------------------------------
    # 2. SPINOFF 02: feynman-jargon-trap-spinoff-02-9x16
    # -------------------------------------------------------------
    sources_2 = [
        {
            "id": "SRC01",
            "title": "The Pleasure of Finding Things Out: What Is and What Should Be",
            "reference": "Dr. Richard P. Feynman (1965). Basic Books. ISBN: 978-0465023950",
            "facts": [
                "Biết tên một sự vật khác hoàn toàn với việc hiểu nó.",
                "Điểm phải dùng từ hàn lâm chính là nơi kiến thức bị hổng.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Cognitive Load During Problem Solving",
            "reference": "Dr. John Sweller (1988). Cognitive Science, 12(2), 257-285. DOI: 10.1207/s15516709cog1202_4",
            "facts": [
                "Định nghĩa phức tạp làm tắc nghẽn bộ nhớ làm việc.",
                "Hình ảnh trực quan mộc mạc giúp giải phóng dung lượng não.",
            ],
        },
    ]

    reqs_2 = [
        {"id": "R01", "text": "Ảo giác hiểu biết khi học thuộc lòng tên gọi khoa học"},
        {"id": "R02", "text": "Khác biệt giữa việc biết tên và hiểu bản chất cơ chế"},
        {"id": "R03", "text": "Quy tắc đứa trẻ mười tuổi và lệnh cấm dùng từ chuyên môn"},
        {"id": "R04", "text": "Phát hiện lỗ hổng tri thức tại nơi câu từ bị tắc nghẽn"},
        {"id": "R05", "text": "Khép vòng lặp biến kiến thức trừu tượng thành trực giác sống động"},
    ]

    pack_2 = PackagingSpec(
        youtube_title="Kỹ Thuật Feynman: Quy Tắc Đứa Trẻ 10 Tuổi",
        visual_hook="Nhân vật người que ngồi ngang hàng với một đứa trẻ mười tuổi và vẽ sơ đồ trực quan",
        text_overlay="ĐỨA TRẺ 10 TUỔI",
        contrast_pair="Nhớ vẹt tên gọi vs. Hiểu sâu bản chất",
        funnel_tier="tier_1_broad",
        seo_keywords=["kỹ thuật feynman", "quy tắc đứa trẻ 10 tuổi", "học sâu", "tư duy bản chất"],
    )

    scenes_2_defs = [
        (
            "SC01",
            "Ảo giác hiểu biết khi học thuộc lòng tên gọi khoa học",
            "Mở màn bằng cú tát sự thật về quy tắc đứa trẻ của Feynman",
            "Không giải thích nổi cho một đứa trẻ, nghĩa là bạn chưa hiểu gì cả. Thuộc lòng từng câu chữ trong sách vở chỉ là một cái vỏ bọc rỗng tuếch.",
            ["R01"],
            ["SRC01"],
            "Nhân vật người que bối rối trước đứa trẻ khi cầm cuốn giáo trình rỗng",
            "Phòng khách gia đình ấm cúng với kệ sách phía sau",
            "analytical_crisp",
            [
                ("Không giải thích nổi cho một đứa trẻ, nghĩa là bạn chưa hiểu gì cả", "SRC01", "Biết tên một sự vật khác hoàn toàn với việc hiểu nó."),
            ],
            [
                ResearchedBeat(
                    image_id="SC01_I1",
                    description="Một đứa trẻ mười tuổi mắt tròn xoe ngơ ngác nhìn lên người lớn, khuôn mặt biểu lộ sự tò mò trong trẻo.",
                    anchor_quote="Không giải thích nổi cho một đứa trẻ",
                    reason="Cận cảnh gương mặt đứa trẻ làm trọng tâm thử thách.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC01_I2",
                    description="Nhân vật người que đứng lúng túng trước đứa trẻ, hai tay cầm cuốn giáo trình dày cộp không biết bắt đầu từ đâu.",
                    anchor_quote="nghĩa là bạn chưa hiểu gì cả",
                    reason="Toàn cảnh sự bế tắc của người học.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="variation",
                    based_on="SC01_I1",
                    preserve="Keep room layout, window geometry, furniture, props and figure design. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Show the described full-frame scene.",
                ),
                ResearchedBeat(
                    image_id="SC01_I3",
                    description="Hình ảnh một cuốn sách giáo trình mở ra nhưng bên trong các trang giấy đều trống rỗng không có chữ viết.",
                    anchor_quote="Thuộc lòng từng câu chữ trong sách vở",
                    reason="Ẩn dụ trực quan về cái vỏ rỗng tuếch của việc học vẹt.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="white_card",
                ),
                ResearchedBeat(
                    image_id="SC01_I4",
                    description="Cận cảnh một dấu hỏi chấm lớn màu đỏ in hằn lên giữa trang sách giáo trình trống rỗng.",
                    anchor_quote="chỉ là một cái vỏ bọc rỗng tuếch",
                    reason="Cận cảnh dấu hỏi chấm cảnh báo ảo giác năng lực.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="macro_prop",
                ),
            ],
        ),
        (
            "SC02",
            "Khác biệt giữa việc biết tên và hiểu bản chất cơ chế",
            "Chỉ ra mâu thuẫn giữa điểm số thi cử và khả năng áp dụng thực tế",
            "Bạn đọc làu làu từng khái niệm trong giáo trình để vượt qua bài kiểm tra. [pause:900ms] Nhưng khi đối diện bài toán đời thực, não bạn hoàn toàn tê liệt. Mọi kiến thức biến mất.",
            ["R02"],
            ["SRC02"],
            "Người que vượt qua bài thi nhưng tê liệt trước cỗ máy hỏng thực tế",
            "Phòng học chuyển cảnh sang xưởng thực hành cơ khí",
            "narrative_warm",
            [
                ("não bạn hoàn toàn tê liệt", "SRC02", "Định nghĩa phức tạp làm tắc nghẽn bộ nhớ làm việc."),
            ],
            [
                ResearchedBeat(
                    image_id="SC02_I1",
                    description="Nhân vật người que ngồi bên bàn học chăm chú đọc to từng trang giáo trình dưới ánh đèn vàng.",
                    anchor_quote="Bạn đọc làu làu từng khái niệm trong giáo trình",
                    reason="Thiết lập bối cảnh học vẹt quen thuộc.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC02_I2",
                    description="Tờ bài thi học kỳ với điểm số cao màu đỏ nằm ngay ngắn trên bàn học.",
                    anchor_quote="để vượt qua bài kiểm tra",
                    reason="Cận cảnh tờ bài thi điểm cao tạo ảo giác năng lực.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC02_I3",
                    description="Một cỗ máy cơ khí thực tế bị hỏng hóc đang bốc khói nhẹ, đòi hỏi người học phải xử lý ngay.",
                    anchor_quote="Nhưng khi đối diện bài toán đời thực",
                    reason="Tình huống thực tế đầy thách thức.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="variation",
                    based_on="SC02_I1",
                    preserve="Keep room layout, window geometry, furniture, props and figure design. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Show the described full-frame scene.",
                ),
                ResearchedBeat(
                    image_id="SC02_I4",
                    description="Người que đứng trước cỗ máy hỏng, hai tay ôm đầu bối rối với đôi mắt mở to chết lặng.",
                    anchor_quote="não bạn hoàn toàn tê liệt",
                    reason="Trạng thái tê liệt trước bài toán đời thực.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="variation",
                    based_on="SC02_I3",
                    preserve="Keep the workshop machinery, smoking components and dramatic overhead spotlight from the base scene. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Focus on the stick figure grasping head in utter paralysis before the smoking machine.",
                ),
            ],
        ),
        (
            "SC03",
            "Bản chất của tên gọi và sự thấu suốt cơ chế",
            "Dẫn lời Richard Feynman phân biệt giữa nhãn mác tên gọi và cơ chế bản chất",
            "Nhà vật lý Richard Feynman từng chỉ ra một sự thật rất sâu sắc. Biết tên gọi của một hiện tượng, hoàn toàn không đồng nghĩa với việc bạn hiểu cơ chế của nó.",
            ["R03"],
            ["SRC01"],
            "Feynman chỉ vào cuốn sổ tay và gạch bỏ tên gọi phức tạp",
            "Giảng đường vật lý cổ điển",
            "analytical_crisp",
            [
                ("không đồng nghĩa với việc bạn hiểu cơ chế của nó", "SRC01", "Biết tên một sự vật khác hoàn toàn với việc hiểu nó."),
            ],
            [
                ResearchedBeat(
                    image_id="SC03_I1",
                    description="Nhà vật lý Richard Feynman đứng mỉm cười hóm hỉnh bên tấm bảng giảng đường với chiếc áo sơ mi xắn tay áo mộc mạc.",
                    anchor_quote="Nhà vật lý Richard Feynman từng chỉ ra",
                    reason="Chân dung nhà vật lý Feynman giản dị.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC03_I2",
                    description="Cận cảnh trang sổ tay của nhà vật lý Feynman, một bàn tay cầm bút gạch bỏ dòng chữ tên gọi phức tạp ở phía trên, chỉ giữ lại hình vẽ minh họa sinh động trực quan ở bên dưới.",
                    anchor_quote="một sự thật rất sâu sắc",
                    reason="Cận cảnh trang sổ tay Feynman gạch bỏ tên gọi phức tạp, ưu tiên hình vẽ cơ chế.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC03_I3",
                    description="Một tấm thẻ nhãn mác đề tên khoa học dài dòng rơi xuống, để lộ ra khoảng trống không có bất kỳ giải thích bản chất nào.",
                    anchor_quote="Biết tên gọi của một hiện tượng",
                    reason="Cận cảnh nhãn mác rơi xuống rỗng tuếch.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="white_card",
                ),
                ResearchedBeat(
                    image_id="SC03_I4",
                    description="Nhân vật người que đứng tần ngần nhìn chiếc nhãn mác rơi, nhận ra sự khác biệt giữa cái tên và bản chất thực tế.",
                    anchor_quote="không đồng nghĩa với việc bạn hiểu cơ chế của nó",
                    reason="Nhận thức thức tỉnh về bản chất của tri thức.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="full_scene",
                ),
            ],
        ),
        (
            "SC04",
            "Phát hiện lỗ hổng tri thức tại nơi câu từ bị tắc nghẽn",
            "Mô tả quy tắc thực hành Feynman: giải thích cho đứa trẻ 10 tuổi và cấm thuật ngữ",
            "Phương pháp của ông rất rõ ràng. Bạn phải giải thích lại sao cho một đứa bé mười tuổi cũng hiểu được, mà nghiêm cấm dùng mọi thuật ngữ chuyên môn hay từ ngữ hoa mỹ.",
            ["R04"],
            ["SRC02"],
            "Người que thực hành quy tắc giải thích cho đứa trẻ và gạt bỏ từ điển thuật ngữ",
            "Phòng học sáng sủa với bảng vẽ và bàn nhỏ",
            "narrative_warm",
            [
                ("sao cho một đứa bé mười tuổi cũng hiểu được", "SRC02", "Hình ảnh trực quan mộc mạc giúp giải phóng dung lượng não."),
            ],
            [
                ResearchedBeat(
                    image_id="SC04_I1",
                    description="Nhân vật người que đứng cạnh tấm bảng đen, vẽ số mười thật lớn biểu trưng cho quy tắc đứa trẻ mười tuổi.",
                    anchor_quote="Phương pháp của ông rất rõ ràng",
                    reason="Giới thiệu con số mười biểu tượng.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC04_I2",
                    description="Đứa trẻ mười tuổi ngồi trên ghế chăm chú lắng nghe, đối diện người que đang giải thích mộc mạc.",
                    anchor_quote="sao cho một đứa bé mười tuổi cũng hiểu được",
                    reason="Khung cảnh tương tác dạy học tự nhiên.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="variation",
                    based_on="SC04_I1",
                    preserve="Keep room layout, window geometry, furniture, props and figure design. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Show the described full-frame scene.",
                ),
                ResearchedBeat(
                    image_id="SC04_I3",
                    description="Một chiếc biển báo cấm màu đỏ gạch chéo cuốn từ điển thuật ngữ dày cộp.",
                    anchor_quote="mà nghiêm cấm dùng mọi thuật ngữ chuyên môn",
                    reason="Cận cảnh biển báo cấm thuật ngữ chuyên môn.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC04_I4",
                    description="Người que dùng ngón tay chỉ vào các hình vẽ minh họa đơn giản trên trang giấy thay vì các từ ngữ hoa mỹ.",
                    anchor_quote="hay từ ngữ hoa mỹ",
                    reason="Biến thể người que kiên trì dùng hình vẽ mộc mạc.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="variation",
                    based_on="SC04_I2",
                    preserve="Keep the child on the chair, round table and cozy room setting from the base scene. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Focus on the stick figure enthusiastically pointing to simple sketches on a paper pad instead of fancy words.",
                ),
            ],
        ),
        (
            "SC05",
            "Khép vòng lặp biến kiến thức trừu tượng thành trực giác sống động",
            "Đúc kết quy luật: điểm nghẽn câu từ là lỗ hổng tri thức và kết thúc bằng thành quả thấu suốt",
            "Nơi nào bạn buộc phải viện đến từ ngữ phức tạp, chính nơi đó kiến thức bị đứt gãy. [pause:500ms] Khi đứa trẻ mỉm cười gật đầu, bạn đã thực sự làm chủ tri thức.",
            ["R05"],
            ["SRC01"],
            "Người que ghép vừa vặn mảnh ghép kiến thức và cùng đứa trẻ mỉm cười thấu suốt",
            "Phòng học sáng bừng ánh nắng mai",
            "reflective_slow",
            [
                ("Nơi nào bạn buộc phải viện đến từ ngữ phức tạp, chính nơi đó kiến thức bị đứt gãy", "SRC01", "Điểm phải dùng từ hàn lâm chính là nơi kiến thức bị hổng."),
            ],
            [
                ResearchedBeat(
                    image_id="SC05_I1",
                    description="Cận cảnh một bộ trò chơi xếp hình mảnh ghép kiến thức trên mặt bàn gỗ, ở giữa có một khoảng trống bị hổng thiếu một mảnh ghép nối.",
                    anchor_quote="Nơi nào bạn buộc phải viện đến từ ngữ phức tạp",
                    reason="Cận cảnh mảnh ghép kiến thức bị hổng giữa chừng.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC05_I2",
                    description="Bàn tay người que cẩn thận cầm một mảnh ghép có vẽ hình minh họa đơn giản đặt vào vừa khít khoảng trống bị hổng trên bộ xếp hình.",
                    anchor_quote="chính nơi đó kiến thức bị đứt gãy",
                    reason="Bàn tay đặt mảnh ghép hình vẽ đơn giản vào vừa khít khoảng trống.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC05_I3",
                    description="Đứa trẻ mười tuổi mỉm cười rạng rỡ gật đầu tán thưởng, hai mắt sáng ngời vì đã hiểu ra cơ chế.",
                    anchor_quote="Khi đứa trẻ mỉm cười gật đầu",
                    reason="Cận cảnh nụ cười hiểu bài của đứa trẻ.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC05_I4",
                    description="Nhân vật người que mỉm cười tự tin bên bàn học, một biểu tượng bóng đèn vàng rực sáng trên đầu.",
                    anchor_quote="bạn đã thực sự làm chủ tri thức",
                    reason="Khép lại với hình ảnh làm chủ tri thức vững vàng.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="variation",
                    based_on="SC05_I3",
                    preserve="Keep room layout, window geometry, furniture, props and figure design. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Show the described full-frame scene.",
                ),
            ],
        ),
    ]

    scenes_2 = []
    for sc_id, title, purp, narr, req, src, act, sett, tone, clms, beats in scenes_2_defs:
        is_last = (sc_id == "SC05")
        rep = SceneCadenceReport(sc_id, 10.0, narr, is_last=is_last)
        scenes_2.append(
            ResearchedScene(
                scene_id=sc_id,
                title=title,
                purpose=purp,
                duration=rep.estimated_audio_duration,
                narration=narr,
                requirements=req,
                source_ids=src,
                character_ids=["CH01"],
                action=act,
                setting=sett,
                camera="Semantic full-frame sequence",
                tone=tone,
                claim_facts=clms,
                visual_beats=beats,
            )
        )

    topic_2 = ResearchedTopic(
        topic="Kỹ Thuật Feynman: Quy Tắc Đứa Trẻ 10 Tuổi Giúp Đập Tan Ảo Giác Nhớ Vẹt Định Nghĩa",
        audience="Sinh viên, học sinh và người tự học tại Việt Nam",
        goal="Phân biệt giữa nhớ tên gọi và hiểu bản chất, áp dụng quy tắc đứa trẻ 10 tuổi để kiểm tra hiểu biết",
        video_type="science",
        min_duration=45.0,
        max_duration=60.0,
        style="Minh hoạ Editorial Graphic 2D toàn khung, nhân vật người que viền đen dày tương tác trực tiếp với đứa trẻ và trang giấy trong cùng bố cục, khung dọc 9:16.",
        aspect_ratio="9:16",
        format_profile="short_9x16",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        packaging=pack_2,
        characters=chars,
        sources=sources_2,
        required_points=reqs_2,
        scenes=scenes_2,
    )

    # -------------------------------------------------------------
    # 3. SPINOFF 03: feynman-jargon-trap-spinoff-03-9x16
    # -------------------------------------------------------------
    sources_3 = [
        {
            "id": "SRC01",
            "title": "Consequences of Erudite Vernacular Utilized Irrespective of Necessity",
            "reference": "Dr. Daniel M. Oppenheimer (2006). Applied Cognitive Psychology, 20(2), 139-156. DOI: 10.1002/acp.1178",
            "facts": [
                "Thuật ngữ rườm rà làm suy giảm uy tín của bài viết.",
                "Người nghe luôn cảnh giác khi gặp các câu từ sáo rỗng.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Genre Analysis: English in Academic and Research Settings",
            "reference": "Dr. John M. Swales (1990). Cambridge University Press. ISBN: 978-0521338134",
            "facts": [
                "Hội đồng luôn soi bản chất nghiên cứu thay vì slide màu mè.",
                "Giải thích ngắn gọn ba câu giúp chiếm trọn lòng tin hội đồng.",
            ],
        },
    ]

    reqs_3 = [
        {"id": "R01", "text": "Cái bẫy biến thuật ngữ thành chiếc nạng ru ngủ não bộ"},
        {"id": "R02", "text": "Nỗi sợ phòng bảo vệ và thói quen lấp liếm bằng slide dày đặc chữ"},
        {"id": "R03", "text": "Bản chất của thuật ngữ khoa học là công cụ nén chứ không phải tấm khiên"},
        {"id": "R04", "text": "Bài test tờ giấy trắng viết ba câu đời thường trước giờ lên bục"},
        {"id": "R05", "text": "Khép vòng lặp làm chủ một trăm hai mươi giây đầu phòng bảo vệ"},
    ]

    pack_3 = PackagingSpec(
        youtube_title="Bài Test Tờ Giấy Trắng Trước Giờ Bảo Vệ Khóa Luận",
        visual_hook="Tờ giấy trắng tinh với ba câu kết luận ngắn gọn bên cạnh chiếc micro phòng bảo vệ",
        text_overlay="TỜ GIẤY TRẮNG",
        contrast_pair="Chiếc nạng thuật ngữ vs. Tờ giấy trắng bản chất",
        funnel_tier="tier_2_mid",
        seo_keywords=["bảo vệ khóa luận", "bài test tờ giấy trắng", "chiếc nạng ngôn từ", "tâm lý hội đồng"],
    )

    scenes_3_defs = [
        (
            "SC01",
            "Cái bẫy biến thuật ngữ thành chiếc nạng ru ngủ não bộ",
            "Mở màn bằng cú tát sự thật về việc dùng slide màu mè và thuật ngữ làm chiếc nạng",
            "Thuật ngữ học thuật đang biến thành chiếc nạng ru ngủ não bạn. Càng che đậy bằng slide màu mè, bạn càng dễ bị đánh gục trên bục bảo vệ.",
            ["R01"],
            ["SRC01"],
            "Chiếc nạng gỗ bên bục thuyết trình và màn chiếu sặc sỡ rung lắc",
            "Phòng bảo vệ khóa luận với bục thuyết trình và màn chiếu",
            "analytical_crisp",
            [
                ("Thuật ngữ học thuật đang biến thành chiếc nạng ru ngủ não bạn", "SRC01", "Thuật ngữ rườm rà làm suy giảm uy tín của bài viết."),
            ],
            [
                ResearchedBeat(
                    image_id="SC01_I1",
                    description="Một cặp nạng gỗ tựa vào bục giảng đường bên cạnh chiếc micro thuyết trình đơn độc.",
                    anchor_quote="Thuật ngữ học thuật đang biến thành chiếc nạng",
                    reason="Ẩn dụ trực quan về chiếc nạng thuật ngữ.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC01_I2",
                    description="Nhân vật người que bước đi khập khiễng trên bục giảng đường khi đang cố bấu víu vào chiếc nạng.",
                    anchor_quote="ru ngủ não bạn",
                    reason="Người học phụ thuộc vào chiếc nạng từ ngữ.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="variation",
                    based_on="SC01_I1",
                    preserve="Keep room layout, window geometry, furniture, props and figure design. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Show the described full-frame scene.",
                ),
                ResearchedBeat(
                    image_id="SC01_I3",
                    description="Màn hình trình chiếu với các hiệu ứng màu sắc sặc sỡ và khối chữ dày đặc đang rung lắc chực sụp đổ.",
                    anchor_quote="bạn càng dễ bị đánh gục trên bục bảo vệ",
                    reason="Cảnh báo sự sụp đổ của slide màu mè.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="white_card",
                ),
            ],
        ),
        (
            "SC02",
            "Nỗi sợ phòng bảo vệ và thói quen lấp liếm bằng slide dày đặc chữ",
            "Tái hiện ma sát tâm lý trước hội đồng bảo vệ và cú sốc khi bị hỏi vặn bản chất",
            "Trước giờ bảo vệ, nhiều bạn cố nhồi vào bài thuyết trình những thuật ngữ thật kêu. [pause:900ms] Nhưng chỉ cần một câu hỏi vặn từ hội đồng, toàn bộ vỏ bọc lập tức sụp đổ.",
            ["R02"],
            ["SRC01"],
            "Hành lang phòng thi căng thẳng và khoảnh khắc hội đồng lật tẩy câu từ sáo rỗng",
            "Hành lang trường đại học chuyển cảnh sang phòng bảo vệ khóa luận",
            "narrative_warm",
            [
                ("toàn bộ vỏ bọc lập tức sụp đổ", "SRC01", "Người nghe luôn cảnh giác khi gặp các câu từ sáo rỗng."),
            ],
            [
                ResearchedBeat(
                    image_id="SC02_I1",
                    description="Hành lang trường đại học tĩnh lặng, các ứng viên ngồi chờ trước cửa phòng bảo vệ khóa luận với vẻ mặt hồi hộp lo âu.",
                    anchor_quote="Trước giờ bảo vệ",
                    reason="Thiết lập không khí căng thẳng trước giờ G.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC02_I2",
                    description="Tập slide thuyết trình in sẵn chi chít chữ chuyên ngành và các khối sơ đồ phức tạp đặt trên bàn.",
                    anchor_quote="nhiều bạn cố nhồi vào bài thuyết trình những thuật ngữ thật kêu",
                    reason="Cận cảnh tập slide cố tình làm rối để che đậy sự mông lung.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC02_I3",
                    description="Vị chủ tịch hội đồng nhìn thẳng qua gọng kính, đưa ra một câu hỏi vặn xoáy vào bản chất của đề tài.",
                    anchor_quote="Nhưng chỉ cần một câu hỏi vặn từ hội đồng",
                    reason="Khoảnh khắc câu hỏi chất vấn bất ngờ từ hội đồng.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="variation",
                    based_on="SC02_I1",
                    preserve="Keep room layout, window geometry, furniture, props and figure design. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Show the described full-frame scene.",
                ),
                ResearchedBeat(
                    image_id="SC02_I4",
                    description="Màn hình máy chiếu phụt tắt, khối chữ học thuật hoa mỹ tan vỡ thành cát bụi trước ánh mắt thất vọng của hội đồng.",
                    anchor_quote="toàn bộ vỏ bọc lập tức sụp đổ",
                    reason="Hình ảnh ẩn dụ về sự sụp đổ của lớp vỏ bọc từ ngữ.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="variation",
                    based_on="SC02_I3",
                    preserve="Keep the committee room backdrop, judge desk and stern lighting from the base scene. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Focus towards the presentation screen shattering like glass into dust before the disappointed committee.",
                ),
            ],
        ),
        (
            "SC03",
            "Bản chất của thuật ngữ khoa học là công cụ nén chứ không phải tấm khiên",
            "Phân tích bản chất: thuật ngữ là công cụ nén thông tin, không thể thay thế tư duy cốt lõi",
            "Thuật ngữ sinh ra để các chuyên gia trao đổi nhanh, chứ không phải tấm khiên giấu dốt. Hội đồng luôn nhìn thấu sự mông lung đằng sau những câu chữ sáo rỗng.",
            ["R03"],
            ["SRC02"],
            "Hội đồng soi thấu tấm khiên rỗng và đối chiếu cán cân bản chất",
            "Phòng bảo vệ với bàn hội đồng nghiêm nghị",
            "analytical_crisp",
            [
                ("Hội đồng luôn nhìn thấu sự mông lung đằng sau những câu chữ sáo rỗng", "SRC02", "Hội đồng luôn soi bản chất nghiên cứu thay vì slide màu mè."),
            ],
            [
                ResearchedBeat(
                    image_id="SC03_I1",
                    description="Hình ảnh hai nhà khoa học bắt tay trao đổi bên một sơ đồ ký hiệu toán học súc tích ngắn gọn.",
                    anchor_quote="Thuật ngữ sinh ra để các chuyên gia trao đổi nhanh",
                    reason="Minh họa chức năng đúng đắn của thuật ngữ giữa các chuyên gia.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC03_I2",
                    description="Một chiếc khiên chắn bằng kim loại rỉ sét có khắc các dòng chữ học thuật trừu tượng.",
                    anchor_quote="chứ không phải tấm khiên giấu dốt",
                    reason="Cận cảnh chiếc khiên che giấu sự mơ hồ.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC03_I3",
                    description="Tia laser của hội đồng chiếu xuyên qua tấm khiên kim loại để lộ ra một dấu hỏi chấm trống rỗng.",
                    anchor_quote="Hội đồng luôn nhìn thấu sự mông lung",
                    reason="Hội đồng nhìn thấu sự mông lung.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC03_I4",
                    description="Hình ảnh một chiếc cán cân thăng bằng: một bên đĩa cân là chồng tài liệu dày cộp chữ nghĩa nhưng nhẹ bẫng bốc lên cao, bên kia là một viên kim cương nhỏ bản chất cốt lõi nặng trịch kéo lệch cán cân xuống.",
                    anchor_quote="đằng sau những câu chữ sáo rỗng",
                    reason="Ẩn dụ chiếc cán cân đối chiếu giữa chồng tài liệu nhẹ bẫng và viên kim cương bản chất nặng trịch.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="white_card",
                ),
            ],
        ),
        (
            "SC04",
            "Bài test tờ giấy trắng viết ba câu đời thường trước giờ lên bục",
            "Đưa ra bài test tờ giấy trắng thực chiến: tóm tắt đề tài bằng 3 câu đời thường",
            "Trước khi bước lên bục, hãy thử ngay quy tắc tờ giấy trắng. Viết lại toàn bộ thông điệp đề tài bằng đúng ba câu ngắn gọn, không dùng bất kỳ từ ngữ chuyên môn nào.",
            ["R04"],
            ["SRC02"],
            "Cây bút gạch bỏ từ ngữ chuyên ngành trên bản nháp và viết ba câu sáng rõ trên tờ giấy trắng tinh",
            "Bàn chuẩn bị trước phòng bảo vệ với đèn bàn và tờ giấy trắng",
            "narrative_warm",
            [
                ("Viết lại toàn bộ thông điệp đề tài bằng đúng ba câu ngắn gọn", "SRC02", "Giải thích ngắn gọn ba câu giúp chiếm trọn lòng tin hội đồng."),
            ],
            [
                ResearchedBeat(
                    image_id="SC04_I1",
                    description="Một tờ giấy A4 trắng tinh đặt ngay ngắn giữa bàn làm việc bên cạnh một cây bút máy đen.",
                    anchor_quote="Trước khi bước lên bục",
                    reason="Cận cảnh quy tắc tờ giấy trắng tinh khôi.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC04_I2",
                    description="Cận cảnh bàn tay cầm bút đỏ gạch xóa thẳng tay những dòng chữ thuật ngữ chuyên ngành dài dòng trên bản nháp nghiên cứu cũ.",
                    anchor_quote="hãy thử ngay quy tắc tờ giấy trắng",
                    reason="Cận cảnh gạch bỏ các thuật ngữ rườm rà trên bản nháp.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC04_I3",
                    description="Bàn tay cầm bút máy đen đặt nét viết lại đúng ba gạch đầu dòng ngắn gọn, súc tích lên một tờ giấy trắng mới tinh khôi.",
                    anchor_quote="Viết lại toàn bộ thông điệp đề tài bằng đúng ba câu ngắn gọn",
                    reason="Cận cảnh viết ba câu cốt lõi súc tích lên tờ giấy trắng mới.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC04_I4",
                    description="Trang giấy trắng hiển thị ba câu văn tiếng Việt đời thường trong sáng không chứa chữ viết tắt hay thuật ngữ ngoại.",
                    anchor_quote="không dùng bất kỳ từ ngữ chuyên môn nào",
                    reason="Minh họa sản phẩm hoàn thành của quy tắc tờ giấy trắng.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="white_card",
                ),
            ],
        ),
        (
            "SC05",
            "Khép vòng lặp làm chủ một trăm hai mươi giây đầu phòng bảo vệ",
            "Khép vòng lặp làm chủ 120 giây đầu phòng bảo vệ bằng sự sáng rõ của tờ giấy trắng",
            "Khi tóm gọn được mọi thứ trên một mặt giấy trắng, bạn sẽ không còn sợ hãi. [pause:500ms] Một trăm hai mươi giây đầu tiên trước hội đồng sẽ hoàn toàn thuộc về bạn.",
            ["R05"],
            ["SRC02"],
            "Người que tự tin làm chủ bục bảo vệ và nhận được cái gật đầu từ hội đồng",
            "Phòng bảo vệ khóa luận sáng sủa với đồng hồ 120 giây",
            "reflective_slow",
            [
                ("Một trăm hai mươi giây đầu tiên trước hội đồng sẽ hoàn toàn thuộc về bạn", "SRC02", "Giải thích ngắn gọn ba câu giúp chiếm trọn lòng tin hội đồng."),
            ],
            [
                ResearchedBeat(
                    image_id="SC05_I1",
                    description="Nhân vật người que đứng trên bục bảo vệ, tay cầm tờ giấy trắng nhỏ mỉm cười tự tin nhìn thẳng vào hội đồng.",
                    anchor_quote="Khi tóm gọn được mọi thứ trên một mặt giấy trắng",
                    reason="Người que làm chủ sân khấu với tờ giấy trắng nhỏ.",
                    character_ids=["CH01"],
                    effect="zoom_in",
                    shot_type="full_scene",
                ),
                ResearchedBeat(
                    image_id="SC05_I2",
                    description="Chiếc đồng hồ điện tử đếm ngược 120 giây đầu tiên hiển thị ánh sáng xanh tích cực.",
                    anchor_quote="bạn sẽ không còn sợ hãi",
                    reason="Cận cảnh 120 giây then chốt tạo ấn tượng đầu tiên.",
                    character_ids=["CH01"],
                    effect="pan_right",
                    shot_type="macro_prop",
                ),
                ResearchedBeat(
                    image_id="SC05_I3",
                    description="Các thành viên hội đồng đồng loạt mỉm cười và gật đầu tán thành trước phần trình bày khúc chiết, sáng rõ.",
                    anchor_quote="Một trăm hai mươi giây đầu tiên",
                    reason="Phản hồi tích cực đồng thuận từ hội đồng.",
                    character_ids=["CH01"],
                    effect="zoom_out",
                    shot_type="variation",
                    based_on="SC05_I1",
                    preserve="Keep room layout, window geometry, furniture, props and figure design. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Show the described full-frame scene.",
                ),
                ResearchedBeat(
                    image_id="SC05_I4",
                    description="Nhân vật người que nở nụ cười rạng rỡ, hoàn toàn làm chủ bục bảo vệ trong sự ngưỡng mộ của cả khán phòng.",
                    anchor_quote="sẽ hoàn toàn thuộc về bạn",
                    reason="Khép lại với chiến thắng ngoạn mục nhờ sự sáng rõ của bản chất.",
                    character_ids=["CH01"],
                    effect="pan_left",
                    shot_type="variation",
                    based_on="SC05_I3",
                    preserve="Keep podium, microphone, presentation stage and audience rows from the base scene. Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift.",
                    change="Focus on the stick figure smiling with glowing triumph at the podium under warm auditorium lights.",
                ),
            ],
        ),
    ]

    scenes_3 = []
    for sc_id, title, purp, narr, req, src, act, sett, tone, clms, beats in scenes_3_defs:
        is_last = (sc_id == "SC05")
        rep = SceneCadenceReport(sc_id, 10.0, narr, is_last=is_last)
        scenes_3.append(
            ResearchedScene(
                scene_id=sc_id,
                title=title,
                purpose=purp,
                duration=rep.estimated_audio_duration,
                narration=narr,
                requirements=req,
                source_ids=src,
                character_ids=["CH01"],
                action=act,
                setting=sett,
                camera="Semantic full-frame sequence",
                tone=tone,
                claim_facts=clms,
                visual_beats=beats,
            )
        )

    topic_3 = ResearchedTopic(
        topic="Chiếc Nạng Ngôn Từ: Bài Test Tờ Giấy Trắng Trước Cửa Phòng Bảo Vệ Khóa Luận",
        audience="Sinh viên, học viên cao học và người bảo vệ luận văn tại Việt Nam",
        goal="Phá vỡ cái bẫy dựa dẫm vào thuật ngữ trừu tượng, áp dụng bài test tờ giấy trắng để làm chủ 120s đầu phòng bảo vệ",
        video_type="science",
        min_duration=45.0,
        max_duration=60.0,
        style="Minh hoạ Editorial Graphic 2D toàn khung, nhân vật người que viền đen dày tương tác trực tiếp với hội đồng và tờ giấy trắng trong cùng bố cục, khung dọc 9:16.",
        aspect_ratio="9:16",
        format_profile="short_9x16",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        packaging=pack_3,
        characters=chars,
        sources=sources_3,
        required_points=reqs_3,
        scenes=scenes_3,
    )

    jobs = [
        ("feynman-jargon-trap-9x16", topic_1),
        ("feynman-jargon-trap-spinoff-02-9x16", topic_2),
        ("feynman-jargon-trap-spinoff-03-9x16", topic_3),
    ]

    for job_name, topic_obj in jobs:
        out_dir = Path("sys/blueprints") / job_name
        res = write_production_package(out_dir, topic_obj, system_root=Path("sys"), brief_revision=1)
        print(f"=== {job_name} ===")
        print(f"  valid_contracts: {res['valid_contracts']}")
        print(f"  contract_errors: {res['contract_errors']}")
        print(f"  cadence status:  {res['cadence_report']['status']}")
        print(f"  total duration:  {res['cadence_report']['total_duration']}")
        print(f"  warnings count:  {res['cadence_report']['warnings_count']}")
        if res["contract_errors"] or res["cadence_report"]["status"] != "PASS":
            raise RuntimeError(f"Job {job_name} failed validation!")


if __name__ == "__main__":
    build_and_validate()
