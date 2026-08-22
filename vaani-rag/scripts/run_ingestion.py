from collections import defaultdict

from ingestion.local_passage_stream import stream_all_passages
from ingestion.chunker import chunk_passage
from ingestion.batch_stream import stream_batches
from ingestion.embedder import BGEM3Embedder
from ingestion.embedding_store import EmbeddingBatchStore
from ingestion.batch_processor import BatchProcessor
from ingestion.checkpoint import (
    save_checkpoint,
    load_checkpoint,
)
from ingestion.qdrant_client import get_qdrant_client
from ingestion.qdrant_store import ensure_collection
from ingestion.qdrant_uploader import upload_vectors_to_qdrant
from ingestion.config import (
    CHUNKING_STRATEGY,
    EMBEDDING_MODEL,
    MAX_ROWS_PER_LANGUAGE,
    QDRANT_COLLECTION_NAME,
)
from ingestion.logging_config import logger


# ============================================================
# PRODUCTION SETTINGS
# ============================================================

BATCH_SIZE = 16

RUN_ID = "vaani_ingestion"

TARGET_TOTAL_VECTORS = 200_000

# Approximate multilingual distribution.
LANGUAGE_TARGETS = {
    "en": 66_667,
    "hi": 66_667,
    "mr": 66_666,
}


# ============================================================
# CHUNK STREAM
# ============================================================

