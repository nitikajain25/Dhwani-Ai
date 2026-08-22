import json
import glob
import collections


files = glob.glob(
    "outputs/embeddings/vaani_batch_*.jsonl"
)

queries = collections.defaultdict(
    lambda: {
        "total": 0,
        "selected": 0,
        "languages": set(),
    }
)


for file_path in files:

    with open(
        file_path,
        encoding="utf-8",
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            record = json.loads(line)

            metadata = record.get(
                "metadata",
                {},
            )

            query_id = metadata.get(
                "query_id"
            )

            if query_id is None:
                continue

            queries[query_id]["total"] += 1

            if metadata.get(
                "is_selected",
                False,
            ):
                queries[query_id]["selected"] += 1

            queries[query_id]["languages"].add(
                metadata.get("language")
            )


print("=" * 70)
print("MSMARCO-XI RELEVANCE LABEL INSPECTION")
print("=" * 70)

print()
print("Embedding files:", len(files))
print("Unique query IDs:", len(queries))

print(
    "Queries with selected passages:",
    sum(
        1
        for v in queries.values()
        if v["selected"] > 0
    ),
)

print(
    "Queries without selected passages:",
    sum(
        1
        for v in queries.values()
        if v["selected"] == 0
    ),
)

print(
    "Total selected chunks:",
    sum(
        v["selected"]
        for v in queries.values()
    ),
)

print()

# ------------------------------------------------------------
# Show first 10 queries
# ------------------------------------------------------------

print("First 10 query IDs:")
print("-" * 70)

for query_id, data in list(
    queries.items()
)[:10]:

    print(
        f"{query_id}: "
        f"chunks={data['total']}, "
        f"selected={data['selected']}, "
        f"languages={sorted(data['languages'])}"
    )

print()
print("Inspection complete.")