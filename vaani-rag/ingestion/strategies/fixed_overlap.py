import hashlib
from typing import List
from ingestion.schemas import Passage, Chunk
from ingestion.strategies import count_tokens, get_tokenizer

def chunk_fixed_overlap(
    passage: Passage, 
    chunk_size: int = 384, 
    chunk_overlap: int = 64
) -> List[Chunk]:
    """
    Fixed-size sliding window chunker with overlapping boundaries.
    Defaults to 384 tokens with 64 tokens overlap.
    """
    text = passage.text
    tokenizer = get_tokenizer()
    chunks_text: List[str] = []

    # 1. Token-level chunking when BGE-M3 tokenizer is available
    if tokenizer is not None:
        try:
            tokens = tokenizer.encode(text, add_special_tokens=False)
            if len(tokens) <= chunk_size:
                chunks_text.append(text)
            else:
                step = chunk_size - chunk_overlap
                if step <= 0:
                    step = chunk_size
                
                for i in range(0, len(tokens), step):
                    window = tokens[i : i + chunk_size]
                    if not window:
                        break
                    decoded_chunk = tokenizer.decode(window, clean_up_tokenization_spaces=False).strip()
                    if decoded_chunk:
                        chunks_text.append(decoded_chunk)
                    # Stop if we have covered the end of the text
                    if i + chunk_size >= len(tokens):
                        break
        except Exception:
            tokenizer = None  # Force fallback to word approximation on exception

    # 2. Fallback to word-level approximation if tokenizer is unavailable
    if tokenizer is None:
        # Approximate: 1 word ~ 1.6 tokens for multilingual datasets
        approx_words_size = max(1, int(chunk_size / 1.6))
        approx_words_overlap = int(chunk_overlap / 1.6)
        
        words = text.split()
        if len(words) <= approx_words_size:
            chunks_text.append(text)
        else:
            step = approx_words_size - approx_words_overlap
            if step <= 0:
                step = approx_words_size
                
            for i in range(0, len(words), step):
                window = words[i : i + approx_words_size]
                if not window:
                    break
                chunks_text.append(" ".join(window))
                if i + approx_words_size >= len(words):
                    break

    # 3. Create Chunk objects
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
                strategy="fixed_overlap",
                chunk_index=idx,
                token_count=t_count,
                content_hash=chunk_hash,
                query_id=passage.query_id,
                query_type=passage.query_type,
                is_selected=passage.is_selected
            )
        )
    return chunks
