# Content & Script Strategy — First Principles Ink (`en_first_principles`)

## 1. Standalone Packaging & V4 Short Funnel
- **Title Contract:** `youtube_title <= 55` characters. Strictly NO numbered prefixes (`P1:`, `Part 2:`, `Ep 3:`) on Shorts.
- **Funnel Twin:** Shares verified primary Fact Vault research with sibling channel `la_ban_hoc_thuat` (`./vp clone-en` / bilingual adaptation).
- **Short->Long Policy:** Declare `parent_long_id` when linked; place channel bridge + 2-choice debate question inside final `15%` (`youtube_closing_question` / pinned creator comment). Never say *"like/share/subscribe"*.
- **NotebookLM 3-Vault Grounding:** Compile verified primary sources into `fact_vault.json` via `sys/tools/notebooklm_vault.py` before drafting narration (`fact_grounding_linter.py --strict`).

## 2. Proven Narrative Spine (`Veritasium`)
- **Sentence Structure Formula:** Công thức 5 bước Veritasium: (1) Mệnh đề điều kiện thực nghiệm ('Hang a heavy spinning wheel...') -> (2) Phá vỡ trực giác thông thường ('Instead of crashing down, it floats...') -> (3) Câu hỏi tu từ ngắn 5-7 chữ ('Now, why doesn't it fall?') -> (4) Giải nghĩa nhân quả bằng từ chỉ hướng ('Because downward gravity pulls the axle...') -> (5) Quy luật tỷ lệ & kết cục tất yếu ('The faster it spins... until friction wins').
- **Long (`long_16x9`) Spine:** Cold open 0-30s: strongest scene of the video, no channel intro -> Stakes: why this matters to the viewer's own life -> 3-5 chapters, each opens with a mini-hook and ends with a re-hook -> Pattern interrupt every 20-30s (story, number, visual gag) -> Synthesis + practical takeaway -> Closing line pointing to the next video
- **Short (`short_9x16`) Spine:** Hook <= 3s: shocking claim or relatable pain + striking first frame -> Open loop: promise the answer, delay it -> Escalation beats every 2-5s (new visual, number or twist) -> Payoff: answer the loop in one clear image -> Closing line
- **20s Verbatim Rhythm Benchmark:** [00:00-00:04.8s] 'If I apply a force down on this side of the wheel, I create a torque.' [pause 0.45s] -> [00:05.3-00:10.2s] 'Now torque is force times the distance from the rotating axis, you could call it r.' [pause 0.40s] -> [00:10.6-00:15.0s] 'So torque is the force applied times the radius away from the turning axis.' [pause 0.60s] -> [00:15.6-00:17.4s] 'Now what's the direction of that torque?' [pause 0.44s] -> [00:17.8-00:20.0s] 'Well, we actually use a right-hand rule to define this.'

## 3. Hook Templates & Seed Topics
### Hook Templates
- The Prisoner's Dilemma: why being purely selfish backfires in the long run.
- Survivorship bias: the WWII airplane bullet holes everyone misunderstood.
- Goodhart's Law: what happens when a measure becomes the target.
- Second-order thinking: how great strategists see three moves ahead.

### Seed Topic Queue
- The Prisoner's Dilemma: Why Being Selfish Always Backfires in the Long Run
- Survivorship Bias: The WWII Plane Bullet Holes Everyone Misunderstood
- Goodhart's Law: What Happens When a Measure Becomes a Target
- Second-Order Thinking: How Great Strategists See Three Moves Ahead
- The Cobra Effect: Why Well-Intentioned Solutions Make Problems Worse
