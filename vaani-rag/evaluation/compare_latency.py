import json
import statistics
from pathlib import Path

def analyze_results():
    base_dir = Path("c:/Users/HP/OneDrive/Desktop/Vaani/vaani-rag/evaluation/results")
    baseline_file = base_dir / "stage3_baseline_results.jsonl"
    reranked_file = base_dir / "stage3_reranked_results.jsonl"
    
    def get_telemetry(path):
        retrieval = []
        reranking = []
        total = []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
                    t = data.get("telemetry", {})
                    retrieval.append(t.get("retrieval_ms", 0))
                    reranking.append(t.get("reranking_ms", 0))
                    total.append(t.get("total_ms", 0))
        except FileNotFoundError:
            pass
        return retrieval, reranking, total

    b_ret, b_rer, b_tot = get_telemetry(baseline_file)
    r_ret, r_rer, r_tot = get_telemetry(reranked_file)

    if not b_ret or not r_ret:
        print("Missing data.")
        return

    print("=== PHASE 1C METRICS REPORT ===")
    print(f"Queries Processed: {len(r_ret)}")
    
    print("\n[Baseline Latency (Top-5 -> Gemini)]")
    print(f"  Avg Retrieval (ms) : {statistics.mean(b_ret):.2f}")
    print(f"  Avg Reranking (ms) : 0.00")
    print(f"  Avg Total (ms)     : {statistics.mean(b_tot):.2f}")

    print("\n[Reranked Latency (Top-20 -> BGE-Reranker -> Top-5 -> Gemini)]")
    print(f"  Avg Retrieval (ms) : {statistics.mean(r_ret):.2f}")
    print(f"  Avg Reranking (ms) : {statistics.mean(r_rer):.2f}")
    print(f"  Avg Total (ms)     : {statistics.mean(r_tot):.2f}")
    
    print("\n[Latency Overhead]")
    overhead = statistics.mean(r_rer)
    print(f"  Reranking Overhead : +{overhead:.2f} ms")

if __name__ == '__main__':
    analyze_results()
