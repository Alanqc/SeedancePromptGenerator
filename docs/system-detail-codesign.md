基于你的整合版本，以下是润色后的系统架构草案，主要调整了要点顺序并确保目录结构一致：

```markdown
# 视频生成 Prompt 系统架构草案（V2）
> 基于"轻 RAG、重 LLM"的混合推理架构，支持多模型与多模态样例

## 1. 设计哲学

### 1.1 核心原则
- **LLM 主导理解**：意图解析、风格映射、物理一致性检查必须由大模型直接处理，**禁止**依赖向量相似度匹配
- **LLM 中立性**：架构**不绑定任何特定大模型**。Kimi 2.5 作为默认参考实现，但系统可无缝切换至 GPT-5、Claude 4、Qwen 或本地模型
- **RAG 退居辅助**：RAG 仅作为"精确技术参数缓存层"，用于存储频繁更新的禁忌词、精确数值（焦距/色温/物理公式）和私有知识库
- **分层解耦**：将"创意理解"（LLM）与"技术约束"（RAG + Rule-based）分离，避免 RAG 误召回破坏创意意图
- **多模态原生**：系统原生支持图文交织的复杂样例（I2V、V2V 场景），而非仅处理纯文本 Prompt

### 1.2 为什么不用纯 RAG？
纯向量匹配存在**语义鸿沟**：
- 无法将"老电影的感觉"映射到"16mm 胶片颗粒 + 色偏 + 轻微抖动"
- 无法处理组合概念（"赛博朋克+雨夜+长焦"会召回不相关内容）
- 无法进行物理一致性检查（如验证"羽毛在强风中静止"是否矛盾）

### 1.3 模型可插拔策略
| 模型类型 | 适用场景 | 适配要点 |
|---------|---------|---------|
| **Kimi 2.5** | 长上下文理解、中文创意 | 默认示例，利用其 Agent Swarm 技术 |
| **Claude 4** | 物理逻辑验证、长思维链 | 需要 Extended Thinking 模式时 |
| **GPT-5** | 跨文化风格理解、多语言 | 国际化项目或需要广泛文化参考时 |
| **Qwen/本地模型** | 隐私敏感、离线环境 | 通过 base_client.py 统一接口接入 |

**关键设计**：所有模型差异通过 `llm-plugins` 层屏蔽，上层 Skill 与 Orchestrator 无感知。

---

## 2. 系统架构

### 2.1 三层处理架构

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
```

### 2.2 关键决策点

| 功能模块 | 技术选型 | 理由 |
|---------|---------|------|
| **意图解析** | LLM 直接推理 | 模糊语义理解必须依赖 LLM 的联想能力，RAG 无法处理"老电影的感觉"这类隐喻 |
| **风格映射** | LLM + Few-shot | 让 LLM 参考 3-5 个示例学习风格，比向量匹配更精准 |
| **技术参数** | RAG (Vector DB) | 镜头焦距、色温值等**精确数值**用 RAG 存储，避免 LLM hallucinate |
| **物理检查** | LLM 逻辑推理 | 必须验证"动量守恒"、"流体连续性"等物理逻辑，RAG 无法推理 |
| **禁忌词过滤** | RAG (频繁更新) | Seedance2 的禁用词列表每周更新，RAG 比模型微调成本低 |

---

## 3. 核心模块详解

### 3.1 LLM 插件层 (llm-plugins/)

**设计目标**: **模型无关的抽象层**，支持热插拔不同厂商模型

```yaml
llm-plugins/
├── base_client.py              # 抽象接口定义 (与具体模型无关)
│   ├── parse_intention()       # 意图解析 (支持多模态输入)
│   ├── generate_prompt()       # Prompt 生成
│   ├── validate_physics()      # 物理验证
│   └── analyze_image()         # 图像理解 (多模态必备)
│
├── kimi_client.py              # Kimi 2.5 实现 (默认示例)
│   ├── 支持 Agent Swarm 模式
│   └── 擅长长文本与中文语境
│
├── claude_client.py            # Claude 4 实现
│   ├── 擅长物理逻辑验证
│   └── 支持 Extended Thinking
│
├── openai_client.py            # GPT-5/o1 实现
│   └── 擅长跨文化风格理解
│
└── local_client.py             # 本地模型适配器 (vLLM/Ollama)
    └── 用于隐私敏感场景
```

