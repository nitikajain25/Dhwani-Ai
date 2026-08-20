import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import torch
from ingestion.embedder import BGEM3Embedder

def main():
    print("Checking CUDA Device state...")
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    if cuda_available:
        print(f"CUDA Device name: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
    else:
        print("WARNING: CUDA is not available. Embedding will execute on CPU.")

    print("\nLoading BGE-M3 Model...")
    t0 = time.time()
    # Instantiate BGEM3Embedder (Singleton)
    embedder = BGEM3Embedder(model_name="BAAI/bge-m3", batch_size=16)
    load_time = time.time() - t0
    print(f"BGEM3Embedder loaded in {load_time:.2f}s")

    # Construct test corpus
    test_texts = [
        "MS MARCO translation for multiple Indic languages is useful for multilingual voice RAG.",
        "यह एक परीक्षण गद्यांश है जो हिंदी एम्बेडिंग के कार्य का सत्यापन करता है।",
        "मराठी मजकूर एन्कोडिंग गुणवत्तेची पडताळणी करण्यासाठी हा मजकूर वापरला जातो."
    ] * 10  # 30 texts to benchmark throughput
    
    print(f"\nRunning batch encoding for {len(test_texts)} sentences...")
    t1 = time.time()
    embeddings = embedder.embed_texts(test_texts)
    embedding_time = time.time() - t1
    
    num_vectors = len(embeddings)
    dim = len(embeddings[0]) if num_vectors > 0 else 0
    throughput = num_vectors / embedding_time if embedding_time > 0 else 0.0

    print("\n============================================================")
    print("EMBEDDING TEST REPORT")
    print("============================================================")
    print(f"model: {embedder.model_name}")
    print(f"device: {embedder.device}")
    print(f"dimension: {dim}")
    print(f"batch size: {embedder.batch_size}")
    print(f"embedding time: {round(embedding_time, 2)}s")
    print(f"throughput: {round(throughput, 2)} vectors/s")
    print("============================================================")

    # Verification checks
    if dim != 1024:
        print(f"FAIL: Expected 1024-dimensional embeddings, but got {dim}.")
        sys.exit(1)
        
    print("SUCCESS: Local embedding and device verification completed.")

if __name__ == "__main__":
    main()
