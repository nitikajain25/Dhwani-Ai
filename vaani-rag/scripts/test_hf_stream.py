from datasets import load_dataset


DATASET = "ai4bharat/MSMARCO-XI"

print("=" * 70)
print("CONTROLLED MSMARCO-XI STREAM TEST")
print("=" * 70)

columns = [
    "source_lang",
    "target_lang",
    "query_id",
    "query_type",
    "passages",
    "Eng_Query",
    "query",
]

print("\nLoading dataset...")
print("Configuration: default")
print("Split: train")
print("Streaming: True")

dataset = load_dataset(
    DATASET,
    name="default",
    split="train",
    streaming=True,
    columns=columns,
)

print("\nDataset loaded:")
print(dataset)

print("\nFetching first row...")

for row in dataset.take(1):

    print("\n" + "=" * 70)
    print("FIRST ROW RECEIVED")
    print("=" * 70)

    print("\nKeys:")
    print(list(row.keys()))

    for key, value in row.items():

        print("\n" + "-" * 70)
        print(f"FIELD: {key}")
        print(f"TYPE : {type(value)}")

        value_repr = repr(value)

        if len(value_repr) > 3000:
            value_repr = value_repr[:3000] + "... [TRUNCATED]"

        print(value_repr)

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)