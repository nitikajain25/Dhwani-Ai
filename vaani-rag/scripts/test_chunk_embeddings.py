from ingestion.local_passage_stream import stream_all_passages
from ingestion.chunker import chunk_passage
from ingestion.embedder import BGEM3Embedder
from ingestion.validator import validate_embeddings
from ingestion.vector_builder import build_vector_record


def main():

    print("=" * 70)
    print("VAANIRAG CHUNK → EMBEDDING → VECTOR RECORD TEST")
    print("=" * 70)

    # ------------------------------------------------------------
    # 1. Load local BGE-M3 embedder
    # ------------------------------------------------------------

    print("\nLoading BGE-M3 embedder...")

    embedder = BGEM3Embedder()

    print(f"Device    : {embedder.get_device()}")
    print(f"Dimension : {embedder.get_dimension()}")

    # ------------------------------------------------------------
    # 2. Get real local passages
    # ------------------------------------------------------------

    print("\nReading local passages...")

    chunks = []

    for passage in stream_all_passages(
        max_rows_per_language=5,
        batch_size=2,
    ):

        passage_chunks = chunk_passage(
            passage,
            strategy="adaptive",
        )

        chunks.extend(passage_chunks)

    print(f"Chunks collected: {len(chunks)}")

    if not chunks:
        raise RuntimeError("No chunks were produced.")

    # ------------------------------------------------------------
    # 3. Extract chunk text
    # ------------------------------------------------------------

    texts = [chunk.text for chunk in chunks]

    print("\nGenerating embeddings...")

    # ------------------------------------------------------------
    # 4. Generate embeddings
    # ------------------------------------------------------------

    embeddings = embedder.embed_texts(texts)

    print(f"Embeddings generated: {len(embeddings)}")

    # ------------------------------------------------------------
    # 5. Check chunk/vector count
    # ------------------------------------------------------------

    if len(chunks) != len(embeddings):
        raise RuntimeError(
            f"Mismatch: {len(chunks)} chunks "
            f"but {len(embeddings)} embeddings."
        )

    print("Chunk → embedding count: PASSED")

    # ------------------------------------------------------------
    # 6. Validate embeddings
    # ------------------------------------------------------------

    valid, reason = validate_embeddings(
        embeddings,
        expected_dim=1024,
    )

    if not valid:
        raise RuntimeError(
            f"Embedding validation failed: {reason}"
        )

    print("Embedding validation: PASSED")

    # ------------------------------------------------------------
    # 7. Build VectorRecords
    # ------------------------------------------------------------

    print("\nBuilding VectorRecords...")

    vector_records = []

    for chunk, embedding in zip(chunks, embeddings):

        record = build_vector_record(
            chunk=chunk,
            embedding=embedding,
        )

        vector_records.append(record)

    # ------------------------------------------------------------
    # 8. Verify VectorRecords
    # ------------------------------------------------------------

    if len(vector_records) != len(chunks):
        raise RuntimeError(
            f"Mismatch: {len(chunks)} chunks "
            f"but {len(vector_records)} VectorRecords."
        )

    print("VectorRecord count: PASSED")

    # ------------------------------------------------------------
    # 9. Display examples
    # ------------------------------------------------------------

    print("\nFirst 5 VectorRecords:")

    for i, record in enumerate(vector_records[:5], start=1):

        print("-" * 70)

        print(f"Record {i}")

        print("ID:")
        print(f"  {record.id}")

        print("Vector dimension:")
        print(f"  {len(record.values)}")

        print("First 5 vector values:")
        print(f"  {record.values[:5]}")

        print("Metadata:")
        print(f"  language      : {record.metadata.get('language')}")
        print(f"  token_count   : {record.metadata.get('token_count')}")
        print(f"  strategy      : {record.metadata.get('strategy')}")

        text = record.metadata.get("text", "")
        print(f"  text          : {text[:120]}")

    # ------------------------------------------------------------
    # 10. Language statistics
    # ------------------------------------------------------------

    language_counts = {}

    for record in vector_records:

        language = record.metadata.get("language")

        language_counts[language] = (
            language_counts.get(language, 0) + 1
        )

    print("\nLanguage statistics:")

    for language, count in sorted(language_counts.items()):

        print(f"  {language}: {count}")

    # ------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("EMBEDDING PIPELINE TEST COMPLETE")
    print("=" * 70)

    print(f"Chunks             : {len(chunks)}")
    print(f"Embeddings         : {len(embeddings)}")
    print(f"VectorRecords      : {len(vector_records)}")
    print(f"Vector dimension   : {embedder.get_dimension()}")
    print(f"Device             : {embedder.get_device()}")

    print("\nALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()