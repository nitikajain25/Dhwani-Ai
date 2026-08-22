from ingestion.embedding_store import EmbeddingBatchStore
from ingestion.schemas import VectorRecord


def main():
    print("=" * 70)
    print("VAANIRAG EMBEDDING STORE TEST")
    print("=" * 70)

    store = EmbeddingBatchStore()

    batch_id = "test_batch_000001"

    records = [
        VectorRecord(
            id="test_vector_1",
            values=[0.1] * 1024,
            metadata={
                "language": "en",
                "text": "This is a test.",
            },
        ),
        VectorRecord(
            id="test_vector_2",
            values=[0.2] * 1024,
            metadata={
                "language": "hi",
                "text": "यह एक परीक्षण है।",
            },
        ),
    ]

    print("\n1. Saving batch...")

    path = store.save_batch(
        batch_id=batch_id,
        records=records,
    )

    print(f"Saved: {path}")

    print("\n2. Checking existence...")

    assert store.exists(batch_id)

    print("Batch exists: PASSED")

    print("\n3. Checking record count...")

    count = store.count_records(batch_id)

    print(f"Records: {count}")

    assert count == 2

    print("Record count: PASSED")

    print("\n4. Loading batch...")

    loaded = store.load_batch(batch_id)

    print(f"Loaded records: {len(loaded)}")

    assert len(loaded) == 2

    print("Load: PASSED")

    print("\n5. Validating vectors...")

    assert loaded[0].id == "test_vector_1"
    assert len(loaded[0].values) == 1024

    assert loaded[1].id == "test_vector_2"
    assert len(loaded[1].values) == 1024

    print("Vector validation: PASSED")

    print("\n" + "=" * 70)
    print("EMBEDDING STORE TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()