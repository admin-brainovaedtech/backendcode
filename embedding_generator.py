import json
import time
from pathlib import Path

from app.services.embedding_service import EmbeddingService


PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "embedding_ready_chunks.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "embedded_chunks.json"
)


def load_chunks():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_chunks(chunks):

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


def generate_embeddings():

    chunks = load_chunks()

    print()
    print("=" * 70)
    print("GEMINI EMBEDDING GENERATION")
    print("=" * 70)

    print(
        f"\nTotal chunks: {len(chunks)}"
    )

    embedding_service = EmbeddingService()

    embedded_chunks = []

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        print(
            f"\n[{index}/{len(chunks)}] "
            f"Chapter {chunk['metadata']['chapter_number']} "
            f"| Page {chunk['metadata']['page']}"
        )

        text = chunk["text"]

        title = chunk["metadata"]["chapter"]

        max_attempts = 3

        for attempt in range(
            1,
            max_attempts + 1
        ):

            try:

                embedding = (
                    embedding_service.embed_document(
                        text=text,
                        title=title
                    )
                )

                embedded_chunk = {
                    "id": chunk["id"],
                    "text": chunk["text"],
                    "embedding": embedding,
                    "metadata": chunk["metadata"]
                }

                embedded_chunks.append(
                    embedded_chunk
                )

                print(
                    f"Embedding generated "
                    f"({len(embedding)} dimensions)"
                )

                break

            except Exception as error:

                print(
                    f"Attempt {attempt} failed: "
                    f"{error}"
                )

                if attempt == max_attempts:

                    raise

                time.sleep(2)

        # Small delay to avoid hitting API limits
        time.sleep(0.2)

    save_chunks(embedded_chunks)

    print()
    print("=" * 70)
    print("EMBEDDING GENERATION COMPLETE")
    print("=" * 70)

    print(
        f"\nEmbeddings generated: "
        f"{len(embedded_chunks)}"
    )

    print(
        f"Output file:"
        f"\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":

    generate_embeddings()