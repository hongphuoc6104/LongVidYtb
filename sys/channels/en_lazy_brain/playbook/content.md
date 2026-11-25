# Content & Script Strategy — Lazy Brain Lab (`en_lazy_brain`)

## 1. Standalone Packaging & V4 Short Funnel
- **Title Contract:** `youtube_title <= 55` characters. Strictly NO numbered prefixes (`P1:`, `Part 2:`, `Ep 3:`) on Shorts.
- **Funnel Twin:** Shares verified primary Fact Vault research with sibling channel `nao_luoi` (`./vp clone-en` / bilingual adaptation).
- **Short->Long Policy:** Declare `parent_long_id` when linked; place channel bridge + 2-choice debate question inside final `15%` (`youtube_closing_question` / pinned creator comment). Never say *"like/share/subscribe"*.
- **NotebookLM 3-Vault Grounding:** Compile verified primary sources into `fact_vault.json` via `sys/tools/notebooklm_vault.py` before drafting narration (`fact_grounding_linter.py --strict`).

## 2. Proven Narrative Spine (`Kurzgesagt / Huberman Lab`)
- **Sentence Structure Formula:** Công thức thần kinh học hành vi Huberman: (1) Trừ khử ảo tưởng thiếu ý chí ('You think you lack willpower') -> (2) Quy chuẩn hóa sinh khách quan ('brain is executing chemistry') -> (3) Xung đột dopamine giá rẻ ('Every cheap dopamine spike trains neurons') -> (4) Hệ quả lệch ngưỡng phần thưởng ('demand more reward for less work') -> (5) Câu hỏi tu từ cảm giác kháng cự ('Why does real effort feel so painful?') -> (6) Cơ chế điều hòa giảm thụ thể ('flooded receptors dial down sensitivity') -> (7) Giao thức hành động vi mô ('Wait ninety seconds before giving in') -> (8) Đích đến phục hồi mạch tập trung ('focus circuits instantly recover').
- **Long (`long_16x9`) Spine:** Cold open 0-30s: strongest scene of the video, no channel intro -> Stakes: why this matters to the viewer's own life -> 3-5 chapters, each opens with a mini-hook and ends with a re-hook -> Pattern interrupt every 20-30s (story, number, visual gag) -> Synthesis + practical takeaway -> Closing line pointing to the next video
- **Short (`short_9x16`) Spine:** Hook <= 3s: shocking claim or relatable pain + striking first frame -> Open loop: promise the answer, delay it -> Escalation beats every 2-5s (new visual, number or twist) -> Payoff: answer the loop in one clear image -> Closing line
- **20s Verbatim Rhythm Benchmark:** [00:00-00:03.0s] 'As you know that after eating, you will feel good.' [pause 0.50s] -> [00:03.5-00:07.5s] 'In other words, it makes the activity of eating pleasurable and memorable,' [pause 0.55s] -> [00:08.0-00:11.5s] 'so you would want to do it again and again whenever you feel hungry.' [pause 0.85s] -> [00:12.4-00:15.4s] 'The brain consists of billions of neurons or nerve cells,' [pause 0.51s] -> [00:15.9-00:20.0s] 'which communicate via neurotransmitters across microscopic synapses.'

## 3. Hook Templates & Seed Topics
### Hook Templates
- Why your brain loves procrastinating on goals that actually matter to you.
- You are not lazy. Your prefrontal cortex is simply stuck in a loop.
- The 2-minute dopamine rule that breaks doomscrolling immediately.
- Why does cleaning your desk feel urgent only when a deadline hits?

### Seed Topic Queue
- Why Your Brain Loves Procrastinating on Important Goals (And How to Trick It)
- The 2-Minute Dopamine Reset That Stops Doomscrolling Instantly
- Why Perfectionism Paralyzes Your Prefrontal Cortex
- Revenge Bedtime Procrastination: Why You Stay Awake at 2 AM
- How Micro-Habits Bypass Your Brain's Threat Detector
