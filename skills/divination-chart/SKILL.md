---
name: divination-chart
description: Use divination-chart-cli to generate and interpret Chinese metaphysical charts, currently Liuyao (六爻) and Bazi (八字), from user-provided dates, times, gender, coin counts, or existing chart JSON. Use when asked to 排卦、起卦、摇卦、解卦、断卦、六爻占卜、排八字、看八字、命盘分析、流年大运, or interpret divination-chart-cli output. Route to the matching chart workflow and do not use for unrelated I Ching translation.
---

# 排盘与解盘

调用远端 `divination-chart-cli` 获得机器可读盘面，再加载对应盘种的参考文件循证解读。把传统术数表述为文化与反思性视角，不把推断包装成确定事实。

## 选择盘种

| 用户意图 | CLI 子命令 | 必须读取 |
| --- | --- | --- |
| 六爻、起卦、摇卦、问具体事情 | `liuyao` | [六爻字段](references/liuyao-chart-fields.md)和[六爻解读](references/liuyao-interpretation.md) |
| 八字、命盘、大运、流年、出生信息分析 | `bazi` | [八字字段](references/bazi-chart-fields.md)和[八字解读](references/bazi-interpretation.md) |

用户意图不明确时先确认盘种。用户要求的盘种尚未被 CLI 支持时，明确说明，不得用另一盘种冒充。新增 CLI 盘种时，在此表增加一行并提供独立字段与解读 reference。

## 通用流程

1. 收集所选盘种的必需输入，只追问缺失且无法安全推断的字段。
2. 使用用户已归一化的当地时间。工具不处理时区、地点或真太阳时；口径可能影响结果时先说明。
3. 运行对应命令，只把成功命令的 stdout 当作盘面 JSON。
4. 校验 JSON 具有该盘种 reference 所列的核心字段。失败时报告具体错误，不得补造盘面。
5. 先列盘面事实，再做传统规则推断，最后给出现实建议。
6. 默认不粘贴整份 JSON；用户要求原始盘面时再附上。

## 六爻工作流

提炼一个具体问题、对象和关注时段。用户给出摇卦值时，要求恰好 6 个 `0-3` 的整数，顺序为初爻到上爻，数值是每次三枚硬币的字面枚数：

- `0`：老阴动
- `1`：少阳静
- `2`：少阴静
- `3`：老阳动

同一问题只起一次卦。未给摇卦值但明确要求起卦时，省略 `--yaogua` 让工具自动摇卦。

```bash
uvx --from git+https://github.com/wangsquirrel/divination-chart-cli \
  divination-chart-cli liuyao \
  --year 2026 --month 7 --day 19 --hour 16
```

若用户给出摇卦值，追加：

```bash
--yaogua 0 1 2 3 0 1
```

用户已提供完整六爻 JSON 时跳过命令。只对 `origin.is_changed=true` 的爻解释变爻；不要把静爻的 `variant` 当成实际变化。

六爻回答采用：

1. **排盘摘要**：问题、时间、起卦方式、本卦 → 变卦、世应、动爻。
2. **取用与证据**：说明用神，列出 3-6 条带 JSON 字段路径的证据。
3. **综合解读**：态势、推动/阻碍、变化及条件。
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
