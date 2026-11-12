# RAG for Beloit College's Documents
## Who the system is for

Our user is a current Beloit student and whoever trying to understand academic requirements and everyday residential policies. We focused on registration, graduation, transfer credit, grading, selected majors, financial aid, housing, guests, keys, parking, and student conduct. The system uses public policies. It cannot tell a student their personal award amount, grade, room assignment, or the outcome of a complaint.

## Choosing and saving the documents

`documents.csv` lists 23 documents, with one row for each selected policy or program topic. The sources include the 2026–2027 student handbook, the 2025–2027 course catalog, and registrar pages. We chose these because they cover the kinds of questions our user would ask. This is a selected collection, not a complete copy of every college policy or department page.

The original files are saved in `raw/`, and the extracted text is in `corpus/`. Keeping both means a website update will not silently change the experiment. `corpus/manifest.csv` records the document metadata and sizes, and `analysis/source_snapshot_manifest.json` records checksums so we can detect changed files.

We used the supplied `beloit_ingest.py` rather than writing a new extractor. Earlier project edits added PDF line unwrapping and whitespace/header cleanup. During the November 11 audit, missing raw snapshots were recovered from repository commit `ee38bd8` instead of downloading new versions. The missing student-ID document was then extracted from page 72 of that saved handbook with the supplied extractor. The other corpus texts were left in place.

## What needed attention

PDF page boundaries do not always line up with policy boundaries. Some files therefore include neighboring material. For example, the quiet-hours file also contains the lost-ID policy, the overnight-guests file includes pets and quiet hours, and the Data Science extract includes neighboring catalog content. A matching document title does not guarantee that a retrieved chunk contains the right passage.

The student-ID and quiet-hours files contain the same lost-ID passage, so Q07 and Q08 accept either as a correct retrieval source. Other duplicated passages may also affect retrieval. Duplicate chunks can take up several of the top three positions without adding new evidence.

We kept page markers in the saved corpus for reference. Before embedding, the loader removes those markers, standalone numeric footers, and standalone TABLE OF CONTENTS lines. It also converts PDF ligatures to ordinary letters and collapses whitespace. It keeps policy numbers, punctuation, and wording. Some extraction misspellings and inline footers remain. The original headers record source page ranges; we do not claim an exact page for each chunk.

## Chunking and retrieval

The baseline uses 250-word chunks with 50 words of overlap. It produces 179 chunks. The second version uses 200-word chunks with the same 50-word overlap and produces 235 chunks. Both exceed the assignment's 150-chunk target.

Overlap gives adjacent chunks some shared context, but it also repeats text and cannot guarantee that a whole sentence stays together. We used fixed word counts because they are easy to inspect and explain. Keeping the overlap at 50 words means it takes up a larger fraction of a smaller chunk; we did not tune that fraction separately.

Document titles stay outside the embedding text. Each chunk carries a source ID such as `handbook-lockout#0`, which lets us trace it to its document. Vertex `text-embedding-005` embeds documents with RETRIEVAL_DOCUMENT and questions with RETRIEVAL_QUERY. Cosine similarity ranks the passages, and the system returns three chunks. A NumPy matrix is enough for a corpus this size. Embeddings are cached and reused when the text and model settings match.

## Our experiment

We changed only chunk size: 250 words versus 200 words. The corpus, preprocessing, 50-word overlap, models, prompt, response schema, temperature, and gold questions stay the same. Both versions retrieve three chunks, following the Evaluation Metrics handout. The same question vector is searched against the two indexes.

We originally tried comparing three retrieved passages with five. That comparison was replaced after reading the handout's fixed-k rule. It is recorded in the AI-use log, but its results are not mixed with the final experiment. The earlier TF-IDF exercise and MiniLM notebook also used different settings, so their chunk counts are not the final Vertex counts.

The final set has 25 questions: 21 answerable and four that require refusal because personal records are unavailable. The code reads `analysis/evaluation_set.json`; the Markdown version includes the questions, expected evidence, and five metric definitions. Every evidence excerpt has been checked against the saved text. Mai and Parker still need to verify the expected answers themselves.

Hit rate, quote fidelity, and refusals are checked in code. Quote matching ignores only case and extra spaces, separately from document cleanup. Correctness requires both partners to score independently, then discuss disagreements. A refusal on an answerable question counts as a wrong refusal even when retrieval missed the evidence.

## What we would improve next

Before using this outside class, we would tighten the document boundaries, reduce duplicated policies, and test questions with less familiar wording. The saved editions would also need to be checked for policy changes. Those would be separate experiments: changing the corpus halfway through this comparison would make it harder to tell what caused a difference in the results.
