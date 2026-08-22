from ingestion.local_passage_stream import stream_all_passages
from ingestion.chunker import chunk_passage
from ingestion.config import CHUNKING_STRATEGY


def main():
    print("=" * 70)
    print("VAANIRAG FULL CORPUS SIZE ESTIMATION")
    print("=" * 70)

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

    print("\nScanning corpus...")
    print("IMPORTANT: This does NOT generate embeddings.")

    for passage in stream_all_passages(
        max_rows_per_language=None,
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

        if total_passages % 10000 == 0:
            print(
                f"Passages scanned: {total_passages:,} | "
                f"Chunks: {total_chunks:,}"
            )

    print("\n" + "=" * 70)
    print("CORPUS RESULTS")
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

    if total_chunks:
        average_tokens = total_tokens / total_chunks
    else:
        average_tokens = 0

    print(
        f"\nAverage tokens/chunk: "
        f"{average_tokens:.2f}"
    )

    # ------------------------------------------------------------
    # VECTOR SIZE
    # ------------------------------------------------------------

    # float32 = 4 bytes
    raw_vector_bytes = total_chunks * 1024 * 4

    # Approximate vector-only storage.
    # Real DB storage will be higher because of indexes,
    # metadata, IDs, etc.
    raw_vector_gb = raw_vector_bytes / (1024 ** 3)

    print("\n" + "=" * 70)
    print("VECTOR STORAGE ESTIMATE")
    print("=" * 70)

    print(
        f"Vectors required : {total_chunks:,}"
    )

    print(
        f"Dimensions       : 1024"
    )

    print(
        f"Raw float32 size : "
        f"{raw_vector_bytes / (1024 ** 2):.2f} MB"
    )

    print(
        f"Raw vector size  : "
        f"{raw_vector_gb:.2f} GB"
    )

    # ------------------------------------------------------------
    # SAFETY ESTIMATES
    # ------------------------------------------------------------

    print("\nEstimated practical DB storage:")
    print(
        f"  2x raw vectors : "
        f"{raw_vector_gb * 2:.2f} GB"
    )

    print(
        f"  3x raw vectors : "
        f"{raw_vector_gb * 3:.2f} GB"
    )

    print(
        f"  4x raw vectors : "
        f"{raw_vector_gb * 4:.2f} GB"
    )

    print("\n" + "=" * 70)
    print("CORPUS MEASUREMENT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()