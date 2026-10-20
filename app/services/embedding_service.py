import os

from google import genai
from google.genai import types

from config.embedding_config import (
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION
)


class EmbeddingService:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable "
                "is not set."
            )

        self.client = genai.Client(
            api_key=api_key
        )

    def embed_document(
        self,
        text: str,
        title: str | None = None
    ):

        if title is None:
            title = "none"

        document_text = (
            f"title: {title} | "
            f"text: {text}"
        )

        response = self.client.models.embed_content(

            model=EMBEDDING_MODEL,

            contents=document_text,

            config=types.EmbedContentConfig(
                output_dimensionality=
                    EMBEDDING_DIMENSION
            )
        )

        return response.embeddings[0].values

    def embed_query(self, query: str):

        query_text = (
            f"task: search result | "
            f"query: {query}"
        )

        response = self.client.models.embed_content(

            model=EMBEDDING_MODEL,

            contents=query_text,

            config=types.EmbedContentConfig(
                output_dimensionality=
                    EMBEDDING_DIMENSION
            )
        )

        return response.embeddings[0].values