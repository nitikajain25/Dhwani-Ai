import hashlib
import numpy as np
from typing import List, Callable, Optional
from ingestion.schemas import Passage, Chunk
from ingestion.strategies import count_tokens
from ingestion.strategies.sentence import split_sentences, chunk_sentence
from ingestion.logging_config import logger

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calculates cosine similarity between two vectors."""
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return float(dot / (norm1 * norm2))

def chunk_semantic(
    passage: Passage,
    embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
    distance_threshold: float = 0.3,
    target_size: int = 384
) -> List[Chunk]:
    """
    Semantic chunker.
    1. Splits passage into sentences.
    2. Embeds all sentences in one batch.
    3. Calculates cosine distances between adjacent sentences.
    4. Triggers boundaries where distance > threshold or size exceeds limit.
    5. Groups sentences into chunks.
    
    If embed_fn is None, falls back to sentence-aware chunking.
    """
    text = passage.text
    sentences = split_sentences(text)
    
    if not sentences:
        return []
        
    if len(sentences) == 1:
        # Only one sentence, no boundaries to compute
        return chunk_sentence(passage, target_size=target_size)

    if embed_fn is None:
        logger.debug(f"No embed_fn provided for semantic chunking. Falling back to sentence chunker.")
        return chunk_sentence(passage, target_size=target_size)

    try:
        # Generate sentence embeddings in one batch
        embeddings = embed_fn(sentences)
        
        # Calculate cosine distance (1 - similarity) between adjacent sentences
        distances = []
        for i in range(len(sentences) - 1):
            v_curr = np.array(embeddings[i])
            v_next = np.array(embeddings[i+1])
            dist = 1.0 - cosine_similarity(v_curr, v_next)
            distances.append(dist)
            
        # Determine split points based on threshold
        splits = [False] * len(sentences)
        for i, dist in enumerate(distances):
            if dist > distance_threshold:
                splits[i] = True  # Split after sentence i
                
        # Group sentences
        chunks_text: List[str] = []
        current_chunk: List[str] = []
        current_tokens = 0
        
        for idx, sent in enumerate(sentences):
            sent_tokens = count_tokens(sent)
            
            # Flush current chunk if:
            # - We have content in the current chunk AND
            # - The previous boundary was a split OR adding this sentence exceeds target_size
            if current_chunk and (splits[idx - 1] or (current_tokens + sent_tokens > target_size)):
                chunks_text.append(" ".join(current_chunk))
                current_chunk = []
                current_tokens = 0
                
            current_chunk.append(sent)
            current_tokens += sent_tokens
            
        if current_chunk:
            chunks_text.append(" ".join(current_chunk))
            
    except Exception as e:
        logger.warning(f"Semantic chunking failed for passage {passage.passage_id}: {e}. Falling back to sentence chunker.")
        return chunk_sentence(passage, target_size=target_size)

    # Convert grouped texts to Chunk objects
    chunks: List[Chunk] = []
    for idx, chunk_txt in enumerate(chunks_text):
        chunk_txt_clean = chunk_txt.strip()
        if not chunk_txt_clean:
            continue
            
        t_count = count_tokens(chunk_txt_clean)
        chunk_hash = hashlib.sha256(chunk_txt_clean.encode("utf-8")).hexdigest()
        chunk_id = f"{passage.language}_{chunk_hash}"

        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                parent_passage_id=passage.passage_id,
                text=chunk_txt_clean,
                language=passage.language,
                strategy="semantic",
                chunk_index=idx,
                token_count=t_count,
                content_hash=chunk_hash,
                query_id=passage.query_id,
                query_type=passage.query_type,
                is_selected=passage.is_selected
            )
        )
    return chunks
