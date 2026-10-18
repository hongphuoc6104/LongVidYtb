# Kế hoạch hình ảnh người que 2D: giản lược vừa đủ, sáng dịu, không rối mắt

Cập nhật: 18/10/2026. Trạng thái: đã triển khai phong cách người que 2D sáng dịu 1.4.0, cập nhật thư mục làm việc chính và tạo sáu ảnh Flow mới từ ba video trước. Đã qua 246 kiểm tra, đủ sáu trạm trên nhánh kiểm tra sạch và hai lượt GitHub Actions thành công. Xem kết quả ở mục 8.

## 1. Yêu cầu đã được làm rõ

Giữ nét vẽ 2D và người que. Mọi hình tạo mới cần đơn giản hơn về mô tả, chi tiết nền và cách dùng màu; nhìn tự nhiên, dịu mắt, có điểm thu hút và vẫn đủ bối cảnh để hiểu câu chuyện.

- Bối cảnh được lựa chọn linh hoạt theo nội dung: căn phòng bình thường có thể chỉ cần vài dấu hiệu nhận biết; không cần vẽ đầy đủ mọi thứ trong phòng.
- Nền có thể là phòng, ngoài trời, địa điểm lịch sử hoặc không gian khái niệm tùy câu chuyện. Không mặc định một căn phòng, một hoàn cảnh, một thời điểm hoặc một bảng màu cho mọi ảnh.
- Người que, biểu cảm, tư thế và đồ vật quan trọng cần rõ; chi tiết trang trí và đồ nền có thể bỏ bớt hoặc vẽ nhẹ hơn.
- Giữ trang phục, bố cục và đồ vật nhất quán khi tiếp nối cùng một cảnh; các bối cảnh độc lập được chọn màu và trang phục phù hợp vai trò.
- Màu sáng nhẹ, pastel linh hoạt, nét vừa phải; giảm mảng đen, màu sẫm diện rộng và tương phản gắt.
- Mức giản lược là đủ để dễ nhìn, không phải nền trống hoàn toàn, thiếu ngữ cảnh hoặc hình nhạt đến khó đọc.

Kế hoạch này thay thế nội dung trước đó về chuyển sang ảnh gần chụp thật và ưu tiên một nhóm bối cảnh cố định. Hai hướng đó không phản ánh yêu cầu đã được làm rõ.

## 2. Kiểm tra nhận xét của người dùng bằng ảnh và prompt thực

Đã đối chiếu actual_prompt của tám ảnh trong các gallery.json, cùng registry 1.3.0 được pin tại các job đã xem. Các nhận xét dưới đây nói về mẫu đã kiểm tra, không suy rộng thành mọi ảnh đều có cùng lỗi.

