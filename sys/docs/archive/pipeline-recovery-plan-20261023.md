# Phương án phục hồi pipeline Video Pilot

**Tài liệu triển khai hiện hành:** [Kiểm tra từng nhánh và kế hoạch sửa tích hợp](module-merge-audit-20261023/PLAN.md). Kế hoạch chi tiết này bổ sung xác nhận của người dùng rằng images/audio đã kiểm duyệt, video đã thử đạt; content/core chưa duyệt. Dùng tài liệu chi tiết thay cho phương án khái quát bên dưới.

Mục tiêu: giữ chất lượng đã chốt ở từng module khi chạy qua core; tự phục hồi đúng chỗ; thời gian được đo rõ; kết thúc bằng video thật đã kiểm tra. Cơ sở: báo cáo `diagnosis-ai-sycophancy-20261023.md`, core `54694e0`, nhánh ảnh chuẩn `module-images` tại `61aaf74` và các thay đổi chưa commit đang có trong thư mục ảnh.

Đây là phương án triển khai, chưa phải xác nhận các thay đổi đã được áp dụng hoặc kiểm chứng toàn trình.

**Kết quả người dùng cần nhận**

- Một lệnh chạy từ chủ đề/nội dung đến MP4/SRT, theo auto hoặc review.
- Core gọi cùng bộ xử lý mà các module dùng khi chạy riêng.
- Hình giữ đúng phong cách, cách dùng nhân vật, cảnh, hình giải thích và ảnh tham chiếu đã duyệt. Không ép tất cả hình thành nền trắng, cũng không tự thêm ánh sáng/căn phòng làm lệch mẫu.
- Giọng VietNarrator, tốc độ 1.0; thời lượng linh hoạt theo nội dung và âm thanh đo được.
- TTS và render chạy trên Colab; Flow dùng pool profile với quyền sở hữu và vòng đời rõ ràng.
- Lỗi ở một phần chỉ làm lại phần cần thiết; dữ liệu còn hợp lệ được giữ.
- Trạng thái cho biết đang chuẩn bị, đang xử lý, đang lấy kết quả, đang phục hồi hay cần chú ý. Có số liệu tiến triển thật.

**1. Giữ nguyên chuẩn ảnh và chặn lệch ngay từ nội dung**

1. Lưu nhận diện phiên bản bộ ảnh chuẩn, prompt compiler, model và các yêu cầu đã dùng để tạo mẫu. Bộ test hiệu năng không tự được coi là mẫu thẩm mỹ cho mọi loại cảnh.
2. Chọn các mẫu sẵn có đại diện cho: cảnh có người, vật thể, sơ đồ và cảnh nối tiếp. Đối chiếu theo đúng loại cảnh đã được duyệt.
3. Dùng cùng dữ liệu cảnh qua đường gọi riêng và core; so sánh yêu cầu thực sự gửi cho Flow: văn bản, model, tỉ lệ, tham chiếu, ảnh gốc và phần được giữ/thay.
4. Sửa các thay đổi ngoài ý muốn ở phần soạn cảnh, giữ ảnh gốc và thử lại. Khi thử lại vì lỗi kết nối, nội dung yêu cầu không đổi. Yêu cầu bị nhà cung cấp từ chối phải được phân loại riêng, không lén sửa mô tả để tạo một ảnh khác.
5. Bảo đảm mô tả cảnh từ content tuân thủ phong cách: bối cảnh và ánh sáng chỉ xuất hiện khi có chủ ý, không tự lặp quán cà phê/đèn vàng cho mọi câu chuyện.
6. Nếu dùng ảnh mẫu phong cách, xác minh khả năng đính kèm và đăng ký trên từng profile; ảnh nhận dạng người và ảnh gốc của cảnh giữ mục đích riêng. Không tự coi một tệp mẫu đã tồn tại trên mọi tài khoản.
7. Nhận chọn lọc thay đổi đang có ở thư mục ảnh. Không chép toàn bộ bản sửa chưa commit: cần giữ hợp đồng 1.7.0, yêu cầu nội dung hiện hành và các cải thiện có chủ ý. Việc trả một hàm về mặc định 1.6.0 chưa tự chứng minh giữ đúng chuẩn 1.7.0.

