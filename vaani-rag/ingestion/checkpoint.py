import json
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
    last_successful_batch: Dict[str, Any]
) -> None:
    """
    Saves the current state of ingestion to outputs/checkpoints/checkpoint.json.
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
        "timestamp": time.time(),
        "timestamp_str": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }
    
    try:
        # Write atomicity (write to temp file and rename) is avoided as ponytail dev is boring/simple,
        # but standard write to file with UTF-8 is fine.
        with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Ingestion checkpoint saved: {rows_processed} rows processed.")
    except Exception as e:
        logger.error(f"Failed to write pipeline checkpoint: {e}")

def load_checkpoint() -> Optional[Dict[str, Any]]:
    """
    Loads and returns the last saved ingestion checkpoint.
    """
    if not CHECKPOINT_PATH.exists():
        logger.info("No checkpoint file found at outputs/checkpoints/checkpoint.json.")
        return None
        
    try:
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Checkpoint loaded successfully. Last run processed rows: {data.get('rows_processed')}")
        return data
    except Exception as e:
        logger.error(f"Failed to read checkpoint: {e}. Starting clean.")
        return None

def clear_checkpoint() -> None:
    """
    Deletes the checkpoint file to reset progress.
    """
    if CHECKPOINT_PATH.exists():
        try:
            CHECKPOINT_PATH.unlink()
            logger.info("Cleared existing checkpoint file.")
        except Exception as e:
            logger.error(f"Failed to clear checkpoint file: {e}")
