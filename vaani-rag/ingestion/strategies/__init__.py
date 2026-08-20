from typing import Any
from transformers import AutoTokenizer
from ingestion.logging_config import logger

_TOKENIZER = None

def get_tokenizer() -> Any:
    """Loads and caches the BGE-M3 tokenizer."""
    global _TOKENIZER
    if _TOKENIZER is None:
        try:
            # Load tokenizer from Hugging Face or local cache
            _TOKENIZER = AutoTokenizer.from_pretrained("BAAI/bge-m3")
        except Exception as e:
            logger.warning(
                f"Could not load BGE-M3 tokenizer. Using fallback word-based token count estimator. Error: {e}"
            )
    return _TOKENIZER

def count_tokens(text: str) -> int:
    """
    Counts tokens in the text using the BGE-M3 tokenizer.
    If the tokenizer cannot be loaded, falls back to a word-based heuristic estimation.
    """
    if not text:
        return 0
    tokenizer = get_tokenizer()
    if tokenizer is not None:
        try:
            return len(tokenizer.encode(text, add_special_tokens=False))
        except Exception as e:
            logger.debug(f"Tokenizer encode failed, using fallback: {e}")
            
    # Fallback heuristic: 1.6 tokens per word on average for multilingual text
    words = text.split()
    return int(len(words) * 1.6)
