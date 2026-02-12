"""Prompt generation for Phase 1 MVP."""

from dataclasses import dataclass

from .intention_parser import Intention
from ..llm_plugins.kimi_client import KimiClient


@dataclass
class PromptResult:
    """Prompt payload produced by layer 3."""

    prompt_text: str
    negative_prompt: str


class PromptGenerator:
    """Generate prompt text without RAG in Phase 1."""

    def __init__(self) -> None:
        self.client = KimiClient()

    def generate(self, intention: Intention) -> PromptResult:
        payload = {
            "style": intention.style,
            "mood": intention.mood,
            "lighting": intention.lighting,
            "camera_hint": intention.camera_hint or "35mm",
            "subject": intention.subject,
            "raw_input": intention.raw_input,
        }
        prompt_text = self.client.generate_prompt(payload)
        negative_prompt = (
            "low quality, blurry, inconsistent lighting, broken anatomy, "
            "object flicker, frame jitter, overexposed"
        )
        return PromptResult(prompt_text=prompt_text, negative_prompt=negative_prompt)

