"""Entry-point for the plugin."""
from __future__ import annotations

from pluggy import PluginManager
from pytask import hookimpl
from pytask_latex import collect
from pytask_latex import config
from pytask_latex import execute


@hookimpl
def pytask_add_hooks(pm: PluginManager) -> None:
    """Register some plugins."""
    pm.register(collect)
    pm.register(config)
    pm.register(execute)
