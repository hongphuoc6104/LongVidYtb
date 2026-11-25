# Content & Script Strategy — Tâm Tĩnh Đêm (`tam_tinh_dem`)

## 1. Standalone Packaging & V4 Short Funnel
- **Title Contract:** `youtube_title <= 55` characters. Strictly NO numbered prefixes (`P1:`, `Part 2:`, `Ep 3:`) on Shorts.
- **Funnel Twin:** Shares verified primary Fact Vault research with sibling channel `en_bamboo_marble` (`./vp clone-en` / bilingual adaptation).
- **Short->Long Policy:** Declare `parent_long_id` when linked; place channel bridge + 2-choice debate question inside final `15%` (`youtube_closing_question` / pinned creator comment). Never say *"like/share/subscribe"*.
- **NotebookLM 3-Vault Grounding:** Compile verified primary sources into `fact_vault.json` via `sys/tools/notebooklm_vault.py` before drafting narration (`fact_grounding_linter.py --strict`).

## 2. Proven Narrative Spine (`Pursuit of Wonder / Studio Ghibli Nocturnal`)
- **Sentence Structure Formula:** Công thức ngụ ngôn đêm vỗ về 5 bước: (1) Lời nhắn nhủ buông bỏ áp lực ngày dài ('Đêm đã khuya, hãy gác lại âu lo...') -> (2) Sự công nhận và an ủi nỗ lực ('Bạn đã cố gắng hết sức hôm nay rồi') -> (3) Ẩn dụ thiên nhiên vỗ về ('Như dòng sông sau ghềnh đá tìm về biển hồ') -> (4) Hình ảnh mặt nước phẳng lặng soi bóng sao ('Lắng đọng tâm trí để thấy bình an') -> (5) Lời chúc giấc ngủ tròn đầy hy vọng ('Nhắm mắt lại, ngày mai sẽ là một khởi đầu dịu dàng').
- **Long (`long_16x9`) Spine:** Cold open 0-30s: strongest scene of the video, no channel intro -> Stakes: why this matters to the viewer's own life -> 3-5 chapters, each opens with a mini-hook and ends with a re-hook -> Pattern interrupt every 20-30s (story, number, visual gag) -> Synthesis + practical takeaway -> Closing line pointing to the next video
- **Short (`short_9x16`) Spine:** Hook <= 3s: shocking claim or relatable pain + striking first frame -> Open loop: promise the answer, delay it -> Escalation beats every 2-5s (new visual, number or twist) -> Payoff: answer the loop in one clear image -> Closing line
- **20s Verbatim Rhythm Benchmark:** [00:00-00:04.2s] 'Đêm đã khuya, hãy gác lại mọi lo toan ngoài ngưỡng cửa...' [pause 0.35s] -> [00:04.6-00:09.5s] 'Ngày hôm nay bạn đã cố gắng hết sức mình rồi.' [pause 0.48s] -> [00:10.0-00:14.6s] 'Như dòng sông sau một ngày chảy xiết qua ghềnh đá...' [pause 0.40s] -> [00:15.0-00:20.0s] 'giờ đây nó tìm về với biển hồ tĩnh lặng, để mặt nước phẳng lặng soi bóng những vì sao.'

## 3. Hook Templates & Seed Topics
### Hook Templates
- Đêm nay trước khi nhắm mắt, có một câu chuyện ngắn mình muốn kể cho bạn nghe.
- Bài học từ chiếc bình nứt: vì sao những khiếm khuyết của bạn lại tạo nên điều kỳ diệu?
- Ba chiếc sàng của Socrates: điều bạn sắp nghe có thật sự đáng để bận lòng?
- Vì sao chúng ta luôn bao dung với người ngoài nhưng lại khắt khe với người thương nhất?

### Seed Topic Queue
- nghĩ về lòng biết ơn
- Ba Chiếc Sàng Của Socrates: Quy Tắc Lọc Lời Đồn Trước Khi Để Tâm Trí Bị Tổn Thương
- Chiếc Bình Nứt Và Bài Học Chấp Nhận Những Khiếm Khuyết Của Chính Mình
- Câu Chuyện Bát Mì Đêm Mưa: Vì Sao Ta Hay Tử Tế Với Người Lạ Nhưng Gắt Gỏng Với Người Thân?
- Luật Nhân Quả Trong Lời Nói: Một Câu Nói Ấm Áp Có Thể Cứu Một Ngày Tồi Tệ Ra Sao?
- Trước Khi Đi Ngủ Đêm Nay: 3 Thứ Cần Đặt Xuống Để Sáng Mai Thức Dậy Nhẹ Lòng
