from ingestion.batch_stream import stream_batches


def main():
    print("=" * 70)
    print("VAANIRAG BATCH STREAM TEST")
    print("=" * 70)

    items = iter(range(1, 11))

    batches = list(
        stream_batches(
            items,
            batch_size=3,
        )
    )

    print("\nBatches:")

    for i, batch in enumerate(batches, start=1):
        print(f"Batch {i}: {batch}")

    assert batches == [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [10],
    ]

    print("\nBatch sizes:")
    print([len(batch) for batch in batches])

    print("\nBATCH STREAM TEST PASSED")


if __name__ == "__main__":
    main()