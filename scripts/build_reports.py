import csv,json,sys
from pathlib import Path
from collections import Counter
from partner_scoring import reconcile,correctness_metric
ROOT=Path(__file__).resolve().parents[1]
run=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/(ROOT/'analysis/final_vertex_run.txt').read_text().strip()
status=json.loads((run/'status.json').read_text())
settings=json.loads((run/'settings.json').read_text())
rows=json.loads((run/'results.json').read_text())
if not status.get('complete') or settings.get('retrieval_only') or any(r.get('api_error') for r in rows):
    raise SystemExit('Final reports require a complete end-to-end run with no unresolved request errors.')
if settings.get('k')!=3 or 'conditions' not in settings:
    raise SystemExit('This reporter requires the fixed-k=3 chunk-size experiment. Older top-k reports are archived.')
summary={s['variant']:s for s in json.loads((run/'summary.json').read_text())}
scored=reconcile(rows,run)
for variant in summary:summary[variant]['correctness']=correctness_metric(scored,variant)
(run/'required_metrics.json').write_text(json.dumps(list(summary.values()),indent=2)+'\n')
(run/'correctness_reconciliation.json').write_text(json.dumps(scored,indent=2)+'\n')
labels={'baseline':'250-word baseline','candidate':'200-word candidate'}
def count(metric):
    if metric['numerator'] is None:
        return f"Pending ({metric.get('scored_questions',0)} of {metric['denominator']} scored and settled)"
    return f"{metric['numerator']} of {metric['denominator']}"
def pair(name):return [count(summary[v][name]) for v in ['baseline','candidate']]
rel=run.relative_to(ROOT)
conditions=settings['conditions']
headline=('We still need to finish our separate correctness scores before comparing accuracy.'
          if any(summary[v]['correctness']['numerator'] is None for v in summary)
          else 'The correctness counts come from our separate scores after resolving disagreements.')
report=f'''# Chunk-size experiment results

We compared 250-word chunks with 200-word chunks, retrieving **three chunks in both versions**. {len(rows)} generated outputs are saved for {len(rows)//2} gold questions. {headline}

We originally tried changing the number of retrieved passages. After reading the metrics handout, we kept retrieval at three and compared chunk sizes instead. These results use only that final experiment; the earlier work is recorded in `ai_use_log.md`.

## Controlled setup

Chunk size is the only setting we changed. Baseline: 250 words, {conditions['baseline']['chunk_count']} chunks. Candidate: 200 words, {conditions['candidate']['chunk_count']} chunks. Both use the same {settings['document_count']} frozen documents, 50-word overlap, three retrieved chunks, `{settings['embedding_model']}` document/query embeddings, `{settings['answer_model']}` answer model, prompt, response schema, temperature zero, and 25 gold questions. Both indexes exceed 150 chunks. The identical query embedding for a question is searched against the two separately chunked indexes.

We kept the overlap at 50 words. That makes overlap a larger share of a 200-word chunk than a 250-word chunk. Smaller chunks also move the boundaries, so a sentence that fits in one version may be split in the other.

The run is `{rel}`. `settings.json` records package versions, model regions, input/code fingerprints and the run timestamp. `results.json` preserves generated answers, full retrieved text, selected evidence, and answerability flags. The two chunk maps are saved separately. The working code now lives in `rag_pipeline.py` so the instructor’s `pipeline.py` can stay original; `implementation_provenance.json` records the move without changing the saved experiment. API errors remaining in this completed run: {sum(s['api_errors'] for s in summary.values())}.

## The five required numbers

| Required metric | 250-word baseline, k=3 | 200-word candidate, k=3 |
|---|---|---|
'''
for title,name in [('Hit rate','hit_rate'),('Quote fidelity — quoted answers','quote_fidelity'),('Correctness — both partners','correctness'),('Correct refusals','correct_refusals'),('Wrong refusals','wrong_refusals')]:
    a,b=pair(name);report+=f'| {title} | {a} | {b} |\n'
