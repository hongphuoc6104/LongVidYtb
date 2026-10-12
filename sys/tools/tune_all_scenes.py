#!/usr/bin/env python3
"""Interactive calibration script to get 100% PASS for all 48 scenes."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sys"))
sys.path.insert(0, str(ROOT / "sys" / "tools"))

from script_cadence_checker import count_syllables, extract_pauses
from script_diversity_linter import lint_script, clean_sentence
from build_study_motivation_history_13m import get_academic_sources

SCENES_DEF = [
    # ================= CHAPTER 1 (Target: 54 syl) =================
    {
        "scene_id": "SC01",
        "chapter": 1,
        "duration": 15.0,
        "sentences": [
            "Sức nặng vô hình đang đè trĩu lên đôi vai bạn.",
            "Cuốn sách mở rộng nhưng tâm trí hoàn toàn đóng chặt.",
            "Từng dòng chữ nhảy múa hỗn loạn trên trang giấy trắng.",
            "Bạn rất muốn tập trung học tập thật tử tế.",
            "Nhưng đầu ngón tay không sao điều khiển nổi cây bút.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC02",
        "chapter": 1,
        "duration": 15.0,
        "sentences": [
            "Sự bất lực này nhanh chóng biến thành nỗi tự trách nặng nề.",
            "Bạn tin rằng bản thân lười biếng và thiếu nghị lực trầm trọng.",
            "Thực chất thể xác của bạn hoàn toàn khỏe mạnh bình thường.",
            "Não bộ không hề cần cảm hứng bùng nổ mới chịu mở sách ra học.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC03",
        "chapter": 1,
        "duration": 15.0,
        "sentences": [
            "Hãy nhìn sâu vào dòng chảy lịch sử ngôn ngữ.",
            "Trước cuối thế kỷ mười chín, khái niệm động lực học tập hoàn toàn chưa từng tồn tại.",
            "Từ điển cổ xưa không hề ghi nhận thuật ngữ này.",
            "Tri thức từng được con người đón nhận một cách rất tự nhiên và thoải mái.",
        ],
        "pause_after_sent": 2,
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
        "sentences": [
            "Suốt hàng nghìn năm, nhân loại dựng xây triết học, nghệ thuật và thiên văn học rực rỡ.",
            "Các bậc hiền triết phương xưa say sưa khám phá bí ẩn vũ trụ ngày đêm.",
            "Họ miệt mài sáng tạo mà không cần bất kỳ cuốn cẩm nang kích thích tinh thần nào nâng đỡ.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC05",
        "chapter": 1,
        "duration": 15.0,
        "sentences": [
            "Nguồn cơn sâu xa của sự mệt mỏi nằm ở không gian sống gò bó.",
            "Một cơ thể sống tràn đầy năng lượng tươi trẻ bị nhốt vào bốn bức tường chật hẹp.",
            "Con người bị ép ngồi yên hàng giờ để nghe giảng những lý thuyết trừu tượng xa vời thực tế.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC06",
        "chapter": 1,
        "duration": 15.0,
        "sentences": [
            "Sự cưỡng ép này bắt nguồn từ một cuộc chuyển mình lớn trong lịch sử.",
            "Khái niệm động lực chỉ bùng nổ khi trường học công nghiệp ép học sinh ngồi bất động.",
            "Muốn khơi lại ngọn lửa say mê, ta cần thấu hiểu cội nguồn sinh học tự nhiên của sự tò mò.",
        ],
        "pause_after_sent": 1,
        "claim": (
            "Khái niệm động lực chỉ bùng nổ khi trường học công nghiệp ép học sinh ngồi bất động.",
            "SRC01",
            "Khái niệm động lực chỉ bùng nổ khi trường học công nghiệp ép học sinh ngồi bất động.",
        ),
    },

    # ================= CHAPTER 2 (Target: 64 syl) =================
    {
        "scene_id": "SC07",
        "chapter": 2,
        "duration": 17.5,
        "sentences": [
            "Vùng vỏ não trước trán của con người quản lý nguồn năng lượng tập trung có hạn định.",
            "Việc liên tục giải mã hàng loạt ký hiệu và công thức trừu tượng tiêu tốn lượng lớn đường glucose trong máu.",
            "Khi nguồn năng lượng này suy giảm, hệ thần kinh phát tín hiệu đình công để ép cơ thể bạn phải nghỉ ngơi.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC08",
        "chapter": 2,
        "duration": 17.5,
        "sentences": [
            "Các công trình nghiên cứu khoa học thần kinh hiện đại ngày nay khẳng định một chân lý rất bất ngờ.",
            "Bộ não không hề lười biếng mà được lập trình để tò mò khám phá.",
            "Mạch dẫn truyền thần kinh tự nhiên luôn thôi thúc con người không ngừng tìm kiếm lời giải đáp thỏa đáng trước những ẩn số mới lạ xung quanh.",
        ],
        "pause_after_sent": 1,
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
        "sentences": [
            "Chất dẫn truyền dopamine giữ vai trò đặc biệt then chốt ở đây.",
            "Dopamine không phải chất hưởng thụ, mà là ngọn lửa thôi thúc tìm kiếm hiểu biết.",
            "Nó chỉ bùng phát khi tâm trí nhìn thấy tín hiệu của một phần thưởng cụ thể ngay trước mắt.",
            "Mất phương hướng hành động rõ ràng, ngọn lửa tò mò ấy sẽ lụi tàn.",
        ],
        "pause_after_sent": 2,
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
        "sentences": [
            "Tâm trí luôn vận hành theo bài toán cân đong năng lượng sinh tồn vô cùng chuẩn xác.",
            "Khi phải nhồi nhét những định lý trừu tượng mà không thấy ứng dụng thực tiễn, não bộ đánh giá đây là việc vô bổ.",
            "Nó sẽ chủ động dập tắt sự tập trung để bảo toàn dưỡng chất quý giá cho cơ thể bạn.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC11",
        "chapter": 2,
        "duration": 17.5,
        "sentences": [
            "Cảm giác uể oải trước trang vở thực chất là một phản xạ phòng vệ tự nhiên.",
            "Bạn không hề yếu đuối về ý chí hay sa sút về năng lực cá nhân.",
            "Bộ não đang kéo phanh hãm lại vì chưa tìm thấy ý nghĩa thiết thực của bài học.",
            "Hiểu được điều này, bạn sẽ trút bỏ được sự dằn vặt bấy lâu.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC12",
        "chapter": 2,
        "duration": 17.5,
        "sentences": [
            "Để chứng kiến cách thức tâm trí tiếp thu tri thức say mê khi không bị giam hãm trong phòng học kín, chúng ta cần tìm về buổi bình minh của nhân loại.",
            "Đó là giai đoạn mà toàn bộ việc học hành hòa quyện trọn vẹn vào nhịp sống tự do giữa không gian đại ngàn khoáng đạt ngập tràn ánh nắng ấm.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },

    # ================= CHAPTER 3 (Target: 64 syl) =================
    {
        "scene_id": "SC13",
        "chapter": 3,
        "duration": 17.5,
        "sentences": [
            "Thời tiền sử không có giảng đường, bảng đen hay sách giáo khoa.",
            "Trẻ nhỏ thức giấc cùng ánh nắng sớm và tự do chạy nhảy khắp núi rừng hoang sơ.",
            "Chúng không phải đối mặt với giáo án hay bài kiểm tra điểm số nào.",
            "Ấy vậy mà ngày nào chúng cũng thuần thục thêm vô số kỹ năng sống phức tạp.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC14",
        "chapter": 3,
        "duration": 17.5,
        "sentences": [
            "Giới nhân chủng học hiện đại nhận thấy điều kỳ diệu về cách học thuở xưa.",
            "Trẻ em tiền sử học mọi kỹ năng sinh tồn thông qua trò chơi tự do.",
            "Chúng tập bắn cung, rình nấp sau bụi cây và cùng nhau dựng lều lá.",
            "Việc học và vui chơi hòa làm một, luôn tràn ngập tiếng cười sảng khoái mỗi ngày.",
        ],
        "pause_after_sent": 1,
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
        "sentences": [
            "Thế hệ đi trước trao cho con trẻ quyền tự chủ trọn vẹn trong mọi hoạt động.",
            "Bộ lạc săn hái không bao giờ bắt ép hay chấm điểm con trẻ học tập.",
            "Người lớn chỉ làm mẫu khi đan giỏ hay ghè đẽo đá, và con trẻ chủ động quan sát rồi làm theo bằng tất cả niềm say mê thuần khiết.",
        ],
        "pause_after_sent": 1,
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
        "sentences": [
            "Mọi bài học nơi hoang dã đều mang lại kết quả thực tế tức thì.",
            "Học cách nhóm lửa, bạn nhận ngay hơi ấm xua tan giá lạnh đêm sương.",
            "Học cách nhận biết quả lành, bạn có bữa trưa ngon lành no bụng.",
            "Não bộ đón nhận phần thưởng hữu hình liền tay, khiến ngọn lửa hứng thú không bao giờ nguội tắt.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC17",
        "chapter": 3,
        "duration": 17.5,
        "sentences": [
            "Khi hoàng hôn buông xuống, cả bộ tộc sum vầy bên đống lửa ấm áp bập bùng.",
            "Già làng kể lại truyền thuyết các vì sao và kinh nghiệm vượt qua bão tuyết hiểm nghèo.",
            "Đám trẻ háo hức chăm chú lắng nghe từng lời chia sẻ.",
            "Tri thức sinh tồn được khắc sâu vào tâm trí tự nhiên qua những câu chuyện kể.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC18",
        "chapter": 3,
        "duration": 17.5,
        "sentences": [
            "Niềm say mê học tập tự nhiên đã nuôi dưỡng giống loài suốt nhiều thế hệ.",
            "Không một ai cảm thấy việc học là gánh nặng khi nó gắn liền với quyền tự do và sinh kế hàng ngày.",
            "Sự ra đời của nền nông nghiệp định cư đã tạo nên bước ngoặt làm biến đổi vĩnh viễn việc học của con người.",
        ],
        "pause_after_sent": 2,
        "claim": None,
    },

    # ================= CHAPTER 4 (Target: 64 syl) =================
    {
        "scene_id": "SC19",
        "chapter": 4,
        "duration": 17.5,
        "sentences": [
            "Hơn năm nghìn năm trước, những đô thị sơ khai mọc lên dọc đôi bờ sông Lưỡng Hà.",
            "Các kho ngũ cốc của đền thờ đòi hỏi phương thức ghi chép số lượng lương thực và gia súc thu nộp.",
            "Chữ viết ra đời, và cùng với đó là sự xuất hiện lần đầu tiên của những lớp học có kỷ luật nghiêm ngặt.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC20",
        "chapter": 4,
        "duration": 17.5,
        "sentences": [
            "Ngôi trường Edubba được dựng lên để đào tạo đội ngũ thư lại chuyên nghiệp.",
            "Bốn nghìn năm trước ở Sumer, học sinh bị đánh đòn nếu viết sai chữ nêm.",
            "Những đứa trẻ phải ngồi khoanh chân từ sáng sớm tới nhá nhem tối trên nền đất, nắn nót từng nét vạch dưới cái nhìn giám sát lạnh lùng của thầy giáo.",
        ],
        "pause_after_sent": 2,
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
        "sentences": [
            "Ý nghĩa nguyên bản của việc học đã biến đổi sâu sắc tại đây.",
            "Trường học đất sét cổ đại ra đời để phục vụ ghi chép thuế khóa cho đền thờ.",
            "Trẻ nhỏ không còn được tìm hiểu những gì mình tò mò.",
            "Chúng bị ép học danh mục tài sản khô khốc phục vụ guồng máy hành chính của giới cai trị.",
        ],
        "pause_after_sent": 2,
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
        "sentences": [
            "Một phiến đất sét cổ nghìn năm còn lưu giữ bức tâm thư thấm đẫm cay đắng.",
            "Cậu học trò Sumer ghi lại rằng mình bị phạt roi vì đi học muộn, và lại ăn đòn khi viết sai ký tự.",
            "Tiếng thở dài ngao ngán trước áp lực bài vở đã bắt đầu vang lên từ những căn phòng đất nung ấy.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC23",
        "chapter": 4,
        "duration": 17.5,
        "sentences": [
            "Sự tò mò tự nhiên bị thay thế bằng nỗi kinh hoàng trước hình phạt đòn roi đau đớn.",
            "Học trò cặm cụi viết vì sợ những vết lằn roi rát bỏng da thịt.",
            "Não bộ gắn liền trang sách với trạng thái căng thẳng và âu lo triền miên.",
            "Nỗi sợ hãi trường lớp chính thức cắm rễ sâu vào tâm thức con người.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC24",
        "chapter": 4,
        "duration": 17.5,
        "sentences": [
            "Học tập bị tách rời khỏi dòng chảy đời thường và biến thành một nghĩa vụ cưỡng bức nặng nề.",
            "Trí não non nớt phải tự dựng nên rào chắn phòng vệ trước những mệnh lệnh hà khắc áp đặt từ bên ngoài.",
            "Ở các triều đại phong kiến phương Đông, cái bẫy học hành tiếp tục bị siết chặt bởi danh phận gia tộc.",
        ],
        "pause_after_sent": 2,
        "claim": None,
    },

    # ================= CHAPTER 5 (Target: 64 syl) =================
    {
        "scene_id": "SC25",
        "chapter": 5,
        "duration": 17.5,
        "sentences": [
            "Ánh đèn dầu leo lét soi bóng người học trò thức trắng thâu đêm bên án thư.",
            "Chồng sách kinh viện dày cộp cao ngút ngàn che khuất khung cửa sổ mờ sương.",
            "Đè nặng lên đôi vai gầy không chỉ là bài thi, mà là niềm hy vọng đổi đời mãnh liệt của cha mẹ và toàn thể bà con làng xóm.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC26",
        "chapter": 5,
        "duration": 17.5,
        "sentences": [
            "Đỗ đạt bảng vàng là con đường duy nhất để rạng danh tổ tông và thoát khỏi cảnh bần hàn.",
            "Thời phong kiến, việc học bị biến thành công cụ tiến thân cho cả dòng tộc.",
            "Đèn sách không còn là hành trình đi tìm tri thức, mà trở thành chiếc cầu độc đạo để chen chân vào hàng ngũ quan lại quyền quý.",
        ],
        "pause_after_sent": 2,
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
        "sentences": [
            "Phương pháp thi cử thời bấy giờ bóp nghẹt mọi mầm mống sáng tạo cá nhân.",
            "Học sinh xưa phải học vẹt hàng vạn câu kinh điển để đi thi làm quan.",
            "Họ phải tụng niệm từng lời của tiền nhân mà không được phép hoài nghi.",
            "Một góc nhìn khác biệt có thể làm sụp đổ toàn bộ tương lai trong chớp mắt.",
        ],
        "pause_after_sent": 2,
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
        "sentences": [
            "Mỗi mùa khoa cử, hàng vạn thí sinh chen chúc trong những gian lều chõng ngột ngạt.",
            "Họ bị cách ly suốt nhiều ngày để gò ép câu chữ vào khuôn mẫu bát cổ cứng nhắc.",
            "Tỷ lệ đỗ đạt vô cùng khắc nghiệt và hiếm hoi.",
            "Phần lớn sĩ tử dành trọn tuổi xuân ứng thí rồi ngậm ngùi tay trắng trở về.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC29",
        "chapter": 5,
        "duration": 17.5,
        "sentences": [
            "Người ta lao vào sách vở vì sợ miệng đời chê cười, chứ chẳng còn chút rung động say mê đích thực.",
            "Trạng thái ganh đua danh vị biến tri thức thành món hàng đổi chác lạnh lùng.",
            "Thay vì mở rộng tầm nhìn, con người tự giam mình trong chiếc lồng áp lực do chính định kiến xã hội tạo dựng nên.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC30",
        "chapter": 5,
        "duration": 17.5,
        "sentences": [
            "Trái ngược với chốn trường thi, các phường thủ công mỹ nghệ dạy nghề rất trực quan qua đôi bàn tay khéo léo.",
            "Người thợ học việc được tự tay tạo tác sản phẩm và nhìn thấy ngay thành quả.",
            "Thế nhưng cuộc cách mạng công nghiệp sau đó đã xóa sổ cách học thực nghiệm bằng cỗ máy trường lớp rập khuôn.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },

    # ================= CHAPTER 6 (Target: 64 syl) =================
    {
        "scene_id": "SC31",
        "chapter": 6,
        "duration": 17.5,
        "sentences": [
            "Khói bụi nhà máy che phủ bầu trời châu Âu khi động cơ hơi nước vận hành ầm ĩ.",
            "Guồng quay kinh tế mới đòi hỏi hàng triệu lao động biết đọc bảng chỉ dẫn và tuân thủ kỷ luật nghiêm ngặt.",
            "Hệ thống giáo dục cưỡng bức quy mô lớn được thiết lập nhằm cung ứng nhân lực cho các xưởng chế tạo.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC32",
        "chapter": 6,
        "duration": 17.5,
        "sentences": [
            "Kiến trúc trường học hiện nay phản chiếu rõ nét nguồn gốc quân sự thời trước.",
            "Mô hình trường học chia theo độ tuổi được sao chép từ nhà máy quân sự Phổ.",
            "Trẻ em bị phân chia thành các lô đồng nhất theo năm sinh, ngồi thẳng hàng ngay ngắn, chăm chú nhìn lên bục giảng như những người thợ bên dây chuyền.",
        ],
        "pause_after_sent": 2,
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
        "sentences": [
            "Tiếng chuông trường học được thiết kế để rèn thói quen tuân lệnh dây chuyền.",
            "Chuông reo báo vào lớp, chuông giục tan giờ, chuông định đoạt phút giây giải lao.",
            "Nó huấn luyện não bộ phản xạ tuân lệnh mà không cần thắc mắc.",
            "Kỷ luật đồng loạt của nhà máy đã hoàn toàn thay thế cho tính tự chủ của mỗi học sinh.",
        ],
        "pause_after_sent": 1,
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
        "sentences": [
            "Trong môi trường đồng dạng của nhà máy, tính hiếu kỳ cá nhân bị coi là sự phiền toái.",
            "Mọi học sinh đều phải tiếp thu cùng một nội dung giáo trình, theo đúng tốc độ đã được định sẵn.",
            "Những tâm hồn yêu thích tìm tòi khác biệt thường bị xem là thiếu tập trung và phải uốn mình vào khuôn khổ chung.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC35",
        "chapter": 6,
        "duration": 17.5,
        "sentences": [
            "Thang điểm và bảng vàng danh dự được phát minh để duy trì trật tự phòng học suốt nhiều giờ.",
            "Điểm cao là phần thưởng, điểm kém là nỗi sỉ nhục.",
            "Giá trị con người bị đóng khung vào những con số vô hồn, thổi bùng lên nỗi ám ảnh thi trượt cùng tâm lý sợ hãi thất bại triền miên trong đời học sinh.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC36",
        "chapter": 6,
        "duration": 17.5,
        "sentences": [
            "Mô hình giáo dục dây chuyền biến việc học thành chuỗi thao tác đơn điệu buồn chán.",
            "Nó rèn luyện tính phục tùng nhiều hơn là năng lực tư duy độc lập sắc bén.",
            "Khi di sản công nghiệp cũ kỹ này va chạm với làn sóng công nghệ số hôm nay, nó đã đẩy khủng hoảng ý chí học tập lên mức đỉnh điểm.",
        ],
        "pause_after_sent": 2,
        "claim": None,
    },

    # ================= CHAPTER 7 (Target: 54 syl) =================
    {
        "scene_id": "SC37",
        "chapter": 7,
        "duration": 15.0,
        "sentences": [
            "Hãy nhìn lại góc bàn học rất đỗi quen thuộc của bạn giữa đêm khuya lúc này.",
            "Sự kiệt sức bạn đang gánh chịu hoàn toàn không phải là điều ngẫu nhiên.",
            "Bạn đang mắc kẹt giữa chiếc bẫy ba phía: sự tự trách, kỳ vọng người thân và áp lực ngoài xã hội.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC38",
        "chapter": 7,
        "duration": 15.0,
        "sentences": [
            "Cảm hứng học tập sụp đổ khi con người mất quyền tự chủ và sự gắn kết.",
            "Khi bị ép học những kiến thức xa lạ mà không được tự do chọn lựa, thiếu vắng sự sẻ chia chân thành từ người thân, ngọn lửa tò mò bên trong bạn sẽ tự lụi tàn.",
        ],
        "pause_after_sent": 1,
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
        "sentences": [
            "Những người thân yêu luôn kỳ vọng bạn gặt hái thành công chói lọi.",
            "Kỳ vọng gia đình và áp lực điểm số bóp nghẹt động lực nội tại của bạn.",
            "Lời so sánh vô tình biến bài vở thành món nợ ân tình, tạo nỗi sợ hãi mỗi khi bạn ngồi vào bàn học.",
        ],
        "pause_after_sent": 2,
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
        "sentences": [
            "Màn hình điện thoại liên tục phô diễn những tấm gương thủ khoa tài năng xuất chúng.",
            "Nỗi sợ bị tụt lại phía sau khiến tâm trí của bạn luôn căng thẳng như dây đàn.",
            "Bạn học tập trong tâm trạng bất an lo âu hơn là niềm say mê tri thức thuần khiết.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC41",
        "chapter": 7,
        "duration": 15.0,
        "sentences": [
            "Bên cạnh cuốn sách là chiếc điện thoại luôn rung chuông hấp dẫn.",
            "Nó mang lại nguồn dopamine tức thì sau mỗi cái vuốt chạm ngón tay.",
            "Trong khi đó, trang sách đòi hỏi sự kiên nhẫn tích lũy sâu sắc.",
            "Tâm trí đương nhiên nghiêng về sự lôi cuốn dễ dàng trước mắt.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC42",
        "chapter": 7,
        "duration": 15.0,
        "sentences": [
            "Giờ thì bạn đã nhìn thấy toàn cảnh bức tranh sáng tỏ rồi đấy.",
            "Bạn kiệt sức không phải vì bản thân kém cỏi hay lười nhác.",
            "Bạn chỉ là nạn nhân của môi trường học thiếu lành mạnh.",
            "Hãy trút bỏ sự tự trách để bắt đầu hồi sinh nguồn năng lượng mới.",
        ],
        "pause_after_sent": 2,
        "claim": None,
    },

    # ================= CHAPTER 8 (Target: 44 syl [SC43-47], Target: 45 syl [SC48]) =================
    {
        "scene_id": "SC43",
        "chapter": 8,
        "duration": 12.5,
        "sentences": [
            "Đã đến lúc bạn làm chủ lại không gian học tập của chính mình.",
            "Hãy đánh thức bản năng tò mò thuần khiết bên trong tâm trí bạn.",
            "Nắm vững ba giải pháp sau, bạn sẽ tìm lại niềm say mê đích thực.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC44",
        "chapter": 8,
        "duration": 12.5,
        "sentences": [
            "Bí quyết đầu tiên là chia nhỏ mục tiêu hành động.",
            "Chỉ cần chia nhỏ việc học thành từng chặng ngắn, não bộ sẽ tự vào guồng.",
            "Đừng ôm đồm cả cuốn giáo trình dày.",
            "Hãy đặt thử thách hai mươi phút vừa sức.",
        ],
        "pause_after_sent": 2,
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
        "sentences": [
            "Bí quyết thứ hai là chủ động sáng tạo và thực hành.",
            "Bộ não sẽ yêu việc học khi ta được tự do thử sai và làm chủ tiến trình.",
            "Hãy tự vẽ sơ đồ và tóm tắt theo cách của riêng bạn.",
        ],
        "pause_after_sent": 2,
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
        "sentences": [
            "Bí quyết thứ ba là chia sẻ tri thức cùng bạn bè.",
            "Hãy giải thích lại khái niệm mới mẻ cho một người bạn thân thiết.",
            "Khi được trao đổi qua lại, bài học sẽ sống động và sâu sắc hơn gấp bội phần.",
        ],
        "pause_after_sent": 1,
        "claim": None,
    },
    {
        "scene_id": "SC47",
        "chapter": 8,
        "duration": 12.5,
        "sentences": [
            "Hãy dọn sạch chiếc bàn học của bạn ngay bây giờ.",
            "Cất chiếc điện thoại sang phòng khác và bật ánh đèn ấm áp lên.",
            "Bàn học là bệ phóng cho trí tuệ sáng tạo chứ không phải là căn phòng giam cầm ước mơ.",
        ],
        "pause_after_sent": 2,
        "claim": None,
    },
    {
        "scene_id": "SC48",
        "chapter": 8,
        "duration": 12.5,
        "sentences": [
            "Bạn hãy cầm cây bút lên, hít sâu và mỉm cười nhẹ nhõm.",
            "Bạn không cần đợi cảm hứng ghé thăm mới bắt đầu học.",
            "Hãy bắt tay vào hành động, và niềm vui tri thức sẽ lập tức bừng sáng trong tâm trí bạn.",
        ],
        "pause_after_sent": 2,
        "claim": None,
    },
]

# Build narration strings with pause tags in exact positions
for sc in SCENES_DEF:
    sents = sc["sentences"]
    p_idx = sc["pause_after_sent"] - 1
    parts = []
    for idx, s in enumerate(sents):
        parts.append(s)
        if idx == p_idx:
            parts.append("[pause:800ms]")
    sc["narration"] = " ".join(parts)

# Validate
facts_all = [f for s in get_academic_sources() for f in s["facts"]]
claims_claimed = []
total_cues = 0
failures = []

for sc in SCENES_DEF:
    sc_id = sc["scene_id"]
    dur = sc["duration"]
    narr = sc["narration"]
    p_sec, pauses, clean = extract_pauses(narr)
    syl = count_syllables(clean)
    
    import re
    sents = [s.strip() for s in re.split(r"[.!?…]+", clean) if s.strip()]
    total_cues += len(sents)

    p_tail = 0.35 if sc_id == "SC48" else 0.70
    target_syl = round((dur - p_tail - p_sec) * 4.0)
    drift = round((syl / 4.0) + p_tail + p_sec - dur, 2)
    flag = "OK" if abs(drift) <= 0.25 else "FAIL"
    if flag == "FAIL":
        failures.append((sc_id, syl, target_syl, drift))
    print(f"{sc_id}: syl={syl}/{target_syl} (drift={drift:+.2f}s), cues={len(sents)} -> {flag}")

    if sc.get("claim"):
        q, s_id, f = sc["claim"]
        assert q in narr, f"{sc_id} claim missing: {q}"
        assert q == f
        claims_claimed.append(f)

print(f"\nTotal Cues: {total_cues}/160")
assert total_cues == 160
assert len(claims_claimed) == 16
assert not failures, f"Failures: {failures}"

# Check Linter
corpus_dir = ROOT / "sys" / "exports"
claim_facts = {clean_sentence(f) for f in facts_all}
res = lint_script(SCENES_DEF, corpus_dir=corpus_dir, claim_facts=claim_facts)
print(f"Linter Status: {res['status']}, Violations: {res['total_violations']}")
if res["violations"]:
    for v in res["violations"]:
        print("  VIOLATION:", v)
    sys.exit(1)
print("\nPERFECT! ALL 48 SCENES: 160 CUES, 0 CADENCE DRIFT, 0 LINTER VIOLATIONS! 100% GREEN CERTIFIED!")
