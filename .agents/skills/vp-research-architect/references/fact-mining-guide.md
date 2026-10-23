# Hướng Dẫn Khai Thác Dữ Kiện, Định Vị Ngách Học Thuật & Việt Hóa 60 Giây Đầu (Fact Mining & Localization Guide)

Tài liệu hướng dẫn dành cho **Research & Narrative Architect** nhằm biến những công trình nghiên cứu học thuật chuẩn quốc tế (Q1) thành các câu chuyện sắc bén, chạm đúng nỗi đau nhận thức của khán giả Việt Nam và chuyển hóa tự nhiên sang hệ sinh thái nghiên cứu chuyên sâu trong Video Pilot.

---

## 1. Định Vị Cố Định Ngách Kênh & Phễu Nội Dung 3 Tầng (Pillar Lock & 3-Tier Funnel)

Trục nội dung được định vị cố định vào ngách **"Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức"** (Cognitive Thinking, Methodology & Epistemic Depth). 

Kênh tập trung giải mã các cơ chế nhận thức sâu sắc, phương pháp tư duy gốc rễ và bản chất của việc hình thành tri thức, giúp người xem nhìn thấu các hiện tượng tâm lý, học tập, công việc và cuộc sống từ góc nhìn nguyên lý đầu tiên (*First-Principles*).

### Quy hoạch Đề tài theo Mô hình Phễu 3 Tầng Linh Hoạt (`funnel_tier`)

Hệ thống phân tầng nội dung theo chiều sâu nhận thức thay vì áp đặt các chủ đề mẫu hay tình huống cố định hẹp:

- **Tầng 1 — Phễu Rộng (`tier_1_broad`, độ lan tỏa đại chúng cao trên TikTok & YouTube): "Tư Duy Nhận Thức, Nghịch Lý & Ảo Giác Tri Thức"**
  - *Mục tiêu:* Tiếp cận tệp người học và người đi làm quan tâm đến phát triển tư duy, bóc tách các ảo giác tâm lý nhận thức phổ biến.
  - *Đặc trưng nội dung:* Các nghịch lý nhận thức, thiên kiến vô thức (*Cognitive Biases*), mô hình tư duy (*Mental Models*), sự ngộ nhận giữa việc tiếp xúc thông tin thụ động và sự thấu suốt bản chất. Đề tài mở rộng tự do dựa trên các cơ chế tâm lý và nhận thức thực nghiệm.

- **Tầng 2 — Phễu Giữa (`tier_2_mid`, tỷ lệ Lưu/Share và giữ chân người xem chuyên sâu rất cao): "Phương Pháp Luận, Phân Tích Căn Nguyên & Bản Chất Vấn Đề"**
  - *Mục tiêu:* Dành cho những ai muốn nắm bắt phương pháp luận giải quyết vấn đề, quy trình nghiên cứu, phân tích chuỗi nhân quả và tư duy hệ thống.
  - *Đặc trưng nội dung:* Giải phẫu cấu trúc luận chứng, tư duy nguyên lý đầu tiên, cách phát hiện khoảng trống tri thức (*Knowledge Gap*), đối chiếu các bằng chứng khoa học, mổ xẻ nguyên nhân gốc rễ (*Root-Cause Analysis*) thay vì triệu chứng bề mặt.

- **Tầng 3 — Phễu Chuyển Đổi (`tier_3_conversion`, nâng cao năng lực tư duy chuyên sâu): "Công Cụ & Khung Tư Duy Đào Sâu Tri Thức"**
  - *Mục tiêu:* Chuyển hóa tri thức thành công cụ tư duy, mô hình hành động và phương pháp luận cấp tiến.
  - *Quy tắc Chống Loãng Tệp:* **Tuyệt đối cấm** các mẹo vặt văn phòng hời hợt (*mẹo Excel, làm slide nhanh, mẹo học vẹt đối phó*). Nội dung tầng 3 phải tập trung vào các khung tư duy thượng nguồn (*Intellectual Frameworks*), cách kết nối tri thức đa ngành, hoặc ứng dụng AI/công nghệ để phản biện, tổng hợp và kiến tạo tri thức có chiều sâu.

