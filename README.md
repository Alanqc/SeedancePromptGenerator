# SkillForVideoGen

用于构建“通过大模型自动生成视频 Prompt”的项目骨架。

当前状态：

- 已完成文档版本化命名与详细设计文档整理
- 已实现 Phase 1 MVP（Layer 1 + Layer 3，无 RAG）
- 已接入 Kimi 真实 API（默认 `kimi-k2.5` + thinking 模式）

建议先阅读：

- `docs/system-design-v1.md`
- `docs/system-design-v2.md`
- `docs/system-detail-codesign.md`

## 运行

```bash
python3 -m src.main
```

## Kimi 配置

```bash
export KIMI_API_KEY="你的Key"
# 可选，默认就是 kimi-k2.5
export KIMI_MODEL="kimi-k2.5"
# 可选，默认就是 https://api.moonshot.cn/v1
export KIMI_BASE_URL="https://api.moonshot.cn/v1"
```

说明：

- `kimi-k2.5` 会自动携带 `thinking: {"type":"enabled"}`
- 可直接在 `private/config.yaml` 填入 key（`api_key: "你的Key"`）
- 默认使用 `https://api.moonshot.cn/v1`（可用 `KIMI_BASE_URL` 覆盖）
- 也兼容 `MOONSHOT_API_KEY` 环境变量名

## 编译检查

```bash
python3 -m compileall src tests
```
