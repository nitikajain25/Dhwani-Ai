from typing import Iterator, Dict, Any
from datasets import load_dataset
from ingestion.logging_config import logger

def load_dataset_stream(split: str = "train") -> Any:
    """
    Loads a streaming connection to the Hugging Face dataset.
    Uses the 'default' configuration as the dataset has a single stream.
    
    Args:
        split: The dataset split (e.g., 'train', 'validation').
        
    Returns:
        A streaming HF Dataset object.
    """
    dataset_id = "ai4bharat/MSMARCO-XI"
    config_name = "default"
    
    logger.info(f"Initializing HF stream for {dataset_id} (config: {config_name}, split: {split})")
    try:
        # Load dataset in streaming mode
        dataset = load_dataset(dataset_id, name=config_name, split=split, streaming=True)
        return dataset
    except Exception as e:
        logger.critical(f"Failed to stream dataset configuration '{config_name}': {e}")
        raise e
