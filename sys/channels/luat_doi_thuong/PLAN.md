# KẾ HOẠCH CHI TIẾT KÊNH: LUẬT ĐỜI THƯỜNG (`luat_doi_thuong`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `luat_doi_thuong` (Đợt triển khai: Wave 2)
- **Nhánh GitHub độc lập:** `channel/luat-doi-thuong` (`origin/channel/luat-doi-thuong`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-luat-doi-thuong`
- **Ngách nội dung:** Pháp lý dân sự bình dân: hợp đồng, thuê nhà, đặt cọc, lao động, vay mượn
- **Lời hứa thương hiệu (Value Proposition):** Hiểu đúng luật đời thường trong 1 phút để tự bảo vệ quyền lợi và túi tiền của mình.
- **Khán giả mục tiêu:** Người đi thuê nhà, người lao động, người kinh doanh nhỏ, gia đình trẻ
- **Nhân vật dẫn chuyện (Persona):** Người bạn hiểu luật, giải thích điều khoản rắc rối bằng ví dụ bình dân
- **Giọng văn (Tone):** Rõ ràng, chuẩn xác, thực tế, bảo vệ người yếu thế | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 45–60s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 10–15 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Luật Sư X** (TikTok): Clear legal warnings on everyday consumer and tenant traps in 60s.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Thư Viện Pháp Luật** (YouTube): Systematic legal code explanations broken down for ordinary citizens.
- **Bộ Luật Dân Sự & Luật Đất Đai Thực Chiến** (Book/Scripture): Căn cứ pháp lý chuẩn mực giải quyết tranh chấp hợp đồng, đặt cọc và quyền sở hữu tài sản.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Mở đầu bằng một tình huống tranh chấp tiền nong hoặc hợp đồng mà ai cũng có thể gặp.
- Trích dẫn đúng tinh thần điều luật hiện hành nhưng giải thích bằng từ ngữ bình dân.
- Luôn chỉ rõ: điều khoản nào là bẫy vô hiệu, làm sao thu thập chứng cứ hợp pháp.
- Khuyến cáo rõ: video mang tính tham khảo kiến thức, vụ việc cụ thể cần luật sư tư vấn.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Đi thuê nhà thấy điều khoản này trong hợp đồng: tuyệt đối không đặt bút ký.`
- `Chủ nhà không chịu trả tiền cọc: 3 bước đòi lại tiền đúng luật 100%.`
- `Cho bạn thân vay tiền chuyển khoản ghi nội dung này: coi như mất trắng.`
- `Công ty ép nhân viên nghỉ việc không bồi thường: cách tự vệ chuẩn pháp lý.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi người xem: bạn từng gặp tranh chấp tương tự chưa? Bình luận nhé.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi vụ việc dân sự điển hình tiếp theo cần phòng tránh.
### Điều cấm kỵ (Avoid)
- Tư vấn pháp lý cho vụ án cụ thể đang xử lý
- Xúi giục lách luật hoặc trốn tránh nghĩa vụ
- Dùng thuật ngữ pháp lý hàn lâm khó hiểu

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_legal_risograph` — Đồ họa Risograph báo chí: minh họa bút mực New Yorker, con dấu pháp lý đỏ trên nền giấy ngà
- **Bảng màu khóa cứng:** `#F4EFE6`, `#1D3557`, `#E63946`, `#A8DADC`, `#457B9D`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Expressive stylized human legal advocate with neat parted dark hair, horn-rimmed glasses, fountain pen and contract folder with proper stylized editorial human proportions
- **Trang phục (`DEFAULT_OUTFIT`):** Crisp Prussian navy (#1D3557) blazer over cream collared shirt with vermilion red pocket square, no shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Sharp legal advocate pointing out red contract trap + 2-4 uppercase VN words.
- **Prompt Style gốc:**
  > Mid-century New Yorker-inspired 2D editorial pen-and-ink risograph print on ivory newsprint canvas (#F4EFE6 ivory newsprint, #1D3557 Prussian ink navy, #E63946 vermilion legal-stamp red, #A8DADC celadon highlight) with subtle paper grain texture, crisp fountain-pen linework, contract seals and balance scales; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **6 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **8–11 phút** cho 1 TikTok Short độc lập; **30–42 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Contract parchment highlighting with Remotion red warning stamps cuts Flow generation by 40%.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Trọn Bộ Cẩm Nang Pháp Lý Đời Thường: Thuê Nhà, Đặt Cọc, Cho Vay Tiền & Hợp Đồng Lao Động*
- **Thời lượng:** 12 phút (26 cảnh)
- **Câu mở đầu (Cold Open):** "Trước khi đặt bút ký vào bất kỳ bản hợp đồng thuê nhà nào, có 3 cái bẫy câu chữ nếu không đọc kỹ sẽ khiến bạn mất trắng tiền cọc."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *đọc kỹ hợp đồng* (50s)
- **Spin-off #2 (0 ảnh mới):** *Chuyển khoản cho vay tiền: ghi nội dung gì để có giá trị pháp lý trước tòa?* (45s)
- **Spin-off #3 (0 ảnh mới):** *Thử việc xong bị công ty cho nghỉ không lý do: bạn được bồi thường gì?* (45s)
- **Fast-Short #4 (6 ảnh Flow):** *Chủ nợ có được quyền nhắn tin đòi người thân của con nợ hay không?* (50s)

### Backlog chủ đề hạt giống tiếp theo
- đọc kỹ hợp đồng
- 5 cái bẫy trong hợp đồng thuê nhà khiến sinh viên mất trắng tiền cọc
- Chuyển khoản cho vay tiền: ghi nội dung gì để có giá trị pháp lý
- Thử việc xong bị công ty cho nghỉ không lý do: bạn được bồi thường gì
- Mua đất giấy tay: những rủi ro pháp lý mất trắng nhà cửa

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#luatdoithuong #phaplybinhdan #hopdong #baovequyenloi #kienthuc`
- **Nguồn doanh thu:** YouTube AdSense, Hợp tác giới thiệu văn phòng luật sư uy tín, Template hợp đồng chuẩn dân sự
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-luat-doi-thuong
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel luat_doi_thuong
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
