from ingestion.dataset_loader import get_row_generator
from ingestion.passage_extractor import extract_passages_from_row


def test_language(language: str):
    print("\n" + "=" * 70)
    print(f"TESTING LANGUAGE: {language}")
    print("=" * 70)

    rows = get_row_generator(
        lang=language,
        max_rows=5,
        split="train",
    )

    total_rows = 0
    total_passages = 0

    for record_index, row in enumerate(rows):
        total_rows += 1

        print(f"\n--- ROW {record_index} ---")

        print("query_id:", row.get("query_id"))
        print("query_type:", row.get("query_type"))
        print("source_lang:", row.get("source_lang"))
        print("target_lang:", row.get("target_lang"))

        passages = list(
            extract_passages_from_row(
                row=row,
                language=language,
                record_index=record_index,
            )
        )

        print("passages extracted:", len(passages))

        for i, passage in enumerate(passages[:3]):
            print(f"\nPassage {i + 1}:")
            print("  language:", passage.language)
            print("  selected:", passage.is_selected)
            print("  text:", passage.text[:300])

        total_passages += len(passages)

    print("\n" + "-" * 70)
    print(f"SUMMARY {language}")
    print("-" * 70)
    print("Rows:", total_rows)
    print("Passages:", total_passages)


if __name__ == "__main__":
    for language in ["en", "hi", "mr"]:
        test_language(language)