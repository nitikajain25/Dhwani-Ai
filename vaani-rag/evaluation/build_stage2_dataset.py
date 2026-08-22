import json
from pathlib import Path
from collections import defaultdict

import pyarrow.parquet as pq


PROJECT_ROOT = Path(__file__).resolve().parent.parent

EMBEDDINGS_DIR = (
    PROJECT_ROOT / "outputs" / "embeddings"
)

RAW_DIR = (
    PROJECT_ROOT / "data" / "raw"
)

OUTPUT_DIR = (
    PROJECT_ROOT / "evaluation" / "results"
)

OUTPUT_FILE = (
    OUTPUT_DIR / "stage2_eval_queries.jsonl"
)

PARQUET_FILES = [
    RAW_DIR / "hitrain.parquet",
    RAW_DIR / "martrain.parquet",
]


def load_represented_queries():

    """
    Find query IDs actually represented in the
    200K embedded corpus.

    For each query ID we keep:
        - total chunks
        - selected chunks
        - languages
    """

    queries = defaultdict(
        lambda: {
            "chunks": 0,
            "selected": 0,
            "languages": set(),
        }
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

                queries[
                    query_id
                ]["chunks"] += 1

                if metadata.get(
                    "is_selected"
                ):

                    queries[
                        query_id
                    ]["selected"] += 1

                language = metadata.get(
                    "language"
                )

                if language:
                    queries[
                        query_id
                    ]["languages"].add(
                        language
                    )

        if index % 500 == 0:

            print(
                f"Processed "
                f"{index:,}/"
                f"{len(files):,} embedding files"
            )

    return queries


def load_query_texts(target_ids):

    """
    Read the original query text from the raw
    Parquet files, but only retain query IDs that
    actually occur in the 200K corpus.
    """

    found = {}

    print()
    print(
        f"Looking up {len(target_ids):,} "
        f"query IDs in raw Parquet data..."
    )

    for parquet_path in PARQUET_FILES:

        if not parquet_path.exists():

            print(
                f"WARNING: Missing "
                f"{parquet_path}"
            )

            continue

        print(
            f"Reading {parquet_path.name}"
        )

        parquet = pq.ParquetFile(
            parquet_path
        )

        for batch in parquet.iter_batches(
            batch_size=5000,
            columns=[
                "query_id",
                "query",
                "query_type",
                "source_lang",
            ],
        ):

            for row in batch.to_pylist():

                query_id = str(
                    row["query_id"]
                )

                if query_id not in target_ids:
                    continue

                query = (
                    row.get("query")
                    or ""
                ).strip()

                if not query:
                    continue

                if query_id not in found:

                    found[query_id] = {
                        "query_id": query_id,
                        "query": query,
                        "query_type": (
                            row.get(
                                "query_type"
                            )
                            or ""
                        ),
                        "source_lang": (
                            row.get(
                                "source_lang"
                            )
                            or ""
                        ),
                    }

    return found


def main():

    print("=" * 70)
    print(
        "BUILD STAGE 2 EVALUATION DATASET"
    )
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # 1. Inspect the actual 200K corpus
    # --------------------------------------------------------

    represented = (
        load_represented_queries()
    )

    print()
    print(
        f"Unique represented query IDs: "
        f"{len(represented):,}"
    )

    selected_queries = {
        query_id
        for query_id, stats
        in represented.items()
        if stats["selected"] > 0
    }

    print(
        f"Queries with selected chunks: "
        f"{len(selected_queries):,}"
    )

    # --------------------------------------------------------
    # 2. Get original query text
    # --------------------------------------------------------

    query_texts = load_query_texts(
        selected_queries
    )

    print(
        f"Query texts found: "
        f"{len(query_texts):,}"
    )

    # --------------------------------------------------------
    # 3. Build final evaluation set
    # --------------------------------------------------------

    final_records = []

    for query_id in sorted(
        query_texts,
        key=lambda x: int(x)
        if x.isdigit()
        else x,
    ):

        info = query_texts[
            query_id
        ]

        stats = represented[
            query_id
        ]

        final_records.append(
            {
                "query_id": query_id,
                "query": info["query"],
                "query_type": (
                    info["query_type"]
                ),
                "source_lang": (
                    info["source_lang"]
                ),
                "corpus_chunks": (
                    stats["chunks"]
                ),
                "selected_chunks": (
                    stats["selected"]
                ),
                "languages": sorted(
                    stats["languages"]
                ),
            }
        )

    # --------------------------------------------------------
    # 4. Save
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        for record in final_records:

            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )

    # --------------------------------------------------------
    # 5. Summary
    # --------------------------------------------------------

    language_counts = defaultdict(int)

    for record in final_records:

        for language in record[
            "languages"
        ]:

            language_counts[
                language
            ] += 1

    print()
    print("=" * 70)
    print(
        "STAGE 2 DATASET SUMMARY"
    )
    print("=" * 70)

    print(
        f"Represented queries : "
        f"{len(represented):,}"
    )

    print(
        f"Positive queries    : "
        f"{len(selected_queries):,}"
    )

    print(
        f"Queries with text   : "
        f"{len(query_texts):,}"
    )

    print()
    print(
        "Languages represented:"
    )

    for language, count in sorted(
        language_counts.items()
    ):

        print(
            f"  {language}: "
            f"{count:,}"
        )

    print()
    print(
        "Output:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "STAGE 2 DATASET BUILD COMPLETE"
    )


if __name__ == "__main__":
    main()