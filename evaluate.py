import csv
import hashlib
import importlib.metadata
import json
from datetime import datetime, timezone
from pathlib import Path
import rag_pipeline as p

ROOT = Path(__file__).resolve().parent
GOLD = ROOT / 'analysis/evaluation_set.json'

def validate_gold():
    questions = json.loads(GOLD.read_text())
    docs = {doc: body for doc, _, body in p.load_documents()}
    assert 20 <= len(questions) <= 30
    assert len({q['question_id'] for q in questions}) == len(questions)
    for q in questions:
        assert q['question'] and q['expected_answer']
        if q['answerable']:
            assert q['relevant_doc_ids'] and q['expected_evidence'], q['question_id']
            assert set(q['relevant_doc_ids']) == {e['doc_id'] for e in q['expected_evidence']}
            for e in q['expected_evidence']:
                assert p.norm(e['quote']) in p.norm(docs[e['doc_id']]), (q['question_id'], e['doc_id'])
        else:
            assert not q['relevant_doc_ids'] and not q['expected_evidence']
    print(f"Validated {len(questions)} questions and all evidence excerpts against {len(docs)} documents.")
    return questions

def retrieval_metrics(q, hits):
    if not q['answerable']:
        return {'document_recall': None, 'hit': None, 'reciprocal_rank': None,
                'evidence_coverage': None}
    found = {source.rsplit('#', 1)[0] for _, source, _ in hits}
    # Two frozen documents contain the same lost-ID policy; either is a valid source.
    groups = [{d} for d in q['relevant_doc_ids']]
    if q['question_id'] in ['Q07', 'Q08']:
        groups = [{'handbook-student-ID', 'handbook-quiet-hours'}]
    recalled = sum(bool(group & found) for group in groups)
    valid_docs = set.union(*groups)
    ranks = [i for i, (_, source, _) in enumerate(hits, 1) if source.rsplit('#', 1)[0] in valid_docs]
    # Literal evidence coverage: fraction of distinct gold sentences found whole in any hit.
    # It is stricter than semantic support and can miss equivalent supporting passages.
    sentences = []
    for e in q['expected_evidence']:
        sentences.extend(m.group(0) for m in p.re.finditer(r'\S.*?(?:[.!?](?=\s|$)|$)', e['quote']))
    covered = sum(any(p.norm(sentence) in p.norm(text) for text, _, _ in hits) for sentence in sentences)
    return {'document_recall': recalled / len(groups), 'hit': int(recalled > 0),
            'reciprocal_rank': 1 / ranks[0] if ranks else 0,
            'evidence_coverage': covered / len(sentences) if sentences else None}

# The handout fixes k=3; only chunk size changes in this experiment.
CONDITIONS = [("baseline", 250), ("candidate", 200)]
FIXED_K = 3


def count_metric(numerator, denominator):
    return {"numerator": numerator, "denominator": denominator}


def summarize(rows):
    """Four automatic required metrics; correctness comes only from partner consensus."""
    summaries = []
    for variant, size in CONDITIONS:
        subset = [r for r in rows if r["variant"] == variant]
        answerable = [r for r in subset if r["answerable"]]
        generated = [r for r in subset if r.get("model_answerable") is not None and not r.get("api_error")]
        unavailable = [r for r in generated if not r["answerable"]]
        available = [r for r in generated if r["answerable"]]
        quoted = [r for r in generated if r.get("evidence")]
        fidelity = []
        individual_quotes = []
        for r in quoted:
            hits = [(h["text"], h["source"], h["score"]) for h in r["retrieved"]]
            matches = [bool(p.verify_quote(e, hits)) for e in r["evidence"]]
            fidelity.append(all(matches))
            individual_quotes.extend(matches)
        summaries.append({
            "variant": variant, "chunk_words": size, "k": FIXED_K,
            "questions": len(subset), "generated_answers": len(generated),
            "api_errors": sum(bool(r.get("api_error")) for r in subset),
            "hit_rate": count_metric(sum(r["hit"] for r in answerable), len(answerable)),
            "quote_fidelity": count_metric(sum(fidelity), len(fidelity)),
            "quote_fidelity_all_questions": count_metric(sum(fidelity), len(subset)),
            "individual_quote_matches": count_metric(sum(individual_quotes), len(individual_quotes)),
            "correctness": {"numerator": None, "denominator": len(subset), "status": "pending independent partner scores"},
            "correct_refusals": count_metric(sum(r["model_answerable"] is False for r in unavailable), len(unavailable)),
            # Count all refusals on answerable gold, regardless of retrieval/generation cause.
            "wrong_refusals": count_metric(sum(r["model_answerable"] is False for r in available), len(available))})
    return summaries


def export_review(rows, destination):
    """Create separate, unscored partner sheets. Never prefill scores from AI review."""
    folder = destination / "partner_review"
    folder.mkdir(exist_ok=True)
    fields = ["variant", "question_id", "chunk_words", "k", "question", "expected_answer",
              "answer", "gold_answerable", "model_answerable", "evidence", "correct", "notes", "reviewer"]
    for person in ["mai", "parker"]:
        path = folder / f"{person}_scores.csv"
        existing = {}
        if path.exists():
            with path.open() as f:
                existing = {(r["variant"], r["question_id"]): r for r in csv.DictReader(f)}
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
            for row in rows:
                old = existing.get((row["variant"], row["question_id"]), {})
                out = {k: row.get(k, "") for k in fields}
                out["gold_answerable"] = row["answerable"]
                out["evidence"] = json.dumps(row["evidence"], ensure_ascii=False)
                for key in ["correct", "notes", "reviewer"]:
                    out[key] = old.get(key, "")
                writer.writerow(out)
    path = folder / "consensus.csv"
    existing = {}
    if path.exists():
        with path.open() as f:
            existing = {(r["variant"],r["question_id"]):r for r in csv.DictReader(f)}
    with path.open("w",newline="") as f:
        writer = csv.DictWriter(f,fieldnames=["variant","question_id","consensus_score","resolution_notes","confirmed_by"])
        writer.writeheader()
        for row in rows:
            key=(row["variant"],row["question_id"])
            writer.writerow(existing.get(key,{"variant":key[0],"question_id":key[1]}))


