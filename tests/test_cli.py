from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from divination_chart_cli import cli


LIUYAO_ARGS = [
    "liuyao",
    "--year",
    "2024",
    "--month",
    "1",
    "--day",
    "1",
    "--hour",
    "12",
    "--yaogua",
    "0",
    "1",
    "2",
    "3",
    "0",
    "1",
]


def test_liuyao_writes_only_json_to_stdout(monkeypatch, capsys):
    monkeypatch.setattr(cli, "generate_liuyao", lambda **kwargs: {"盘": kwargs})

    assert cli.main(LIUYAO_ARGS) == 0

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert output["盘"]["yaogua"] == [0, 1, 2, 3, 0, 1]
    assert captured.err == ""


def test_bazi_accepts_midnight_target_time(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "generate_bazi",
        lambda **kwargs: {"target": kwargs["target_time"].isoformat()},
    )

    cli.main(
        [
            "bazi",
            "--birth-year",
            "1990",
            "--birth-month",
            "8",
            "--birth-day",
            "15",
            "--birth-hour",
            "14",
            "--gender",
            "1",
            "--now-year",
            "2026",
            "--now-month",
            "7",
            "--now-day",
            "19",
            "--now-hour",
            "0",
        ]
    )

    assert json.loads(capsys.readouterr().out)["target"] == "2026-07-19T00:00:00"


def test_bazi_rejects_partial_target_time():
    with pytest.raises(SystemExit) as error:
        cli.main(
            [
                "bazi",
                "--birth-year",
                "1990",
                "--birth-month",
                "8",
                "--birth-day",
                "15",
                "--birth-hour",
                "14",
                "--gender",
                "1",
                "--now-year",
                "2026",
            ]
        )

    assert error.value.code == 2


def test_invalid_calendar_date_is_reported_as_usage_error():
    with pytest.raises(SystemExit) as error:
        cli.main(
            [
                "liuyao",
                "--year",
                "2024",
                "--month",
                "2",
                "--day",
                "31",
                "--hour",
                "12",
            ]
        )

    assert error.value.code == 2


def test_liuyao_help_documents_explicit_input_protocols(capsys):
    with pytest.raises(SystemExit) as error:
        cli.main(["liuyao", "--help"])

    assert error.value.code == 0
    help_text = capsys.readouterr().out
    assert all(
        option in help_text
        for option in (
            "--lines",
            "--coin-counts",
            "--coin-side",
            "--minute",
            "--second",
        )
    )


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "divination_chart_cli.cli", *args],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def test_real_cli_version_matches_project_release():
    project_file = Path(__file__).resolve().parents[1] / "pyproject.toml"
    expected = tomllib.loads(project_file.read_text(encoding="utf-8"))["project"][
        "version"
    ]
    result = run_cli("--version")
    assert result.returncode == 0
    assert result.stdout.strip() == expected
    assert result.stderr == ""


DATE_ARGS = ["--year", "2026", "--month", "2", "--day", "4", "--hour", "4"]


@pytest.mark.parametrize("command", ["liuyao", "sixline"])
def test_real_cli_precise_coin_cast_is_one_json_document(command):
    result = run_cli(
        command,
        *DATE_ARGS,
        "--minute",
        "30",
        "--second",
        "12",
        "--coin-counts",
        *(["3"] * 6),
        "--coin-side",
        "text",
    )
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert result.stderr == ""
    assert len(result.stdout.splitlines()) == 1
    assert (output["benguaming"], output["bianguaming"]) == ("坤", "乾")
    assert output["time"] == "2026-02-04 04:30:12"
    assert output["yuejian"] == "寅"
    assert output["line_values"] == [6] * 6


def test_real_legacy_and_pretty_commands_preserve_chart():
    compact = run_cli(*LIUYAO_ARGS)
    pretty = run_cli("--pretty", *LIUYAO_ARGS)
    assert compact.returncode == pretty.returncode == 0
    assert compact.stderr == pretty.stderr == ""
    assert json.loads(compact.stdout) == json.loads(pretty.stdout)
    assert json.loads(compact.stdout)["benguaming"] == "未济"


@pytest.mark.parametrize(
    "extra",
    [
        ["--minute", "60"],
        ["--second", "-1"],
        ["--zi-hour", "invalid"],
        ["--coin-counts", *(["3"] * 6)],
        ["--coin-side", "text"],
        ["--coin-counts", *(["3"] * 6), "--coin-side", "heads"],
        ["--lines", *(["6"] * 5)],
        ["--lines", *(["10"] * 6)],
        ["--lines", *(["6"] * 6), "--yaogua", *(["0"] * 6)],
        ["--coin-counts", *(["0"] * 6), "--coin-side", "back", "--lines", *(["6"] * 6)],
    ],
)
def test_real_cli_rejects_ambiguous_or_invalid_inputs_without_stdout(extra):
    result = run_cli("liuyao", *DATE_ARGS, *extra)
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    "rule, expected_day",
    [
        ("default_next_day", "甲午"),
        ("lunar_sect2_day_same", "癸巳"),
    ],
)
def test_real_cli_explicit_day_boundary(rule, expected_day):
    result = run_cli(
        "liuyao",
        "--year",
        "2026",
        "--month",
        "9",
        "--day",
        "16",
        "--hour",
        "23",
        "--zi-hour",
        rule,
        "--lines",
        *(["7"] * 6),
    )
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["bazi"].split()[2] == expected_day
    assert output["calendar"]["zi_hour"] == rule
