"""Main orchestrator skeleton."""

from dataclasses import dataclass

from .intention_parser import IntentionParser
from .prompt_generator import PromptGenerator
from .physics_validator import PhysicsValidator


@dataclass
class RunResult:
    """Top-level execution result."""

    success: bool
    message: str
    prompt_text: str
    negative_prompt: str
    validation_issues: list[str]
    role_outputs: list[tuple[str, str]] = None  # (role_name, content)，多角色时有值

    def __post_init__(self) -> None:
        if self.role_outputs is None:
            self.role_outputs = []


class Orchestrator:
    """Phase 1 orchestrator: Layer 1 + Layer 3 only；支持多角色 skill。"""

    def __init__(self, skill_name: str = "seedance2") -> None:
        self.intention_parser = IntentionParser()
        self.prompt_generator = PromptGenerator(skill_name=skill_name)
        self.physics_validator = PhysicsValidator()

    def run(self, user_input: str) -> RunResult:
        intention = self.intention_parser.parse(user_input)
        prompt_result = self.prompt_generator.generate(intention)
        validation = self.physics_validator.validate(prompt_result.prompt_text)
        message = "Phase 1 MVP completed."
        if not validation.ok:
            message = "Phase 1 MVP completed with physics warnings."
        return RunResult(
            success=validation.ok,
            message=message,
            prompt_text=prompt_result.prompt_text,
            negative_prompt=prompt_result.negative_prompt,
            validation_issues=validation.issues,
            role_outputs=getattr(prompt_result, "role_outputs", []) or [],
        )

