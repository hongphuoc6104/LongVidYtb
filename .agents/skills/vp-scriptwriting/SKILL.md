---
name: vp-scriptwriting
description: "Author and transform explainer video scripts into natural conversational spoken storytelling with counter-intuitive 3-second hooks and calibrated acoustic cadence."
---

# VP Scriptwriting — Conversational Essayist, Feynman Simplification & Voice Cadence Skill

`vp-scriptwriting` là bộ kỹ năng cốt lõi dùng để sáng tác và thẩm định kịch bản video trong Video Pilot (cho cả `long_16x9` và `short_9x16`). Bộ kỹ năng này được tối ưu hóa cho **Agent Gemini Flash**: chuyển hóa từ các ràng buộc cứng sang **hướng dẫn mang tính xây dựng (constructive guidance)**, vận dụng **phương pháp Feynman** để đơn giản hóa các ý niệm phức tạp qua các chuỗi câu đơn giản, giàu nhịp điệu cảm xúc và gắn kết 1-1 với hành động hình ảnh toàn khung (`full_frame_v1`).

---

## 1. Bản Sắc Giọng Kể, Phương Pháp Feynman & Nhịp Câu Tự Nhiên

- **Hình tượng (The Voice Archetype):** **Conversational Essayist (Nhà luận thuyết trò chuyện)** — điềm đạm, ấm áp, sắc sảo, như người bạn đồng hành tri thức bên bàn cà phê, theo tinh thần **"Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức"**.
- **Trục Phân Tích - Bình Luận - Đánh Giá Con Người (`human_editorial` Spine — Chống AI-Slop):**
  - Kịch bản lấy lập trường (`editorial_stance`) và các ý tưởng chi tiết mở rộng từ góc nhìn tác giả (`expanded_content_ideas` trong `brief.json`) làm **xương sống dẫn dắt**.
  - Tuyệt đối không viết theo lối tổng hợp thông tin trung tính kiểu Wikipedia/AI. Mỗi phân đoạn thể hiện rõ sự **phân tích nguyên nhân ngầm**, **bình luận phản biện**, và **đánh giá trọng số giá trị** của con người; dữ kiện khoa học (`sources`) được trích dẫn làm bằng chứng phục vụ cho trục bình luận đó.
- **Mở Đầu Hấp Dẫn & Lát Cắt Đời Thực Sát Sườn (Relatable & Grounded Hook):**
  - Mở đầu bằng câu thoại ngắn gọn, đi thẳng vào hành vi đời thực sát sườn hoặc một nghịch lý/quan sát phản trực giác mà người xem vừa trải qua — tránh ẩn dụ sách vở mơ hồ, sáo rỗng.
  - Trong đoạn mở đầu, kết nối lát cắt hành vi quen thuộc với cơ chế nhận thức đằng sau bằng ngôn ngữ bình dân sắc bén (ví dụ: *"Đi làm về mệt rã rời, bạn nằm vật ra giường để xả hơi một chút. Tay cầm điện thoại định lướt mười lăm phút, mà ngoảnh đi ngoảnh lại đã trôi vèo hai tiếng... Thật ra thứ được nghỉ lúc đó chỉ là cái lưng của bạn, chứ không phải bộ não."*).
  - Giải thích cơ chế tâm lý/nhận thức qua **các đối cực hành vi đời thường cụ thể** (*"giây trước vừa bật cười vì một đoạn hài ngắn, giây sau đã căng thẳng xem người lạ cãi vã"*, *"bưng bát cơm hay nhắm mắt đi ngủ, máy vẫn chạy"*, *"bật tiếng rì rầm bên gối chỉ vì sợ sự im lặng"*) thay vì liệt kê thuật ngữ trừu tượng (*"nén cảm xúc"*, *"quá tải thông tin"*).
  - **Tránh** mở đầu bằng lời chào sáo rỗng (*"Xin chào"*), giới thiệu đề tài máy móc (*"Hôm nay chúng ta..."*), hoặc câu dẫn nhập chậm (*"Hãy nghĩ về..."*, *"Hãy hình dung..."*, *"Hãy tưởng tượng..."*, *"Giờ đây, hãy thử..."*).
- **Ưu Tiên Từ Thuần Việt Trơn Âm (Tránh Từ Mượn Dễ Lắp Bắp Trên TTS):**
  - Khi có từ tiếng Việt tự nhiên tương đương, ưu tiên dùng từ thuần Việt giàu sức gợi (*"đoạn hài ngắn"*, *"lướt điện thoại"*, *"bỏ máy xuống"*, *"tiếng rì rầm"*) thay vì lạm dụng từ mượn phiên âm (`"vi-đê-ô"`, `"pót-cát"`, `"nô-ti-phi-cây-sần"`) khiến giọng đọc mất tự nhiên.
