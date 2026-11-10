#!/usr/bin/env python3
"""
DSDA 310 - Project 2 reference pipeline.

Corpus -> chunks -> embeddings -> index -> retrieval -> grounded answer.

    python3 -m pip install --user google-genai numpy
    python3 pipeline.py "Can I move off campus next year?"
    python3 pipeline.py --selftest   # no Vertex calls, checks the plumbing

Windows: use `py` instead of `python3`.

Expects corpus/ in the current directory, produced by beloit_ingest.py.
Embeddings are cached in .embeddings.npz and reused until the chunks change.

Run embed_test.py BEFORE this. If embed_test.py fails, this will too, and
the error will be harder to read.

This is a reference implementation provided by the instructor. Record that
in ai_use_log.md. The decisions in here (chunk size, k, prompt wording) are
the ones you are expected to examine, justify, or change for yourselves.
"""
import argparse, hashlib, json, os, sys
from pathlib import Path
import time

CORPUS = Path("corpus")
CACHE = Path(".embeddings.npz")

# Hardcoded on purpose. `export` does not exist on Windows PowerShell, and
# a missing environment variable is the single most common setup failure.
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT") or "project2-dsda"

# Two models, two regions, two clients. text-embedding-005 is not served at
# "global", and gemini-3.5-flash 404s at us-central1 even though it appears
# in the catalog there. The 404 says "not found or your project does not
# have access", which reads like a permissions problem and is not one.
EMBED_MODEL = "text-embedding-005"
EMBED_LOCATION = "us-central1"
CHAT_MODEL = "gemini-3.5-flash"
CHAT_LOCATION = "global"

CHUNK_WORDS = 250
OVERLAP_WORDS = 50
TOP_K = 3
# text-embedding-005 caps a single request at 20,000 input tokens, not at a
# number of items. 250-word chunks run about 350 tokens each, so 100 per
# request is roughly 35,000 and returns a 400 INVALID_ARGUMENT. 20 keeps a
# wide margin even if you raise CHUNK_WORDS.
EMBED_BATCH = 20


# ----------------------------------------------------------------- load

def load_documents():
    """corpus/*.txt -> [(doc_id, title, body)], header stripped."""
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


# ---------------------------------------------------------------- chunk

def chunk(body, size=CHUNK_WORDS, overlap=OVERLAP_WORDS):
    """Fixed-width word chunks with overlap. Deliberately simple: you decide
    whether to cut at sentence boundaries, how much to overlap, and whether
    the title belongs inside the chunk text.

    Note that overlap here is a fixed number of WORDS. If you compare two
    chunk sizes with the same word overlap, the two conditions differ in
    overlap fraction as well as in size, and you are varying two things."""
    words = body.split()
    if not words:
        return []
    step = max(size - overlap, 1)
    out = []
    for i in range(0, len(words), step):
        piece = words[i:i + size]
        if piece:
            out.append(" ".join(piece))
        if i + size >= len(words):
            break
    return out


def build_chunks(docs):
    """-> (texts, sources) as parallel lists. sources look like doc-id#3."""
    texts, sources = [], []
    for doc_id, _title, body in docs:
        for i, piece in enumerate(chunk(body)):
            texts.append(piece)
            sources.append(f"{doc_id}#{i}")
    return texts, sources


# ---------------------------------------------------------------- embed

def get_clients():
    """-> (embed_client, chat_client). Two regions, so two clients."""
    from google import genai
    if not PROJECT:
        sys.exit("PROJECT is empty. Edit PROJECT near the top of this file.")
    embed_client = genai.Client(vertexai=True, project=PROJECT,
                                location=EMBED_LOCATION)
    chat_client = genai.Client(vertexai=True, project=PROJECT,
                               location=CHAT_LOCATION)
    return embed_client, chat_client


def embed_texts(client, texts):
    """One vector per text, in batches."""
    import numpy as np
    vectors = []
    for start in range(0, len(texts), EMBED_BATCH):
        batch = texts[start:start + EMBED_BATCH]
        try:
            resp = client.models.embed_content(model=EMBED_MODEL, contents=batch)
            vectors.extend(e.values for e in resp.embeddings)
        except Exception as exc:
            if "token count" not in str(exc):
                raise
            # Batch still too large for the 20,000-token request cap.
            # Fall back to one chunk per request for this batch only.
            print("  batch over the token cap; sending these one at a time")
            for text in batch:
                resp = client.models.embed_content(model=EMBED_MODEL,
                                                   contents=[text])
                vectors.extend(e.values for e in resp.embeddings)
        print(f"  embedded {min(start + len(batch), len(texts))}/{len(texts)}")
    return np.array(vectors, dtype="float32")


