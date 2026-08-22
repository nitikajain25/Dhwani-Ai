from typing import List, Dict, Any

from ingestion.schemas import Chunk, VectorRecord
from ingestion.embedder import BGEM3Embedder
from ingestion.vector_builder import build_vector_record
from ingestion.embedding_store import EmbeddingBatchStore
from ingestion.logging_config import logger


class BatchProcessor:
    """
    Converts chunks into embeddings and persists them as local JSONL batches.

    Flow:

        chunks
          ↓
        BGE-M3
          ↓
        embeddings
          ↓
        VectorRecords
          ↓
        EmbeddingBatchStore
          ↓
        batch_XXXXXX.jsonl
    """

    def __init__(
        self,
        embedder: BGEM3Embedder,
        batch_size: int = 64,
        store: EmbeddingBatchStore | None = None,
    ):
        self.embedder = embedder
        self.batch_size = batch_size
        self.store = store or EmbeddingBatchStore()

    def process_batch(
        self,
        chunks: List[Chunk],
        batch_id: str,
    ) -> Dict[str, Any]:

        if not chunks:
            raise ValueError("Cannot process an empty chunk batch.")

        logger.info(
            f"Processing batch '{batch_id}' "
            f"with {len(chunks)} chunks."
        )

        # ---------------------------------------------------------
        # 1. Generate embeddings
        # ---------------------------------------------------------

        texts = [chunk.text for chunk in chunks]

        embeddings = self.embedder.embed_texts(texts)

        if len(embeddings) != len(chunks):
            raise RuntimeError(
                f"Embedding count mismatch: "
                f"{len(chunks)} chunks -> "
                f"{len(embeddings)} embeddings"
            )

        # ---------------------------------------------------------
        # 2. Build VectorRecords
        # ---------------------------------------------------------

        records: List[VectorRecord] = []

        for chunk, embedding in zip(chunks, embeddings):

            record = build_vector_record(
                chunk=chunk,
                embedding=embedding,
            )

            records.append(record)

        # ---------------------------------------------------------
        # 3. Persist completed batch locally
        # ---------------------------------------------------------

        output_path = self.store.save_batch(
            batch_id=batch_id,
            records=records,
        )

        logger.info(
            f"Batch '{batch_id}' completed successfully. "
            f"Vectors: {len(records)}"
        )

        return {
            "batch_id": batch_id,
            "chunk_count": len(chunks),
            "embedding_count": len(embeddings),
            "vector_count": len(records),
            "output_path": str(output_path),
        }