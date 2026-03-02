# 视频生成 Prompt 系统设计（V3：多角色协作）

> 在 V2 基础上引入 **Skill 多角色协作**：同一 Skill 内配置多个角色，按序参与生成，通过角色互动产出最终 Prompt。对应实现见 `system-detail-codesign.md` 第 3.5 节及目录结构。

## 1. 设计目标（V3 增量）

- 在 Phase 1 MVP 主链路不变的前提下，支持 **按 Skill 配置多角色**
- 多角色按 **order 顺序** 依次调用 LLM，每角色可见「用户意图 + 前序所有角色输出」
- 最后一名的输出作为 **最终 Prompt**；若无角色配置则退化为 V2 单轮生成
- 程序可 **指定 Skill**（如 `SKILL_NAME=seedance2`），并 **输出各角色结果** 便于确认与调试

## 2. 核心原则

- **与 V2 兼容**：无 `roles.yaml` 或解析失败时，仍走单次 `generate_prompt`，行为与 V2 一致
- **配置驱动**：角色定义完全在 Skill 的 `roles.yaml` 中，无需改代码即可增删改角色
- **可观测**：运行时可打印已加载角色列表、各角色输出、最终 Prompt，便于确认与排错

## 3. V3 范围

### 包含

- Skill 内 **多角色配置**：`roles.yaml`（id / name / order / system_prompt）
- **角色加载器**：从 `src/skills/{skill_name}/roles.yaml` 加载并按 order 排序
- **多角色生成流水线**：PromptGenerator 在存在角色时按序调用 `client.chat(role.system_prompt, user_content)`，user_content = 意图 + 前序输出
- **LLM 插件扩展**：`chat(system_prompt, user_content)` 单轮对话，供流水线使用
- **运行时可配置**：环境变量 `SKILL_NAME` 指定当前 Skill，默认 `seedance2`
- **输出约定**：`RunResult.role_outputs: [(role_name, content), ...]`，main 可打印各角色输出与最终 Prompt

### 不包含（仍按 V2）

- PageIndex 离线版、多模态输入、多 Skill 路由等仍属后续 Phase

## 4. 处理流程（V3 多角色）

```text
用户输入
  -> Layer 1 IntentionParser（同 V2）
  -> 若 skill 有 roles：
       -> 按 order 对每个 role：
            user_content = 意图 JSON + 前序各角色输出
            role_output = client.chat(role.system_prompt, user_content)
            记录 (role.name, role_output)
       -> 最终 Prompt = 最后一名角色的输出
  -> 否则：单轮 client.generate_prompt(意图)（同 V2）
  -> Layer 3 PhysicsValidator（同 V2）
  -> 输出 (prompt_text, negative_prompt, validation_issues, role_outputs)
```

## 5. 目录与接口映射（V3 增量）

| 项目 | 说明 |
|------|------|
| `src/skills/{skill}/roles.yaml` | 多角色定义（如 seedance2 的导演 / 摄影 / 成稿） |
| `src/skills/role_loader.py` | `load_skill_roles(skill_name)`，返回按 order 排序的 role 列表 |
| `src/llm_plugins/kimi_client.py` | 新增 `chat(system_prompt, user_content) -> str` |
| `src/core/prompt_generator.py` | 支持 `skill_name`，有 roles 时走 `_generate_with_roles`，返回 `PromptResult.role_outputs` |
| `src/core/orchestrator.py` | `Orchestrator(skill_name)`，将 `role_outputs` 传入 `RunResult` |
| `src/main.py` | 读取 `SKILL_NAME`，启动时打印已加载角色，结束时打印各角色输出与最终 Prompt |

## 6. 输出约定（V3）

- `prompt_text` / `negative_prompt` / `validation_issues`：与 V2 一致
- **role_outputs**：`list[(role_name, content)]`，多角色时有值，单轮时为空列表
- 主入口在存在 `role_outputs` 时，可先打印「已加载 N 个角色」、逐条「Role i: name」+ 内容，再打印「最终 Prompt」

## 7. 与 V2 的衔接

- **文档**：V2 描述 Phase 1 MVP 主链路；V3 描述 Phase 1 增强（多角色）。详细模块与 ADR 见 `system-detail-codesign.md`。
- **实现**：同一代码库，通过是否存在 `roles.yaml` 及 `role_loader` 是否返回非空列表自动选择多角色或单轮生成。

## 8. 后续路线图（不变）

- Phase 2：PageIndex 离线版、约束分层加载
- Phase 3：多模态、反馈闭环、多模型接入
