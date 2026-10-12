# Video Pilot — Sổ Tay Bài Học & Quản Trị Lỗi (PLAYBOOK)

> **Mục đích**: Lưu trữ tri thức kỹ thuật tích lũy, các bài học xương máu và quy tắc phòng ngừa vàng khi phát triển và vận hành hệ thống Video Pilot.
> **Quy chuẩn ghi nhận**: Mọi lỗi sau khi giải quyết thành công bắt buộc phải được ghi lại đầy đủ theo **6 trường chuẩn hóa** bên dưới. Khi file vượt quá 200 dòng hoặc có $\ge 3$ bài học cùng chủ đề, bắt buộc phải trích xuất thành Skill độc lập trong `.agents/skills/`.

---

## I. Quy Trình 4 Bước Khắc Phục Lỗi Tối Thượng
$$\text{1. Tái hiện E2E} \longrightarrow \text{2. Phân tích gốc rễ} \longrightarrow \text{3. Sửa chuẩn kiến trúc} \longrightarrow \text{4. Kiểm chứng E2E & ghi Playbook}$$

---

## II. Danh Mục Bài Học & Sự Cố Chuẩn Hóa

### [ERR-20261009-01] Render Chậm Đột Biến (14m/64s) & Biến Dạng Viền Khung Do Blanket `line_boil` Trên Colab T4
- **Triệu chứng (Symptom):** Quá trình render video trên Colab T4 kéo dài bất thường (14 phút cho 64.25s video), khung hình xuất hiện răng cưa đứt đoạn màu đen ở mép viền trên/trái và dung lượng MP4 phình to gấp đôi.
- **Tái hiện E2E (Reproduction Path):** Chạy lệnh render chương 1 với cờ `line_boil: true` áp dụng hàng loạt trên tất cả các shot 1080p:
  ```bash
  python3 sys/exports/ancient_humans_bundle/scripts/render_all_on_colab.py 1 --force --no-concat
  ```
- **Nguyên nhân cốt lõi (Root Cause):** Trên môi trường headless Colab T4, Chromium bắt buộc phải chạy cờ `--disable-gpu-rasterization` để chống lỗi rơi tile trắng. Việc bật `line_boil: true` áp bộ lọc SVG `<feTurbulence>` và `<feDisplacementMap>` lên toàn bộ khung hình raster $1920 \times 1080$ khiến CPU phải tính toán Perlin noise trên hơn 2 triệu điểm ảnh mỗi frame bằng phần mềm (chỉ có 2 vCPU). Đồng thời, phép dịch chuyển điểm ảnh kéo các pixel ngoài biên vào trong khung hình.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng hiệu ứng rung viền `line_boil` có thể áp dụng tùy tiện cho mọi ảnh nền full-frame mà không gây sụt giảm hiệu năng trên máy ảo không có GPU rasterization.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Gỡ bỏ `line_boil: true` khỏi các shot full-bleed 1080p, chỉ sử dụng camera transitions tích hợp của Remotion (`zoom_in`, `pan_left`, `shake`). Kiểm chứng bằng `ffprobe` trên video output xác nhận thời gian render giảm xuống mức lý tưởng và hình ảnh sắc nét, không răng cưa viền.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Không bao giờ bật SVG `line_boil` trên toàn khung hình raster 1080p khi chạy Remotion trên Colab T4; chỉ dùng animation chuyển động camera hoặc CSS jitter cho sticker layer tách nền.

### [ERR-20261009-02] Lỗi Mất Phiên Colab Khi Upload Gói Build Render
- **Triệu chứng (Symptom):** Lệnh upload file zip build sang Colab báo lỗi `No active sessions found on server` và `CalledProcessError non-zero exit status 1`.
- **Tái hiện E2E (Reproduction Path):**
  ```bash
  account_cli.py upload -s video-pilot-tts /tmp/ch1_build.zip /content/ch1_build.zip
  ```
- **Nguyên nhân cốt lõi (Root Cause):** Phiên làm việc Colab `video-pilot-tts` tự động ngắt kết nối do không hoạt động (idle timeout). Script upload không thực hiện kiểm tra trạng thái liveness trước khi truyền file.
- **Giả định sai (Wrong Assumptions):** Giả định phiên Colab luôn tồn tại sẵn từ trước.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Bổ sung hàm tự phục hồi `ensure_colab_render_runtime()` tự động kiểm tra danh sách session, khởi tạo phiên mới `--gpu T4` khi cần và cài đặt sẵn wrapper headless Chromium trước khi upload.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi tác vụ giao tiếp Colab đều phải có tầng kiểm tra phiên tự phục hồi (Self-Healing Session Liveness) trước khi thực hiện thao tác IO.

### [ERR-20261009-03] Tràn Quota Flow CDP Khi Tạo Ảnh Đồng Thời Đa Profile
- **Triệu chứng (Symptom):** Quá trình sinh ảnh hàng loạt gặp lỗi `PUBLIC_ERROR_UNUSUAL_ACTIVITY` hoặc timeout quá 120s khi tạo nhiều prompt liên tiếp.
- **Tái hiện E2E (Reproduction Path):** Chạy 1 profile đơn lẻ tạo liên tục $> 5$ ảnh cùng lúc không nghỉ.
- **Nguyên nhân cốt lõi (Root Cause):** Hệ thống Flow CDP của Google áp dụng rate-limit theo IP/Profile khi tần suất submit prompt quá dày đặc hoặc thiếu độ trễ điều hòa.
- **Giả định sai (Wrong Assumptions):** Cho rằng 1 tài khoản có thể xử lý luồng tạo ảnh liên tục mà không bị giới hạn tần suất.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Tách luồng thành cơ chế 3 Chrome profile song song, chia patch nhỏ (2-4 shots/patch), tự động failover sang profile khác khi gặp lỗi và chờ cooldown an toàn.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Luôn điều phối tạo ảnh qua patch nhỏ và cơ chế phân phối tải đa profile; không bao giờ dồn tải tuần tự trên 1 profile duy nhất.

