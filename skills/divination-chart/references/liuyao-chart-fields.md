# 六爻 JSON 字段

## 顶层字段

| 字段 | 含义 | 解读用途 |
| --- | --- | --- |
| `yaogua` | 初爻到上爻的旧版 divicast 编码 0–3 | 保持历史兼容，不能当传统字面枚数 |
| `line_values` | 初爻到上爻的标准爻值 6–9 | 优先复核阴阳动静 |
| `casting` | 原始输入口径与数值 | 分清字面、背面、旧编码与随机起卦 |
| `calendar` | 时间、节气基准及年/月/日界 | 复核交节和子时口径 |
| `time` | 实际传入的无时区时间，保留分秒 | 确认原始时间，23 点民用日期不改写 |
| `bazi` | 起卦时间四柱 | 时间背景 |
| `yuejian` | 月柱地支 | 月令、季节性强弱的主要依据 |
| `richen` | 日柱地支 | 当日生克冲合的主要依据 |
| `kongwang` | 两个旬空地支拼接 | 判断暂时落空、延迟或力量受限 |
| `benguaming` | 本卦名 | 当前结构和大势 |
| `bianguaming` | 变卦名 | 动爻所指向的变化结构 |
| `guagong` | 本卦所属卦宫 | 六亲排布的参照 |
| `bengua_type` | 本卦的六合、六冲、游魂、归魂等类型 | 辅助判断聚散、往复 |
| `biangua_type` | 变卦的特殊类型 | 辅助判断变化后的结构 |
| `shensha` | 神煞与对应地支 | 次级象意，不作核心证据 |

`guashen`、`chuangzhang`、`xianggui` 是附加传统信息。除非问题和所用流派明确需要，否则不要让它们盖过用神、世应、月日与动爻。

## 爻字段

`yao_1` 是初爻（最下），依次到 `yao_6` 上爻（最上）。每爻包含：

- `liushen`：青龙、朱雀、勾陈、腾蛇、白虎或玄武。
- `origin`：本卦此爻。
- `variant`：变卦同一爻位。

`origin` 中：

- `relative`：六亲。
- `gan`、`zhi`、`wuxing`：纳甲干支和五行。
- `line`：`⚊` 为阳，`⚋` 为阴。
- `is_subject=true`：世爻。
- `is_object=true`：应爻。
- `is_changed=true`：动爻。
- `fushen`：伏神；不存在时字段被省略。

## 重要陷阱

- `variant` 在六个爻位上始终存在。只有对应 `origin.is_changed=true` 时，它才是需要解释的实际变爻。
- `yaogua` 始终是旧引擎编码：`0=老阴动、1=少阳静、2=少阴静、3=老阳动`。
  标准爻值等于编码加 6。传统字面计数须用 `--coin-counts ... --coin-side text`；
  对应标准爻值为 `9 - 字面枚数`。旧文档的“字面枚数”名称有误。
- JSON 给出排盘事实，不直接给出用神、旺衰、吉凶或应期；这些属于解释，需要明确证据和假设。
- `origin.is_changed` 只表示摇卦所得的明动；`false` 不排除日冲引起的暗动，
  但不能据此使用该静爻的 `variant`。无明动也不能直接等同于没有变化。

## 输入与时间元数据

`casting.input_format` 为 `legacy_yaogua`、`line_values`、`coin_counts` 或
`random_three_coins`。手动输入的原始六个值在 `casting.values`；硬币计数另有
`casting.coin_side=text|back`。随机起卦没有手动输入的 `values` 和 `coin_side`；
最终结果见 `line_values`，复现时用 `--lines`。

`calendar` 由底层依据本次计算规则生成：

| 字段 | 值 | 含义 |
| --- | --- | --- |
| `time_basis` | `caller_normalized_naive` | 调用方归一化，工具不转换时区或真太阳时 |
| `solar_terms` | `tyme_UTC+08:00` | 节气交接时刻用 tyme 的 UTC+08:00 基准 |
| `year_boundary` | `lichun` | 立春换年 |
| `month_boundary` | `jie` | 十二节换月；不是公历月初、农历初一或每个中气 |
| `day_boundary` | 默认 `23:00`；流派 2 为 `00:00` | 日柱、旬空与六神按所选日界计算 |
| `zi_hour` | `default_next_day` 或 `lunar_sect2_day_same` | 实际算法标识；流派 2 晚子时时柱沿用 Tyme 算法 |
| `pillar_source` | `time` 或 `provided` | 按时间推算，或底层调用者显式提供四柱 |

`pillar_source=provided` 时，节气、年/月/日界及 `zi_hour` 可省略，不能声称其四柱
一定由显示的 `time` 推算。CLI 新起卦使用 `time` 来源；用户带来的 JSON 可能是显式四柱。

旧 JSON 可以没有 `line_values`、`casting`、`calendar`，不要因此编造输入来源。
仅能由 `yaogua` 确认旧编码对应的阴阳动静，不能倒推用户实际数的是哪一面。
若来自本 CLI 的旧版，可说明其底层默认日界；其他工具的旧盘要另核时间口径。
若 `line_values`、`yaogua`、`origin.line`、`origin.is_changed` 不一致，先指出矛盾，
核对原始记录后再解读，不静默选择一个字段。
