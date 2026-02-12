"""Physics validation skeleton."""

from dataclasses import dataclass, field
from typing import List

from ..llm_plugins.kimi_client import KimiClient


@dataclass
class ValidationResult:
    """Physics validation output."""

    ok: bool
    issues: List[str] = field(default_factory=list)


class PhysicsValidator:
    """Simple physics checker for Phase 1."""

    def __init__(self) -> None:
        self.client = KimiClient()

    def validate(self, prompt_text: str) -> ValidationResult:
        payload = self.client.validate_physics(prompt_text)
        return ValidationResult(
            ok=bool(payload.get("ok", True)),
            issues=list(payload.get("issues", [])),
        )

