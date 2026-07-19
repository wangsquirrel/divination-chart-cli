"""Chart generation independent from the command-line parser."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from divicast.birth_chart.birth import BirthChart
from divicast.birth_chart.output import to_standard_format as bazi_to_standard_format
from divicast.entities.misc import Gender
from divicast.sixline import DivinatorySymbol
from divicast.sixline.output import to_standard_format as liuyao_to_standard_format


def generate_liuyao(
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    yaogua: list[int] | None = None,
) -> Any:
    """Generate the same standard six-line output as divination-chart-mcp."""
    chart_time = datetime(year, month, day, hour)
    chart = DivinatorySymbol.create(cnts=yaogua, now=chart_time)
    return liuyao_to_standard_format(chart)


def generate_bazi(
    *,
    birth_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: int,
    gender: int = 0,
    target_time: datetime | None = None,
) -> Any:
    """Generate the same standard Bazi output as divination-chart-mcp."""
    birth_time = datetime(birth_year, birth_month, birth_day, birth_hour)
    chart = BirthChart.create(
        dt=birth_time,
        gender=Gender.Male if gender == 1 else Gender.Female,
    )
    return bazi_to_standard_format(chart, target_dt=target_time or datetime.now())
