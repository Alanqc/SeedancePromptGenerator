"""Prompt generation for Phase 1 MVP；支持 skill 多角色协作生成。"""

import json
from dataclasses import dataclass, field
from typing import List, Tuple

from .intention_parser import Intention
from ..llm_plugins.kimi_client import KimiClient
from ..skills.role_loader import load_skill_roles


@dataclass
class PromptResult:
    """Prompt payload produced by layer 3."""

    prompt_text: str
    negative_prompt: str
    role_outputs: List[Tuple[str, str]] = field(default_factory=list)  # (role_name, content)


def _intention_to_user_context(intention: Intention) -> str:
    """把意图转成给角色的统一上下文文本。"""
    payload = {
        "style": intention.style,
        "mood": intention.mood,
        "lighting": intention.lighting,
        "camera_hint": intention.camera_hint or "35mm",
        "subject": intention.subject,
        "raw_input": intention.raw_input,
    }
    return json.dumps(payload, ensure_ascii=False)


class PromptGenerator:
    """Generate prompt text；若 skill 配置了 roles 则多角色按序互动生成。"""

    def __init__(self, skill_name: str = "seedance2") -> None:
        self.client = KimiClient()
        self.skill_name = skill_name
        self._roles: List[dict] = load_skill_roles(skill_name)

    def generate(self, intention: Intention) -> PromptResult:
        role_outputs: List[Tuple[str, str]] = []
        if self._roles:
            prompt_text, role_outputs = self._generate_with_roles(intention)
        else:
            payload = {
                "style": intention.style,
                "mood": intention.mood,
                "lighting": intention.lighting,
                "camera_hint": intention.camera_hint or "35mm",
                "subject": intention.subject,
                "raw_input": intention.raw_input,
            }
            prompt_text = self.client.generate_prompt(payload)

        negative_prompt = (
            "low quality, blurry, inconsistent lighting, broken anatomy, "
            "object flicker, frame jitter, overexposed"
        )
        return PromptResult(
            prompt_text=prompt_text,
            negative_prompt=negative_prompt,
            role_outputs=role_outputs,
        )

    def _generate_with_roles(self, intention: Intention) -> Tuple[str, List[Tuple[str, str]]]:
        """多角色按 order 依次参与：每轮传入「意图 + 前面所有角色输出」。返回 (最终 Prompt, [(role_name, content), ...])。"""
        base_context = _intention_to_user_context(intention)
        transcript: List[str] = []
        role_outputs: List[Tuple[str, str]] = []

        for role in self._roles:
            system_prompt = role.get("system_prompt", "").strip()
            name = role.get("name") or role.get("id") or "unknown"
            if not system_prompt:
                continue
            parts = [f"【用户意图】\n{base_context}"]
            for i, out in enumerate(transcript, 1):
                parts.append(f"【前序角色输出 {i}】\n{out}")
            user_content = "\n\n".join(parts)
            out_text = self.client.chat(system_prompt, user_content)
            transcript.append(out_text)
            role_outputs.append((name, out_text))

        final = transcript[-1].strip() if transcript else ""
        return final, role_outputs

