# divination-chart-cli

基于 [wangsquirrel/divicast](https://github.com/wangsquirrel/divicast) 的
agent-friendly 排盘命令行程序。它把 `divination-chart-mcp` 的六爻、八字能力转换为
一次执行、一次 JSON 输出的 CLI。

CLI `0.2.0` 使用 PyPI 的 `divicast>=0.2.4,<0.3.0`；不需要相邻的底层库源码目录。

## 设计约定

- 成功时 stdout 只包含一个 UTF-8 JSON 文档，不混入日志。
- 默认输出单行紧凑 JSON，适合 agent 或脚本读取。
- 参数错误写入 stderr，并返回非零退出码。
- 时间是已归一化的本地 `naive datetime`；程序不转换时区、地点或真太阳时。

## 通过 uvx 使用

直接从 GitHub 运行：

```bash
uvx --from git+https://github.com/wangsquirrel/divination-chart-cli \
  divination-chart-cli liuyao \
  --year 2024 --month 1 --day 1 --hour 12 --minute 30 --second 0 \
  --lines 6 7 8 9 6 7
```

六爻输入均为**初爻到上爻**，以下三种方式互斥；全部省略时模拟三枚公平硬币摇卦。

| 参数 | 口径 |
| --- | --- |
| `--lines 6 7 8 9 6 7` | 推荐。标准爻值：6 老阴动、7 少阳静、8 少阴静、9 老阳动 |
| `--coin-counts 3 2 1 0 3 2 --coin-side text` | 传统铜钱的字面枚数；必须声明 `text`（字面）或 `back`（背面） |
| `--yaogua 0 1 2 3 0 1` | 兼容旧版 divicast 编码：0 老阴、1 少阳、2 少阴、3 老阳 |

表中三个示例表示同一盘。传统铜钱法按字面计 2、背面计 3 加总，所以字面枚数
`0/1/2/3` 分别对应爻值 `9/8/7/6`；背面枚数对应 `6/7/8/9`。
依据为《卜筮正宗》卷一“以钱代蓍法”。
[原文](https://www.shidianguji.com/book/AMNL0060/chapter/1ma05akk4w74j)
现代硬币需要先约定哪面对应字面，程序不会按“正面”“国徽面”猜测。

**旧版说明曾把 `--yaogua` 称为“字面枚数”，该名称与传统铜钱法相反。**
为复现已有盘面，旧参数和输出 `yaogua` 的数值含义保持不变；不要把新记录的
传统字面枚数直接传给它，也不要自动翻转历史 JSON。

六爻 JSON 保留原字段，并新增：

- `line_values`：统一的 6–9 爻值；不依赖输入方式。
- `casting`：原始输入方式、数值，以及适用时的硬币计数面。
- `calendar`：时间基准、节气基准、换年、换月和换日口径。

### 六爻时间口径

`--minute`、`--second` 均可选，省略为 0。旧命令仍按整点排盘；知道分秒时应传入，
尤其是交节附近。例如 `2026-02-04 04:00` 为丑月，`04:30` 已为寅月。
底层默认按**立春换年、十二节交接时刻换月、23:00 换日**计算；23 点仍原样显示民用日期，
日柱已属次日，旬空和六神随该日柱计算。
`--zi-hour default_next_day` 明确选择此默认值；`--zi-hour lunar_sect2_day_same` 则采用
Tyme 流派 2，晚子时日柱仍属当天、0 点换日，时柱沿用该流派算法。
实际口径由底层计算并写入 `calendar`，不读取或修改全局日界配置。

输入是调用方已归一化的无时区时间，CLI 不转换时区、地点或真太阳时。
tyme 的节气时刻以 UTC+08:00 为基准。北京时间可直接输入；其他地区的时间应先明确
采用北京时间还是当地排盘口径。若采用北京时间，应先转换完整时间再传入，不能只删除
时区信息；本工具不实现当地节气时刻或真太阳时校正。时间只精确到小时且可能跨交节时，
应分别检查可能的前后盘面，不能声称月建已经确定。

六爻 Skill 默认采用《增删卜易》纳甲规则框架；取用、暗动、动变、空破和应期的
条件与分歧见[解读规则](skills/divination-chart/references/liuyao-interpretation.md)
及[来源索引](skills/divination-chart/references/liuyao-source-map.md)。

八字排盘：

```bash
uvx --from git+https://github.com/wangsquirrel/divination-chart-cli \
  divination-chart-cli bazi \
  --birth-year 1990 --birth-month 8 --birth-day 15 --birth-hour 14 \
  --gender 1 \
  --now-year 2026 --now-month 7 --now-day 19 --now-hour 16
```

`--gender` 中 `0` 表示女性，`1` 表示男性。四个 `--now-*` 参数必须全部提供或全部
省略；省略时使用程序执行时的系统时间。需要便于人阅读的格式时，可把全局参数
`--pretty` 放在子命令之前：

```bash
uvx --from git+https://github.com/wangsquirrel/divination-chart-cli \
  divination-chart-cli --pretty bazi ...
```

完整参数：

```bash
uvx --from git+https://github.com/wangsquirrel/divination-chart-cli divination-chart-cli --help
uvx --from git+https://github.com/wangsquirrel/divination-chart-cli divination-chart-cli liuyao --help
uvx --from git+https://github.com/wangsquirrel/divination-chart-cli divination-chart-cli bazi --help
```

六爻子命令也提供别名 `sixline`。

新参数要求 CLI `0.2.0` 或更高版本。可用 `divination-chart-cli --version` 核对。
如果远端已更新而 `uvx` 仍命中旧缓存，可刷新 CLI 包后再检查：

```bash
uvx --refresh-package divination-chart-cli \
  --from git+https://github.com/wangsquirrel/divination-chart-cli \
  divination-chart-cli --version
```

## 安装排盘 Skill

仓库内的
[`divination-chart`](skills/divination-chart/SKILL.md)
Skill 会调用本 CLI 生成并解读六爻、八字盘面；后续盘种也会通过同一 Skill 扩展。

在 Codex 中使用内置安装器：

```text
$skill-installer install https://github.com/wangsquirrel/divination-chart-cli/tree/main/skills/divination-chart
```

也可以使用跨 Agent 的 `skills` CLI：

```bash
npx skills add wangsquirrel/divination-chart-cli --global --yes
```

安装后可这样调用：

```text
$divination-chart 我想问未来三个月换工作是否合适，请现在起一卦并解读。
$divination-chart 请按我的出生信息排八字，并分析当前大运和今年趋势。
```

手动安装时，只需把 `skills/divination-chart` 目录复制或链接到用户级
`~/.agents/skills/divination-chart`；无需克隆后长期保留整个仓库。

## 开发

当前 CLI 使用 PyPI 发布的底层库，`uv.lock` 记录已验证的 `divicast 0.2.4` 及其
分发文件哈希。克隆本仓库即可独立开发，不需要 `../divicast`：

```bash
uv sync --dev --locked
uv run pytest
uv run divination-chart-cli --version
```

从以前的同版本 editable 联调环境切换时，执行一次
`uv sync --dev --locked --reinstall-package divicast`，确保实际安装来源也切换到 PyPI。

验证当前源码的一次性调用：

```bash
uvx --from . divination-chart-cli liuyao \
  --year 2026 --month 2 --day 4 --hour 4 --minute 30 --lines 6 7 8 9 6 7
```

确需联合开发底层时，可临时使用 `uvx --with ../divicast --from . ...`，或在临时环境中
覆盖依赖；不要把本机路径写回默认依赖和锁文件。分发依赖始终指向正式版本。
修改本地源码不会自动更新远端 Git 安装来源，需另行提交和推送。

排盘算法基准已迁入 `divicast/tests/test_sixline_contract.py`，其中维护独立来源的
64 卦表、4096 种组合及历法边界。这里保留真实 CLI 进程、错误通道、参数互斥、
日界选择，以及 CLI 与底层标准 JSON 一致性的集成测试。分工见 [tests/README.md](tests/README.md)。
