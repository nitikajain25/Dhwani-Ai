import time
from typing import Dict, Any, List

class IngestionMetrics:
    """
    Maintains telemetry statistics for all stages of the pipeline.
    Produces formatted final reports.
    """
    def __init__(self):
        self.start_time = time.time()
        self.end_time = None
        
        # Progress counters by language
        self.rows_processed = {}
        self.passages_extracted = {}
        self.unique_passages = {}
        
        # Chunks telemetry
        self.chunk_count = 0
        self.chunk_token_sum = 0
        self.chunk_token_max = 0

        # Embedding telemetry
        self.embedding_start = None
        self.embedding_time = 0.0
        self.total_vectors_embedded = 0
        
        # Validation telemetry
        self.valid_vectors = 0
        self.invalid_vectors = 0
        self.nan_vectors = 0
        self.inf_vectors = 0
        self.dimension_failures = 0
        
        # Pinecone upload telemetry
        self.uploaded_vectors = 0
        self.failed_vectors = 0
        self.upload_retries = 0
        self.upload_duration = 0.0

    def start_embedding(self):
        self.embedding_start = time.time()

    def stop_embedding(self, count: int):
        if self.embedding_start:
            self.embedding_time += time.time() - self.embedding_start
            self.total_vectors_embedded += count
            self.embedding_start = None

    def record_chunk(self, token_count: int):
        self.chunk_count += 1
        self.chunk_token_sum += token_count
        if token_count > self.chunk_token_max:
            self.chunk_token_max = token_count

    def get_chunk_stats(self) -> Dict[str, Any]:
        """Calculates token counts distributions."""
        if self.chunk_count == 0:
            return {"count": 0, "avg": 0, "med": 0, "max": 0}
            
        avg_tokens = self.chunk_token_sum / self.chunk_count
        
        return {
            "count": self.chunk_count,
            "avg": round(avg_tokens, 2),
            "med": "N/A", # Dropped exact median to save memory for large runs
            "max": self.chunk_token_max
        }

    def finalize(self):
        self.end_time = time.time()

    def get_total_duration(self) -> float:
        end = self.end_time or time.time()
        return round(end - self.start_time, 2)
