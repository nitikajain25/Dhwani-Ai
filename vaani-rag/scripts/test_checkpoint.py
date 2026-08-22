from ingestion.checkpoint import (
    save_checkpoint,
    load_checkpoint,
    clear_checkpoint,
)


def main():
    print("=" * 70)
    print("VAANIRAG CHECKPOINT TEST")
    print("=" * 70)

    clear_checkpoint()

    print("\n1. Saving checkpoint...")

    save_checkpoint(
        dataset_name="MSMARCO-XI-local",
        languages=["en", "hi", "mr"],
        chunking_strategy="adaptive",
        embedding_model="BAAI/bge-m3",
        embedding_dimension=1024,

        rows_processed={
            "hi": 10,
            "mr": 10,
        },

        passages_processed={
            "en": 98,
            "hi": 100,
            "mr": 100,
        },

        chunks_processed={
            "en": 98,
            "hi": 100,
            "mr": 100,
        },

        vectors_uploaded={
            "en": 98,
            "hi": 100,
            "mr": 100,
        },

        last_successful_batch={
            "language": "mr",
            "batch_id": "batch_000003",
        },

        completed_batches=[
            "batch_000000",
            "batch_000001",
            "batch_000002",
            "batch_000003",
        ],

        status="running",

        run_id="test-run-001",
    )

    print("Checkpoint saved.")

    print("\n2. Loading checkpoint...")

    checkpoint = load_checkpoint()

    if checkpoint is None:
        raise RuntimeError(
            "Checkpoint was not loaded."
        )

    print("Checkpoint loaded.")

    print("\n3. Verifying values...")

    assert checkpoint["dataset"] == "MSMARCO-XI-local"

    assert checkpoint["embedding_dimension"] == 1024

    assert checkpoint["rows_processed"]["hi"] == 10

    assert checkpoint["chunks_processed"]["en"] == 98

    assert checkpoint["status"] == "running"

    assert checkpoint["run_id"] == "test-run-001"

    assert len(checkpoint["completed_batches"]) == 4

    assert (
        checkpoint["last_successful_batch"]["batch_id"]
        == "batch_000003"
    )

    print("All checkpoint values verified.")

    print("\n4. Testing completed batches...")

    completed = set(
        checkpoint["completed_batches"]
    )

    assert "batch_000000" in completed
    assert "batch_000003" in completed
    assert "batch_000004" not in completed

    print("Completed batch tracking: PASSED")

    print("\n5. Clearing checkpoint...")

    clear_checkpoint()

    assert load_checkpoint() is None

    print("Checkpoint clearing: PASSED")

    print("\n" + "=" * 70)
    print("CHECKPOINT TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()