**配置方式**:
```yaml
# config.yaml (位于 Private 层)
llm:
  default_provider: "kimi"      # 可切换: kimi / claude / openai / local
  fallback_provider: "claude"   # 失败时的降级选项
  
  providers:
    kimi:
      model: "kimi-2.5"
      api_key: "${KIMI_API_KEY}"
    claude:
      model: "claude-4-sonnet"
      api_key: "${ANTHROPIC_KEY}"
```

### 3.2 Skill 层 (skills/)

**设计原则**: Skill 不是"检索模板"，而是"结构化约束 + 多模态示例库"

```yaml
skills/
├── seedance2/                    # 针对 Seedance2 的 Skill 包
│   ├── templates/                # Jinja2 模板 (六层框架)
│   │   ├── cinematic_v1.j2       # 电影级风格模板
│   │   ├── anime_v1.j2           # 动漫风格模板
│   │   └── i2v_base.j2           # 图生视频专用模板
│   │
│   ├── constraints/              # 约束规则库 (分层叠加)
│   │   ├── global.yaml           # 全局硬约束 (物理/安全底线)
│   │   ├── cinematic_domain.yaml # 电影领域约束 (24fps/胶片感)
│   │   └── seedance2_model.yaml  # 模型特供避坑 (最新禁忌词/优化提示)
│   │
│   └── examples/                 # 多模态样例库 (替代 few_shots.json)
│       ├── index.yaml            # 样例索引与标签 (快速检索)
│       │
│       ├── example_001/          # 复杂多模态样例
│       │   ├── meta.yaml         # 元数据: 风格/场景/适用模型/版本历史
│       │   ├── inputs/           # 多模态输入集合
│       │   │   ├── ref_image_1.jpg    # 参考图1: 构图参考
│       │   │   ├── ref_image_2.png    # 参考图2: 色调参考
│       │   │   └── user_prompt.txt    # 原始用户描述
│       │   ├── output/           # 成功输出标准
│       │   │   ├── final_prompt.txt   # 生成的完整 Prompt
│       │   │   └── negative_prompt.txt
│       │   └── assets/           # 效果验证文件
│       │       └── result.mp4    # 生成的视频样例
│       │
│       ├── example_002/          # I2V (Image-to-Video) 专项样例
│       │   ├── meta.yaml         # tags: ["i2v", "cyberpunk", "rain"]
│       │   ├── inputs/
│       │   │   ├── source_image.jpg   # 起始帧
│       │   │   └── motion_desc.txt    # 运动描述
│       │   └── output/
│       │       └── video_prompt.txt
│       │
│       └── example_003/          # 多轮对话调优样例
│           ├── meta.yaml         # tags: ["refinement", "multi-turn"]
│           ├── inputs/
│           │   ├── turn_1.json        # 第一轮: 初始意图
│           │   ├── turn_2.json        # 第二轮: "光再亮一点"
│           │   └── turn_3.json        # 第三轮: "增加雨滴效果"
│           └── output/
│               └── final_optimized_prompt.txt
│
└── common/                       # 跨模型通用组件库
    ├── physics_rules.yaml        # 物理规则库 (如: "液体具有表面张力")
    └── camera_lexicon.yaml       # 镜头术语词典 (供 LLM 参考)
```

