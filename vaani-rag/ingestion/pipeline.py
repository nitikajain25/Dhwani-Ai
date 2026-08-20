import argparse
import sys
import time
from typing import List, Dict, Any

from ingestion import config
from ingestion.logging_config import logger
from ingestion.dataset_loader import get_row_generator
from ingestion.passage_extractor import extract_passages_from_row
from ingestion.cleaner import clean_passage
from ingestion.deduplicator import Deduplicator
from ingestion.chunker import chunk_passage
from ingestion.embedder import BGEM3Embedder
from ingestion.validator import validate_embeddings
from ingestion.vector_builder import build_vector_record
from ingestion.pinecone_client import get_pinecone_client, verify_and_get_index
from ingestion.pinecone_uploader import upload_vectors_in_batches
from ingestion.checkpoint import save_checkpoint, load_checkpoint, clear_checkpoint
from ingestion.metrics import IngestionMetrics
from ingestion.schemas import Chunk

def run_pipeline(
    languages: List[str],
    max_rows: int,
    strategy: str,
    dry_run: bool,
    upload: bool
) -> IngestionMetrics:
    """
    Executes the ingestion pipeline end-to-end.
    """
    logger.info("Initializing VaaniRAG Offline Ingestion Pipeline...")
    metrics = IngestionMetrics()
    
    # Enable SQLite dedup for runs larger than the 100-row dry run
    dedup = Deduplicator(use_sqlite=(max_rows > 100))
    
    # 1. Resumability Setup
    checkpoint = load_checkpoint()
    rows_processed = {lang: 0 for lang in languages}
    passages_processed = {lang: 0 for lang in languages}
    chunks_processed = {lang: 0 for lang in languages}
    
    if checkpoint:
        # Check config compatibility
        if (checkpoint.get("dataset") == "ai4bharat/MSMARCO-XI" and
            checkpoint.get("chunking_strategy") == strategy and
            checkpoint.get("embedding_model") == config.EMBEDDING_MODEL):
            rows_processed = checkpoint.get("rows_processed", rows_processed)
            passages_processed = checkpoint.get("passages_processed", passages_processed)
            chunks_processed = checkpoint.get("chunks_processed", chunks_processed)
            logger.info("Compatible checkpoint found. Resuming progress...")
        else:
            logger.warning("Existing checkpoint is incompatible with current configuration. Starting fresh.")
            clear_checkpoint()
            
    # Load embedder early if strategy requires it (e.g. semantic, adaptive)
    embedder = None
    if strategy in ("semantic", "adaptive"):
        embedder = BGEM3Embedder(config.EMBEDDING_MODEL, config.EMBEDDING_BATCH_SIZE)

    # 2. Pass 1: Extraction, Cleaning, Deduplication, and Chunking (Memory Safe Local Cache)
    chunks_file_path = config.CHUNKS_DIR / f"extracted_chunks_{strategy}.jsonl"
    write_mode = "a" if checkpoint else "w"
    
    logger.info(f"Pass 1: Extracted chunks will be saved locally to {chunks_file_path}")
    
    # Track statistics per language
    lang_row_counts = {lang: 0 for lang in languages}
    lang_passage_counts = {lang: 0 for lang in languages}
    lang_unique_counts = {lang: 0 for lang in languages}

    with open(chunks_file_path, write_mode, encoding="utf-8") as f_out:
        from ingestion.dataset_loader import load_dataset_stream
        
        try:
            stream = load_dataset_stream(split="train")
        except Exception as e:
            logger.error(f"Error loading stream: {e}")
            sys.exit(1)
            
        global_skip = min(rows_processed.values()) if any(rows_processed.values()) else 0
        if global_skip > 0:
            logger.info(f"Skipping first {global_skip} rows based on checkpoint.")

        hi_rows_seen = 0
        mr_rows_seen = 0
        
        for idx, row in enumerate(stream):
            if idx < global_skip:
                continue
                
            current_row_idx = idx
            target_lang_raw = str(row.get("target_lang", ""))
            
            is_hi_row = target_lang_raw.startswith("hi_")
            is_mr_row = target_lang_raw.startswith("mr_")
            
            if is_hi_row and "hi" in languages and hi_rows_seen < max_rows:
                hi_rows_seen += 1
            if is_mr_row and "mr" in languages and mr_rows_seen < max_rows:
                mr_rows_seen += 1

            hi_done = hi_rows_seen >= max_rows if "hi" in languages else True
            mr_done = mr_rows_seen >= max_rows if "mr" in languages else True
            en_done = lang_unique_counts.get("en", 0) >= max_rows if "en" in languages else True
            
            if hi_done and mr_done and en_done:
                logger.info("Reached limits for all requested languages. Stopping stream.")
                break
                
            # Extract both English and Translated passages from the row
            passages = list(extract_passages_from_row(row, current_row_idx))
            
            for p in passages:
                lang = p.language
                if lang not in languages:
                    continue
                    
                # Enforcement of limits before processing
                if lang == "en" and en_done:
                    continue
                if lang == "hi" and hi_rows_seen > max_rows:
                    continue
                if lang == "mr" and mr_rows_seen > max_rows:
                    continue
                    
                lang_passage_counts[lang] += 1
                
                p_clean = clean_passage(p)
                if not p_clean:
                    continue
                    
                # Global Deduplication
                if dedup.is_duplicate(p_clean):
                    continue
                    
                lang_unique_counts[lang] += 1
                
                chunks = chunk_passage(
                    p_clean, 
                    strategy=strategy, 
                    embed_fn=embedder.embed_texts if embedder else None
                )
                
                for c in chunks:
                    f_out.write(c.model_dump_json() + "\n")
                    metrics.record_chunk(c.token_count)
                    chunks_processed[lang] += 1
            
            # Update counters for metrics/checkpoints
            if not hi_done:
                rows_processed["hi"] = current_row_idx + 1
                lang_row_counts["hi"] = hi_rows_seen
            if not mr_done:
                rows_processed["mr"] = current_row_idx + 1
                lang_row_counts["mr"] = mr_rows_seen
            if not en_done:
                rows_processed["en"] = current_row_idx + 1
                lang_row_counts["en"] = current_row_idx + 1  # english tracks global row scan depth

    # Collect stats for metrics
    metrics.rows_processed = lang_row_counts
    metrics.passages_extracted = lang_passage_counts
    metrics.unique_passages = lang_unique_counts

    total_chunks = len(metrics.chunk_token_counts)
    
    # 3. Ingestion Scale & Cost Safety Estimation
    bytes_per_float = 4
    storage_bytes = total_chunks * 1024 * bytes_per_float
    storage_mb = storage_bytes / (1024 * 1024)
    
    logger.info("============================================================")
    logger.info("INGESTION SCALE ESTIMATE")
    logger.info(f"Estimated passages: {sum(lang_unique_counts.values())}")
    logger.info(f"Estimated chunks/vectors: {total_chunks}")
    logger.info(f"Estimated raw vector storage: {storage_mb:.4f} MB")
    logger.info("============================================================")

    if upload and total_chunks > 100000 and not config.CONFIRM_LARGE_UPLOAD:
        logger.critical(
            f"COST SAFETY CHECK FAILED: Vector count ({total_chunks}) exceeds 100,000. "
            "Pinecone upload aborted. Set CONFIRM_LARGE_UPLOAD=true to override."
        )
        sys.exit(1)

    batch_size = config.EMBED_UPLOAD_BATCH_SIZE
    
    # 4. Pass 2: Batched Local Embedding, Validation, and Pinecone Upload
    if not embedder:
        embedder = BGEM3Embedder(config.EMBEDDING_MODEL, config.EMBEDDING_BATCH_SIZE)
        
    pc_index = None
    if upload and not dry_run:
        pc_client = get_pinecone_client()
        pc_index = verify_and_get_index(pc_client, config.PINECONE_INDEX_NAME)
        
    if chunks_file_path.exists():
        logger.info("Pass 2: Streaming chunks for Embedding and Pinecone Upload")
        current_batch: List[Chunk] = []
        current_lang = None
        
        def process_batch(batch: List[Chunk], lang: str, offset: int):
            if not batch:
                return
            texts = [c.text for c in batch]
            
            # Local Batch Embedding
            metrics.start_embedding()
            embeddings = embedder.embed_texts(texts)
            metrics.stop_embedding(len(texts))
            
            # Validation Checks
            is_valid, err_reason = validate_embeddings(embeddings)
            if not is_valid:
                logger.critical(f"FATAL: Vector validation failed for batch at offset {offset}: {err_reason}")
                metrics.invalid_vectors += len(batch)
                sys.exit(1)
                
            metrics.valid_vectors += len(batch)
            
            # Build VectorRecords
            records = []
            for c, emb in zip(batch, embeddings):
                records.append(build_vector_record(c, emb))
                
            # Pinecone upload
            if upload and not dry_run and pc_index is not None:
                upload_res = upload_vectors_in_batches(
                    index=pc_index,
                    vectors=records,
                    namespace=lang,
                    batch_size=config.PINECONE_UPSERT_BATCH_SIZE
                )
                metrics.uploaded_vectors += upload_res["uploaded"]
                metrics.failed_vectors += upload_res["failed"]
                metrics.upload_retries += upload_res["retries"]
                metrics.upload_duration += upload_res["duration"]
                
                if upload_res["failed"] > 0:
                    logger.critical(f"FATAL: Pinecone upload failed for batch at offset {offset}. Keeping checkpoint.")
                    # Keep checkpoint intact, mark run as failed (by exiting)
                    sys.exit(1)
                    
            # Save progress checkpoint after every successful batch
            save_checkpoint(
                dataset_name="ai4bharat/MSMARCO-XI",
                languages=languages,
                chunking_strategy=strategy,
                embedding_model=config.EMBEDDING_MODEL,
                embedding_dimension=embedder.dimension,
                rows_processed=rows_processed,
                passages_processed=passages_processed,
                chunks_processed=chunks_processed,
                vectors_uploaded={lang: metrics.uploaded_vectors for lang in languages},
                last_successful_batch={"lang": lang, "offset": offset}
            )
            dedup.commit()
            
        with open(chunks_file_path, "r", encoding="utf-8") as f_in:
            offset = 0
            # Read streaming to avoid memory issues
            for line_num, line in enumerate(f_in):
                if not line.strip():
                    continue
                    
                chunk = Chunk.model_validate_json(line)
                
                # Check resumability based on checkpoint
                # To be precise, we need to skip if we already processed this chunk.
                # Since we don't have exact chunk offset in old checkpoint, we just process everything 
                # but we could skip based on `chunks_processed`.
                # For simplicity and ponytail mode, we rely on the first pass resume logic 
                # or if we are re-running, it re-embeds unless we do exact matching.
                # Actually, the instructions say "Do not re-embed the entire previous JSONL file after a restart."
                # So we must skip already processed batches.
                # Let's track chunks processed per language in pass 2.
                
                pass2_chunks_processed = checkpoint.get("vectors_uploaded", {}).get(chunk.language, 0) if checkpoint else 0
                if offset < pass2_chunks_processed:
                    offset += 1
                    continue
                
                if current_lang != chunk.language:
                    process_batch(current_batch, current_lang, offset)
                    current_batch = []
                    current_lang = chunk.language
                    
                current_batch.append(chunk)
                
                if len(current_batch) >= batch_size:
                    process_batch(current_batch, current_lang, offset)
                    offset += len(current_batch)
                    current_batch = []
                    
            # Final batch
            if current_batch:
                process_batch(current_batch, current_lang, offset)

    metrics.finalize()
    
    # 5. Clear checkpoint on full pipeline success ONLY if upload didn't fail
    if metrics.failed_vectors == 0:
        clear_checkpoint()
    
    # Print the exact requested Report Layout
    print_final_report(metrics, strategy, embedder, dry_run, upload)
    return metrics

