from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)

from ingestion.config import QDRANT_COLLECTION_NAME
from ingestion.schemas import VectorRecord
from ingestion.logging_config import logger


VECTOR_DIMENSION = 1024


def ensure_collection(
    client: QdrantClient,
    collection_name: str = QDRANT_COLLECTION_NAME,
) -> None:
    """
    Create the DhawaniRAG Qdrant collection if it does not exist.

    BGE-M3:
        dimension = 1024
        distance  = cosine
    """

    collections = client.get_collections()

    existing_names = {
        collection.name
        for collection in collections.collections
    }

    if collection_name in existing_names:

        logger.info(
            f"Qdrant collection '{collection_name}' "
            "already exists."
        )

        info = client.get_collection(
            collection_name
        )

        actual_dimension = (
            info.config.params.vectors.size
        )

        if actual_dimension != VECTOR_DIMENSION:
            raise ValueError(
                f"Collection '{collection_name}' has "
                f"dimension {actual_dimension}. "
                f"Expected {VECTOR_DIMENSION}."
            )

        return

    logger.info(
        f"Creating Qdrant collection "
        f"'{collection_name}'..."
    )

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=VECTOR_DIMENSION,
            distance=Distance.COSINE,
        ),
    )

    logger.info(
        f"Qdrant collection '{collection_name}' "
        "created successfully."
    )


def upload_vectors(
    client: QdrantClient,
    collection_name: str,
    vectors: List[VectorRecord],
    batch_size: int = 100,
) -> Dict[str, Any]:
    """
    Upload VectorRecord objects to Qdrant.

    Vector IDs are converted to deterministic UUIDs because
    Qdrant point IDs must be unsigned integers or UUIDs.

    The original DhawaniRAG vector ID is preserved in payload.
    """

    if not vectors:
        return {
            "attempted": 0,
            "uploaded": 0,
            "failed": 0,
        }

    total_attempted = len(vectors)
    total_uploaded = 0
    total_failed = 0

    for offset in range(
        0,
        len(vectors),
        batch_size,
    ):

        batch = vectors[
            offset : offset + batch_size
        ]

        points = []

        for record in batch:

            # ------------------------------------------------
            # Convert deterministic DhawaniRAG ID into UUID.
            #
            # Example:
            # en_abc123...
            #
            # becomes a valid UUID derived from that string.
            # ------------------------------------------------

            import uuid

            point_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    record.id,
                )
            )

            payload = dict(
                record.metadata or {}
            )

            # Preserve original DhawaniRAG ID.
            payload[
                "vaani_id"
            ] = record.id

            payload[
                "text"
            ] = payload.get(
                "text",
                "",
            )

            points.append(
                PointStruct(
                    id=point_id,
                    vector=record.values,
                    payload=payload,
                )
            )

        try:

            client.upsert(
                collection_name=collection_name,
                points=points,
                wait=True,
            )

            total_uploaded += len(batch)

            logger.info(
                f"Uploaded Qdrant batch "
                f"{offset // batch_size + 1}: "
                f"{len(batch)} vectors"
            )

        except Exception as e:

            total_failed += len(batch)

            logger.error(
                f"Qdrant upload failed for batch "
                f"{offset // batch_size + 1}: {e}"
            )

            raise

    return {
        "attempted": total_attempted,
        "uploaded": total_uploaded,
        "failed": total_failed,
    }