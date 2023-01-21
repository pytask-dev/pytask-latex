"""Parametrize tasks."""
from __future__ import annotations

from typing import Any

import pytask
from pytask import hookimpl


@hookimpl
def pytask_parametrize_kwarg_to_marker(obj: Any, kwargs: dict[str, Any]) -> None:
    """Register kwargs as latex marker."""
    if callable(obj) and "latex" in kwargs:  # noqa: PLR2004
        pytask.mark.latex(**kwargs.pop("latex"))(obj)
