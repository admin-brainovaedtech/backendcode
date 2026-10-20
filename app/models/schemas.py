from dataclasses import dataclass
from typing import List


@dataclass
class SourceChunk:

    chapter_number: int
    chapter: str
    document: str
    page: int
    content: str


@dataclass
class BrainovaResponse:

    answer: str
    sources: List[SourceChunk]