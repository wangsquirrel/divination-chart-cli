# divination-chart-cli

基于 [wangsquirrel/divicast](https://github.com/wangsquirrel/divicast) 的
agent-friendly 排盘命令行程序。它把 `divination-chart-mcp` 的六爻、八字能力转换为
一次执行、一次 JSON 输出的 CLI。

## 设计约定

- 成功时 stdout 只包含一个 UTF-8 JSON 文档，不混入日志。
- 默认输出单行紧凑 JSON，适合 agent 或脚本读取。
- 参数错误写入 stderr，并返回非零退出码。
- 时间是已归一化的本地 `naive datetime`；程序不转换时区、地点或真太阳时。

## 通过 uvx 使用

在本地仓库运行：

```bash
uvx --from . divination-chart-cli liuyao \
  --year 2024 --month 1 --day 1 --hour 12 \
  --yaogua 0 1 2 3 0 1
```

发布到 GitHub 后可直接运行：

```bash
uvx --from git+https://github.com/<owner>/divination-chart-cli divination-chart-cli liuyao \
  --year 2024 --month 1 --day 1 --hour 12 \
  --yaogua 0 1 2 3 0 1
```

`--yaogua` 的顺序是初爻到上爻，每项为硬币背面数 `0-3`。省略该参数时会自动摇卦。

八字排盘：

```bash
uvx --from . divination-chart-cli bazi \
  --birth-year 1990 --birth-month 8 --birth-day 15 --birth-hour 14 \
  --gender 1 \
  --now-year 2026 --now-month 7 --now-day 19 --now-hour 16
```

`--gender` 中 `0` 表示女性，`1` 表示男性。四个 `--now-*` 参数必须全部提供或全部
省略；省略时使用程序执行时的系统时间。需要便于人阅读的格式时，可把全局参数
`--pretty` 放在子命令之前：

```bash
uvx --from . divination-chart-cli --pretty bazi ...
```

完整参数：

```bash
uvx --from . divination-chart-cli --help
uvx --from . divination-chart-cli liuyao --help
uvx --from . divination-chart-cli bazi --help
```

六爻子命令也提供别名 `sixline`。

## 开发

```bash
uv sync --dev
uv run pytest
```
