from typing import List, Callable, Optional
from ingestion.schemas import Passage, Chunk
from ingestion.strategies import count_tokens
from ingestion.strategies.original import chunk_original
from ingestion.strategies.sentence import chunk_sentence
from ingestion.strategies.fixed_overlap import chunk_fixed_overlap
from ingestion.strategies.semantic import chunk_semantic

def chunk_adaptive(
    passage: Passage,
    embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
    short_limit: int = 150,
    medium_limit: int = 500,
    long_limit: int = 1000,
    distance_threshold: float = 0.3
) -> List[Chunk]:
    """
    Adaptive chunker. Selects chunking strategy dynamically based on passage length.
    All strategy outputs have their strategy attribute set to 'adaptive' for schema uniformity.
    """
    token_count = count_tokens(passage.text)
    
    # Rule 1: Short Passage -> Keep Original
    if token_count <= short_limit:
        chunks = chunk_original(passage)
        for c in chunks:
            c.strategy = "adaptive"
        return chunks
        
    # Rule 2: Medium Passage -> Sentence-Aware Grouping (no overlap)
    elif token_count <= medium_limit:
        chunks = chunk_sentence(passage, target_size=256, min_size=64)
        for c in chunks:
            c.strategy = "adaptive"
        return chunks
        
    # Rule 3: Long Passage -> Fixed overlap chunking (controlled overlap)
    elif token_count <= long_limit:
        chunks = chunk_fixed_overlap(passage, chunk_size=384, chunk_overlap=64)
        for c in chunks:
            c.strategy = "adaptive"
        return chunks
        
    # Rule 4: Very Long Passage -> Fallback Fixed overlap
    else:
        chunks = chunk_fixed_overlap(passage, chunk_size=384, chunk_overlap=128)
            
        for c in chunks:
            c.strategy = "adaptive"
        return chunks
