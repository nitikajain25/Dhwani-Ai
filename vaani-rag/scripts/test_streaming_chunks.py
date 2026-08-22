from ingestion.local_passage_stream import stream_all_passages
from ingestion.chunker import chunk_passage
from ingestion.batch_stream import stream_batches
from ingestion.config import CHUNKING_STRATEGY


def stream_all_chunks(max_rows_per_language=5):
    """
    Converts the real passage stream into a streaming chunk stream.

    Important:
    We yield chunks one at a time instead of collecting the
    entire corpus in memory.
    """

    for passage in stream_all_passages(
        max_rows_per_language=max_rows_per_language,
        batch_size=2,
    ):
        chunks = chunk_passage(
            passage,
            strategy=CHUNKING_STRATEGY,
        )

        for chunk in chunks:
            yield chunk


def main():

    print("=" * 70)
    print("VAANIRAG REAL STREAMING CHUNK TEST")
    print("=" * 70)

    print("\nRows per language: 5")
    print("Batch size       : 16")

    chunk_stream = stream_all_chunks(
        max_rows_per_language=5,
    )

    total_chunks = 0
    total_batches = 0

    print("\nStreaming batches...\n")

    for batch_number, batch in enumerate(
        stream_batches(
            chunk_stream,
            batch_size=16,
        ),
        start=1,
    ):

        total_batches += 1
        total_chunks += len(batch)

        print(
            f"Batch {batch_number}: "
            f"{len(batch)} chunks"
        )

        print(
            f"  First chunk : {batch[0].chunk_id}"
        )

        print(
            f"  Last chunk  : {batch[-1].chunk_id}"
        )

    print("\n" + "=" * 70)
    print("STREAMING SUMMARY")
    print("=" * 70)

    print(f"Total chunks  : {total_chunks}")
    print(f"Total batches : {total_batches}")

    assert total_chunks > 0
    assert total_batches > 0

    print("\nSTREAMING CHUNK TEST PASSED")


if __name__ == "__main__":
    main()