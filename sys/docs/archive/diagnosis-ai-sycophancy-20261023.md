# Chẩn đoán lần chạy video ngày 23/10/2026

**Cập nhật sau mốc khảo sát:** MP4 được thu về lúc 23:00:02, ffprobe xác nhận 1080×1920, H.264/AAC, 190,12 giây. Người dùng xác nhận content/core chưa được kiểm duyệt; nhãn chấp nhận kỹ thuật trong DB không phải phê duyệt của người dùng. Xem [kiểm tra từng nhánh và kế hoạch chi tiết](module-merge-audit-20261023/PLAN.md) để biết kết luận cập nhật. Các số liệu bên dưới giữ nguyên mốc khảo sát 22:56.

Mốc kiểm tra: **22:56:11, giờ Việt Nam**. Job: `ai-sycophancy-9x16`. Nhánh chạy: `module-core`, commit `54694e0`. Đây là báo cáo khảo sát; không sửa mã nguồn, trạng thái job hay can thiệp phiên đang chạy.

**Kết quả chính:** thời gian bị kéo dài bởi lỗi tại các điểm nối giữa module, nhiều lần dừng/chạy lại và một phần khả năng chạy song song chưa được luồng tổng sử dụng. Ảnh khác mẫu có cả nguyên nhân từ nội dung yêu cầu mới và thay đổi hành vi trong bản tích hợp. Chưa có bằng chứng toàn bộ luồng đã được sửa xong.

**Thời gian từng khâu**

| Khâu | Mốc trong nhật ký | Thời gian trôi qua | Diễn giải |
|---|---|---:|---|
| Nhận và kiểm tra nội dung có sẵn | 20:47:03–20:47:06 | Khoảng 3 giây | Không bao gồm thời gian tác giả soạn nội dung trước khi tạo job. |
| Âm thanh | 20:49:27–21:07:27 | Khoảng 18 phút | 4 lượt thực thi, 3 lần bị chặn. |
| Hình ảnh | 21:08:33–21:45:58 | Khoảng 37 phút 25 giây | 14 lượt thực thi: một lượt thành công lấy ảnh nhân vật tham chiếu, một lượt hoàn thành ảnh cảnh, 12 lượt bị chặn. Không phải 14 lần tạo mới toàn bộ ảnh. |
| Xuất video | 21:46:53–22:56:11 | Khoảng 69 phút 18 giây | 3 lượt thực thi được ghi nhận; lượt mới nhất bắt đầu 22:44:09. Chưa có MP4 được thu về. |

Từ khi tạo job đến mốc kiểm tra: **khoảng 2 giờ 9 phút**. Âm thanh đầu ra dài **190,05 giây**, tương đương khoảng 3 phút 10 giây; kịch bản có 12 cảnh và 97 ảnh cảnh.

Các khoảng trên là thời gian đồng hồ, bao gồm khởi tạo, xử lý, lỗi, điều tra/phục hồi và chạy lại. Không được hiểu thành thời gian GPU liên tục làm việc.

**1. Âm thanh: thiếu tệp khi chuyển sang máy Colab**

- Lịch sử tài khoản Colab `account-16` ghi `FileNotFoundError` với `media_packaging.py` lúc **20:54:04** và **21:01:15**.
- Hai yêu cầu cũ `393259fd6d...` và `799c780a26...` chỉ khai báo `subtitles.py` trong danh sách tệp hỗ trợ. Máy từ xa chạy worker mới nhưng không nhận đủ tệp worker cần.
- Lượt kế tiếp còn gặp khóa yêu cầu trước đang chờ thu kết quả (`COLAB_PENDING_OTHER_REQUEST`).
- Yêu cầu cuối `fcf5c3a89c...` đã khai báo đủ `audio_processing.py`, `subtitles.py`, `media_packaging.py`; cache ghi `complete`, đầu ra được nhận lúc **21:07:27**.
- Báo cáo TTS cuối ghi `elapsed_seconds = 221.6058`, khoảng **3 phút 42 giây** cho phần xử lý được báo cáo, ngắn hơn nhiều so với 18 phút của cả khâu. Báo cáo này không bao gồm mọi thời gian khởi tạo/trao đổi/phục hồi.

**Trạng thái:** lỗi thiếu tệp có bằng chứng đã khắc phục và âm thanh đã thu về thành công trong lượt này.

**2. Khả năng chia TTS cho nhiều máy chưa được nối vào đường chạy đang dùng**

- `sys/adapters.py:741` đưa job có hợp đồng đầu ra tới `remote_audio.produce`.
- `sys/remote_audio.py:119` tạo một yêu cầu chứa toàn bộ cảnh; dòng 125 gọi một `Client.synthesize`.
- `sys/remote_audio.py:195` có `produce_parallel`, chia cảnh cho nhiều Colab T4, nhưng đường gọi trên không sử dụng hàm đó.
- Dữ liệu thực tế phù hợp với mã: 63 đoạn lời đọc được gửi vào một yêu cầu trên `account-16`; báo cáo có 16 lô, mỗi lô tối đa 4 đoạn. Gom lô trên một máy không đồng nghĩa chia việc cho nhiều máy.

