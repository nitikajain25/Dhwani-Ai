from datasets import load_dataset


DATASET_ID = "ai4bharat/MSMARCO-XI"


print("=" * 70)
print("MSMARCO-XI LIVE DATASET INSPECTION")
print("=" * 70)

print("\nLoading DEFAULT configuration in streaming mode...")

dataset = load_dataset(
    DATASET_ID,
    name="default",
    split="train",
    streaming=True,
    keep_in_memory=False,
)

print("\nDataset object:")
print(dataset)

print("\nFetching first row...")
print("If this takes more than ~60 seconds, press Ctrl+C.")

iterator = iter(dataset)

row = next(iterator)

print("FIRST ROW RECEIVED!")

print("\n" + "=" * 70)
print("ROW TYPE")
print("=" * 70)

print(type(row))

print("\n" + "=" * 70)
print("ROW KEYS")
print("=" * 70)

print(row.keys())

print("\n" + "=" * 70)
print("ROW CONTENT")
print("=" * 70)

for key, value in row.items():
    print(f"\nKEY: {key}")
    print(f"TYPE: {type(value)}")

    text = repr(value)

    if len(text) > 2000:
        text = text[:2000] + "... [TRUNCATED]"

    print(text)

print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)