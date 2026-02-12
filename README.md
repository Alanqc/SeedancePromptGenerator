# SkillForVideoGen

用于构建“通过大模型自动生成视频 Prompt”的项目骨架。

当前状态：

- 已完成文档版本化命名与详细设计文档整理
- 已实现 Phase 1 MVP（Layer 1 + Layer 3，无 RAG）
- 项目可运行、可编译，当前使用本地 mock 插件

建议先阅读：

- `docs/system-design-v1.md`
- `docs/system-design-v2.md`
- `docs/system-detail-codesign.md`

## 运行

```bash
python3 -m src.main
```

## 编译检查

```bash
python3 -m compileall src tests
```
