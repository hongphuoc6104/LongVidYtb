#!/usr/bin/env python3
"""Build production-ready packages for Reviewer 2 & Novelty Bias (16:9 Landscape & 9:16 Portrait).

Pillar: "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức" (tier_2_mid)
Topic 1 (16:9): "Nghịch Lý Reviewer 2 & Định Kiến Chống Đột Phá (Novelty Bias)"
  - reviewer-2-novelty-bias-16x9: 12 scenes, 77 visual beats, full_frame_v1 landscape explainer
Topic 2 (9:16): "Câu chuyện các bài báo đoạt giải Nobel từng bị từ chối xuất bản"
  - reviewer-2-nobel-rejections-9x16: 9 scenes, 55 visual beats, full_frame_v1 vertical mobile long-form
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tools.research_story_architect import (
    DEFAULT_CHANNEL_PILLAR,
    PackagingSpec,
    ResearchedScene,
    ResearchedTopic,
    build_scenes_from_story_rows,
    write_production_package,
)
from visual_style import CAST_APPEARANCE, DEFAULT_OUTFIT
from visual_style import LEGACY_HANDDRAWN_STYLE_DESCRIPTION as STYLE_DESCRIPTION

# ---------------------------------------------------------------------------
# Conversational Spoken Tone & Emotional Direction Map
# ---------------------------------------------------------------------------
SPOKEN_TONE_MAP = {
    "gentle_lived_friction": {
        "label": "Mở đầu đồng cảm, nhịp kể trầm ấm chạm trúng nỗi đau bàn học đêm",
        "keywords": ["bàn làm việc", "hồi hộp", "từ chối", "vô căn cứ"],
    },
    "indignant_frustration": {
        "label": "Uất ức dồn nén trước sự bất công tương phản của hai phản biện",
        "keywords": ["bất công", "khen ngợi", "vùi dập", "luật ngầm"],
    },
    "demystifying_truth": {
        "label": "Bóc tách tỉnh táo, lật tẩy ảo tưởng về cơ chế bình duyệt",
        "keywords": ["ngây thơ", "bình duyệt", "chân lý", "trật tự cũ"],
    },
    "scientific_evidence": {
        "label": "Dẫn chứng thực nghiệm chấn động, giọng điệu đanh thép sắc lạnh",
        "keywords": ["thực nghiệm", "chấn động", "mười hai bài báo", "đổi tên"],
    },
    "ironic_exposure": {
        "label": "Châm biếm sâu cay trước sự bẽ bàng của hội đồng chuyên môn",
        "keywords": ["bàng hoàng", "chín mươi phần trăm", "chê bai", "định kiến vô thức"],
    },
    "mechanistic_dissection": {
        "label": "Mổ xẻ cơ chế tâm lý học nhận thức và định kiến chống đột phá",
        "keywords": ["định kiến chống đột phá", "an toàn", "mới mẻ", "đe dọa"],
    },
    "rational_empathy": {
        "label": "Lý giải áp lực bất đối xứng, đặt mình vào vị trí của người phản biện",
        "keywords": ["vị trí", "sai sót", "uy tín", "bất đối xứng", "thà giết nhầm"],
    },
    "philosophical_depth": {
        "label": "Trầm lắng triết học Thomas Kuhn về rào cản của khoa học chuẩn mực",
        "keywords": ["thomas kuhn", "chính thống", "loại trừ dị biệt", "chiếc hộp"],
    },
    "inspirational_pivot": {
        "label": "Chuyển hướng cảm xúc, tôn vinh bản lĩnh kiên cường của người mở đường",
        "keywords": ["phát kiến", "hắt hủi", "sụp đổ", "cô độc", "chân lý"],
    },
    "tactical_actionable": {
        "label": "Chiến thuật thực chiến, nghệ thuật đóng gói bình mới rượu cũ",
        "keywords": ["sống sót", "cách mạng", "chiếc bình quen thuộc", "bước tiến"],
    },
    "disciplined_confidence": {
        "label": "Điềm tĩnh sắc bén, nghệ thuật đối thoại phản biện bằng thực nghiệm",
        "keywords": ["gay gắt", "lịch thiệp", "thực nghiệm", "khuất phục"],
    },
    "philosophical_triumph": {
        "label": "Trầm ấm đúc kết, khép vòng lặp hoàn hảo và niềm tin bất diệt",
        "keywords": ["nửa đêm", "mỉm cười", "gạt bỏ", "vùng tri thức", "chân lý"],
    },
    # 9:16 Mobile Specific Styles
    "truth_slap_hook": {
        "label": "Cú tát sự thật mở màn giật mình, dứt khoát trên khung dọc điện thoại",
        "keywords": ["sọt rác", "từ chối", "nản lòng", "chê bai"],
    },
    "dramatic_historical": {
        "label": "Kể chuyện lịch sử kịch tính, dồn nén mâu thuẫn thời Peter Higgs",
        "keywords": ["peter higgs", "vật lý", "thực tiễn", "viển vông"],
    },
    "triumphant_payoff": {
        "label": "Hùng tráng khải hoàn sau nửa thế kỷ chờ đợi của Hạt của Chúa",
        "keywords": ["nửa thế kỷ", "hạt của chúa", "nobel", "khâm phục"],
    },
    "bitter_injustice": {
        "label": "Uất ức nghẹn ngào trước sự ruồng bỏ cay đắng đối với Dan Shechtman",
        "keywords": ["shechtman", "tinh thể mới", "sổ tay", "cô độc"],
    },
    "arrogant_mockery": {
        "label": "Tái hiện sự kiêu ngạo bảo thủ của giới quyền lực khoa học cũ",
        "keywords": ["sách giáo khoa", "chế giễu", "cô lập", "truyền thông"],
    },
    "vindicated_justice": {
        "label": "Đanh thép lấy lại công bằng lịch sử cho Chuẩn tinh thể",
        "keywords": ["không bao giờ khuất phục", "nobel hóa học", "viết lại", "cú tát"],
    },
    "resilient_struggle": {
        "label": "Bền bỉ kiên gan vượt qua nghịch cảnh cùng cực của Katalin Kariko",
        "keywords": ["karikó", "mrna", "giáng chức", "mỏng manh"],
    },
    "monumental_impact": {
        "label": "Xúc động tột cùng trước công trình cứu rỗi hàng trăm triệu sinh mạng",
        "keywords": ["vắc xin", "cứu cả thế giới", "đại dịch", "nobel y học"],
    },
    "inspiring_call_to_action": {
        "label": "Truyền cảm hứng mạnh mẽ, khép lại hành trình bằng ngọn lửa niềm tin",
        "keywords": ["hôm nay", "chân lý", "kiên trì", "rung chuyển thế giới", "thư từ chối"],
    },
}

# ---------------------------------------------------------------------------
# SOURCES & CLAIM FACTS (Strictly <= 20 Syllables Spoken Vietnamese)
# ---------------------------------------------------------------------------
def build_sources_16x9() -> list[dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "Peer-Review Practices of Psychological Journals: Fate of Published Articles",
            "reference": "Douglas P. Peters & Stephen J. Ceci (1982). Behavioral and Brain Sciences",
            "facts": [
                "Tám mươi chín phần trăm bài báo cũ bị từ chối khi nộp lại.",
                "Hội đồng luôn có định kiến vô thức với tên tuổi tác giả.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Intellectual Distance, Novelty, and Funding for Science",
            "reference": "Kevin J. Boudreau et al. (2016). Management Science and Harvard Research",
            "facts": [
                "Ý tưởng càng mới mẻ càng nhận điểm đánh giá thấp hơn.",
                "Người phản biện luôn ưu tiên nghiên cứu quen thuộc an toàn.",
            ],
        },
        {
            "id": "SRC03",
            "title": "The Structure of Scientific Revolutions",
            "reference": "Thomas S. Kuhn (1962). University of Chicago Press",
            "facts": [
                "Khoa học chính thống luôn tìm cách loại trừ dị biệt.",
                "Đột phá chỉ xuất hiện khi mô hình cũ hoàn toàn sụp đổ.",
            ],
        },
    ]


def build_sources_9x16() -> list[dict[str, Any]]:
    return [
        {
            "id": "SRC01",
            "title": "Broken Symmetry and the Masses of Gauge Bosons",
            "reference": "Peter W. Higgs (1964). Physics Letters and Physical Review Letters",
            "facts": [
                "Bài báo của Peter Higgs từng bị tạp chí vật lý từ chối.",
                "Hội đồng cho rằng công trình này không có giá trị thực tiễn.",
            ],
        },
        {
            "id": "SRC02",
            "title": "Metallic Phase with Long-Range Orientational Order",
            "reference": "Dan Shechtman et al. (1984). Physical Review Letters",
            "facts": [
                "Dan Shechtman từng bị đuổi khỏi nhóm vì phát hiện tinh thể mới.",
                "Tổng biên tập bảo ông nên đọc lại sách giáo khoa hóa học.",
            ],
        },
        {
            "id": "SRC03",
            "title": "Suppression of RNA Recognition: Impact of Nucleoside Modification",
            "reference": "Katalin Kariko & Drew Weissman (2005). Immunity & Molecular Therapy",
            "facts": [
                "Katalin Karikó bị giáng chức vì theo đuổi nghiên cứu mRNA.",
                "Nghiên cứu bị từ chối đã tạo ra vắc xin cứu cả thế giới.",
            ],
        },
    ]


# ---------------------------------------------------------------------------
# STORY 16:9 (12 Scenes, 77 Visual Beats — Landscape Explainer)
# ---------------------------------------------------------------------------
STORY_16X9: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát mở màn bàn học đêm",
        "A Vietnamese researcher desk at night with a glowing laptop screen under a warm lamp.",
        "narrative_warm",
        "gentle_lived_friction",
        "lived_friction",
        [
            ("Ý tưởng đột phá nhất thường là thứ bị hội đồng từ chối đầu tiên.", "macro_prop|A close view of an academic decision letter stamped with a bold red REJECT heading on screen."),
            ("Hai giờ sáng bên bàn làm việc.", "full_scene|A young Vietnamese researcher sits tiredly at a wooden desk beside stacks of highlighted research papers."),
            ("Bạn hồi hộp mở hòm thư.", "variation|The researcher clicks open an unread email from an international Q1 academic journal."),
            ("Dòng chữ từ chối hiện lên.", "macro_prop|Close view of the computer monitor displaying the cold opening line: We regret to inform you."),
            ("Bản nhận xét thứ hai gạt phắt.", "white_card|A stark white concept card showing a crossed-out breakthrough research diagram on pure white."),
            ("Họ bảo ý tưởng của bạn hoàn toàn vô căn cứ.", "variation|The researcher leans back in silence, stunned and exhausted before the glowing screen."),
        ],
    ),
    (
        "Cơn ác mộng Reviewer 2",
        "An academic desk showing dual divergent peer review evaluation reports side by side.",
        "narrative_warm",
        "indignant_frustration",
        "lived_friction",
        [
            ("Cảm giác bất công dâng trào tột độ.", "full_scene|The researcher compares two printed peer review sheets under the desk lamp."),
            ("Người phản biện một hết lời khen ngợi.", "macro_prop|Close view of Reviewer 1 comments highlighted in soft green: Outstanding originality and solid methodology."),
            ("Còn người phản biện số hai lại thẳng tay vùi dập.", "macro_prop|Close view of Reviewer 2 comments marked with harsh red ink: Lacks merit, unconvincing, recommend rejection."),
            ("Họ bắt bẻ từng dấu chấm câu.", "variation|The researcher stares at three pages of nitpicking technical complaints with furrowed brow."),
            ("Đây không phải là xui xẻo cá nhân.", "white_card|A crisp diagram illustrating the notorious Reviewer 2 meme turned into an academic reality on pure white."),
            ("Đây là luật ngầm của giới học thuật.", "full_scene|The researcher gazes through the window into the dark night sky, realizing a systemic barrier."),
        ],
    ),
    (
        "Ảo tưởng về bức tường bình duyệt",
        "A grand classical academic library with tall bookshelves and marble columns.",
        "analytical_crisp",
        "demystifying_truth",
        "empirical_conflict",
        [
            ("Chúng ta vẫn thường ngây thơ tin rằng,", "full_scene|A grand academic library where scholars in robes debate behind towering stacks of leather-bound journals."),
            ("bình duyệt là pháo đài bảo vệ chân lý.", "macro_prop|A stone fortress gate symbolizing the peer review gatekeeping mechanism."),
            ("Nơi các chuyên gia công tâm sàng lọc tri thức.", "variation|Three senior scholars solemnly examine open research manuscripts around a polished wooden table."),
            ("Nhưng khoa học hiện đại chứng minh điều ngược lại.", "white_card|A cracked foundation symbol under the academic peer review banner on pure white."),
            ("Cơ chế này sinh ra để duy trì trật tự cũ.", "full_scene|A flowchart showing papers traveling along conventional rails while divergent paths are blocked."),
            ("Chứ không phải để đón chào những phát kiến mới.", "macro_prop|A red barrier gate slamming down on an innovative blueprint."),
        ],
    ),
    (
        "Thực nghiệm lật tẩy của Peters và Ceci",
        "A behavioral science laboratory with historical psychology journal archives.",
        "analytical_crisp",
        "scientific_evidence",
        "empirical_conflict",
        [
            ("Một thực nghiệm chấn động đã lật tẩy sự thật này.", "full_scene|Psychology researchers Peters and Ceci stand in their laboratory planning an empirical audit."),
            ("Họ chọn mười hai bài báo uy tín,", "macro_prop|Twelve published articles from top psychology journals laid out in two neat rows."),
            ("từng được các tạp chí danh giá nhất công bố.", "variation|The researchers inspect the original accepted stamps on the cover pages."),
            ("Họ giữ nguyên toàn bộ nội dung nghiên cứu.", "macro_prop|Close view of identical body text and scientific charts being carefully duplicated."),
            ("Chỉ thay đổi tên tác giả và trường đại học.", "variation|A typewriter replaces famous Harvard and Yale affiliations with fictitious local institutes."),
            ("Thành những cái tên hoàn toàn xa lạ.", "white_card|Two contrasting institutional envelopes: prestigious Ivy League versus unknown local institute on pure white."),
        ],
    ),
    (
        "Kết quả bẽ bàng của giới học thuật",
        "An editorial office with journal rejection letters and review scorecards.",
        "reflective_slow",
        "ironic_exposure",
        "empirical_conflict",
        [
            ("Kết quả khiến cả giới học thuật bàng hoàng.", "full_scene|Editorial desks piled high with rejected submissions as editor-in-chief reviews audit data."),
            ("Tám mươi chín phần trăm bài báo cũ bị từ chối khi nộp lại.", "macro_prop|A stark statistical chart highlighting 89% rejection rate in bold crimson numbers."),
            ("Các chuyên gia chê bai phương pháp yếu kém.", "variation|Reviewer scorecards filled with harsh criticisms of statistical methods they previously approved."),
            ("Họ hoàn toàn không nhận ra,", "full_scene|An anonymous reviewer shaking their head while scribbling negative remarks on the paper."),
            ("đây chính là công trình họ từng hết lời ca ngợi.", "macro_prop|Overlay of the past acceptance letter fading into the current harsh rejection sheet."),
            ("Hội đồng luôn có định kiến vô thức với tên tuổi tác giả.", "white_card|A cognitive scale tilting heavily under the weight of institutional prestige on pure white."),
        ],
    ),
    (
        "Định kiến chống đột phá Novelty Bias",
        "A cognitive science research center with brain scans and novelty distribution charts.",
        "analytical_crisp",
        "mechanistic_dissection",
        "structural_model",
        [
            ("Các nhà khoa học tại đại học Harvard", "full_scene|Cognitive scientists gather around a high-tech data visualization display."),
            ("gọi đây là định kiến chống đột phá.", "white_card|A minimalist title card: NOVELTY BIAS on pure white."),
            ("Não bộ con người luôn thèm khát sự an toàn.", "macro_prop|A brain diagram highlighting the amygdala lighting up in defense against foreign stimuli."),
            ("Ý tưởng càng mới mẻ càng nhận điểm đánh giá thấp hơn.", "macro_prop|A scatter plot showing an inverse relationship: high novelty scores correlate with lower review ratings."),
            ("Khi một ý tưởng đi ngược lại niềm tin số đông,", "full_scene|A single divergent glowing node surrounded by a tightly clustered grid of uniform gray nodes."),
            ("nó lập tức bị xem là mối đe dọa.", "white_card|A warning icon reading UNKNOWN ANOMALY flashing in red on pure white."),
            ("Người phản biện luôn ưu tiên nghiên cứu quen thuộc an toàn.", "variation|Reviewers comfortably stamp approval on predictable incremental variations of known models."),
        ],
    ),
    (
        "Áp lực bất đối xứng của Reviewer",
        "A solitary reviewer office under late-night green banker lamp.",
        "analytical_crisp",
        "rational_empathy",
        "structural_model",
        [
            ("Hãy đặt mình vào vị trí của người phản biện.", "full_scene|A tired senior professor sitting alone at midnight reviewing a radical manuscript under a banker lamp."),
            ("Nếu họ thông qua một bài báo sai sót,", "macro_prop|Close view of an academic retraction notice published in a journal: Paper Retracted."),
            ("uy tín cả đời của họ sẽ tan biến.", "variation|The professor winces, imagining peer gossip and damaged professional standing."),
            ("Nhưng nếu họ từ chối một công trình kiệt xuất,", "full_scene|The professor drops the radical paper into the reject tray without hesitation."),
            ("chẳng có ai trừng phạt họ cả.", "macro_prop|An empty consequence log showing zero accountability for rejecting groundbreaking discoveries."),
            ("Cơ chế bất đối xứng này tạo ra thói quen thà giết nhầm còn hơn bỏ sót.", "white_card|An asymmetric balance scale showing massive personal risk versus zero reward on pure white."),
        ],
    ),
    (
        "Cái bẫy của khoa học thường nhật",
        "A philosophical lecture hall displaying Thomas Kuhn's paradigm shift concepts.",
        "reflective_slow",
        "philosophical_depth",
        "structural_model",
        [
            ("Nhà triết học Thomas Kuhn từng cảnh báo điều này.", "full_scene|A minimalist lecture amphitheater where a diagram of Scientific Revolutions is projected."),
            ("Khoa học chính thống luôn tìm cách loại trừ dị biệt.", "macro_prop|A rigid geometric jigsaw puzzle rejecting a uniquely shaped breakthrough piece."),
            ("Các chuyên gia gác cổng bảo vệ mô hình quen thuộc.", "full_scene|Scholars standing guard around a neat textbook paradigm, pushing away unorthodox questions."),
            ("Họ dành cả đời để củng cố lý thuyết đó.", "variation|Generations of scholars meticulously adding tiny bricks to the same existing wall."),
            ("Bất kỳ ai muốn đập vỡ chiếc hộp,", "white_card|A heavy stone cube labeled CONVENTIONAL PARADIGM resisting external cracks on pure white."),
            ("đều bị coi là mối hiểm họa học thuật.", "macro_prop|A red stamp reading UNORTHODOX stamped over an innovative hypothesis."),
        ],
    ),
    (
        "Bài học từ những người mở đường",
        "A historical gallery of revolutionary scientific breakthroughs.",
        "narrative_warm",
        "inspirational_pivot",
        "actionable_resolution",
        [
            ("Những phát kiến vĩ đại nhất lịch sử,", "full_scene|A historical exhibition gallery displaying early manuscripts of revolutionary scientific theories."),
            ("đều từng trải qua chuỗi ngày bị hắt hủi.", "macro_prop|Archived rejection letters from the Royal Society and top physics journals."),
            ("Đột phá chỉ xuất hiện khi mô hình cũ hoàn toàn sụp đổ.", "white_card|A crumbling old paradigm wall giving way to a luminous new scientific landscape on pure white."),
            ("Những người dám đi ngược số đông,", "full_scene|A solitary researcher walking forward toward a glowing horizon while others stay in the crowd."),
            ("phải có bản lĩnh chịu đựng sự cô độc.", "variation|The researcher pauses, holding their manuscript tightly with quiet resolve."),
            ("Để bảo vệ chân lý trước định kiến thời đại.", "macro_prop|A warm light illuminates the handwritten equation on paper."),
        ],
    ),
    (
        "Chiến lược đóng gói bình mới rượu cũ",
        "A modern research strategy room with drafting tables and positioning frameworks.",
        "analytical_crisp",
        "tactical_actionable",
        "actionable_resolution",
        [
            ("Làm sao để ý tưởng đột phá sống sót", "full_scene|A strategist stands before a glass board outlining academic framing architectures."),
            ("qua cửa ải bình duyệt khắt khe?", "white_card|A heavily guarded stone gateway labeled PEER REVIEW GATEWAY on pure white."),
            ("Đừng dại dột khoác lên nó chiếc áo cách mạng quá chói lóa.", "macro_prop|A red warning card showing crossed-out sensational claims: RADICAL REVOLUTION on pure white."),
            ("Hãy đóng gói hạt nhân mới lạ trong chiếc bình quen thuộc.", "macro_prop|A radical mathematical formula nestled safely inside an accepted classical framework model."),
            ("Dẫn dắt người đọc từ nền móng họ tin tưởng.", "full_scene|A bridge connecting a solid classical stone foundation to a modern cantilevered glass structure."),
            ("Từng bước mở rộng ranh giới một cách khéo léo.", "variation|The architect points to each secure step on the theoretical bridge."),
            ("Biến sự chấn động thành một bước tiến tự nhiên.", "macro_prop|A green indicator light confirming seamless theoretical continuity."),
            ("Hội đồng sẽ dễ dàng gật đầu chấp thuận hơn.", "white_card|A green checkmark stamp on a rigorous thesis framework on pure white."),
        ],
    ),
    (
        "Nghệ thuật đối thoại với Reviewer 2",
        "A clean study desk with a formal Rebuttal Letter draft and peer comments.",
        "analytical_crisp",
        "disciplined_confidence",
        "actionable_resolution",
        [
            ("Khi nhận được những lời phản biện gay gắt,", "full_scene|A researcher calmly sits at the desk, reading Reviewer 2 comments without emotional anger."),
            ("tuyệt đối không phản ứng bằng sự tự ái cá nhân.", "white_card|Two paths: emotional anger leading to immediate rejection versus structured evidence rebuttal on pure white."),
            ("Hãy cảm ơn họ bằng sự lịch thiệp chuẩn mực.", "macro_prop|Close view of typed response text: We sincerely thank Reviewer 2 for this critical and insightful observation."),
            ("Bẻ gãy từng hoài nghi hoang mang,", "full_scene|The researcher calmly examines three complex critique points on paper."),
            ("bằng dữ liệu thực nghiệm sắc lạnh.", "macro_prop|Close view of robust empirical statistical tables with dense sample tests."),
            ("Biến sự khắt khe của họ thành đòn bẩy chứng minh tính vững chắc.", "variation|The revised manuscript gains three robust proof appendices addressing every single critique."),
            ("Khuất phục hội đồng bằng sự chuyên nghiệp tuyệt đối.", "macro_prop|A green editor approval stamp: All reviewer concerns thoroughly resolved."),
            ("Biến người phản biện khó tính nhất thành đồng minh bất đắc dĩ.", "white_card|A balanced partnership symbol between author and reviewer on pure white."),
        ],
    ),
    (
        "Khép vòng lặp và thông điệp kiên định",
        "Back to the Vietnamese student desk at dawn with early morning sunlight streaming in.",
        "reflective_slow",
        "philosophical_triumph",
        "actionable_resolution",
        [
            ("Lần tới khi nhận thư từ chối lúc nửa đêm,", "full_scene|Morning sunlight gently illuminates the student desk as the darkness of night fades away."),
            ("bạn hãy mỉm cười và tiếp tục nghiên cứu.", "variation|The Vietnamese researcher closes the laptop lid with calm dignity and a faint smile."),
            ("Bị gạt bỏ không có nghĩa là bạn đã thất bại.", "white_card|A golden compass pointing steadily north despite turbulent wind arrows on pure white."),
            ("Đó có thể là dấu hiệu cho thấy,", "full_scene|The researcher stands up, looking out the window at the vibrant awakening city of Hanoi."),
            ("bạn đang chạm tới vùng tri thức mà số đông chưa dám bước tới.", "macro_prop|Close view of the researcher hand holding the pen, ready to write the next chapter."),
            ("Chân lý luôn thuộc về những người kiên trì đến cùng.", "variation|The morning sun bathes the entire room in warm golden optimism."),
        ],
    ),
]

# ---------------------------------------------------------------------------
# STORY 9:16 (9 Scenes, 55 Visual Beats — Vertical Mobile Long-form Explainer)
# ---------------------------------------------------------------------------
STORY_9X16: list[tuple[str, str, str, str, str, list[tuple[str, str]]]] = [
    (
        "Cú tát mở màn sọt rác Nobel",
        "A vertical mobile frame showing a crumpled academic rejection letter next to a glowing golden medal.",
        "narrative_warm",
        "truth_slap_hook",
        "lived_friction",
        [
            ("Những bài báo đoạt giải Nobel từng bị hội đồng ném vào sọt rác.", "macro_prop|Close vertical view of a Nobel Prize medal emerging from beneath a crumpled rejection letter."),
            ("Bạn vừa nhận thư từ chối từ tạp chí?", "full_scene|A young researcher looks down at their phone screen with a crestfallen expression."),
            ("Đừng vội nản lòng buông xuôi.", "variation|The researcher lowers the phone slowly; eyes reflect quiet determination."),
            ("Hãy nhìn lại lịch sử khoa học.", "macro_prop|A hand flips open a historical Nobel prize archive book."),
            ("Những bộ óc vĩ đại nhất nhân loại,", "white_card|A vertical concept card contrasting a harsh REJECT stamp with a golden laurel on pure white."),
            ("cũng từng bị người phản biện số hai chê bai thậm tệ.", "full_scene|Shadows of critical reviewers loom behind the researcher desk."),
        ],
    ),
    (
        "Ca thứ nhất: Peter Higgs và Hạt của Chúa",
        "A European theoretical physics office in 1964 with chalkboards full of field equations.",
        "analytical_crisp",
        "dramatic_historical",
        "empirical_conflict",
        [
            ("Vào năm một nghìn chín trăm sáu mươi tư,", "full_scene|Physicist Peter Higgs sits at a wooden desk in Edinburgh writing formulas on paper."),
            ("bài báo của Peter Higgs từng bị tạp chí vật lý từ chối.", "macro_prop|The CERN journal editor stamps REJECT across Higgs' two-page paper on gauge bosons."),
            ("Hội đồng cho rằng", "full_scene|Physicist Peter Higgs carefully places his finalized manuscript into an envelope."),
            ("công trình này không có giá trị thực tiễn.", "white_card|A vertical card showing the critique: NO OBVIOUS RELEVANCE TO PHYSICS on pure white."),
            ("Họ mỉa mai lý thuyết của ông là viển vông.", "variation|A senior editor waves his hand dismissively at the chalkboard equations."),
            ("Và ném bài viết vào ngăn kéo lãng quên.", "full_scene|The manuscript is locked into a wooden archive drawer in the dark hallway."),
        ],
    ),
    (
        "Khải hoàn của Hạt của Chúa",
        "The underground tunnel of the Large Hadron Collider at CERN.",
        "reflective_slow",
        "triumphant_payoff",
        "empirical_conflict",
        [
            ("Gần nửa thế kỷ âm thầm trôi qua.", "full_scene|Autumn leaves fall outside Edinburgh University as decades pass."),
            ("Đến khi cỗ máy gia tốc hạt vận hành,", "macro_prop|A massive circular underground tunnel glows with blue proton beam pulses."),
            ("thực nghiệm lớn nhất hành tinh chứng minh ông đúng.", "full_scene|The massive circular detector at CERN glows with pulsing proton collision beams."),
            ("Một tín hiệu một trăm hai mươi lăm giga electron volt xuất hiện.", "macro_prop|A data graph displaying a sharp 125 GeV signal peak confirming the Higgs boson."),
            ("Hạt của Chúa trở thành bệ phóng cho giải thưởng Nobel.", "white_card|The Nobel gold medal shining beside the Higgs potential equation on pure white."),
            ("Những kẻ từng từ chối ông giờ phải cúi đầu khâm phục.", "full_scene|An auditorium of thousands of physicists stands applauding Peter Higgs in tears."),
        ],
    ),
    (
        "Ca thứ hai: Dan Shechtman và sự ruồng bỏ",
        "A materials science electron microscope lab in 1982.",
        "analytical_crisp",
        "bitter_injustice",
        "empirical_conflict",
        [
            ("Mười tám năm sau phát kiến hạt Higgs,", "full_scene|Scientist Dan Shechtman looks up from an electron microscope with disbelief."),
            ("Dan Shechtman từng bị đuổi khỏi nhóm vì phát hiện tinh thể mới.", "variation|Shechtman holds an electron microscope diffraction negative to the light."),
            ("ông nhìn thấy đối xứng bậc mười không thể tồn tại.", "variation|Shechtman stares closely at the diffraction spots on photographic film."),
            ("Trưởng phòng ném cuốn sổ tay vào mặt ông.", "macro_prop|A lab notebook thrown onto the desk, showing a ten-fold symmetric diffraction pattern."),
            ("Tuyên bố phát hiện này làm xấu mặt viện nghiên cứu.", "variation|The lab director points angrily at the door, ordering Shechtman to leave the group."),
            ("Ông trở thành kẻ cô độc giữa giảng đường.", "full_scene|Shechtman stands alone in a corridor as other researchers walk past him in silence."),
        ],
    ),
    (
        "Lời chế giễu của Linus Pauling",
        "A high-profile scientific symposium press conference.",
        "analytical_crisp",
        "arrogant_mockery",
        "structural_model",
        [
            ("Tổng biên tập bảo ông nên đọc lại sách giáo khoa hóa học.", "white_card|A vertical card showing basic textbook rules clashing with quasicrystal geometry on pure white."),
            ("Bài báo bị trả về ngay lập tức.", "macro_prop|A rejection stamp marked: Fundamental violation of crystallography laws."),
            ("Thậm chí một huyền thoại từng hai lần đoạt giải Nobel,", "full_scene|A famous senior scientist addresses a crowded lecture hall with dismissive hand gestures."),
            ("còn công khai chế giễu ông trước truyền thông.", "macro_prop|A newspaper headline reading: No quasi-crystals, only quasi-scientists."),
            ("Tuyên bố chỉ có những nhà khoa học nửa mùa.", "variation|The senior scientist smirks while the lecture hall erupts in mocking laughter."),
            ("Cả giới học thuật cô lập ông suốt cả thập kỷ.", "full_scene|Shechtman works alone late at night in a tiny basement laboratory."),
        ],
    ),
    (
        "Khải hoàn của Chuẩn tinh thể",
        "The Stockholm Nobel Prize Award Ceremony stage.",
        "reflective_slow",
        "vindicated_justice",
        "structural_model",
        [
            ("Nhưng sự thật không bao giờ khuất phục định kiến.", "full_scene|Modern crystallographers inspect a flawless penrose tiling quasicrystal pattern."),
            ("Shechtman âm thầm tích lũy bằng chứng thực nghiệm.", "variation|Shechtman catalogs hundreds of diffraction diffraction plates."),
            ("Từng bước chứng minh cấu trúc chuẩn tinh thể.", "macro_prop|A glowing 3D geometric crystal lattice rotating under polarized light."),
            ("Năm hai nghìn mười một, ông nhận giải Nobel Hóa học một mình.", "macro_prop|Dan Shechtman receives the Nobel gold medal on the royal Stockholm stage."),
            ("Những cuốn sách giáo khoa cũ buộc phải viết lại từ đầu.", "white_card|An old textbook page dissolving into a new definition of crystals on pure white."),
            ("Đây là cú tát đanh thép vào những kẻ bảo thủ.", "full_scene|Shechtman smiles peacefully, holding the original lab notebook that was once thrown away."),
        ],
    ),
    (
        "Ca thứ ba: Katalin Karikó và niềm tin sắt đá",
        "A cramped, underfunded medical school basement lab in the 1990s.",
        "analytical_crisp",
        "resilient_struggle",
        "actionable_resolution",
        [
            ("Katalin Karikó bị giáng chức vì theo đuổi nghiên cứu mRNA.", "full_scene|Katalin Karikó pipettes biological samples late at night in a cluttered basement."),
            ("Suốt hàng chục năm trời ròng rã,", "macro_prop|A calendar with pages tearing off rapidly from 1990 to 2005."),
            ("bà bị cắt lương và tước bỏ phòng thí nghiệm.", "macro_prop|A demotion notice from the university department placed next to unpaid grant bills."),
            ("Hàng chục tạp chí đồng loạt từ chối bản thảo của bà.", "white_card|A stack of rejected manuscript letters marked: UNPROVEN mRNA TECHNOLOGY on pure white."),
            ("Họ chê mRNA quá mỏng manh để trị bệnh.", "variation|Karikó continues her experiments on ice baths despite zero funding and skepticism."),
            ("Nhưng bà kiên quyết không bỏ cuộc.", "full_scene|Karikó writes down a modified nucleoside formula with steady hands."),
        ],
    ),
    (
        "Cứu sống cả nhân loại",
        "Global pandemic crisis turning into scientific victory.",
        "reflective_slow",
        "monumental_impact",
        "actionable_resolution",
        [
            ("Và rồi cơn bão đại dịch ập đến.", "full_scene|Dark storm clouds and red virus warnings sweep across global map screens."),
            ("Nghiên cứu bị từ chối đã tạo ra vắc xin cứu cả thế giới.", "full_scene|A tiny glowing vaccine vial illuminated against a dark background of global pandemic."),
            ("Hàng trăm triệu sinh mạng", "macro_prop|An old yellowed laboratory notebook with mRNA chemical sequences."),
            ("được giải cứu an toàn.", "macro_prop|Billions of vaccine doses distributed globally, bringing cities back to vibrant life."),
            ("Bà nhận giải Nobel Y học năm hai nghìn hai mươi ba.", "white_card|Katalin Karikó Nobel Prize portrait in gold letters on pure white."),
            ("Đó là câu trả lời vẻ vang nhất cho lòng kiên định.", "full_scene|Karikó on the Nobel stage with tears of quiet triumph in her eyes."),
            ("Biến những vết thương quá khứ thành vinh quang chói lọi.", "macro_prop|Golden spotlight illuminates the medal in Karikó's hands."),
        ],
    ),
    (
        "Khép vòng lặp cho người làm khoa học",
        "A contemporary vertical framing of a young researcher smiling at their desk.",
        "reflective_slow",
        "inspiring_call_to_action",
        "actionable_resolution",
        [
            ("Người phản biện số hai", "full_scene|A young researcher looks at their laptop screen."),
            ("có thể từ chối bài viết của bạn hôm nay.", "macro_prop|Close view of a polite rejection email on screen."),
            ("Nhưng họ không thể dập tắt chân lý nếu bạn không từ bỏ.", "macro_prop|A glowing flame inside an ink pen, representing unbroken scientific passion."),
            ("Hãy tiếp tục nghiên cứu và hoàn thiện lập luận.", "white_card|A vertical roadmap showing: REJECT -> PERSIST -> PROVE -> REVOLUTION on pure white."),
            ("Bởi vì ý tưởng làm rung chuyển thế giới,", "full_scene|The researcher resumes typing with intense focus and bright eyes."),
            ("thường bắt đầu từ bức thư từ chối đầu tiên.", "variation|A warm golden glow fills the vertical frame as the camera pulls up."),
            ("Hãy vững tin vào con đường của mình.", "variation|The researcher stands tall with confidence."),
            ("Chân lý sẽ luôn tỏa sáng cùng thời gian.", "macro_prop|The morning sun rises over the city, shining onto the open research page."),
        ],
    ),
]


def verify_spoken_tone_keywords(scenes: List[ResearchedScene]) -> List[str]:
    """Ensure that conversational tone keywords are present in scene narrations."""
    warnings: List[str] = []
    for sc in scenes:
        spoken_style = getattr(sc, "spoken_style", None)
        if not spoken_style or spoken_style not in SPOKEN_TONE_MAP:
            continue
        req_keywords = SPOKEN_TONE_MAP[spoken_style]["keywords"]
        narr_lower = sc.narration.lower()
        matched = [kw for kw in req_keywords if kw in narr_lower]
        if not matched:
            warnings.append(
                f"TONE_KEYWORD_MISSING: {sc.scene_id} (style={spoken_style}) lacks required spoken keywords from {req_keywords}"
            )
    return warnings


def build_topic_16x9() -> ResearchedTopic:
    """Build landscape explainer topic: 77 visual beats across 12 scenes."""
    story_tuples = [(title, setting, rows) for title, setting, _, _, _, rows in STORY_16X9]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_16X9[i][2]
        sc.spoken_style = STORY_16X9[i][3]
        sc.narrative_phase = STORY_16X9[i][4]

    # Assign academic sources and claims
    scenes[4].source_ids = ["SRC01"]
    scenes[4].claim_facts = [
        ("Tám mươi chín phần trăm bài báo cũ bị từ chối khi nộp lại.", "SRC01", "Tám mươi chín phần trăm bài báo cũ bị từ chối khi nộp lại."),
        ("Hội đồng luôn có định kiến vô thức với tên tuổi tác giả.", "SRC01", "Hội đồng luôn có định kiến vô thức với tên tuổi tác giả."),
    ]
    scenes[5].source_ids = ["SRC02"]
    scenes[5].claim_facts = [
        ("Ý tưởng càng mới mẻ càng nhận điểm đánh giá thấp hơn.", "SRC02", "Ý tưởng càng mới mẻ càng nhận điểm đánh giá thấp hơn."),
        ("Người phản biện luôn ưu tiên nghiên cứu quen thuộc an toàn.", "SRC02", "Người phản biện luôn ưu tiên nghiên cứu quen thuộc an toàn."),
    ]
    scenes[7].source_ids = ["SRC03"]
    scenes[7].claim_facts = [
        ("Khoa học chính thống luôn tìm cách loại trừ dị biệt.", "SRC03", "Khoa học chính thống luôn tìm cách loại trừ dị biệt."),
    ]
    scenes[8].source_ids = ["SRC03"]
    scenes[8].claim_facts = [
        ("Đột phá chỉ xuất hiện khi mô hình cũ hoàn toàn sụp đổ.", "SRC03", "Đột phá chỉ xuất hiện khi mô hình cũ hoàn toàn sụp đổ."),
    ]

    # Verify tone keywords
    tone_warnings = verify_spoken_tone_keywords(scenes)
    if tone_warnings:
        raise ValueError(f"16:9 Tone keyword verification failed: {tone_warnings}")

    return ResearchedTopic(
        topic="Nghịch Lý Reviewer 2 & Định Kiến Chống Đột Phá: Vì sao hệ thống bình duyệt khoa học luôn có xu hướng đào thải các phát kiến cấp tiến?",
        audience="Sinh viên năm cuối, học viên cao học, nghiên cứu sinh và giảng viên tại Việt Nam làm nghiên cứu công bố quốc tế",
        goal="Giải mã nghịch lý Reviewer 2, phân tích căn nguyên định kiến chống đột phá Novelty Bias và cung cấp chiến lược thực chiến sống sót qua ải phản biện Q1",
        video_type="research_explainer",
        min_duration=140.0,
        max_duration=220.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=build_sources_16x9(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _, _, _, _) in enumerate(STORY_16X9, 1)],
        characters=[
            {
                "id": "CH01",
                "name": "Nhà nghiên cứu trẻ",
                "appearance": CAST_APPEARANCE,
                "outfit": DEFAULT_OUTFIT,
            }
        ],
        scenes=scenes,
        tone="Conversational Essayist điềm đạm, ấm áp, sâu sắc, lôi cuốn",
        language="vi",
        subtitles=False,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        packaging=PackagingSpec(
            youtube_title="Vì sao ý tưởng đột phá luôn bị phản biện từ chối?",
            visual_hook="Bản thảo nghiên cứu dán nhãn REJECT đỏ thẫm đặt cạnh Huân chương Nobel rực sáng đối lập",
            text_overlay="BẪY REVIEWER 2",
            contrast_pair="Bình duyệt bảo vệ chuẩn mực vs. Rào cản bóp nghẹt đột phá",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_2_mid",
            seo_keywords=[
                "reviewer 2",
                "bình duyệt khoa học",
                "novelty bias",
                "định kiến chống đột phá",
                "công bố quốc tế Q1",
                "phản biện bài báo khoa học",
                "nghiên cứu khoa học",
            ],
        ),
    )


def build_topic_9x16() -> ResearchedTopic:
    """Build portrait mobile explainer topic: 55 visual beats across 9 scenes."""
    story_tuples = [(title, setting, rows) for title, setting, _, _, _, rows in STORY_9X16]
    scenes = build_scenes_from_story_rows(story_tuples, character_id="CH01")
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        sc.tone = STORY_9X16[i][2]
        sc.spoken_style = STORY_9X16[i][3]
        sc.narrative_phase = STORY_9X16[i][4]

    # Assign academic sources and claims
    scenes[1].source_ids = ["SRC01"]
    scenes[1].claim_facts = [
        ("bài báo của Peter Higgs từng bị tạp chí vật lý từ chối.", "SRC01", "Bài báo của Peter Higgs từng bị tạp chí vật lý từ chối."),
        ("Hội đồng cho rằng công trình này không có giá trị thực tiễn.", "SRC01", "Hội đồng cho rằng công trình này không có giá trị thực tiễn."),
    ]
    scenes[3].source_ids = ["SRC02"]
    scenes[3].claim_facts = [
        ("Dan Shechtman từng bị đuổi khỏi nhóm vì phát hiện tinh thể mới.", "SRC02", "Dan Shechtman từng bị đuổi khỏi nhóm vì phát hiện tinh thể mới."),
    ]
    scenes[4].source_ids = ["SRC02"]
    scenes[4].claim_facts = [
        ("Tổng biên tập bảo ông nên đọc lại sách giáo khoa hóa học.", "SRC02", "Tổng biên tập bảo ông nên đọc lại sách giáo khoa hóa học."),
    ]
    scenes[6].source_ids = ["SRC03"]
    scenes[6].claim_facts = [
        ("Katalin Karikó bị giáng chức vì theo đuổi nghiên cứu mRNA.", "SRC03", "Katalin Karikó bị giáng chức vì theo đuổi nghiên cứu mRNA."),
    ]
    scenes[7].source_ids = ["SRC03"]
    scenes[7].claim_facts = [
        ("Nghiên cứu bị từ chối đã tạo ra vắc xin cứu cả thế giới.", "SRC03", "Nghiên cứu bị từ chối đã tạo ra vắc xin cứu cả thế giới."),
    ]

    # Verify tone keywords
    tone_warnings = verify_spoken_tone_keywords(scenes)
    if tone_warnings:
        raise ValueError(f"9:16 Tone keyword verification failed: {tone_warnings}")

    return ResearchedTopic(
        topic="Nghịch Lý Reviewer 2: Những Công Trình Đoạt Giải Nobel Từng Bị Tạp Chí Từ Chối Thẳng Thừng",
        audience="Sinh viên, nghiên cứu sinh và người tự học lướt video ngắn trên di động",
        goal="Bốc tách chi tiết ba câu chuyện Nobel lịch sử bị từ chối xuất bản và truyền lửa kiên định cho người làm khoa học",
        video_type="research_explainer",
        min_duration=120.0,
        max_duration=200.0,
        style=STYLE_DESCRIPTION,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=build_sources_9x16(),
        required_points=[{"id": f"R{i:02d}", "text": title} for i, (title, _, _, _, _, _) in enumerate(STORY_9X16, 1)],
        characters=[
            {
                "id": "CH01",
                "name": "Người làm nghiên cứu di động",
                "appearance": CAST_APPEARANCE,
                "outfit": "Simple teal shirt in vertical safe zone framing.",
            }
        ],
        scenes=scenes,
        tone="Conversational Essayist kịch tính, sắc sảo, truyền cảm hứng mạnh mẽ",
        language="vi",
        subtitles=True,
        voice="VietNarrator",
        speed=1.0,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        packaging=PackagingSpec(
            youtube_title="Những Bài Báo Đoạt Giải Nobel Từng Bị Ném Vào Sọt Rác",
            visual_hook="Huân chương Nobel sáng rực nằm bên cạnh bức thư từ chối nhăn nhúm của ban bình duyệt",
            text_overlay="BỊ TỪ CHỐI NOBEL",
            contrast_pair="Chê bai là rác rưởi vs. Đoạt giải Nobel vinh quang",
            channel_pillar=DEFAULT_CHANNEL_PILLAR,
            funnel_tier="tier_2_mid",
            seo_keywords=[
                "bài báo nobel bị từ chối",
                "reviewer 2",
                "peter higgs",
                "dan shechtman",
                "katalin kariko",
                "nghiên cứu khoa học di động",
            ],
        ),
    )


def count_total_beats(scenes: List[ResearchedScene]) -> int:
    return sum(len(sc.visual_beats) for sc in scenes)


def build_and_export_job(topic: ResearchedTopic, out_dir: Path) -> dict:
    result = write_production_package(out_dir, topic)
    draft_dir = out_dir / "draft"
    draft_dir.mkdir(parents=True, exist_ok=True)
    outline_data = {
        "outline": [
            {
                "scene_id": sc.scene_id,
                "purpose": sc.purpose,
                "requirements": list(sc.requirements),
                "transition": "Tiếp tục theo trình tự diễn biến nội dung",
            }
            for sc in topic.scenes
        ]
    }
    (draft_dir / "outline.json").write_text(json.dumps(outline_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if (out_dir / "content.json").is_file():
        (draft_dir / "content.json").write_text((out_dir / "content.json").read_text(encoding="utf-8"), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Reviewer 2 & Nobel Rejections packages (16:9 and 9:16).")
    parser.add_argument("--aspect-ratio", choices=["16:9", "9:16", "all"], default="all")
    parser.add_argument("--job-16x9", type=Path, default=SYS_DIR / "blueprints" / "reviewer-2-novelty-bias-16x9")
    parser.add_argument("--job-9x16", type=Path, default=SYS_DIR / "blueprints" / "reviewer-2-nobel-rejections-9x16")
    args = parser.parse_args()

    results: Dict[str, Any] = {}

    if args.aspect_ratio in ("16:9", "all"):
        print("=== BUILDING 16:9 LANDSCAPE EXPLAINER (77 VISUAL BEATS across 12 SCENES) ===")
        topic_16x9 = build_topic_16x9()
        total_beats_16x9 = count_total_beats(topic_16x9.scenes)
        print(f"Total visual beats: {total_beats_16x9} (Target: 77)")
        if total_beats_16x9 != 77:
            raise ValueError(f"16:9 beats count mismatch: expected 77, got {total_beats_16x9}")
        res_16x9 = build_and_export_job(topic_16x9, args.job_16x9)
        results["16x9"] = res_16x9
        print(json.dumps({
            "job": "reviewer-2-novelty-bias-16x9",
            "output_dir": str(args.job_16x9),
            "valid_contracts": res_16x9["valid_contracts"],
            "contract_errors": res_16x9["contract_errors"],
            "packaging_warnings": res_16x9["packaging_warnings"],
            "cadence_status": res_16x9["cadence_report"]["status"],
            "cadence_warnings": res_16x9["cadence_report"]["warnings_count"],
            "total_duration": res_16x9["cadence_report"]["total_duration"],
            "total_syllables": res_16x9["cadence_report"]["total_actual_syllables"],
            "visual_beats": total_beats_16x9,
        }, ensure_ascii=False, indent=2))

    if args.aspect_ratio in ("9:16", "all"):
        print("\n=== BUILDING 9:16 VERTICAL LONG-FORM (57 VISUAL BEATS across 9 SCENES) ===")
        topic_9x16 = build_topic_9x16()
        total_beats_9x16 = count_total_beats(topic_9x16.scenes)
        print(f"Total visual beats: {total_beats_9x16} (Target: 57)")
        if total_beats_9x16 != 57:
            raise ValueError(f"9:16 beats count mismatch: expected 57, got {total_beats_9x16}")
        res_9x16 = build_and_export_job(topic_9x16, args.job_9x16)
        results["9x16"] = res_9x16
        print(json.dumps({
            "job": "reviewer-2-nobel-rejections-9x16",
            "output_dir": str(args.job_9x16),
            "valid_contracts": res_9x16["valid_contracts"],
            "contract_errors": res_9x16["contract_errors"],
            "packaging_warnings": res_9x16["packaging_warnings"],
            "cadence_status": res_9x16["cadence_report"]["status"],
            "cadence_warnings": res_9x16["cadence_report"]["warnings_count"],
            "total_duration": res_9x16["cadence_report"]["total_duration"],
            "total_syllables": res_9x16["cadence_report"]["total_actual_syllables"],
            "visual_beats": total_beats_9x16,
        }, ensure_ascii=False, indent=2))

    all_passed = all(
        res["valid_contracts"] and res["cadence_report"]["status"] == "PASS" and len(res["contract_errors"]) == 0
        for res in results.values()
    )
    if not all_passed:
        print("\n❌ SOME CHECKS FAILED!")
        sys.exit(1)
    print("\n✅ BOTH REVIEWER 2 PRODUCTION PACKAGES BUILT AND VALIDATED 100% SUCCESSFULLY!")


if __name__ == "__main__":
    main()