**样例索引结构 (index.yaml)**:
```yaml
# 用于快速检索，避免遍历目录
examples:
  - id: "ex_001"
    path: "example_001/"
    tags: ["cinematic", "cyberpunk", "neon", "rain"]
    modalities: ["text", "image"]      # 支持的输入模态
    complexity: "high"                  # 复杂度评级
    model_compatibility: ["seedance2", "sora"]  # 适用的视频模型
    
  - id: "ex_002"
    path: "example_002/"
    tags: ["i2v", "anime", "character"]
    modalities: ["image"]               # 纯图生视频样例
    complexity: "medium"
    
search_index:
  # 为支持传统检索，可构建轻量级向量索引
  # 但仅用于定位样例目录，不用于生成内容
  embedding_model: "text-embedding-3-small"
  dimensions: 1536
```

**样例元数据 (meta.yaml)**:
```yaml
id: "ex_001"
description: "赛博朋克雨夜 + 霓虹反射 + 长焦镜头"
author: "system"
created_at: "2025-02-10"

# 输入规格
input_spec:
  type: "multimodal"
  components:
    - type: "reference_image"
      count: 2
      description: "构图参考 + 色调参考"
    - type: "text"
      description: "用户原始描述"
      
# 成功标准 (用于评估新输出)
success_criteria:
  required_elements: ["neon_reflection", "rain_particles", "bokeh"]
  camera_work: "shallow_depth_of_field"
  physics_accuracy: "high"

# 版本控制
version: "1.2"
history:
  - "1.0": 初始创建
  - "1.1": 调整光影描述
  - "1.2": 增加物理约束
```

**约束加载策略**:
```python
# 伪代码: 动态约束组合 (非 RAG，基于规则匹配)
def load_constraints(intention: IntentionObject):
    constraints = []
    constraints.append(load_yaml("global.yaml"))  #  always load
    
    # 根据意图选择领域约束 (Rule-based，非向量相似)
    if intention.style in ["cinematic", "film"]:
        constraints.append(load_yaml("cinematic_domain.yaml"))
    
    # 根据目标模型选择特定约束
    if intention.target_model == "seedance2":
        constraints.append(load_yaml("seedance2_model.yaml"))
        
    return merge_constraints(constraints, priority="local_first")
```

### 3.3 技术参数缓存层 (tech-cache/) —— 唯一的 RAG 模块

**定位**: 仅存储**事实性、精确性、频繁更新**的数据

```yaml
tech-cache/
├── embeddings/               # 向量存储 (仅此类数据)
│   ├── lens_specs/          # 镜头规格: "50mm f/1.4 的景深范围"
│   ├── color_science/       # 色彩科学: "D65 色温对应 6500K"
│   └── banned_words/        # 禁用词: Seedance2 最新屏蔽列表
│
└── metadata/                # 索引信息
    ├── update_log.yaml      # 记录各缓存最后更新时间
    └── source_urls.yaml     # 数据来源 (官方文档链接)
```

**触发条件** (严格控制):
```python
def should_use_rag(intention: IntentionObject) -> bool:
    """仅在以下情况触发 RAG"""
    return (
        intention.needs_precise_parameter or  # 需要精确数值
        intention.contains_obscure_technical_term or  # 生僻术语
        intention.requires_latest_model_constraints  # 最新约束
    )
```

### 3.4 Private 层 (private/)

**用途**: 本地私有配置与私有知识

```yaml
private/                    # .gitignore 忽略
├── config.yaml            # API Keys (多模型配置)
├── custom_skills/         # 个人/团队私有 Skill
│   └── my_studio_style.yaml
└── local_rag/             # 私有 RAG 数据 (客户品牌规范等)
    └── client_brand_guidelines.md
```

---

## 4. 数据流示例

### 示例 1: 纯文本输入
**场景**: 用户输入"拍一个像《银翼杀手》那样的赛博朋克雨夜，霓虹灯反射在潮湿地面，用 85mm 镜头"

**Step 1**: 意图解析 (LLM 直接处理)
```json
{
  "style": "cyberpunk_cinematic",
  "reference": "Blade Runner",
  "lighting": "neon_noir",
  "camera": {
    "lens_hint": "85mm",
    "needs_precise_check": true
  },
  "mood": "dystopian_romantic"
}
```

