import json
from pathlib import Path
from collections import defaultdict

from ingestion.qdrant_client import get_qdrant_client
from ingestion.config import QDRANT_COLLECTION_NAME
from ingestion.embedder import BGEM3Embedder
from ingestion.retriever import QdrantRetriever


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EMBEDDINGS_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
)

QUERY_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "results"
    / "stage2_eval_queries.jsonl"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "evaluation"
    / "results"
)

RESULTS_FILE = (
    RESULTS_DIR
    / "stage2_results.jsonl"
)

METRICS_FILE = (
    RESULTS_DIR
    / "stage2_metrics.json"
)


# ============================================================
# SETTINGS
# ============================================================

TOP_K = 20

# ------------------------------------------------------------
# FIRST RUN:
#
# 50
#
# After the 50-query test succeeds, change to:
#
# None
#
# to evaluate all 4,124 queries.
# ------------------------------------------------------------

MAX_QUERIES = None


# ============================================================
# LOAD EVALUATION QUERIES
# ============================================================

def load_evaluation_queries():

    queries = {}

    if not QUERY_FILE.exists():

        raise FileNotFoundError(
            f"Evaluation query file not found:\n"
            f"{QUERY_FILE}"
        )

    with open(
        QUERY_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        for line in f:

            if not line.strip():
                continue

            record = json.loads(line)

            query_id = str(
                record["query_id"]
            )

            queries[query_id] = record

    return queries


# ============================================================
# BUILD GOLD CHUNK IDS
# ============================================================

def load_gold_chunk_ids(
    target_query_ids,
):

    """
    Read the actual 200K embedding records.

    A chunk is considered relevant when:

        metadata.query_id == evaluation query_id

    AND

        metadata.is_selected == True

    The actual chunk ID is stored as:

        record["id"]

    This gives us exact corpus-level relevance labels.
    """

    gold = defaultdict(set)

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

                if query_id not in target_query_ids:
                    continue

                if not metadata.get(
                    "is_selected",
                    False,
                ):
                    continue

                chunk_id = record.get(
                    "id"
                )

                if chunk_id:

                    gold[
                        query_id
                    ].add(
                        chunk_id
                    )

        if index % 500 == 0:

            print(
                f"Processed "
                f"{index:,}/"
                f"{len(files):,} embedding files"
            )

    return gold


# ============================================================
# EXTRACT RETRIEVED CHUNK ID
# ============================================================

def get_result_chunk_id(result):

    """
    Handle the QdrantRetriever result object.

    The project retriever should expose chunk_id.
    """

    chunk_id = getattr(
        result,
        "chunk_id",
        None,
    )

    if chunk_id:
        return str(chunk_id)

    # Fallback if the result exposes metadata.
    metadata = getattr(
        result,
        "metadata",
        None,
    )

    if isinstance(
        metadata,
        dict,
    ):

        chunk_id = metadata.get(
            "chunk_id"
        )

        if chunk_id:
            return str(chunk_id)

        vector_id = metadata.get(
            "vector_id"
        )

        if vector_id:
            return str(vector_id)

    return None


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    results,
):

    total = len(results)

    if total == 0:

        return {
            "queries": 0,
            "recall_at_5": 0.0,
            "recall_at_10": 0.0,
            "recall_at_20": 0.0,
            "mrr": 0.0,
            "language_stats": {},
        }

    hits_5 = 0
    hits_10 = 0
    hits_20 = 0

    reciprocal_rank_sum = 0.0

    language_stats = defaultdict(
        lambda: {
            "queries": 0,
            "hits_5": 0,
            "hits_10": 0,
            "hits_20": 0,
            "mrr_sum": 0.0,
        }
    )

    for item in results:

        retrieved = item[
            "results"
        ]

        first_relevant_rank = None

        for result in retrieved:

            if result[
                "relevant"
            ]:

                first_relevant_rank = (
                    result["rank"]
                )

                break

        if first_relevant_rank:

            reciprocal_rank = (
                1.0
                / first_relevant_rank
            )

        else:

            reciprocal_rank = 0.0

        reciprocal_rank_sum += (
            reciprocal_rank
        )

        hit_5 = any(
            r["relevant"]
            for r in retrieved[:5]
        )

        hit_10 = any(
            r["relevant"]
            for r in retrieved[:10]
        )

        hit_20 = any(
            r["relevant"]
            for r in retrieved[:20]
        )

        if hit_5:
            hits_5 += 1

        if hit_10:
            hits_10 += 1

        if hit_20:
            hits_20 += 1

        language = (
            item.get(
                "source_lang"
            )
            or "unknown"
        )

        stats = language_stats[
            language
        ]

        stats["queries"] += 1

        if hit_5:
            stats["hits_5"] += 1

        if hit_10:
            stats["hits_10"] += 1

        if hit_20:
            stats["hits_20"] += 1

        stats["mrr_sum"] += (
            reciprocal_rank
        )

    metrics = {
        "queries": total,
        "recall_at_5": (
            hits_5 / total
        ),
        "recall_at_10": (
            hits_10 / total
        ),
        "recall_at_20": (
            hits_20 / total
        ),
        "mrr": (
            reciprocal_rank_sum
            / total
        ),
        "language_stats": {},
    }

    for language, stats in (
        language_stats.items()
    ):

        count = stats[
            "queries"
        ]

        metrics[
            "language_stats"
        ][language] = {
            "queries": count,
            "recall_at_5": (
                stats["hits_5"]
                / count
            ),
            "recall_at_10": (
                stats["hits_10"]
                / count
            ),
            "recall_at_20": (
                stats["hits_20"]
                / count
            ),
            "mrr": (
                stats["mrr_sum"]
                / count
            ),
        }

    return metrics


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "VAANIRAG STAGE 2 "
        "CORPUS-SPECIFIC RETRIEVAL EVALUATION"
    )
    print("=" * 70)

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Load 4,124-query evaluation set
    # --------------------------------------------------------

    print()
    print(
        "Loading evaluation queries..."
    )

    queries = (
        load_evaluation_queries()
    )

    print(
        f"Evaluation queries available: "
        f"{len(queries):,}"
    )

    if not queries:

        raise RuntimeError(
            "No evaluation queries found."
        )

    # --------------------------------------------------------
    # Build exact gold chunk IDs
    # --------------------------------------------------------

    print()
    print(
        "Building exact gold chunk IDs "
        "from the 200K corpus..."
    )

    gold = load_gold_chunk_ids(
        set(queries.keys())
    )

    valid_query_ids = [
        query_id
        for query_id in queries
        if query_id in gold
        and gold[query_id]
    ]

    print()
    print(
        f"Queries with gold chunks: "
        f"{len(valid_query_ids):,}"
    )

    total_gold_chunks = sum(
        len(gold[query_id])
        for query_id in valid_query_ids
    )

    print(
        f"Total gold chunks: "
        f"{total_gold_chunks:,}"
    )

    # --------------------------------------------------------
    # Apply test limit
    # --------------------------------------------------------

    valid_query_ids = sorted(
        valid_query_ids,
        key=lambda x: (
            int(x)
            if x.isdigit()
            else x
        ),
    )

    if MAX_QUERIES is not None:

        valid_query_ids = (
            valid_query_ids[
                :MAX_QUERIES
            ]
        )

        print()
        print(
            f"LIMITED TEST: "
            f"{len(valid_query_ids)} queries"
        )

    else:

        print()
        print(
            f"FULL EVALUATION: "
            f"{len(valid_query_ids):,} queries"
        )

    # --------------------------------------------------------
    # Qdrant
    # --------------------------------------------------------

    print()
    print(
        "Connecting to Qdrant..."
    )

    client = get_qdrant_client()

    info = client.get_collection(
        QDRANT_COLLECTION_NAME
    )

    print(
        f"Qdrant points: "
        f"{info.points_count:,}"
    )

    print(
        f"Qdrant status: "
        f"{info.status}"
    )

    # --------------------------------------------------------
    # Embedder
    # --------------------------------------------------------

    print()
    print(
        "Loading BGE-M3..."
    )

    embedder = BGEM3Embedder(
        device="GPU"
    )

    print(
        f"Embedding dimension: "
        f"{embedder.get_dimension()}"
    )

    # --------------------------------------------------------
    # Retriever
    # --------------------------------------------------------

    retriever = QdrantRetriever(
        client=client,
        embedder=embedder,
    )

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    all_results = []

    print()
    print(
        "Starting retrieval..."
    )

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8",
    ) as output:

        for index, query_id in enumerate(
            valid_query_ids,
            start=1,
        ):

            query_record = queries[
                query_id
            ]

            query_text = (
                query_record["query"]
            )

            print()
            print(
                f"[{index}/"
                f"{len(valid_query_ids)}]"
            )

            print(
                f"Query ID: {query_id}"
            )

            print(
                f"Language: "
                f"{query_record.get('source_lang')}"
            )

            print(
                f"Query: "
                f"{query_text[:200]}"
            )

            retrieved = (
                retriever.search(
                    query=query_text,
                    top_k=TOP_K,
                )
            )

            evaluated = []

            gold_ids = gold[
                query_id
            ]

            for rank, result in enumerate(
                retrieved,
                start=1,
            ):

                chunk_id = (
                    get_result_chunk_id(
                        result
                    )
                )

                relevant = (
                    chunk_id in gold_ids
                )

                evaluated.append(
                    {
                        "rank": rank,
                        "score": float(
                            result.score
                        ),
                        "relevant": relevant,
                        "chunk_id": chunk_id,
                        "parent_passage_id": (
                            getattr(
                                result,
                                "parent_passage_id",
                                None,
                            )
                        ),
                        "language": (
                            getattr(
                                result,
                                "language",
                                None,
                            )
                        ),
                        "query_id": (
                            getattr(
                                result,
                                "query_id",
                                None,
                            )
                        ),
                        "text": (
                            getattr(
                                result,
                                "text",
                                ""
                            )
                        ),
                    }
                )

            item = {
                "query_id": query_id,
                "query": query_text,
                "source_lang": (
                    query_record.get(
                        "source_lang"
                    )
                ),
                "query_type": (
                    query_record.get(
                        "query_type"
                    )
                ),
                "gold_chunk_count": len(
                    gold_ids
                ),
                "results": evaluated,
            }

            all_results.append(
                item
            )

            output.write(
                json.dumps(
                    item,
                    ensure_ascii=False,
                )
                + "\n"
            )

            first_relevant = next(
                (
                    r["rank"]
                    for r in evaluated
                    if r["relevant"]
                ),
                None,
            )

            print(
                "First relevant rank:",
                (
                    first_relevant
                    if first_relevant
                    else "NOT FOUND"
                ),
            )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    metrics = calculate_metrics(
        all_results
    )

    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            metrics,
            f,
            indent=2,
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "STAGE 2 EVALUATION SUMMARY"
    )
    print("=" * 70)

    print(
        f"Queries evaluated : "
        f"{metrics['queries']:,}"
    )

    print(
        f"Recall@5          : "
        f"{metrics['recall_at_5']:.2%}"
    )

    print(
        f"Recall@10         : "
        f"{metrics['recall_at_10']:.2%}"
    )

    print(
        f"Recall@20         : "
        f"{metrics['recall_at_20']:.2%}"
    )

    print(
        f"MRR               : "
        f"{metrics['mrr']:.4f}"
    )

    print()
    print(
        "By source language:"
    )

    for language, stats in sorted(
        metrics[
            "language_stats"
        ].items()
    ):

        print(
            f"  {language}: "
            f"queries="
            f"{stats['queries']:,}, "
            f"R@5="
            f"{stats['recall_at_5']:.2%}, "
            f"R@10="
            f"{stats['recall_at_10']:.2%}, "
            f"R@20="
            f"{stats['recall_at_20']:.2%}, "
            f"MRR="
            f"{stats['mrr']:.4f}"
        )

    print()
    print(
        "Detailed results:"
    )

    print(
        RESULTS_FILE
    )

    print()
    print(
        "Metrics:"
    )

    print(
        METRICS_FILE
    )

    print()
    print(
        "STAGE 2 EVALUATION COMPLETE"
    )


if __name__ == "__main__":
    main()