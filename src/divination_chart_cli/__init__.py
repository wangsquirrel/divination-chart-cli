"""Command-line interface for divination chart generation."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("divination-chart-cli")
except PackageNotFoundError:
    __version__ = "0+unknown"
