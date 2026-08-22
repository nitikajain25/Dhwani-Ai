import hashlib
from typing import List
from ingestion.schemas import Passage, Chunk
from ingestion.strategies import count_tokens
from ingestion.logging_config import logger

def chunk_original(passage: Passage) -> List[Chunk]:
    """
    Keeps the original passage as a single chunk unit.
    Safe limit: BGE-M3 max input is 8192 tokens.
    """
    text = passage.text
    token_count = count_tokens(text)
    
    # BGE-M3 maximum sequence length is 8192.
    if token_count > 8192:
        logger.warning(
            f"Passage {passage.passage_id} has {token_count} tokens which exceeds the safe model limit of 8192. Routing to fixed-overlap."
        )
        # Use fixed-overlap for oversized passages
        from ingestion.strategies.fixed_overlap import chunk_fixed_overlap
        # Apply fixed overlap with 4000 token chunk size, 200 overlap to be safe and preserve content
        return chunk_fixed_overlap(passage, chunk_size=4000, chunk_overlap=200)

    chunk_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    chunk_id = f"{passage.language}_original_{chunk_hash}"
    
    chunk = Chunk(
        chunk_id=chunk_id,
        parent_passage_id=passage.passage_id,
        text=text,
        language=passage.language,
        strategy="original",
        chunk_index=0,
        token_count=token_count,
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        query_id=passage.query_id,
        query_type=passage.query_type,
        is_selected=passage.is_selected
    )
    
    return [chunk]

# Import tokenizer helper dynamically to avoid circular dependencies
from ingestion.strategies import get_tokenizer