# Show actual per-question changes, without inventing a correctness judgment.
lookup={(r['variant'],r['question_id']):r for r in rows}
changed=[]
for qid in sorted({r['question_id'] for r in rows}):
    a,b=lookup[('baseline',qid)],lookup[('candidate',qid)]
    if a['hit']!=b['hit'] or a['model_answerable']!=b['model_answerable']:
        changed.append((a,b))
report+='\n## Observed changes\n\n'
if not changed:
    report+='No per-question hit or refusal flags changed. This does not establish equal correctness.\n'
for a,b in changed:
    report+=f"{a['question_id']}: {a['question']}\n\n250 words — answerable={a['model_answerable']}: {a['answer']}\n\n200 words — answerable={b['model_answerable']}: {b['answer']}\n\nOne version answered and the other refused. We can count that difference now, but both responses still need our independent correctness scores.\n\n"
report+='''
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
'''
for title,name in [('Answers with verified quotes / all questions','quote_fidelity_all_questions'),('Individual quotes matching their source','individual_quote_matches')]:
    a,b=pair(name);report+=f'| {title} | {a} | {b} |\n'
report+='''
## What can and cannot be concluded

The automatic counts tell us whether retrieval found an expected document, whether quotes match, and when the system refused. They do not tell us whether every answer is right. A retrieved document can contain the wrong section, and a genuine quote can accompany an incomplete answer. We will compare accuracy after both partners finish scoring.

This test uses 25 questions drawn from documents already familiar to the project, with AI help in drafting the gold set. It is a small test, not proof of performance on unfamiliar questions. Some files overlap or include neighboring policies, and chunk boundaries can split sentences. The same evidence may appear in more than one file. The expected answers were never sent to the answer model, and the questions and source documents stayed fixed. Future model responses may still vary at temperature zero.

See `analysis/failure_taxonomy.md` for automatically observable failures and the distinction between those counts and pending correctness judgments. No corpus, prompt, model, or overlap setting was changed to improve a condition mid-experiment.
'''
(ROOT/'analysis/results.md').write_text(report)

# Preserve partner-entered failure causes; do not invent semantic classifications.
path=run/'partner_review/failure_review.csv'
old={}
if path.exists():
    with path.open() as f:old={(r['variant'],r['question_id']):r for r in csv.DictReader(f)}
fields=['variant','question_id','cause','notes','reviewer']
with path.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for r in rows:w.writerow(old.get((r['variant'],r['question_id']),{'variant':r['variant'],'question_id':r['question_id']}))
reviewed_causes=old
scores={(d['variant'],d['question_id']):d for d in scored}
failures=[]
for row in rows:
    key=(row['variant'],row['question_id']);cats=[]
    if row['answerable'] and row['model_answerable'] is False:cats.append('wrong_refusal')
    if row['answerable'] and row['hit']==0:cats.append('source_hit_miss')
    if row.get('citation_status')=='invalid':cats.append('invalid_citation')
    if scores[key]['correct']==0:
        cats.append('incorrect_answer')
        cats += [x.strip() for x in reviewed_causes.get(key,{}).get('cause','').split(';') if x.strip()]
    if cats:failures.append((row,list(dict.fromkeys(cats))))
counts={v:Counter(cat for r,cats in failures if r['variant']==v for cat in cats) for v in summary}
taxonomy='''# Failure taxonomy for the fixed-top-3 chunk-size experiment

This report lists the failures we can count directly from the saved outputs. A refusal on an answerable question counts as a wrong refusal, even when the model was being cautious because retrieval missed the evidence. Other incorrect answers and their causes will be added after we finish scoring independently.

| Automatically measurable category | 250-word baseline | 200-word candidate |
|---|---|---|
'''
for category in ['wrong_refusal','source_hit_miss','invalid_citation']:
    taxonomy+=f"| {category} | {counts['baseline'][category]} | {counts['candidate'][category]} |\n"
for v in summary:
    m=summary[v]['correctness']
    taxonomy+=f"\n{labels[v]} correctness review: {count(m)}. We still need to finish scoring before the list of incorrect answers is complete.\n"
