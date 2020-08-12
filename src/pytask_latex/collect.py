import copy
import functools
import subprocess
from typing import Iterable
from typing import Optional
from typing import Union

from _pytask.config import hookimpl
from _pytask.mark import get_specific_markers_from_task
from _pytask.mark import has_marker
from _pytask.nodes import PythonFunctionTask
from _pytask.parametrize import _copy_func
from _pytask.shared import to_list


def latex(options: Optional[Union[str, Iterable[str]]] = None):
    """Specify command line options for latexmk.

    Parameters
    ----------
    options : Optional[Union[str, Iterable[str]]]
        One or multiple command line options passed to latexmk.

    """
    if options is None:
        options = ["--pdf", "--interaction=nonstopmode", "--synctex=1"]
    elif isinstance(options, str):
        options = [options]
    return options


def compile_latex_document(depends_on, produces, latex):
    latex_document = to_list(depends_on)[0]

    if latex_document.stem != produces.stem:
        latex.append(f"--jobname={produces.stem}")

    subprocess.run(
        [
            "latexmk",
            *latex,
            f"--output-directory={produces.parent.as_posix()}",
            f"{latex_document.as_posix()}",
        ]
    )


@hookimpl
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
        latex_function.pytaskmark = copy.deepcopy(task.function.pytaskmark)

        args = _create_command_line_arguments(task)
        latex_function = functools.partial(latex_function, latex=args)

        task.function = latex_function

        if task.depends_on[0].value.suffix != ".tex":
            raise ValueError(
                "The first dependency of a LaTeX task must be the document which will "
                "be compiled."
            )

        return task


def _create_command_line_arguments(task):
    latex_marks = get_specific_markers_from_task(task, "latex")
    mark = latex_marks[0]
    for mark_ in latex_marks[1:]:
        mark = mark.combine_with(mark_)

    options = latex(*mark.args, **mark.kwargs)

    return options