**Step 2**: 混合处理
- **Path A (LLM)**: 风格理解、氛围描述、构图建议 → 直接生成
- **Path B (RAG)**: 查询 "85mm 镜头在 Full Frame 上的视角范围" (精确数值)

**Step 3**: Skill 组装
加载约束: `global.yaml` → `cinematic_domain.yaml` → `seedance2_model.yaml`

**Step 4**: 生成与验证
生成六层框架 Prompt，验证物理一致性（雨天+霓虹反射合理，85mm描述符合光学特性）

### 示例 2: 多模态输入
**场景**: 用户上传两张参考图（赛博朋克街景+人物特写），输入："让这个角色在雨中走，保持这种色调"

**Step 1**: 多模态意图解析
- 输入: 文本 + 2 张图片
- 分析: 构图、色调、人物姿态
- 输出: `{"style": "cyberpunk_cinematic", "reference_images": 2, ...}`

**Step 2**: 检索多模态样例
- 查询 `examples/index.yaml`，匹配 `cyberpunk` + `rain` + `i2v` 标签
- 定位 `example_002/`，加载 `source_image.jpg` + `motion_desc.txt` + `video_prompt.txt` 作为 Few-shot

**Step 3**: 生成 (带参考图)
LLM 同时接收用户参考图 + 样例（图文）+ Skill 约束，生成保持色调一致的 Prompt

**Step 4**: 验证与输出
- 物理验证：检查"雨中行走"动作合理性
- 输出：结构化 Prompt + 引用样例 ID `ex_002`（用于溯源）

---

## 5. 关键设计决策 (ADR)

### ADR-001: 为什么意图解析不用 RAG？
- **决策**: 意图解析必须直接使用 LLM 推理
- **理由**: 用户输入"像老电影的感觉"是隐喻，RAG 的向量匹配会字面化理解为"old movie"，而 LLM 能推理出"16mm 胶片、色偏、轻微抖动"等隐含要素
- **影响**: 增加 LLM Token 消耗，但大幅提升准确性

### ADR-002: RAG 仅用于技术参数缓存
- **决策**: RAG 退居"精确数值查询"角色
- **理由**: 
  - LLM 可能 hallucinate 镜头焦距 (如记错 50mm 在 APS-C 上的等效焦距)
  - 视频模型禁忌词列表需频繁更新，RAG 比模型微调成本低
- **边界**: 禁止用 RAG 做风格匹配或创意生成

### ADR-003: 约束分层与冲突解决
- **决策**: 采用 Global → Domain → Model 三层约束，Local Private 优先级最高
- **理由**: 
  - 避免"写实风格约束"破坏"二次元风格"表达
  - 允许用户在 Private 层覆盖系统默认规则 (如特定客户的品牌色要求)

### ADR-004: 多模型中立性 (Model Neutrality)
- **决策**: 架构不绑定特定大模型，通过 `llm-plugins` 层实现可插拔
- **理由**: 
  - 不同模型各有所长 (Kimi 长上下文/Claude 物理推理/GPT 跨文化)
  - 避免厂商锁定，支持私有化部署
- **实现**: 统一抽象接口 `base_client.py`，所有模型差异在下层屏蔽

### ADR-005: 多模态样例目录化 (Multi-modal Example Directory)
- **决策**: 废弃单文件 `few_shots.json`，采用目录结构存储复杂样例
- **理由**:
  - 单文件无法承载多图、多轮对话、视频附件等多模态数据
  - 独立目录支持版本控制 (`meta.yaml` 中的 `history`)
  - 便于团队协作 (Git 友好，避免 JSON 冲突)
- **结构**: `examples/{id}/` 包含 `inputs/`、`output/`、`assets/`、`meta.yaml`

### ADR-006: 样例索引与内容分离
- **决策**: 使用 `index.yaml` 建立轻量级索引，但内容存储在独立目录
- **理由**:
  - 快速检索无需遍历文件系统
  - 支持混合检索：标签匹配 (精确) + 向量相似 (模糊，仅用于定位)
  - 样例内容可包含大文件 (图片/视频) 而不拖慢索引

