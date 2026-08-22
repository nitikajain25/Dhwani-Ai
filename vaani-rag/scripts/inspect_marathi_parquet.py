from pathlib import Path
import pyarrow.parquet as pq


FILE = Path("data/raw/martrain.parquet")


print("=" * 70)
print("LOCAL HINDI PARQUET INSPECTION")
print("=" * 70)

if not FILE.exists():
    raise FileNotFoundError(f"File not found: {FILE}")

print(f"\nFile: {FILE}")
print(f"Size: {FILE.stat().st_size / (1024 ** 3):.2f} GB")

print("\nOpening Parquet metadata...")

parquet = pq.ParquetFile(FILE)

print("Parquet opened successfully.")

print("\nSchema:")
print(parquet.schema_arrow)

print("\nNumber of rows:")
print(parquet.metadata.num_rows)

print("\nNumber of row groups:")
print(parquet.metadata.num_row_groups)

print("\nColumns:")
for column in parquet.schema_arrow.names:
    print(f"  - {column}")

print("\nReading ONE small batch...")

batch = next(
    parquet.iter_batches(
        batch_size=1
    )
)

print("First row read successfully.")

row = batch.to_pylist()[0]

print("\nFirst-row fields:")
for key, value in row.items():

    print(f"\n--- {key} ---")

    if isinstance(value, str):
        print(value[:500])

    elif isinstance(value, list):
        print(f"List length: {len(value)}")

        if value:
            print("First item:")
            print(str(value[0])[:1000])

    elif isinstance(value, dict):
        print("Dictionary keys:")
        print(list(value.keys()))

        for k, v in value.items():
            if isinstance(v, list):
                print(
                    f"  {k}: list length={len(v)}"
                )
                if v:
                    print(
                        f"    first: {str(v[0])[:500]}"
                    )
            else:
                print(
                    f"  {k}: {str(v)[:500]}"
                )

    else:
        print(str(value)[:500])


print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)