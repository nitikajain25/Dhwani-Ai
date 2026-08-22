from ingestion.qdrant_client import get_qdrant_client
from ingestion.embedder import BGEM3Embedder
from ingestion.retriever import QdrantRetriever


def main():

    print("=" * 70)
    print("VAANIRAG RETRIEVAL TEST")
    print("=" * 70)

    print("\nConnecting to Qdrant...")

    client = get_qdrant_client()

    print("Qdrant: OK")

    print("\nLoading BGE-M3...")

    embedder = BGEM3Embedder(
        device="GPU"
    )

    print("Embedding model: OK")
    print("Dimension:", embedder.get_dimension())
    print("Device:", embedder.get_device())

    retriever = QdrantRetriever(
        client=client,
        embedder=embedder,
    )

    queries = [
        "What is photosynthesis?",
        "What information is contained in the document?",
        "How does the human body use oxygen?",
    ]

    for query in queries:

        print("\n" + "-" * 70)
        print("QUERY:", query)
        print("-" * 70)

        results = retriever.search(
            query=query,
            top_k=5,
        )

        print("Results:", len(results))

        for i, result in enumerate(
            results,
            start=1,
        ):

            print(f"\nResult {i}")
            print("Score    :", f"{result.score:.4f}")
            print("Language :", result.language)
            print("Chunk ID  :", result.chunk_id)
            print("Text     :", result.text[:500])


if __name__ == "__main__":
    main()