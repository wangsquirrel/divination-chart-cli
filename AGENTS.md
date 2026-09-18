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
- 六爻输入转换、校验、历法规则和标准输出由 `divicast>=0.2.4` 统一提供；
  `charts.py` 只转发参数，不重新定义 CastingInput、CalendarConvention 或输出子类。
- 默认使用 PyPI 的正式底层库，`uv.lock` 由 uv 生成并记录注册表分发文件；
  不提交 `../divicast` 等本机路径覆盖。联合开发仅在显式的临时调用或环境中覆盖依赖。
- CLI 版本只在 `pyproject.toml` 维护，运行时从分发元数据读取；新参数要求的
  最低 CLI 版本应同步写入 README 和 Skill。
- 新增或修改参数时同步更新 README 和测试。
- `skills/divination-chart/` 是随仓库发布的排盘、解盘 Skill；修改 CLI 参数、
  JSON 字段或新增盘种时，同步更新 Skill 路由与对应 references。
- 六爻 `--yaogua` 和 JSON `yaogua` 保留旧版 0–3 编码，不能重新解释为传统
  字面枚数；新记录用 `--lines`（6–9）或 `--coin-counts` 配 `--coin-side`。
- 六爻时间支持分秒，默认 UTC+08:00 节气、立春换年、交节换月、23:00 换日；
  `--zi-hour` 可选择底层的两种日界，实际元数据由底层生成。
- 排盘回归的固定表须附独立来源，不能直接把计算库当前输出当成正确答案；
  六爻解读默认《增删卜易》纳甲框架，新增规则注明适用条件和来源分歧。

## 常用命令

```bash
uv sync --dev --locked
uv run pytest
uv run divination-chart-cli --help
```

## 当前状态

- 已实现 `liuyao`（别名 `sixline`）与 `bazi`。
- CLI 当前版本为 `0.2.0`，使用 PyPI 的 `divicast 0.2.4`；支持无邻目录源码的独立安装。
- 已验证本地 `uvx --from .` 启动、真实排盘 JSON、测试与分发构建。
- 已提供可从 GitHub 安装的 `divination-chart` Skill，当前支持六爻和八字。
- 六爻已区分传统铜钱计数、标准爻值与旧编码，输出 `line_values`、`casting`、
  `calendar`；64 卦、4096 种组合及时间边界基准已迁入 divicast，CLI 保留协议集成测试。
- 六爻解读已补取用两现／伏藏、月日空破、暗动、原忌、变爻作用范围、进退墓绝、
  反伏与应期条件，并提供来源索引及独立场景验收用例。
