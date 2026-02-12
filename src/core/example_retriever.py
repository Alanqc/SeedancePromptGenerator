"""Example retrieval skeleton."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class RetrievalResult:
    """Retrieved example IDs placeholder."""

    example_ids: List[str] = field(default_factory=list)


class ExampleRetriever:
    """No-op retriever for skill examples."""

    def retrieve(self, tags: List[str]) -> RetrievalResult:
        _ = tags
        return RetrievalResult()

