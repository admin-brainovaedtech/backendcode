import json
from pathlib import Path

from storage.qdrant_storage import (
    upload_embeddings,
    get_qdrant_client,
    COLLECTION_NAME
)


PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "embedded_chunks.json"
)


def main():

    print()
    print("=" * 70)
    print("QDRANT VECTOR UPLOAD")
    print("=" * 70)

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    print(
        f"\nEmbeddings loaded: "
        f"{len(chunks)}"
    )

    upload_embeddings(chunks)

    client = get_qdrant_client()

    info = client.get_collection(
        COLLECTION_NAME
    )

    print(
        f"\nCollection: "
        f"{COLLECTION_NAME}"
    )

    print(
        f"Points in Qdrant: "
        f"{info.points_count}"
    )


if __name__ == "__main__":

    main()