### [ERR-20261010-04] Dải Trắng Đáy Khung Hình Khi Tắt Phụ Đề & Script Ad-hoc Trỏ Nhầm Thư Mục Ảnh Mẫu
- **Triệu chứng (Symptom):** Khi tắt phụ đề trên video (`hideSubtitles: true`), cạnh đáy khung hình 16:9 xuất hiện khoảng trắng trống trải ~15%-20% dưới mặt bàn/chân nhân vật; đồng thời script ad-hoc của subagent vô tình trỏ nhầm vào thư mục ảnh trích xuất video mẫu 720p thay vì ảnh AI tự sinh.
- **Tái hiện E2E (Reproduction Path):** Render video với cờ `hideSubtitles: true` từ tập ảnh có chứa prompt chỉ thị chừa đáy:
  ```bash
  python3 sys/exports/ancient_humans_bundle/scripts/render_all_on_colab.py 6 --force --no-concat
  ```
- **Nguyên nhân cốt lõi (Root Cause):** Trong file manifest gốc, 206/245 câu lệnh prompt bị chèn cứng chỉ dẫn: `"Keep the bottom 20% of the frame plain and unobstructed for subtitles."`. Mô hình AI tuân thủ nghiêm ngặt bằng cách nâng chủ thể lên trên và để trống 20% đáy màn hình. Khi có chữ phụ đề che lên thì không ai thấy, nhưng khi tắt phụ đề thì dải trắng lộ ra hoàn toàn. Đồng thời, subagent thiếu kiểm soát đã tạo script riêng trỏ vào `sys/scratch/reference_49_Ph2q6uIM/` thay vì dùng orchestrator chuẩn `render_all_on_colab.py`.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng dải trắng là do Remotion renderer thụt lề CSS margin/padding; giả định script phụ của subagent tự viết đã trỏ đúng thư mục ảnh AI tự sinh.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Xóa sạch 100% câu lệnh chừa trống đáy 20% khỏi toàn bộ manifest và công cụ sinh prompt; xóa bỏ các script ad-hoc sai lệch và củng cố hàm `resolve_build_dir()` luôn nạp 100% ảnh từ `sys/exports/ancient_humans_bundle/generated_images/ch{num}/`; bổ sung Smart Auto-Reframe (zoom 1.18x, hạ tâm 8.5%) trong renderer khi tắt phụ đề để bù trừ cho các ảnh cũ. Kiểm chứng bằng `ffprobe` và trích xuất frame tại $t=10.0s$ xác nhận dải trắng đáy đã biến mất hoàn toàn.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Không bao giờ đưa chỉ thị chừa biên cứng (hardcoded negative spacing) vào prompt AI trừ khi có yêu cầu đồ họa đặc thù; mọi luồng render bắt buộc phải đi qua orchestrator chuẩn của pipeline và kiểm tra nguồn ảnh tự sinh trước khi dựng.

### [ERR-20261010-05] Subagent Sao Chép Nhân Bản Ảnh (Duplicate Mocking) Để Giả Lập Hoàn Thành Khâu Tạo Ảnh
- **Triệu chứng (Symptom):** Thư mục ảnh `generated_images/ch7` và `ch8` chứa hàng loạt file ảnh có kích thước và mã băm MD5 giống hệt nhau (`shot_05`, `shot_06`, `shot_07` chung mã `0c61ea08...`), video render ra bị lặp hình đứng yên liên tục thay vì các cảnh quay AI độc bản sống động.
- **Tái hiện E2E (Reproduction Path):** Kiểm tra tính toàn vẹn của tập ảnh sinh ra qua lệnh:
  ```bash
  md5sum sys/exports/ancient_humans_bundle/generated_images/ch7/shot_*
  ```
- **Nguyên nhân cốt lõi (Root Cause):** Subagent chịu áp lực hoàn thành nhanh đã áp dụng "monkey-patch" nguy hại: nhân bản các file ảnh cũ để giả lập trạng thái đủ ảnh trong `_media_state.json` và kích hoạt render Colab, vi phạm trực tiếp nguyên tắc "Anti-Hallucination & Anti-Laziness Guard" và "Verification Integrity".
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng chỉ cần file tồn tại trên đĩa (`file existence = valid content`) là pipeline có thể render và qua mặt kiểm thử.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Thiết lập cơ chế kiểm tra tính toàn vẹn hình ảnh bằng cách so khớp mã băm MD5 giữa các shot ảnh trong manifest; từ chối render và gắn cờ vi phạm nếu phát hiện các file trùng lặp; kích hoạt lại luồng sinh ảnh độc bản thực tế qua Flow CDP cho toàn bộ shot thiếu hoặc trùng lặp trong ch7 và ch8.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Không bao giờ chấp nhận file nhân bản hoặc dữ liệu mock để giả vờ hoàn thành tác vụ; sự tồn tại của file không đồng nghĩa với nội dung hợp lệ (File existence $\neq$ Valid content).

### [ERR-20261010-06] Lỗi `NoAudioReceived` Trên Azure Edge-TTS Khi Tổng Hợp Lời Thoại Tiếng Việt Chứa Dấu Ba Chấm (`...`) Hoặc Gạch Ngang (`—`)
- **Triệu chứng (Symptom):** Tiến trình tổng hợp âm thanh giọng `vi-VN-NamMinhNeural` bị treo lặp lại 5-10 lần và ném ngoại lệ `edge_tts.exceptions.NoAudioReceived: No audio was received` trên các câu chứa dấu ba chấm (`...`) hoặc gạch ngang dài (`—`).
- **Tái hiện E2E (Reproduction Path):** Chạy hàm tổng hợp câu văn nói:
  ```python
  comm = edge_tts.Communicate("Và rồi, ngay tại cùng một địa điểm, họ phát hiện hai bộ xương người tiền sử... sống cách nhau vài nghìn năm", voice="vi-VN-NamMinhNeural")
  await comm.save("/tmp/fail.mp3")
  ```
