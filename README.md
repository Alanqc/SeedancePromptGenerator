# SkillForVideoGen

用于构建“通过大模型自动生成视频 Prompt”的项目骨架。

当前状态：

- 已完成文档版本化命名与详细设计文档整理
- 已实现 Phase 1 MVP（Layer 1 + Layer 3，无 PageIndex 离线版）
- 已接入 Kimi 真实 API（默认 `kimi-k2.5` + thinking 模式）
- 支持 **Skill 多角色协作**：在 skill 中配置 `roles.yaml`，多角色按序参与生成最终 Prompt（见 `src/skills/seedance2/roles.yaml`）

建议先阅读：

- `docs/system-design-v1.md`
- `docs/system-design-v2.md`
- `docs/system-design-v3.md`（多角色协作）
- `docs/system-detail-codesign.md`

## 依赖（多角色 skill 需要）

```bash
pip install -r requirements.txt   # 多角色需 PyYAML 解析 roles.yaml
```

## 运行

```bash
python3 -m src.main
# 或带输入
python3 -m src.main "拍一个赛博朋克雨夜场景，使用85mm镜头。"
# 指定 skill（默认 seedance2，会加载该 skill 的 roles.yaml 做多角色生成）
SKILL_NAME=seedance2 python3 -m src.main "你的描述"
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
- 可直接在 `private/config.yaml` 填入 key（`api_key: "你的Key"`）；可复制 `private-config.example.yaml` 到 `private/config.yaml`
- 默认使用 `https://api.moonshot.cn/v1`（可用 `KIMI_BASE_URL` 覆盖）
- 也兼容 `MOONSHOT_API_KEY` 环境变量名

## 编译检查

```bash
python3 -m compileall src tests
```
