from ingestion.local_dataset_loader import get_local_row_generator


def main():

    print("=" * 70)
    print("VAANIRAG ROW RESUME TEST")
    print("=" * 70)

    # ------------------------------------------------------------
    # Read first 5 rows
    # ------------------------------------------------------------

    print("\nReading rows 0-4...")

    first_rows = list(
        get_local_row_generator(
            language="hi",
            start_row=0,
            max_rows=5,
            batch_size=2,
        )
    )

    print(
        f"Rows returned: {len(first_rows)}"
    )

    assert len(first_rows) == 5

    # ------------------------------------------------------------
    # Read next 5 rows
    # ------------------------------------------------------------

    print("\nReading rows 5-9...")

    resumed_rows = list(
        get_local_row_generator(
            language="hi",
            start_row=5,
            max_rows=5,
            batch_size=2,
        )
    )

    print(
        f"Rows returned: {len(resumed_rows)}"
    )

    assert len(resumed_rows) == 5

    # ------------------------------------------------------------
    # Verify that the two sets are different
    # ------------------------------------------------------------

    first_ids = [
        row.get("query_id")
        for row in first_rows
    ]

    resumed_ids = [
        row.get("query_id")
        for row in resumed_rows
    ]

    print("\nFirst batch query IDs:")
    for value in first_ids:
        print(f"  {value}")

    print("\nResumed batch query IDs:")
    for value in resumed_ids:
        print(f"  {value}")

    assert first_ids != resumed_ids

    print("\n" + "=" * 70)
    print("ROW RESUME TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()