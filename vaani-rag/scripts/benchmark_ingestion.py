import sys
import time
from typing import List
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ingestion import config
from ingestion.dataset_loader import get_row_generator
from ingestion.passage_extractor import extract_passages_from_row
from ingestion.cleaner import clean_passage
from ingestion.deduplicator import Deduplicator
from ingestion.chunker import chunk_passage
from ingestion.embedder import BGEM3Embedder
from ingestion.strategies import count_tokens

def main():
    print("Initializing Ingestion Chunker Benchmarking Script...")
    
    # 1. Load Embedder
    embedder = BGEM3Embedder(config.EMBEDDING_MODEL, config.EMBEDDING_BATCH_SIZE)
    
    # 2. Extract a controlled sample of unique passages from the dataset
    languages = ["en", "hi", "mr"]
    sample_size_per_lang = 5
    unique_passages = []
    dedup = Deduplicator()
    
    print(f"Loading {sample_size_per_lang} rows per language to build benchmark sample...")
    for lang in languages:
        row_gen = get_row_generator(lang, max_rows=sample_size_per_lang, split="train")
        for idx, row in enumerate(row_gen):
            passages = list(extract_passages_from_row(row, lang, idx))
            for p in passages:
                p_clean = clean_passage(p)
                if p_clean and not dedup.is_duplicate(p_clean):
                    unique_passages.append(p_clean)
                    
    num_passages = len(unique_passages)
    print(f"Total unique passages in controlled sample: {num_passages}\n")
    
    strategies = ["original", "sentence", "fixed_overlap", "semantic", "adaptive"]
    
    print(f"{'Strategy':<15} | {'Chunks':<8} | {'Avg Tokens':<10} | {'Embed Time':<10} | {'Throughput':<10} | {'Storage Est':<12}")
    print("-" * 75)
    
    # 3. Benchmark each strategy
    for strategy in strategies:
        # Generate chunks
        chunks = []
        for p in unique_passages:
            p_chunks = chunk_passage(
                p, 
                strategy=strategy, 
                embed_fn=embedder.embed_texts
            )
            chunks.extend(p_chunks)
            
        num_chunks = len(chunks)
        
        # Calculate tokens stats
        token_counts = [c.token_count for c in chunks]
        avg_tokens = sum(token_counts) / num_chunks if num_chunks > 0 else 0.0
        
        # Measure embedding execution speed
        texts = [c.text for c in chunks]
        t0 = time.time()
        embeddings = embedder.embed_texts(texts)
        embed_duration = time.time() - t0
        
        throughput = num_chunks / embed_duration if embed_duration > 0 else 0.0
        
        # Vector size estimate: count * 1024 * 4 bytes
        bytes_per_float = 4
        storage_est_kb = (num_chunks * 1024 * bytes_per_float) / 1024
        
        print(
            f"{strategy:<15} | {num_chunks:<8} | {avg_tokens:<10.1f} | "
            f"{embed_duration:<9.2f}s | {throughput:<8.1f} v/s | {storage_est_kb:<8.2f} KB"
        )
        
    print("-" * 75)
    print("NOTE: Retrieval latency, Recall@K, and MRR metrics will be evaluated by the runtime application later.")

if __name__ == "__main__":
    main()
