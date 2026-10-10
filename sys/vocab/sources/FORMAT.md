# Vocabulary Source File Format

Each file represents a topic, named after its corresponding `id` in `vocab/topics.json`.
Each line defines ONE SENSE of a word:

```
word|pos|vietnamese_meaning|cefr[|sense_key]
```

- `word`: lowercase (`take`, `look after`, `ice cream`); capitalized only for acronyms (`ATM`, `GDP`).
- `pos`: n, v, adj, adv, prep, conj, pron, det, phr, num, int.
- `vietnamese_meaning`: concise Vietnamese definition/gloss, exactly one sense, no examples, no `|` separator.
- `cefr`: CEFR level: A1, A2, B1, B2, C1.
- `sense_key` (column 5, optional): lowercase/hyphenated identifier, mandatory when the same `word|pos`
  appears multiple times with different senses — each sense forms an individual entry and video.

Example of sense separation:

```
bank|n|ngân hàng|A2|finance
bank|n|bờ sông|B1|river
```

Lines starting with `#` are comments. `python3 vocab/bank.py build` blocks execution if syntax is invalid,
CEFR level is unrecognized, or duplicate `word|pos` occurs without a distinct sense key.
