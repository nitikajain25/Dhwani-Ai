from ingestion.local_dataset_loader import get_local_row_generator
from ingestion.passage_extractor import extract_passages_from_row


def test_language(language: str, expected_target: str):
    print("\n" + "=" * 70)
    print(f"TESTING LOCAL EXTRACTION: {language.upper()}")
    print("=" * 70)

    rows = get_local_row_generator(
        language=language,
        max_rows=5,
        batch_size=2,
    )

    total_passages = 0
    english_passages = 0
    translated_passages = 0

    for record_index, row in enumerate(rows):
        print(f"\nRow {record_index + 1}")
        print(f"Query ID: {row.get('query_id')}")
        print(f"Target language: {row.get('target_lang')}")

        assert row.get("target_lang") == expected_target

        passages = list(
            extract_passages_from_row(
                row=row,
                language=language,
                record_index=record_index,
            )
        )

        print(f"Extracted passages: {len(passages)}")

        for passage in passages:
            total_passages += 1

            # For Hindi/Marathi extraction, the extractor should
            # return translated passages only.
            if passage.language == language:
                translated_passages += 1

            if passage.language == "en":
                english_passages += 1

        if passages:
            first = passages[0]

            print("First extracted passage:")
            print(f"  ID       : {first.passage_id}")
            print(f"  Language : {first.language}")
            print(f"  Hash     : {first.content_hash[:16]}...")
            print(f"  Text     : {first.text[:300]}")

    print("\n" + "-" * 70)
    print(f"{language.upper()} EXTRACTION SUMMARY")
    print("-" * 70)
    print(f"Total extracted passages : {total_passages}")
    print(f"{language} passages       : {translated_passages}")
    print(f"English passages         : {english_passages}")

    print("\nTEST PASSED")


def main():
    print("=" * 70)
    print("VAANIRAG LOCAL LOADER → PASSAGE EXTRACTOR TEST")
    print("=" * 70)

    test_language(
        language="hi",
        expected_target="hin_Deva",
    )

    test_language(
        language="mr",
        expected_target="mar_Deva",
    )

    print("\n" + "=" * 70)
    print("LOCAL EXTRACTION PIPELINE TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()