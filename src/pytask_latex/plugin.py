import pytask
from pytask_latex import collect
from pytask_latex import execute
from pytask_latex import parametrize


@pytask.hookimpl
def pytask_add_hooks(pm):
    pm.register(collect)
    pm.register(execute)
    pm.register(parametrize)
