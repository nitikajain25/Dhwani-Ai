import re
import hashlib
from typing import List
from ingestion.schemas import Passage, Chunk
from ingestion.strategies import count_tokens

def split_sentences(text: str) -> List[str]:
    """
    Splits text into sentences using standard punctuation for English, Hindi, and Marathi.
    Handles '.', '?', '!' for English, and '।', '॥' for Hindi/Marathi.
    """
    if not text:
        return []
    # Split on sentence terminals optionally followed by whitespace
    sentences = re.split(r"(?<=[.!?।॥])\s*", text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_sentence(passage: Passage, target_size: int = 384, min_size: int = 64) -> List[Chunk]:
    """
    Sentence-aware chunker. Groups sentences into cohesive units targeting a size in tokens.
    """
    text = passage.text
    sentences = split_sentences(text)
    if not sentences:
        return []

    chunks_text: List[str] = []
    current_chunk: List[str] = []
    current_tokens = 0

    for sent in sentences:
        sent_tokens = count_tokens(sent)
        
        # If adding this sentence would exceed target size, flush the current chunk first
        if current_chunk and (current_tokens + sent_tokens > target_size):
            chunks_text.append(" ".join(current_chunk))
            current_chunk = []
            current_tokens = 0
            
        current_chunk.append(sent)
        current_tokens += sent_tokens

    # Add final chunk
    if current_chunk:
        final_text = " ".join(current_chunk)
        # Avoid tiny residual chunks: merge with the last chunk if possible
        if chunks_text and (current_tokens < min_size):
            chunks_text[-1] = chunks_text[-1] + " " + final_text
        else:
            chunks_text.append(final_text)

    # Build Pydantic Chunk objects
    chunks: List[Chunk] = []
    for idx, chunk_txt in enumerate(chunks_text):
        t_count = count_tokens(chunk_txt)
        chunk_hash = hashlib.sha256(chunk_txt.encode("utf-8")).hexdigest()
        chunk_id = f"{passage.language}_sentence_{chunk_hash}"
        
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                parent_passage_id=passage.passage_id,
                text=chunk_txt,
                language=passage.language,
                strategy="sentence",
                chunk_index=idx,
                token_count=t_count,
                content_hash=chunk_hash,
                query_id=passage.query_id,
                query_type=passage.query_type,
                is_selected=passage.is_selected
            )
        )

    return chunks
