---
name: divination-chart
description: Use divination-chart-cli to generate and interpret Chinese metaphysical charts, currently Liuyao (六爻) and Bazi (八字), from user-provided dates, times, gender, coin counts, or existing chart JSON. Use when asked to 排卦、起卦、摇卦、解卦、断卦、六爻占卜、排八字、看八字、命盘分析、流年大运, or interpret divination-chart-cli output. Route to the matching chart workflow and do not use for unrelated I Ching translation.
---

# 排盘与解盘

调用远端 `divination-chart-cli` 获得机器可读盘面，再加载对应盘种的参考文件循证解读。把传统术数表述为文化与反思性视角，不把推断包装成确定事实。

六爻新参数要求 CLI `0.2.0` 或更高版本，底层由 CLI 从 PyPI 安装 `divicast>=0.2.4,<0.3.0`，无需相邻源码目录。首次调用 CLI 或参数不识别时先检查同一调用来源的 `--version`／`--help`。已知远端升级但仍命中旧缓存时，可用 `uvx --refresh-package divination-chart-cli --from git+https://github.com/wangsquirrel/divination-chart-cli divination-chart-cli --version` 刷新一次；仍不兼容则报告具体版本问题，不能改用错误输入口径。

在 CLI 仓库根目录开发或验证当前修改时，用 `uv run divination-chart-cli ...` 或 `uvx --from . divination-chart-cli ...`；安装后的独立 Skill 使用下文的远端命令。不要把未推送的本地修改当成远端已经可用。

## 选择盘种

| 用户意图 | CLI 子命令 | 必须读取 |
| --- | --- | --- |
| 六爻、起卦、摇卦、问具体事情 | `liuyao` | [六爻字段](references/liuyao-chart-fields.md)和[六爻解读](references/liuyao-interpretation.md) |
| 八字、命盘、大运、流年、出生信息分析 | `bazi` | [八字字段](references/bazi-chart-fields.md)和[八字解读](references/bazi-interpretation.md) |

用户意图不明确时先确认盘种。用户要求的盘种尚未被 CLI 支持时，明确说明，不得用另一盘种冒充。新增 CLI 盘种时，在此表增加一行并提供独立字段与解读 reference。

## 通用流程

1. 收集所选盘种的必需输入，只追问缺失且无法安全推断的字段。
2. 使用已明确排盘口径的时间。六爻分秒和节气基准见下文；工具不转换时区、地点或真太阳时。
3. 运行对应命令，只把成功命令的 stdout 当作盘面 JSON。
4. 校验 JSON 具有该盘种 reference 所列的核心字段。失败时报告具体错误，不得补造盘面。
5. 先列盘面事实，再做传统规则推断，最后给出现实建议。
6. 默认不粘贴整份 JSON；用户要求原始盘面时再附上。

## 六爻工作流

提炼一个具体问题、对象和关注时段。使用《增删卜易》纳甲框架，先读取六爻字段和解读规则；问应期时另读[应期规则](references/liuyao-timing.md)，核实出处、术语或流派分歧时读[来源索引](references/liuyao-source-map.md)。书中不同作者的意见不能合并为无条件定律。

用户给出摇卦记录时，核对恰好六次、从初爻到上爻，并确认记录的含义：

- 已知阴阳动静或标准爻值：用 `--lines`，`6=老阴动、7=少阳静、8=少阴静、9=老阳动`。
- 传统铜钱字面／背面枚数：用 `--coin-counts`，并指定 `--coin-side text`／`back`。字面枚数 `0/1/2/3` 对应 `9/8/7/6`；不要猜现代硬币哪面是字面。
- 明确来自旧版 CLI 的 0–3 编码或 `yaogua`：才用 `--yaogua`，保留 `0老阴、1少阳、2少阴、3老阳`；这不是传统字面枚数。未知来源的 0–3 记录先核对，不能自动翻转。

