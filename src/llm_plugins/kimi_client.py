"""Kimi plugin placeholder implementation."""

import re
from typing import Any, Dict, List

from .base_client import BaseClient


class KimiClient(BaseClient):
    """Local mock implementation for Phase 1 MVP."""

    def parse_intention(self, text: str, image_paths: List[str]) -> Dict[str, Any]:
        _ = image_paths
        lens_match = re.search(r"(\d{2,3}mm)", text.lower())
        camera_hint = lens_match.group(1) if lens_match else ""
        style = self._infer_style(text)
        mood = self._infer_mood(text)
        lighting = self._infer_lighting(text)
        technical_hints: List[str] = []
        if "雨" in text or "rain" in text.lower():
            technical_hints.append("rain_particles")
        if "老电影" in text or "胶片" in text:
            technical_hints.append("film_grain")

        return {
            "style": style,
            "mood": mood,
            "lighting": lighting,
            "camera_hint": camera_hint,
            "needs_precise_params": bool(camera_hint),
            "technical_hints": technical_hints,
            "subject": "角色",
            "raw_input": text,
        }

    def generate_prompt(self, intention_payload: Dict[str, Any]) -> str:
        style = intention_payload.get("style", "cinematic_general")
        mood = intention_payload.get("mood", "neutral")
        lighting = intention_payload.get("lighting", "natural")
        camera_hint = intention_payload.get("camera_hint", "35mm")
        subject = intention_payload.get("subject", "角色")
        raw_input = intention_payload.get("raw_input", "")
        return (
            "[Subject & Movement]\n"
            f"{subject} 在场景中稳定移动，保持 {mood} 情绪。\n"
            "[Camera Work]\n"
            f"使用 {camera_hint} 镜头，连续运镜，画面风格 {style}。\n"
            "[Physics]\n"
            "动作遵循重力与惯性，避免不合理静止或穿模。\n"
            "[Lighting]\n"
            f"整体光影采用 {lighting}，保留层次和主体可见性。\n"
            "[Audio]\n"
            "环境音与动作同步，不出现突兀断裂。\n"
            "[Temporal]\n"
            "镜头从建立场景到主体特写自然过渡。\n"
            f"[User Intent]\n{raw_input}"
        )

    def validate_physics(self, prompt_text: str) -> Dict[str, Any]:
        issues: List[str] = []
        if "大风" in prompt_text and "静止" in prompt_text:
            issues.append("检测到矛盾：大风环境下主体静止。")
        if "水下" in prompt_text and "火焰" in prompt_text and "魔幻" not in prompt_text:
            issues.append("检测到潜在矛盾：水下火焰需明确魔幻设定。")
        return {"ok": len(issues) == 0, "issues": issues}

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        _ = image_path
        return {"summary": "image analysis not implemented in Phase 1"}

    def _infer_style(self, text: str) -> str:
        lowered = text.lower()
        if "赛博朋克" in text or "cyberpunk" in lowered:
            return "cyberpunk_cinematic"
        if "动漫" in text or "anime" in lowered:
            return "anime_stylized"
        if "老电影" in text or "胶片" in text:
            return "cinematic_retro"
        return "cinematic_general"

    def _infer_mood(self, text: str) -> str:
        if "怀旧" in text:
            return "nostalgic"
        if "紧张" in text:
            return "tense"
        if "浪漫" in text:
            return "romantic"
        return "neutral"

    def _infer_lighting(self, text: str) -> str:
        lowered = text.lower()
        if "霓虹" in text or "neon" in lowered:
            return "neon_noir"
        if "昏暗" in text or "low key" in lowered:
            return "low_key"
        return "natural"