| Ảnh gốc | Prompt/mô tả thực tế liên quan | Quan sát và kết luận |
| --- | --- | --- |
| Collector — phòng tối (local artifact: `sys/runs/collectors-fallacy-16x9/revisions/images/6/SC11_I1_16x9.jpg`) | “A moody student room lit only by the cold pulsing light of an external drive.” | Phần lớn phòng phủ xanh đen; ít đồ nhưng vẫn nặng mắt. Đây chủ yếu là vấn đề độ sáng, khác với vấn đề nhiều chi tiết. |
| Collector — phòng sáng (local artifact: `sys/runs/collectors-fallacy-16x9/revisions/images/6/SC16_I1_16x9.jpg`) | “A serene minimalist study room with abundant natural light.” | Nền sáng và thoáng hơn rõ rệt, nhưng áo xanh đậm, quần navy và nét đen vẫn nặng. Đây là mốc tham khảo về độ thoáng, chưa phải phong cách đã đạt. |
| Adversarial AI — hội đồng (local artifact: `sys/runs/adversarial-ai-16x9/revisions/images/6/SC02_I1_16x9.jpg`) | “Three committee professors sit solemnly behind an academic evaluation table.” | Có nhiều kệ sách, sách từng cuốn, bảng biểu, chồng giấy và đồ bàn ngoài hành động ba người ngồi. Mô tả hành động ngắn vẫn có thể dẫn tới ảnh nền nhiều chi tiết. |
| Adversarial AI — mạng khái niệm (local artifact: `sys/runs/adversarial-ai-16x9/revisions/images/6/SC03_I1_16x9.jpg`) | Không gian máy tính khái niệm và “A glowing holographic visualization of neural network token prediction paths.” | Nhiều nhánh, màn hình, dây cáp, đường kiến trúc và đường phát sáng cùng cạnh tranh. Cần giản lược cách biểu diễn nhưng vẫn giữ ý giải thích của cảnh. |
| Reviewer — màn hình thư (local artifact: `sys/runs/reviewer-2-novelty-bias-16x9/revisions/images/6/SC01_I4_16x9.jpg`) | Bàn nghiên cứu ban đêm, màn hình phát sáng, đèn ấm; cận cảnh dòng thư từ chối. | Màn hình có điểm tập trung rõ, nhưng nền tối và nhiều đồ bàn, vùng vàng mạnh và viền đen làm ảnh nặng. Có thể giữ cảnh đêm và nội dung thư trong bản sửa. |
| Reviewer — cổng thành (local artifact: `sys/runs/reviewer-2-novelty-bias-16x9/revisions/images/6/SC03_I2_16x9.jpg`) | Thư viện cổ điển lớn và cổng thành tượng trưng cho cơ chế gác cổng phản biện. | Nhiều nhân vật, kệ sách, cột, vòm, gạch và đường nét. Ẩn dụ có thể được giữ nếu hữu ích; cần giảm chi tiết kiến trúc và các nhóm phụ thay vì mặc định đổi thành căn phòng khác. |
| Reviewer — bình minh (local artifact: `sys/runs/reviewer-2-novelty-bias-16x9/revisions/images/6/SC12_I1_16x9.jpg`) | Bàn học lúc bình minh, ánh nắng sáng sớm chiếu vào. | Có bản đồ, lịch, ảnh, quạt, dây điện, cặp, sách, rèm và cửa sổ nhiều thanh; ánh sáng đã ấm nhưng nền còn nhiều nét và vật phụ. |
| Collector dọc — điện thoại (local artifact: `sys/runs/collectors-fallacy-9x16/revisions/images/8/SC02_I1_9x16.jpg`) | Màn hình dọc với nhiều bài đã lưu từ hai năm trước. | Nền không tối, nhưng giao diện lặp nhiều hàng và nét đen rất dày. Có thể chỉ cần vài hàng gợi ý và một chi tiết thời gian quan trọng để giữ nghĩa “lưu lâu chưa đọc”. |

Ảnh tham chiếu đã xem: cast sheet của Collector (local artifact: `sys/runs/collectors-fallacy-16x9/revisions/images/2/REF-CH01.jpg`). Tờ tham chiếu có người que đúng yêu cầu, nhưng áo teal đậm, quần navy và viền đen dày. Gallery của các job Collector 16:9 và Adversarial AI 16:9 khai báo cùng hash ảnh tham chiếu. Đây là một nguồn có thể duy trì bảng màu nặng; cần kiểm tra bằng thử nghiệm trước khi kết luận mức tác động của reference.

Kết luận kiểm tra: nhận xét của người dùng có căn cứ. Tuy nhiên, cần xử lý riêng ba yếu tố: mật độ chi tiết, độ sáng/mảng màu và sức nặng đường nét. Có ảnh ít đồ nhưng tối; có ảnh sáng nhưng vẫn nhiều nét đen. Chỉ rút ngắn prompt hoặc giảm độ bão hòa màu sẽ không giải quyết hết.

## 3. Những điểm trong prompt đang đẩy hình theo hướng nặng

