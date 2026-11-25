# Content & Script Strategy — Ủa Sao Vậy? (`ua_sao_vay`)

## 1. Standalone Packaging & V4 Short Funnel
- **Title Contract:** `youtube_title <= 55` characters. Strictly NO numbered prefixes (`P1:`, `Part 2:`, `Ep 3:`) on Shorts.
- **Funnel Twin:** Shares verified primary Fact Vault research with sibling channel `en_wait_how` (`./vp clone-en` / bilingual adaptation).
- **Short->Long Policy:** Declare `parent_long_id` when linked; place channel bridge + 2-choice debate question inside final `15%` (`youtube_closing_question` / pinned creator comment). Never say *"like/share/subscribe"*.
- **NotebookLM 3-Vault Grounding:** Compile verified primary sources into `fact_vault.json` via `sys/tools/notebooklm_vault.py` before drafting narration (`fact_grounding_linter.py --strict`).

## 2. Proven Narrative Spine (`Veritasium / Zack D. Films`)
- **Sentence Structure Formula:** Công thức tò mò bất ngờ 5 bước: (1) Bật thốt câu hỏi ngớ ngẩn nhưng gây nghiện ('Ủa sao bấm bút lại kêu cách cách?') -> (2) Phóng to lát cắt cơ học bên trong ('Bên trong là cỗ máy cam thu nhỏ') -> (3) Bóc tách chi tiết kỹ thuật cốt lõi ('Rãnh xoay định hướng góc 45 độ') -> (4) Giả định nếu cơ chế biến mất ('Nếu thiếu nó, ngòi bút lập tức thụt lùi') -> (5) Cảm thán trí tuệ ẩn sau vật phẩm bình dân ('Một phát minh thiên tài trên đầu ngón tay bạn').
- **Long (`long_16x9`) Spine:** Cold open: the weirdest question of the episode -> Compilation of 6-10 linked 'ủa sao vậy' questions -> Each segment: question -> common wrong answer -> real answer -> visual proof -> Running mascot gag between segments -> Final mind-blowing fact + next episode tease
- **Short (`short_9x16`) Spine:** Hook <= 3s: shocking claim or relatable pain + striking first frame -> Open loop: promise the answer, delay it -> Escalation beats every 2-5s (new visual, number or twist) -> Payoff: answer the loop in one clear image -> Closing line
- **20s Verbatim Rhythm Benchmark:** [00:00-00:03.2s] 'Ủa sao bấm bút bi lại phát ra tiếng cách cách?' [pause 0.22s] -> [00:03.5-00:07.8s] 'Ẩn bên trong thân nhựa rẻ tiền là một cỗ máy cơ khí thu nhỏ' [pause 0.35s] -> [00:08.2-00:12.6s] 'với rãnh xoay cam dẫn hướng cực kỳ tinh xảo.' [pause 0.45s] -> [00:13.1-00:20.0s] 'Nếu không có góc nghiêng 45 độ này, ngòi bút sẽ vĩnh viễn thụt lùi vào trong mỗi khi bạn chạm giấy!'

## 3. Hook Templates & Seed Topics
### Hook Templates
- Ủa, sao [hiện tượng quen thuộc] vậy?
- Ai cũng nghĩ [niềm tin phổ biến]. Sai bét.
- Điều gì xảy ra nếu [tình huống giả định]?
- [Vật quen thuộc] có một bí mật mà 99% người không để ý.

### Seed Topic Queue
- Ủa, sao muỗi chỉ đốt một số người
- Ủa, sao dưa hấu ngâm nước lại nổi
- Ủa, sao mình không tự cù lét mình được
- Điều gì xảy ra nếu bạn không ngủ 3 ngày
- Ủa, sao chai nước suối có hạn sử dụng
