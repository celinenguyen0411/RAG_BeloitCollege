# RAG Pipeline Evaluation Set

## 1. Evaluation Metrics Summary

| Metric | Score | Description |
| :--- | :--- | :--- |
| **Hit Rate** | **20 of 21** | Expected document retrieved in top-3 chunks for answerable questions. |
| **Quote Fidelity** | **18 of 25** | Returned quotes that verifiably exist in the source context chunk. |
| **Correct Refusals** | **4 of 4** | Out-of-corpus/unanswerable questions correctly refused by the system. |
| **Wrong Refusals** | **3 of 21** | Answerable questions incorrectly refused by the system. |
| **Correctness** | **[X of 25]** | Generated answers matching the human gold key upon manual verification. |

---
## 2. Methodology & Scoring Decisions
* **Retrieval Depth ($k=3$):** Hit rate checks if the expected source file appears within the top 3 vector matches.
* **Quote Verification:** Executed programmatically using case-insensitive normalized string matching against context chunks.
* **Refusal Rules:** Refusals are recorded when `answerable` returns `False`. Hedged text with `answerable: True` is scored as an incorrect answer rather than a refusal.
* **Correctness Scoring:** Evaluated manually via peer cross-verification comparing pipeline answers against target gold answers.

---
## 3. Gold Dataset & Pipeline Results

| # | Question | Expected Doc | Top 3 Retrieved | Answerable | Hit | Quote Verified | Refusal Status | Correctness |
|---|---|---|---|---|---|---|---|---|
| 1 | Roommate conflict steps | handbook-room-changes | handbook-room-changes | True | 1 | 1 | Normal | 1 |
| 2 | Quiet hours policy | handbook-quiet-hours | handbook-quiet-hours | True | 1 | 1 | Normal | 1 |
| 3 | Overnight guest limits | handbook-overnight-guests | handbook-overnight-guests | True | 1 | 1 | Normal | 1 |
| 4 | Housing & meal requirements | handbook-residency | handbook-residency | True | 1 | 1 | Normal | 1 |
| 5 | Lockout procedure | handbook-lockout | handbook-lockout | True | 1 | 1 | Normal | 1 |
| 6 | Room key replacement | handbook-lockout | handbook-lockout | True | 1 | 1 | Normal | 1 |
| 7 | Lost ID replacement | handbook-quiet-hours | handbook-quiet-hours | True | 1 | 1 | Normal | 1 |
| 8 | Meal refund without ID | handbook-quiet-hours | handbook-quiet-hours | True | 1 | 1 | Normal | 1 |
| 9 | Parking & unpaid tickets | handbook-vehicle-parking | handbook-vehicle-parking | True | 1 | 1 | Normal | 1 |
| 10 | Summer hold resolution | handbook-account-holds | handbook-account-holds | True | 1 | 1 | Normal | 1 |
| 11 | Repeat course policy | catalog-grading-policy | catalog-grading-policy | True | 1 | 1 | Normal | 1 |
| 12 | Incomplete grade rules | catalog-grading-policy | catalog-grading-policy | True | 1 | 1 | Normal | 1 |
| 13 | Course drop after week 1 | registrar-registration | registrar-registration | True | 1 | 1 | Normal | 1 |
| 14 | Graduation unit/GPA limits | registrar-graduation-requirements | catalog-biology | False | 0 | 0 | Wrong Refusal | 0 |
| 15 | Double counting units | catalog-data-science | catalog-data-science | True | 1 | 1 | Normal | 1 |
| 16 | AP credit vs transfer | registrar-transfer-credits, registrar-graduation-requirements | registrar-transfer-credits | True | 1 | 1 | Normal | 1 |
| 17 | Off-campus Q requirement | registrar-transfer-credits | registrar-transfer-credits | True | 1 | 1 | Normal | 1 |
| 18 | Petitioning for a WP grade | registrar-registration, catalog-grading-policy | registrar-registration | True | 1 | 1 | Normal | 1 |
| 19 | DS & Econ seminar rules | catalog-data-science, catalog-econ-requirements | catalog-econ-courses, catalog-data-science | False | 1 | 0 | Wrong Refusal | 0 |
| 20 | 4-night guest dispute | handbook-overnight-guests, handbook-room-changes | handbook-quiet-hours, handbook-overnight-guests | False | 1 | 0 | Wrong Refusal | 0 |
| 21 | ESA vs pet cat policy | handbook-overnight-guests, handbook-emotional-support-animals | handbook-emotional-support-animals | True | 1 | 1 | Normal | 1 |
| 22 | Personal fin-aid award | "" | N/A | False | 0 | 0 | Correct Refusal | 1 |
| 23 | Personal room assignment | "" | N/A | False | 0 | 0 | Correct Refusal | 1 |
| 24 | Current DSDA 310 grade | "" | N/A | False | 0 | 0 | Correct Refusal | 1 |
| 25 | Quiet hours complainants | "" | N/A | False | 0 | 0 | Correct Refusal | 1 |