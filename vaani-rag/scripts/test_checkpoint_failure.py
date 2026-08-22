from ingestion.embedder import BGEM3Embedder
from ingestion.chunker import chunk_passage
from ingestion.embedding_store import EmbeddingBatchStore
from ingestion.batch_processor import BatchProcessor
from ingestion.checkpoint import (
    save_checkpoint,
    load_checkpoint,
    clear_checkpoint,
)
from ingestion.schemas import Passage


def main():

    print("=" * 70)
    print("VAANIRAG CHECKPOINT FAILURE/RECOVERY TEST")
    print("=" * 70)

    # ============================================================
    # CLEAN START
    # ============================================================

    clear_checkpoint()

    store = EmbeddingBatchStore()

    # Remove old test batches if they exist.
    for batch_id in [
        "failure_test_000001",
        "failure_test_000002",
    ]:
        path = store.batch_path(batch_id)

        if path.exists():
            path.unlink()

    # ============================================================
    # LOAD EMBEDDER
    # ============================================================

    print("\nLoading BGE-M3...")

    embedder = BGEM3Embedder()

    print(f"Device    : {embedder.get_device()}")
    print(f"Dimension : {embedder.get_dimension()}")

    processor = BatchProcessor(
        embedder=embedder,
        store=store,
    )

    # ============================================================
    # CREATE TEST CHUNKS
    # ============================================================

    print("\nCreating test chunks...")

    texts = [
        "Artificial intelligence is a field of computer science.",
        "Machine learning allows computers to learn from data.",
        "Natural language processing works with human language.",
        "Vector databases store embeddings for similarity search.",
    ]

    chunks = []

    for i, text in enumerate(texts):

        passage = Passage(
            passage_id=f"failure_test_passage_{i}",
            text=text,
            language="en",
            query_id=None,
            query_type=None,
            source_lang="eng_Latn",
            target_lang="eng_Latn",
            is_selected=False,
            original_record_index=i,
            content_hash=str(i) * 64,
        )

        passage_chunks = chunk_passage(
            passage,
            strategy="adaptive",
        )

        chunks.extend(passage_chunks)

    print(f"Chunks created: {len(chunks)}")

    # ============================================================
    # BATCH 1 — SHOULD SUCCEED
    # ============================================================

    batch1 = "failure_test_000001"

    print("\n" + "=" * 70)
    print("PHASE 1: PROCESSING SUCCESSFUL BATCH")
    print("=" * 70)

    result1 = processor.process_batch(
        chunks=chunks[:2],
        batch_id=batch1,
    )

    print(
        f"Batch 1 vectors: "
        f"{result1['vector_count']}"
    )

    save_checkpoint(
        dataset_name="failure_test",
        languages=["en"],
        chunking_strategy="adaptive",
        embedding_model="BAAI/bge-m3",
        embedding_dimension=1024,
        rows_processed={"en": 2},
        passages_processed={"en": 2},
        chunks_processed={"en": 2},
        vectors_uploaded={"en": 2},
        last_successful_batch={
            "batch_id": batch1,
            "vector_count": result1["vector_count"],
        },
        completed_batches=[batch1],
        status="running",
        run_id="failure_test",
    )

    print("Batch 1 checkpoint saved.")

    # ============================================================
    # VERIFY BATCH 1 CHECKPOINT
    # ============================================================

    checkpoint = load_checkpoint()

    assert checkpoint is not None
    assert batch1 in checkpoint["completed_batches"]

    print("Batch 1 checkpoint: PASSED")

    # ============================================================
    # BATCH 2 — INTENTIONAL FAILURE
    # ============================================================

    batch2 = "failure_test_000002"

    print("\n" + "=" * 70)
    print("PHASE 2: INTENTIONAL FAILURE")
    print("=" * 70)

    try:

        print(f"Processing {batch2}...")

        # These chunks represent the batch that will fail.
        bad_chunks = chunks[2:]

        print(
            f"Prepared {len(bad_chunks)} chunks "
            "for the failed batch."
        )

        # --------------------------------------------------------
        # INTENTIONAL FAILURE
        # --------------------------------------------------------
        #
        # We deliberately raise an exception BEFORE saving a
        # checkpoint for batch 2.
        #
        # This simulates a crash/error during real ingestion.
        #

        raise RuntimeError(
            "INTENTIONAL TEST FAILURE: "
            "simulated embedding failure"
        )

    except Exception as e:

        print(f"Expected failure caught: {e}")

        print(
            "IMPORTANT: batch 2 checkpoint will NOT be saved."
        )

    # ============================================================
    # VERIFY CHECKPOINT AFTER FAILURE
    # ============================================================

    print("\n" + "=" * 70)
    print("VERIFYING STATE AFTER FAILURE")
    print("=" * 70)

    checkpoint = load_checkpoint()

    assert checkpoint is not None

    completed = checkpoint["completed_batches"]

    print(f"Completed batches: {completed}")

    # Batch 1 must still be marked completed.
    assert batch1 in completed

    # Batch 2 must NOT be marked completed.
    assert batch2 not in completed

    print(
        "Failed batch NOT checkpointed: PASSED"
    )

    # ============================================================
    # SIMULATED RESTART
    # ============================================================

    print("\n" + "=" * 70)
    print("PHASE 3: SIMULATED RESTART")
    print("=" * 70)

    checkpoint = load_checkpoint()

    assert checkpoint is not None

    completed = set(
        checkpoint["completed_batches"]
    )

    # ------------------------------------------------------------
    # Batch 1 should be skipped.
    # ------------------------------------------------------------

    if batch1 in completed:

        print(
            f"SKIP {batch1} "
            "(already completed)"
        )

    else:

        print(
            f"ERROR: {batch1} "
            "would be repeated"
        )

    # ------------------------------------------------------------
    # Batch 2 should be resumed.
    # ------------------------------------------------------------

    if batch2 in completed:

        print(
            f"ERROR: {batch2} "
            "incorrectly marked completed"
        )

    else:

        print(
            f"RESUME {batch2} "
            "(correct behavior)"
        )

    assert batch1 in completed
    assert batch2 not in completed

    # ============================================================
    # ACTUALLY PROCESS BATCH 2 AFTER RECOVERY
    # ============================================================

    print("\nProcessing failed batch again...")

    result2 = processor.process_batch(
        chunks=chunks[2:],
        batch_id=batch2,
    )

    print(
        f"Batch 2 successfully recovered. "
        f"Vectors: {result2['vector_count']}"
    )

    # ============================================================
    # SAVE FINAL CHECKPOINT
    # ============================================================

    save_checkpoint(
        dataset_name="failure_test",
        languages=["en"],
        chunking_strategy="adaptive",
        embedding_model="BAAI/bge-m3",
        embedding_dimension=1024,
        rows_processed={"en": 4},
        passages_processed={"en": 4},
        chunks_processed={"en": 4},
        vectors_uploaded={
            "en": result1["vector_count"]
            + result2["vector_count"]
        },
        last_successful_batch={
            "batch_id": batch2,
            "vector_count": result2["vector_count"],
        },
        completed_batches=[
            batch1,
            batch2,
        ],
        status="completed",
        run_id="failure_test",
    )

    # ============================================================
    # FINAL VERIFICATION
    # ============================================================

    print("\n" + "=" * 70)
    print("FINAL VERIFICATION")
    print("=" * 70)

    final_checkpoint = load_checkpoint()

    assert final_checkpoint is not None

    final_batches = final_checkpoint[
        "completed_batches"
    ]

    print(
        f"Completed batches: "
        f"{final_batches}"
    )

    print(
        f"Final status: "
        f"{final_checkpoint['status']}"
    )

    # Both batches should now be completed.
    assert batch1 in final_batches
    assert batch2 in final_batches

    # Pipeline should be marked completed.
    assert (
        final_checkpoint["status"]
        == "completed"
    )

    # Both embedding batch files should exist.
    assert store.exists(batch1)
    assert store.exists(batch2)

    print("Batch 1 exists: PASSED")
    print(
        "Batch 2 recovered and exists: PASSED"
    )
    print(
        "Final checkpoint status: PASSED"
    )
    print(
        "Failure recovery logic: PASSED"
    )

    # ============================================================
    # CLEANUP
    # ============================================================

    clear_checkpoint()

    for batch_id in [
        batch1,
        batch2,
    ]:

        path = store.batch_path(batch_id)

        if path.exists():
            path.unlink()

    print("\n" + "=" * 70)
    print(
        "CHECKPOINT FAILURE/RECOVERY TEST PASSED"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()