Điều kiện đạt: đầu vào gửi đi tương đương giữa module riêng/core với cùng một cảnh; mẫu hình mới phù hợp bộ chuẩn khi xem trực tiếp. Kết quả kiểm thử mã không thay cho kiểm tra hình.

**2. Một bộ xử lý cho mỗi module, hai cách gọi**

- Lệnh chạy riêng và core đều gọi một đầu vào công khai của module tương ứng; loại bỏ các đường gọi sản xuất có hành vi khác nhau.
- Core quản lý thứ tự, phiên bản, tài nguyên, phục hồi và thu kết quả. Các module sở hữu xử lý chuyên môn của mình.
- Hợp đồng dữ liệu chung ghi rõ: phiên bản nội dung/cấu hình, tệp đầu vào, tệp đầu ra, trạng thái, quyền sở hữu yêu cầu và lỗi đã phân loại.
- Content xuất cảnh và neo lời kể; audio xuất WAV, thời gian đo thật và mốc lời; images xuất ảnh và bằng chứng nguồn; video nhận các đầu ra đó để tạo timeline và MP4/SRT.
- Thay đổi nội dung làm hết hạn đúng đầu ra phụ thuộc. Sửa ảnh không làm lại giọng khi lời đọc còn nguyên; sửa render không tạo lại ảnh/giọng còn hợp lệ.

Điều kiện đạt: kiểm tra đường gọi thực chứng minh core sử dụng đúng bộ xử lý đã thử riêng; kiểm tra đổi đầu vào và chạy lại riêng từng khâu không thu nhầm kết quả cũ.

**3. Khôi phục tăng tốc âm thanh và bảo vệ phiên máy**

- Giữ bản sửa gửi đủ `audio_processing.py`, `subtitles.py`, `media_packaging.py`; kiểm tra đủ tệp và phiên bản trước khi gửi việc.
- Nối khả năng chia TTS cho nhiều T4 vào đúng đường sản xuất, có đầy đủ hợp đồng đầu ra, quyền chạy và phục hồi. Không chỉ đổi tên hàm được gọi.
- Chọn số máy theo lượng công việc, tài khoản sẵn sàng và chi phí khởi tạo; giữ đúng thứ tự câu và các khoảng nghỉ.
- Ghép, xử lý và đo âm thanh trên Colab theo ranh giới remote/local của dự án; không đưa tác vụ media nặng về máy điều phối.
- Bộ quản lý phiên chỉ thu hồi phiên khi mọi công việc thuộc quyền của nó đã kết thúc/thu kết quả, hoặc có yêu cầu dừng hợp lệ. Một worktree không được tắt tài nguyên đang phục vụ công việc khác.
- Kiểm tra đường chạy render không phải chuẩn bị lại toàn bộ môi trường TTS không cần thiết; bộ nguồn và môi trường được kiểm tra theo loại công việc.

Điều kiện đạt: quan sát được các phần TTS chạy trên nhiều máy khi phù hợp; đầu ra đo được đủ câu, đúng thứ tự, không lệch phụ đề; phiên không bị dọn giữa chừng.

**4. Phục hồi Flow đúng yêu cầu, đúng tài khoản**

- Tách ba tình huống: chắc chắn chưa gửi; đã gửi và đang lấy kết quả; chưa xác định kết quả gửi.
- Chỉ gửi lại khi đã chứng minh chưa gửi. Khi đã gửi/chưa rõ, kiểm tra và thu yêu cầu cũ trên đúng chủ sở hữu.
- Nhận diện chủ sở hữu bằng đầy đủ profile/tài khoản/dự án/phiên; giữ chuỗi ảnh dựa trên cùng một ảnh gốc ở nơi có quyền sử dụng ảnh gốc.
- Chỉ giao việc cho profile có kết nối và dự án sẵn sàng; giảm hoặc thay worker cho công việc mới khi profile hỏng.
- Phục hồi lỗi tạm thời với số lần giới hạn và tiến độ rõ ràng. Lỗi dữ liệu hoặc từ chối của nhà cung cấp phải nêu đúng phần cần xử lý.
- Luôn đóng đúng tài nguyên được mở bởi lượt chạy; giữ kết quả đã tải và kiểm tra để tiếp tục từ phần còn thiếu.