**Trạng thái:** trong core tại mốc kiểm tra, khả năng chạy nhiều máy của module riêng chưa được sử dụng bởi đường sản xuất này. Đây là một khác biệt tích hợp, không phải nguyên nhân duy nhất của 18 phút.

**3. Hình ảnh: kẹt ở nhận diện phiên/tài khoản và kết nối, phải khởi chạy lại nhiều lần**

Nhật ký ghi các nhóm lỗi:

- 21:08:36: yêu cầu đã tồn tại, phải thu/đối soát thay vì gửi lại (`FLOW_BUDGET`).
- 21:11:50: quy định có nhân vật không khớp ảnh nhận dạng (`FLOW_ENTITY_POLICY_INVALID`).
- 21:14:32: worker không báo đúng dự án Flow đang hoạt động (`FLOW_PROJECT_MISMATCH`).
- 21:21:20 và 21:33:25: kết nối HTTP bị hỏng/đóng.
- 21:24:40, 21:26:49, 21:28:51: nhận sai tài khoản hoặc cố thay chủ sở hữu của yêu cầu đang được ghim (`FLOW_OWNER_MISMATCH`, `Pinned request ownership cannot be changed`).
- 21:30:29: nhà cung cấp từ chối một yêu cầu (`PUBLIC_ERROR_UNSAFE_GENERATION`); nhật ký không chứng minh cụ thể từ/ngữ cảnh nào gây từ chối.
- 21:36:45, 21:40:43, 21:42:27: không nối được trình duyệt (`CDP_TRANSPORT_CLOSED`, `Connection refused`).

Tổng khoảng cách từ từng lần báo lỗi ảnh đến lần bắt đầu thực thi tiếp theo là **23,92 phút**. Khoảng này có thể chứa xử lý phục hồi hoặc công việc còn đang chạy; không thể quy toàn bộ thành thời gian chờ trống.

Bản tích hợp đã bổ sung nối lại trình duyệt, đối chiếu đầy đủ đường dẫn profile và phục hồi tài khoản của yêu cầu. Lượt 14 đã hoàn thành 97 ảnh cảnh. Nhãn `issue_resolved` được ghi khi một lượt của module qua kiểm tra kỹ thuật; bản thân nhãn này không chứng minh lỗi hết tái diễn hoặc ảnh đúng thẩm mỹ.

Mốc tham khảo từ nhánh ảnh: test 10 ảnh mất 113,21 giây; 30 ảnh mất 203,3 giây; 60 ảnh mất 263,2 giây; 90 ảnh mất 373,43 giây, đều không ghi ảnh thất bại. Bộ dữ liệu thử và video thực tế khác nhau nên đây không phải cam kết thời gian cho 97 ảnh của job này.

**Trạng thái:** lượt này đã vượt qua khâu ảnh; chưa có lượt chạy toàn trình sạch sau sửa để chứng minh ổn định lâu dài.

**4. Xuất video: cấu hình vượt giới hạn máy, sau đó phiên bị dừng và cấp lại**

- 21:49:00: render thất bại; lần chẩn đoán 21:54:59 ghi rõ `Maximum for --concurrency is 2 (number of cores on this system)`.
- Bản trước truyền mức đồng thời 6 cho Remotion trên máy chỉ chấp nhận 2. T4 là GPU; giới hạn này đến từ số lõi CPU của máy Colab.
- `sys/renderer/render.mjs:300` hiện kẹp mức đồng thời theo số lõi máy; thay đổi đã nằm trong commit `54694e0` lúc **22:15:35**. Hồ sơ `failed-render-1792767475071835192.json` cũng ghi nguyên nhân và lần render cũ không có MP4/tiến trình còn chạy.
- Lượt tiếp theo bắt đầu **21:58:49**. Lịch sử tài khoản ghi phiên bị chấm dứt lúc **22:33:42**; quan sát chính thức lúc **22:41:08** xác nhận không có phiên máy chủ; một T4 mới được cấp lúc **22:41:46**.
- Không đủ bằng chứng để quy việc chấm dứt phiên cho Google, người dùng hay một tiến trình quản lý cụ thể.
- Lượt render thứ ba bắt đầu **22:44:09**. Đến **22:56:11**, DB ghi `running`, yêu cầu ghi `submitted`, nhưng chưa có `render-result.json`/MP4 được thu về. Trạng thái này chưa chứng minh được tốc độ tiến triển bên trong máy từ xa.
- Đường gọi hiện chờ kết quả từ xa với hạn 5.400 giây; tiến trình render bên trong có hạn 3.600 giây. Hạn dài không phải bằng chứng cần chừng ấy thời gian, nhưng có thể khiến lỗi hoặc kết nối bị kẹt chậm lộ ra ở bên ngoài. Đây là rủi ro quan sát thấy từ mã, chưa được khẳng định là nguyên nhân trực tiếp của mọi phút ở lượt hai.

**Trạng thái:** lỗi cấu hình 6/2 đã sửa trong mã; chưa có video hoàn tất để xác nhận sửa xong toàn bộ khâu và hết chậm.

