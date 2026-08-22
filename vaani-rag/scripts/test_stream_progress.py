from ingestion.local_passage_stream import stream_all_passages


def main():

    print("=" * 70)
    print("VAANIRAG STREAM SOURCE PROGRESS TEST")
    print("=" * 70)

    progress = {}

    def on_progress(
        dataset: str,
        next_row: int,
    ):
        progress[dataset] = next_row

    print("\nReading first 5 rows from each dataset...")

    passages = list(
        stream_all_passages(
            max_rows_per_language=5,
            batch_size=2,
            start_rows={
                "hi": 0,
                "mr": 0,
            },
            progress_callback=on_progress,
        )
    )

    print(
        f"\nPassages produced: {len(passages)}"
    )

    print("\nSource progress:")

    for dataset, row in progress.items():
        print(
            f"  {dataset}: next row = {row}"
        )

    # Both physical datasets should have consumed 5 rows.
    assert progress.get("hi") == 5
    assert progress.get("mr") == 5

    print(
        "\nSource progress tracking: PASSED"
    )

    # ------------------------------------------------------------
    # Test resume
    # ------------------------------------------------------------

    progress_after_resume = {}

    def on_resume_progress(
        dataset: str,
        next_row: int,
    ):
        progress_after_resume[dataset] = next_row

    print(
        "\nTesting resume from hi=5, mr=5..."
    )

    resumed_passages = list(
        stream_all_passages(
            max_rows_per_language=5,
            batch_size=2,
            start_rows={
                "hi": 5,
                "mr": 5,
            },
            progress_callback=on_resume_progress,
        )
    )

    print(
        f"Resumed passages produced: "
        f"{len(resumed_passages)}"
    )

    print("\nProgress after resume:")

    for dataset, row in progress_after_resume.items():
        print(
            f"  {dataset}: next row = {row}"
        )

    assert progress_after_resume.get("hi") == 10
    assert progress_after_resume.get("mr") == 10

    print(
        "\nResume progress tracking: PASSED"
    )

    print("\n" + "=" * 70)
    print("STREAM SOURCE PROGRESS TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()