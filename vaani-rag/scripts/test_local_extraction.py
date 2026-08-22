from pathlib import Path
import pyarrow.parquet as pq

HINDI_FILE = Path("data/raw/hitrain.parquet")
MARATHI_FILE = Path("data/raw/martrain.parquet")

ROWS_TO_TEST = 10


def inspect_language(file_path: Path, language_name: str):
    print("\n" + "=" * 70)
    print(f"TESTING {language_name.upper()}")
    print("=" * 70)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    parquet = pq.ParquetFile(file_path)

    english_count = 0
    translated_count = 0
    selected_count = 0
    missing_translation_count = 0
    total_passages = 0

    english_texts = []

    # Read only the first ROWS_TO_TEST rows.
    # This does NOT load the whole 3.5 GB file.
    batch = next(
        parquet.iter_batches(
            batch_size=ROWS_TO_TEST,
            columns=[
                "query_id",
                "passages",
                "source_lang",
                "target_lang",
            ],
        )
    )

    rows = batch.to_pylist()

    print(f"Rows inspected: {len(rows)}")

    for row_number, row in enumerate(rows):
        passages = row["passages"]

        english_passages = passages["English_passages"]
        translated_passages = passages["Translated_passages"]
        selected_flags = passages["is_selected"]

        print(f"\nRow {row_number + 1}")
        print(f"Query ID: {row['query_id']}")
        print(f"Source: {row['source_lang']}")
        print(f"Target: {row['target_lang']}")
        print(f"Number of passages: {len(english_passages)}")

        for i, english_text in enumerate(english_passages):
            total_passages += 1

            if english_text and str(english_text).strip():
                english_count += 1
                english_texts.append(str(english_text).strip())

            translated_text = ""

            if i < len(translated_passages):
                translated_text = translated_passages[i]

            if translated_text and str(translated_text).strip():
                translated_count += 1
            else:
                missing_translation_count += 1

            selected = 0

            if i < len(selected_flags):
                selected = selected_flags[i]

            if selected:
                selected_count += 1

            # Show only the first passage of each row.
            if i == 0:
                print("\nFirst passage:")
                print("  EN :", str(english_text)[:300])

                if translated_text:
                    print(
                        f"  {language_name[:2].upper()} :",
                        str(translated_text)[:300],
                    )
                else:
                    print(
                        f"  {language_name[:2].upper()} : "
                        "[MISSING TRANSLATION]"
                    )

                print("  Selected:", selected)

    # Check duplicate English passages inside the inspected sample.
    unique_english = set(english_texts)
    duplicate_english = len(english_texts) - len(unique_english)

    print("\n" + "-" * 70)
    print(f"{language_name.upper()} SUMMARY")
    print("-" * 70)

    print(f"Total passages inspected       : {total_passages}")
    print(f"English passages available     : {english_count}")
    print(f"Translated passages available  : {translated_count}")
    print(f"Missing translations           : {missing_translation_count}")
    print(f"Selected passages              : {selected_count}")
    print(f"Unique English passages        : {len(unique_english)}")
    print(f"Duplicate English in sample    : {duplicate_english}")


def main():
    print("=" * 70)
    print("VAANIRAG LOCAL EXTRACTION TEST")
    print("=" * 70)
    print()
    print("This test reads only the first 10 rows from each Parquet file.")
    print("No embeddings are generated.")
    print("No Pinecone upload occurs.")

    inspect_language(
        HINDI_FILE,
        "Hindi",
    )

    inspect_language(
        MARATHI_FILE,
        "Marathi",
    )

    print("\n" + "=" * 70)
    print("EXTRACTION TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()