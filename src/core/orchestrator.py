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


class Orchestrator:
    """Phase 1 orchestrator: Layer 1 + Layer 3 only."""

    def __init__(self) -> None:
        self.intention_parser = IntentionParser()
        self.prompt_generator = PromptGenerator()
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
        )

