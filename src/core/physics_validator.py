"""Physics validation skeleton."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ValidationResult:
    """Physics validation output placeholder."""

    ok: bool = True
    issues: List[str] = field(default_factory=list)


class PhysicsValidator:
    """No-op physics checker."""

    def validate(self, prompt_text: str) -> ValidationResult:
        _ = prompt_text
        return ValidationResult()

