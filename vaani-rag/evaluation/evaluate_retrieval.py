import json
from pathlib import Path
from collections import Counter

from ingestion.qdrant_client import get_qdrant_client
from ingestion.config import QDRANT_COLLECTION_NAME
from ingestion.embedder import BGEM3Embedder
from ingestion.retriever import QdrantRetriever


PROJECT_ROOT = Path(__file__).resolve().parent.parent

QUERIES_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "queries.jsonl"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "evaluation"
    / "results"
)

RESULTS_FILE = (
    RESULTS_DIR
    / "stage1_results.jsonl"
)


TOP_K = 20


def load_queries():
    queries = []

    with open(
        QUERIES_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            queries.append(
                json.loads(line)
            )

    return queries


def text_matches_terms(
    text,
    expected_terms,
):
    """
    Lightweight sanity check.

    Returns True when at least one expected
    term appears in the retrieved text.
    """

    text_lower = text.lower()

    for term in expected_terms:

        if term.lower() in text_lower:
            return True

    return False


def evaluate_query(
    retriever,
    query_data,
):
    query = query_data["query"]
    expected_terms = query_data.get(
        "expected_terms",
        [],
    )

    results = retriever.search(
        query=query,
        top_k=TOP_K,
    )

    evaluated_results = []

    for rank, result in enumerate(
        results,
        start=1,
    ):

        matched = text_matches_terms(
            result.text,
            expected_terms,
        )

        evaluated_results.append(
            {
                "rank": rank,
                "score": result.score,
                "language": result.language,
                "chunk_id": result.chunk_id,
                "parent_passage_id": (
                    result.parent_passage_id
                ),
                "query_id": result.query_id,
                "query_type": result.query_type,
                "is_selected": result.is_selected,
                "matched_expected_term": matched,
                "text": result.text,
            }
        )

    return evaluated_results


def calculate_metrics(
    all_results,
):
    total = len(all_results)

    recall_5 = 0
    recall_10 = 0
    recall_20 = 0

    language_stats = {}

    for item in all_results:

        results = item["results"]

        if any(
            r["matched_expected_term"]
            for r in results[:5]
        ):
            recall_5 += 1

        if any(
            r["matched_expected_term"]
            for r in results[:10]
        ):
            recall_10 += 1

        if any(
            r["matched_expected_term"]
            for r in results[:20]
        ):
            recall_20 += 1

        language = item["language"]

        if language not in language_stats:
            language_stats[language] = {
                "total": 0,
                "recall_5": 0,
                "recall_10": 0,
                "recall_20": 0,
            }

        stats = language_stats[language]

        stats["total"] += 1

        if any(
            r["matched_expected_term"]
            for r in results[:5]
        ):
            stats["recall_5"] += 1

        if any(
            r["matched_expected_term"]
            for r in results[:10]
        ):
            stats["recall_10"] += 1

        if any(
            r["matched_expected_term"]
            for r in results[:20]
        ):
            stats["recall_20"] += 1

    metrics = {
        "total_queries": total,
        "recall_at_5": (
            recall_5 / total
            if total else 0
        ),
        "recall_at_10": (
            recall_10 / total
            if total else 0
        ),
        "recall_at_20": (
            recall_20 / total
            if total else 0
        ),
        "language_stats": {},
    }

    for language, stats in language_stats.items():

        n = stats["total"]

        metrics["language_stats"][language] = {
            "queries": n,
            "recall_at_5": (
                stats["recall_5"] / n
                if n else 0
            ),
            "recall_at_10": (
                stats["recall_10"] / n
                if n else 0
            ),
            "recall_at_20": (
                stats["recall_20"] / n
                if n else 0
            ),
        }

    return metrics


def main():

    print("=" * 70)
    print("VAANIRAG STAGE 1 RETRIEVAL EVALUATION")
    print("=" * 70)

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # Load evaluation queries
    # ---------------------------------------------------------

    queries = load_queries()

    print(
        f"\nEvaluation queries: {len(queries)}"
    )

    counts = Counter(
        q["language"]
        for q in queries
    )

    print(
        f"English : {counts.get('en', 0)}"
    )

    print(
        f"Hindi   : {counts.get('hi', 0)}"
    )

    print(
        f"Marathi : {counts.get('mr', 0)}"
    )

    # ---------------------------------------------------------
    # Connect to Qdrant
    # ---------------------------------------------------------

    print(
        "\nConnecting to Qdrant..."
    )

    client = get_qdrant_client()

    info = client.get_collection(
        QDRANT_COLLECTION_NAME
    )

    print(
        f"Qdrant points: {info.points_count}"
    )

    print(
        f"Collection status: {info.status}"
    )

    # ---------------------------------------------------------
    # Load BGE-M3
    # ---------------------------------------------------------

    print(
        "\nLoading BGE-M3..."
    )

    embedder = BGEM3Embedder(
        device="GPU"
    )

    print(
        f"Embedding dimension: "
        f"{embedder.get_dimension()}"
    )

    # ---------------------------------------------------------
    # Create retriever
    # ---------------------------------------------------------

    retriever = QdrantRetriever(
        client=client,
        embedder=embedder,
    )

    # ---------------------------------------------------------
    # Evaluate
    # ---------------------------------------------------------

    all_results = []

    print(
        f"\nRunning Top-{TOP_K} retrieval..."
    )

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8",
    ) as output:

        for index, query_data in enumerate(
            queries,
            start=1,
        ):

            print(
                f"\n[{index}/{len(queries)}] "
                f"{query_data['language'].upper()} "
                f"{query_data['query']}"
            )

            results = evaluate_query(
                retriever,
                query_data,
            )

            evaluation = {
                "query_id": query_data[
                    "query_id"
                ],
                "language": query_data[
                    "language"
                ],
                "query": query_data[
                    "query"
                ],
                "expected_terms": query_data.get(
                    "expected_terms",
                    [],
                ),
                "results": results,
            }

            all_results.append(
                evaluation
            )

            output.write(
                json.dumps(
                    evaluation,
                    ensure_ascii=False,
                )
                + "\n"
            )

            hits = [
                r
                for r in results[:5]
                if r["matched_expected_term"]
            ]

            print(
                f"  Top-5 term hit: "
                f"{'YES' if hits else 'NO'}"
            )

            if results:

                print(
                    f"  Rank 1 score: "
                    f"{results[0]['score']:.4f}"
                )

                print(
                    f"  Rank 1 language: "
                    f"{results[0]['language']}"
                )

                print(
                    "  Rank 1 text: "
                    + results[0]["text"][:180]
                    .replace("\n", " ")
                )

    # ---------------------------------------------------------
    # Metrics
    # ---------------------------------------------------------

    metrics = calculate_metrics(
        all_results
    )

    metrics_file = (
        RESULTS_DIR
        / "stage1_metrics.json"
    )

    with open(
        metrics_file,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            metrics,
            f,
            indent=2,
            ensure_ascii=False,
        )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("STAGE 1 EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Queries     : "
        f"{metrics['total_queries']}"
    )

    print(
        f"Recall@5    : "
        f"{metrics['recall_at_5']:.2%}"
    )

    print(
        f"Recall@10   : "
        f"{metrics['recall_at_10']:.2%}"
    )

    print(
        f"Recall@20   : "
        f"{metrics['recall_at_20']:.2%}"
    )

    print("\nBy language:")

    for language, stats in (
        metrics["language_stats"]
        .items()
    ):

        print(
            f"  {language.upper()}: "
            f"R@5={stats['recall_at_5']:.2%}, "
            f"R@10={stats['recall_at_10']:.2%}, "
            f"R@20={stats['recall_at_20']:.2%}"
        )

    print(
        f"\nResults saved to:"
        f"\n  {RESULTS_FILE}"
    )

    print(
        f"\nMetrics saved to:"
        f"\n  {metrics_file}"
    )

    print(
        "\nSTAGE 1 RETRIEVAL EVALUATION COMPLETE"
    )


if __name__ == "__main__":
    main()