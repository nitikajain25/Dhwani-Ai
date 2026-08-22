import json
from pathlib import Path
from collections import Counter, defaultdict


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "results"
    / "stage2_results.jsonl"
)


def main():

    print("=" * 70)
    print("STAGE 2 RETRIEVAL ERROR ANALYSIS")
    print("=" * 70)

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

    print(
        f"\nQueries loaded: {len(results):,}"
    )

    # --------------------------------------------------------
    # First relevant rank
    # --------------------------------------------------------

    rank_distribution = Counter()

    failures = []

    successful = []

    for item in results:

        first_rank = None

        for result in item["results"]:

            if result["relevant"]:

                first_rank = result["rank"]
                break

        if first_rank is None:

            rank_distribution[
                "NOT_FOUND"
            ] += 1

            failures.append(item)

        else:

            rank_distribution[
                first_rank
            ] += 1

            successful.append(
                (
                    first_rank,
                    item,
                )
            )

    # --------------------------------------------------------
    # Rank buckets
    # --------------------------------------------------------

    buckets = {
        "Rank 1": 0,
        "Ranks 2-5": 0,
        "Ranks 6-10": 0,
        "Ranks 11-20": 0,
        "Not found": 0,
    }

    for rank, count in (
        rank_distribution.items()
    ):

        if rank == "NOT_FOUND":

            buckets["Not found"] += count

        elif rank == 1:

            buckets["Rank 1"] += count

        elif rank <= 5:

            buckets["Ranks 2-5"] += count

        elif rank <= 10:

            buckets["Ranks 6-10"] += count

        else:

            buckets["Ranks 11-20"] += count

    print()
    print("-" * 70)
    print("FIRST RELEVANT RESULT")
    print("-" * 70)

    for name, count in buckets.items():

        percentage = (
            count / len(results) * 100
        )

        print(
            f"{name:<15} "
            f"{count:>5,} "
            f"({percentage:6.2f}%)"
        )

    # --------------------------------------------------------
    # Language analysis
    # --------------------------------------------------------

    languages = Counter()

    for item in results:

        language = (
            item.get("source_lang")
            or "unknown"
        )

        languages[language] += 1

    print()
    print("-" * 70)
    print("SOURCE LANGUAGE FIELD")
    print("-" * 70)

    for language, count in (
        languages.most_common()
    ):

        print(
            f"{language:<20}"
            f"{count:>6,}"
        )

    # --------------------------------------------------------
    # Result language analysis
    # --------------------------------------------------------

    retrieved_languages = Counter()

    for item in results:

        for result in item["results"]:

            language = (
                result.get("language")
                or "unknown"
            )

            retrieved_languages[
                language
            ] += 1

    print()
    print("-" * 70)
    print("RETRIEVED CHUNK LANGUAGES")
    print("-" * 70)

    for language, count in (
        retrieved_languages.most_common()
    ):

        print(
            f"{language:<20}"
            f"{count:>8,}"
        )

    # --------------------------------------------------------
    # Failed queries
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("FAILED QUERIES")
    print("-" * 70)

    print(
        f"Total NOT FOUND: "
        f"{len(failures):,}"
    )

    for index, item in enumerate(
        failures[:20],
        start=1,
    ):

        print()
        print(
            f"[FAIL {index}] "
            f"Query ID: "
            f"{item['query_id']}"
        )

        print(
            f"Query: "
            f"{item['query']}"
        )

        print(
            f"Gold chunks: "
            f"{item['gold_chunk_count']}"
        )

        print(
            "Top result:"
        )

        if item["results"]:

            top = item["results"][0]

            print(
                f"  score={top['score']:.4f}"
            )

            print(
                f"  language="
                f"{top['language']}"
            )

            print(
                f"  chunk_id="
                f"{top['chunk_id']}"
            )

            print(
                f"  text="
                f"{top['text'][:250]}"
            )

    # --------------------------------------------------------
    # Best queries
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("RANK-1 EXAMPLES")
    print("-" * 70)

    rank_one = [
        item
        for rank, item in successful
        if rank == 1
    ]

    for index, item in enumerate(
        rank_one[:10],
        start=1,
    ):

        print()
        print(
            f"[TOP {index}] "
            f"Query ID: "
            f"{item['query_id']}"
        )

        print(
            f"Query: "
            f"{item['query']}"
        )

        print(
            f"Gold chunks: "
            f"{item['gold_chunk_count']}"
        )

        top = item["results"][0]

        print(
            f"Score: "
            f"{top['score']:.4f}"
        )

        print(
            f"Language: "
            f"{top['language']}"
        )

        print(
            f"Text: "
            f"{top['text'][:250]}"
        )

    # --------------------------------------------------------
    # Average first relevant rank
    # --------------------------------------------------------

    ranks = [
        rank
        for rank, item in successful
    ]

    if ranks:

        average_rank = (
            sum(ranks)
            / len(ranks)
        )

        print()
        print("-" * 70)
        print("RANK STATISTICS")
        print("-" * 70)

        print(
            f"Successful queries: "
            f"{len(ranks):,}"
        )

        print(
            f"Average first relevant rank: "
            f"{average_rank:.2f}"
        )

        print(
            f"Best rank: "
            f"{min(ranks)}"
        )

        print(
            f"Worst rank: "
            f"{max(ranks)}"
        )

    print()
    print("=" * 70)
    print("STAGE 2 ERROR ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()