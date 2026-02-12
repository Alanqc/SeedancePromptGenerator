"""Main orchestrator skeleton."""

from dataclasses import dataclass

from .example_retriever import ExampleRetriever
from .intention_parser import IntentionParser
from .physics_validator import PhysicsValidator


@dataclass
class RunResult:
    """Top-level execution result placeholder."""

    success: bool
    message: str


class Orchestrator:
    """No-op orchestrator wiring all core components."""

    def __init__(self) -> None:
        self.intention_parser = IntentionParser()
        self.example_retriever = ExampleRetriever()
        self.physics_validator = PhysicsValidator()

    def run(self, user_input: str) -> RunResult:
        intention = self.intention_parser.parse(user_input)
        self.example_retriever.retrieve(intention.technical_hints)
        self.physics_validator.validate("placeholder prompt")
        return RunResult(
            success=True,
            message="Skeleton is running. No business functionality is implemented.",
        )

