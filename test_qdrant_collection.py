from storage.qdrant_storage import (
    create_collection,
    get_qdrant_client,
    COLLECTION_NAME
)


def main():

    create_collection()

    client = get_qdrant_client()

    info = client.get_collection(
        COLLECTION_NAME
    )

    print()
    print("=" * 60)
    print("QDRANT COLLECTION")
    print("=" * 60)

    print(
        f"\nCollection: "
        f"{COLLECTION_NAME}"
    )

    print(
        f"Status: "
        f"{info.status}"
    )

    print(
        f"Vector size: "
        f"{info.config.params.vectors.size}"
    )

    print(
        f"Distance: "
        f"{info.config.params.vectors.distance}"
    )

    print(
        f"Points: "
        f"{info.points_count}"
    )


if __name__ == "__main__":
    main()