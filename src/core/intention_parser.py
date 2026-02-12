"""Intent parsing skeleton."""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..llm_plugins.kimi_client import KimiClient


@dataclass
class Intention:
    """Structured intention for Phase 1."""

    style: str = "cinematic_general"
    mood: str = "neutral"
    lighting: str = "natural"
    subject: str = "角色"
    camera_hint: str = ""
    technical_hints: List[str] = field(default_factory=list)
    needs_precise_params: bool = False
    raw_input: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntentionParser:
    """Intent parser with Kimi plugin."""

    def __init__(self) -> None:
        self.client = KimiClient()

    def parse(self, user_input: str) -> Intention:
        payload = self.client.parse_intention(user_input, image_paths=[])
        return Intention(
            style=str(payload.get("style", "cinematic_general")),
            mood=str(payload.get("mood", "neutral")),
            lighting=str(payload.get("lighting", "natural")),
            subject=str(payload.get("subject", "角色")),
            camera_hint=str(payload.get("camera_hint", "")),
            technical_hints=list(payload.get("technical_hints", [])),
            needs_precise_params=bool(payload.get("needs_precise_params", False)),
            raw_input=str(payload.get("raw_input", user_input)),
            metadata={
                "provider": "kimi",
                "model": self.client.model,
            },
        )

