import time
import random
from typing import List, Dict, Any
from pinecone import Index
from ingestion.schemas import VectorRecord
from ingestion.logging_config import logger

def upload_vectors_in_batches(
    index: any,
    vectors: List[VectorRecord],
    namespace: str,
    batch_size: int = 100,
    max_retries: int = 5,
    initial_delay: float = 1.0
) -> Dict[str, Any]:
    """
    Upserts a list of VectorRecord objects into Pinecone Cloud.
    Applies batching and exponential backoff retry logic.
    
    Args:
        index: The Pinecone Index connection.
        vectors: List of VectorRecord objects.
        namespace: The namespace target ('en', 'hi', or 'mr').
        batch_size: Upsert batch size.
        max_retries: Maximum exponential retries before failing a batch.
        initial_delay: Start delay for backoff.
        
    Returns:
        Dictionary of execution metrics (attempted, uploaded, failed, retries, duration, rate).
    """
    total_attempted = len(vectors)
    total_uploaded = 0
    total_failed = 0
    total_retries = 0
    
    t0 = time.time()
    
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        
        # Pinecone upsert format: list of tuples (id, values, metadata)
        pinecone_payload = []
        for record in batch:
            pinecone_payload.append((record.id, record.values, record.metadata))
            
        retries = 0
        success = False
        delay = initial_delay
        
        while retries <= max_retries:
            try:
                # Execute the upsert call
                index.upsert(vectors=pinecone_payload, namespace=namespace)
                total_uploaded += len(batch)
                success = True
                break
            except Exception as e:
                retries += 1
                total_retries += 1
                
                if retries > max_retries:
                    logger.error(
                        f"Failed to upsert batch (offset {i}) after {max_retries} attempts: {e}"
                    )
                    total_failed += len(batch)
                    break
                
                # Exponential backoff with jitter: delay * 2^(retry - 1) + jitter
                sleep_time = delay * (2 ** (retries - 1)) + random.uniform(0, 0.2)
                logger.warning(
                    f"Pinecone upsert failed: {e}. Retrying batch {i//batch_size} "
                    f"in {sleep_time:.2f}s (retry {retries}/{max_retries})..."
                )
                time.sleep(sleep_time)
                
    duration = time.time() - t0
    rate = total_uploaded / duration if duration > 0 else 0.0
    
    return {
        "attempted": total_attempted,
        "uploaded": total_uploaded,
        "failed": total_failed,
        "retries": total_retries,
        "duration": round(duration, 2),
        "rate_per_sec": round(rate, 2)
    }
