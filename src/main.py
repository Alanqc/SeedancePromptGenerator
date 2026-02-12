"""Application entrypoint for the skeleton system."""

import sys

from .core.orchestrator import Orchestrator


def main() -> int:
    """Run Phase 1 MVP flow."""
    user_input = " ".join(sys.argv[1:]).strip() or "拍一个赛博朋克雨夜场景，使用85mm镜头。"
    orchestrator = Orchestrator()
    result = orchestrator.run(user_input)
    print(result.message)
    print("\n=== Prompt ===")
    print(result.prompt_text)
    print("\n=== Negative Prompt ===")
    print(result.negative_prompt)
    if result.validation_issues:
        print("\n=== Physics Warnings ===")
        for issue in result.validation_issues:
            print(f"- {issue}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

