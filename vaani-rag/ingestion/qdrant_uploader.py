import hashlib
import uuid
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from ingestion.schemas import VectorRecord
from ingestion.config import QDRANT_COLLECTION_NAME
from ingestion.logging_config import logger


def vector_id_to_uuid(vector_id: str) -> str:
    """
    Converts our existing string vector/chunk ID into a
    deterministic UUID accepted by Qdrant.

    The original vector ID is still stored in the payload,
    so no identity information is lost.
    """

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            vector_id,
        )
    )


def upload_vectors_to_qdrant(
    client: QdrantClient,
    vectors: List[VectorRecord],
    namespace: str,
    batch_size: int = 64,
) -> Dict[str, Any]:
    """
    Upload VectorRecord objects to Qdrant.

    Each VectorRecord becomes one Qdrant point.

    Qdrant point:
        id      -> deterministic UUID
        vector  -> 1024-dimensional embedding
        payload -> original vector metadata
    """

    total = len(vectors)

    if total == 0:
        return {
            "attempted": 0,
            "uploaded": 0,
            "failed": 0,
        }

    uploaded = 0
    failed = 0

    for start in range(0, total, batch_size):

        batch = vectors[
            start:start + batch_size
        ]

        points = []

        for record in batch:

            qdrant_id = vector_id_to_uuid(
                record.id
            )

            payload = dict(
                record.metadata or {}
            )

            # Preserve the original DhawaniRAG ID.
            payload["vector_id"] = record.id

            # Store the namespace/language.
            payload["namespace"] = namespace

            points.append(
                PointStruct(
                    id=qdrant_id,
                    vector=record.values,
                    payload=payload,
                )
            )

        try:

            client.upsert(
                collection_name=QDRANT_COLLECTION_NAME,
                points=points,
                wait=True,
            )

            uploaded += len(batch)

            logger.info(
                f"Uploaded Qdrant batch "
                f"{start // batch_size + 1}: "
                f"{len(batch)} vectors"
            )

        except Exception as e:

            failed += len(batch)

            logger.exception(
                f"Qdrant upload failed for "
                f"batch starting at {start}: {e}"
            )

            raise

    return {
        "attempted": total,
        "uploaded": uploaded,
        "failed": failed,
    }