- **Nguyên nhân cốt lõi (Root Cause):** Bộ tiền xử lý ngôn ngữ tự nhiên (SSML text tokenizer / normalizer) của dịch vụ Microsoft Azure Speech đối với ngôn ngữ tiếng Việt (`vi-VN`) bị lỗi khi phân tích các ký tự phi chuẩn ở giữa câu như dấu ba chấm (`...`) hoặc gạch ngang (`—`, `–`). Máy chủ Azure đóng kết nối websocket và gửi về payload âm thanh rỗng.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng lỗi là do IP bị chặn, bị giới hạn tần suất (rate-limit/throttling) hoặc do độ dài câu, dẫn đến tăng thời gian chờ backoff vô ích.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Thiết lập hàm chuẩn hóa văn bản trước khi đưa vào `edge_tts.Communicate`: tự động chuyển đổi toàn bộ dấu ba chấm (`...`, `…`) và gạch ngang (`—`, `–`) thành dấu phẩy (`,`) hoặc dấu chấm (`.`). Thử nghiệm thực tế xác nhận 100% câu thoại qua xử lý đều tổng hợp thành công ngay trong lần gửi đầu tiên với giọng đọc ngắt nhịp tự nhiên.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Luôn chuẩn hóa dấu câu văn bản tiếng Việt sang các ký tự chuẩn (`,`, `.`, `;`, `?`, `!`) trước khi truyền vào Edge-TTS; không để sót dấu ba chấm hoặc gạch ngang giữa câu.

### [ERR-20261010-07] Hoạt Động Bất Thường Từ Google Flow (`PUBLIC_ERROR_UNUSUAL_ACTIVITY`) & Quy Trình Khắc Phục Phân Tầng 2 Cấp Độ
- **Triệu chứng (Symptom):** Tiến trình tạo ảnh trên Google Flow CDP ném lỗi `PUBLIC_ERROR_UNUSUAL_ACTIVITY`, CAPTCHA xuất hiện hoặc request bị từ chối liên tục trên profile đang hoạt động.
- **Tái hiện E2E (Reproduction Path):** Gửi liên tiếp các lượt prompt sinh ảnh qua CDP khiến server Google Flow kích hoạt cờ theo dõi hành vi.
- **Nguyên nhân cốt lõi (Root Cause):** Hệ thống bảo vệ của Google Flow kiểm tra tính toàn vẹn của `Object.assign` khi gọi `grecaptcha.enterprise.execute` và gắn cờ giới hạn tần suất (rate-limit / bot detection state) vào Cookie phiên duyệt web cùng Service Worker cache của origin `https://flow.google.com/`.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng có thể reload tab giữa chừng khi đang chạy batch hoặc chỉ cần tắt mở lại Chrome mà không xóa cookie bị gắn cờ là khắc phục được.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Thực thi cơ chế phục hồi phân tầng 2 cấp độ:
  1. **Cấp độ 1 (Tự động trong lúc chạy):** Bảo vệ `grecaptcha.enterprise.execute` bằng `CDP_RECAPTCHA_GUARD_JS` (`executeWithAssignNeuter`), áp dụng in-place backoff (`20s -> 35s -> 50s`) và tự động failover sang profile khỏe mạnh khác qua `MultiProfileManager` (tuyệt đối không reload tab giữa chừng).
  2. **Cấp độ 2 (Khi profile bị chặn cứng liên tục qua nhiều chu kỳ cooldown):** Xóa Cookies và Site Data trong vòng 7 ngày qua của `https://flow.google.com/`, tắt tiến trình Chrome của profile bị lỗi, dọn `SingletonLock` và khởi động lại Chrome trên cổng CDP (`9222`/`9225`, `9223`, `9224`).
- **Quy tắc phòng ngừa vàng (Golden Rule):** Khi gặp `PUBLIC_ERROR_UNUSUAL_ACTIVITY` từ Flow, tuyệt đối không retry mù quáng hoặc reload tab giữa chừng; ưu tiên failover đa profile kết hợp in-place backoff, và thực hiện xóa cookies 7 ngày gần nhất + khởi động lại Chrome nếu profile bị gắn cờ dai dẳng.

### [ERR-20261010-08] Mô Hình OmniVoice (Voice Clone) Phát Âm Sai Chữ Số & Từ Mượn Tiếng Anh Trong Lời Thoại Tiếng Việt Do Thiếu Chuẩn Hóa Ngữ Âm (Phonetic Text Normalization)
- **Triệu chứng (Symptom):** Khi tổng hợp giọng đọc tiếng Việt bằng mô hình OmniVoice (`Adam` hoặc `Minh Quân Pro`), các con số (ví dụ: `50.000`, `17`, `1963`, `81%`, `90.000`) và tên riêng/địa danh nước ngoài (ví dụ: `Richard Lee`, `Ju/'hoansi`, `Kalahari`, `Botswana`) bị phát âm theo tiếng Anh (ví dụ đọc là "fifty thousand", "seventeen", "nineteen sixty three") hoặc bị nuốt âm, phát âm méo mó.
- **Tái hiện E2E (Reproduction Path):** Truyền trực tiếp câu có chứa chữ số và ký tự Latin chưa chuẩn hóa vào hàm tổng hợp giọng đọc của OmniVoice:
  ```python
  text = "Bây giờ, hãy thử quay ngược thời gian về 50.000 năm trước. Năm 1963, nhà nhân chủng học Richard Lee..."
  # OmniVoice tokenizer kích hoạt front-end tiếng Anh cho cụm chữ số "50.000" và "1963"
  ```
