"""从 skill 目录加载多角色配置 (roles.yaml)。"""

from pathlib import Path
from typing import Any, Dict, List

# 即 src/skills，其下为各 skill 目录如 seedance2
_SKILLS_ROOT = Path(__file__).resolve().parents[0]


def load_skill_roles(skill_name: str) -> List[Dict[str, Any]]:
    """
    加载指定 skill 的 roles 配置。
    返回按 order 排序的列表，每项含 id, name, order, system_prompt。
    若不存在或解析失败则返回空列表。
    """
    path = _SKILLS_ROOT / skill_name / "roles.yaml"
    if not path.exists():
        return []

    try:
        import yaml
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if not raw or not isinstance(raw, dict):
        return []

    roles = raw.get("roles")
    if not isinstance(roles, list):
        return []

    result: List[Dict[str, Any]] = []
    for r in roles:
        if not isinstance(r, dict):
            continue
        order = r.get("order")
        if order is None:
            continue
        system_prompt = r.get("system_prompt") or r.get("system_prompt_text") or ""
        if isinstance(system_prompt, str):
            system_prompt = system_prompt.strip()
        else:
            system_prompt = ""
        result.append({
            "id": str(r.get("id", "")),
            "name": str(r.get("name", "")),
            "order": int(order) if isinstance(order, (int, float)) else 0,
            "system_prompt": system_prompt,
        })

    result.sort(key=lambda x: x["order"])
    return result
