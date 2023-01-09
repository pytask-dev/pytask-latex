"""Configure pytask."""
from __future__ import annotations

from typing import Any

from pytask import hookimpl


@hookimpl
def pytask_parse_config(config: dict[str, Any]) -> None:
    """Register the latex marker in the configuration."""
    config["markers"]["latex"] = "Tasks which compile LaTeX documents."
    config["infer_latex_dependencies"] = config.get("infer_latex_dependencies", True)
