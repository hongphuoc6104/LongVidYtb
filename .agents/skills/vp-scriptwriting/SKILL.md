---
name: vp-scriptwriting
description: Transform formal, written or machine-translated video scripts into natural, engaging, spoken conversational storytelling (văn nói, văn kể) for Video Pilot explainers. Integrates narrative pacing, conversational hooks, breathing pauses, and rhythm-matched speech synthesis.
---

# VP Scriptwriting — Spoken Storytelling & Conversational Narration Skill

`vp-scriptwriting` is the core skill and guideline for authoring, evaluating, and transforming video scripts in Video Pilot. It bridges the gap between formal written documentation ("văn viết trang trọng") and captivating spoken storytelling ("văn nói, văn kể"), ensuring the audience feels as though an insightful friend is guiding them through an immersive journey.

---

## 1. Core Mission & Psychological Anchor

- **The Voice Archetype**: The **Conversational Explorer** (Người bạn đồng hành khám phá). Not a university lecturer reading a textbook, nor an over-hyped commercial voiceover. The narrator speaks with quiet curiosity, dry wit, rhythmic suspense, and deep empathy.
- **The Core Listener Test**: If read aloud, does it sound like someone speaking to you across a coffee table, or does it sound like a translated Wikipedia entry? If it sounds like a translation, it fails.
- **Invariant**: **100% Factual & Vocabulary Fidelity**. Never omit technical terms, historical dates, scientific figures, or essential concepts. Transform *how* they are told, never *what* is told.

---

## 2. Anatomy of the Reference Script (Why the Original English Works)

Analyzing top-performing explainer scripts (e.g., *Ancient Humans: The Mystery of Time*):

1. **Intimate Personal Opening (The Hook)**:
   - *Example*: *"This morning, a machine yelled at you until you woke up. You silenced her."*
   - *Technique*: Personification of daily objects ("machine yelled at you"), short active clauses (3–4 words), immediate connection to the viewer's morning routine.
2. **Juxtaposition & Contrast**:
   - Compares the modern 40-hour work week and constant alarm anxiety with a 50,000-year-old human waking up naturally with the sunrise.
   - Pits two ancient skeletons against each other: healthy hunter-gatherer vs broken farmer.
3. **Conversational Turn & Suspension**:
   - *"And here's the part nobody tells you..."*
   - *"Because the best hours of the day haven't even begun yet."*
   - *"So who is who? Take a guess."*
   - These markers interrupt monotone delivery, reset listener attention, and create micro-cliffhangers.
4. **Circular Closure (Payoff)**:
   - Ends by re-framing the opening metaphor: *"That alarm ringing this morning? That's just the latest bill coming due."*

---

## 3. The Spoken Vietnamese Translation Rubric ("Văn Nói, Văn Kể")

When translating or adapting English reference material into Vietnamese, direct translation often falls into "văn viết hàn lâm" (stiff academic writing). Use the following conversion principles:

| Formal Written Trap ("Văn viết trang trọng") | Natural Spoken Storytelling ("Văn nói, văn kể") | Why it works |
|---|---|---|
| *"Để trả lời câu hỏi đó, chúng ta phải bắt đầu từ..."* | *"Muốn hiểu được điều này, chúng ta phải nhìn sâu vào lòng đất..."* | Replaces formal infinitive with active spoken curiosity. |
| *"Ngày của bạn đã bị định sẵn: bạn phải đi đâu, làm gì..."* | *"Từ giây phút đó, ngày hôm nay của bạn coi như đã bị sắp đặt xong xuôi..."* | Natural Vietnamese cadence ("coi như đã... xong xuôi"). |
| *"Bao nhiêu giờ thuộc về kẻ khác."* | *"Bao nhiêu tiếng đồng hồ phải cày cuốc cho người khác."* | Vivid, relatable human reality over cold literal phrasing. |
| *"Bộ xương thứ hai kể một câu chuyện nghiệt ngã hơn..."* | *"Thế nhưng, bộ xương thứ hai lại kể một câu chuyện cay đắng hơn nhiều..."* | Conversational conjunction + emotional nuance. |
| *"Những giờ quan trọng nhất không phải là lúc săn bắn..."* | *"Nhưng đây mới là điều bất ngờ mà ít ai để ý: khoảng thời gian quý giá nhất..."* | Conversational revelation hook ("Đây mới là điều..."). |
| *"Tiếng chuông báo thức chỉ là hóa đơn thanh toán gần nhất."* | *"Tiếng chuông réo inh ỏi sáng nay của bạn, thật ra chỉ là tờ hóa đơn mới nhất..."* | Sensory sound ("réo inh ỏi") + conversational particle ("thật ra chỉ là"). |

### Rules for Spoken Vietnamese:
1. **Clause Length**: Keep clauses between 6 and 14 syllables. Never write run-on sentences exceeding 25 syllables without a breathing pause (comma or period).
2. **Conversational Discourse Markers**: Use natural transitions: *"Thế nhưng...", "Hóa ra...", "Bạn có tin không...", "Hãy thử ngẫm lại xem...", "Và rồi..."*
3. **Avoid Passive Stiff Phrasing**: Avoid clumsy passive voice (*"được thực hiện bởi"*, *"đã bị định trước"*). Use active agent-centered phrasing (*"người ta đã...", "chúng ta bị cuốn vào..."*).
4. **Punctuation as Breath Control**: Commas (`,`) denote a 0.3s breath; periods (`.`) denote a 0.5s–0.7s beat reset; em dashes (`—`) or ellipses (`...`) denote dramatic pauses (0.8s–1.0s).

---

## 4. Audio Pacing & TTS Configuration

- **Speech Rate**: 3.2 – 3.8 syllables per second. Natural storytelling needs space for ideas to settle.
- **Voice Recommendation**:
  - `vi-VN-NamMinhNeural` (natural masculine storytelling timbre, smooth inflections).
  - Recommended rate tuning: `+12%` to `+18%` for energetic explainers, `+0%` to `+8%` for contemplative history/philosophy.
- **Scene Pacing Breakdown**:
  - **Hook / Opening**: 1.5s – 2.0s per shot. High visual dynamic.
  - **Exposition / Setup**: 2.0s – 3.0s per shot.
  - **Climax / Key Contrast**: 1.5s – 2.2s per shot.
  - **Philosophical Takeaway / Outro**: 2.5s – 3.2s per shot with calm, lingering transitions.

---

## 5. Pipeline Integration Workflow

When drafting or editing a video chapter:
1. **Analyze Core English / Outline**: Extract core facts, vocabulary terms, and dramatic arc.
2. **Author Spoken Dialogue**: Apply the Spoken Vietnamese Rubric. Read each sentence aloud at natural speaking tempo.
3. **Generate TTS Audio**: Synthesize narration WAV and measure total duration.
4. **Align Timeline & Sub-beats**: Match scene cues and image switch timings (`cues` and `scenesByAspect`) to speech cadences so image cuts hit natural stressed words or sentence pauses.
5. **Verify Audio Quality**: Ensure zero word clipping, zero unnatural pauses (>1.5s), and LUFS target of -14.0 LUFS.
