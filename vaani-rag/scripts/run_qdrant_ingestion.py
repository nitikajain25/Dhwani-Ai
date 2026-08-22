import time

from ingestion.local_passage_stream import stream_all_passages
from ingestion.chunker import chunk_passage
from ingestion.batch_stream import stream_batches
from ingestion.embedder import BGEM3Embedder
from ingestion.embedding_store import EmbeddingBatchStore
from ingestion.batch_processor import BatchProcessor
from ingestion.qdrant_client import get_qdrant_client
from ingestion.qdrant_store import (
    ensure_collection,
    upload_vectors,
)
from ingestion.checkpoint import (
    save_checkpoint,
    load_checkpoint,
)
from ingestion.config import (
    CHUNKING_STRATEGY,
    EMBEDDING_MODEL,
    MAX_ROWS_PER_LANGUAGE,
    QDRANT_COLLECTION_NAME,
)
from ingestion.logging_config import logger


# ============================================================
# SAFE FIRST PRODUCTION TEST
# ============================================================

BATCH_SIZE = 16

# We deliberately start with 1,000 vectors.
# After validation, this can be increased to 1,000,000.
TARGET_VECTORS = 1000

RUN_ID = "vaani_qdrant_1m"


# ============================================================
# STREAM CHUNKS
# ============================================================

