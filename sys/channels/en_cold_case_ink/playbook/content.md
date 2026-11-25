# Content & Script Strategy — Cold Case Ink (`en_cold_case_ink`)

## 1. Standalone Packaging & V4 Short Funnel
- **Title Contract:** `youtube_title <= 55` characters. Strictly NO numbered prefixes (`P1:`, `Part 2:`, `Ep 3:`) on Shorts.
- **Funnel Twin:** Shares verified primary Fact Vault research with sibling channel `ho_so_ky_la` (`./vp clone-en` / bilingual adaptation).
- **Short->Long Policy:** Declare `parent_long_id` when linked; place channel bridge + 2-choice debate question inside final `15%` (`youtube_closing_question` / pinned creator comment). Never say *"like/share/subscribe"*.
- **NotebookLM 3-Vault Grounding:** Compile verified primary sources into `fact_vault.json` via `sys/tools/notebooklm_vault.py` before drafting narration (`fact_grounding_linter.py --strict`).

## 2. Proven Narrative Spine (`LEMMiNO`)
- **Sentence Structure Formula:** Công thức 5 bước LEMMiNO: (1) Mốc thời gian và không gian lịch sử cụ thể ('Before dawn in Victorian London...') -> (2) Hành động đời thường của người chứng kiến ('a resident stepped into the silent alley...') -> (3) Phát hiện rùng rợn phá vỡ sự tĩnh lặng ('On the landing lay an unmoving silhouette...') -> (4) Câu hỏi tu từ truy vấn dấu vết biến mất ('Who vanished so cleanly into the fog?') -> (5) Tổng kết điều tra pháp y và sự bế tắc của các manh mối ('red thread ties five separate crime scenes... yet the shadow remains forever unsolved').
- **Long (`long_16x9`) Spine:** Cold open 0-30s: strongest scene of the video, no channel intro -> Stakes: why this matters to the viewer's own life -> 3-5 chapters, each opens with a mini-hook and ends with a re-hook -> Pattern interrupt every 20-30s (story, number, visual gag) -> Synthesis + practical takeaway -> Closing line pointing to the next video
- **Short (`short_9x16`) Spine:** Hook <= 3s: shocking claim or relatable pain + striking first frame -> Open loop: promise the answer, delay it -> Escalation beats every 2-5s (new visual, number or twist) -> Payoff: answer the loop in one clear image -> Closing line
- **20s Verbatim Rhythm Benchmark:** [00:00-00:03.5s] '...when an upstairs tenant named John Reeves headed out for work.' [pause 1.50s] -> [00:05.0-00:11.5s] 'Upon reaching the first floor landing, Reeves encountered the body of a woman lying upon her back in a pool of blood.' [pause 2.50s] -> [00:14.0-00:17.5s] 'Horrified by the sight, he stumbled down to the street below in search for help.' [pause 0.50s] -> [00:18.0-00:20.0s] 'At four forty-five in the morning, the mystery began.'

## 3. Hook Templates & Seed Topics
### Hook Templates
- The Dyatlov Pass incident: how avalanche physics solved the 1959 mystery.
- Why did the Mary Celeste crew abandon a perfectly safe ship full of food?
- The Flannan Isles lighthouse: what happened to the three keepers in 1900?
- The Dancing Plague of 1518: mass hysteria or ergot poisoning?

### Seed Topic Queue
- The Dyatlov Pass Incident: How Avalanche Physics Solved the 1959 Mystery
- Why Did the Mary Celeste Crew Abandon a Perfectly Safe Ship Full of Food?
- The Flannan Isles Lighthouse: What Happened to the Three Keepers in 1900?
- The Dancing Plague of 1518: Mass Hysteria or Ergot Poisoning?
- The Tunguska Event: How an Airburst Flattened 800 Square Miles Without a Crater
