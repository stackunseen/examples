"""Score retrieval on its own, before any model writes an answer.

For each question in golden.jsonl, a hit at k means one of its expected sections is among the first k retrieved.
Recall at k is the share of questions with a hit; MRR rewards finding it near the top. The three modes show
what each index contributes and what fusing them buys.

    python evaluate.py                    # the table, plus the questions hybrid search misses
    python evaluate.py --min-recall 0.9   # exit with an error if hybrid recall at 5 drops below 0.9 (a CI gate)
    python evaluate.py --chunking windows # the same questions against fixed 40-word chunks
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rag import Retriever, load_chunks, load_windows

GOLDEN = Path(__file__).parent / "golden.jsonl"
KS = (1, 3, 5)


def load_golden() -> list[dict]:
    return [json.loads(line) for line in GOLDEN.read_text(encoding="utf-8").splitlines() if line.strip()]


def score(retriever: Retriever, golden: list[dict], mode: str) -> tuple[dict[int, float], float, list[tuple[str, str]]]:
    hits = {k: 0 for k in KS}
    reciprocal_ranks = 0.0
    misses = []
    for item in golden:
        ids = [c.id for c in retriever.search(item["question"], k=max(KS), mode=mode)]
        first = next((i for i, cid in enumerate(ids) if cid in item["expected"]), None)
        for k in KS:
            hits[k] += first is not None and first < k
        reciprocal_ranks += 1 / (first + 1) if first is not None else 0.0
        if first is None or first > 0:
            misses.append((item["question"], ids[0]))
    n = len(golden)
    return {k: hits[k] / n for k in KS}, reciprocal_ranks / n, misses


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--min-recall", type=float, default=None, help="fail if hybrid recall at 5 is below this")
    parser.add_argument("--chunking", choices=["headings", "windows"], default="headings", help="windows: fixed 40-word chunks")
    args = parser.parse_args()

    retriever = Retriever(load_chunks() if args.chunking == "headings" else load_windows())
    golden = load_golden()
    print(f"{len(golden)} questions, {len(retriever.chunks)} chunks\n")
    print(f"{'mode':<8} {'recall@1':>9} {'recall@3':>9} {'recall@5':>9} {'MRR':>6}")
    results = {}
    for mode in ("bm25", "ngram", "hybrid"):
        recall, mrr, misses = score(retriever, golden, mode)
        results[mode] = (recall, misses)
        print(f"{mode:<8} {recall[1]:>9.2f} {recall[3]:>9.2f} {recall[5]:>9.2f} {mrr:>6.2f}")

    recall, misses = results["hybrid"]
    if misses:
        print("\nHybrid search did not rank the expected section first for:")
        for question, top in misses:
            print(f"  - {question}\n    first result: {top}")

    if args.min_recall is not None and recall[5] < args.min_recall:
        print(f"\nFAIL: hybrid recall at 5 is {recall[5]:.2f}, below {args.min_recall:.2f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
