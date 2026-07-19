from __future__ import annotations

import json

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
