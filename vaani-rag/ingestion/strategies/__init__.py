from typing import Any
from pathlib import Path

from transformers import AutoTokenizer

from ingestion.logging_config import logger


_TOKENIZER = None


def get_tokenizer() -> Any:
    """
    Loads and caches the local BGE-M3 tokenizer.

    The tokenizer is loaded from the project's local model directory.
    No Hugging Face download is performed.
    """
    global _TOKENIZER

    if _TOKENIZER is None:
        try:
            project_root = Path(__file__).resolve().parents[2]

            tokenizer_path = (
                project_root
                / "models"
                / "bge-m3-openvino"
            )

            logger.info(
                f"Loading local BGE-M3 tokenizer from: {tokenizer_path}"
            )

            _TOKENIZER = AutoTokenizer.from_pretrained(
                str(tokenizer_path),
                local_files_only=True,
            )

            logger.info("Local BGE-M3 tokenizer loaded successfully.")

        except Exception as e:
            logger.warning(
                "Could not load local BGE-M3 tokenizer. "
                f"Using fallback word-based token count estimator. Error: {e}"
            )

    return _TOKENIZER


def count_tokens(text: str) -> int:
    """
    Counts tokens using the local BGE-M3 tokenizer.

    Falls back to a word-based estimate if the tokenizer
    cannot be loaded.
    """
    if not text:
        return 0

    tokenizer = get_tokenizer()

    if tokenizer is not None:
        try:
            return len(
                tokenizer.encode(
                    text,
                    add_special_tokens=False,
                )
            )
        except Exception as e:
            logger.debug(
                f"Tokenizer encode failed, using fallback: {e}"
            )

    # Fallback heuristic for multilingual text.
    words = text.split()
    return int(len(words) * 1.6)