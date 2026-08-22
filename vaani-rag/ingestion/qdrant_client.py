from qdrant_client import QdrantClient

from ingestion.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
)
from ingestion.logging_config import logger


def get_qdrant_client() -> QdrantClient:
    """
    Create and return a Qdrant Cloud client.
    """

    if not QDRANT_URL:
        raise ValueError(
            "QDRANT_URL is missing from environment."
        )

    if not QDRANT_API_KEY:
        raise ValueError(
            "QDRANT_API_KEY is missing from environment."
        )

    try:
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )

        # Small connectivity check.
        client.get_collections()

        logger.info(
            "Successfully connected to Qdrant Cloud."
        )

        return client

    except Exception as e:
        logger.error(
            f"Failed to connect to Qdrant Cloud: {e}"
        )
        raise