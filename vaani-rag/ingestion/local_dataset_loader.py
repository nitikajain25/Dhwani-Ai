from pathlib import Path
from typing import Iterator, Dict, Any

import pyarrow.parquet as pq

from ingestion.logging_config import logger


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

DATASET_FILES = {
    "hi": RAW_DATA_DIR / "hitrain.parquet",
    "mr": RAW_DATA_DIR / "martrain.parquet",
}


def get_local_row_generator(
    language: str,
    max_rows: int | None,
    batch_size: int = 100,
    start_row: int = 0,
) -> Iterator[Dict[str, Any]]:
    """
    Streams rows from a locally downloaded MSMARCO-XI Parquet file.

    The Parquet file is NOT loaded completely into RAM.

    start_row:
        Number of rows to skip before yielding rows.

    max_rows:
        Maximum number of rows to yield AFTER start_row.

        Example:

            start_row=1000
            max_rows=100

        means rows 1000 through 1099 are yielded.
    """

    language = language.lower().strip()

    if language not in DATASET_FILES:
        raise ValueError(
            f"Unsupported language '{language}'. "
            f"Supported languages: {list(DATASET_FILES.keys())}"
        )

    file_path = DATASET_FILES[language]

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {file_path}"
        )

    if start_row < 0:
        raise ValueError("start_row cannot be negative.")

    if max_rows is not None and max_rows < 0:
        raise ValueError("max_rows cannot be negative.")

    logger.info(
        f"Opening local {language} Parquet dataset: {file_path}"
    )

    parquet_file = pq.ParquetFile(file_path)

    total_rows = parquet_file.metadata.num_rows

    logger.info(
        f"{language} dataset opened successfully. "
        f"Rows: {total_rows}"
    )

    if start_row >= total_rows:
        logger.info(
            f"start_row={start_row} is at or beyond the end "
            f"of {language} dataset."
        )
        return

    rows_seen = 0
    rows_yielded = 0

    for batch in parquet_file.iter_batches(
        batch_size=batch_size
    ):

        rows = batch.to_pylist()

        for row in rows:

            current_row_index = rows_seen
            rows_seen += 1

            # ----------------------------------------------------
            # Skip rows already processed in a previous run
            # ----------------------------------------------------

            if current_row_index < start_row:
                continue

            # ----------------------------------------------------
            # Respect max_rows AFTER start_row
            # ----------------------------------------------------

            if (
                max_rows is not None
                and rows_yielded >= max_rows
            ):
                logger.info(
                    f"Reached max_rows={max_rows} "
                    f"after start_row={start_row} "
                    f"for language '{language}'."
                )
                return

            yield row

            rows_yielded += 1

    logger.info(
        f"Finished reading {rows_yielded} rows "
        f"from local {language} dataset "
        f"starting at row {start_row}."
    )