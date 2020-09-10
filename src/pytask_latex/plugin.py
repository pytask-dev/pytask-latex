"""Entry-point for the plugin."""
from _pytask.config import hookimpl
from pytask_latex import collect
from pytask_latex import config
from pytask_latex import execute
from pytask_latex import parametrize


@hookimpl
def pytask_add_hooks(pm):
    """Register some plugins."""
    pm.register(collect)
    pm.register(config)
    pm.register(execute)
    pm.register(parametrize)