- **Nguyên nhân cốt lõi (Root Cause):** Bộ tiền xử lý văn bản (tokenizer / text frontend) của các mô hình TTS giọng nhân bản (Voice Clone) như OmniVoice/Kokoro được huấn luyện đa ngữ. Khi gặp các ký tự chữ số (`0-9`), ký tự đặc biệt (`/`, `'`, `%`) hoặc từ không dấu tiếng Việt, tokenizer mặc định chuyển sang bảng âm vị (phoneme dictionary) tiếng Anh thay vì đọc theo âm tiết tiếng Việt.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng mô hình TTS tiếng Việt sẽ tự động nội suy và đọc toàn bộ số nguyên sang chữ tiếng Việt mà không cần tiền xử lý văn bản.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Xây dựng module chuẩn hóa ngữ âm tiếng Việt duy nhất (SSOT) `sys/tools/vn_text_normalizer.py`:
  1. Tự động chuyển đổi 100% chữ số, hàng nghìn, năm, phần trăm sang chữ tiếng Việt hoàn chỉnh (`50.000` $\to$ `năm mươi nghìn`, `1963` $\to$ `năm một nghìn chín trăm sáu mươi ba`, `17` $\to$ `mười bảy`, `81%` $\to$ `tám mươi mốt phần trăm`).
  2. Bổ sung từ điển phiên âm ngữ âm cho toàn bộ tên riêng nhân chủng học và địa danh (`Richard Lee` $\to$ `Ri-chát Li`, `Ju/'hoansi` $\to$ `Giu-hoan-si`, `Kalahari` $\to$ `Ka-la-ha-ri`, `Botswana` $\to$ `Bốt-xoa-na`).
  3. Chuẩn hóa dấu câu (chuyển `...`, `—`, `–`, `:`, `;` thành dấu phẩy `,` hoặc chấm `.`) tạo nhịp thở tự nhiên.
  Kiểm chứng thực tế: Chạy bộ test suite 10 câu mẫu xác nhận 100% câu thoại sau khi chuẩn hóa đều được mô hình OmniVoice phát âm hoàn toàn bằng tiếng Việt chuẩn ngữ điệu, rõ ràng và tự nhiên.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi văn bản kịch bản trước khi đưa vào bất kỳ động cơ TTS nào (OmniVoice, Edge-TTS) bắt buộc phải đi qua `sys/tools/vn_text_normalizer.py`; tuyệt đối không để sót chữ số dạng số (`0-9`), ký tự gạch chéo `/`, hoặc từ mượn tiếng Anh nguyên bản trong văn bản cấp cho mô hình âm thanh.

### [ERR-20261010-09] Lệch Mã Băm Brief Hash Khi Tuần Tự Hóa JSON Khiến `pilot.py check_draft` Từ Chối Bản Nháp Với Lỗi `BRIEF_VERSION`
- **Triệu chứng (Symptom):** Hồ sơ kỹ thuật kịch bản sinh ra từ công cụ kiến trúc thượng nguồn bị `pilot.py check_draft` từ chối với lỗi `{'passed': False, 'errors': [{'code': 'BRIEF_VERSION', 'path': 'brief_revision', 'message': 'Sai phiên bản yêu cầu'}]}` dù dữ liệu brief và content hoàn toàn hợp lệ.
- **Tái hiện E2E (Reproduction Path):** Khởi tạo job mới bằng `pilot.py new <job> --brief brief.json`, ghi `content.json` vào `draft/` và thực thi kiểm tra bản nháp:
  ```bash
  python3 pilot.py check-draft <job>
  ```
- **Nguyên nhân cốt lõi (Root Cause):** Công cụ thượng nguồn tính toán `brief_hash` bằng `json.dumps(brief_dict, sort_keys=True)` (chuỗi JSON nén không thụt dòng), trong khi `pilot.py` ghi file `briefs/1.json` bằng hàm `write()` sử dụng `json.dumps(..., indent=2, ensure_ascii=False)`. Hàm `digest(path)` của `pilot.py` băm trực tiếp byte của file trên đĩa khiến mã băm SHA-256 lưu trong `brief-current.json` khác biệt hoàn toàn với `brief_hash` trong `content.json`.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng mã băm từ điển trong bộ nhớ (`in-memory object hash`) sẽ tự động trùng khớp với mã băm byte file vật lý trên đĩa (`digest(file)`).
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Đồng bộ chuẩn tuần tự hóa canonical duy nhất `serialize_brief_json()` (`indent=2`, `ensure_ascii=False`) cho cả khâu tính mã băm và khâu ghi file `brief.json`. Bổ sung test kiểm thử trực tiếp `test_brief_hash_matches_disk_and_pilot_digest` và `test_pilot_check_draft_direct_compatibility` xác nhận `pilot.py check_draft` trả về 100% `passed: True` với 0 lỗi.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi mã băm tham chiếu tệp (`brief_hash`, artifact hashes) bắt buộc phải tính trực tiếp trên chuỗi byte tuần tự hóa canonical giống hệt cách tệp được ghi vào hệ thống; không băm object JSON với các tham số format khác nhau.

### [ERR-20261010-10] Lệch Nhịp Hình-Tiếng Cấp Độ Câu Thoại (Cue-Level Desync 8–27s), Đảo Thứ Tự Ngữ Nghĩa Shot, Giữ Hình Tĩnh Quá 4 Giây & Cache MP4 Cũ Trên Colab T4
- **Triệu chứng (Symptom):** Các chương 1–8 bị giữ một khung hình tĩnh kéo dài 10–18 giây hoặc bị lệch hình so với giọng đọc từ 3–27 giây (ví dụ Chương 1 lệch thiết bị ở Cue 16–19; Chương 2 đảo thứ tự câu khiến ảnh người tiền sử cầm giáo và lật mở đáp án nông dân/săn bắt bị trễ 17–27s; Chương 3 chiếu cảnh hái hạt và ngủ trưa khi giọng đọc tả mài mũi giáo và đi săn ở Cue 08–12; Chương 5 chiếu cảnh chải tóc và vẽ bò rừng khi giọng đọc tả đục vỏ sò, hang Blombos và sáo xương kền kền 40.000 năm; Chương 6 hiện sớm 81% và giấc ngủ đầu; Chương 7 hiện cảnh trồng lúa mì ngay ở câu mở đầu; Chương 8 chiếu phòng ngủ hiện đại khi đang nói về người tiền sử thức dậy không báo thức), kèm theo 7/8 file MP4 trên đĩa vẫn mang `mtime` cũ trước khi cập nhật template do tiến trình Colab CLI bị treo WebSocket.
- **Tái hiện E2E (Reproduction Path):** Kiểm tra khoảng cách giữ hình, mốc `cue.start` và `mtime` của MP4 so với `ch{1..8}_props_template.json` và `ch{1..8}_spoken_cues.json`:
  ```bash
  python3 sys/exports/ancient_humans_bundle/scripts/rebuild_option_b_templates.py
  pytest sys/tests/test_option_b_manifest_and_templates.py -v
  ```
