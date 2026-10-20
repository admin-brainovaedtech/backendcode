
import re
from dataclasses import dataclass

from app.services.embedding_service import EmbeddingService
from storage.qdrant_storage import (
    get_qdrant_client,
    COLLECTION_NAME
)


@dataclass
class SemanticSearchResult:
    score: float
    text: str
    chapter_number: int
    chapter: str
    document: str
    page: int


class SemanticSearch:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.client = get_qdrant_client()

    def search(self, query: str, limit: int = 5):
        """Search by vector similarity, as before."""
        query_vector = self.embedding_service.embed_query(query)

        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=limit,
            with_payload=True
        )

        search_results = []

        for result in results.points:
            payload = result.payload or {}

            search_results.append(
                SemanticSearchResult(
                    score=result.score,
                    text=payload.get("text", ""),
                    chapter_number=payload.get("chapter_number", 0),
                    chapter=payload.get("chapter", "Unknown"),
                    document=payload.get("document", ""),
                    page=payload.get("page", 0)
                )
            )

        return search_results

    def search_keyword_fallback(self, query: str, limit: int = 5):
        """
        Scan the small Qdrant collection for exact concept terms.
        This is a fallback, not a replacement for vector search.
        Keyword matches are validated before being used to answer.
        """
        stopwords = {
            "a", "an", "the", "is", "are", "was", "were",
            "what", "which", "who", "where", "when", "why",
            "how", "do", "does", "did", "of", "in", "on",
            "to", "for", "and", "or", "with", "by", "explain",
            "define", "tell", "me", "about", "please"
        }

        terms = [
            word for word in re.findall(r"[a-zA-Z0-9]+", query.lower())
            if len(word) > 2 and word not in stopwords
        ]

        if not terms:
            return []

        # Scan all points. This is suitable for the current
        # small collection; use indexed full-text search at scale.
        offset = None
        matches = []

        while True:
            response = self.client.scroll(
                collection_name=COLLECTION_NAME,
                offset=offset,
                limit=100,
                with_payload=True,
                with_vectors=False
            )

            points, next_offset = response

            for point in points:
                payload = point.payload or {}
                text = payload.get("text", "")
                text_lower = text.lower()

                matched_terms = [
                    term for term in terms if term in text_lower
                ]

                if not matched_terms:
                    continue

                # Rank by number of distinct query terms matched,
                # then by occurrences of those terms.
                coverage = len(set(matched_terms))
                occurrences = sum(
                    text_lower.count(term) for term in set(matched_terms)
                )

                matches.append(
                    (
                        coverage,
                        occurrences,
                        SemanticSearchResult(
                            # Zero means this result came from keyword
                            # matching, not a vector similarity score.
                            score=0.0,
                            text=text,
                            chapter_number=payload.get("chapter_number", 0),
                            chapter=payload.get("chapter", "Unknown"),
                            document=payload.get("document", ""),
                            page=payload.get("page", 0)
                        )
                    )
                )

            if next_offset is None:
                break

            offset = next_offset

        matches.sort(
            key=lambda item: (item[0], item[1]),
            reverse=True
        )

        # Deduplicate chunks by chapter, page and text.
        selected = []
        seen = set()

        for _, _, result in matches:
            key = (result.chapter, result.page, result.text)

            if key in seen:
                continue

            seen.add(key)
            selected.append(result)

            if len(selected) >= limit:
                break

        return selected
