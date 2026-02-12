"""Base interface for all LLM plugins."""

from abc import ABC, abstractmethod
from typing import Dict, List


class BaseClient(ABC):
    """Abstract LLM client contract."""

    @abstractmethod
    def parse_intention(self, text: str, image_paths: List[str]) -> Dict[str, str]:
        """Parse user intent into structured fields."""

    @abstractmethod
    def generate_prompt(self, intention_payload: Dict[str, str]) -> str:
        """Generate a final prompt string."""

    @abstractmethod
    def validate_physics(self, prompt_text: str) -> Dict[str, str]:
        """Validate physical consistency of prompt text."""

    @abstractmethod
    def analyze_image(self, image_path: str) -> Dict[str, str]:
        """Analyze a single image input."""

