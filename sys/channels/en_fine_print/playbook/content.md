# Content & Script Strategy — Everyday Fine Print (`en_fine_print`)

## 1. Standalone Packaging & V4 Short Funnel
- **Title Contract:** `youtube_title <= 55` characters. Strictly NO numbered prefixes (`P1:`, `Part 2:`, `Ep 3:`) on Shorts.
- **Funnel Twin:** Shares verified primary Fact Vault research with sibling channel `luat_doi_thuong` (`./vp clone-en` / bilingual adaptation).
- **Short->Long Policy:** Declare `parent_long_id` when linked; place channel bridge + 2-choice debate question inside final `15%` (`youtube_closing_question` / pinned creator comment). Never say *"like/share/subscribe"*.
- **NotebookLM 3-Vault Grounding:** Compile verified primary sources into `fact_vault.json` via `sys/tools/notebooklm_vault.py` before drafting narration (`fact_grounding_linter.py --strict`).

## 2. Proven Narrative Spine (`CNBC Make It / LegalEagle`)
- **Sentence Structure Formula:** Công thức 5 bước LegalEagle / CNBC: (1) Hành vi tưởng chừng vô hại ('Clicking I Agree seems harmless...') -> (2) Đòn lật tẩy bất ngờ ('until you realize what was signed...') -> (3) Bằng chứng số liệu giám sát quy mô lớn ('Fifteen hundred data points packaged and sold...') -> (4) Câu hỏi tu từ truy vấn trách nhiệm ('Who actually owns that sensitive information?') -> (5) Vạch trần bẫy pháp lý trong điều khoản chi tiết ('Hidden deep inside section fourteen... long before you read the fine print').
- **Long (`long_16x9`) Spine:** Cold open 0-30s: strongest scene of the video, no channel intro -> Stakes: why this matters to the viewer's own life -> 3-5 chapters, each opens with a mini-hook and ends with a re-hook -> Pattern interrupt every 20-30s (story, number, visual gag) -> Synthesis + practical takeaway -> Closing line pointing to the next video
- **Short (`short_9x16`) Spine:** Hook <= 3s: shocking claim or relatable pain + striking first frame -> Open loop: promise the answer, delay it -> Escalation beats every 2-5s (new visual, number or twist) -> Payoff: answer the loop in one clear image -> Closing line
- **20s Verbatim Rhythm Benchmark:** [00:00-00:03.5s] '...hundred dollar a year service, because that's the value of the data you're providing.' [pause 0.16s] -> [00:03.5-00:09.0s] 'If they use ten percent of that data, they're going to be the most valuable company ever.' [pause 0.41s] -> [00:09.0-00:11.5s] 'It was about taking your information.' [pause 0.15s] -> [00:11.5-00:17.0s] 'Companies that you've never heard of claim to have about fifteen hundred points of data on the average American citizen.' [pause 0.15s] -> [00:17.0-00:20.0s] 'Is it hard to go through it and actually find specific details?'

## 3. Hook Templates & Seed Topics
### Hook Templates
- The hidden clauses in everyday contracts that cost you thousands every year.
- Why security deposit and non-refundable fee mean completely different things.
- Subscription dark patterns: how apps make canceling intentionally confusing.
- What actually happens legally when someone sends money to the wrong account?

### Seed Topic Queue
- The Hidden Clauses in Everyday Contracts That Cost You Thousands Every Year
- Why Security Deposit and Non-Refundable Fee Mean Completely Different Things
- Subscription Dark Patterns: How Apps Make Canceling Intentionally Confusing
- What Actually Happens Legally When Someone Sends Money to the Wrong Account?
- 5 Lease Clauses You Should Always Check Before Signing an Apartment Contract
