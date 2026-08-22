import re


def clean_text(text: str) -> str:
    """
    Cleans extracted passage text without aggressively rewriting it.

    The cleaner:
    - normalizes whitespace
    - removes leading/trailing whitespace
    - fixes whitespace around common punctuation
    - preserves the actual textual content
    """

    if not isinstance(text, str):
        return ""

    text = text.strip()

    # Collapse repeated whitespace.
    text = re.sub(r"\s+", " ", text)

    # Remove whitespace immediately before punctuation.
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)

    # Add a missing space after punctuation when followed by a word.
    text = re.sub(r"([,.;:!?])([A-Za-z\u0900-\u097F])", r"\1 \2", text)

    return text.strip()