import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

CHUNK_FILE = (
    PROJECT_ROOT
    / "data"
    / "class9_science_chunks.json"
)


def main():

    with open(
        CHUNK_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    print()
    print("=" * 60)
    print("BRAINOVA CHUNK VALIDATION")
    print("=" * 60)

    print(f"\nTotal chunks: {len(chunks)}")

    # --------------------------------------------------
    # Chapter count
    # --------------------------------------------------

    chapter_counts = Counter(
        (
            chunk["chapter_number"],
            chunk["chapter"]
        )
        for chunk in chunks
    )

    print("\nChapters found:")
    print("----------------")

    for (
        chapter_number,
        chapter_name
    ), count in sorted(chapter_counts.items()):

        print(
            f"Chapter {chapter_number}: "
            f"{chapter_name} "
            f"({count} chunks)"
        )

    # --------------------------------------------------
    # Document count
    # --------------------------------------------------

    document_counts = Counter(
        chunk["document"]
        for chunk in chunks
    )

    print("\nDocuments found:")
    print("----------------")

    for document, count in sorted(
        document_counts.items()
    ):

        print(
            f"{document}: {count} chunks"
        )

    # --------------------------------------------------
    # Metadata validation
    # --------------------------------------------------

    required_fields = [
        "board",
        "class",
        "subject",
        "chapter_number",
        "chapter",
        "document",
        "page",
        "content"
    ]

    invalid_chunks = 0

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        missing = [
            field
            for field in required_fields
            if field not in chunk
        ]

        if missing:

            invalid_chunks += 1

            print(
                f"\nChunk {index} "
                f"missing: {missing}"
            )

    print("\nMetadata validation:")
    print("--------------------")

    if invalid_chunks == 0:

        print(
            "All chunks contain required metadata."
        )

    else:

        print(
            f"{invalid_chunks} invalid chunks found."
        )

    # --------------------------------------------------
    # Sample chunk
    # --------------------------------------------------

    if chunks:

        print("\nSample chunk:")
        print("-------------")

        print(
            json.dumps(
                chunks[0],
                ensure_ascii=False,
                indent=2
            )
        )


if __name__ == "__main__":
    main()