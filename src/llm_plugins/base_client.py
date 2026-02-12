"""Base interface for all LLM plugins."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseClient(ABC):
    """Abstract LLM client contract."""

    @abstractmethod
    def parse_intention(self, text: str, image_paths: List[str]) -> Dict[str, Any]:
        """Parse user intent into structured fields."""

    @abstractmethod
    def generate_prompt(self, intention_payload: Dict[str, Any]) -> str:
        """Generate a final prompt string."""

    @abstractmethod
    def validate_physics(self, prompt_text: str) -> Dict[str, Any]:
        """Validate physical consistency of prompt text."""

    @abstractmethod
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze a single image input."""

