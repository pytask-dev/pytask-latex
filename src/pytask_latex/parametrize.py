"""Parametrize tasks."""
from __future__ import annotations

import pytask
from pytask import hookimpl


@hookimpl
def pytask_parametrize_kwarg_to_marker(obj, kwargs):
    """Register kwargs as latex marker."""
    if callable(obj):
        if "latex" in kwargs:
            pytask.mark.latex(**kwargs.pop("latex"))(obj)
