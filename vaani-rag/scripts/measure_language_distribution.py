import time

from ingestion.local_passage_stream import stream_all_passages
from ingestion.chunker import chunk_passage
from ingestion.config import CHUNKING_STRATEGY


SAMPLE_ROWS = 10_000


def main():
    print("=" * 70)
    print("VAANIRAG LANGUAGE DISTRIBUTION ESTIMATOR")
    print("=" * 70)

    print(f"\nSample rows per physical dataset: {SAMPLE_ROWS:,}")
    print("No embeddings will be generated.")
    print("No Pinecone/Qdrant upload will happen.")
    print("No checkpoint will be modified.")

    start = time.time()

    passage_counts = {
        "en": 0,
        "hi": 0,
        "mr": 0,
    }

    chunk_counts = {
        "en": 0,
        "hi": 0,
        "mr": 0,
    }

    token_counts = {
        "en": 0,
        "hi": 0,
        "mr": 0,
    }

    print("\nScanning sample...\n")

    for passage in stream_all_passages(
        max_rows_per_language=SAMPLE_ROWS,
        batch_size=1000,
    ):
        language = passage.language

        if language not in passage_counts:
            continue

        passage_counts[language] += 1

        chunks = chunk_passage(
            passage,
            strategy=CHUNKING_STRATEGY,
        )

        for chunk in chunks:
            chunk_counts[language] += 1
            token_counts[language] += chunk.token_count

        total_passages = sum(passage_counts.values())

        if total_passages % 1000 == 0:
            elapsed = time.time() - start

            print(
                f"Progress: {total_passages:,} passages | "
                f"{sum(chunk_counts.values()):,} chunks | "
                f"{elapsed:.1f}s"
            )

    elapsed = time.time() - start

    total_passages = sum(passage_counts.values())
    total_chunks = sum(chunk_counts.values())
    total_tokens = sum(token_counts.values())

    print("\n" + "=" * 70)
    print("SAMPLE RESULTS")
    print("=" * 70)

    print("\nPassages:")
    for language in ["en", "hi", "mr"]:
        print(
            f"  {language}: "
            f"{passage_counts[language]:,}"
        )

    print(
        f"  TOTAL: {total_passages:,}"
    )

    print("\nChunks:")
    for language in ["en", "hi", "mr"]:
        print(
            f"  {language}: "
            f"{chunk_counts[language]:,}"
        )

    print(
        f"  TOTAL: {total_chunks:,}"
    )

    print("\nTokens:")
    for language in ["en", "hi", "mr"]:
        print(
            f"  {language}: "
            f"{token_counts[language]:,}"
        )

    print(
        f"  TOTAL: {total_tokens:,}"
    )

    print("\n" + "=" * 70)
    print("LANGUAGE SHARE")
    print("=" * 70)

    for language in ["en", "hi", "mr"]:
        share = (
            chunk_counts[language] / total_chunks * 100
            if total_chunks
            else 0
        )

        print(
            f"{language}: "
            f"{share:.2f}%"
        )

    print("\n" + "=" * 70)
    print("1M VECTOR ALLOCATION")
    print("=" * 70)

    TARGET_VECTORS = 1_000_000

    for language in ["en", "hi", "mr"]:
        share = (
            chunk_counts[language] / total_chunks
            if total_chunks
            else 0
        )

        allocation = round(
            TARGET_VECTORS * share
        )

        print(
            f"{language}: "
            f"{allocation:,} vectors"
        )

    print(
        f"TOTAL: {TARGET_VECTORS:,} vectors"
    )

    print("\n" + "=" * 70)
    print("TIMING")
    print("=" * 70)

    print(
        f"Sample runtime: {elapsed:.2f} seconds"
    )

    print("\n" + "=" * 70)
    print("LANGUAGE DISTRIBUTION TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()