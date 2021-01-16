"""Parametrize tasks."""
from _pytask.config import hookimpl
from _pytask.mark import MARK_GEN as mark  # noqa: N811


@hookimpl
def pytask_parametrize_kwarg_to_marker(obj, kwargs):
    """Register kwargs as latex marker."""
    if callable(obj):
        if "latex" in kwargs:
            mark.latex(kwargs.pop("latex"))(obj)