def stream_all_chunks(
    start_rows,
    progress_callback,
    language_counts,
):
    """
    Converts the passage stream into a streaming chunk stream.

    The stream never loads the corpus into RAM.

    language_counts tracks how many chunks have already
    been accepted for each language.
    """

    for passage in stream_all_passages(
        max_rows_per_language=MAX_ROWS_PER_LANGUAGE,
        batch_size=2,
        start_rows=start_rows,
        progress_callback=progress_callback,
    ):

        language = passage.language

        # ----------------------------------------------------
        # Stop accepting chunks for a language once its
        # target has been reached.
        # ----------------------------------------------------

        if language_counts[language] >= LANGUAGE_TARGETS[language]:
            continue

        chunks = chunk_passage(
            passage,
            strategy=CHUNKING_STRATEGY,
        )

        for chunk in chunks:

            if (
                language_counts[language]
                >= LANGUAGE_TARGETS[language]
            ):
                break

            yield chunk


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("VAANIRAG PRODUCTION QDRANT INGESTION")
    print("=" * 70)

    print(
        f"\nTarget vectors    : {TARGET_TOTAL_VECTORS:,}"
    )

    print(
        f"English target    : {LANGUAGE_TARGETS['en']:,}"
    )

    print(
        f"Hindi target      : {LANGUAGE_TARGETS['hi']:,}"
    )

    print(
        f"Marathi target    : {LANGUAGE_TARGETS['mr']:,}"
    )

    print(
        f"Chunking strategy : {CHUNKING_STRATEGY}"
    )

    print(
        f"Batch size        : {BATCH_SIZE}"
    )

    # ========================================================
    # LOAD CHECKPOINT
    # ========================================================

    checkpoint = load_checkpoint()

    if checkpoint is None:

        source_rows = {
            "hi": 0,
            "mr": 0,
        }

        completed_batches = set()

        language_counts = defaultdict(int)

        print(
            "\nNo previous checkpoint found."
        )

        print(
            "Starting a new ingestion run."
        )

    else:

        source_rows = checkpoint.get(
            "rows_processed",
            {},
        )

        source_rows = {
            "hi": int(
                source_rows.get("hi", 0)
            ),
            "mr": int(
                source_rows.get("mr", 0)
            ),
        }

        completed_batches = set(
            checkpoint.get(
                "completed_batches",
                [],
            )
        )

        saved_language_counts = (
            checkpoint.get(
                "language_chunks",
                {},
            )
        )

        language_counts = defaultdict(
            int,
            {
                "en": int(
                    saved_language_counts.get(
                        "en",
                        0,
                    )
                ),
                "hi": int(
                    saved_language_counts.get(
                        "hi",
                        0,
                    )
                ),
                "mr": int(
                    saved_language_counts.get(
                        "mr",
                        0,
                    )
                ),
            },
        )

        print(
            "\nResuming previous run."
        )

        print(
            f"Completed batches: "
            f"{len(completed_batches)}"
        )

        print(
            f"Saved source rows: "
            f"{source_rows}"
        )

        print(
            f"Saved language chunks: "
            f"{dict(language_counts)}"
        )

    # ========================================================
    # SOURCE PROGRESS
    # ========================================================

    current_source_rows = dict(
        source_rows
    )

    def on_source_progress(
        dataset: str,
        next_row: int,
    ):
        """
        Called after a physical source row has been
        completely consumed.

        This is kept in memory until the corresponding
        Qdrant batch succeeds.
        """

        current_source_rows[
            dataset
        ] = next_row

    # ========================================================
    # CONNECT TO QDRANT
    # ========================================================

    print(
        "\nConnecting to Qdrant..."
    )

    qdrant_client = (
        get_qdrant_client()
    )

    ensure_collection(
        qdrant_client,
        QDRANT_COLLECTION_NAME,
    )

    print(
        "Qdrant connection : OK"
    )

    print(
        f"Collection         : "
        f"{QDRANT_COLLECTION_NAME}"
    )

    # ========================================================
    # LOAD EMBEDDER
    # ========================================================

    print(
        "\nLoading BGE-M3..."
    )

    embedder = BGEM3Embedder()

    print(
        f"Device    : "
        f"{embedder.get_device()}"
    )

    print(
        f"Dimension : "
        f"{embedder.get_dimension()}"
    )

    if embedder.get_dimension() != 1024:
        raise ValueError(
            "BGE-M3 dimension mismatch. "
            "Expected 1024."
        )

    # ========================================================
    # STORAGE + PROCESSOR
    # ========================================================

    store = EmbeddingBatchStore()

    processor = BatchProcessor(
        embedder=embedder,
        store=store,
    )

    # ========================================================
    # STREAM
    # ========================================================

    print(
        "\nStarting streaming pipeline..."
    )

    chunk_stream = stream_all_chunks(
        start_rows=source_rows,
        progress_callback=on_source_progress,
        language_counts=language_counts,
    )

    total_seen = 0
    total_uploaded = sum(
        language_counts.values()
    )

    skipped_chunks = 0

    batch_number = 0

    # ========================================================
    # PROCESS BATCHES
    # ========================================================

    for batch in stream_batches(
        chunk_stream,
        batch_size=BATCH_SIZE,
    ):

        # ----------------------------------------------------
        # Check total target
        # ----------------------------------------------------

        remaining = (
            TARGET_TOTAL_VECTORS
            - total_uploaded
        )

        if remaining <= 0:
            break

        # ----------------------------------------------------
        # Trim final batch if necessary
        # ----------------------------------------------------

        if len(batch) > remaining:

            batch = batch[
                :remaining
            ]

        if not batch:
            break

        batch_number += 1

        batch_id = (
            f"vaani_batch_"
            f"{batch_number:06d}"
        )

        total_seen += len(batch)

        print(
            "\n" + "-" * 70
        )

        print(
            f"Batch {batch_number}"
        )

        print(
            f"Batch ID : {batch_id}"
        )

        print(
            f"Chunks   : {len(batch)}"
        )

        # ----------------------------------------------------
        # Count language composition
        # ----------------------------------------------------

        batch_language_counts = (
            defaultdict(int)
        )

        for chunk in batch:

            batch_language_counts[
                chunk.language
            ] += 1

        print(
            "Languages: "
            f"{dict(batch_language_counts)}"
        )

        # ----------------------------------------------------
        # SKIP COMPLETED BATCH
        # ----------------------------------------------------

        if batch_id in completed_batches:

            skipped_chunks += len(batch)

            print(
                f"SKIP {batch_id} "
                "(already completed)"
            )

            continue

        # ====================================================
        # 1. EMBEDDING + LOCAL BACKUP
        # ====================================================

        try:

            result = (
                processor.process_batch(
                    chunks=batch,
                    batch_id=batch_id,
                )
            )

            vector_count = result[
                "vector_count"
            ]

            print(
                "Local embedding batch: "
                f"{vector_count} vectors"
            )

            # =================================================
            # 2. LOAD THE EXACT LOCAL BATCH
            # =================================================

            records = store.load_batch(
                batch_id
            )

            if len(records) != vector_count:

                raise RuntimeError(
                    "Local embedding batch "
                    "count mismatch: "
                    f"expected {vector_count}, "
                    f"found {len(records)}"
                )

            # =================================================
            # 3. UPLOAD TO QDRANT
            # =================================================

            print(
                "Uploading to Qdrant..."
            )

            upload_result = (
                upload_vectors_to_qdrant(
                    client=qdrant_client,
                    vectors=records,
                    namespace="vaani",
                    batch_size=64,
                )
            )

            uploaded = upload_result[
                "uploaded"
            ]

            failed = upload_result[
                "failed"
            ]

            print(
                f"Qdrant attempted : "
                f"{upload_result['attempted']}"
            )

            print(
                f"Qdrant uploaded  : "
                f"{uploaded}"
            )

            print(
                f"Qdrant failed    : "
                f"{failed}"
            )

            if (
                failed != 0
                or uploaded != vector_count
            ):

                raise RuntimeError(
                    "Qdrant upload verification "
                    "failed."
                )

            # =================================================
            # 4. ONLY NOW UPDATE COUNTERS
            # =================================================

            for language, count in (
                batch_language_counts.items()
            ):

                language_counts[
                    language
                ] += count

            total_uploaded = sum(
                language_counts.values()
            )

            completed_batches.add(
                batch_id
            )

            source_rows = dict(
                current_source_rows
            )

            # =================================================
            # 5. CHECKPOINT
            # =================================================

            save_checkpoint(
                dataset_name="MSMARCO-XI",

                languages=[
                    "en",
                    "hi",
                    "mr",
                ],

                chunking_strategy=(
                    CHUNKING_STRATEGY
                ),

                embedding_model=(
                    EMBEDDING_MODEL
                ),

                embedding_dimension=(
                    embedder.get_dimension()
                ),

                rows_processed=(
                    source_rows
                ),

                passages_processed={},

                chunks_processed={
                    "en": language_counts["en"],
                    "hi": language_counts["hi"],
                    "mr": language_counts["mr"],
                    "total": total_uploaded,
                },

                vectors_uploaded={
                    "en": language_counts["en"],
                    "hi": language_counts["hi"],
                    "mr": language_counts["mr"],
                    "total": total_uploaded,
                },

                last_successful_batch={
                    "batch_id": batch_id,
                    "vector_count": vector_count,
                },

                completed_batches=sorted(
                    completed_batches
                ),

                status="running",

                run_id=RUN_ID,
            )

            print(
                "\nBatch completed and "
                "checkpointed."
            )

            print(
                f"Progress: "
                f"{total_uploaded:,} / "
                f"{TARGET_TOTAL_VECTORS:,}"
            )

            print(
                f"EN={language_counts['en']:,} "
                f"HI={language_counts['hi']:,} "
                f"MR={language_counts['mr']:,}"
            )

        except Exception as e:

            logger.exception(
                f"Batch {batch_id} failed."
            )

            print(
                f"\nERROR processing "
                f"{batch_id}: {e}"
            )

            print(
                "Checkpoint was NOT advanced "
                "for this batch."
            )

            print(
                "The local embedding batch "
                "may already exist."
            )

            print(
                "The next run will retry "
                "the batch."
            )

            raise

    # ========================================================
    # FINAL STATUS
    # ========================================================

    final_total = sum(
        language_counts.values()
    )

    final_source_rows = dict(
        current_source_rows
    )

    completed = (
        final_total
        >= TARGET_TOTAL_VECTORS
    )

    save_checkpoint(
        dataset_name="MSMARCO-XI",

        languages=[
            "en",
            "hi",
            "mr",
        ],

        chunking_strategy=(
            CHUNKING_STRATEGY
        ),

        embedding_model=(
            EMBEDDING_MODEL
        ),

        embedding_dimension=(
            embedder.get_dimension()
        ),

        rows_processed=(
            final_source_rows
        ),

        passages_processed={},

        chunks_processed={
            "en": language_counts["en"],
            "hi": language_counts["hi"],
            "mr": language_counts["mr"],
            "total": final_total,
        },

        vectors_uploaded={
            "en": language_counts["en"],
            "hi": language_counts["hi"],
            "mr": language_counts["mr"],
            "total": final_total,
        },

        last_successful_batch={
            "batch_id": (
                f"vaani_batch_"
                f"{batch_number:06d}"
                if batch_number
                else None
            ),
            "vector_count": (
                total_seen
            ),
        },

        completed_batches=sorted(
            completed_batches
        ),

        status=(
            "completed"
            if completed
            else "running"
        ),

        run_id=RUN_ID,
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "INGESTION SUMMARY"
    )

    print(
        "=" * 70
    )

    print(
        f"Target vectors     : "
        f"{TARGET_TOTAL_VECTORS:,}"
    )

    print(
        f"Vectors uploaded   : "
        f"{final_total:,}"
    )

    print(
        f"English vectors    : "
        f"{language_counts['en']:,}"
    )

    print(
        f"Hindi vectors      : "
        f"{language_counts['hi']:,}"
    )

    print(
        f"Marathi vectors    : "
        f"{language_counts['mr']:,}"
    )

    print(
        f"Skipped chunks     : "
        f"{skipped_chunks:,}"
    )

    print(
        f"Batches completed  : "
        f"{len(completed_batches):,}"
    )

    print(
        f"Source rows        : "
        f"{final_source_rows}"
    )

    if completed:

        print(
            "\nINGESTION RUN COMPLETE"
        )

    else:

        print(
            "\nINGESTION RUN STOPPED "
            "BEFORE TARGET."
        )

        print(
            "Run the same command again "
            "to resume."
        )


if __name__ == "__main__":
    main()