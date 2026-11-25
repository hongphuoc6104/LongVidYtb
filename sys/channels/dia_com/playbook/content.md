# Content & Script Strategy — Đĩa Cơm Khoa Học (`dia_com`)

## 1. Standalone Packaging & V4 Short Funnel
- **Title Contract:** `youtube_title <= 55` characters. Strictly NO numbered prefixes (`P1:`, `Part 2:`, `Ep 3:`) on Shorts.
- **Funnel Twin:** Shares verified primary Fact Vault research with sibling channel `en_kitchen_molecules` (`./vp clone-en` / bilingual adaptation).
- **Short->Long Policy:** Declare `parent_long_id` when linked; place channel bridge + 2-choice debate question inside final `15%` (`youtube_closing_question` / pinned creator comment). Never say *"like/share/subscribe"*.
- **NotebookLM 3-Vault Grounding:** Compile verified primary sources into `fact_vault.json` via `sys/tools/notebooklm_vault.py` before drafting narration (`fact_grounding_linter.py --strict`).

## 2. Proven Narrative Spine (`America's Test Kitchen / Modernist Cuisine`)
- **Sentence Structure Formula:** Công thức hóa học ẩm thực 5 bước: (1) So sánh đối nghịch quen thuộc trong bếp ('Rán thịt thì thơm nức vs luộc thì nhạt nhòa') -> (2) Đặt câu hỏi truy tìm phản ứng hóa học ('Tại sao nhiệt độ lại quyết định mùi hương?') -> (3) Hé lộ tên phản ứng và ngưỡng kích hoạt ('Phản ứng Maillard bùng nổ trên 140 độ C') -> (4) Giải thích lý do thất bại ở phương pháp cũ ('Nước sôi 100 độ kìm hãm phân tử hương') -> (5) Mẹo nấu ăn khoa học áp dụng ngay ('Thấm khô mặt thịt trước khi áp chảo nóng').
- **Long (`long_16x9`) Spine:** Cold open 0-30s: strongest scene of the video, no channel intro -> Stakes: why this matters to the viewer's own life -> 3-5 chapters, each opens with a mini-hook and ends with a re-hook -> Pattern interrupt every 20-30s (story, number, visual gag) -> Synthesis + practical takeaway -> Closing line pointing to the next video
- **Short (`short_9x16`) Spine:** Hook <= 3s: shocking claim or relatable pain + striking first frame -> Open loop: promise the answer, delay it -> Escalation beats every 2-5s (new visual, number or twist) -> Payoff: answer the loop in one clear image -> Closing line
- **20s Verbatim Rhythm Benchmark:** [00:00-00:03.6s] 'Tại sao rán thịt bò thì thơm ngào ngạt...' [pause 0.26s] -> [00:03.9-00:08.2s] 'nhưng nếu đem luộc, mùi vị lại nhạt nhòa đến vậy?' [pause 0.40s] -> [00:08.6-00:13.5s] 'Bí mật nằm ở phản ứng Maillard chỉ bùng nổ ở nhiệt độ trên 140 độ C.' [pause 0.46s] -> [00:14.0-00:20.0s] 'Nước sôi chỉ tới 100 độ, khóa chặt hàng trăm phân tử hương thơm không cho bung tỏa.'

## 3. Hook Templates & Seed Topics
### Hook Templates
- Vì sao [món ăn/thói quen bếp] tưởng vô hại lại biến chất ở [nhiệt độ]?
- Khoa học giải thích vì sao mẹ bạn luôn [thói quen nấu ăn] đúng đến kinh ngạc.
- Bí mật hóa học đằng sau miếng thịt kho tàu mềm rục mà không nát.
- Đừng [thói quen rã đông/bảo quản] kiểu này nếu không muốn vi khuẩn nhân đôi.

### Seed Topic Queue
- nấu ăn tại nhà
- Phản ứng Maillard: bí quyết để thịt áp chảo dậy mùi thơm nức mũi
- Vì sao rã đông thịt bằng nước nóng là sai lầm nguy hiểm
- Hóa học của nồi nước dùng phở trong veo không bị đục
- Cơm nguội hâm lại: cách bảo quản đúng để không sinh độc tố
