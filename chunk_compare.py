#!/usr/bin/env python3
"""
DSDA 310 - chunk size comparison (In-class, Oct 29).

Splits your corpus two ways, searches both with the same questions, and prints
what came back so you can compare.

    python3 -m pip install --user scikit-learn
    python3 chunk_compare.py

Retrieval here is keyword matching (TF-IDF), the same method as the first half of
ICA 10. It needs nothing but scikit-learn: no Google Cloud, no embeddings, no
setup. It is NOT what you will use in Project 2. It is here because the question
today is what chunk SIZE does, and holding the search method fixed is how you see
that on its own.

------------------------------------------------------------------------------
YOU HAVE ONE FUNCTION TO WRITE: chunk(). See the TODO below.
------------------------------------------------------------------------------
"""
import re, sys
from pathlib import Path

CORPUS = Path("corpus")

# The two sizes you are comparing today, in words.
SIZES = [250, 750]

# Your own questions. Use three of the ten you wrote for Tuesday.
QUESTIONS = [
    "What initial steps must a student take to resolve a roommate or floor mate conflict before a room change can be approved?",
    "What three academic progress standards determine continued financial-aid eligibility?",
    "How many units can be double counted if a student majoring in Data Science or Data Analytics pursues another major or minor?",
]


def need(mod, pipname=None):
    try:
        return __import__(mod)
    except ImportError:
        sys.exit(f"Missing package '{mod}'. Run:  python3 -m pip install --user {pipname or mod}")


def load_documents():
    """Read corpus/*.txt, split the header off, return (doc_id, title, body)."""
    if not CORPUS.exists():
        sys.exit("No corpus/ folder. Run beloit_ingest.py (without --check) first.")
    docs = []
    for path in sorted(CORPUS.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        head, _, body = text.partition("-" * 60 + "\n")
        if not body:
            head, body = "", text
        title = ""
        for line in head.splitlines():
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip()
        docs.append((path.stem, title or path.stem, body.strip()))
    if not docs:
        sys.exit("corpus/ has no .txt files.")
    return docs


def chunk(body, size):
    words = body.split()
    if not words:
        return []

    overlap = 30
    step = max(1, size - overlap)
    chunks = []

    for i in range(0, len(words), step):
        chunk_words = words[i : i + size]
        chunks.append(" ".join(chunk_words))

    return chunks


def build(docs, size):
    """Chunk every document; return parallel lists of text and source id."""
    texts, sources = [], []
    for doc_id, title, body in docs:
        pieces = chunk(body, size)
        for i, piece in enumerate(pieces):
            piece = piece.strip()
            if piece:
                texts.append(piece)
                sources.append(f"{doc_id}#{i}")
    return texts, sources


def search(texts, questions, top=3):
    """TF-IDF cosine. Returns, per question, a list of (index, score)."""
    sk = need("sklearn", "scikit-learn")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    vec = TfidfVectorizer(stop_words="english")
    matrix = vec.fit_transform(texts)
    out = []
    for q in questions:
        scores = cosine_similarity(vec.transform([q]), matrix)[0]
        ranked = sorted(enumerate(scores), key=lambda p: -p[1])[:top]
        out.append(ranked)
    return out


def main():
    docs = load_documents()
    print(f"{len(docs)} document(s) in corpus/\n")

    results = {}
    for size in SIZES:
        texts, sources = build(docs, size)
        words = sum(len(t.split()) for t in texts)
        print(f"size {size:>4}:  {len(texts):>4} chunks, "
              f"{words:,} words total, "
              f"mean {words // max(len(texts), 1)} words per chunk")
        results[size] = (texts, sources, search(texts, QUESTIONS))

    print()
    for qi, question in enumerate(QUESTIONS):
        print("=" * 72)
        print(f"Q{qi + 1}  {question}")
        for size in SIZES:
            texts, sources, ranked = results[size]
            print(f"\n  --- chunks of {size} words ---")
            for rank, (idx, score) in enumerate(ranked[qi], start=1):
                preview = " ".join(texts[idx].split())[:160]
                print(f"  {rank}. {score:.4f}  {sources[idx]}")
                print(f"     {preview}...")
            top2 = ranked[qi][:2]
            if len(top2) == 2:
                print(f"     gap between 1st and 2nd: {top2[0][1] - top2[1][1]:.4f}")
        print()

    print("=" * 72)
    print("""
For each question, for each size, write down:
  1. Did the right document come back first?
  2. Does the top chunk contain the WHOLE answer, or part of it?
  3. How close was second place? A small gap means the ranking was nearly a
     coin flip.

Then one sentence: which size you are using in Project 2, and what it costs you.
If both sizes gave the same answer on all three questions, that is a result too -
it usually means the corpus is too small for the choice to matter yet.
""")


if __name__ == "__main__":
    main()
