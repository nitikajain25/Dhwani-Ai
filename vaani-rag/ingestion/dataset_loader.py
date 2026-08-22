import os
from typing import Any
from datasets import load_dataset
from typing import Iterator, Dict, Any
from pathlib import Path
import requests
import pyarrow.parquet as pq
from ingestion.logging_config import logger


DATASET_REPO = "ai4bharat/MSMARCO-XI"

# Exact Parquet files in the Hugging Face repository.
LANGUAGE_FILES = {
    "hi": "train/hintrain.parquet",
    "mr": "train/martrain.parquet",
}

HF_RESOLVE_BASE = (
    f"https://huggingface.co/datasets/"
    f"{DATASET_REPO}/resolve/main/"
)


def get_parquet_url(language: str, split: str = "train") -> str:
    """
    Loads a streaming connection to the Hugging Face dataset.
    Uses the 'default' configuration as the dataset has a single stream.
    """
    if not os.getenv("HF_TOKEN"):
        logger.warning("HF_TOKEN environment variable is not set. HF downloads will be unauthenticated and may be rate-limited.")

    dataset_id = "ai4bharat/MSMARCO-XI"
    config_name = "default"
    
    logger.info(f"Loading MSMARCO-XI {config_name} configuration")
    logger.info(f"Streaming split={split}")
    
    try:
        dataset = load_dataset(dataset_id, name=config_name, split=split, streaming=True)
        return dataset
    except Exception as e:
        logger.critical(f"Failed to stream dataset configuration '{config_name}': {e}")
        raise e
    # Returns the direct Hugging Face Parquet URL for a supported language.
    """

    language = language.lower().strip()

    if split != "train":
        raise ValueError(
            "The current ingestion pipeline is configured for the train split."
        )

    if language not in LANGUAGE_FILES:
        raise ValueError(
            f"Unsupported language '{language}'. "
            f"Supported source files: {list(LANGUAGE_FILES.keys())}"
        )

    return HF_RESOLVE_BASE + LANGUAGE_FILES[language]


def download_parquet(
    language: str,
    destination: Path,
    split: str = "train",
) -> Path:
    
    Downloads one language Parquet file from Hugging Face.

    This function downloads the file to disk instead of loading the
    entire dataset into RAM.
    """

    url = get_parquet_url(language, split)

    destination.parent.mkdir(parents=True, exist_ok=True)

    logger.info(
        f"Downloading {language} dataset file from Hugging Face:\n"
        f"{url}"
    )

    response = requests.get(
        url,
        stream=True,
        timeout=60,
        allow_redirects=True,
    )

    response.raise_for_status()

    total_bytes = int(response.headers.get("content-length", 0))

    logger.info(
        f"Download size: "
        f"{total_bytes / (1024 ** 3):.2f} GB"
        if total_bytes
        else "Download size: unknown"
    )

    downloaded = 0

    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size=8 * 1024 * 1024):
            if not chunk:
                continue

            f.write(chunk)
            downloaded += len(chunk)

            if total_bytes:
                percent = downloaded / total_bytes * 100

                if downloaded % (256 * 1024 * 1024) < 8 * 1024 * 1024:
                    logger.info(
                        f"{language}: "
                        f"{downloaded / (1024 ** 3):.2f} GB / "
                        f"{total_bytes / (1024 ** 3):.2f} GB "
                        f"({percent:.1f}%)"
                    )

    logger.info(
        f"Finished downloading {language}: {destination}"
    )

    return destination


def iter_parquet_rows(
    parquet_path: Path,
    batch_size: int = 256,
) -> Iterator[Dict[str, Any]]:
    """
    Reads a local Parquet file in controlled Arrow batches.

    IMPORTANT:
    This does NOT load the entire Parquet file into RAM.

    Only one Arrow RecordBatch is materialized at a time.
    """

    logger.info(
        f"Opening Parquet file: {parquet_path}"
    )

    parquet_file = pq.ParquetFile(parquet_path)

    logger.info(
        f"Parquet metadata: "
        f"{parquet_file.metadata.num_rows:,} rows, "
        f"{parquet_file.metadata.num_row_groups:,} row groups"
    )

    for batch_number, batch in enumerate(
        parquet_file.iter_batches(
            batch_size=batch_size,
            use_threads=True,
        )
    ):
        logger.debug(
            f"Reading Parquet batch {batch_number}"
        )

        rows = batch.to_pylist()

        for row in rows:
            yield row


def get_row_generator(
    lang: str,
    max_rows: int,
    split: str = "train",
    skip: int = 0,
    cache_dir: str = "data/cache",
    batch_size: int = 256,
) -> Iterator[Dict[str, Any]]:
    """
    Downloads and streams a language-specific Parquet file.

    The file is stored on disk, but only small batches are loaded
    into memory at any given time.

    Args:
        lang:
            Language code: hi or mr.

        max_rows:
            Maximum number of dataset rows to yield.

        split:
            Dataset split. Currently train.

        skip:
            Number of rows to skip for checkpoint recovery.

        cache_dir:
            Local directory for downloaded Parquet files.

        batch_size:
            Number of rows processed per Arrow batch.

    Yields:
        Dataset rows as dictionaries.
    """

    lang = lang.lower().strip()

    if lang not in LANGUAGE_FILES:
        raise ValueError(
            f"Unsupported language '{lang}'. "
            f"Use one of: {list(LANGUAGE_FILES.keys())}"
        )

    cache_path = (
        Path(cache_dir)
        / split
        / LANGUAGE_FILES[lang].split("/")[-1]
    )

    # Download only if we don't already have the file.
    if not cache_path.exists():

        logger.info(
            f"Cached Parquet file not found for {lang}."
        )

        download_parquet(
            language=lang,
            destination=cache_path,
            split=split,
        )

    else:
        logger.info(
            f"Using existing cached Parquet file:\n"
            f"{cache_path}"
        )

    yielded = 0
    skipped = 0

    for row in iter_parquet_rows(
        parquet_path=cache_path,
        batch_size=batch_size,
    ):

        if skipped < skip:
            skipped += 1
            continue

        if yielded >= max_rows:
            logger.info(
                f"Reached max_rows={max_rows} for language '{lang}'."
            )
            break

        yield row

        yielded += 1
