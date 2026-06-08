import json
import uuid
import time
from src.db import init_db, save_result
from src.evaluators.faithfulness import score_faithfulness
from src.evaluators.relevance import score_relevance
from src.evaluators.latency import query_with_latency

GOLDEN_SET_PATH = "src/data/golden_set.json"

def run_evaluation(max_questions: int = 50):
    """Run the full evaluation pipeline."""

    # Init DB
    init_db()

    # Load golden set
    with open(GOLDEN_SET_PATH, "r") as f:
        golden_set = json.load(f)

    golden_set = golden_set[:max_questions]
    run_id = str(uuid.uuid4())[:8]  # short run ID e.g. "a3f2b1c9"

    print(f"\n{'='*50}")
    print(f"EVAL RUN: {run_id}")
    print(f"Questions: {len(golden_set)}")
    print(f"{'='*50}\n")

    results = []

    for i, item in enumerate(golden_set, 1):
        print(f"[{i}/{len(golden_set)}] {item['question'][:60]}...")

        # Step 1 — Query RAG API + measure latency
        result = query_with_latency(item["question"])

        if result["error"]:
            print(f"  ✗ API error: {result['error']}")
            continue

        # Step 2 — Score faithfulness
        faithfulness = score_faithfulness(
            question=item["question"],
            expected=item["expected_answer"],
            actual=result["answer"]
        )

        # Step 3 — Score relevance
        relevance = score_relevance(
            question=item["question"],
            actual=result["answer"]
        )

        # Step 4 — Save to DB
        save_result(
            run_id=run_id,
            question_id=item["id"],
            question=item["question"],
            topic=item["topic"],
            difficulty=item["difficulty"],
            expected_answer=item["expected_answer"],
            actual_answer=result["answer"],
            routed_to=result["routed_to"],
            faithfulness=faithfulness,
            relevance=relevance,
            latency_ms=result["latency_ms"]
        )

        print(f"  ✓ Routed: {result['routed_to']} | "
              f"Faithfulness: {faithfulness} | "
              f"Relevance: {relevance} | "
              f"Latency: {result['latency_ms']}ms")

        results.append({**item, **result,
                        "faithfulness": faithfulness,
                        "relevance": relevance})

        # Small delay to avoid Groq rate limits
        time.sleep(0.5)

    # Summary
    if results:
        avg_f = round(sum(r["faithfulness"] for r in results) / len(results), 2)
        avg_r = round(sum(r["relevance"]    for r in results) / len(results), 2)
        avg_l = round(sum(r["latency_ms"]   for r in results) / len(results), 2)

        print(f"\n{'='*50}")
        print(f"RUN {run_id} COMPLETE")
        print(f"Avg Faithfulness : {avg_f}")
        print(f"Avg Relevance    : {avg_r}")
        print(f"Avg Latency      : {avg_l}ms")
        print(f"{'='*50}\n")

    return run_id

if __name__ == "__main__":
    run_evaluation()