- Registry 1.3.0 dùng “thick confident black outlines” trong style, lặp “thick black outline” ở cast, và thêm “bold black outlines” ở cận cảnh tay. Đây là yêu cầu nét đen dày, không phải điều bắt buộc để giữ người que.
- Registry có câu “soft muted natural colors”, nhưng muted không đồng nghĩa với sáng nhạt. Màu xanh navy, xám nâu hoặc xanh đậm vẫn có thể dịu về độ bão hòa nhưng nặng về độ sáng.
- Một số mô tả cảnh yêu cầu “lit only”, “moody”, “glowing in the dark” hoặc ánh đèn gắt. Chúng có thể kéo cả ảnh vào mảng tối dù phần phong cách chung nói tránh dark grading.
- Các builder có style “deep navy accents”, outfit “teal shirt and navy trousers” và appearance viền đen dày. Đường sinh prompt và reference thực tế cần được đồng bộ; chỉ sửa content.style không đủ cho đường prompt pinned.
- Prompt chưa phân cấp rõ mức chi tiết giữa chủ thể và nền. Mô tả “một phòng hội đồng” dễ được triển khai thành phòng đầy kệ, sách và bảng khi không nêu mức giản lược phù hợp.
- Renderer có vignette tối mép khi hide_overlays không bật. Props render đã đọc của Collector và Adversarial AI khai báo modern_style: true, không khai báo hide_overlays; theo mã hiện tại, nhánh vignette 22% ở mép có thể được áp dụng. Đây là yếu tố cần đối chiếu frame video; ảnh gốc đã tối trước render nên vignette không giải thích toàn bộ vấn đề.

## 4. Quy chuẩn tạo hình đề xuất

| Thành phần | Hướng điều chỉnh |
| --- | --- |
| Người que | Giữ đầu tròn trắng, mắt/mặt đơn giản, chi que và tay hoạt hình; biểu cảm và tư thế diễn đạt câu chuyện. Không chuyển sang người thật. |
| Mức chi tiết | Vẽ rõ những gì giúp hiểu hành động; lược các vật không đóng góp. Không áp số lượng vật/người cứng cho mọi cảnh. |
| Background | Dùng vài dấu hiệu đủ nhận ra không gian, nét nền mảnh và nhẹ hơn chủ thể; bỏ bớt hàng sách, ô gạch, bảng nhỏ và dây nếu không cần. |
| Màu nền | Mảng màu sáng, sạch, nhẹ; pastel theo bối cảnh. Không phủ mọi cảnh bằng cùng màu kem, xanh hoặc tím. |
| Mảng tối | Giảm những vùng gần đen lớn ở tường, quần áo, đồ nội thất và bóng. Nét mặt, đồng tử và điểm cần rõ vẫn được dùng màu tối nhỏ. |
| Nét vẽ | Nét chủ thể mảnh đến vừa, nền nhẹ hơn; dùng charcoal/xám ấm tùy ảnh. Tránh viền marker đen dày bao mọi vật. |
| Ánh sáng | Ánh sáng mềm, chênh sáng vừa phải. Cảnh đêm vẫn là đêm nhưng có ánh sáng môi trường đủ đọc hình; không tự đổi mọi cảnh sang ban ngày. |
| Sức hút | Tạo qua tư thế, biểu cảm, tương quan lớn/nhỏ, khoảng thoáng và một điểm nhấn màu có mục đích. Không cần thêm nhiều đồ hoặc tăng độ đậm. |
| Ẩn dụ | Được dùng khi giúp hiểu ý. Mỗi khung giữ một quan hệ chính, giảm bộ phận trang trí; không cấm toàn bộ cảnh tưởng tượng. |

Mục tiêu: chủ thể rõ, nền vừa đủ, màu sáng dịu, tổng thể thoáng. Không yêu cầu nền trống, không bắt mọi cảnh thành phòng học, không đổi trường phái tạo hình.

## 5. Gợi ý prompt

### Phần phong cách dùng chung — không cố định bối cảnh

Đây là hướng phong cách đã duyệt. Bản triển khai nằm trong registry 1.4.0 và được kiểm tra qua sáu ảnh Flow thật; không đưa quy tắc style vào allowed_text hoặc giả làm dữ liệu cảnh.

