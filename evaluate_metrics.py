import json
import pandas as pd


def norm(s):
    return " ".join((s or "").lower().split())


def load_and_prepare_eval():
    with open("eval_results.json", "r", encoding="utf-8") as f:
        results = json.load(f)

    rows = []
    for out in results:
        q = out["question"]
        expected_doc = out.get("expected_doc", "")

        # Extract top-3 retrieved document names (removing chunk IDs/anchors if present)
        retrieved_raw = [item[0] for item in out.get("retrieved", [])[:3]]
        retrieved_docs = [r.split("#")[0].replace(".txt", "").strip() for r in retrieved_raw]

        # Calculate Hit Rate: Check if expected doc(s) appear in top 3 retrieved chunks
        if expected_doc:
            expected_list = [d.strip() for d in expected_doc.split(",")]
            # Hit is 1 if at least one expected doc is in retrieved top-3
            hit = int(any(exp in retrieved_docs for exp in expected_list))
        else:
            hit = 0  # Unanswerable questions have no hit rate

        # Quote fidelity check
        quote = out.get("quote", "")
        quote_verified = out.get("quote_verified", False)
        quote_found = int(quote_verified or (norm(quote) != "" and norm(quote) in norm(out.get("prompt", "")))) if quote else 0

        # Refusal check (answerable is False)
        refused = int(out.get("answerable") is False)

        rows.append({
            "question": q,
            "expected_doc": expected_doc,
            "retrieved_top3": ", ".join(retrieved_docs),
            "hit": hit,
            "quote_found": quote_found,
            "refused": refused,
            "answerable": out.get("answerable"),
            "answer": out.get("answer", ""),
            "quote": quote,
            "correct": None  # To be filled in manually (1 or 0)
        })

    df = pd.DataFrame(rows)
    return df


def print_metrics(df):
    ans = df[df.expected_doc != ""]
    unans = df[df.expected_doc == ""]

    print("\n" + "=" * 50)
    print("      RAG PIPELINE EVALUATION METRICS")
    print("=" * 50)
    print(f"Hit Rate:         {ans.hit.sum()} of {len(ans)}")
    print(f"Quote Fidelity:   {df.quote_found.sum()} of {len(df)}")
    print(f"Correct Refusals: {unans.refused.sum()} of {len(unans)}")
    print(f"Wrong Refusals:   {ans.refused.sum()} of {len(ans)}")

    if df["correct"].notnull().all():
        print(f"Correctness:      {int(df.correct.sum())} of {len(df)}")
    else:
        unscored = df["correct"].isnull().sum()
        print(f"Correctness:      PENDING ({unscored} questions left to score manually)")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    df = load_and_prepare_eval()

    # Save to CSV for easy manual correctness scoring
    df.to_csv("eval_for_grading.csv", index=False)
    print("Saved 'eval_for_grading.csv'. Open it to fill in the 'correct' column (1 or 0).")

    print_metrics(df)