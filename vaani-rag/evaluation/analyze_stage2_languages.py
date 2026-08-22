import json
from pathlib import Path
from collections import defaultdict, Counter


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "results"
    / "stage2_results.jsonl"
)

EMBEDDINGS_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
)


def load_results():

    results = []

    with open(
        RESULTS_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        for line in f:

            if line.strip():

                results.append(
                    json.loads(line)
                )

    return results


def build_query_language_map(
    query_ids
):

    """
    Determine languages from the actual
    200K embedding records.

    We count languages among SELECTED
    chunks for each query.

    This avoids the Parquet-file collision
    where the same query_id can occur in
    multiple language datasets.
    """

    language_counts = defaultdict(
        Counter
    )

    files = sorted(
        EMBEDDINGS_DIR.glob(
            "vaani_batch_*.jsonl"
        )
    )

    print(
        f"Embedding files: {len(files):,}"
    )

    for index, file_path in enumerate(
        files,
        start=1,
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as f:

            for line in f:

                if not line.strip():
                    continue

                record = json.loads(line)

                metadata = record.get(
                    "metadata",
                    {},
                )

                query_id = metadata.get(
                    "query_id"
                )

                if query_id is None:
                    continue

                query_id = str(query_id)

                if query_id not in query_ids:
                    continue

                if not metadata.get(
                    "is_selected",
                    False,
                ):
                    continue

                language = metadata.get(
                    "language"
                )

                if language:

                    language_counts[
                        query_id
                    ][language] += 1

        if index % 500 == 0:

            print(
                f"Processed "
                f"{index:,}/"
                f"{len(files):,}"
            )

    return language_counts


def choose_language(
    counts
):

    """
    Choose the language with the largest
    number of selected chunks.

    If tied, mark as mixed.
    """

    if not counts:
        return "unknown"

    maximum = max(
        counts.values()
    )

    winners = [
        language
        for language, count
        in counts.items()
        if count == maximum
    ]

    if len(winners) == 1:
        return winners[0]

    return "mixed"


def main():

    print("=" * 70)
    print(
        "STAGE 2 CORPUS LANGUAGE ANALYSIS"
    )
    print("=" * 70)

    results = load_results()

    print()
    print(
        f"Evaluation results: "
        f"{len(results):,}"
    )

    query_ids = {
        str(item["query_id"])
        for item in results
    }

    print()
    print(
        "Building language mapping from "
        "selected chunks in the 200K corpus..."
    )

    language_counts = (
        build_query_language_map(
            query_ids
        )
    )

    # --------------------------------------------------------
    # Determine language per query
    # --------------------------------------------------------

    query_language = {}

    for query_id in query_ids:

        query_language[
            query_id
        ] = choose_language(
            language_counts.get(
                query_id,
                {},
            )
        )

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    stats = defaultdict(
        lambda: {
            "queries": 0,
            "hit5": 0,
            "hit10": 0,
            "hit20": 0,
            "mrr_sum": 0.0,
            "not_found": 0,
        }
    )

    for item in results:

        query_id = str(
            item["query_id"]
        )

        language = query_language.get(
            query_id,
            "unknown",
        )

        first_rank = None

        for result in item[
            "results"
        ]:

            if result["relevant"]:

                first_rank = result[
                    "rank"
                ]

                break

        s = stats[language]

        s["queries"] += 1

        if first_rank is None:

            s["not_found"] += 1

        else:

            if first_rank <= 5:
                s["hit5"] += 1

            if first_rank <= 10:
                s["hit10"] += 1

            if first_rank <= 20:
                s["hit20"] += 1

            s["mrr_sum"] += (
                1.0 / first_rank
            )

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "MULTILINGUAL RETRIEVAL RESULTS"
    )
    print("=" * 70)

    for language in [
        "en",
        "hi",
        "mr",
        "mixed",
        "unknown",
    ]:

        if language not in stats:
            continue

        s = stats[language]
        n = s["queries"]

        print()
        print(
            language.upper()
        )

        print(
            f"Queries     : {n:,}"
        )

        print(
            f"Recall@5    : "
            f"{s['hit5'] / n:.2%}"
        )

        print(
            f"Recall@10   : "
            f"{s['hit10'] / n:.2%}"
        )

        print(
            f"Recall@20   : "
            f"{s['hit20'] / n:.2%}"
        )

        print(
            f"MRR         : "
            f"{s['mrr_sum'] / n:.4f}"
        )

        print(
            f"Not found   : "
            f"{s['not_found']:,} "
            f"({s['not_found'] / n:.2%})"
        )

    # --------------------------------------------------------
    # Mapping distribution
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "QUERY LANGUAGE DISTRIBUTION"
    )
    print("=" * 70)

    for language, s in sorted(
        stats.items()
    ):

        print(
            f"{language}: "
            f"{s['queries']:,}"
        )

    print()
    print(
        "LANGUAGE ANALYSIS COMPLETE"
    )


if __name__ == "__main__":
    main()