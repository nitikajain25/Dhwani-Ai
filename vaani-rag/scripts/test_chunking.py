from collections import Counter

from ingestion.local_passage_stream import stream_all_passages
from ingestion.chunker import chunk_passage
from ingestion.config import CHUNKING_STRATEGY
from ingestion.strategies import count_tokens


def main():
    print("=" * 70)
    print("VAANIRAG REAL DATA CHUNKING TEST")
    print("=" * 70)

    # ------------------------------------------------------------
    # Test only a small number of rows.
    #
    # 5 rows per physical dataset means:
    #   English + Hindi + Marathi
    #
    # This is intentionally small so we can safely inspect the
    # chunking behaviour before processing the full dataset.
    # ------------------------------------------------------------

    max_rows = 5

    print()
    print(f"Chunking strategy: {CHUNKING_STRATEGY}")
    print(f"Rows per language: {max_rows}")
    print()

    total_passages = 0
    total_chunks = 0

    language_passages = Counter()
    language_chunks = Counter()

    chunk_sizes = []

    # ------------------------------------------------------------
    # Stream already-cleaned + deduplicated passages
    # ------------------------------------------------------------

    passages = stream_all_passages(
        max_rows_per_language=max_rows,
        batch_size=2,
    )

    # ------------------------------------------------------------
    # Process passages through the configured chunker
    # ------------------------------------------------------------

    for passage_number, passage in enumerate(passages, start=1):

        total_passages += 1
        language_passages[passage.language] += 1

        chunks = chunk_passage(
            passage=passage,
            strategy=CHUNKING_STRATEGY,
        )

        total_chunks += len(chunks)
        language_chunks[passage.language] += len(chunks)

        # Record chunk token sizes
        for chunk in chunks:
            chunk_sizes.append(chunk.token_count)

        # --------------------------------------------------------
        # Show first 10 passages in detail
        # --------------------------------------------------------

        if passage_number <= 10:
            print("-" * 70)
            print(f"PASSAGE {passage_number}")
            print("-" * 70)

            print(f"Passage ID : {passage.passage_id}")
            print(f"Language   : {passage.language}")
            print(f"Tokens     : {count_tokens(passage.text)}")
            print(f"Chunks     : {len(chunks)}")

            for chunk in chunks:
                preview = chunk.text[:180].replace("\n", " ")

                print()
                print(
                    f"  Chunk {chunk.chunk_index + 1}: "
                    f"{chunk.token_count} tokens"
                )
                print(f"  ID       : {chunk.chunk_id}")
                print(f"  Strategy : {chunk.strategy}")
                print(f"  Preview  : {preview}")

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    print()
    print("=" * 70)
    print("CHUNKING SUMMARY")
    print("=" * 70)

    print(f"Total passages : {total_passages}")
    print(f"Total chunks   : {total_chunks}")

    print()
    print("Passages by language:")
    for language in sorted(language_passages):
        print(
            f"  {language}: "
            f"{language_passages[language]}"
        )

    print()
    print("Chunks by language:")
    for language in sorted(language_chunks):
        print(
            f"  {language}: "
            f"{language_chunks[language]}"
        )

    # ------------------------------------------------------------
    # Chunk size statistics
    # ------------------------------------------------------------

    if chunk_sizes:
        average = sum(chunk_sizes) / len(chunk_sizes)

        print()
        print("Chunk token statistics:")
        print(f"  Minimum : {min(chunk_sizes)}")
        print(f"  Average : {average:.2f}")
        print(f"  Maximum : {max(chunk_sizes)}")

    # ------------------------------------------------------------
    # Passage-to-chunk expansion
    # ------------------------------------------------------------

    if total_passages > 0:
        expansion = total_chunks / total_passages

        print()
        print(
            f"Average chunks per passage: "
            f"{expansion:.2f}"
        )

    print()
    print("=" * 70)
    print("CHUNKING TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()