def fingerprint(texts):
    """Changes when the chunks change, so a stale cache is never reused."""
    h = hashlib.sha1()
    h.update(str(len(texts)).encode())
    h.update(EMBED_MODEL.encode())   # switching models invalidates the cache
    for t in texts:
        h.update(t.encode("utf-8"))
    return h.hexdigest()


def load_or_embed(client, texts):
    """Embed once, reuse forever. Re-embedding every run is slow and costs money."""
    import numpy as np
    fp = fingerprint(texts)
    if CACHE.exists():
        cached = np.load(CACHE, allow_pickle=False)
        if str(cached["fingerprint"]) == fp:
            print(f"using cached embeddings ({cached['vectors'].shape[0]} chunks)")
            return cached["vectors"]
        print("chunks or embedding model changed since the cache was written; re-embedding")
    print(f"embedding {len(texts)} chunks")
    vectors = embed_texts(client, texts)
    np.savez(CACHE, vectors=vectors, fingerprint=np.array(fp))
    return vectors


# ------------------------------------------------------------- retrieve

def cosine_top_k(matrix, query_vec, k=TOP_K):
    """-> [(index, score)] for the k most similar rows."""
    import numpy as np
    m = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
    q = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    scores = m @ q
    order = np.argsort(-scores)[:k]
    return [(int(i), float(scores[i])) for i in order]


def retrieve(embed_client, matrix, texts, sources, question, k=TOP_K):
    import numpy as np
    qv = np.array(
        embed_client.models.embed_content(model=EMBED_MODEL, contents=[question])
        .embeddings[0].values, dtype="float32")
    return [(texts[i], sources[i], s) for i, s in cosine_top_k(matrix, qv, k)]


# ---------------------------------------------------------------- answer

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "answer": {"type": "STRING"},
        "quote": {"type": "STRING"},
        "source": {"type": "STRING"},
        "answerable": {"type": "BOOLEAN"},
    },
    "required": ["answer", "quote", "source", "answerable"],
}


def build_prompt(question, hits):
    """The retrieved passages go IN the prompt. That is what makes this RAG.

    Retrieval always returns something. On a corpus with no housing policy,
    "Can I move off campus?" will still come back with three chunks at
    plausible-looking scores. The refusal instruction below is the only thing
    standing between that and an invented answer. Try deleting it once."""
    passages = "\n\n".join(
        f"[{src}]\n{text}" for text, src, _score in hits)
    return (
        "Answer the question using only the passages below.\n"
        "If the passages do not contain the answer, set answerable to false, "
        "leave answer and quote empty, and do not use outside knowledge.\n"
        "The quote must be copied word for word from one passage. Do not join "
        "sentences together or reword them.\n"
        "Set source to the bracketed label of the passage the quote came from.\n\n"
        f"PASSAGES:\n{passages}\n\n"
        f"QUESTION: {question}"
    )


def generate(chat_client, prompt):
    resp = chat_client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json", "response_schema": SCHEMA},
    )
    return json.loads(resp.text)


def norm(s):
    return " ".join((s or "").lower().split())


def verify_quote(out, hits):
    """The schema guarantees a string, not a real quotation. Check it yourself."""
    q = norm(out.get("quote"))
    if not q:
        return None
    return any(q in norm(text) for text, _src, _score in hits)


# ------------------------------------------------------- the one function

def answer_question(embed_client, chat_client, matrix, texts, sources,
                    question, k=TOP_K):
    """Question in, scored answer out. The evaluation set calls this 20-30 times."""
    hits = retrieve(embed_client, matrix, texts, sources, question, k)
    prompt = build_prompt(question, hits)
    out = generate(chat_client, prompt)
    return {
        "question": question,
        "retrieved": [(src, round(score, 4)) for _t, src, score in hits],
        "prompt": prompt,
        "answer": out.get("answer", ""),
        "quote": out.get("quote", ""),
        "source": out.get("source", ""),
        "answerable": out.get("answerable"),
        "quote_verified": verify_quote(out, hits),
    }


# ------------------------------------------------------------- selftest

