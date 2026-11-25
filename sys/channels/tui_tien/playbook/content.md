# Content & Script Strategy — Túi Tiền Biết Nói (`tui_tien`)

## 1. Standalone Packaging & V4 Short Funnel
- **Title Contract:** `youtube_title <= 55` characters. Strictly NO numbered prefixes (`P1:`, `Part 2:`, `Ep 3:`) on Shorts.
- **Funnel Twin:** Shares verified primary Fact Vault research with sibling channel `en_wallet_anatomy` (`./vp clone-en` / bilingual adaptation).
- **Short->Long Policy:** Declare `parent_long_id` when linked; place channel bridge + 2-choice debate question inside final `15%` (`youtube_closing_question` / pinned creator comment). Never say *"like/share/subscribe"*.
- **NotebookLM 3-Vault Grounding:** Compile verified primary sources into `fact_vault.json` via `sys/tools/notebooklm_vault.py` before drafting narration (`fact_grounding_linter.py --strict`).

## 2. Proven Narrative Spine (`Two Cents PBS / WSJ Consumer Economics / Tài Chính & Kinh Doanh`)
- **Sentence Structure Formula:** Công thức bóc tách dòng tiền 5 bước: (1) Nêu món đồ quen thuộc và mức giá niêm yết ('Một ly trà sữa 50 nghìn...') -> (2) Cú sốc chi phí nguyên liệu thực tế ('thực chất chỉ tốn chưa tới 4 nghìn') -> (3) Câu hỏi truy vết dòng tiền thất thoát ('Vậy 46 nghìn còn lại biến đi đâu?') -> (4) Liệt kê chi phí chìm vô hình ('Mặt bằng, thương hiệu, chiết khấu app giao hàng...') -> (5) Đòn bẩy hành động bảo vệ ví tiền ('Hiểu rõ giá gốc để không bao giờ bị bẫy giá chi phối').
- **Long (`long_16x9`) Spine:** Cold open 0-30s: strongest scene of the video, no channel intro -> Stakes: why this matters to the viewer's own life -> 3-5 chapters, each opens with a mini-hook and ends with a re-hook -> Pattern interrupt every 20-30s (story, number, visual gag) -> Synthesis + practical takeaway -> Closing line pointing to the next video
- **Short (`short_9x16`) Spine:** Hook <= 3s: shocking claim or relatable pain + striking first frame -> Open loop: promise the answer, delay it -> Escalation beats every 2-5s (new visual, number or twist) -> Payoff: answer the loop in one clear image -> Closing line
- **20s Verbatim Rhythm Benchmark:** [00:00-00:03.2s] 'Một ly trà sữa 50 nghìn trên tay bạn...' [pause 0.28s] -> [00:03.5-00:07.8s] 'thực chất chi phí trà, sữa và trân châu chỉ tốn chưa tới 4 nghìn đồng.' [pause 0.42s] -> [00:08.2-00:13.1s] 'Vậy 46 nghìn còn lại đã biến đi đâu mất?' [pause 0.48s] -> [00:13.6-00:20.0s] 'Mặt bằng, nhân viên, bao bì... và đặc biệt là phí nhượng quyền thương hiệu âm thầm rút sạch túi tiền của bạn.'

## 3. Hook Templates & Seed Topics
### Hook Templates
- Ly [món] [giá] nghìn, chủ quán thật ra lời bao nhiêu?
- Vì sao [thương hiệu/mô hình] lỗ mà vẫn mở thêm chi nhánh?
- Nếu mỗi ngày bạn bớt [khoản nhỏ], 5 năm sau bạn có [số tiền].
- Bạn đang trả tiền cho [thứ vô hình] mà không biết.

### Seed Topic Queue
- Ly trà sữa 35 nghìn: chủ quán lời thật bao nhiêu
- Vì sao siêu thị để sữa ở cuối cửa hàng
- Mua trả góp 0%: ai trả lãi cho bạn
- Vì sao quán cà phê sống được dù khách ngồi cả ngày
- Bớt 30 nghìn mỗi ngày, 5 năm sau bạn có bao nhiêu