def stream_all_chunks(
    start_rows,
    progress_callback,
):
    """
    Convert resumable passages into a streaming chunk stream.

    Only the current passage/chunks are held in memory.
    """

    for passage in stream_all_passages(
        max_rows_per_language=MAX_ROWS_PER_LANGUAGE,
        batch_size=BATCH_SIZE,
        start_rows=start_rows,
        progress_callback=progress_callback,
    ):

        chunks = chunk_passage(
            passage,
            strategy=CHUNKING_STRATEGY,
        )

        for chunk in chunks:
            yield chunk


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("VAANIRAG QDRANT PRODUCTION INGESTION")
    print("=" * 70)

    print(
        f"\nRows per language : "
        f"{MAX_ROWS_PER_LANGUAGE}"
    )

    print(
        f"Batch size        : "
        f"{BATCH_SIZE}"
    )

    print(
        f"Target vectors    : "
        f"{TARGET_VECTORS}"
    )

    print(
        f"Qdrant collection : "
        f"{QDRANT_COLLECTION_NAME}"
    )

    print(
        f"Run ID            : "
        f"{RUN_ID}"
    )

    # ========================================================
    # LOAD CHECKPOINT
    # ========================================================

    checkpoint = load_checkpoint()

    # --------------------------------------------------------
    # IMPORTANT:
    # Only use the checkpoint if it belongs to this runner.
    # --------------------------------------------------------

    if (
        checkpoint is not None
        and checkpoint.get("run_id") == RUN_ID
    ):

        start_rows = checkpoint.get(
            "rows_processed",
            {
                "hi": 0,
                "mr": 0,
            },
        )

        completed_batches = set(
            checkpoint.get(
                "completed_batches",
                [],
            )
        )

        vectors_uploaded = (
            checkpoint
            .get("vectors_uploaded", {})
            .get("total", 0)
        )

        chunks_uploaded = (
            checkpoint
            .get("chunks_processed", {})
            .get("total", 0)
        )

        print(
            "\nResuming Qdrant ingestion."
        )

        print(
            f"Saved source rows: "
            f"{start_rows}"
        )

        print(
            f"Completed batches: "
            f"{len(completed_batches)}"
        )

        print(
            f"Saved vectors: "
            f"{vectors_uploaded}"
        )

    else:

        start_rows = {
            "hi": 0,
            "mr": 0,
        }

        completed_batches = set()

        vectors_uploaded = 0

        chunks_uploaded = 0

        print(
            "\nNo Qdrant checkpoint found."
        )

        print(
            "Starting a new Qdrant ingestion run."
        )

    # ========================================================
    # CONNECT TO QDRANT
    # ========================================================

    print(
        "\nConnecting to Qdrant..."
    )

    qdrant = get_qdrant_client()

    ensure_collection(
        qdrant,
        QDRANT_COLLECTION_NAME,
    )

    print(
        "Qdrant collection ready."
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

    # ========================================================
    # LOCAL TEMPORARY EMBEDDING STORE
    # ========================================================

    store = EmbeddingBatchStore()

    processor = BatchProcessor(
        embedder=embedder,
        store=store,
    )

    # ========================================================
    # SOURCE PROGRESS
    # ========================================================

    current_source_rows = dict(
        start_rows
    )

    def progress_callback(
        source_dataset,
        next_row,
    ):
        """
        Receives the next physical source row.

        This is kept in memory until the corresponding
        Qdrant batch has successfully uploaded.
        """

        current_source_rows[
            source_dataset
        ] = next_row

    # ========================================================
    # CREATE STREAM
    # ========================================================

    print(
        "\nStarting resumable streaming pipeline..."
    )

    chunk_stream = stream_all_chunks(
        start_rows=start_rows,
        progress_callback=progress_callback,
    )

    # ========================================================
    # PROCESS BATCHES
    # ========================================================

    batch_number = 0

    started_at = time.time()

    for batch in stream_batches(
        chunk_stream,
        batch_size=BATCH_SIZE,
    ):

        # ----------------------------------------------------
        # Stop once target reached.
        # ----------------------------------------------------

        if vectors_uploaded >= TARGET_VECTORS:

            print(
                "\nTarget vector count reached."
            )

            break

        batch_number += 1

        batch_id = (
            f"qdrant_batch_{batch_number:06d}"
        )

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
        # LIMIT FINAL BATCH
        # ----------------------------------------------------

        remaining = (
            TARGET_VECTORS
            - vectors_uploaded
        )

        if len(batch) > remaining:

            batch = batch[:remaining]

            print(
                f"Limited batch to "
                f"{remaining} chunks."
            )

        if not batch:
            break

        # ----------------------------------------------------
        # PROCESS EMBEDDINGS
        # ----------------------------------------------------

        try:

            result = processor.process_batch(
                chunks=batch,
                batch_id=batch_id,
            )

            vector_count = result[
                "vector_count"
            ]

            print(
                f"Embeddings generated: "
                f"{vector_count}"
            )

            # ------------------------------------------------
            # LOAD VECTOR RECORDS
            # ------------------------------------------------

            vectors = store.load_batch(
                batch_id
            )

            if len(vectors) != vector_count:

                raise RuntimeError(
                    f"Vector count mismatch. "
                    f"Processor created "
                    f"{vector_count}, but store "
                    f"contains {len(vectors)}."
                )

            # ------------------------------------------------
            # UPLOAD TO QDRANT
            # ------------------------------------------------

            print(
                "Uploading to Qdrant..."
            )

            upload_result = upload_vectors(
                client=qdrant,
                collection_name=(
                    QDRANT_COLLECTION_NAME
                ),
                vectors=vectors,
                batch_size=BATCH_SIZE,
            )

            uploaded = upload_result[
                "uploaded"
            ]

            failed = upload_result[
                "failed"
            ]

            print(
                f"Uploaded : {uploaded}"
            )

            print(
                f"Failed   : {failed}"
            )

            if failed != 0:

                raise RuntimeError(
                    f"Qdrant upload failed "
                    f"for {batch_id}."
                )

            if uploaded != vector_count:

                raise RuntimeError(
                    f"Qdrant upload count mismatch. "
                    f"Expected {vector_count}, "
                    f"uploaded {uploaded}."
                )

            # ------------------------------------------------
            # UPDATE COUNTERS
            # ------------------------------------------------

            vectors_uploaded += uploaded

            chunks_uploaded += len(
                batch
            )

            completed_batches.add(
                batch_id
            )

            # ------------------------------------------------
            # CHECKPOINT
            #
            # IMPORTANT:
            # Source progress is saved ONLY after
            # Qdrant successfully received the batch.
            # ------------------------------------------------

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
                rows_processed={
                    "hi": current_source_rows.get(
                        "hi",
                        0,
                    ),
                    "mr": current_source_rows.get(
                        "mr",
                        0,
                    ),
                },
                passages_processed={},
                chunks_processed={
                    "total": chunks_uploaded
                },
                vectors_uploaded={
                    "total": vectors_uploaded
                },
                last_successful_batch={
                    "batch_id": batch_id,
                    "vector_count": uploaded,
                },
                completed_batches=sorted(
                    completed_batches
                ),
                status="running",
                run_id=RUN_ID,
            )

            print(
                "Qdrant upload: PASSED"
            )

            print(
                "Checkpoint: PASSED"
            )

            print(
                f"Total vectors: "
                f"{vectors_uploaded}"
            )

        except Exception as e:

            logger.exception(
                f"Batch {batch_id} failed."
            )

            print(
                "\nERROR:"
            )

            print(e)

            print(
                "\nCheckpoint was NOT advanced "
                "for this failed batch."
            )

            print(
                "The batch will be retried "
                "on the next run."
            )

            raise

    # ========================================================
    # FINAL CHECKPOINT
    # ========================================================

    elapsed = (
        time.time()
        - started_at
    )

    last_batch = (
        sorted(completed_batches)[-1]
        if completed_batches
        else None
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
        rows_processed={
            "hi": current_source_rows.get(
                "hi",
                0,
            ),
            "mr": current_source_rows.get(
                "mr",
                0,
            ),
        },
        passages_processed={},
        chunks_processed={
            "total": chunks_uploaded
        },
        vectors_uploaded={
            "total": vectors_uploaded
        },
        last_successful_batch={
            "batch_id": last_batch,
            "vector_count": (
                vectors_uploaded
            ),
        },
        completed_batches=sorted(
            completed_batches
        ),
        status="completed",
        run_id=RUN_ID,
    )

    # ========================================================
    # VERIFY QDRANT
    # ========================================================

    info = qdrant.get_collection(
        QDRANT_COLLECTION_NAME
    )

    qdrant_count = info.points_count

    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "QDRANT INGESTION SUMMARY"
    )

    print(
        "=" * 70
    )

    print(
        f"Vectors uploaded : "
        f"{vectors_uploaded}"
    )

    print(
        f"Qdrant points    : "
        f"{qdrant_count}"
    )

    print(
        f"Source rows      : "
        f"{current_source_rows}"
    )

    print(
        f"Completed batches: "
        f"{len(completed_batches)}"
    )

    print(
        f"Elapsed seconds  : "
        f"{elapsed:.2f}"
    )

    if qdrant_count < vectors_uploaded:

        print(
            "\nWARNING: Qdrant count is "
            "lower than uploaded count."
        )

    else:

        print(
            "\nQDRANT INGESTION TEST COMPLETE"
        )


if __name__ == "__main__":
    main()