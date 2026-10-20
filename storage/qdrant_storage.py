import os
import os
import time
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)

from config.embedding_config import (
    EMBEDDING_DIMENSION
)


QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "brainova_class9"

def qdrant_point_id(chunk_id):

    return str(
        uuid.UUID(
            chunk_id[:32]
        )
    )

def upload_embeddings(
    embedded_chunks,
    batch_size=25
):

    client = get_qdrant_client()

    total = len(embedded_chunks)

    print(
        f"\nUploading {total} vectors "
        f"in batches of {batch_size}..."
    )

    uploaded = 0

    for start in range(
        0,
        total,
        batch_size
    ):

        batch = embedded_chunks[
            start:start + batch_size
        ]

        points = []

        for chunk in batch:

            points.append(
                PointStruct(
                    id=qdrant_point_id(chunk["id"]),
                    vector=chunk["embedding"],
                    payload={
                        "text": chunk["text"],
                        **chunk["metadata"]
                    }
                )
            )

        max_attempts = 3

        for attempt in range(
            1,
            max_attempts + 1
        ):

            try:

                client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points,
                    wait=True
                )

                uploaded += len(points)

                print(
                    f"Uploaded "
                    f"{uploaded}/{total}"
                )

                break

            except Exception as error:

                print(
                    f"Batch failed "
                    f"(attempt {attempt}/"
                    f"{max_attempts}): "
                    f"{error}"
                )

                if attempt == max_attempts:
                    raise

                time.sleep(3)

def get_qdrant_client():

    if not QDRANT_URL:
        raise ValueError(
            "QDRANT_URL environment variable "
            "is not set."
        )

    if not QDRANT_API_KEY:
        raise ValueError(
            "QDRANT_API_KEY environment variable "
            "is not set."
        )

    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )


def create_collection():

    client = get_qdrant_client()

    collections = client.get_collections()

    existing_collections = {
        collection.name
        for collection in collections.collections
    }

    if COLLECTION_NAME in existing_collections:

        print(
            f"Collection already exists: "
            f"{COLLECTION_NAME}"
        )

        return

    client.create_collection(

        collection_name=COLLECTION_NAME,

        vectors_config=VectorParams(
            size=EMBEDDING_DIMENSION,
            distance=Distance.COSINE
        )
    )

    print(
        f"Created collection: "
        f"{COLLECTION_NAME}"
    )