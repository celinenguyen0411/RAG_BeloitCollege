## 2026-11-07 — Codex notebook implementation

- Tool/task: Codex read the project instructions, inspected the existing corpus and question files, and drafted the end-to-end `pipeline.ipynb` plus reproduction instructions.
- Output status: Implementation added for partner review; model download, full notebook execution, and live OpenAI answers remain unverified.
- Design: MiniLM embeddings, a NumPy cosine index, structured OpenAI answers, exact-quote validation, and a controlled top-3 versus top-5 comparison. Chunk size is capped by MiniLM's tokenizer limit to prevent silent truncation.
- Verification: All Python code cells passed syntax checks; actual input loading confirmed 22 corpus documents, 10 test questions, and 12 evaluation draft questions. Mocked generation checks accepted an exact quote, rejected a fabricated quote, and retained a refusal. These checks do not measure live answer quality.
- Issues caught: `analysis/evaluation_set.md` is empty; the draft is in `analysis/evaluation_questions`. Only three draft questions have source labels, and the lost-ID question cites quiet-hours while the student-ID corpus file is absent. No gold answers or labels were changed automatically.
- Human verification still needed: Read generated answers and supporting passages, correct the gold labels, complete the evaluation set, and review both variants before reporting results.

## 2026-11-07 — Citation validation fix

- Task: Investigate an answer replaced by `citation_status: invalid`.
- Finding: Saved notebook output confirms retrieval found room-change chunks and generation reached the citation check. The original model quote was discarded, so the exact failed citation cannot be recovered. Actual room-change text contains PDF ligatures (`ﬃ`, `ﬂ`) that reproduce false rejections when the model uses normal letters.
- Change: Normalize Unicode typography and whitespace on both sides of quote checks, clarify continuous-quote instructions, and preserve validation errors plus rejected responses. No fuzzy matching; invented text still fails.
- Verification: Reproduced a ligature mismatch against the real corpus and confirmed the corrected check accepts it. Confirmed fabricated text, unknown chunk IDs, empty quotes, and missing evidence remain rejected. All code cells pass syntax checks. No live API call was made for this fix.

## 2026-11-07 — Replace model-copied quotes with evidence selection

- Finding: The user's diagnostic response contains corrupted control characters inside the model-written quote. Unicode normalization cannot reconstruct those characters reliably. The earlier normalization fix did not resolve the reported failure.
- Change: Python numbers source sentences; OpenAI selects evidence IDs constrained by an enum. Python copies the corresponding original sentences directly into evidence. No fuzzy quote matching or automatic acceptance of untraceable quotes is used.
- Verification: Ran the complete generation function with a simulated API response and actual room-change corpus text. Selected sentences were returned as exact source substrings. Unknown IDs and absent evidence were rejected; refusal was retained. All notebook code cells pass syntax checks. Live API behavior was not tested in this change.