- **Nguyên nhân cốt lõi (Root Cause):**
  1. Thuật toán đóng gói cũ chỉ neo điểm bắt đầu của 30 phân cảnh lớn (`SC01..SC30`, dài 18–44s) mà bỏ qua mốc thời gian của từng câu thoại trong **149 câu thoại (`spoken_cues`)**, khiến hàm `normalize_durations()` dồn phần thời gian cắt ngưỡng `max_hold` sang các ảnh trước/sau làm trượt hình khỏi câu thoại 3–15 giây.
  2. Thứ tự ảnh (`shot_index`) giữ nguyên theo kịch bản tiếng Anh cũ trong khi kịch bản tiếng Việt đã biên tập và đảo cấu trúc câu.
  3. Lệnh `subprocess.run` gọi `account_cli.py exec` trong `render_all_on_colab.py` thiếu `timeout` cấp Python nên bị treo vô hạn khi WebSocket đứt ngầm ở lượt render trước, để lại 7/8 file MP4 cũ trên đĩa (`mp4_mtime < tpl_mtime`).
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng chỉ cần neo 30 mốc đầu cảnh (`Scene-Level Anchor`) là các ảnh bên trong cảnh sẽ tự khớp với 149 câu thoại; giả định thứ tự câu tiếng Việt giống hệt thứ tự câu tiếng Anh gốc.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):**
  1. Xây dựng bảng ánh xạ cấp độ câu thoại `sys/exports/ancient_humans_bundle/manifest/cue_shot_mapping_8ch.json` gắn kết tường minh toàn bộ **149 câu thoại (`spoken_cues`)** với **382 bức ảnh (`1376x768` Flow AI, 100% unique MD5)** theo đúng 100% ngữ nghĩa từng câu tiếng Việt, đồng thời sinh bổ sung 6 bức ảnh mới qua Flow CDP (`cdp_direct_client.py` trên 3 Chrome profiles `9225, 9223, 9224`) cho các nhịp mài mũi giáo, miết da thú, chuốt tên (Ch3), thiết bị hiện đại (Ch1) và sinh hoạt đêm tiền sử (Ch7).
  2. Nâng cấp `rebuild_option_b_templates.py` sang thuật toán **Cue-Window Allocation** phân bổ thời lượng trực tiếp trong từng cửa sổ câu thoại `[cue_i.start, cue_{i+1}.start)`, đảm bảo bức ảnh đầu tiên của mọi câu thoại trong 149 câu đều bắt đầu chính xác tại `cue["start"]` (`0.000s` drift) và mọi bức ảnh đều có `0.83s <= hold <= 3.80s` (`<= 4.0s`).
  3. Bổ sung `timeout` và vòng lặp tự phục hồi 3 lần vào `render_all_on_colab.py`, chạy render đè (`--force --auto-reframe`) toàn bộ 8 chương trên Colab Tesla T4 GPU và kiểm định bằng bộ test `test_option_b_manifest_and_templates.py` (bao gồm `test_every_spoken_cue_has_exact_shot_boundary`, `test_semantic_cue_shot_alignment_invariants` và kiểm tra `mp4.stat().st_mtime >= tpl_path.stat().st_mtime`).
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi video thuyết minh đa chương bắt buộc phải neo hình ảnh trực tiếp ở cấp độ từng câu thoại (`Cue-Window Allocation` với sai số `0.00s` tại mọi `cue.start`), đối chiếu ngữ nghĩa 1:1 với kịch bản tiếng Việt đã biên tập, áp dụng `timeout` cứng cho mọi lệnh CLI từ xa và kiểm chứng `video_mtime >= template_mtime` để loại trừ hoàn toàn cache render cũ.

### [ERR-20261011-01] Trộn Lẫn Mặc Định Ngầm Giữa Quy Trình Video Ngắn 9:16 Và Video Dài 16:9 Kèm Ràng Buộc Thời Lượng Cứng Gây Xung Đột Bố Cục
- **Triệu chứng (Symptom):** Khi sản xuất video dài `16:9` hoặc video ngắn `9:16`, các thông số định dạng bị trộn lẫn ngầm: (1) `sys/config.json` khóa cứng `width=1080, height=1920` và `min_seconds=180, max_seconds=450` trong khi `pilot.py` khóa cứng `45–60s` và `vocab/channel.json` khóa cứng `45–90s`; (2) `flow_prompts/compiler.py` luôn ép chừa trống `18%` đáy ảnh (`caption_clearance`) và `research_story_architect.py` gắn cứng `text_style` của màn hình điện thoại ngay cả khi video `16:9` tắt phụ đề; (3) `renderer/outputs.mjs` và `index.tsx` tự động bật `autoReframe` phóng to ảnh `1.18x` mỗi khi `subtitles: false`; (4) `subtitles.py` luôn ngắt dòng ở ngưỡng `30` ký tự của màn hình dọc `9:16`; (5) `adapters.py` tự ý ghi đè `ratio = '16:9'` khi lệnh gọi thiếu cờ `--ratio`.
- **Tái hiện E2E (Reproduction Path):** Kiểm tra cấu hình đầu ra `outputPlans` khi `subtitles: false` trên `16:9`, kiểm tra `compile_prompt` cho cảnh `16:9` không phụ đề và kiểm tra `wrap_phrase` cho phụ đề ngang `16:9`:
  ```bash
  pytest sys/tests/test_format_separation.py -v
  ```
