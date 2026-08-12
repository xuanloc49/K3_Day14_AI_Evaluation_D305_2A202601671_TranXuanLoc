"""
Exercise 3.5 — Retrieval Reranking Experiment

Selects at least 5 cases from actual_answers.json, computes Context Recall and
Context Precision before and after reranking, and prints a comparison table.
"""

from __future__ import annotations

import json
from pathlib import Path

from template import RAGASEvaluator, rerank_by_overlap, _tokenize


def main() -> None:
    golden_path = Path("golden_dataset.json")
    actual_path = Path("artifacts/actual_answers.json")

    golden = json.loads(golden_path.read_text(encoding="utf-8"))
    actual = json.loads(actual_path.read_text(encoding="utf-8"))

    # Build lookup by ID
    golden_by_id = {r["id"]: r for r in golden["qa_pairs"]}
    actual_by_id = {r["id"]: r for r in actual["answers"]}

    # Select cases: pick a mix of difficulties with retrieved_contexts
    selected_ids = ["E01", "E04", "M01", "M04", "H01", "H02", "H03", "H05", "A03"]

    evaluator = RAGASEvaluator()

    print("=" * 100)
    print("Exercise 3.5 — Retrieval Reranking Experiment")
    print("=" * 100)
    print()

    # Table header
    print(f"| {'ID':<4} | {'Recall before':>14} | {'Recall after':>13} | "
          f"{'Precision before':>16} | {'Precision after':>16} | {'Delta Precision':>16} |")
    print(f"|{'-'*6}|{'-'*16}|{'-'*15}|{'-'*18}|{'-'*18}|{'-'*18}|")

    total_recall_before = 0.0
    total_recall_after = 0.0
    total_precision_before = 0.0
    total_precision_after = 0.0
    count = 0

    for case_id in selected_ids:
        golden_record = golden_by_id.get(case_id)
        actual_record = actual_by_id.get(case_id)
        if golden_record is None or actual_record is None:
            continue

        expected = golden_record["expected_answer"]
        question = golden_record["question"]
        retrieved_texts = [c["text"] for c in actual_record["retrieved_contexts"]]

        if not retrieved_texts:
            continue

        # Before reranking
        recall_before = evaluator.evaluate_context_recall(retrieved_texts, expected)
        precision_before = evaluator.evaluate_context_precision(retrieved_texts, expected)

        # Rerank by overlap with the question (query)
        reranked = rerank_by_overlap(retrieved_texts, question)

        # After reranking
        recall_after = evaluator.evaluate_context_recall(reranked, expected)
        precision_after = evaluator.evaluate_context_precision(reranked, expected)

        delta = precision_after - precision_before

        print(f"| {case_id:<4} | {recall_before:>14.3f} | {recall_after:>13.3f} | "
              f"{precision_before:>16.3f} | {precision_after:>16.3f} | "
              f"{delta:>+16.3f} |")

        total_recall_before += recall_before
        total_recall_after += recall_after
        total_precision_before += precision_before
        total_precision_after += precision_after
        count += 1

    if count > 0:
        avg_recall_before = total_recall_before / count
        avg_recall_after = total_recall_after / count
        avg_precision_before = total_precision_before / count
        avg_precision_after = total_precision_after / count
        avg_delta = avg_precision_after - avg_precision_before

        print(f"|{'-'*6}|{'-'*16}|{'-'*15}|{'-'*18}|{'-'*18}|{'-'*18}|")
        print(f"| {'Avg':<4} | {avg_recall_before:>14.3f} | {avg_recall_after:>13.3f} | "
              f"{avg_precision_before:>16.3f} | {avg_precision_after:>16.3f} | "
              f"{avg_delta:>+16.3f} |")

    print()
    print("Key observations:")
    print("1. Recall is IDENTICAL before and after — reranking does not add or remove chunks.")
    print("2. Precision changes because AP@K rewards relevant chunks appearing earlier.")
    print(f"3. Average precision delta: {avg_delta:+.3f}")


if __name__ == "__main__":
    main()
