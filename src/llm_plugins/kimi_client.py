"""Kimi plugin placeholder implementation."""

from typing import Dict, List

from .base_client import BaseClient


class KimiClient(BaseClient):
    """No-op implementation used by the skeleton."""

    def parse_intention(self, text: str, image_paths: List[str]) -> Dict[str, str]:
        _ = (text, image_paths)
        return {}

    def generate_prompt(self, intention_payload: Dict[str, str]) -> str:
        _ = intention_payload
        return ""

    def validate_physics(self, prompt_text: str) -> Dict[str, str]:
        _ = prompt_text
        return {"ok": "true"}

    def analyze_image(self, image_path: str) -> Dict[str, str]:
        _ = image_path
        return {}

