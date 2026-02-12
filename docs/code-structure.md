# 代码结构设计（仅目录骨架）

## 1. 顶层目录说明

```text
SkillForVideoGen/
├── .gitignore
├── README.md
├── docs/
│   ├── system-design-v1.md
│   ├── system-design-v2.md
│   ├── system-detail-codesign.md
│   └── code-structure.md
├── llm-plugins/
│   ├── README.md
│   └── kimi/
│       └── README.md
├── skills/
│   ├── README.md
│   └── seedance2/
│       ├── README.md
│       ├── templates/
│       │   └── README.md
│       ├── constraints/
│       │   └── README.md
│       └── examples/
│           └── README.md
└── Private/
    ├── README.local.md
    ├── kimi/
    │   └── README.local.md
    └── skills/
        └── README.local.md
```

---

## 2. 目录职责定义

### `docs/`

- 放系统设计、结构设计、后续接口规范文档
- 本次已经创建两份核心文档

### `llm-plugins/`

- 放所有大模型插件实现
- 当前预留 `kimi/` 作为默认插件
- 后续新增模型时按同层目录扩展，不影响 Skill 层

### `skills/`

- 放公开可版本化的 Skill 目录
- 本次提供 `seedance2` 样例结构：
  - `templates/`: Prompt 模板草案
  - `constraints/`: 规则与约束定义
  - `examples/`: 输入输出示例

### `Private/`

- 放本地私有资源（不上传）
- 建议内容：
  - `Private/kimi/`: API key、本地连接配置
  - `Private/skills/`: 个人私有 Skill 或调优规则

---

## 3. 命名与扩展约定

- LLM 插件目录建议使用厂商名：`kimi`、`openai`、`qwen`
- Skill 目录建议使用目标模型或业务场景名：`seedance2`
- 私有目录统一放 `Private/`，避免散落在项目其他位置
- 任何可复用规范先写到 `docs/`，再落地实现

---

## 4. 当前状态

- 已完成：目录骨架 + 设计文档
- 未开始：任何业务代码实现（符合“先设计后编码”目标）