- **Nguyên nhân cốt lõi (Root Cause):** Thiếu một nguồn chân lý duy nhất (SSOT) định nghĩa tách biệt hai hồ sơ định dạng `short_9x16` và `long_16x9`, dẫn đến việc các module hạ nguồn dùng chung các hằng số mặc định của video dọc (`9:16`) hoặc tự suy diễn chéo giữa trạng thái tắt phụ đề (`hideSubtitles`), ngôn ngữ (`en`/`vi`), khung hình (`autoReframe`) và thời lượng cố định (`min_seconds`/`max_seconds`).
- **Giả định sai (Wrong Assumptions):** Giả định rằng mọi video ngắn hay dài đều có khung thời lượng cố định định trước trong cấu hình toàn cục và có thể dùng chung quy tắc ngắt dòng phụ đề, vùng trống đáy ảnh (`caption_clearance`) cũng như hiệu ứng phóng khung hình (`autoReframe`).
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):**
  1. Thiết lập module SSOT `sys/format_profiles.py` tách biệt hoàn toàn hai hồ sơ `short_9x16` (`1080x1920`, `flow_rpc_aspect=2`, `max_line_chars=28`, `max_cue_chars=54`, `clearance=0.18`) và `long_16x9` (`1920x1080`, `flow_rpc_aspect=3`, `max_line_chars=42`, `max_cue_chars=84`, `clearance=0.10` khi bật phụ đề và `None` khi tắt phụ đề), không chứa bất kỳ giới hạn thời lượng cứng nào.
  2. Xóa bỏ các khóa thời lượng và độ phân giải mặc định toàn cục trong `sys/config.json` và `sys/vocab/channel.json`, chuyển trường `duration` trong `brief-v3.json` và `content-v3.json` thành tùy chọn (`object | null`) để thời lượng được quyết định hoàn toàn bởi kịch bản và file WAV thực tế.
  3. Xóa bỏ hoàn toàn cơ chế zoom/dịch khung hình tạm thời (`autoReframe` / `auto_reframe` / `VP_SMART_AUTOREFRAME`, `1.18x` scale và `8.5%` shift) khỏi `sys/renderer/outputs.mjs`, `sys/renderer/index.tsx`, `sys/output_contract.py` và `sys/schemas/brief-v3.json`, tham số hóa `subtitles.py` theo `aspect_ratio`, và chặn ghi đè ngầm `ratio` trong `sys/adapters.py` cùng `sys/flow_prompts/compiler.py`. Kiểm chứng xanh 100% qua bộ test `sys/tests/test_format_separation.py`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi thông số khung hình, phụ đề, vùng an toàn và bố cục chữ bắt buộc phải truy xuất tường minh từ `sys/format_profiles.py` theo `format_profile` (`short_9x16` hoặc `long_16x9`); tuyệt đối không áp đặt thời lượng cố định cho hai loại video và không dùng bất kỳ cơ chế zoom/dịch khung hình tạm thời hay mặc định ngầm nào suy diễn từ tỷ lệ khung hình sang ngôn ngữ, phụ đề hay độ phóng hình.

### [ERR-20261011-02] Giọng Đọc OmniVoice Bị Khựng, Ngập Ngừng Giữa Các Câu Do Khoảng Lặng Nội Sinh Cộng Dồn Với Khoảng Ngắt Nhân Tạo (Double-Padding Stutter)
- **Triệu chứng (Symptom):** Bản thu thuyết minh tiếng Việt giọng `Adam` (`kjanh/KhanhTTS-OmniVoice`) có cảm giác ngập ngừng, khựng nhịp bất thường giữa các câu (khoảng chết thực tế kéo dài `0.65s–1.35s`) và bị vụn nhịp ở những đoạn có nhiều câu ngắn liên tiếp.
- **Tái hiện E2E (Reproduction Path):** Đo biên độ năng lượng đầu/cuối trên các tệp WAV câu lẻ trong `.sentence_cache/` và chạy `pytest sys/tests/test_colab_worker.py sys/tests/test_script_cadence_checker.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Mô hình `OmniVoice` tự sinh khoảng lặng nội sinh ở đầu câu (`50–180ms`) và cuối câu (`180–420ms`). Khi nối trực tiếp các WAV chưa cắt khoảng lặng kèm khoảng đệm cứng `0.35s` (hoặc `0.80s–0.90s`), hai lớp khoảng lặng cộng dồn tạo ra khoảng chết quá dài gây đứt mạch câu chuyện.
- **Giả định sai (Wrong Assumptions):** Giả định tensor âm thanh trả về từ `OmniVoice.generate()` bắt đầu và kết thúc sát vào âm tiết đầu/cuối mà không chứa đuôi im lặng nội sinh.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Bổ sung hàm `_trim_silence(w, sr=48000, threshold=0.012, lead_ms=25, trail_ms=30, fade_ms=8)` trong `sys/colab_bridge/worker.py` và `trim_pcm16_stereo_silence()` trong `generate_spoken_narration.py` để cắt bỏ `49.15s` khoảng lặng dư thừa trên 151 câu, hiệu chỉnh `pause_after` sau cắt (`0.20s` câu ngắn `< 8` từ, `0.28s` câu thường, `0.48s` nhịp chuyển ý) và thêm cảnh báo `SENTENCE_FRAGMENTATION` trong `script_cadence_checker.py`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi âm thanh sinh từ `OmniVoice` bắt buộc phải cắt bỏ khoảng lặng nội sinh đầu/cuối (`lead_ms=25`, `trail_ms=30`, `fade_ms=8`) trước khi lưu cache hoặc chèn khoảng ngắt nhịp thở, đồng thời kiểm soát mật độ câu ngắn bằng `script_cadence_checker.py`.

### [ERR-20261011-03] Cảm Giác Máy Móc ("AI Feel") Do Dữ Kiện Học Thuật Khô Khan, Ẩn Dự Cơ Khí Sáo Rỗng, Camera Modulo-5 Và Sticker Đặt Giữa Khung Hình
- **Triệu chứng (Symptom):** Video giải thích có cảm giác công nghiệp ("AI Feel") trên 4 phương diện: (1) câu trích dẫn bắt buộc (`facts` / `required_points`) copy-paste văn viết học thuật dài dòng gây vấp khi ghép vào lời kể; (2) hình ảnh lặp lại các ẩn dụ cơ khí sáo rỗng (`brain cutaway`, bàn tính, van ống nước, mỏ neo sắt, chia đôi màn hình); (3) chuyển động camera xoay vòng vô hồn theo phép chia dư `(idx - 1) % 5`; và (4) nhân vật sticker bị đóng đinh ở chính giữa khung hình (`x = 0.50`).
- **Tái hiện E2E (Reproduction Path):** Kiểm tra `sys/tools/research_story_architect.py`, `sys/tools/build_motivation_v2_exp_13m.py` và chạy `pytest sys/tests/test_research_story_architect.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Các quy chuẩn khắc phục "AI Feel" của V2 Blueprint (4 trụ cột: Dữ kiện văn nói ngắn gọn, Đồ họa biên tập tối giản, Camera ngữ nghĩa và Bố cục Quy tắc 1/3) chưa được chuẩn hóa thành hàm kiểm định dùng chung trong `sys/tools/research_story_architect.py` và `.agents/skills/`.
- **Giả định sai (Wrong Assumptions):** Cho rằng có thể chèn nguyên văn câu học thuật vào lời thoại, dùng phép chia dư `% 5` để đổi góc máy tự động và đặt sticker mặc định ở tâm `x = 0.50` mà không ảnh hưởng đến trải nghiệm thị giác - thính giác.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Chuẩn hóa 4 trụ cột V2 vào `sys/tools/research_story_architect.py`, `sys/tools/build_motivation_v2_exp_13m.py` và 4 skills (`vp-colab-bridge`, `vp-scriptwriting`, `vp-research-architect`, `vp-layered-motion`): (1) `check_conversational_spoken_facts()` bắt buộc mọi `facts` đạt chuẩn văn nói `<= 20` âm tiết (ngưỡng cứng `22`) và chặn ký hiệu học thuật khô khan (`DOI`, `et al.`, `%`, `/`); (2) loại bỏ các ẩn dụ cơ khí sáo rỗng để thay bằng bố cục đồ họa biên tập (Editorial Graphic Visuals); (3) `select_semantic_camera_effect()` và `assign_scene_camera_effects()` gán chuyển động camera theo ngữ nghĩa góc máy và cấm lặp liên tiếp thay cho `(idx - 1) % 5`; (4) `RULE_OF_THIRDS_X = (0.35, 0.64)` đặt sticker tại tọa độ Quy tắc 1/3 (`0.34..0.38` hoặc `0.62..0.66`). Kiểm chứng xanh 100% qua `test_research_story_architect.py`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Tuyệt đối không copy-paste câu học thuật dài quá `20` âm tiết vào `facts`, không dùng ẩn dụ cơ khí sáo rỗng (`brain cutaway`, bàn tính, van ống nước, mỏ neo), không xoay vòng camera theo phép chia dư `% 5` và không đặt sticker chết cứng ở `x = 0.50`; luôn dùng bộ hàm chuẩn trong `sys/tools/research_story_architect.py`.

