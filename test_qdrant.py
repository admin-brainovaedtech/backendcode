from storage.qdrant_storage import get_qdrant_client


def main():

    client = get_qdrant_client()

    collections = client.get_collections()

    print("\nConnected to Qdrant successfully.")

    print(
        f"Collections: "
        f"{len(collections.collections)}"
    )

    for collection in collections.collections:

        print(
            f"- {collection.name}"
        )


if __name__ == "__main__":
    main()