import json
import os
import time
from typing import Dict, Any, List, Optional

from ingestion.config import CHECKPOINTS_DIR
from ingestion.logging_config import logger


CHECKPOINT_PATH = CHECKPOINTS_DIR / "checkpoint.json"


def save_checkpoint(
    dataset_name: str,
    languages: List[str],
    chunking_strategy: str,
    embedding_model: str,
    embedding_dimension: int,
    rows_processed: Dict[str, int],
    passages_processed: Dict[str, int],
    chunks_processed: Dict[str, int],
    vectors_uploaded: Dict[str, int],
    last_successful_batch: Dict[str, Any],
    completed_batches: Optional[List[str]] = None,
    status: str = "running",
    run_id: Optional[str] = None,
) -> None:
    """
    Saves the current ingestion state.

    The checkpoint describes work that has already been successfully
    completed/persisted.
    """

    checkpoint_data = {
        "dataset": dataset_name,
        "languages": languages,
        "chunking_strategy": chunking_strategy,
        "embedding_model": embedding_model,
        "embedding_dimension": embedding_dimension,

        "rows_processed": rows_processed,
        "passages_processed": passages_processed,
        "chunks_processed": chunks_processed,
        "vectors_uploaded": vectors_uploaded,

        "last_successful_batch": last_successful_batch,

        "completed_batches": completed_batches or [],

        "status": status,
        "run_id": run_id,

        "timestamp": time.time(),
        "timestamp_str": time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime()
        ),
    }

    temp_path = CHECKPOINT_PATH.with_suffix(".tmp")

    try:
        CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)

        # Write to a temporary file first.
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(
                checkpoint_data,
                f,
                indent=2,
                ensure_ascii=False,
            )
            f.flush()
            os.fsync(f.fileno())

        # Replace the previous checkpoint atomically.
        os.replace(temp_path, CHECKPOINT_PATH)

        logger.info(
            "Ingestion checkpoint saved. "
            f"Rows={rows_processed}, "
            f"Chunks={chunks_processed}, "
            f"Batches={len(checkpoint_data['completed_batches'])}"
        )

    except Exception as e:
        logger.error(
            f"Failed to write pipeline checkpoint: {e}"
        )

        # Clean up temporary file if it exists.
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception:
            pass


def load_checkpoint() -> Optional[Dict[str, Any]]:
    """
    Loads the latest ingestion checkpoint.

    Returns:
        Checkpoint dictionary if one exists and is valid.
        None otherwise.
    """

    if not CHECKPOINT_PATH.exists():
        logger.info(
            "No checkpoint file found at "
            f"{CHECKPOINT_PATH}."
        )
        return None

    try:
        with open(
            CHECKPOINT_PATH,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        logger.info(
            "Checkpoint loaded successfully. "
            f"Status={data.get('status')}, "
            f"Rows={data.get('rows_processed')}, "
            f"Chunks={data.get('chunks_processed')}, "
            f"Batches={len(data.get('completed_batches', []))}"
        )

        return data

    except Exception as e:
        logger.error(
            f"Failed to read checkpoint: {e}. "
            "Starting clean."
        )
        return None


def clear_checkpoint() -> None:
    """
    Deletes the checkpoint file and resets progress.
    """

    if CHECKPOINT_PATH.exists():
        try:
            CHECKPOINT_PATH.unlink()

            logger.info(
                "Cleared existing checkpoint file."
            )

        except Exception as e:
            logger.error(
                f"Failed to clear checkpoint file: {e}"
            )