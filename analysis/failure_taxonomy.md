# Failure taxonomy for the fixed-top-3 chunk-size experiment

This report lists the failures we can count directly from the saved outputs. A refusal on an answerable question counts as a wrong refusal, even when the model was being cautious because retrieval missed the evidence. Other incorrect answers and their causes will be added after we finish scoring independently.

| Automatically measurable category | 250-word baseline | 200-word candidate |
|---|---|---|
| wrong_refusal | 2 | 3 |
| source_hit_miss | 0 | 0 |
| invalid_citation | 0 | 0 |

250-word baseline correctness review: Pending (0 of 25 scored and settled). We still need to finish scoring before the list of incorrect answers is complete.

200-word candidate correctness review: Pending (0 of 25 scored and settled). We still need to finish scoring before the list of incorrect answers is complete.

## Category definitions

- wrong_refusal: answerable gold question, but the returned answerable flag is false. This follows the handout regardless of why the refusal happened.
- source_hit_miss: none of the expected documents appears among the three retrieved chunks. A source hit can still miss a necessary passage or another required document.
- invalid_citation: selected evidence IDs or quote/source string checks fail.
- incorrect_answer: the partners settle on correctness=0. Explain its cause in `partner_review/failure_review.csv`: for example, retrieval_miss, incomplete_answer, incorrect_fact, unsupported_claim, or other.

Category counts may overlap. A source miss need not cause an incorrect answer when equivalent evidence exists elsewhere. Refusal and correctness failures are different measurements. A reported zero in an automatic category does not imply zero unreviewed semantic errors.

## Worked examples of observed automatic categories

### wrong_refusal: candidate Q16

Question: Can AP credit satisfy the writing or quantitative reasoning requirements, and how does that differ from transferring a college course?

Expected answer: AP credit cannot satisfy these requirements. Eligible transferred college courses may satisfy quantitative reasoning and one writing requirement, but not the remaining two writing requirements or intercultural literacy.

Actual response: I am sorry, but the provided text does not contain sufficient information to fully answer the question. While it states that AP credits cannot be used to fulfill any Domain or Skills requirements, the information regarding how this differs for transfer courses is incomplete because the text cuts off at "Transfer credits may help students fulfill."

Retrieved chunk IDs: registrar-transfer-credits#7, registrar-transfer-credits#8, registrar-transfer-credits#0.

This is an observed wrong_refusal under the definition above. The saved row includes the full retrieved passages. Checking those passages will show whether the evidence was missing or whether the answer overlooked it.

source_hit_miss: no cases in this run.

invalid_citation: no cases in this run.

## Every automatically observed or partner-confirmed failed row

| Variant | Question | Categories | Partner cause notes |
|---|---|---|---|
| candidate | Q16 | wrong_refusal |  |
| baseline | Q19 | wrong_refusal |  |
| candidate | Q19 | wrong_refusal |  |
| baseline | Q20 | wrong_refusal |  |
| candidate | Q20 | wrong_refusal |  |
