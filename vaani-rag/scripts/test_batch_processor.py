from ingestion.batch_processor import BatchProcessor
from ingestion.embedder import BGEM3Embedder
from ingestion.chunker import chunk_passage
from ingestion.local_passage_stream import stream_all_passages
from ingestion.logging_config import logger


def main():
    print("=" * 70)
    print("VAANIRAG BATCH PROCESSOR TEST")
    print("=" * 70)

    # ------------------------------------------------------------
    # 1. Load embedder
    # ------------------------------------------------------------

    print("\nLoading BGE-M3 embedder...")

    embedder = BGEM3Embedder()

    print(f"Device    : {embedder.get_device()}")
    print(f"Dimension : {embedder.dimension}")

    # ------------------------------------------------------------
    # 2. Read a tiny amount of real data
    # ------------------------------------------------------------

    print("\nReading real passages...")

    passages = []

    for passage in stream_all_passages(
        max_rows_per_language=1,
        batch_size=2,
    ):
        passages.append(passage)

        if len(passages) >= 3:
            break

    print(f"Passages collected: {len(passages)}")

    # ------------------------------------------------------------
    # 3. Chunk passages
    # ------------------------------------------------------------

    chunks = []

    for passage in passages:
        passage_chunks = chunk_passage(passage)
        chunks.extend(passage_chunks)

    print(f"Chunks collected: {len(chunks)}")

    if not chunks:
        raise RuntimeError("No chunks were produced.")

    # ------------------------------------------------------------
    # 4. Process one embedding batch
    # ------------------------------------------------------------

    processor = BatchProcessor(
        embedder=embedder,
        batch_size=64,
    )

    result = processor.process_batch(
        chunks=chunks,
        batch_id="test_batch_processor_000001",
    )

    # ------------------------------------------------------------
    # 5. Verify result
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("BATCH RESULT")
    print("=" * 70)

    for key, value in result.items():
        print(f"{key}: {value}")

    if result["chunk_count"] != result["embedding_count"]:
        raise RuntimeError(
            "Chunk/embedding count mismatch."
        )

    if result["embedding_count"] != result["vector_count"]:
        raise RuntimeError(
            "Embedding/vector count mismatch."
        )

    print("\nBATCH PROCESSOR TEST PASSED")


if __name__ == "__main__":
    main()