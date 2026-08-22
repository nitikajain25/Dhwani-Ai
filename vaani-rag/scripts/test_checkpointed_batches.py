from ingestion.embedder import BGEM3Embedder
from ingestion.batch_processor import BatchProcessor
from ingestion.embedding_store import EmbeddingBatchStore
from ingestion.checkpoint import (
    save_checkpoint,
    load_checkpoint,
    clear_checkpoint,
)
from ingestion.local_passage_stream import stream_all_passages
from ingestion.chunker import chunk_passage
from ingestion.config import (
    EMBEDDING_MODEL,
    CHUNKING_STRATEGY,
)
from ingestion.logging_config import logger


DATASET_NAME = "MSMARCO-XI-local-test"
LANGUAGES = ["en", "hi", "mr"]


def collect_test_chunks(max_chunks=12):
    """
    Collect a small number of real chunks from the local dataset.
    """

    chunks = []

    for passage in stream_all_passages(
        max_rows_per_language=1,
        batch_size=2,
    ):
        passage_chunks = chunk_passage(passage)

        for chunk in passage_chunks:
            chunks.append(chunk)

            if len(chunks) >= max_chunks:
                return chunks

    return chunks


def main():

    print("=" * 70)
    print("VAANIRAG CHECKPOINTED BATCH TEST")
    print("=" * 70)

    # ------------------------------------------------------------
    # Clean previous test state
    # ------------------------------------------------------------

    clear_checkpoint()

    store = EmbeddingBatchStore()

    # Remove old test batches if present.
    for batch_number in range(1, 10):
        batch_id = f"checkpoint_test_{batch_number:06d}"

        path = store.batch_path(batch_id)

        if path.exists():
            path.unlink()

    # ------------------------------------------------------------
    # Load embedder
    # ------------------------------------------------------------

    print("\nLoading BGE-M3...")

    embedder = BGEM3Embedder()

    print(f"Device    : {embedder.get_device()}")
    print(f"Dimension : {embedder.get_dimension()}")

    processor = BatchProcessor(
        embedder=embedder,
        batch_size=32,
        store=store,
    )

    # ------------------------------------------------------------
    # Collect small real dataset sample
    # ------------------------------------------------------------

    print("\nCollecting real chunks...")

    chunks = collect_test_chunks(
        max_chunks=12
    )

    print(f"Chunks collected: {len(chunks)}")

    if len(chunks) < 12:
        raise RuntimeError(
            f"Expected at least 12 chunks, got {len(chunks)}"
        )

    # ------------------------------------------------------------
    # Divide into 3 small batches
    # ------------------------------------------------------------

    batch_size = 4

    batches = [
        chunks[0:4],
        chunks[4:8],
        chunks[8:12],
    ]

    print("\nTest batches:")
    print(f"Batch 1: {len(batches[0])} chunks")
    print(f"Batch 2: {len(batches[1])} chunks")
    print(f"Batch 3: {len(batches[2])} chunks")

    completed_batches = []

    rows_processed = {
        "hi": 0,
        "mr": 0,
    }

    passages_processed = {
        "en": 0,
        "hi": 0,
        "mr": 0,
    }

    chunks_processed = {
        "en": 0,
        "hi": 0,
        "mr": 0,
    }

    vectors_uploaded = {
        "en": 0,
        "hi": 0,
        "mr": 0,
    }

    # ------------------------------------------------------------
    # Process first two batches
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("PHASE 1: PROCESSING FIRST TWO BATCHES")
    print("=" * 70)

    for batch_number in range(1, 3):

        batch_id = (
            f"checkpoint_test_{batch_number:06d}"
        )

        batch_chunks = batches[batch_number - 1]

        print(
            f"\nProcessing {batch_id}..."
        )

        result = processor.process_batch(
            chunks=batch_chunks,
            batch_id=batch_id,
        )

        # The JSONL must exist before checkpointing.
        if not store.exists(batch_id):
            raise RuntimeError(
                f"Batch file missing: {batch_id}"
            )

        completed_batches.append(batch_id)

        for chunk in batch_chunks:
            chunks_processed[chunk.language] += 1
            vectors_uploaded[chunk.language] += 1

        save_checkpoint(
            dataset_name=DATASET_NAME,
            languages=LANGUAGES,
            chunking_strategy=CHUNKING_STRATEGY,
            embedding_model=EMBEDDING_MODEL,
            embedding_dimension=embedder.get_dimension(),
            rows_processed=rows_processed,
            passages_processed=passages_processed,
            chunks_processed=chunks_processed,
            vectors_uploaded=vectors_uploaded,
            last_successful_batch={
                "batch_id": batch_id,
                "vector_count": result["vector_count"],
            },
            completed_batches=completed_batches,
            status="running",
            run_id="checkpoint-test",
        )

        print(
            f"Completed: {batch_id}"
        )

    # ------------------------------------------------------------
    # Verify checkpoint
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("VERIFYING CHECKPOINT")
    print("=" * 70)

    checkpoint = load_checkpoint()

    if checkpoint is None:
        raise RuntimeError(
            "Checkpoint was not created."
        )

    saved_batches = checkpoint.get(
        "completed_batches",
        [],
    )

    print(
        "Completed batches:",
        saved_batches,
    )

    expected = [
        "checkpoint_test_000001",
        "checkpoint_test_000002",
    ]

    if saved_batches != expected:
        raise RuntimeError(
            f"Unexpected completed batches: "
            f"{saved_batches}"
        )

    print("Checkpoint tracking: PASSED")

    # ------------------------------------------------------------
    # Simulate restart
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("PHASE 2: SIMULATED RESTART")
    print("=" * 70)

    loaded_checkpoint = load_checkpoint()

    completed_after_restart = set(
        loaded_checkpoint.get(
            "completed_batches",
            [],
        )
    )

    # ------------------------------------------------------------
    # Resume remaining batches
    # ------------------------------------------------------------

    for batch_number in range(1, 4):

        batch_id = (
            f"checkpoint_test_{batch_number:06d}"
        )

        # Skip already completed batches.
        if batch_id in completed_after_restart:

            print(
                f"SKIP {batch_id} "
                f"(already completed)"
            )

            continue

        print(
            f"RESUME {batch_id}"
        )

        batch_chunks = batches[
            batch_number - 1
        ]

        result = processor.process_batch(
            chunks=batch_chunks,
            batch_id=batch_id,
        )

        if not store.exists(batch_id):
            raise RuntimeError(
                f"Batch file missing: {batch_id}"
            )

        completed_after_restart.add(
            batch_id
        )

        for chunk in batch_chunks:
            chunks_processed[chunk.language] += 1
            vectors_uploaded[chunk.language] += 1

        save_checkpoint(
            dataset_name=DATASET_NAME,
            languages=LANGUAGES,
            chunking_strategy=CHUNKING_STRATEGY,
            embedding_model=EMBEDDING_MODEL,
            embedding_dimension=embedder.get_dimension(),
            rows_processed=rows_processed,
            passages_processed=passages_processed,
            chunks_processed=chunks_processed,
            vectors_uploaded=vectors_uploaded,
            last_successful_batch={
                "batch_id": batch_id,
                "vector_count": result["vector_count"],
            },
            completed_batches=sorted(
                completed_after_restart
            ),
            status="completed",
            run_id="checkpoint-test",
        )

    # ------------------------------------------------------------
    # Final verification
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL VERIFICATION")
    print("=" * 70)

    final_checkpoint = load_checkpoint()

    final_batches = final_checkpoint.get(
        "completed_batches",
        [],
    )

    expected_final = [
        "checkpoint_test_000001",
        "checkpoint_test_000002",
        "checkpoint_test_000003",
    ]

    if final_batches != expected_final:
        raise RuntimeError(
            f"Final batch list incorrect: "
            f"{final_batches}"
        )

    for batch_id in expected_final:

        if not store.exists(batch_id):
            raise RuntimeError(
                f"Missing final batch: {batch_id}"
            )

        count = store.count_records(
            batch_id
        )

        if count != 4:
            raise RuntimeError(
                f"{batch_id} contains "
                f"{count} records instead of 4."
            )

    print(
        "All 3 batches exist: PASSED"
    )

    print(
        "Checkpoint resume logic: PASSED"
    )

    print(
        "Final checkpoint status:",
        final_checkpoint.get("status"),
    )

    print("\n" + "=" * 70)
    print("CHECKPOINTED BATCH TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()