# Scoring our answers

The assignment asks us to score correctness separately, then compare our results. There are 25 questions and two chunk sizes, so each of us has 50 answers to review.

## Our own scores

Open your file in the final run's `partner_review` folder:

- Mai uses `mai_scores.csv`.
- Parker uses `parker_scores.csv`.

Read the question, expected answer, generated answer, and supporting passages. Put 1 or 0 in `correct`, add your name in `reviewer`, and use `notes` to explain a difficult decision. Finish your own sheet before looking at the other person's scores.

Use 1 if the answer gives the same facts as the expected answer and keeps any conditions that change its meaning. Different wording is fine. Use 0 if it gives a wrong fact, leaves out an important condition, or avoids answering. A real citation does not automatically make an answer correct.

For a question the corpus cannot answer, refusing without making up personal information is correct. Refusing a question the corpus can answer is incorrect, even if retrieval missed the right passage. The refusal count uses the returned `model_answerable` flag; a vague answer with that flag set to true is not counted as a refusal.

Keep the saved questions and model answers unchanged. Only fill in the scoring fields.

## Compare our scores

Once we have both finished, run:

```bash
python scripts/reconcile_scores.py
```

If we gave the same score, there is nothing to resolve. If we disagree, read the answer and source together, discuss it, and fill in that row of `consensus.csv`:

- `consensus_score`: the agreed 0 or 1.
- `resolution_notes`: why we chose it.
- `confirmed_by`: Mai and Parker.

The consensus sheet is only for disagreements. Both independent scores are still needed. Leave anything unresolved blank rather than guessing; correctness will stay pending until every answer is settled.

## Explain the failures

For incorrect answers, add a cause and a short explanation in `failure_review.csv`. Useful causes are `retrieval_miss`, `incomplete_answer`, `incorrect_fact`, `unsupported_claim`, `invalid_citation`, or `other`. Use semicolons if more than one applies.

For example, retrieval may find a guest policy but miss the passage explaining how to resolve a roommate conflict. An answer can also find the right passage but leave out an exception. Those are different problems, so the explanation matters.

Wrong refusals are counted automatically for every answerable question the model refuses. We still explain whether missing evidence caused the refusal; we do not remove it from the count.

After updating the scores and explanations, refresh the written reports:

```bash
python scripts/build_reports.py
```

The two personal score sheets, the disagreement sheet, and the failure notes support the assignment's scoring and failure-analysis requirements. They are working records, not extra experiments.
