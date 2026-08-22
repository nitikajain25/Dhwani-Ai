from typing import Iterator

from ingestion.local_dataset_loader import get_local_row_generator
from ingestion.passage_extractor import extract_passages_from_row
from ingestion.text_cleaner import clean_text
from ingestion.schemas import Passage
from ingestion.logging_config import logger


def stream_language_passages(
    language: str,
    source_dataset: str | None = None,
    max_rows: int | None = None,
    batch_size: int = 2,
    start_row: int = 0,
    progress_callback=None,
) -> Iterator[Passage]:
    """
    Streams passages from a local Parquet dataset.

    Supports resumable source-row processing.

    language:
        en -> English passages
        hi -> Hindi passages
        mr -> Marathi passages

    source_dataset:
        hi or mr when language == "en".
    """

    # --------------------------------------------------------
    # Determine physical dataset
    # --------------------------------------------------------

    if language == "en":

        if source_dataset not in ("hi", "mr"):
            raise ValueError(
                "English extraction requires "
                "source_dataset='hi' or "
                "source_dataset='mr'."
            )

        loader_language = source_dataset

    elif language in ("hi", "mr"):

        loader_language = language

    else:

        raise ValueError(
            f"Unsupported language '{language}'. "
            "Supported languages: ['en', 'hi', 'mr']"
        )

    # --------------------------------------------------------
    # Read source rows
    # --------------------------------------------------------

    rows = get_local_row_generator(
        language=loader_language,
        max_rows=max_rows,
        batch_size=batch_size,
        start_row=start_row,
    )

    # --------------------------------------------------------
    # Extract passages
    # --------------------------------------------------------

    for record_index, row in enumerate(
        rows,
        start=start_row,
    ):

        passages = extract_passages_from_row(
            row=row,
            language=language,
            record_index=record_index,
        )

        for passage in passages:

            cleaned = clean_text(
                passage.text
            )

            if not cleaned:
                continue

            passage.text = cleaned

            yield passage

        # ----------------------------------------------------
        # Source progress
        #
        # Only update after the complete row has been
        # processed.
        # ----------------------------------------------------

        if progress_callback is not None:

            progress_callback(
                loader_language,
                record_index + 1,
            )


def stream_all_passages(
    max_rows_per_language: int | None = None,
    batch_size: int = 2,
    start_rows: dict | None = None,
    progress_callback=None,
) -> Iterator[Passage]:
    """
    Streams the multilingual DhawaniRAG corpus.

    English:
        Extracted from BOTH Hindi and Marathi datasets.

    Hindi:
        Extracted from Hindi dataset.

    Marathi:
        Extracted from Marathi dataset.

    All languages are globally deduplicated by content_hash.
    """

    if start_rows is None:
        start_rows = {
            "hi": 0,
            "mr": 0,
        }

    # ========================================================
    # GLOBAL CONTENT DEDUPLICATION
    # ========================================================

    seen_hashes = set()

    duplicate_count = 0

    # ========================================================
    # ENGLISH FROM HINDI
    # ========================================================

    logger.info(
        "Starting English extraction from Hindi "
        f"dataset at row {start_rows.get('hi', 0)}."
    )

    for passage in stream_language_passages(
        language="en",
        source_dataset="hi",
        max_rows=max_rows_per_language,
        batch_size=batch_size,
        start_row=start_rows.get(
            "hi",
            0,
        ),
        progress_callback=progress_callback,
    ):

        if passage.content_hash in seen_hashes:

            duplicate_count += 1

            continue

        seen_hashes.add(
            passage.content_hash
        )

        yield passage

    # ========================================================
    # ENGLISH FROM MARATHI
    # ========================================================

    logger.info(
        "Starting English extraction from Marathi "
        f"dataset at row {start_rows.get('mr', 0)}."
    )

    for passage in stream_language_passages(
        language="en",
        source_dataset="mr",
        max_rows=max_rows_per_language,
        batch_size=batch_size,
        start_row=start_rows.get(
            "mr",
            0,
        ),
        progress_callback=progress_callback,
    ):

        if passage.content_hash in seen_hashes:

            duplicate_count += 1

            continue

        seen_hashes.add(
            passage.content_hash
        )

        yield passage

    # ========================================================
    # HINDI
    # ========================================================

    logger.info(
        "Starting Hindi extraction "
        f"at row {start_rows.get('hi', 0)}."
    )

    for passage in stream_language_passages(
        language="hi",
        max_rows=max_rows_per_language,
        batch_size=batch_size,
        start_row=start_rows.get(
            "hi",
            0,
        ),
        progress_callback=progress_callback,
    ):

        if passage.content_hash in seen_hashes:

            duplicate_count += 1

            continue

        seen_hashes.add(
            passage.content_hash
        )

        yield passage

    # ========================================================
    # MARATHI
    # ========================================================

    logger.info(
        "Starting Marathi extraction "
        f"at row {start_rows.get('mr', 0)}."
    )

    for passage in stream_language_passages(
        language="mr",
        max_rows=max_rows_per_language,
        batch_size=batch_size,
        start_row=start_rows.get(
            "mr",
            0,
        ),
        progress_callback=progress_callback,
    ):

        if passage.content_hash in seen_hashes:

            duplicate_count += 1

            continue

        seen_hashes.add(
            passage.content_hash
        )

        yield passage

    # ========================================================
    # DEDUP SUMMARY
    # ========================================================

    logger.info(
        f"Global passage deduplication complete. "
        f"Unique passages: {len(seen_hashes)}, "
        f"duplicates skipped: {duplicate_count}"
    )