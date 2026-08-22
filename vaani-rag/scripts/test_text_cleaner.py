from ingestion.text_cleaner import clean_text


def main():
    print("=" * 70)
    print("VAANIRAG TEXT CLEANER TEST")
    print("=" * 70)

    tests = [
        (
            "The engineers iswhat their success truly meant.",
            "The engineers iswhat their success truly meant.",
        ),
        (
            "scientific minds  was   equally important",
            "scientific minds was equally important",
        ),
        (
            "Hello , world ! This is a test.",
            "Hello, world! This is a test.",
        ),
        (
            "फ्लोएममध्ये  प्रकाशसंश्लेषणाचे उत्पादने",
            "फ्लोएममध्ये प्रकाशसंश्लेषणाचे उत्पादने",
        ),
    ]

    for original, expected in tests:
        cleaned = clean_text(original)

        print("\nOriginal:")
        print(original)

        print("Cleaned:")
        print(cleaned)

        print("PASS" if cleaned == expected else "FAIL")

    print("\n" + "=" * 70)
    print("TEXT CLEANER TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()