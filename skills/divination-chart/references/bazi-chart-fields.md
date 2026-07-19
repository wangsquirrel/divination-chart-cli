# 八字 JSON 字段

## 顶层结构

| 字段 | 含义 | 解读用途 |
| --- | --- | --- |
| `personal_info` | 公历/农历出生、性别、生肖、星座、节气 | 首先复核输入和历法结果 |
| `natal_chart` | 日主、四柱、命宫等静态命盘 | 命局原始事实 |
| `luck_cycles` | 起运时间、顺逆行、大运及流年 | 阶段性背景 |
| `target_flow` | 指定时间的流年、流月、流日、流时 | 回答当前或目标时期问题 |
| `heuristic_analysis` | 库生成的五行、旺衰、十神、喜忌、格局、关系分析 | 启发式辅助，不是最终结论 |

## 原局

`natal_chart.four_pillars` 包含 `year`、`month`、`day`、`hour`。每柱包括：

- `pillar`：干支。
- `heavenlyStem`：天干、五行、阴阳、以日主为参照的十神。
- `earthlyBranch`：地支、五行、阴阳和 `hiddenStems` 藏干。
- `nayin`、`xun`、`kongwang`、`shensha`。
- `forDayMastertwelveLifeStages`：相对日主的十二长生。
- `forPillarStemtwelveLifeStages`：本柱天干自坐十二长生。

核心入口：

- `natal_chart.day_master`、`day_master_element`、`day_master_yinyang`。
- `natal_chart.four_pillars.month`：月令与季节背景。
- 各支 `hiddenStems`：通根和十神的实际来源。
- `natal_chart.calc_rules`：库使用的计算口径；解释差异时引用。

## 大运与目标时间

- `luck_cycles.start_age`、`start_date`、`direction`：起运信息。
- `luck_cycles.major_cycles[]`：每步大运的年龄、年份、干支、十神和流年明细。
- `target_flow.target_datetime`：本次动态分析的目标时间。
- `target_flow.year_pillar` 至 `hour_pillar`：目标时点四层流运。
- `target_flow.flow_months[]`：该流年按节气划分的流月起点和干支。

选择当前大运时，同时核对 `age_range` 与 `year_range`，不要只按数组位置猜测。

## 启发式分析

- `heuristic_analysis.wuxing`：五行加权分数和月支五行。
- `heuristic_analysis.strength`：扶助/克泄耗分数、通根和日主强弱估计。
- `heuristic_analysis.ten_god`：十神及十神家族加权分数。
- `heuristic_analysis.favorability`：倾向补益/回避五行。
- `heuristic_analysis.geju`：候选格局和依据。
- `heuristic_analysis.relations.events`：干支合冲刑害破会等标准化事件。

这些字段的命名已经提示“heuristic”。引用时写成“库的启发式估计”，并回到四柱、月令、藏干和关系事件交叉检查。

## 重要陷阱

- 工具接收已经归一化的当地 naive datetime，不处理时区、出生地或真太阳时。
- `now-*` 决定 `target_flow`，不改变出生原局。
- 性别影响大运顺逆等计算，解盘前必须核对。
- 星座、生肖、纳音、神煞是附加信息，不应盖过月令、日主、十神和干支结构。
- 不同八字流派对身强弱、格局、喜忌和早晚子时可能有不同口径；结合 `calc_rules` 说明边界。
