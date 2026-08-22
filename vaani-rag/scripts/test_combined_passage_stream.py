from collections import Counter

from ingestion.local_passage_stream import stream_all_passages


def main():
    print("=" * 70)
    print("VAANIRAG COMBINED PASSAGE STREAM TEST")
    print("=" * 70)

    passages = stream_all_passages(
        max_rows_per_language=5,
        batch_size=2,
    )

    counts = Counter()
    english_hashes = set()

    total = 0

    for passage in passages:
        total += 1
        counts[passage.language] += 1

        if passage.language == "en":
            english_hashes.add(passage.content_hash)

        if total <= 10:
            print("\nPassage", total)
            print(f"  ID       : {passage.passage_id}")
            print(f"  Language : {passage.language}")
            print(f"  Hash     : {passage.content_hash[:16]}...")
            print(f"  Text     : {passage.text[:200]}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"Total passages : {total}")
    print(f"English       : {counts['en']}")
    print(f"Hindi         : {counts['hi']}")
    print(f"Marathi       : {counts['mr']}")

    print(f"\nUnique English hashes: {len(english_hashes)}")

    print("\nTEST COMPLETE")


if __name__ == "__main__":
    main()