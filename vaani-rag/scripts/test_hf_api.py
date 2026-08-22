import requests

DATASET = "ai4bharat/MSMARCO-XI"

print("=" * 70)
print("HUGGING FACE DATASET SERVER TEST")
print("=" * 70)

url = "https://datasets-server.huggingface.co/first-rows"

params = {
    "dataset": DATASET,
    "config": "default",
    "split": "train",
}

print("\nRequesting first rows from Hugging Face Dataset Server...")

response = requests.get(
    url,
    params=params,
    timeout=60,
)

print("\nHTTP status:", response.status_code)

response.raise_for_status()

data = response.json()

print("\nResponse keys:")
print(data.keys())

print("\nNumber of rows returned:")
print(len(data.get("rows", [])))

if data.get("rows"):
    row = data["rows"][0]

    print("\n" + "=" * 70)
    print("FIRST ROW")
    print("=" * 70)

    print("Row keys:")
    print(row.keys())

    for key, value in row.items():
        print(f"\nKEY: {key}")
        print(f"TYPE: {type(value)}")

        text = repr(value)

        if len(text) > 2000:
            text = text[:2000] + "... [TRUNCATED]"

        print(text)

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)