---

## 2. Tiêu Chí Khai Thác Nguồn Học Thuật (Academic Sourcing Standards)

Mọi luận điểm và cơ chế giải thích trong video phải dựa trên nền tảng khoa học vững chắc:

1. **Nguồn có định danh kiểm chứng được:**
   - **DOI (Digital Object Identifier):** Đối với các bài báo bình duyệt trên tạp chí chuyên ngành uy tín (Nature, Science, PNAS, Psychological Science, Journal of Educational Psychology...).
   - **ISBN (Sách chuyên khảo/phương pháp luận):** Các ấn phẩm từ nhà xuất bản đại học (Oxford, Harvard, Cambridge, MIT Press, *The Craft of Research* - Booth et al.).
   - **Quy tắc Văn nói (`Conversational Spoken Fact Protocol`):** Lưu giữ đầy đủ tên giáo sư, đại học, năm xuất bản và DOI trong `brief.json` (`sources[].reference`), nhưng chuyển hóa `sources[].facts` thành câu văn nói tiếng Việt tự nhiên $\le 20$ âm tiết (ngưỡng cứng $22$), không đọc danh xưng học thuật rườm rà trong `narration`.
2. **Cơ chế cốt lõi thay vì mẹo vặt bề mặt:**
   - Tuyệt đối tránh các bài viết blog tổng hợp bề mặt kiểu *"5 mẹo gõ hàm Excel"* hay *"Cách làm slide đẹp"*.
   - Khai thác tận gốc **cơ chế nhận thức, tâm lý học thần kinh và phương pháp luận nghiên cứu**: *Illusion of Competence* (Karpicke & Roediger, 2008), *Cognitive Load Theory* (Sweller, 1988), cấu trúc *Create a Research Space - CARS Model* (Swales, 1990), hay phản ứng phòng vệ của hạch hạnh nhân (*amygdala*).

---

## 3. Quy Tắc Việt Hóa Bắt Buộc Trong 60 Giây Đầu (`Vietnamese Cultural Localization`)

Để giải quyết triệt để **Bẫy 4 (Độ vênh văn hóa khi dịch kịch bản ngoại khiến khán giả lướt qua ngay 15–60s đầu)**:

1. **Bắt buộc Việt hóa 100% bối cảnh Chương 1 (`0:00 – 1:30` bản dài) hoặc `SC01–SC02` (bản ngắn):**
   - Mở màn phải chạm trực tiếp vào trải nghiệm sống thật của học sinh, sinh viên, học viên cao học và người đi làm tại Việt Nam:
     - Đêm trước kỳ thi học kỳ hoặc hạn nộp khóa luận tốt nghiệp, giáo trình đánh dấu bút dạ quang vàng rực kín trang nhưng gấp sách lại là quên sạch.
     - Mở file Word trắng tinh gõ ngay chữ *"Chương 1: Cơ sở lý thuyết"* lúc 11 giờ đêm rồi đứng hình suốt 3 tiếng vì chưa xác định được *Research Gap*.
     - Khoảnh khắc 120 giây đầu tiên đứng trên bục bảo vệ khóa luận khi giảng viên phản biện lật nhanh về phần *Tài liệu tham khảo* và đặt câu hỏi *"Đề tài này có gì mới?"*.
     - Áp lực văn phòng cuối tháng, thói quen lướt Shopee/TikTok vô thức lúc 1 giờ sáng, hoặc truyền thống học vẹt văn mẫu và khoa cử phong kiến Việt Nam.