taxonomy+='''
## Category definitions

- wrong_refusal: answerable gold question, but the returned answerable flag is false. This follows the handout regardless of why the refusal happened.
- source_hit_miss: none of the expected documents appears among the three retrieved chunks. A source hit can still miss a necessary passage or another required document.
- invalid_citation: selected evidence IDs or quote/source string checks fail.
- incorrect_answer: the partners settle on correctness=0. Explain its cause in `partner_review/failure_review.csv`: for example, retrieval_miss, incomplete_answer, incorrect_fact, unsupported_claim, or other.

Category counts may overlap. A source miss need not cause an incorrect answer when equivalent evidence exists elsewhere. Refusal and correctness failures are different measurements. A reported zero in an automatic category does not imply zero unreviewed semantic errors.

## Worked examples of observed automatic categories
'''
for category in ['wrong_refusal','source_hit_miss','invalid_citation']:
    examples=[r for r,cats in failures if category in cats]
    if not examples:
        taxonomy+=f'\n{category}: no cases in this run.\n';continue
    r=examples[0]
    taxonomy+=f"\n### {category}: {r['variant']} {r['question_id']}\n\nQuestion: {r['question']}\n\nExpected answer: {r['expected_answer']}\n\nActual response: {r['answer']}\n\nRetrieved chunk IDs: {', '.join(h['source'] for h in r['retrieved'])}.\n\nThis is an observed {category} under the definition above. The saved row includes the full retrieved passages. Checking those passages will show whether the evidence was missing or whether the answer overlooked it.\n"
taxonomy+='\n## Every automatically observed or partner-confirmed failed row\n\n| Variant | Question | Categories | Partner cause notes |\n|---|---|---|---|\n'
for r,cats in failures:
    note=reviewed_causes.get((r['variant'],r['question_id']),{}).get('notes','')
    taxonomy+=f"| {r['variant']} | {r['question_id']} | {'; '.join(cats)} | {note.replace('|','/')} |\n"
if not failures:taxonomy+='No automatic failures observed; correctness review may still identify failures.\n'
(ROOT/'analysis/failure_taxonomy.md').write_text(taxonomy)
executive=f'''# Beloit College policy assistant

We built this project to help current Beloit students find answers to questions about classes, graduation, housing, and other college policies. The system searches {settings['document_count']} saved public documents and writes an answer using the passages it finds. It includes those passages so the reader can check the answer. It cannot look up personal grades, financial-aid awards, room assignments, or private reports.

Our experiment asks whether smaller chunks help retrieval. We compared 250-word chunks with 200-word chunks, keeping the overlap at 50 words and retrieving three passages in both versions. The two indexes contain {conditions['baseline']['chunk_count']} and {conditions['candidate']['chunk_count']} chunks. We used the same models, prompt, documents, and 25 questions for both.

The 250-word version found an expected source document for {count(summary['baseline']['hit_rate'])} answerable questions; the 200-word version did so for {count(summary['candidate']['hit_rate'])}. That did not always mean they found the passage needed to answer the whole question. The 250-word version refused {count(summary['baseline']['wrong_refusals'])} answerable questions; the 200-word version refused {count(summary['candidate']['wrong_refusals'])}. Both correctly refused {count(summary['baseline']['correct_refusals'])} requests for personal information. All quoted answers passed the source-text check: {count(summary['baseline']['quote_fidelity'])} for larger chunks and {count(summary['candidate']['quote_fidelity'])} for smaller chunks.

Correctness is {count(summary['baseline']['correctness'])} for the larger chunks and {count(summary['candidate']['correctness'])} for the smaller chunks. This measure comes from Mai and Parker scoring separately and discussing disagreements. Until that review is complete, we cannot say which version is more accurate. AI-assisted suggestions are kept separate from the required human scores.

We would use this as a starting point for finding a policy, with someone reading the evidence before relying on the answer. We would not use it to make decisions for students. The test set is small, some source files overlap, and policies may change after the saved editions. For an important decision, the student should confirm the policy with the relevant college office. Our remaining work is to finish correctness scoring, explain the failures, and rehearse the demonstration. The notebook has now been checked from beginning to end with Vertex.
'''
(ROOT/'executive_summary.md').write_text(executive)
print('Updated required metrics and reports from',rel)