- **Nhịp Thở Âm Học Tự Nhiên & Khoảng Nghỉ:**
  - Ở đoạn mở đầu, giữ lời dẫn trôi chảy, nhịp nhàng. Không lạm dụng các thẻ `[pause:...]` kịch tính quá dày đặc ở phần đầu để giữ đà cuốn hút; để hệ thống âm học tự động xử lý các khoảng lấy hơi tự nhiên (`breaths`).
- **Quy Tắc Nhịp Điệu & Phương Pháp Feynman (Feynman Technique & Chained Simple Sentences):**
  - **Chuỗi câu đơn giản giải thích ý niệm phức tạp (Chained Simple Sentences):** Áp dụng nguyên lý Feynman: mỗi câu chỉ truyền tải **một ý niệm duy nhất**, sử dụng ngôn từ đời thường giản dị. Khi giải thích cơ chế phức tạp, hãy xâu chuỗi nhiều câu đơn mạch lạc thay vì dồn nén vào một câu ghép dài dòng, đa tầng nấc.
  - **Xen kẽ nhịp điệu sinh động:** Kết hợp tự nhiên giữa các câu ngắn đanh gọn (nhấn mạnh kết luận, thức tỉnh nhận thức) với các câu giải thích cơ chế liền mạch. Với câu kết đoạn có cụm âm mũi nặng (`-ng`, `-m`, `-n`), giữ độ dài gọn gàng để giọng đọc hạ kết trọn vẹn, không hụt hơi.
  - **Cấm ngắt dấu phẩy ngang xương giữa Chủ ngữ và Vị ngữ:** Tuyệt đối không chèn dấu phẩy vô lý giữa chủ ngữ và động từ (ví dụ sai: *"Bản chất của tổng quan tài liệu, là..."* hoặc *"Đó là nơi bạn vẽ nên, khoảng trống..."*). Hãy tách hẳn thành hai câu tự nhiên.
  - **Tự động chuẩn hóa ở Backend:** Hệ thống (`sys/remote_audio.py`, `sys/adapters.py`, `sys/colab_bridge/worker.py`) tự động tách thẻ `[pause:...]` thành khoảng nghỉ âm học thực tế, tự động phiên âm số/từ mượn qua `vn_text_normalizer.py` và tự động gỡ dấu gạch nối liên chữ trước khi vào BPE TTS. Agent chỉ cần tập trung viết câu tiếng Việt đời thực, giàu hình ảnh.

### Few-Shot Exemplars: Phương Pháp Feynman Trong Kịch Bản

Dưới đây là các ví dụ mẫu (exemplars) minh họa cách dùng chuỗi câu đơn giản để bóc tách các khái niệm học thuật/nhận thức phức tạp:

- **Mẫu 1 — Quá Tải Nhận Thức (Cognitive Load):**
  > *"Khi bạn làm việc, bộ não giống như một cái bàn. Chiếc bàn chỉ để vừa ba cuốn sách. Nếu bạn chất lên mười cuốn, sách sẽ rơi xuống đất."*
  > *(Thay vì: "Hiện tượng suy giảm khả năng xử lý thông tin do quá tải tải nhận thức ngoại lai vượt ngưỡng dung lượng bộ nhớ làm việc.")*

- **Mẫu 2 — Gợi Nhớ Chủ Động (Active Recall):**
  > *"Đọc lại một trang sách năm lần chỉ giúp mắt bạn quen mặt chữ. Não bạn không hề vận động. Muốn nhớ thật, bạn phải gấp sách lại và tự hỏi: mình vừa đọc được gì?"*
  > *(Thay vì: "Phương pháp đọc thụ động tạo ra ảo giác năng lực nhận thức thay vì củng cố đường mòn synapse qua thực hành truy xuất thông tin chủ động.")*

- **Mẫu 3 — Nguyên Lý Gốc (First-Principles Thinking):**
  > *"Thay vì học thuộc lòng hàng chục công thức rời rạc, hãy nhìn vào quy luật cơ bản nhất. Chiếc xe đạp hay tên lửa vũ trụ đều bắt đầu từ định luật chuyển động. Hiểu được gốc rễ, bạn sẽ tự dựng lại được toàn bộ bức tranh."*
  > *(Thay vì: "Tư duy nguyên lý tiên đề đòi hỏi phân rã hệ thống thành các chân lý căn bản không thể giản lược hơn rồi tái cấu trúc theo mô hình diễn dịch.")*

---

## 2. Mạch Truyện Thích Ứng (Adaptive Narrative Flow) & Điều Biến Giọng Động