---

## 6. 目录结构总览

```text
video-prompt-system/
├── docs/                       # 架构文档与 ADR
├── src/
│   ├── core/
│   │   ├── orchestrator.py     # 主编排器 (实现三层架构)
│   │   ├── intention_parser.py # 意图解析 (LLM 调用)
│   │   ├── physics_validator.py # 物理验证 (LLM 调用)
│   │   └── example_retriever.py # 样例检索器 (查 index.yaml)
│   ├── llm_plugins/            # 模型无关层
│   │   ├── base_client.py      # 抽象接口 (多模态支持)
│   │   ├── kimi_client.py      # 默认实现
│   │   ├── claude_client.py    # 备选实现
│   │   └── openai_client.py    # 备选实现
│   ├── skills/
│   │   ├── seedance2/          # 特定模型 Skill
│   │   │   ├── templates/      # Jinja2 模板
│   │   │   ├── constraints/    # 分层约束
│   │   │   └── examples/       # 多模态样例库
│   │   │       ├── index.yaml  # 轻量索引
│   │   │       ├── example_001/# 复杂样例目录
│   │   │       ├── example_002/
│   │   │       └── ...
│   │   └── common/             # 跨模型通用组件
│   │       ├── physics_rules.yaml
│   │       └── camera_lexicon.yaml
│   └── tech_cache/             # 技术参数缓存 (唯一 RAG 区)
│       ├── indexer.py
│       └── retriever.py
├── private/                    # 本地私有 (gitignored)
│   ├── config.yaml             # API Keys & 模型配置
│   ├── custom_skills/
│   └── local_rag/
└── tests/
    ├── test_intention_parser.py
    └── test_physics_validation.py
```

---

## 7. 后续迭代路线图

### Phase 1 (MVP)
- 实现 Layer 1 (意图解析) + Layer 3 (生成)，**完全不用 RAG**，验证 LLM 直接推理的准确性
- 硬编码常见技术参数作为 Few-shot

### Phase 2 (增强)
- 引入 tech-cache (RAG)，仅用于：
  - 频繁更新的禁忌词列表
  - 精确镜头参数查询
- 实现约束分层加载与多模态样例库

### Phase 3 (高级)
- 引入反馈闭环 (Refinement Loop): 用户说"光再亮一点"，系统基于上一轮 Context 增量修改
- 多模态输入增强: 支持上传参考图，LLM 分析 + 可选 RAG 匹配相似风格参数

---

## 附录: Prompt 设计模板 (供 LLM 使用)

### 系统 Prompt (意图解析)
```
你是一位专业的视频导演意图分析师。将用户的模糊描述转化为结构化意图。

规则:
1. 必须理解隐喻 ("电影感" → 具体技术特征)
2. 识别是否需要精确技术参数 (如特定焦距、色温值)
3. 输出标准 JSON 格式，标记 needs_precise_check 字段
4. 禁止虚构具体数值，不确定时标记为 needs_precise_check=true

示例:
输入: "老电影的感觉，人物在昏暗房间"
输出: {"style": "cinematic_retro", "lighting": "low_key", "film_stock": "16mm", "needs_precise_check": false}
```

### 系统 Prompt (物理验证)
```
你是一位物理特效总监。检查视频 Prompt 中的物理逻辑错误。

检查清单:
- 流体动力学: 烟雾/水流是否符合连续性
- 光学: 镜头焦距与景深描述是否匹配
- 动力学: 破碎/碰撞是否符合动量守恒

发现矛盾时，指出错误并提供修正建议。
```

---

**总结**: 本架构的核心是**"让大模型做它擅长的事（理解、推理、创造），让 RAG 做它擅长的事（存储精确事实）"**，通过模型中立设计和多模态样例库，构建可演进的视频 Prompt 生成系统。
```