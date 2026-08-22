import time
import statistics

from ingestion.qdrant_client import get_qdrant_client
from ingestion.config import QDRANT_COLLECTION_NAME
from ingestion.embedder import BGEM3Embedder
from ingestion.retriever import QdrantRetriever


QUERY = "What is the legal definition of mediation?"
TOP_K = 5

print("=" * 70)
print("VAANI RETRIEVAL + LATENCY TEST")
print("=" * 70)

# ------------------------------------------------------------
# Initialize
# ------------------------------------------------------------

print("\nInitializing Qdrant...")
client = get_qdrant_client()

print("Initializing BGE-M3...")
embedder = BGEM3Embedder()

retriever = QdrantRetriever(
    client=client,
    embedder=embedder,
    collection_name=QDRANT_COLLECTION_NAME,
)

# ------------------------------------------------------------
# Warm-up
# ------------------------------------------------------------

print("\nRunning 5 warm-up requests...")

for i in range(5):
    retriever.search(
        QUERY,
        top_k=TOP_K,
    )

print("Warm-up complete.")

# ------------------------------------------------------------
# Measured requests
# ------------------------------------------------------------

embedding_times = []
qdrant_times = []
total_times = []

print("\nRunning 30 measured requests...\n")

for i in range(30):

    # Measure embedding only
    start = time.perf_counter()

    query_vector = embedder.embed_query(QUERY)

    embedding_ms = (
        time.perf_counter() - start
    ) * 1000

    # Measure Qdrant only
    start = time.perf_counter()

    response = client.query_points(
        collection_name=QDRANT_COLLECTION_NAME,
        query=query_vector,
        limit=TOP_K,
        with_payload=True,
        with_vectors=False,
    )

    qdrant_ms = (
        time.perf_counter() - start
    ) * 1000

    total_ms = embedding_ms + qdrant_ms

    embedding_times.append(embedding_ms)
    qdrant_times.append(qdrant_ms)
    total_times.append(total_ms)

    print(
        f"{i + 1:02d}/30  "
        f"Embedding={embedding_ms:8.2f} ms  "
        f"Qdrant={qdrant_ms:8.2f} ms  "
        f"Total={total_ms:8.2f} ms"
    )


# ------------------------------------------------------------
# Statistics
# ------------------------------------------------------------

def percentile(values, p):
    values = sorted(values)

    index = (len(values) - 1) * p

    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    weight = index - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * weight
    )


def print_stats(name, values):

    print(f"\n{name}")

    print(f"  Min : {min(values):.2f} ms")
    print(f"  Max : {max(values):.2f} ms")
    print(f"  Mean: {statistics.mean(values):.2f} ms")
    print(f"  P50 : {percentile(values, 0.50):.2f} ms")
    print(f"  P95 : {percentile(values, 0.95):.2f} ms")
    print(f"  P99 : {percentile(values, 0.99):.2f} ms")


print("\n" + "=" * 70)
print("LATENCY RESULTS")
print("=" * 70)

print_stats(
    "Embedding latency",
    embedding_times,
)

print_stats(
    "Qdrant latency",
    qdrant_times,
)

print_stats(
    "Total retrieval latency",
    total_times,
)


# ------------------------------------------------------------
# Show actual retrieved results
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("RETRIEVAL RESULTS")
print("=" * 70)

results = retriever.search(
    QUERY,
    top_k=TOP_K,
)

for rank, result in enumerate(results, 1):

    print(f"\nRank {rank}")
    print(f"Score    : {result.score}")
    print(f"Language : {result.language}")
    print(f"Chunk ID : {result.chunk_id}")
    print(
        f"Selected : {result.is_selected}"
    )
    print(
        f"Text     : {result.text[:300]}"
    )

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)