**5. Vì sao ảnh khác mẫu đã duyệt**

Đã mở trực tiếp ảnh thử ở `vp-agent-images/sys/runs/test-300-images` và ảnh sản xuất trong `revisions/images/14`.

- Bộ quy tắc chung `sys/flow_prompts/` và `sys/visual_style.py` tại `module-images` và core không có khác biệt Git trong lần đối chiếu. Vì vậy không có căn cứ nói toàn bộ bộ tạo ảnh chuẩn đã bị thay thế.
- **Đầu vào khác:** ảnh thử `batch_1/SC001` yêu cầu nền trắng tuyệt đối, khối màu phẳng, không đổ bóng/gradient/gạch nét. Ảnh video `SC01_I1` yêu cầu máy tính bảng, cà phê đá, quán cà phê Sài Gòn và đèn treo ánh sáng ấm. Ảnh thực tế có nền be/vàng, căn phòng và bóng đổ. Như vậy chính yêu cầu cảnh đang đẩy kết quả sang hướng khác mẫu trắng tối giản.
- **Quy tắc ghép ảnh khác:** core giới hạn hai ảnh biến thể liên tiếp rồi chuyển thành cảnh mới (`research_story_architect.py:1212`), thay ảnh gốc mỗi lần gặp `full_scene` (dòng 1240), đồng thời giới hạn số lần giữ cảnh gốc trong `scripts/visual_quality.py`. Các thay đổi này có thể làm bố cục/nhân vật thiếu liền mạch so với nhánh ảnh. Chưa đủ bằng chứng quy mọi ảnh sai trong job này riêng cho từng quy tắc.
- **Yêu cầu bị sửa khi thử lại:** `cdp_direct_client.py:750` tự thêm câu `Clean educational 2D diagram illustration` vào prompt sau lần đầu. Cơ chế này không có trong bản module-images đã chốt. Chưa có bằng chứng xác định chính xác ảnh nào trong bộ 97 ảnh đã đi qua nhánh thử lại này.
- **Thiếu khóa mẫu hình:** yêu cầu đã lưu của `SC01_I1` có danh sách tham chiếu trống. Bộ ảnh đẹp trong thư mục test không tự trở thành mẫu hình ảnh được đính kèm cho job mới. Ảnh nhân vật tham chiếu có mục đích khác với ảnh mẫu phong cách.
- **Kiểm tra kỹ thuật khác duyệt chất lượng:** các lần chấp nhận ảnh ghi rõ `Technical output accepted, no quality approval`. Không có chứng cứ người dùng đã duyệt bộ ảnh mới này.

**Trạng thái sửa ảnh:** thư mục `/home/hongphuoc6104/Desktop/vp-agent-images` đang ở nhánh `fix/core-image-parity`, có thay đổi chưa commit để bỏ giới hạn biến thể/reset ảnh gốc, bỏ sửa prompt khi thử lại và bổ sung kiểm tra đối chiếu. Những thay đổi đó chưa nằm trong `module-core` tại mốc kiểm tra. Chưa có ảnh mới sau sửa và chưa có đối chiếu hình ảnh toàn trình để xác nhận đúng ý người dùng.

**Ưu tiên xử lý tiếp theo**

1. Chốt lại bộ ảnh đã được người dùng duyệt làm chuẩn; đối chiếu cùng đầu vào qua module riêng và core, bao gồm yêu cầu thực sự gửi đi, ảnh mẫu đính kèm, bố cục, nhân vật và màu sắc. Không tự đổi yêu cầu đã chốt khi thử lại.
2. Hoàn thiện đường gọi chung: chuyển đầy đủ tệp sang Colab, bảo toàn tài khoản/phiên của từng yêu cầu, dùng đúng khả năng chia việc đã kiểm chứng ở module riêng.
3. Theo dõi tiến độ render thực và báo sớm nếu phiên chết/không tiến triển; chỉ công nhận khâu video hoàn tất sau khi nhận MP4 và kiểm tra đầu ra.
4. Chạy lại cùng một đầu vào từ đầu đến cuối, có mốc thời gian từng khâu và không cần can thiệp phục hồi, trước khi tuyên bố bản tích hợp ổn định.

**Nguồn bằng chứng chính**

- `sys/.state/jobs.sqlite`, bảng `events` và `modules`, được mở chỉ đọc.
- `sys/runs/ai-sycophancy-9x16/revisions/`, `cache/colab-tts/`, `cache/colab-render/`, `flow/attempts/`, `workflow.json`.
- `~/.config/video-pilot/colab/profiles/account-16/history/video-pilot-tts.jsonl` và `account-18/history/video-pilot-tts.jsonl`: chỉ đọc thời gian, lỗi và kết quả thao tác liên quan.
- `sys/.state/colab-observations/server-runtime-absent-1792770068241829055.json`.
- Ảnh, chỉ dẫn và `batch_report.json` trong `/home/hongphuoc6104/Desktop/vp-agent-images/sys/runs/test-300-images/`.
- Đối chiếu Git giữa `module-core`, `module-images`, `module-audio`, `module-video` và các thay đổi đang có trong thư mục nhánh ảnh.
