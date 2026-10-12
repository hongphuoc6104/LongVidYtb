# Hướng Dẫn Khai Thác Dữ Kiện & Định Kiến Khoa Học (Fact Mining Guide)

Tài liệu hướng dẫn dành cho **Research & Narrative Architect** nhằm biến những công trình nghiên cứu học thuật phức tạp thành các câu chuyện ngắn gọn, sâu sắc và lay động lòng người trong Video Pilot.

---

## 1. Tiêu Chí Khai Thác Nguồn Học Thuật (Academic Sourcing Standards)

Mọi luận điểm và cơ chế giải thích trong video phải dựa trên nền tảng khoa học vững chắc:

1. **Nguồn có định danh kiểm chứng được:**
   - **DOI (Digital Object Identifier):** Đối với các bài báo bình duyệt trên tạp chí chuyên ngành uy tín (Nature, Science, PNAS, Journal of Neuroscience, Psychological Science...).
   - **ISBN (Sách chuyên khảo/học thuật):** Các ấn phẩm từ nhà xuất bản đại học (Oxford University Press, Harvard University Press, Cambridge...).
   - **Tác giả & Viện nghiên cứu:** Xác định rõ tên nhà khoa học đứng đầu công trình và trường đại học nơi nghiên cứu được thực hiện.
   - **Năm công bố:** Ưu tiên các nghiên cứu kinh điển có sự xác nhận của các phân tích tổng hợp (meta-analysis) gần đây.

2. **Cơ chế cốt lõi thay vì mẹo vặt bề mặt:**
   - Tránh trích dẫn các bài viết blog self-help tổng hợp bề mặt kiểu *"5 mẹo để làm việc tập trung"*.
   - Khai thác tận gốc **cơ chế sinh học/tâm lý học**: ví dụ phản ứng phòng vệ của hạch hạnh nhân (amygdala), sự mệt mỏi ý chí của thùy trán trước (prefrontal cortex), hay sự biến động chất dẫn truyền dopamine.

---

## 2. Kỹ Thuật Phát Hiện "Định Kiến Sai Lầm Phổ Biến" (Common Misconception Discovery)

Một video hấp dẫn không đơn thuần là cung cấp kiến thức mới, mà là **lật ngược niềm tin cũ** của khán giả:

```
[Niềm tin trực giác phổ biến của 90% số đông] 
                     vs
[Sự thật thực nghiệm được khoa học chứng minh]
```

### Các bước phát hiện định kiến:
1. **Tìm kiếm giả định trực giác sai (Intuitive Fallacy):**
   - Đặt câu hỏi: *"Khán giả nghĩ lý do của hiện tượng này là gì?"*
   - *Ví dụ về sự trì hoãn:* Khán giả nghĩ họ lười biếng, thiếu kỷ luật hoặc quản lý thời gian kém.
2. **Khám phá nghịch lý khoa học (The Scientific Paradox):**
   - Đặt câu hỏi: *"Nghiên cứu khoa học đo đạc được điều gì thực sự diễn ra trong não bộ/cơ thể?"*
   - *Ví dụ:* Các nhà khoa học thần kinh phát hiện trì hoãn là một phản ứng né tránh cảm xúc tiêu cực (emotional regulation failure). Não bộ xem nhiệm vụ khó như một mối đe dọa sinh tồn.
3. **Định hình câu đòn bẩy (The Pivot Statement):**
   - Tạo ra câu nói lật ngược vấn đề tạo cảm giác bừng tỉnh:
   - *"Bạn không trì hoãn vì bạn lười. Bạn trì hoãn vì não bạn đang cố bảo vệ bạn khỏi sự căng thẳng."*

---

## 3. Kỹ Thuật Neo Giữ Trải Nghiệm Đời Thường (Daily-Life Relatability Anchor)

Khoa học trừu tượng sẽ trở nên vô nghĩa nếu không chạm được vào giác quan và thói quen thường nhật của khán giả:

1. **Khoảnh khắc vi mô (Micro-Moments):**
   - Chọn một hành động cụ thể, quen thuộc đến mức ai cũng từng trải qua:
     - 11:30 đêm trước deadline, bạn mở tủ lạnh lần thứ 4 dù bụng không hề đói.
     - Chuông báo thức kêu, bạn tắt đi và nhìn chằm chằm lên trần nhà thêm 15 phút.
     - Dọn dẹp bàn làm việc sạch bóng chỉ để tránh phải mở file báo cáo.
2. **Phép thử chiếc bàn cà phê (The Coffee Table Test):**
   - Khi viết lời dẫn giải thích cơ chế, hãy tưởng tượng bạn đang kể cho một người bạn thân nghe bên tách cà phê.
   - Nếu bạn dùng các từ ngữ quá nặng nề: *"Cơ chế kích hoạt thụ thể ức chế GABAergic..."* $\rightarrow$ Bạn trượt bài kiểm tra.
   - Hãy chuyển hóa: *"Hạch hạnh nhân trong đầu bạn lập tức bật còi báo động, giống hệt như khi tổ tiên chúng ta nhìn thấy thú dữ ngoài đồng cỏ."*

---

## 4. Cấu Trúc Sổ Bộ Dữ Kiện & Nguồn (Fact Verification Ledger)

Trước khi viết kịch bản, kiến trúc sư nghiên cứu phải hệ thống hóa thông tin vào bảng dữ liệu chuẩn:

```json
{
  "sources": [
    {
      "id": "SRC01",
      "title": "Procrastination and the Priority of Short-Term Mood Regulation",
      "author": "Dr. Timothy A. Pychyl & Dr. Fuschia M. Sirois",
      "year": 2013,
      "reference": "Social and Personality Psychology Compass, 7(2), 115-127. DOI: 10.1111/spc3.12011",
      "facts": [
        "Trì hoãn là sự thất bại trong điều hòa cảm xúc ngắn hạn, không phải vấn đề quản lý thời gian.",
        "Hạch hạnh nhân xem xét nhiệm vụ gây lo âu như một mối đe dọa trực tiếp đến tâm lý.",
        "Não bộ ưu tiên xoa dịu cảm xúc tức thì hơn là phần thưởng dài hạn của tương lai."
      ]
    }
  ]
}
```

Mọi dữ kiện trong danh sách `facts` sau đó sẽ được liên kết trực tiếp vào mảng `claims` trong `content.json`, đảm bảo tính trung thực 100% của video.
