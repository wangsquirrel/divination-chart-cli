# 测试分工

- `test_cli.py`：真实 CLI 进程、标准输出与错误通道、退出码、互斥参数、别名、pretty 及日界选项。
- `test_liuyao.py`：同样输入经 CLI 得到的 JSON 必须等于底层统一输出；检查参数和日界传递。
- `skill_cases/liuyao.md`：六爻 Skill 的人工／独立模型场景验收，不是 pytest 文案匹配测试。

排盘算法的独立基准在 `divicast` 仓库的 `tests/test_sixline_contract.py`、
`tests/fixtures/sixline_reference.json` 和 `sixline_reference.md` 维护。
它们覆盖 64 卦归宫世应、纳甲、伏神、4096 种动静组合、六神旬空、交节与子时，
以及底层输入校验、来源记录、全局历法配置隔离和 Schema。本仓库使用 PyPI 依赖运行
`uv run pytest`，不要求相邻 checkout。升级底层时需核对其版本对应的回归结果，再运行
这里的接口测试；不在两个仓库复制维护同一套固定表。
