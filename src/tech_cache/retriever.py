"""Tech cache retrieval placeholder."""

from typing import Dict


class TechCacheRetriever:
    """No-op retriever for precise technical parameters."""

    def query(self, term: str) -> Dict[str, str]:
        _ = term
        return {}

