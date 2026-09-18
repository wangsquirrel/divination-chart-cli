"""Agent-friendly command-line entry point."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Sequence

from . import __version__
from .charts import generate_bazi, generate_liuyao


class CliError(ValueError):
    """A user-facing input error."""


def _bounded_int(name: str, minimum: int, maximum: int):
    def parse(value: str) -> int:
        try:
            parsed = int(value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"{name} 必须是整数") from exc
        if not minimum <= parsed <= maximum:
            raise argparse.ArgumentTypeError(
                f"{name} 必须在 {minimum} 到 {maximum} 之间"
            )
        return parsed

    return parse


def _add_date_fields(
    parser: argparse.ArgumentParser,
    *,
    prefix: str = "",
    required: bool = True,
) -> None:
    option_prefix = f"{prefix}-" if prefix else ""
    destination_prefix = f"{prefix}_" if prefix else ""
    parser.add_argument(
        f"--{option_prefix}year",
        dest=f"{destination_prefix}year",
        required=required,
        type=_bounded_int("年份", 1900, 2100),
        help="公历年份（1900-2100）",
    )
    parser.add_argument(
        f"--{option_prefix}month",
        dest=f"{destination_prefix}month",
        required=required,
        type=_bounded_int("月份", 1, 12),
        help="公历月份（1-12）",
    )
    parser.add_argument(
        f"--{option_prefix}day",
        dest=f"{destination_prefix}day",
        required=required,
        type=_bounded_int("日期", 1, 31),
        help="公历日期（1-31）",
    )
    parser.add_argument(
        f"--{option_prefix}hour",
        dest=f"{destination_prefix}hour",
        required=required,
        type=_bounded_int("小时", 0, 23),
        help="24 小时制小时（0-23）",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="divination-chart-cli",
        description="生成适合 agent 消费的六爻、八字排盘 JSON。",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="缩进输出 JSON；默认输出紧凑的单行 JSON",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    liuyao = subparsers.add_parser(
        "liuyao",
        aliases=["sixline"],
        help="六爻排盘",
        description="按公历年月日时分秒生成六爻 JSON；默认23:00换日，交节换月。",
    )
    _add_date_fields(liuyao)
    liuyao.add_argument(
        "--minute",
        type=_bounded_int("分钟", 0, 59),
        default=0,
        help="分钟（0-59），省略为 0；交节附近请提供准确时间",
    )
    liuyao.add_argument(
        "--second",
        type=_bounded_int("秒", 0, 59),
        default=0,
        help="秒（0-59），省略为 0",
    )
    liuyao.add_argument(
        "--zi-hour",
        choices=("default_next_day", "lunar_sect2_day_same"),
        default="default_next_day",
        help="日界：default_next_day=23点（默认）；lunar_sect2_day_same=0点日界，晚子时时柱按Tyme流派2",
    )
    casting = liuyao.add_mutually_exclusive_group()
    casting.add_argument(
        "--yaogua",
        nargs=6,
        metavar=("Y1", "Y2", "Y3", "Y4", "Y5", "Y6"),
        type=_bounded_int("摇卦值", 0, 3),
        help="旧版编码（0老阴/1少阳/2少阴/3老阳），不是传统字面枚数；初爻到上爻",
    )
    casting.add_argument(
        "--lines",
        nargs=6,
        metavar=("L1", "L2", "L3", "L4", "L5", "L6"),
        type=_bounded_int("爻值", 6, 9),
        help="标准爻值（6老阴/7少阳/8少阴/9老阳），初爻到上爻",
    )
    casting.add_argument(
        "--coin-counts",
        nargs=6,
        metavar=("C1", "C2", "C3", "C4", "C5", "C6"),
        type=_bounded_int("硬币枚数", 0, 3),
        help="传统铜钱法的 6 次枚数（0-3），须指定 --coin-side；均省略则自动摇卦",
    )
    liuyao.add_argument(
        "--coin-side",
        choices=("text", "back"),
        help="--coin-counts 数哪一面：text=字面，back=背面；不猜测现代硬币正反面",
    )
    liuyao.set_defaults(handler=_handle_liuyao)

    bazi = subparsers.add_parser(
        "bazi",
        help="八字排盘",
        description="按出生时间、性别和目标时间生成八字排盘 JSON。",
    )
    _add_date_fields(bazi, prefix="birth")
    bazi.add_argument(
        "--gender",
        required=True,
        type=_bounded_int("性别", 0, 1),
        help="0=女，1=男",
    )
    _add_date_fields(bazi, prefix="now", required=False)
    bazi.set_defaults(handler=_handle_bazi)
    return parser


def _handle_liuyao(args: argparse.Namespace) -> Any:
    return generate_liuyao(
        year=args.year,
        month=args.month,
        day=args.day,
        hour=args.hour,
        minute=args.minute,
        second=args.second,
        yaogua=args.yaogua,
        lines=args.lines,
        coin_counts=args.coin_counts,
        coin_side=args.coin_side,
        zi_hour=args.zi_hour,
    )


def _target_time(args: argparse.Namespace) -> datetime | None:
    values = [args.now_year, args.now_month, args.now_day, args.now_hour]
    if all(value is None for value in values):
        return None
    if any(value is None for value in values):
        raise CliError(
            "--now-year、--now-month、--now-day、--now-hour 必须同时提供"
        )
    return datetime(*values)


def _handle_bazi(args: argparse.Namespace) -> Any:
    return generate_bazi(
        birth_year=args.birth_year,
        birth_month=args.birth_month,
        birth_day=args.birth_day,
        birth_hour=args.birth_hour,
        gender=args.gender,
        target_time=_target_time(args),
    )


def _json_text(value: Any, *, pretty: bool) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json", exclude_none=True)
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except (CliError, ValueError) as exc:
        parser.error(str(exc))
    print(_json_text(result, pretty=args.pretty))
    return 0


if __name__ == "__main__":
    sys.exit(main())
