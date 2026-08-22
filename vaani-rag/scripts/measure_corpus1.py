import sys
import time

from ingestion.local_passage_stream import stream_all_passages
from ingestion.chunker import chunk_passage
from ingestion.config import CHUNKING_STRATEGY


SAMPLE_ROWS = 10_000


def main():
    print("=" * 70)
    print("VAANIRAG FAST CORPUS SIZE ESTIMATOR")
    print("=" * 70)

    print(f"\nSampling approximately {SAMPLE_ROWS:,} rows per source dataset.")
    print("No embeddings will be generated.")
    print("No checkpoint will be modified.")
    print("No embedding files will be created.")

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

    total_passages = 0
    total_chunks = 0
    total_tokens = 0

    print("\nScanning sample...")

    for passage in stream_all_passages(
        max_rows_per_language=SAMPLE_ROWS,
        batch_size=1000,
    ):
        language = passage.language

        passage_counts[language] += 1
        total_passages += 1

        chunks = chunk_passage(
            passage,
            strategy=CHUNKING_STRATEGY,
        )

        for chunk in chunks:
            chunk_counts[language] += 1
            token_counts[language] += chunk.token_count

            total_chunks += 1
            total_tokens += chunk.token_count

        if total_passages % 1000 == 0:
            elapsed = time.time() - start

            print(
                f"Progress: {total_passages:,} passages | "
                f"{total_chunks:,} chunks | "
                f"{elapsed:.1f}s"
            )

    elapsed = time.time() - start

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

    average_tokens = (
        total_tokens / total_chunks
        if total_chunks
        else 0
    )

    chunks_per_passage = (
        total_chunks / total_passages
        if total_passages
        else 0
    )

    print(
        f"\nAverage tokens/chunk: "
        f"{average_tokens:.2f}"
    )

    print(
        f"Average chunks/passage: "
        f"{chunks_per_passage:.2f}"
    )

    # ------------------------------------------------------------
    # ESTIMATE COMPLETE DATASET
    # ------------------------------------------------------------

    # There are two physical datasets:
    #
    # Hindi dataset  = 778,638 rows
    # Marathi dataset = 765,873 rows
    #
    # Each dataset contributes up to SAMPLE_ROWS rows to this sample.

    total_source_rows = 778_638 + 765_873

    sample_source_rows = SAMPLE_ROWS * 2

    scale_factor = (
        total_source_rows / sample_source_rows
    )

    estimated_passages = total_passages * scale_factor
    estimated_chunks = total_chunks * scale_factor
    estimated_tokens = total_tokens * scale_factor

    print("\n" + "=" * 70)
    print("FULL CORPUS ESTIMATE")
    print("=" * 70)

    print(
        f"Physical source rows : "
        f"{total_source_rows:,}"
    )

    print(
        f"Estimated passages   : "
        f"{estimated_passages:,.0f}"
    )

    print(
        f"Estimated chunks     : "
        f"{estimated_chunks:,.0f}"
    )

    print(
        f"Estimated tokens     : "
        f"{estimated_tokens:,.0f}"
    )

    # ------------------------------------------------------------
    # VECTOR STORAGE
    # ------------------------------------------------------------

    # BGE-M3 = 1024 dimensions
    # float32 = 4 bytes

    raw_vector_bytes = (
        estimated_chunks * 1024 * 4
    )

    raw_vector_gb = (
        raw_vector_bytes / (1024 ** 3)
    )

    print("\n" + "=" * 70)
    print("VECTOR STORAGE ESTIMATE")
    print("=" * 70)

    print(
        f"Estimated vectors : "
        f"{estimated_chunks:,.0f}"
    )

    print(
        "Dimensions        : 1024"
    )

    print(
        f"Raw float32 data  : "
        f"{raw_vector_gb:.2f} GB"
    )

    print("\nPractical storage planning:")

    print(
        f"  2x overhead: "
        f"{raw_vector_gb * 2:.2f} GB"
    )

    print(
        f"  3x overhead: "
        f"{raw_vector_gb * 3:.2f} GB"
    )

    print(
        f"  4x overhead: "
        f"{raw_vector_gb * 4:.2f} GB"
    )

    print("\n" + "=" * 70)
    print("TIMING")
    print("=" * 70)

    print(
        f"Sample runtime: "
        f"{elapsed:.2f} seconds"
    )

    if elapsed > 0:
        estimated_full_seconds = (
            elapsed * scale_factor
        )

        print(
            f"Estimated full scan: "
            f"{estimated_full_seconds / 3600:.2f} hours"
        )

    print("\n" + "=" * 70)
    print("FAST CORPUS ESTIMATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()