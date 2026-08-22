from ingestion.local_passage_stream import stream_all_passages


def main():

    print("=" * 70)
    print("VAANIRAG DEDUPLICATED PASSAGE STREAM TEST")
    print("=" * 70)

    max_rows_per_language = 5

    total = 0

    for passage in stream_all_passages(
        max_rows_per_language=max_rows_per_language
    ):
        total += 1

    print()
    print("=" * 70)
    print("RESULT")
    print("=" * 70)

    print(f"Unique passages yielded: {total}")

    print()
    print("TEST COMPLETE")


if __name__ == "__main__":
    main()