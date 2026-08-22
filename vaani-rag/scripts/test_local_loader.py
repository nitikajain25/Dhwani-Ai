from ingestion.local_dataset_loader import get_local_row_generator


def main():
    print("=" * 70)
    print("LOCAL PARQUET LOADER TEST")
    print("=" * 70)

    for language in ["hi", "mr"]:
        print("\n" + "=" * 70)
        print(f"TESTING: {language.upper()}")
        print("=" * 70)

        rows = get_local_row_generator(
            language=language,
            max_rows=5,
            batch_size=2,
        )

        count = 0

        for row in rows:
            count += 1

            print(f"\nRow {count}")
            print("Keys:", list(row.keys()))
            print("Query ID:", row.get("query_id"))
            print("Source:", row.get("source_lang"))
            print("Target:", row.get("target_lang"))

            passages = row.get("passages", {})

            print(
                "English passages:",
                len(passages.get("English_passages", []))
            )

            print(
                "Translated passages:",
                len(passages.get("Translated_passages", []))
            )

            if count >= 5:
                break

        print(f"\nRows successfully read: {count}")

    print("\n" + "=" * 70)
    print("LOCAL LOADER TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()