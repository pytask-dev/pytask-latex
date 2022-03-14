"""Parametrize tasks."""
from __future__ import annotations

from _pytask.config import hookimpl
from _pytask.mark import MARK_GEN as mark  # noqa: N811


@hookimpl
def pytask_parametrize_kwarg_to_marker(obj, kwargs):
    """Register kwargs as latex marker."""
    if callable(obj):
        if "latex" in kwargs:
            if isinstance(kwargs["latex"], dict):
                mark.latex(**kwargs.pop("latex"))(obj)
            else:
                mark.latex(kwargs.pop("latex"))(obj)
