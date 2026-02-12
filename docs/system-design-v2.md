# 视频生成 Prompt 系统设计（V2 精简版）

> 本文是 `system-detail-codesign.md` 的执行摘要，面向实现与协作。

## 1. 设计目标

- 用大模型将用户描述转换为结构化视频 Prompt
- 架构保持模型可插拔（默认 Kimi，后续可替换）
- Phase 1 先跑通主链路，不引入 RAG

## 2. 核心原则

- **重 LLM，轻检索**：创意理解与逻辑校验由 LLM 负责
- **模型中立**：通过插件层屏蔽模型差异
- **分层清晰**：输入解析、Prompt 生成、物理校验分离
- **渐进迭代**：先 MVP，可运行后再做增强

## 3. Phase 1（MVP）范围

### 包含

- Layer 1：意图解析（Intention Parser）
- Layer 3：Prompt 生成与物理一致性校验
- CLI 可运行入口：`python3 -m src.main`

### 不包含

- RAG/向量库检索
- 多模态图片理解
- 其他模型厂商接入（当前仅接入 Kimi）

## 4. 处理流程（MVP）

```text
用户输入
  -> Layer 1 IntentionParser
  -> Layer 3 PromptGenerator
  -> Layer 3 PhysicsValidator
  -> 输出 (prompt / negative prompt / warnings)
```

## 5. 目录映射（MVP 实现）

- `src/main.py`：命令行入口
- `src/core/orchestrator.py`：主编排器（串联 Layer 1 + Layer 3）
- `src/core/intention_parser.py`：意图解析
- `src/core/prompt_generator.py`：Prompt 生成
- `src/core/physics_validator.py`：物理校验
- `src/llm_plugins/base_client.py`：插件抽象接口
- `src/llm_plugins/kimi_client.py`：默认 Kimi 真实 API 实现

## 6. 输出约定

- `prompt_text`：按六层结构输出（主体、镜头、物理、光影、音频、时间）
- `negative_prompt`：基础负向约束
- `validation_issues`：物理一致性警告列表

## 7. 后续路线图

### Phase 2

- 引入 tech-cache（仅精确参数与禁忌词）
- 增加 Skill 约束分层加载（Global/Domain/Model）

### Phase 3

- 多模态输入（图像 + 文本）
- 反馈闭环（多轮 Prompt 精修）
- 插件能力增强（真实 Kimi/OpenAI/Claude 接入）
