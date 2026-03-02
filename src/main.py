"""Application entrypoint for the skeleton system."""

import os
import sys

from .core.orchestrator import Orchestrator


def main() -> int:
    """Run Phase 1 MVP flow；可通过环境变量 SKILL_NAME 指定 skill（多角色配置）。"""
    user_input = " ".join(sys.argv[1:]).strip() or "拍一个赛博朋克雨夜场景，使用85mm镜头。"
    skill_name = os.getenv("SKILL_NAME", "seedance2")
    orchestrator = Orchestrator(skill_name=skill_name)
    roles = getattr(orchestrator.prompt_generator, "_roles", [])
    if roles:
        names = [r.get("name") or r.get("id", "") for r in roles]
        print(f"Skill: {skill_name}, 已加载 {len(roles)} 个角色: {names}")
    else:
        print(f"Skill: {skill_name}, 未配置多角色，使用单轮生成")
    result = orchestrator.run(user_input)
    print(result.message)

    if result.role_outputs:
        print(f"\n--- 已加载 {len(result.role_outputs)} 个角色，各角色输出 ---")
        for i, (role_name, content) in enumerate(result.role_outputs, 1):
            print(f"\n=== Role {i}: {role_name} ===")
            print(content.strip())
        print("\n" + "=" * 40)
        print("=== 最终 Prompt ===")
    else:
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

