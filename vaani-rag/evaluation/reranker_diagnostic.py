import time
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Prevent terminal encoding failures
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from ingestion.reranker import BGEM3Reranker
from ingestion.retriever import RetrievalResult

def run_diagnostic():
    print("=" * 60)
    print("RERANKER PERFORMANCE DIAGNOSTIC")
    print("=" * 60)
    
    # 1. Initialization and compilation
    t0 = time.time()
    reranker = BGEM3Reranker(device="GPU")
    init_time = time.time() - t0
    
    print(f"\n[Compilation / Init]")
    print(f"Total initialization time: {init_time:.2f}s")
    print(f"Reported compilation time inside init: {reranker.compilation_time_s:.2f}s")
    
    # Generate 20 dummy candidates
    query = "What is the process of photosynthesis?"
    dummy_text = "Photosynthesis is a system of biological processes by which photosynthetic organisms, such as most plants, algae, and cyanobacteria, convert light energy, typically from sunlight, into the chemical energy necessary to fuel their metabolism."
    
    # Let's make texts slightly different lengths to ensure dynamic shape variations
    texts = [dummy_text * (1 + (i % 3)) for i in range(20)]
    
    print(f"\n[Processing 20 candidates]")
    print(f"Query: {query}")
    print(f"Total candidates: {len(texts)}")
    
    # Break down the _predict_scores method to measure each part
    pairs = [[query, text] for text in texts]
    
    # --- Tokenization ---
    t0 = time.time()
    features = reranker.tokenizer(
        pairs,
        padding=True,
        truncation=True,
        return_tensors="pt",
    )
    tokenization_time = time.time() - t0
    print(f"\n[Timing Breakdown]")
    print(f"Tokenization & Tensor Prep time: {tokenization_time * 1000:.2f} ms")
    print(f"Input shape: {features['input_ids'].shape}")
    
    # --- Inference ---
    t0 = time.time()
    outputs = reranker.model(**features)
    inference_time = time.time() - t0
    print(f"OpenVINO Inference time: {inference_time * 1000:.2f} ms")
    
    # --- Post-processing ---
    t0 = time.time()
    logits = outputs.logits.detach().numpy()
    scores = logits.squeeze(axis=-1).tolist()
    if isinstance(scores, float):
        scores = [scores]
    post_time = time.time() - t0
    print(f"Post-processing time: {post_time * 1000:.2f} ms")
    
    total_time = tokenization_time + inference_time + post_time
    print(f"Total prediction loop time: {total_time * 1000:.2f} ms")
    
    # --- Check multiple calls (warmup / dynamic shape effects) ---
    print("\n[Running 3 more iterations to check for recompilation/caching]")
    for i in range(3):
        t0 = time.time()
        _ = reranker._predict_scores(query, texts)
        print(f"  Iteration {i+1} total time: {(time.time() - t0) * 1000:.2f} ms")
        
    print("\n[Diagnostics Details]")
    print(f"Underlying Model Type: {type(reranker.model)}")
    print(f"Device: {reranker.model.device}")

if __name__ == "__main__":
    run_diagnostic()
