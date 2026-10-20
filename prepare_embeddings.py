import json
import hashlib
import uuid
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "class9_science_chunks.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "embedding_ready_chunks.json"
)


def create_chunk_id(chunk):

    unique_text = (
        f"{chunk['document']}"
        f"|{chunk['page']}"
        f"|{chunk['content']}"
    )

    hash_value = hashlib.sha256(
        unique_text.encode("utf-8")
    ).hexdigest()

    return str(
        uuid.UUID(
            hash_value[:32]
        )
    )


def prepare_chunks():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    prepared = []

    for chunk in chunks:

        prepared.append({

            "id": create_chunk_id(chunk),

            "text": chunk["content"],

            "metadata": {

                "board":
                    chunk["board"],

                "class":
                    chunk["class"],

                "subject":
                    chunk["subject"],

                "chapter_number":
                    chunk["chapter_number"],

                "chapter":
                    chunk["chapter"],

                "document":
                    chunk["document"],

                "page":
                    chunk["page"]
            }
        })

    return prepared


def main():

    chunks = prepare_chunks()

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 60)
    print("EMBEDDING PREPARATION COMPLETE")
    print("=" * 60)

    print(
        f"\nInput chunks: "
        f"{len(chunks)}"
    )

    print(
        f"Output file:"
        f"\n{OUTPUT_FILE}"
    )

    if chunks:

        print("\nSample prepared chunk:")
        print("----------------------")

        print(
            json.dumps(
                chunks[0],
                ensure_ascii=False,
                indent=2
            )
        )


if __name__ == "__main__":
    main()