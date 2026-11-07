# Beloit College RAG project

A simple policy question-answering pipeline for current Beloit students.

Open [pipeline.ipynb](pipeline.ipynb) in Jupyter or VS Code with a Python 3.10+ kernel, from the repository root. Run the first cell to install dependencies, then run cells in order. The first retrieval run downloads the MiniLM model from Hugging Face. The existing [corpus](corpus/) is used directly; do not rerun extraction to use this notebook.

To generate answers, set `RUN_GENERATION = True` in the configuration cell and rerun from there. Provide `OPENAI_API_KEY` in your environment or enter it at the hidden prompt. The default answer model is `gpt-4.1-mini`; override it with `OPENAI_MODEL`. API calls incur charges. With generation disabled, retrieval and its evaluation still run.

The notebook saves chunks, embeddings, run settings, retrieval metrics, and a manual answer-review sheet under `analysis/pipeline_outputs/`. Re-running replaces those outputs; copy a run elsewhere before changing settings if you want to preserve it. The controlled comparison changes only retrieved passage count (3 versus 5). Model-generated answers can vary between runs.

Inputs: [document list](documents.csv), [ingestion plan](ingestion_plan.md), [early test questions](analysis/test_questions.md), and [evaluation draft](analysis/evaluation_questions). The notebook prefers `analysis/evaluation_set.md` once it contains questions in the documented format. The current draft still needs 20–30 verified questions, source IDs, and evidence; the notebook flags missing labels rather than inventing them.

Project writeups: [results](analysis/results.md), [failure taxonomy](analysis/failure_taxonomy.md), [AI-use log](ai_use_log.md), and [executive summary](executive_summary.md).
