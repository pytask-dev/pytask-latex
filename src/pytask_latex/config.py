"""Configure pytask."""
from __future__ import annotations

from typing import Any
from typing import Callable

from pytask import hookimpl


@hookimpl
def pytask_parse_config(config, config_from_file):
    """Register the latex marker in the configuration."""
    config["markers"]["latex"] = "Tasks which compile LaTeX documents."
    config["infer_latex_dependencies"] = _get_first_non_none_value(
        config_from_file,
        key="infer_latex_dependencies",
        callback=_convert_truthy_or_falsy_to_bool,
        default=True,
    )


def _convert_truthy_or_falsy_to_bool(x: bool | str | None) -> bool:
    """Convert truthy or falsy value in .ini to Python boolean."""
    if x in [True, "True", "true", "1"]:
        out = True
    elif x in [False, "False", "false", "0"]:
        out = False
    elif x in [None, "None", "none"]:
        out = None
    else:
        raise ValueError(
            f"Input {x!r} is neither truthy (True, true, 1) or falsy (False, false, 0)."
        )
    return out


def _get_first_non_none_value(
    *configs: dict[str, Any],
    key: str,
    default: Any | None = None,
    callback: Callable[..., Any] | None = None,
) -> Any:
    """Get the first non-None value for a key from a list of dictionaries.

    This function allows to prioritize information from many configurations by changing
    the order of the inputs while also providing a default.

    Examples
    --------
    >>> _get_first_non_none_value({"a": None}, {"a": 1}, key="a")
    1
    >>> _get_first_non_none_value({"a": None}, {"a": None}, key="a", default="default")
    'default'
    >>> _get_first_non_none_value({}, {}, key="a", default="default")
    'default'
    >>> _get_first_non_none_value({"a": None}, {"a": "b"}, key="a")
    'b'

    """
    callback = (lambda x: x) if callback is None else callback  # noqa: E731
    processed_values = (callback(config.get(key)) for config in configs)
    return next((value for value in processed_values if value is not None), default)
