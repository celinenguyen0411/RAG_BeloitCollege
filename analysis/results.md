# Chunk-size experiment results

We compared 250-word chunks with 200-word chunks, retrieving **three chunks in both versions**. 50 generated outputs are saved for 25 gold questions. We still need to finish our separate correctness scores before comparing accuracy.

We originally tried changing the number of retrieved passages. After reading the metrics handout, we kept retrieval at three and compared chunk sizes instead. These results use only that final experiment; the earlier work is recorded in `ai_use_log.md`.

## Controlled setup

Chunk size is the only setting we changed. Baseline: 250 words, 179 chunks. Candidate: 200 words, 235 chunks. Both use the same 23 frozen documents, 50-word overlap, three retrieved chunks, `text-embedding-005` document/query embeddings, `gemini-3.5-flash` answer model, prompt, response schema, temperature zero, and 25 gold questions. Both indexes exceed 150 chunks. The identical query embedding for a question is searched against the two separately chunked indexes.

We kept the overlap at 50 words. That makes overlap a larger share of a 200-word chunk than a 250-word chunk. Smaller chunks also move the boundaries, so a sentence that fits in one version may be split in the other.

The run is `analysis/vertex_runs/b88ba8fa865a`. `settings.json` records package versions, model regions, input/code fingerprints and the run timestamp. `results.json` preserves generated answers, full retrieved text, selected evidence, and answerability flags. The two chunk maps are saved separately. The working code now lives in `rag_pipeline.py` so the instructor’s `pipeline.py` can stay original; `implementation_provenance.json` records the move without changing the saved experiment. API errors remaining in this completed run: 0.

## The five required numbers

| Required metric | 250-word baseline, k=3 | 200-word candidate, k=3 |
|---|---|---|
| Hit rate | 21 of 21 | 21 of 21 |
| Quote fidelity — quoted answers | 19 of 19 | 18 of 18 |
| Correctness — both partners | Pending (0 of 25 scored and settled) | Pending (0 of 25 scored and settled) |
| Correct refusals | 4 of 4 | 4 of 4 |
| Wrong refusals | 2 of 21 | 3 of 21 |

## Observed changes

Q16: Can AP credit satisfy the writing or quantitative reasoning requirements, and how does that differ from transferring a college course?

250 words — answerable=True: AP credits cannot be used to fulfill any Domain or Skills requirements. In contrast, transfer credits from other institutions can help students fulfill requirements in Beloit's "5 Domains and 5 Skills."

200 words — answerable=False: I am sorry, but the provided text does not contain sufficient information to fully answer the question. While it states that AP credits cannot be used to fulfill any Domain or Skills requirements, the information regarding how this differs for transfer courses is incomplete because the text cuts off at "Transfer credits may help students fulfill."

One version answered and the other refused. We can count that difference now, but both responses still need our independent correctness scores.


## Definitions and scoring

- Hit rate: among the 21 answerable gold questions, the number with an expected document among the three retrieved chunks. For questions with several expected documents, this is an any-source hit, not proof that every required passage was retrieved. Q07/Q08 accept either student-ID or quiet-hours because both contain the same lost-ID policy.
- Quote fidelity: among answers returning evidence, how many have every quote in its claimed retrieved chunk. The code uses exactly `" ".join((s or "").lower().split())`; no Unicode/punctuation normalization or fuzzy matching is used in this check. The source-ID match is checked too. Quotes are copied by Python from the selected evidence IDs, but still pass the prescribed string search.
- Correctness: among all 25 gold questions, how many match the facts and material conditions of the reference answer. Different wording is accepted. Mai and Parker score independently, then discuss disagreements. Blank or unilateral scores cannot become final correctness; AI scores are not used.
- Correct refusals: among the four unanswerable questions, the number with returned `answerable=false` (stored as `model_answerable` to avoid confusing it with the gold label).
- Wrong refusals: among the 21 answerable questions, the number with returned `answerable=false`, including refusals caused by retrieval misses. A vague answer with `answerable=true` is not a refusal and must instead be considered during correctness scoring.

The metric definitions also appear in `analysis/evaluation_set.md` as required. Counts include their denominators. Partner scoring instructions are in `analysis/review_rubric.md`.

## Quote-fidelity denominator ambiguity

The handout defines quote fidelity over answers returning quotes, but its example code prints a denominator of all gold questions. Both are reported explicitly below. With several quotes per answer, the primary per-answer metric requires all selected quotes to match; the supplemental individual-quote count is also included.

| Supplemental count | 250 words | 200 words |
|---|---|---|
| Answers with verified quotes / all questions | 19 of 25 | 18 of 25 |
| Individual quotes matching their source | 57 of 57 | 52 of 52 |

## What can and cannot be concluded

The automatic counts tell us whether retrieval found an expected document, whether quotes match, and when the system refused. They do not tell us whether every answer is right. A retrieved document can contain the wrong section, and a genuine quote can accompany an incomplete answer. We will compare accuracy after both partners finish scoring.

This test uses 25 questions drawn from documents already familiar to the project, with AI help in drafting the gold set. It is a small test, not proof of performance on unfamiliar questions. Some files overlap or include neighboring policies, and chunk boundaries can split sentences. The same evidence may appear in more than one file. The expected answers were never sent to the answer model, and the questions and source documents stayed fixed. Future model responses may still vary at temperature zero.

See `analysis/failure_taxonomy.md` for automatically observable failures and the distinction between those counts and pending correctness judgments. No corpus, prompt, model, or overlap setting was changed to improve a condition mid-experiment.
