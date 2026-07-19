# AGENTS.md

## 项目目标

将 `divination-chart-mcp` 的六爻、八字排盘能力封装成可通过 `uvx` 一次性调用的
JSON CLI，供 agent skill 和自动化脚本消费。

## 约定

- 修改阶段性完成后，择机更新本文件。
- stdout 是机器接口：成功时只输出一个 JSON 文档，不得混入日志或提示。
- 用户输入错误写入 stderr，并以非零状态码退出。
- CLI 参数尽量与 `divination-chart-mcp` 的输入字段保持一致。
- `src/divination_chart_cli/charts.py` 负责排盘，`src/divination_chart_cli/cli.py`
  只负责参数和序列化。
- 新增或修改参数时同步更新 README 和测试。

## 常用命令

```bash
uv sync --dev
uv run pytest
uv run divination-chart-cli --help
```

## 当前状态

- 已实现 `liuyao`（别名 `sixline`）与 `bazi`。
- 已验证本地 `uvx --from .` 启动、真实排盘 JSON、测试与分发构建。