2. **Trì hoãn địa danh & thuật ngữ ngoại xa lạ sang Chương 3 trở đi (`Foreign Jargon Deferral`):**
   - **Nghiêm cấm** đưa các địa danh lịch sử/nhân học xa lạ với người Việt (*Sumer*, *Edubba*, *Lưỡng Hà*, *Mesopotamia*, *nhà máy Phổ*, *sa mạc Kalahari*, *bộ tộc Ju/'hoansi*) vào 60 giây đầu tiên (`CH01` / `SC01–SC02`).
   - Chỉ được dẫn dắt sang các bối cảnh lịch sử thế giới hoặc thí nghiệm quốc tế từ **Chương 3 trở đi** (hoặc từ `SC03` trong video ngắn), sau khi khán giả đã bị khóa chặt sự chú ý bởi nỗi đau thực tại của chính họ ở Chương 1 và cơ chế nhận thức ở Chương 2.

---

## 4. Kỹ Thuật Phát Hiện "Định Kiến Sai Lầm" & Cú Tát Sự Thật (`Truth-Slap Pivot`)

```
[Thói quen học vẹt / Định kiến trực giác của 90% số đông]
                         vs
[Cơ chế Nhận thức / Luật ngầm Học thuật Q1 được chứng minh]
```

1. **Tìm kiếm giả định trực giác sai (Intuitive Fallacy):**
   - *Ví dụ 1:* Sinh viên tin rằng đọc đi đọc lại giáo trình 5 lần và tô màu kín sách là đang học chăm chỉ.
   - *Ví dụ 2:* Người mới nghiên cứu tin rằng viết bài báo khoa học bắt đầu bằng việc mở Microsoft Word lên và gõ từ trang đầu.
2. **Khám phá nghịch lý học thuật (The Scientific Paradox):**
   - *Thực nghiệm nhận thức:* Việc đọc lại thụ động tạo ra *Ảo giác năng lực (Illusion of Competence)* — não nhận diện mặt chữ quen thuộc rồi lầm tưởng là đã nắm được cấu trúc nhân quả.
   - *Chuỗi quyết định Q1:* Một công trình chuẩn quốc tế luôn đi theo chuỗi `Question → Gap → Method → Evidence → Paper`; mở Word khi chưa có *Gap* và *Evidence* chỉ tạo ra văn bản rỗng.
3. **Định hình câu mở đầu Cú Tát Sự Thật (`Counter-Intuitive Hook <= 18 âm tiết`):**
   - *"Tô màu kín quyển giáo trình không giúp bạn giỏi lên, nó đang ru ngủ não bạn."* (16 âm tiết).
   - *"Bài báo khoa học chuẩn quốc tế không bao giờ bắt đầu bằng việc mở Word."* (15 âm tiết).

---

## 5. Cấu Trúc Sổ Bộ Dữ Kiện & Nguồn Chuẩn Văn Nói (`Fact Verification Ledger`)

Mọi dữ kiện trong `sources[].facts` bắt buộc phải tuân thủ **Conversational Spoken Fact Protocol** ($\le 20$ âm tiết, không chứa ký hiệu `DOI`, `et al.`, `%`, `/`):

```json
{
  "sources": [
    {
      "id": "SRC01",
      "title": "The Critical Importance of Retrieval for Learning",
      "author": "Dr. Jeffrey D. Karpicke & Dr. Henry L. Roediger",
      "year": 2008,
      "reference": "Science, 319(5865), 966-968. DOI: 10.1126/science.1152408",
      "facts": [
        "Đọc lại sách nhiều lần chỉ tạo ra ảo giác rằng bạn đã hiểu bài.",
        "Não bộ chỉ thực sự ghi nhớ sâu khi phải tự mình truy xuất thông tin."
      ]
    },
    {
      "id": "SRC02",
      "title": "Genre Analysis: English in Academic and Research Settings",
      "author": "Dr. John M. Swales",
      "year": 1990,
      "reference": "Cambridge University Press. ISBN: 978-0521338134",
      "facts": [
        "Bài báo quốc tế luôn bắt đầu từ khoảng trống tri thức chứ không phải trang giấy.",
        "Hội đồng phản biện luôn tìm kiếm lỗ hổng nghiên cứu ngay trong hai phút đầu."
      ]
    }
  ]
}
```