1. **Mạch Truyện Linh Hoạt Theo Chiều Sâu (`content_depth_estimate`):**
   - Kịch bản phát triển tự nhiên theo dòng suy nghĩ của người xem, thích ứng với độ phức tạp của đề tài mà không bị bó buộc vào số lượng chặng cứng nhắc:
     - **Mở bài (`hook` / `lead_in`):** Quan sát đời thực sát sườn, gợi mở câu hỏi cốt lõi (`tone: "narrative_warm"`).
     - **Vấn đề & Mâu thuẫn (`problem`):** Phơi bày khoảng cách giữa cách hiểu thông thường và thực tế.
     - **Cơ chế nhân quả (`causal_mechanism` / `explanation`):** Giải phẫu quy luật gốc rễ bằng phương pháp Feynman, mô hình hóa trực quan qua sơ đồ hoặc ẩn dụ vật lý (`visual_diagram`, `concept_metaphor`).
     - **Phản biện & Mở rộng (`counter_argument`):** Lật ngược giả định, xem xét giới hạn hoặc góc nhìn đa chiều để tránh phiến diện.
     - **Đúc kết & Hành động (`takeaway` / `closing`):** Đúc kết nguyên lý then chốt, khép vòng lặp ý niệm với mở bài (`tone: "reflective_slow"`).
   - **Điều biến `tone` động (`_infer_scene_tone`):** Hệ thống tự động xen kẽ `reflective_slow` hoặc `narrative_warm` ở các cảnh đặt câu hỏi bản chất (`?`, `tại sao`, `nghịch lý`, `sụp đổ`, `ảo giác`) để giữ sóng cảm xúc.
2. **Chuyển Ý Tự Nhiên (Cấm Khẩu Hiệu Mục Lục Kiểu AI):**
   - Tránh các câu dẫn sáo rỗng hoặc thông báo mục lục máy móc (*"Phần 1 là..."*, *"Bước sang phần hai..."*, *"Đầu tiên chúng ta hãy..."*, *"Tóm lại là..."*, *"Trong kỷ nguyên số hiện nay..."*, *"Như một con dao hai lưỡi..."*, *"Nhưng rồi..."*, *"Hãy cùng khám phá..."*). Hãy chuyển mạch bằng câu hỏi kích hoạt tò mò hoặc từ nối tự nhiên (*"Vấn đề nằm ở chỗ..."*, *"Thế nhưng có một điều kỳ lạ..."*, *"Nếu nhìn sâu vào cơ chế..."*, *"Khoan đã, liệu điều này có luôn đúng?"*).
3. **Phân Vùng Bối Cảnh Nhất Quán (Chronology & Contextual Flow):**
   - Dẫn dắt dòng thời gian và bối cảnh mạch lạc, tránh nhảy cóc thời kỳ tùy tiện. Mở đầu bằng những tình huống gần gũi, quen thuộc để người xem dễ dàng đồng cảm.

---

## 3. Viết Kịch Bản Gắn Kết Với Nhịp Hình Ảnh (`Clause/Sentence-Beat Pairing`)

Soạn kịch bản theo từng cặp **`(Câu hoặc mệnh đề thoại tự nhiên, "loại_shot|Hành động hình ảnh cụ thể")`** (như trong hàm `build_scenes_from_story_rows` trong `sys/content/research_story_architect.py`):

- **`full_scene`**: Nhân vật doodle đầu tròn trắng (`CAST_APPEARANCE`) và đồ vật tương tác trực tiếp trên sân khấu 2D phẳng.
- **`variation`**: Giữ nguyên bối cảnh 2D và góc máy của ảnh trước (`based_on`), chỉ đổi cử chỉ tay/biểu cảm nhân vật.
- **`macro_prop`**: Cận cảnh bàn tay tròn trắng / đạo cụ chính trên nền màu phẳng 2D.
- **`visual_diagram`**: Sơ đồ nhân quả hoặc biểu đồ so sánh vẽ tay nguệch ngoạc trực quan trên nền màu phẳng (`camera: hold`).
- **`concept_metaphor`**: Ẩn dụ thị giác kiểu truyện tranh 2D (`Nguệch Ngoạc`) vật lý hóa cơ chế trừu tượng (quả tạ đè đầu, đám mây suy nghĩ, tia sét cảm xúc).
- **`cutaway_detail`**: Cửa sổ cắt lớp mở nửa trên chiếc đầu tròn trắng tinh `#FFFFFF` để lộ người que tí hon hoặc bộ não đang quá tải bên trong.
- **`white_card`**: Thẻ khái niệm nền màu phẳng (`#FFFFFF`, `#F8F0DC`, `#F2B88B`, `#2E4361`) cô lập một đối sánh tối giản (`camera: hold`).
- **`white_isolated`**: Nền phẳng `#FFFFFF` hoặc `#F8F0DC` với đối tượng hoặc nhân vật được cô lập hoàn toàn.
- **`still_life`**: Nhịp nghỉ thị giác tập trung vào 1–2 vật thể 2D phẳng — không vẽ nhân vật.
- **`environment`**: Nhịp nghỉ thị giác sân khấu 2 mặt phẳng tối giản — hoàn toàn vắng bóng nhân vật.

