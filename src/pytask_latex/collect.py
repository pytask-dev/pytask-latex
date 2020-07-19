import copy
import functools
import subprocess

import pytask
from pytask.mark import get_markers_from_task
from pytask.mark import has_marker
from pytask.nodes import PythonFunctionTask
from pytask.parametrize import _copy_func


def compile_latex_document(depends_on, produces, args):
    if depends_on.stem != produces.stem:
        args.append(f"--jobname={produces.stem}")

    subprocess.run(
        ["latexmk"]
        + args
        + [
            f"--output-directory={produces.parent.as_posix()}",
            f"{depends_on.as_posix()}",
        ]
    )


@pytask.hookimpl
def pytask_collect_task(session, path, name, obj):
    """Collect a task which is a function.

    There is some discussion on how to detect functions in this `thread
    <https://stackoverflow.com/q/624926/7523785>`_. :class:`types.FunctionType` does not
    detect built-ins which is not possible anyway.

    """
    if name.startswith("task_") and callable(obj) and has_marker(obj, "latex"):
        task = PythonFunctionTask.from_path_name_function_session(
            path, name, obj, session
        )
        latex_function = _copy_func(compile_latex_document)
        latex_function.pytestmark = copy.deepcopy(task.function.pytestmark)

        args = _create_command_line_arguments(task)
        latex_function = functools.partial(latex_function, args=args)

        task.function = latex_function

        return task


def _create_command_line_arguments(task):
    args = get_markers_from_task(task, "latex")[0].args
    if args:
        out = list(args)
    else:
        out = ["--pdf", "--interaction=nonstopmode", "--synctex=1"]

    return out