def run_evaluation(retrieval_only=False):
    import numpy as np
    questions = validate_gold()
    docs = p.load_documents()
    indexes = {}
    for variant, size in CONDITIONS:
        texts, sources = p.build_chunks(docs, size=size, overlap=p.OVERLAP_WORDS)
        if len(texts) < 150:
            raise ValueError(f"{variant} has fewer than 150 chunks")
        indexes[variant] = {"texts": texts, "sources": sources, "chunk_words": size,
                            "chunk_count": len(texts), "fingerprint": p.fingerprint(texts)}
    settings = {"provider":"Vertex AI", "project":p.PROJECT,
                "embedding_model":p.EMBED_MODEL, "answer_model":p.CHAT_MODEL,
                "embedding_region":p.EMBED_LOCATION,"answer_region":p.CHAT_LOCATION,
                "overlap_words":p.OVERLAP_WORDS, "k":FIXED_K,"temperature":0,
                "document_count":len(docs),"experiment":"chunk_words: 250 vs 200; k=3 fixed",
                "conditions":{v:{k:d[k] for k in ["chunk_words","chunk_count","fingerprint"]} for v,d in indexes.items()},
                "retrieval_only":retrieval_only,
                "gold_sha256":hashlib.sha256(GOLD.read_bytes()).hexdigest(),
                "pipeline_sha256":hashlib.sha256((ROOT/"rag_pipeline.py").read_bytes()).hexdigest(),
                "evaluation_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    run_id = hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()[:12]
    destination = ROOT/"analysis"/"vertex_runs"/run_id
    destination.mkdir(parents=True,exist_ok=True)
    output_path = destination/"results.json"
    rows = json.loads(output_path.read_text()) if output_path.exists() else []
    settings["versions"]={name:importlib.metadata.version(name) for name in ["google-genai","numpy","google-auth"]}
    settings["last_attempt_utc"]=datetime.now(timezone.utc).isoformat()
    (destination/"settings.json").write_text(json.dumps(settings,indent=2)+"\n")
    for variant,d in indexes.items():
        (destination/f"{variant}_chunks.json").write_text(json.dumps([
            {"source":source,"text":text} for text,source in zip(d["texts"],d["sources"])],indent=2,ensure_ascii=False)+"\n")
    print(f"Run {run_id}: 250-word baseline={indexes['baseline']['chunk_count']} chunks; "
          f"200-word candidate={indexes['candidate']['chunk_count']} chunks; both k=3",flush=True)
    try:
        embed, chat = p.get_clients()
        completed={(r["variant"],r["question_id"]) for r in rows if not r.get("api_error")}
        if len(completed) < 2*len(questions):
            for variant,d in indexes.items():
                cache = p.CACHE if variant=="baseline" else ROOT/".embeddings_200.npz"
                d["matrix"]=p.load_or_embed(embed,d["texts"],cache=cache)
            for q in questions:
                needed=[v for v,_ in CONDITIONS if (v,q["question_id"]) not in completed]
                if not needed:
                    continue
                # Same query vector, searched against each independently chunked index.
                query=np.array(embed.models.embed_content(model=p.EMBED_MODEL,contents=[q["question"]],
                    config={"task_type":"RETRIEVAL_QUERY","auto_truncate":False}).embeddings[0].values,dtype="float32")
                for variant in needed:
                    d=indexes[variant]
                    ranked=p.cosine_top_k(d["matrix"],query,k=FIXED_K)
                    hits=[(d["texts"][i],d["sources"][i],score) for i,score in ranked]
                    row={**q,"variant":variant,"chunk_words":d["chunk_words"],"k":FIXED_K,
                         **retrieval_metrics(q,hits),
                         "retrieved":[{"source":s,"score":score,"text":t} for t,s,score in hits],
                         "answer":None,"model_answerable":None,"evidence":[],"api_error":None}
                    try:
                        if not retrieval_only:
                            answer=p.answer_from_hits(chat,q["question"],hits)
                            row.update({key:value for key,value in answer.items() if key not in ["answerable","retrieved"]})
                            row["model_answerable"]=answer["answerable"]
                    except Exception as exc:
                        row["api_error"]=type(exc).__name__
                    rows=[r for r in rows if (r["variant"],r["question_id"])!=(variant,q["question_id"])]+[row]
                    output_path.write_text(json.dumps(rows,indent=2,ensure_ascii=False)+"\n")
                    export_review(rows,destination)
                    print(variant,q["question_id"],row.get("citation_status") or row.get("api_error") or "retrieved",flush=True)
                    if row["api_error"]:
                        raise RuntimeError(f"Generation failed: {row['api_error']}; fix access before resuming")
        summaries=summarize(rows)
        (destination/"summary.json").write_text(json.dumps(summaries,indent=2)+"\n")
        export_review(rows,destination)
        (destination/"status.json").write_text(json.dumps({"complete":len(rows)==2*len(questions),"rows":len(rows)},indent=2)+"\n")
        print(json.dumps(summaries,indent=2))
    except Exception as exc:
        (destination/"status.json").write_text(json.dumps({"complete":False,"error_type":type(exc).__name__,"rows":len(rows)},indent=2)+"\n")
        print(f"Run stopped ({type(exc).__name__}); saved progress in {destination.relative_to(ROOT)}.",flush=True)
        raise
    return rows,summaries,destination