1. **Công Thức Thị Giác Feynman & Nhịp Kể (Feynman Visual Formula):**
   - **1 nhân vật + 1 ẩn dụ trọng tâm:** Tập trung sự chú ý vào một nhân vật que doodle và một ẩn dụ thị giác cốt lõi trên nền phẳng sạch sẽ (`#FFFFFF` hoặc `#F8F0DC`), chiếm ít nhất 60% khoảng trống âm (*negative space*).
   - **Khung hình domino phát triển tuần tự:** Các khung hình bổ sung chi tiết từng bước theo đà diễn giải của câu chuyện, không nhồi nhét đồ đạc, đường chân tường hay chi tiết trang trí thừa thãi.
   - **Mô tả bối cảnh gọn gàng:** Mô tả không gian 2D tối giản và ánh sáng/màu nền, tập trung vào hành động và ý niệm biểu đạt.
2. **Cold open (`0:00–0:15`, `SC01`) & Căn Khớp Kép Ước Tính / Thực Đo:**
   - Với cảnh mở đầu `SC01` dài ~70–75 chữ (~15s WAV thực đo), chia thành các nhịp hình linh hoạt (khoảng 1.0–2.5s/nhịp) để mở màn sống động và khớp với timeline âm thanh thực tế. Tránh lặp lại các câu lệnh vật lý vụn vặt liên tiếp.
3. **Thân bài (`sau 0:15`):**
   - Với câu dài có bước ngoặt ý, tách thành các nhịp hình theo mệnh đề (`split_long_sentence_into_beat_clauses()`) để mỗi nhịp hình rơi vào khoảng **`1.2s–3.5s`**, kể chuyện thí nghiệm và giải thích cơ chế sinh động mà không trích dẫn khô khan kiểu `et al.`, `DOI:`, `(2008)`.

---

## 4. Công Cụ Kiểm Tra Tự Động

Các công cụ kiểm tra tự động chạy ở chế độ **cảnh báo xây dựng (soft advisory warnings, `strict=False` mặc định)** để hỗ trợ tác giả tinh chỉnh kịch bản mà không chặn luồng sáng tạo:

```bash
# Phân tích âm học, nhịp điệu và độ trôi timeline (cảnh báo mềm khuyến nghị)
python3 sys/tools/script_cadence_checker.py path/to/content.json

# Kiểm định tính đa dạng từ vựng và cấu trúc chuyển ý (cảnh báo mềm khuyến nghị)
python3 sys/tools/script_diversity_linter.py path/to/content.json
```

*Lưu ý: Tùy chọn `--strict` có thể được kích hoạt khi cần kiểm định nghiêm ngặt tuyệt đối trong CI.*

---

## 5. Danh Mục Tài Liệu Tham Khảo

- [Khung Kể Chuyện Conversational Essayist](references/conversational-essayist-framework.md)
- [Sổ Tay Lời Dẫn Văn Nói Tiếng Việt](references/spoken-narration-guide.md)
- [Quy Chuẩn Giọng Đọc, Tốc Độ & Ngắt Nhịp](../vp-channel-patterns/references/voice-cadence-pacing.md)
- [Chỉ Dẫn Kịch Bản Sản Xuất](../vp-production/references/script.md)
- [Chỉ Dẫn Âm Thanh Sản Xuất](../vp-production/references/audio.md)
- [Hợp Đồng Chất Lượng Toàn Khung](../vp-full-frame-quality/SKILL.md)

## Active pause authoring (format_v1)

- Default gaps come from `sys/format_profiles.py`; do not add a pause at every image cut.
- SC01 has short automatic breaths for smooth flow.
- Suggested intentional pivots: 450 ms for standalone shorts, 600 ms for long narration. Existing tags remain exact; never silently compress them. Use a terminal tag for a deliberate major scene transition.
- Run `sys/tools/preview_narration_pauses.py` for planned silence; actual WAV determines timing. Legacy cadence estimates are not the new pause budget.
- Details and rollout: [pause implementation plan](../../../sys/docs/narration-pause-implementation-plan.md).

## ContentPhilosophy `research_guide`
- Hook theo kiểu tutorial: SC01 nêu vấn đề thực tế của người mới nghiên cứu + lời hứa kết quả rõ ràng. Diễn đạt chân phương, dễ hiểu theo phương pháp Feynman, chia sẻ giải pháp từng bước một cách mạch lạc.
