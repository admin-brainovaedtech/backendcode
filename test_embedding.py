from app.services.embedding_service import (
    EmbeddingService
)


def main():

    service = EmbeddingService()

    text = (
        "Uniform motion is motion in which "
        "an object covers equal distances "
        "in equal intervals of time."
    )

    embedding = service.embed_document(
        text,
        title="Describing Motion Around Us"
    )

    print()
    print("=" * 60)
    print("GEMINI EMBEDDING TEST")
    print("=" * 60)

    print(
        f"\nModel: "
        f"{service.__class__.__name__}"
    )

    print(
        f"Embedding dimensions: "
        f"{len(embedding)}"
    )

    print(
        "\nFirst 10 values:"
    )

    print(
        embedding[:10]
    )


if __name__ == "__main__":
    main()