from dataclasses import dataclass
from typing import List, Optional

from qdrant_client import QdrantClient

from ingestion.config import QDRANT_COLLECTION_NAME
from ingestion.embedder import BGEM3Embedder


@dataclass
class RetrievalResult:
    """
    One semantic-search result returned from Qdrant.
    """

    score: float
    text: str
    language: Optional[str]
    chunk_id: Optional[str]
    parent_passage_id: Optional[str]
    strategy: Optional[str]
    query_id: Optional[str]
    query_type: Optional[str]
    is_selected: Optional[bool]


class QdrantRetriever:
    """
    Converts a user query into a BGE-M3 embedding and
    retrieves semantically similar chunks from Qdrant.
    """

    def __init__(
        self,
        client: QdrantClient,
        embedder: BGEM3Embedder,
        collection_name: str = QDRANT_COLLECTION_NAME,
    ):
        self.client = client
        self.embedder = embedder
        self.collection_name = collection_name

    def search(
        self,
        query: str,
        top_k: int = 5,
        language: Optional[str] = None,
    ) -> List[RetrievalResult]:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        # ---------------------------------------------------------
        # 1. Embed the user query with the same BGE-M3 model
        # ---------------------------------------------------------

        query_vector = self.embedder.embed_query(
            query.strip()
        )

        # ---------------------------------------------------------
        # 2. Optional language filtering
        # ---------------------------------------------------------

        query_filter = None

        if language:
            from qdrant_client.models import (
                Filter,
                FieldCondition,
                MatchValue,
            )

            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="language",
                        match=MatchValue(
                            value=language
                        ),
                    )
                ]
            )

        # ---------------------------------------------------------
        # 3. Search Qdrant
        # ---------------------------------------------------------

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        # ---------------------------------------------------------
        # 4. Convert Qdrant results into our result objects
        # ---------------------------------------------------------

        results = []

        for point in response.points:

            payload = point.payload or {}

            results.append(
                RetrievalResult(
                    score=float(point.score),
                    text=str(
                        payload.get(
                            "text",
                            "",
                        )
                    ),
                    language=payload.get(
                        "language"
                    ),
                    chunk_id=payload.get(
                        "chunk_id"
                    ),
                    parent_passage_id=payload.get(
                        "parent_passage_id"
                    ),
                    strategy=payload.get(
                        "strategy"
                    ),
                    query_id=payload.get(
                        "query_id"
                    ),
                    query_type=payload.get(
                        "query_type"
                    ),
                    is_selected=payload.get(
                        "is_selected"
                    ),
                )
            )

        return results