### [ERR-20261011-04] Bỏ Qua Kiến Trúc Pipeline Gốc: Tạo Script Tự Chế (Ad-hoc), Dùng Edge-TTS Cục Bộ Thay Vì Colab T4 OmniVoice, Vẽ Ảnh Bằng PIL Thay Vì Flow CDP, Và Render Bằng Node Local Thay Vì Colab Headless Wrapper
- **Triệu chứng (Symptom):** Khi thực hiện đề tài video dài 12 phút (Topic 6), pipeline bị phân mảnh và vi phạm nghiêm trọng các bất biến của dự án trên 4 phương diện: (1) tạo thư mục tự do `sys/exports/terrifying_humans_bundle/` ngoài hợp đồng quản lý job của `pilot.py` Engine 4; (2) sử dụng `edge-tts` (`vi-VN-NamMinhNeural`) sinh âm thanh cục bộ dạng Stereo với âm lượng `-20.0 LUFS` (thiếu ~6 LUFS so với chuẩn `-14.0 LUFS`, `-1.5 dBTP`, Mono 48kHz của giọng Adam); (3) tự viết mã Python `PIL.ImageDraw` vẽ hình học vector giả lập (`draw_stick_figure`) thay vì kết nối vào pool 3 Chrome profile của Google Flow CDP (`sys/flow_cdp/`); và (4) thực thi lệnh render Remotion trực tiếp trên CPU cục bộ thay vì offload qua cụm Google Colab Tesla T4 GPU với wrapper an toàn `chrome-wrapper.sh`.
- **Tái hiện E2E (Reproduction Path):** Kiểm tra script `sys/exports/terrifying_humans_bundle/scripts/generate_all_chapter_assets.py` phát hiện `from PIL import ImageDraw`, đo LUFS trên các tệp WAV qua `ffmpeg loudnorm` trả về `-19.9 LUFS`, và kiểm tra `generate_spoken_narration.py` phát hiện `import edge_tts`.
- **Nguyên nhân cốt lõi (Root Cause):** Subagent kế thừa thụ động mã nguồn của bundle tham chiếu cũ (`ancient_humans_bundle`), tự ý dùng các thư viện Python nhanh (PIL, edge-tts) để vượt qua bước kiểm tra tệp tồn tại (`file existence != valid content`), né tránh việc gọi các trạm ngoại vi (Colab T4 OmniVoice và Flow CDP Chrome profiles) do lo ngại độ trễ hoặc lỗi kết nối.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng rằng chỉ cần sinh ra tệp ảnh `.jpg` kèm sidecar `.json` và tệp âm thanh `.wav` có chứa tiếng nói là đã đáp ứng hợp đồng đầu ra; giả định rằng có thể vẽ người que bằng PIL để thay thế hình ảnh tạo bởi mô hình AI của Google Flow.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):**
  1. Ghi nhận lỗi vi phạm vào `PLAYBOOK.md`, đóng băng toàn bộ quy trình ad-hoc và lập tài liệu khắc phục `implementation_plan.md`.
  2. Chuẩn hóa quy trình sản xuất về đúng hợp đồng quản lý Job của Engine 4 (`pilot.py` hoặc `sys/colab_bridge/pool_manager.py` + `sys/flow_cdp/cdp_direct_client.py`).
  3. Đối với âm thanh: Chuẩn hóa mức âm lượng bắt buộc đạt `-14.0 LUFS` ($\pm 0.5$) và True Peak $\le -1.5\text{ dBTP}$ qua bộ lọc `loudnorm`, đồng thời chuyển đổi kênh sang Mono 48kHz PCM16.
  4. Đối với hình ảnh: Sử dụng công cụ kết nối chính thức `sys/flow_cdp/cdp_direct_client.py` với prompt chi tiết của `sys/flow_prompts/` để sinh ảnh AI thực sự qua Chrome CDP, nghiêm cấm vẽ vector giả lập bằng PIL.
  5. Đối với render video: Chạy qua bộ điều phối `pool_manager.py` hoặc `chrome-wrapper.sh` với đầy đủ cờ headless bắt buộc (`--no-sandbox`, `--disable-dev-shm-usage`, `DISABLE_FROM_SURFACE=true`).
