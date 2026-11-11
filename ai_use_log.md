# AI-use log

I used Codex to help with the notebook, debugging, evaluation setup, and writing. The extractor and original Vertex pipeline came from the instructor. The notes below record what was used, what needed changing, and how it was checked. They do not count as either partner's independent correctness scores.

## Earlier work

This summary was added on November 11 from the work recorded in this chat.

- Codex first helped build a MiniLM/OpenAI notebook. The project later moved to Vertex. The early notebook was checked for syntax and input loading; the final Vertex notebook was also run.
- I already had 25 draft questions. Codex helped format them for the evaluator, choose evidence excerpts, and adjust some source labels. The excerpts were checked against the saved text. We still need to verify that each expected answer is right.
- The first citation fix was not enough. PDF ligatures and corrupted characters made model-copied quotes fail the check. We changed the system so the model selects sentence IDs and Python copies the source text. Tests check missing IDs, wrong sources, and invented quotations.
- We initially compared three retrieved passages with five. After reading the metrics handout, we replaced that comparison with 250-word versus 200-word chunks, keeping retrieval at three and overlap at 50 words. The final run saved 50 outputs with the same questions, models, and prompt.
- Missing source snapshots were recovered from Git history, and the supplied extractor produced the missing student-ID document. The source audit checks that all listed documents and snapshots exist and that their checksums match.
- I asked Codex for suggested scores, then removed those optional files. They were not entered as my scores or Parker's scores. We still need to complete the two independent scoring sheets and discuss disagreements.
- Codex also helped draft and simplify the documentation. Report counts come from the saved outputs, and correctness stays pending while the required human scoring is unfinished.

## November 11: getting the working version consistent

I asked to keep the instructor's `pipeline.py` original. The working implementation was moved to `rag_pipeline.py`, and the notebook, evaluator, and tests were updated to use it. An executable-code comparison confirmed that the moved version matches the saved experiment; only example command names in its opening description changed.

Codex found that the older metrics script could search the whole prompt for a quote. It was changed to check the claimed retrieved passage instead. The script now preserves matching existing grades when refreshing its CSV. All 25 older scores were kept, separately from the final chunk-size experiment.

The 18 tests passed, including checks for a wrong source, a quote appearing only in the question, and score preservation. The source audit passed for 23 documents and 25 questions. All six notebook code cells ran successfully with Vertex, using cached embeddings and one example answer. The full 50-answer comparison was not repeated for that check.

## November 11: cleanup and writing scope

I asked for a simpler project folder, but clarified that Parker's work should be left alone. The older evaluation files removed during the last cleanup were restored, including the grading sheet and its scores. Git history was checked, and I confirmed that further wording edits should be limited to `README.md`, this log, `pipeline.ipynb`, and my 25-question draft.

The current wording pass changes explanations and formatting only. It leaves the notebook code and outputs, question text, expected answers, source evidence, and scoring records unchanged. No commit or push was made for these edits.
