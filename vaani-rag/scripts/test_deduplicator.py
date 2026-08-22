from ingestion.deduplicator import Deduplicator
from ingestion.schemas import Passage


def make_passage(
    text: str,
    passage_id: str,
    content_hash: str
) -> Passage:

    return Passage(
        passage_id=passage_id,
        text=text,
        language="en",
        query_id="test",
        query_type="test",
        source_lang="eng_Latn",
        target_lang="eng_Latn",
        is_selected=False,
        original_record_index=0,
        content_hash=content_hash
    )


def main():

    print("=" * 70)
    print("VAANIRAG DEDUPLICATOR TEST")
    print("=" * 70)

    passages = [
        make_passage(
            "The Manhattan Project was a research project.",
            "p1",
            "hash_A"
        ),

        make_passage(
            "This is a different passage.",
            "p2",
            "hash_B"
        ),

        make_passage(
            "The Manhattan Project was a research project.",
            "p3",
            "hash_A"
        ),

        make_passage(
            "Another unique passage.",
            "p4",
            "hash_C"
        ),

        make_passage(
            "This is a different passage.",
            "p5",
            "hash_B"
        ),
    ]

    # Use SQLite because this is what we will use
    # for the real large-scale ingestion.
    deduplicator = Deduplicator(use_sqlite=True)

    unique_passages = []

    for passage in passages:

        if not deduplicator.is_duplicate(passage):
            unique_passages.append(passage)

    deduplicator.commit()

    print()
    print("Input passages :", len(passages))
    print("Unique passages:", len(unique_passages))
    print("Duplicates     :", deduplicator.duplicate_count)

    print()
    print("Unique passage IDs:")

    for passage in unique_passages:
        print(f"  {passage.passage_id}")

    print()
    print("Statistics:")

    stats = deduplicator.get_stats()

    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Expected:
    # p1 → unique
    # p2 → unique
    # p3 → duplicate of p1
    # p4 → unique
    # p5 → duplicate of p2

    assert len(unique_passages) == 3
    assert deduplicator.duplicate_count == 2
    assert stats["raw_passages"] == 5
    assert stats["unique_passages"] == 3

    print()
    print("TEST PASSED")


if __name__ == "__main__":
    main()