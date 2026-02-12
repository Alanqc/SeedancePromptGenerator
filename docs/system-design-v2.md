# 视频生成 Prompt 系统架构草案（V2）

> 基于"轻 RAG、重 LLM"的混合推理架构，支持多模型与多模态样例。
> 本文件由 `docs/system-detail-codesign.md` 覆盖同步生成，作为正式架构基线。

## 1. 设计哲学

### 1.1 核心原则

- LLM 主导理解：意图解析、风格映射、物理一致性检查由大模型处理
- LLM 中立性：不绑定特定模型，Kimi 作为默认实现
- RAG 退居辅助：仅用于精确参数、禁忌词、频繁更新知识
- 分层解耦：创意理解与技术约束分层处理
- 多模态原生：支持文本、图片、视频帧等输入

### 1.2 模型可插拔

通过 `llm_plugins` 统一抽象屏蔽厂商差异，上层 `core` 与 `skills` 无感知。

---

## 2. 三层处理架构
```text
┌─────────────────────────────────────────────────────────────┐
│                     用户输入层 (Input)                       │
│         支持: 纯文本 / 参考图 / 视频帧 / 组合输入              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: 意图解析 (Intention Parser)                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  执行者: 可配置 LLM (默认 Kimi 2.5，可替换为 Claude/GPT)       │
│  输入: 支持多模态 (文本 + 参考图片列表)                        │
│  输出: 结构化意图 JSON                                       │
│  {                                                          │
│    "style": "cinematic_retro",     // 风格意图               │
│    "mood": "nostalgic",            // 情绪意图               │
│    "lighting": "low_key",          // 光影意图               │
│    "technical_hints": ["film_grain", "shallow_dof"],        │
│    "needs_precise_params": false   // 是否需要查 RAG         │
│  }                                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
┌──────────────────┐    ┌──────────────────────────┐
│  Path A: 纯 LLM   │    │  Path B: 混合增强 (可选)  │
│  直接生成         │    │  仅当需要精确参数时触发    │
│  (90% 场景)       │    │  (10% 场景)              │
└────────┬─────────┘    └───────────┬──────────────┘
         │                          │
         │    ┌─────────────────────┘
         │    │  RAG 查询条件:
         │    │  - 镜头焦距数值
         │    │  - 色温/光圈参数  
         │    │  - Seedance2 最新禁忌词
         │    │  - 私有品牌规范
         │    ▼
         │  ┌──────────────────────────┐
         │  │  技术参数缓存 (Vector DB) │
         │  │  - 查精确值: "50mm 在 APS-C │
         │  │    上的等效焦距"          │
         │  │  - 查禁忌: "Seedance2 2月 │
         │  │    更新禁用词列表"        │
         │  └───────────┬──────────────┘
         │              │
         └──────────────┴──────────────┐
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Skill 组装与约束应用 (Skill Assembler)              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  职责: 将意图 + 可选的技术参数 → 组装成完整 Prompt            │
│                                                              │
│  约束分层加载 (动态组合):                                     │
│  1. Global Constraints (全局): 物理底线、安全策略             │
│  2. Domain Constraints (领域): cinematic/anime/vlog         │
│  3. Model Constraints (模型): Seedance2/Sora 特定避坑        │
│                                                              │
│  冲突解决: 优先级权重机制 (Local Private > Model > Domain)   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 生成与验证 (Generation & Validation)               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  执行者: 可配置 LLM (必须 LLM 推理)                          │
│                                                              │
│  子步骤:                                                     │
│  1. Prompt 生成 (六层框架):                                   │
│     - Subject & Movement (主体动作)                          │
│     - Camera Work (镜头语言)                                 │
│     - Physics (物理动态: 惯性/黏度/张力)                     │
│     - Lighting (光影氛围)                                    │
│     - Audio (声音同步)                                       │
│     - Temporal (时间演变)                                    │
│                                                              │
│  2. 物理一致性验证 (Physics Audit):                          │
│     - 检查矛盾: "大风中羽毛静止" → 报错或自动修正            │
│     - 检查合理性: "水下火焰" → 提示添加"魔幻"标签            │
│                                                              │
│  3. Negative Prompt 生成                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     输出层 (Output)                          │
│  结构化 Prompt + 引用的样例 ID (用于溯源)                     │
└─────────────────────────────────────────────────────────────┘

---

## 3. 核心模块

### 3.1 LLM 插件层（`src/llm_plugins/`）

- `base_client.py`: 抽象接口
- `kimi_client.py`: 默认实现（后续可加 `claude/openai/local`）

### 3.2 Skill 层（`src/skills/`）

- `seedance2/templates/`: 模板
- `seedance2/constraints/`: 规则
- `seedance2/examples/`: 多模态样例
- `common/`: 跨模型通用词典与物理规则

### 3.3 技术参数缓存层（`src/tech_cache/`）

- 唯一 RAG 区域
- 只存储事实性与精确性数据

### 3.4 Private 层（`private/`）

- 本地私有配置、私有 Skill、本地私有知识库
- 默认不上传仓库（需 `.gitignore` 忽略）

---

## 4. ADR（关键架构决策）

- ADR-001：意图解析不用 RAG，使用 LLM 直接推理
- ADR-002：RAG 仅用于精确技术参数和高频更新约束
- ADR-003：约束分层，且支持 local private 覆盖
- ADR-004：多模型中立，通过插件层可插拔
- ADR-005：多模态样例目录化，替代单文件 few-shot
- ADR-006：样例索引与样例内容分离

---

## 5. 目录结构总览（实施基线）

```text
video-prompt-system/
├── docs/
│   ├── system-detail-codesign.md
│   └── system-newdesign-v2.md
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── orchestrator.py
│   │   ├── intention_parser.py
│   │   ├── physics_validator.py
│   │   └── example_retriever.py
│   ├── llm_plugins/
│   │   ├── base_client.py
│   │   └── kimi_client.py
│   ├── skills/
│   │   ├── seedance2/
│   │   │   ├── templates/
│   │   │   ├── constraints/
│   │   │   └── examples/
│   │   └── common/
│   └── tech_cache/
│       ├── indexer.py
│       └── retriever.py
├── private/
│   ├── config.yaml
│   ├── custom_skills/
│   └── local_rag/
└── tests/
    ├── test_intention_parser.py
    └── test_physics_validation.py
```

---

## 6. 本阶段落地范围

- 只建立“可编译、可运行”的基础骨架
- 不接入真实 API，不实现业务逻辑
- 所有模块提供 no-op 或占位返回，保证结构稳定