> Hand-drawn 2D explainer illustration with anonymous round-white-headed stick figures, simple expressive faces, stick limbs and simplified cartoon hands. Preserve the requested setting, time of day, action and visual metaphor. Use a moderately simplified composition: make the main action clear and keep only the environmental cues needed to understand the scene. Suggest secondary objects with simple shapes and fewer interior lines; background linework is lighter and finer than the focal subject. Use light-value, gently muted colors chosen naturally for this scene, with soft illumination and restrained shadows. Keep dark values mainly in small facial features and essential focal contours rather than large filled areas. Use fine-to-medium charcoal or warm-gray outlines instead of thick black marker borders. Create interest through gesture, composition, open space and selective color accents. Keep enough context for the place to feel natural. Complete edge-to-edge illustration. Avoid muddy dark grading, harsh spotlights, neon saturation and decorative visual noise. Do not impose a fixed room, fixed palette or recurring outfit color. Render only the lettering supplied in allowed_text.

### Ví dụ mô tả cảnh ngắn, đủ ý

Các ví dụ này minh họa cách giản lược, không phải danh sách bối cảnh được phép.

- Phòng hội đồng: “Three stick-figure professors sit behind a table, listening thoughtfully. Suggest the meeting room with a plain wall and a simple door. Keep the people and their expressions clear; omit decorative shelves, tiny charts and repeated paper stacks.”
- Cảnh đêm: “A stick-figure student studies at a desk at night. A window suggests the time of day. Use soft ambient fill so the person and desk remain easy to see; simplify the rest of the room into quiet color shapes.”
- Cảnh khái niệm: “Two stick figures examine a simple branching prediction diagram. Show only the few branches needed to explain the choice. Suggest the surrounding space lightly; omit racks, cables and decorative screens.”

## 6. Kế hoạch triển khai theo ưu tiên

1. **Sửa lớp style và mô tả authoring.** Giữ người que; thay yêu cầu viền đen dày bằng nét vừa phải, thêm quy tắc nền nhẹ và giản lược vừa đủ, phân biệt màu muted với màu sáng. Gỡ các quy định palette/outfit sẫm mặc định không cần thiết; không xóa bối cảnh hoặc thay ý cảnh để đạt tiêu chí đơn giản.
2. **Phiên bản hóa và đồng bộ reference.** Dự kiến registry 1.4.0, giữ nguyên registry/pin lịch sử. Kiểm tra style sheet mới vì reference cũ có thể kéo màu và nét cũ trở lại. Đồng bộ compiler/caller, skill full-frame, brand reference và builder; giữ hợp đồng người que, Base/variation, full-bleed và allowed text.
3. **Thử có đối chứng trên đúng bối cảnh cũ.** Chọn sáu loại cảnh đa dạng: phòng ban ngày, cảnh đêm, cảnh nhiều người, ngoài trời, không gian khái niệm và cận cảnh. Đây là bộ kiểm tra, không phải giới hạn bối cảnh của sản phẩm. Với mỗi cảnh, giữ ý, số người cần thiết, tỷ lệ và model; đối chiếu đầu ra cũ với bản prompt đề xuất. Tạo sáu ảnh mới trước; chỉ mở rộng khi đã hiểu nguyên nhân lỗi còn lại.
4. **Đánh giá tách ba trục.** Kiểm tra chủ thể và hành động có rõ khi thu nhỏ; nền có quá nhiều chi tiết cạnh tranh; mảng màu và nét có còn nặng/tối. Ảnh đạt khi vẫn nhận ra bối cảnh và câu chuyện, có điểm thu hút, không trống hoặc nhợt nhạt. Thống kê màu/mật độ cạnh nếu dùng chỉ hỗ trợ quan sát, không tự chứng nhận thẩm mỹ.
5. **Kiểm tra trong video và áp dụng cho job mới.** Kiểm tra thêm cả hai tỷ lệ, chuỗi variation, phụ đề và frame video so với ảnh gốc; xem xét giảm/tắt vignette cho phong cách này. TTS/render dùng đường Colab/Remotion chính thức, xác minh MP4 bằng ffprobe. Sau khi bộ thử đạt, đổi mặc định cho mọi ảnh của job mới. Job hiện hữu đổi style qua revision/impact được hỗ trợ; không sửa journal/DB/pin bằng tay.

