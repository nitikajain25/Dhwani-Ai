from ingestion.local_dataset_loader import get_local_row_generator
from ingestion.passage_extractor import extract_passages_from_row


def test_english_from_source(language: str):
    print("\n" + "=" * 70)
    print(f"EXTRACTING ENGLISH FROM {language.upper()} DATASET")
    print("=" * 70)

    rows = get_local_row_generator(
        language=language,
        max_rows=5,
        batch_size=2,
    )

    total = 0
    unique_hashes = set()

    for record_index, row in enumerate(rows):

        passages = list(
            extract_passages_from_row(
                row=row,
                language="en",
                record_index=record_index,
            )
        )

        print(f"\nRow {record_index + 1}")
        print(f"Query ID: {row.get('query_id')}")
        print(f"English passages extracted: {len(passages)}")

        for passage in passages:
            total += 1
            unique_hashes.add(passage.content_hash)

            if total <= 3:
                print("\nEnglish passage:")
                print(f"  ID   : {passage.passage_id}")
                print(f"  Hash : {passage.content_hash}")
                print(f"  Text : {passage.text[:300]}")

    print("\n" + "-" * 70)
    print(f"{language.upper()} ENGLISH SUMMARY")
    print("-" * 70)
    print(f"Total English passages : {total}")
    print(f"Unique English hashes  : {len(unique_hashes)}")
    print(f"Duplicates             : {total - len(unique_hashes)}")


def main():
    print("=" * 70)
    print("VAANIRAG ENGLISH EXTRACTION TEST")
    print("=" * 70)

    test_english_from_source("hi")
    test_english_from_source("mr")

    print("\n" + "=" * 70)
    print("ENGLISH EXTRACTION TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()