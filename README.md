# Beloit College AI assistant

Link to slideshow presentaion: https://docs.google.com/presentation/d/1Rifh9bH_yOFkrLE-P7X70OOB6-6JmeJemp4n8Z8Mnyc/edit?usp=sharing

We built this project to help current Beloit students find answers to academic and housing questions. It searches our saved documents and uses Vertex AI to write an answer from the passages it finds. Each answer includes the source text so the reader can check it. When the evidence is missing, the system should say it cannot answer.

We use 23 documents from the student handbook, course catalog, and registrar pages. These explain general policies; they do not contain personal grades, financial-aid awards, or room assignments.

## Run the project

The working version is `rag_pipeline.py`. We kept the instructor's `pipeline.py` unchanged for reference. The notebook uses the working version too.

Sign in with Google Cloud CLI using an account that has Vertex AI access and available billing/quota:

```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=dsda310-project2
gcloud auth application-default set-quota-project "$GOOGLE_CLOUD_PROJECT"
python rag_pipeline.py "Who should I contact if I am locked out on Saturday night?"
```

Embeddings use `text-embedding-005` in `us-central1`; answers use `gemini-3.5-flash` in `global`. Vertex calls incur charges. No OpenAI key is needed, and credentials should stay outside this repository. Embeddings are cached locally so they do not need to be regenerated each time.

If your account uses different models or regions, set `VERTEX_EMBED_MODEL`, `VERTEX_CHAT_MODEL`, `VERTEX_EMBED_LOCATION`, or `VERTEX_CHAT_LOCATION`, then rerun both experiment conditions.

These checks do not make API calls:

```bash
python rag_pipeline.py --selftest
python rag_pipeline.py --validate-gold
python -m unittest discover -s tests -v
python scripts/audit_project.py
```

## What we compared

Our main question was whether smaller chunks would help the system find the right passage. The baseline uses 250-word chunks and the other version uses 200-word chunks. Both keep 50 words of overlap and retrieve exactly three chunks, as required by the evaluation handout. The indexes contain 179 and 235 chunks.

We kept the corpus, models, prompt, and 25 questions the same. Smaller chunks may focus the search, but they can also cut off useful context.

To run the comparison:

```bash
python rag_pipeline.py --evaluate
```

This produces 50 answers, one per question for each version. Results are saved as the run progresses under `analysis/vertex_runs/<run-id>/`. If a request fails, running the command again resumes the unfinished work. Changing the gold questions or pipeline/evaluation code creates a new run ID. To repeat the same run from scratch, move its previous results folder elsewhere first.

For a retrieval-only check, use `python rag_pipeline.py --evaluate --retrieval-only`. It still uses Vertex embeddings, but it does not generate answers and cannot replace the full evaluation.

## Scoring the answers

The five required metrics are hit rate, quote fidelity, correctness, correct refusals, and wrong refusals. Their definitions are in `analysis/evaluation_set.md`, and the results are in `analysis/results.md`. We report counts with denominators, such as “21 of 21”.

We still need to score correctness separately. The final run's `partner_review/` folder has `mai_scores.csv` and `parker_scores.csv`. Each partner should fill their own sheet before looking at the other's scores: enter 0 or 1 in `correct`, your name in `reviewer`, and notes for anything unclear. An answer can have a real citation and still miss an important condition.

After both sheets are complete, run:

```bash
python scripts/reconcile_scores.py
```

If the scores differ, discuss the answer and fill that row in `consensus.csv` with the agreed score, the reason, and both names. Missing scores and unresolved disagreements stay pending. Only our own independent scores count toward correctness.

Add explanations for incorrect answers in `failure_review.csv`, then refresh the reports:

```bash
python scripts/build_reports.py
```

The current final run is listed in `analysis/final_vertex_run.txt`. The reports show both interpretations of the quote-fidelity denominator because the handout's definition and sample code use different denominators.

## Using the notebook

`pipeline.ipynb` explains the same Vertex functions used by `rag_pipeline.py`. Open it from the project root with the `.venv` kernel, or run it after Google authentication:

```bash
jupyter nbconvert --to notebook --execute pipeline.ipynb --output pipeline_executed.ipynb --ExecutePreprocessor.timeout=1200
```

`RUN_GENERATION` controls the example answer; `RUN_EVALUATION` controls the full comparison. The working Python implementation passes its checks, and the notebook was executed successfully from top to bottom with Vertex on November 11. Its full evaluation cell stays disabled by default so a notebook check does not repeat all 50 answers.

## Where to find things

| File or folder | What it contains |
|---|---|
| `documents.csv`, `raw/`, `corpus/` | Source list, cached originals, and extracted text |
| `ingestion_plan.md` | Why these sources and chunking settings were chosen, plus extraction issues |
| `analysis/test_questions.md` | Our early development questions |
| `analysis/evaluation_questions` | Mai’s 25-question working draft |
| `analysis/evaluation_set.md` and `.json` | The 25 gold questions, expected answers, and evidence; the code reads JSON |
| `analysis/results.md` | The comparison and five required metrics |
| `analysis/failure_taxonomy.md` | Observed failures and examples |
| `analysis/review_rubric.md` | Instructions for independent correctness scoring |
| `executive_summary.md` | A short explanation of what the system does and how well it works |
| `ai_use_log.md` | How AI was used and how its output was checked |

The extractor and original Vertex pipeline were provided by the instructor. `pipeline.py` is kept unchanged as the reference. Our working implementation is `rag_pipeline.py`, which the notebook and evaluator import. The AI-use log records earlier experiments and how AI helped with the work. Before submitting, we need to check the expected answers, finish our separate scores, discuss disagreements, and update the reports.
