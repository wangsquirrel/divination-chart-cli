from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

from divicast.sixline import DivinatorySymbol, to_standard_format
from divination_chart_cli.charts import generate_liuyao


@pytest.mark.parametrize(
    "cli_args, library_args",
    [
        (["--yaogua", "0", "1", "2", "3", "0", "1"], {"cnts": [0, 1, 2, 3, 0, 1]}),
        (
            ["--lines", "6", "7", "8", "9", "6", "7"],
            {"line_values": [6, 7, 8, 9, 6, 7]},
        ),
        (
            ["--coin-counts", "3", "2", "1", "0", "3", "2", "--coin-side", "text"],
            {"coin_counts": [3, 2, 1, 0, 3, 2], "coin_side": "text"},
        ),
        (
            ["--coin-counts", "0", "1", "2", "3", "0", "1", "--coin-side", "back"],
            {"coin_counts": [0, 1, 2, 3, 0, 1], "coin_side": "back"},
        ),
    ],
)
def test_cli_preserves_library_contract(cli_args, library_args):
    dt = datetime(2026, 2, 4, 4, 30, 12)
    expected = to_standard_format(
        DivinatorySymbol.create(now=dt, **library_args)
    ).model_dump(mode="json", exclude_none=True)
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "divination_chart_cli.cli",
            "liuyao",
            "--year",
            "2026",
            "--month",
            "2",
            "--day",
            "4",
            "--hour",
            "4",
            "--minute",
            "30",
            "--second",
            "12",
            *cli_args,
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, run.stderr
    assert run.stderr == ""
    assert json.loads(run.stdout) == expected


@pytest.mark.parametrize(
    "rule, day_pillar, boundary",
    [
        ("default_next_day", "甲午", "23:00"),
        ("lunar_sect2_day_same", "癸巳", "00:00"),
    ],
)
def test_adapter_uses_library_day_rule_and_metadata(rule, day_pillar, boundary):
    result = generate_liuyao(
        year=2026, month=9, day=16, hour=23, lines=[7] * 6, zi_hour=rule
    )
    output = result.model_dump(mode="json", exclude_none=True)
    assert output["bazi"].split()[2] == day_pillar
    assert output["calendar"]["day_boundary"] == boundary
    assert output["calendar"]["zi_hour"] == rule
    assert output["calendar"]["pillar_source"] == "time"
