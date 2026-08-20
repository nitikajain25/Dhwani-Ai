import re
import unicodedata
import hashlib
from typing import Optional
from ingestion.schemas import Passage
from ingestion.logging_config import logger

def clean_text(text: str) -> str:
    """
    Cleans raw text deterministically:
    - Normalizes Unicode (NFC) which is standard for Indic scripts.
    - Normalizes multiple spaces, tabs, and newlines into a single space.
    - Strips leading and trailing whitespaces.
    - Preserves case, Indic characters, punctuation, and sentence boundaries.
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Unicode safe normalization (NFC)
    normalized = unicodedata.normalize("NFC", text)
    
    # 2. Whitespace normalization: Replace sequences of tabs/newlines/spaces with a single space
    cleaned = re.sub(r"\s+", " ", normalized)
    
    return cleaned.strip()

def clean_passage(passage: Passage) -> Optional[Passage]:
    """
    Cleans a Passage object's text. Recalculates its content hash and passage_id.
    
    Args:
        passage: The input Passage object.
        
    Returns:
        The updated Passage object, or None if the passage text is empty.
    """
    cleaned_text = clean_text(passage.text)
    if not cleaned_text:
        logger.debug(f"Passage {passage.passage_id} became empty after cleaning. Filtering out.")
        return None

    # Update text
    passage.text = cleaned_text
    
    # Re-calculate hash based on cleaned text
    new_hash = hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest()
    passage.content_hash = new_hash
    
    # Reconstruct ID while keeping record_index and intra-row index if available
    parts = passage.passage_id.split("_")
    if len(parts) >= 5:
        # Format: {language}_passage_{old_hash[:16]}_{record_index}_{idx}
        record_index = parts[-2]
        idx = parts[-1]
        passage.passage_id = f"{passage.language}_passage_{new_hash[:16]}_{record_index}_{idx}"
    else:
        passage.passage_id = f"{passage.language}_passage_{new_hash[:16]}"
        
    return passage
