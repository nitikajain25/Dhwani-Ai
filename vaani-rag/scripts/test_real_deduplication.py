from ingestion.deduplicator import Deduplicator
from ingestion.local_passage_stream import stream_all_passages


def main():

    print("=" * 70)
    print("VAANIRAG REAL DATA DEDUPLICATION TEST")
    print("=" * 70)

    max_rows_per_language = 5

    deduplicator = Deduplicator(use_sqlite=True)

    total_passages = 0

    print()
    print("Reading real Hindi + Marathi passage stream...")
    print()

    passages = stream_all_passages(
        max_rows_per_language=max_rows_per_language
    )

    for passage in passages:

        total_passages += 1

        is_duplicate = deduplicator.is_duplicate(passage)

        if total_passages <= 15:
            status = "DUPLICATE" if is_duplicate else "UNIQUE"

            print(
                f"{total_passages:3d}. "
                f"{passage.language:2s} | "
                f"{status:9s} | "
                f"{passage.passage_id[:35]}"
            )

    deduplicator.commit()

    stats = deduplicator.get_stats()

    print()
    print("=" * 70)
    print("DEDUPLICATION SUMMARY")
    print("=" * 70)

    print(f"Raw passages       : {stats['raw_passages']}")
    print(f"Unique passages    : {stats['unique_passages']}")
    print(f"Duplicates         : {stats['duplicates']}")
    print(f"Duplicate percent  : {stats['duplicate_percentage']}%")

    print()
    print("TEST COMPLETE")


if __name__ == "__main__":
    main()