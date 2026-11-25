# Content & Script Strategy — Luật Đời Thường (`luat_doi_thuong`)

## 1. Standalone Packaging & V4 Short Funnel
- **Title Contract:** `youtube_title <= 55` characters. Strictly NO numbered prefixes (`P1:`, `Part 2:`, `Ep 3:`) on Shorts.
- **Funnel Twin:** Shares verified primary Fact Vault research with sibling channel `en_fine_print` (`./vp clone-en` / bilingual adaptation).
- **Short->Long Policy:** Declare `parent_long_id` when linked; place channel bridge + 2-choice debate question inside final `15%` (`youtube_closing_question` / pinned creator comment). Never say *"like/share/subscribe"*.
- **NotebookLM 3-Vault Grounding:** Compile verified primary sources into `fact_vault.json` via `sys/tools/notebooklm_vault.py` before drafting narration (`fact_grounding_linter.py --strict`).

## 2. Proven Narrative Spine (`LegalEagle / CNBC Make It / Luật Sư X`)
- **Sentence Structure Formula:** Công thức giải mã bẫy pháp lý 5 bước: (1) Cảnh báo hành vi ký kết chủ quan ('Ký mà không đọc kỹ...') -> (2) Hậu quả thiệt hại tài chính nhãn tiền ('mất trắng tiền cọc') -> (3) Viện dẫn căn cứ pháp lý bảo vệ ('Điều luật quy định rõ...') -> (4) Câu hỏi lật tẩy bẫy chữ nghĩa ('Tại sao người thuê vẫn chịu thiệt?') -> (5) Thao tác hợp đồng thực chiến để tự bảo vệ ('Thêm đúng một câu này trước khi đặt bút ký').
- **Long (`long_16x9`) Spine:** Cold open 0-30s: strongest scene of the video, no channel intro -> Stakes: why this matters to the viewer's own life -> 3-5 chapters, each opens with a mini-hook and ends with a re-hook -> Pattern interrupt every 20-30s (story, number, visual gag) -> Synthesis + practical takeaway -> Closing line pointing to the next video
- **Short (`short_9x16`) Spine:** Hook <= 3s: shocking claim or relatable pain + striking first frame -> Open loop: promise the answer, delay it -> Escalation beats every 2-5s (new visual, number or twist) -> Payoff: answer the loop in one clear image -> Closing line
- **20s Verbatim Rhythm Benchmark:** [00:00-00:03.8s] 'Ký vào hợp đồng thuê nhà mà không đọc dòng này...' [pause 0.26s] -> [00:04.1-00:08.5s] 'bạn vừa vô tình tặng trắng hai tháng tiền cọc cho chủ nhà.' [pause 0.40s] -> [00:08.9-00:13.8s] 'Pháp luật dân sự quy định rất rõ về điều khoản bất khả kháng.' [pause 0.35s] -> [00:14.2-00:20.0s] 'Nhưng tại sao 90 phần trăm người đi thuê vẫn ngậm đắng nuốt cay chịu mất tiền?'

## 3. Hook Templates & Seed Topics
### Hook Templates
- Đi thuê nhà thấy điều khoản này trong hợp đồng: tuyệt đối không đặt bút ký.
- Chủ nhà không chịu trả tiền cọc: 3 bước đòi lại tiền đúng luật 100%.
- Cho bạn thân vay tiền chuyển khoản ghi nội dung này: coi như mất trắng.
- Công ty ép nhân viên nghỉ việc không bồi thường: cách tự vệ chuẩn pháp lý.

### Seed Topic Queue
- đọc kỹ hợp đồng
- 5 cái bẫy trong hợp đồng thuê nhà khiến sinh viên mất trắng tiền cọc
- Chuyển khoản cho vay tiền: ghi nội dung gì để có giá trị pháp lý
- Thử việc xong bị công ty cho nghỉ không lý do: bạn được bồi thường gì
- Mua đất giấy tay: những rủi ro pháp lý mất trắng nhà cửa