Điều kiện đạt: mô phỏng mất kết nối, lỗi trước gửi và mất kết nối sau gửi đều không nhân đôi yêu cầu hay đổi tài khoản lấy kết quả. Một lô Flow thật chứng minh tiếp tục được sau lỗi.

**5. Xuất video có tiến độ thật và cơ chế phát hiện kẹt**

- Giữ giới hạn mức đồng thời theo máy Colab thật; giữ wrapper Headless EGL, đồng bộ ảnh và cấu hình NVENC theo quy định dự án.
- Ghi riêng các mốc: cấp máy, chuẩn bị môi trường, tải dữ liệu, chuẩn bị cảnh, dựng frame, mã hóa, tải kết quả.
- Truyền số frame hoàn tất và thời điểm tiến triển gần nhất ra bộ điều phối. Nhịp báo sống của bộ điều khiển không thay cho tiến độ dựng hình.
- Dùng khoảng phát hiện không tiến triển theo tác vụ và dữ liệu đo, tách khỏi hạn tổng. Không tự hủy tác vụ vẫn đang tiến triển chỉ vì video dài.
- Khi mất kết nối: kiểm tra tiến trình và đầu ra từ xa trước khi dựng lại. Chỉ xử lý tiến trình mồ côi thuộc lượt chạy đang phục hồi.
- Chỉ giải phóng tài nguyên sau khi nhận đủ đầu ra bền vững và kiểm tra MP4 bằng ffprobe.

Điều kiện đạt: thử trên T4 thật, có tiến độ frame quan sát được, có MP4/SRT và số đo luồng hình/âm thanh; phục hồi kết nối không dựng trùng.

**6. Tối ưu thứ tự sau khi đã chạy đúng**

- Auto có thể chạy âm thanh và ảnh độc lập song song sau khi khóa kịch bản, nếu việc tạo ảnh không cần kết quả âm thanh. Timeline và nhịp hình cuối cùng dựa trên WAV đo thật.
- Review vẫn giữ các điểm dừng outline/dialogue/audio/images/video đã quy định.
- Chuẩn bị tài nguyên vừa đủ, tận dụng môi trường còn hợp lệ trong lượt chạy và không để máy nghỉ tiêu hao sau khi hoàn tất.
- Báo riêng thời gian xử lý, chuẩn bị, truyền dữ liệu và phục hồi. Đặt mục tiêu hiệu năng từ bài thử cùng dữ liệu và quy mô; không hứa một thời gian cố định cho mọi video.

**7. Cách kiểm tra và tiêu chí bàn giao**

| Lớp kiểm tra | Bằng chứng cần có |
|---|---|
| So sánh module riêng/core | Cùng đầu vào; đường gọi và yêu cầu gửi đi tương đương; bảo toàn phiên bản 1.7.0 và chuẩn ảnh |
| Kiểm tra đường nối | Đủ tệp Colab; nhiều T4 thực sự được sử dụng khi phù hợp; quyền sở hữu không sai; kết quả cũ không bị nhận nhầm |
| Kiểm tra phục hồi | Không gửi trùng; giữ tài sản hợp lệ; lỗi hiện rõ; không thu hồi phiên còn việc |
| Lượt thật quy mô nhỏ | Flow và T4 thật; đủ loại cảnh, ảnh gốc/biến thể; WAV, MP4, SRT đã kiểm tra |
| Lượt đầy đủ | Một job kiểm chứng mới cùng quy mô bài lỗi; không ghi đè job cũ; có thời gian từng khâu và hình ảnh đúng chuẩn |
| Cả hai định dạng | Kiểm tra đường sản xuất long_16x9 và short_9x16; thời lượng động; voice/subtitle đúng hợp đồng |
| Quy trình phần mềm | Đủ sáu trạm của dự án, cập nhật bài học lỗi và bằng chứng CI đúng phiên bản thay đổi |

Chỉ đánh dấu lỗi đã khắc phục khi có bằng chứng kiểm tra đúng lỗi đó. Hoàn thành một bước kỹ thuật, hoàn thành toàn video và phù hợp thẩm mỹ phải được báo riêng.

**Thứ tự triển khai:** giữ chuẩn ảnh và đầu vào → thống nhất đường gọi → sửa truyền dữ liệu/quản lý phiên/phục hồi → kiểm chứng render → chạy toàn trình → tối ưu thêm phần độc lập có thể chạy song song.
