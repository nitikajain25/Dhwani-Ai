from typing import List, Callable, Optional
from ingestion.schemas import Passage, Chunk
from ingestion.strategies.original import chunk_original
from ingestion.strategies.sentence import chunk_sentence
from ingestion.strategies.fixed_overlap import chunk_fixed_overlap
from ingestion.strategies.semantic import chunk_semantic
from ingestion.strategies.adaptive import chunk_adaptive
from ingestion.logging_config import logger

def chunk_passage(
    passage: Passage,
    strategy: str = "adaptive",
    embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
    **kwargs
) -> List[Chunk]:
    """
    Routes the passage to the configured chunking strategy.
    
    Args:
        passage: The input Passage object.
        strategy: The chunking strategy name.
        embed_fn: Optional sentence embedding function (required for semantic chunking).
        **kwargs: Optional parameters for individual strategies.
        
    Returns:
        A list of generated Chunk Pydantic models.
    """
    strat = strategy.lower().strip()
    
    if strat == "original":
        chunks = chunk_original(passage)
    elif strat == "sentence":
        target = kwargs.get("target_size", 384)
        min_sz = kwargs.get("min_size", 64)
        chunks = chunk_sentence(passage, target_size=target, min_size=min_sz)
    elif strat == "fixed_overlap":
        size = kwargs.get("chunk_size", 384)
        overlap = kwargs.get("chunk_overlap", 64)
        chunks = chunk_fixed_overlap(passage, chunk_size=size, chunk_overlap=overlap)
    elif strat == "semantic":
        threshold = kwargs.get("distance_threshold", 0.3)
        target = kwargs.get("target_size", 384)
        chunks = chunk_semantic(
            passage, 
            embed_fn=embed_fn, 
            distance_threshold=threshold, 
            target_size=target
        )
    elif strat == "adaptive":
        short = kwargs.get("short_limit", 150)
        med = kwargs.get("medium_limit", 500)
        long_lim = kwargs.get("long_limit", 1000)
        threshold = kwargs.get("distance_threshold", 0.3)
        chunks = chunk_adaptive(
            passage,
            embed_fn=embed_fn,
            short_limit=short,
            medium_limit=med,
            long_limit=long_lim,
            distance_threshold=threshold
        )
    else:
        logger.warning(f"Unknown chunking strategy '{strategy}'. Defaulting to 'original'.")
        chunks = chunk_original(passage)

    # Post-processing guard: Ensure no chunk exceeds the 8192-token BGE-M3 safe limit
    final_chunks = []
    for c in chunks:
        if c.token_count > 8192:
            logger.warning(
                f"Generated chunk {c.chunk_id} has {c.token_count} tokens, "
                f"exceeding BGE-M3 safe limit of 8192. Splitting with fixed overlap."
            )
            temp_p = Passage(
                passage_id=c.parent_passage_id,
                text=c.text,
                language=c.language,
                query_id=c.query_id,
                query_type=c.query_type,
                is_selected=c.is_selected,
                original_record_index=passage.original_record_index,
                content_hash=c.content_hash
            )
            sub_chunks = chunk_fixed_overlap(temp_p, chunk_size=4000, chunk_overlap=200)
            for sc in sub_chunks:
                sc.strategy = c.strategy
                sc.chunk_id = f"{sc.language}_{sc.strategy}_{sc.content_hash}"
            final_chunks.extend(sub_chunks)
        else:
            final_chunks.append(c)
            
    return final_chunks
