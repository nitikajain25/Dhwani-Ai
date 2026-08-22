import sys
import json
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Prevent terminal encoding failures
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from ingestion.embedder import BGEM3Embedder
from ingestion.rag_pipeline import RAGBaselinePipeline

QUERIES_FILE = PROJECT_ROOT / "evaluation" / "queries.jsonl"
RESULTS_FILE = PROJECT_ROOT / "evaluation" / "results" / "stage3_baseline_results.jsonl"

def main():
    print("=" * 80)
    print("VAANIRAG STAGE 3 baseline RAG EVALUATION")
    print("=" * 80)

    # 1. Initialize RAG baseline pipeline
    print("\nInitializing Pipeline (loading OpenVINO BGE-M3 model)...")
    try:
        # Load local embedder
        embedder = BGEM3Embedder()
        pipeline = RAGBaselinePipeline(embedder=embedder)
        print("SUCCESS: Pipeline initialized successfully!")
    except Exception as e:
        print(f"FAILED to initialize pipeline: {e}")
        return

    # 2. Load Stage 3 evaluation queries (30 queries)
    if not QUERIES_FILE.exists():
        print(f"FAILED: Queries file not found at {QUERIES_FILE}")
        return

    queries = []
    with open(QUERIES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                queries.append(json.loads(line))

    print(f"Loaded {len(queries)} evaluation queries.")

    # 3. Create results directory
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 4. Evaluate queries
    print("\nRunning RAG generation...")
    evaluated_count = 0
    
    with open(RESULTS_FILE, "w", encoding="utf-8") as out:
        for idx, item in enumerate(queries, 1):
            q_text = item["query"]
            q_lang = item["language"]
            q_id = item["query_id"]
            
            print(f"\n[{idx}/{len(queries)}] Processing ({q_lang.upper()}): {q_text}")
            
            t0 = time.time()
            response = pipeline.generate_answer(query=q_text, language=q_lang, top_k=5)
            elapsed = time.time() - t0
            
            print(f"  Status: {'SUCCESS' if response.success else 'FAILED'}")
            print(f"  Answer: {response.answer}")
            print(f"  Retrieved Chunks: {len(response.retrieved_candidates)}")
            print(f"  Latency Profiles:")
            print(f"    Retrieval: {response.telemetry.retrieval_ms:.2f} ms")
            print(f"    Context Prep: {response.telemetry.context_prep_ms:.2f} ms")
            print(f"    Inference (Gemini): {response.telemetry.gemini_generation_ms:.2f} ms")
            print(f"    Total Process: {response.telemetry.total_ms:.2f} ms")

            # Format result record
            result_record = {
                "query_id": q_id,
                "query": q_text,
                "language": q_lang,
                "success": response.success,
                "answer": response.answer,
                "retrieved_candidates": [
                    {
                        "chunk_id": c.chunk_id,
                        "text": c.text,
                        "language": c.language,
                        "score": c.retrieval_score
                    }
                    for c in response.retrieved_candidates
                ],
                "telemetry": {
                    "retrieval_ms": response.telemetry.retrieval_ms,
                    "context_prep_ms": response.telemetry.context_prep_ms,
                    "gemini_generation_ms": response.telemetry.gemini_generation_ms,
                    "total_ms": response.telemetry.total_ms
                },
                "error": response.error_message
            }
            out.write(json.dumps(result_record, ensure_ascii=False) + "\n")
            evaluated_count += 1
            
            # Short throttle to prevent hitting Gemini Cloud API rate limits
            if not response.success and "429" in (response.error_message or ""):
                print("  Rate Limit Hit (429)! Backing off for 20 seconds...")
                time.sleep(20.0)
            else:
                time.sleep(4.5)

    print("\n" + "=" * 80)
    print(f"STAGE 3 BASELINE RAG EVALUATION COMPLETE: {evaluated_count} queries processed.")
    print(f"Results written to: {RESULTS_FILE}")
    print("=" * 80)

if __name__ == "__main__":
    main()