三种输入互斥。同一问题默认复用已起的卦，不为获得喜欢的结论重新摇卦；这是本 Skill 的复现约定，不冒称经典禁止复占。未给记录但明确要求起卦时，省略三种输入参数，让工具模拟三枚硬币。

起卦时间用实际时钟或用户提供的原始时间，不能照抄示例日期。六爻支持分秒，默认 0；默认日界为 **23:00**，按节气交接换月、立春换年。用户明确采用晚子时日柱仍属当天的 Tyme 流派 2 时，传 `--zi-hour lunar_sect2_day_same`，0 点换日；不要用移动时间一小时来模拟另一日界。按输出 `calendar` 核对实际口径。节气基准为 UTC+08:00；非北京时间先明确口径，需要北京时间时先转换，再传无时区时间。工具不实现当地节气或真太阳时校正。仅知整点范围且可能跨交节时，保留两种时间可能性，不能补造分秒后给唯一月建。

```bash
uvx --from git+https://github.com/wangsquirrel/divination-chart-cli \
  divination-chart-cli liuyao \
  --year 2026 --month 7 --day 19 --hour 16 --minute 30 --second 0
```

若用户给出标准爻值，追加：

```bash
--lines 6 7 8 9 6 7
```

等价的传统字面计数是 `--coin-counts 3 2 1 0 3 2 --coin-side text`。此接口要求底层 `divicast>=0.2.4`。如果环境依赖未就绪或不认识新参数，应报告具体版本问题，不得降级为把字面枚数直接交给 `--yaogua`；不得补造盘面。

用户已提供完整六爻 JSON 时跳过命令，核对 `time`、可用的 `casting`／`calendar` 和阴阳动静；旧 JSON 没有新增字段时按六爻字段文件处理。只对 `origin.is_changed=true` 解释实际变爻。静爻可能暗动，须结合月日判定，但暗动不产生 `variant` 变爻。

六爻回答采用：

1. **排盘摘要**：问题、时间、起卦方式、本卦 → 变卦、世应、动爻。
2. **取用与证据**：列明用神候选、主用及理由；两现或不现时保留未排除的解释，列出 3-6 条带 JSON 字段路径的证据。
3. **综合解读**：按月日、空破、明暗动、原忌、动变的适用条件解释推动与阻碍，包含反证；推断要同时给字段依据和规则依据。
4. **结论与建议**：倾向性判断、现实行动和不确定性。

## 八字工作流

收集公历出生年月日时和性别。`--gender` 中 `0=女`、`1=男`。用户询问当前或指定时期时，提供完整的四个 `--now-*` 参数；省略时 CLI 使用执行时系统时间。

```bash
uvx --from git+https://github.com/wangsquirrel/divination-chart-cli \
  divination-chart-cli bazi \
  --birth-year 1990 --birth-month 8 --birth-day 15 --birth-hour 14 \
  --gender 1 \
  --now-year 2026 --now-month 7 --now-day 19 --now-hour 16
```

用户已提供完整八字 JSON 时跳过命令。先核对 `personal_info` 的出生时间和性别，再解读，防止输入错误导致整盘错位。把 `heuristic_analysis` 明确视为库的启发式计算结果，结合四柱原始字段说明，不能直接复述为定论。

八字回答采用：

1. **命盘摘要**：出生信息、四柱、日主和当前大运/目标流年。
2. **结构证据**：月令、通根、十神、五行、干支关系及对应 JSON 字段。
3. **主题解读**：围绕用户问题分析优势、张力、阶段变化和触发条件。
4. **建议与边界**：现实可执行建议、不同流派可能的分歧和不确定性。

## 解释边界

- 工具不提供《周易》卦辞、爻辞。不要伪造或凭记忆引用；用户明确要求经典文本时另行核实来源，并与纳甲六爻分析分开。
- 不得声称排盘能保证事件、性格、健康、婚姻或财富结果。
- 涉及医疗、法律、财务、安全等高风险决定时，只提供文化与反思性解读，并建议以专业意见和现实证据为准。
- 避免恐吓性断语、宿命论、歧视性性别推断和无法验证的精确承诺。