Ảnh thử đã được tạo bằng Flow CDP, có sidecar và prompt thực; không dùng ảnh mô phỏng tự vẽ làm bằng chứng. Kết quả và phạm vi xác minh nằm ở mục 8.

## 7. Phạm vi kỹ thuật khi triển khai

- Điểm sửa chính: sys/flow_prompts/versions/, sys/flow_prompts/compiler.py, sys/image_pipeline.py, sys/tools/research_story_architect.py, builder đang dùng và hướng dẫn style/reference. Các nhánh kiểm tra cứng 1.3.0 cho shot type/full-bleed phải được mở rộng có chủ đích cho phiên bản mới.
- Critique tiếp tục kiểm tra người que đúng hợp đồng; không loại bỏ invariant này. Thêm kiểm tra hành vi cho palette/style mới và việc caller không chèn lại nét đen dày.
- Giữ test lịch sử 1.3.0; thêm test phiên bản mới cho người que, tay hoạt hình, full-frame, tham chiếu, pin trước gửi và không gửi lặp khi replay.
- Chạy ./pipeline status trước khi sửa engine, các suite prompt/integration/full-frame liên quan và đủ sáu trạm của conveyor khi triển khai. Ghi PLAYBOOK đúng schema cho lỗi thực sự đã sửa; không tuyên bố chất lượng ảnh từ test fixture.
- Đánh giá thẩm mỹ bộ thử trong review; giữ đúng chế độ auto không reviewer. Bảo toàn thay đổi cục bộ, assets và request đang submitted/unknown.

Tiêu chí bàn giao: cùng phong cách người que 2D và bối cảnh linh hoạt, ảnh mới có nền giản lược vừa đủ, đường nét nhẹ hơn và màu sáng dịu hơn; có ảnh thật và video thử để chứng minh kết quả.

## 8. Kết quả triển khai và bàn giao

- Mặc định tạo ảnh mới: registry 1.4.0; người que 2D, nét charcoal vừa phải, màu sáng nhạt và background giản lược vừa đủ, không khóa căn phòng hoặc bảng màu.
- Đồng bộ authoring, prompt caller, hướng dẫn và các bộ tạo gói cục bộ; profile màu được truyền tới renderer để không thêm vignette/grain.
- Giữ nguyên byte các registry lịch sử và ảnh gốc. Sáu nguồn ảnh lịch sử đã đối chiếu lại hash, không đổi.
- Đã tạo và xem trực tiếp sáu ảnh Flow mới: cảnh đêm, đọc tài liệu ban ngày, hội đồng, sơ đồ dự đoán, rừng và điện thoại dọc. Cảnh đêm vẫn tối hơn các cảnh sáng; chưa ghi nhận phản hồi thẩm mỹ của người dùng.
- Trang so sánh trước–sau (local artifact: `sys/runs/soft-pastel-style-review-20261018/comparison.html`) · Bộ sáu ảnh mới (local artifact: `sys/runs/soft-pastel-style-review-20261018/new-images.zip`).
- Kiểm tra tại thư mục chính: 246 passed, 8 subtests passed; các thay đổi khác của người dùng được giữ lại nên thư mục chính không được ghi nhận là cây Git sạch.
- Nhánh kiểm tra sạch, commit 45a9a1464aedafab698b01ff6a3ec381d777161a: đủ sáu trạm và hai CI success. Chứng cứ được chép nguyên vẹn vào thư mục evidence của bộ ảnh thử.
- [PR nháp #2](https://github.com/hongphuoc6104/LongVidYtb/pull/2) lưu thay đổi engine và kiểm thử; đã áp dụng mã tương ứng tại thư mục làm việc chính.
- Chưa render MP4 mới. Kiểm tra renderer trong lượt này chứng minh đường truyền profile và hợp đồng metadata, không chứng nhận một video thực chưa được tạo.
