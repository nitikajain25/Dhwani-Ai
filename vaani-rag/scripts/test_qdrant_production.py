from ingestion.embedder import BGEM3Embedder
from ingestion.local_passage_stream import stream_all_passages
from ingestion.chunker import chunk_passage
from ingestion.batch_processor import BatchProcessor
from ingestion.embedding_store import EmbeddingBatchStore
from ingestion.qdrant_client import get_qdrant_client
from ingestion.qdrant_store import ensure_collection
from ingestion.qdrant_uploader import upload_vectors_to_qdrant
from ingestion.config import (
    QDRANT_COLLECTION_NAME,
    CHUNKING_STRATEGY,
)


def main():

    print("=" * 70)
    print("VAANIRAG QDRANT PRODUCTION PIPELINE TEST")
    print("=" * 70)

    # ------------------------------------------------------------
    # CONNECT QDRANT
    # ------------------------------------------------------------

    print("\nConnecting to Qdrant...")

    client = get_qdrant_client()

    ensure_collection(
        client,
        QDRANT_COLLECTION_NAME,
    )

    print("Qdrant: OK")

    # ------------------------------------------------------------
    # LOAD EMBEDDER
    # ------------------------------------------------------------

    print("\nLoading BGE-M3...")

    embedder = BGEM3Embedder()

    print(
        f"Device    : {embedder.get_device()}"
    )

    print(
        f"Dimension : {embedder.get_dimension()}"
    )

    # ------------------------------------------------------------
    # COLLECT REAL PASSAGES
    # ------------------------------------------------------------

    print("\nCollecting real DhawaniRAG passages...")

    language_counts = {
        "en": 0,
        "hi": 0,
        "mr": 0,
    }

    chunks = []

    for passage in stream_all_passages(
        max_rows_per_language=5,
        batch_size=2,
    ):

        language = passage.language

        if language not in language_counts:
            continue

        if language_counts[language] >= 10:
            continue

        passage_chunks = chunk_passage(
            passage,
            strategy=CHUNKING_STRATEGY,
        )

        for chunk in passage_chunks:

            if language_counts[language] >= 10:
                break

            chunks.append(chunk)

            language_counts[language] += 1

        if all(
            count >= 10
            for count in language_counts.values()
        ):
            break

    print(
        f"\nEnglish chunks : "
        f"{language_counts['en']}"
    )

    print(
        f"Hindi chunks   : "
        f"{language_counts['hi']}"
    )

    print(
        f"Marathi chunks : "
        f"{language_counts['mr']}"
    )

    total_chunks = len(chunks)

    print(
        f"Total chunks   : "
        f"{total_chunks}"
    )

    assert total_chunks > 0

    # ------------------------------------------------------------
    # CREATE VECTOR RECORDS
    # ------------------------------------------------------------

    print("\nGenerating embeddings...")

    store = EmbeddingBatchStore()

    processor = BatchProcessor(
        embedder=embedder,
        store=store,
    )

    test_batch_id = "qdrant_production_test"

    # Remove local test batch if it exists.
    path = store.batch_path(
        test_batch_id
    )

    if path.exists():
        path.unlink()

    result = processor.process_batch(
        chunks=chunks,
        batch_id=test_batch_id,
    )

    print(
        f"Local embedding batch created: "
        f"{result['vector_count']} vectors"
    )

    # ------------------------------------------------------------
    # READ VECTOR RECORDS
    # ------------------------------------------------------------

    records = store.load_batch(
        test_batch_id
    )

    print(
        f"Vector records loaded: "
        f"{len(records)}"
    )

    assert len(records) == total_chunks

    # ------------------------------------------------------------
    # UPLOAD TO QDRANT
    # ------------------------------------------------------------

    print("\nUploading vectors to Qdrant...")

    upload_result = upload_vectors_to_qdrant(
        client=client,
        vectors=records,
        namespace="multilingual",
        batch_size=16,
    )

    print(
        f"Attempted : "
        f"{upload_result['attempted']}"
    )

    print(
        f"Uploaded  : "
        f"{upload_result['uploaded']}"
    )

    print(
        f"Failed    : "
        f"{upload_result['failed']}"
    )

    assert upload_result["uploaded"] == total_chunks

    print(
        "\nQdrant upload: PASSED"
    )

    # ------------------------------------------------------------
    # VERIFY COLLECTION
    # ------------------------------------------------------------

    info = client.get_collection(
        QDRANT_COLLECTION_NAME
    )

    print(
        f"\nQdrant point count: "
        f"{info.points_count}"
    )

    assert info.points_count == total_chunks

    print(
        "Qdrant count verification: PASSED"
    )

    # ------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------

    query = (
        "What information is contained "
        "in the document?"
    )

    print(
        f"\nTesting similarity search:"
    )

    print(
        f"Query: {query}"
    )

    query_vector = embedder.embed_query(
        query
    )

    results = client.query_points(
        collection_name=QDRANT_COLLECTION_NAME,
        query=query_vector,
        limit=5,
        with_payload=True,
    ).points

    print(
        f"\nResults returned: "
        f"{len(results)}"
    )

    assert len(results) > 0

    for i, result in enumerate(
        results,
        start=1,
    ):

        payload = result.payload or {}

        print(
            f"\nResult {i}"
        )

        print(
            f"Score      : "
            f"{result.score:.4f}"
        )

        print(
            f"Vector ID  : "
            f"{payload.get('vector_id')}"
        )

        print(
            f"Language   : "
            f"{payload.get('language')}"
        )

        text = payload.get(
            "text",
            "",
        )

        print(
            f"Text       : "
            f"{str(text)[:150]}"
        )

    print(
        "\nSimilarity search: PASSED"
    )

    # ------------------------------------------------------------
    # CLEAN LOCAL TEST BATCH
    # ------------------------------------------------------------

    if path.exists():
        path.unlink()

    # ------------------------------------------------------------
    # FINAL
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("QDRANT PRODUCTION PIPELINE TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()