from ingestion.embedder import BGEM3Embedder
from ingestion.qdrant_client import get_qdrant_client
from ingestion.qdrant_store import ensure_collection
from ingestion.config import QDRANT_COLLECTION_NAME


def main():
    print("=" * 70)
    print("VAANIRAG QDRANT VECTOR TEST")
    print("=" * 70)

    # ------------------------------------------------------------
    # CONNECT TO QDRANT
    # ------------------------------------------------------------

    print("\nConnecting to Qdrant...")

    client = get_qdrant_client()

    ensure_collection(
        client,
        QDRANT_COLLECTION_NAME,
    )

    print("Qdrant connection: OK")
    print(f"Collection: {QDRANT_COLLECTION_NAME}")

    # ------------------------------------------------------------
    # LOAD EMBEDDER
    # ------------------------------------------------------------

    print("\nLoading BGE-M3...")

    embedder = BGEM3Embedder()

    print(f"Device    : {embedder.get_device()}")
    print(f"Dimension : {embedder.get_dimension()}")

    # ------------------------------------------------------------
    # TEST TEXTS
    # ------------------------------------------------------------

    texts = [
        "Artificial intelligence helps computers understand information.",
        "Machine learning allows computers to learn from data.",
        "Vector databases are used to search embedding vectors.",
    ]

    print(
        f"\nGenerating embeddings for "
        f"{len(texts)} test texts..."
    )

    # IMPORTANT:
    # BGEM3Embedder uses embed_texts(), not embed().
    embeddings = embedder.embed_texts(texts)

    print(
        f"Embeddings generated: {len(embeddings)}"
    )

    # ------------------------------------------------------------
    # VALIDATE EMBEDDINGS
    # ------------------------------------------------------------

    assert len(embeddings) == len(texts)

    for i, vector in enumerate(embeddings):

        assert len(vector) == 1024

        print(
            f"Vector {i + 1}: "
            f"{len(vector)} dimensions"
        )

    print("Embedding validation: PASSED")

    # ------------------------------------------------------------
    # UPLOAD TEST VECTORS
    # ------------------------------------------------------------

    from qdrant_client.models import PointStruct

    points = []

    for i, (text, vector) in enumerate(
        zip(texts, embeddings)
    ):

        points.append(
            PointStruct(
                id=i + 1,
                vector=vector,
                payload={
                    "language": "en",
                    "text": text,
                    "test": True,
                },
            )
        )

    print("\nUploading test vectors...")

    client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=points,
        wait=True,
    )

    print("Test vector upload: PASSED")

    # ------------------------------------------------------------
    # VERIFY COUNT
    # ------------------------------------------------------------

    info = client.get_collection(
        QDRANT_COLLECTION_NAME
    )

    print(
        f"Collection points: "
        f"{info.points_count}"
    )

    assert info.points_count >= 3

    print(
        "Collection count verification: PASSED"
    )

    # ------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------

    query = (
        "How are embedding vectors searched?"
    )

    print(f"\nSearch query: {query}")

    # IMPORTANT:
    # Queries use embed_query().
    query_vector = embedder.embed_query(query)

    results = client.query_points(
        collection_name=QDRANT_COLLECTION_NAME,
        query=query_vector,
        limit=3,
        with_payload=True,
    ).points

    print("\nSearch results:")

    for result in results:

        print(
            f"\nScore: {result.score:.4f}"
        )

        print(
            f"ID: {result.id}"
        )

        print(
            f"Text: {result.payload.get('text')}"
        )

    assert len(results) > 0

    returned_ids = {
        str(result.id)
        for result in results
    }

    assert "3" in returned_ids

    print("\nSimilarity search: PASSED")

    # ------------------------------------------------------------
    # COMPLETE
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("QDRANT VECTOR TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()