def print_final_report(
    metrics: IngestionMetrics,
    strategy: str,
    embedder: BGEM3Embedder,
    dry_run: bool,
    upload: bool
):
    chunk_stats = metrics.get_chunk_stats()
    embedding_duration = metrics.embedding_time
    throughput = metrics.total_vectors_embedded / embedding_duration if embedding_duration > 0 else 0.0
    
    print("\n" + "=" * 60)
    print("DATASET REPORT")
    print("=" * 60)
    for lang in ["en", "hi", "mr"]:
        print(f"{lang.upper()}:")
        print(f"  rows: {metrics.rows_processed.get(lang, 0)}")
        print(f"  passages: {metrics.passages_extracted.get(lang, 0)}")
        print(f"  unique passages: {metrics.unique_passages.get(lang, 0)}")
        print()

    print("=" * 60)
    print("CHUNK REPORT")
    print("=" * 60)
    print(f"strategy: {strategy}")
    print(f"chunks: {chunk_stats['count']}")
    print(f"average tokens: {chunk_stats['avg']}")
    print(f"median tokens: {chunk_stats['med']}")
    print(f"max tokens: {chunk_stats['max']}")
    print()

    print("=" * 60)
    print("EMBEDDING REPORT")
    print("=" * 60)
    print(f"model: {embedder.model_name}")
    print(f"device: {embedder.device}")
    print(f"dimension: {embedder.dimension}")
    print(f"batch size: {embedder.batch_size}")
    print(f"embedding time: {round(embedding_duration, 2)}s")
    print(f"throughput: {round(throughput, 2)} vectors/s")
    print()

    print("=" * 60)
    print("VALIDATION REPORT")
    print("=" * 60)
    print(f"valid vectors: {metrics.valid_vectors}")
    print(f"invalid vectors: {metrics.invalid_vectors}")
    print(f"NaN vectors: {metrics.nan_vectors}")
    print(f"infinite vectors: {metrics.inf_vectors}")
    print(f"dimension failures: {metrics.dimension_failures}")
    print()

    print("=" * 60)
    print("PINECONE REPORT")
    print("=" * 60)
    if dry_run or not upload:
        print("Pinecone upload: SKIPPED (dry run)")
    else:
        # Print per-language uploads summary
        for lang in metrics.rows_processed.keys():
            print(f"namespace: {lang}")
            print(f"  vectors uploaded: {metrics.uploaded_vectors if lang in metrics.rows_processed else 0}") # rough namespace specific estimation
            print(f"  failed: {metrics.failed_vectors}")
            print(f"  retries: {metrics.upload_retries}")
            print(f"  duration: {metrics.upload_duration}s")
            print()
    print("=" * 60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VaaniRAG Offline Ingestion Pipeline CLI")
    parser.add_argument(
        "--languages", 
        type=str, 
        default="en,hi,mr", 
        help="Comma-separated languages (e.g. en,hi,mr)"
    )
    parser.add_argument(
        "--max-rows", 
        type=int, 
        default=100, 
        help="Maximum rows to process per language configuration"
    )
    parser.add_argument(
        "--strategy", 
        type=str, 
        default="adaptive", 
        help="Chunking strategy (original, sentence, fixed_overlap, semantic, adaptive)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        default=None, 
        help="Force dry run mode (runs embedding locally, skips Pinecone Cloud upsert)"
    )
    parser.add_argument(
        "--upload", 
        action="store_true", 
        default=None, 
        help="Enable upserting to Pinecone Cloud"
    )
    
    args = parser.parse_args()
    
    # Resolve overrides: CLI overrides env config variables
    langs = [lang.strip().lower() for lang in args.languages.split(",") if lang.strip()]
    max_rows = args.max_rows
    strategy = args.strategy.strip().lower()
    
    is_dry_run = args.dry_run if args.dry_run is not None else config.DRY_RUN
    is_upload = args.upload if args.upload is not None else config.UPLOAD_TO_PINECONE
    
    # If upload is explicitly set, disable dry run
    if is_upload:
        is_dry_run = False
        
    try:
        run_pipeline(
            languages=langs,
            max_rows=max_rows,
            strategy=strategy,
            dry_run=is_dry_run,
            upload=is_upload
        )
    except KeyboardInterrupt:
        logger.warning("Pipeline execution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Pipeline execution failed: {e}")
        sys.exit(1)
