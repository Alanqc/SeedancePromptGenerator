"""Intent parsing skeleton."""

from dataclasses import dataclass, field
from typing import Dict, List

from ..llm_plugins.kimi_client import KimiClient


@dataclass
class Intention:
    """Structured intention placeholder."""

    style: str = "unknown"
    mood: str = "neutral"
    lighting: str = "unspecified"
    technical_hints: List[str] = field(default_factory=list)
    needs_precise_params: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)


class IntentionParser:
    """No-op intention parser with pluggable LLM client."""

    def __init__(self) -> None:
        self.client = KimiClient()

    def parse(self, user_input: str) -> Intention:
        _ = self.client.parse_intention(user_input, image_paths=[])
        return Intention()

