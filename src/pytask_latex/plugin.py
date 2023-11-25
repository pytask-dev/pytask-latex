"""Entry-point for the plugin."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pytask import hookimpl
from pytask_latex import collect
from pytask_latex import config
from pytask_latex import execute

if TYPE_CHECKING:
    from pluggy import PluginManager


@hookimpl
def pytask_add_hooks(pm: PluginManager) -> None:
    """Register some plugins."""
    pm.register(collect)
    pm.register(config)
    pm.register(execute)