def selftest():
    """Everything except the Vertex calls, with no client at all."""
    import numpy as np

    body = " ".join(f"word{i}" for i in range(600))
    pieces = chunk(body, size=250, overlap=50)
    assert len(pieces) == 3, f"expected 3 chunks, got {len(pieces)}"
    assert pieces[0].split()[-50:] == pieces[1].split()[:50], "overlap is wrong"
    assert pieces[-1].split()[-1] == "word599", "last words were dropped"
    print("chunking ok:", [len(p.split()) for p in pieces])

    short = chunk(" ".join(f"w{i}" for i in range(80)), size=250, overlap=50)
    assert len(short) == 1, f"short document should give 1 chunk, got {len(short)}"
    print("short-document chunking ok")

    m = np.array([[1.0, 0.0], [0.0, 1.0], [0.9, 0.1]], dtype="float32")
    top = cosine_top_k(m, np.array([1.0, 0.0], dtype="float32"), k=2)
    assert top[0][0] == 0 and top[1][0] == 2, top
    assert abs(top[0][1] - 1.0) < 1e-5, top
    print("cosine ok:", [(i, round(s, 3)) for i, s in top])

    hits = [("All students are required to live in college-owned housing.", "housing#0", 0.7)]
    assert verify_quote({"quote": "required to LIVE in college-owned housing"}, hits) is True
    assert verify_quote({"quote": "students may live anywhere"}, hits) is False
    assert verify_quote({"quote": ""}, hits) is None
    print("quote verification ok")

    p = build_prompt("Can I move off campus?", hits)
    assert "college-owned housing" in p and "Can I move off campus?" in p
    assert "[housing#0]" in p
    print("prompt ok:", len(p), "chars")

    assert fingerprint(["a", "b"]) != fingerprint(["a", "c"])
    print("cache fingerprint ok")
    print("\nall plumbing checks passed. Vertex calls are NOT covered by this.")
    print("Run embed_test.py to check those.")

# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?", help="a question to run through the pipeline")
    ap.add_argument("--selftest", action="store_true", help="check the plumbing, no API calls")
    ap.add_argument("-k", type=int, default=TOP_K)
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return

    # Load corpus and embeddings
    docs = load_documents()
    texts, sources = build_chunks(docs)
    print(f"{len(docs)} documents, {len(texts)} chunks")
    if len(texts) < 150:
        print(f"    WARNING: {len(texts)} chunks is under the 150 floor")

    embed_client, chat_client = get_clients()
    matrix = load_or_embed(embed_client, texts)

    # OPTION A: Single question passed in command line
    if args.question:
        out = answer_question(embed_client, chat_client, matrix, texts, sources,
                              args.question, args.k)

        print("\n" + "=" * 70)
        print("QUESTION:", out["question"])
        print("\nRETRIEVED:")
        for src, score in out["retrieved"]:
            print(f"  {score:.4f}  {src}")
        print("\nPROMPT SENT TO THE MODEL:")
        print("-" * 70)
        print(out["prompt"])
        print("-" * 70)
        print("\nANSWER:")
        print(json.dumps({k: out[k] for k in
                          ("answer", "quote", "source", "answerable")}, indent=2))
        print("\nquote actually present in a retrieved chunk:", out["quote_verified"])
        return

# OPTION B: No question passed -> LOAD & RUN ALL GOLD QUESTIONS FROM JSON!
    json_path = "gold_dataset.json"
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            gold_dataset = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Could not find '{json_path}'. Make sure it is saved in your project root folder.")
        return

    print(f"\n--- Running Pipeline on {len(gold_dataset)} Gold Questions ---")
    all_results = []

    for i, item in enumerate(gold_dataset, 1):
        q = item["question"]
        expected_doc = item.get("expected_doc", "")

        print(f"\n[{i}/{len(gold_dataset)}] Processing: {q}")
        
        # Retry loop inside main keeps professor's generate() untouched
        while True:
            try:
                out = answer_question(embed_client, chat_client, matrix, texts, sources, q, args.k)
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print("  [Rate Limit 429] Waiting 15s for quota window to reset...")
                    time.sleep(15)
                else:
                    raise e

        out["expected_doc"] = expected_doc
        all_results.append(out)

        # Save progress after every question so work is never lost
        with open("eval_results.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2)

        time.sleep(3)  # Standard delay between questions

    print("\n" + "=" * 70)
    print(f"Done! Evaluated {len(all_results)} questions.")
    print("Results saved to 'eval_results.json'")
    print("=" * 70)


if __name__ == "__main__":
    main()