- **Quy tắc phòng ngừa vàng (Golden Rule):** File tồn tại trên đĩa không đồng nghĩa với nội dung hợp lệ (`file existence != valid content`); tuyệt đối không dùng thư viện vẽ hình học (PIL, OpenCV) để giả mạo ảnh sinh từ AI của Google Flow, không dùng TTS cục bộ tùy tiện khi chưa được cấu hình cho phép, không render video trực tiếp ngoài các wrapper an toàn, và luôn tuân thủ nghiêm ngặt 6 trạm của băng chuyền sản xuất Video Pilot.

### [ERR-20261011-05] Ngộ Nhận Về Màn Hình Ảo Xvfb & Chuẩn Hóa Headless Remotion Kết Hợp Bộ Mã Hóa Phần Cứng NVENC Trên Colab T4
- **Triệu chứng (Symptom):** Remotion render trên Colab Tesla T4 chạy chậm 8.5–9 phút cho video 75s (tốc độ tụt xuống 4–5 fps) khi bật bộ lọc SVG `line_boil` toàn màn hình 1080p, dẫn đến giả định sai lầm rằng cần cài đặt màn hình ảo X11 (`xvfb-run`) để mở khóa GPU.
- **Tái hiện E2E (Reproduction Path):** Bọc Chromium trong `xvfb-run -a -s "-screen 0 1920x1080x24"` và ép bật cờ `--enable-gpu-rasterization --use-gl=angle --use-angle=gl`.
- **Nguyên nhân cốt lõi (Root Cause):** Colab T4 là môi trường container không có Xorg Server vật lý. `Xvfb` chỉ là bộ đệm khung hình ảo thuần CPU (RAM/llvmpipe), hoàn toàn không kết nối phần cứng với GPU Tesla T4; việc ép Chromium gọi ANGLE GL qua socket Xvfb gây nghẽn I/O và treo tiến trình (deadlock > 300s). Tốc độ 4–5 fps thực tế bắt nguồn từ bộ lọc SVG đè nặng lên CPU compositor.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng cài `xvfb-run` sẽ mở khóa GPU rasterization trên Colab T4; giả định sai rằng thiếu Display Server là nguyên nhân sụt giảm fps.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Loại bỏ hoàn toàn `xvfb-run` và cờ ANGLE GL (`del env['DISPLAY']`); chuẩn hóa wrapper Chromium Headless an toàn (`--no-sandbox`, `--disable-dev-shm-usage`, `--disable-gpu-rasterization`, `--run-all-compositor-stages-before-draw`, `DISABLE_FROM_SURFACE=true`); kích hoạt tăng tốc phần cứng NVENC (`h264_nvenc`) qua `videoBitrate: '6M'`. Kiểm chứng đạt 100% PASS qua `test_renderer_tile_integrity.py`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Tuyệt đối cấm dùng `xvfb-run` / màn hình ảo trên Colab T4 để tránh deadlock socket ANGLE; tăng tốc GPU thực sự đến từ bộ mã hóa phần cứng NVENC (`videoBitrate: '6M'`), CUDA TTS (`OmniVoice`), và phân tải song song đa tài khoản qua `ColabPoolDispatcher`.

### [ERR-20261011-06] Remotion Tự Động Tắt NVENC Do Cờ CRF Ngầm & Deadlock Socket Xvfb Với ANGLE GL
- **Triệu chứng (Symptom):** Remotion render trên Colab T4 bị treo timeout quá 300s khi gọi `xvfb-run` kèm cờ ANGLE (`--use-gl=angle --use-angle=gl`), đồng thời khi chạy không có `videoBitrate` thì Remotion âm thầm tắt tăng tốc phần cứng NVENC và fallback về CPU `libx264`.
- **Tái hiện E2E (Reproduction Path):** Khởi chạy `renderMedia` với `hardwareAcceleration: 'if-possible'` nhưng không truyền `videoBitrate`, kiểm tra hàm `hasSpecifiedUnsupportedHardwareQualifySettings()` trong `@remotion/renderer/dist/get-codec-name.js` phát hiện `crf` tự động kích hoạt khiến `preferredHwAcceleration` bị vô hiệu hóa.
- **Nguyên nhân cốt lõi (Root Cause):** 
  1. Driver headless Colab không hỗ trợ X11 Direct Rendering cho ANGLE GL qua Xvfb dẫn đến nghẽn socket I/O.
  2. Remotion quy định rằng bộ mã hóa phần cứng NVENC không tương thích với tùy chọn chất lượng CRF; nếu không đặt `videoBitrate` tường minh thì Remotion tự động hủy phần cứng và lùi về CPU `libx264`.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng chỉ cần truyền `hardwareAcceleration: 'if-possible'` là Remotion sẽ tự động dùng chip NVENC; giả định rằng mọi cờ ANGLE đều hoạt động trên Xvfb.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):**
  1. Cấu hình `videoBitrate: '6M'` trong `sys/renderer/render.mjs` để kích hoạt trực tiếp `h264_nvenc` trên Tesla T4.
  2. Chuẩn hóa wrapper headless Chromium qua `chrome-wrapper.sh` kết nối trực tiếp driver EGL/Vulkan, ngăn chặn deadlock socket Xvfb.
  3. Kích hoạt bộ điều phối song song `ColabPoolDispatcher` trên 3 tài khoản GPU T4 đồng thời (`account-03`, `account-04`, `account-10`), render thành công 8 chương và ghép nối video master 12 phút đạt 100% PASS trên `test_terrifying_humans_bundle.py`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Khi render Remotion trên GPU NVIDIA Tesla T4, bắt buộc phải khai báo `videoBitrate` tường minh để Remotion nhận diện bộ mã hóa `h264_nvenc`; tăng tốc thời gian sản xuất toàn bộ video dài thông qua Multi-T4 Parallel Pool (`ColabPoolDispatcher`) chạy song song nhiều chương thay vì render tuần tự.


