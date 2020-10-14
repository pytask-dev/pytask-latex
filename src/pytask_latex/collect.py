"""Collect tasks."""
import copy
import functools
import subprocess
from typing import Iterable
from typing import Optional
from typing import Union

from _pytask.config import hookimpl
from _pytask.mark import get_specific_markers_from_task
from _pytask.mark import has_marker
from _pytask.nodes import FilePathNode
from _pytask.nodes import PythonFunctionTask
from _pytask.parametrize import _copy_func
from _pytask.shared import to_list


DEFAULT_OPTIONS = ["--pdf", "--interaction=nonstopmode", "--synctex=1", "--cd"]


def latex(options: Optional[Union[str, Iterable[str]]] = None):
    """Specify command line options for latexmk.

    Parameters
    ----------
    options : Optional[Union[str, Iterable[str]]]
        One or multiple command line options passed to latexmk.

    """
    if options is None:
        options = DEFAULT_OPTIONS.copy()
    elif isinstance(options, str):
        options = [options]

    return options


def compile_latex_document(depends_on, produces, latex):
    """Compile a LaTeX document.

    This function replaces the dummy function of an LaTeX task. It is a nice wrapper
    around subprocess.

    The output folder needs to be declared as a relative path to the directory where the
    latex source lies.

    1. It must be relative because bibtex / biber, which is necessary for
       bibliographies, does not accept full paths as a safety measure.
    2. Due to the ``--cd`` flag, latexmk will change the directory to the one where the
       source files are. Thus, relative to the latex sources.

    See this `discussion on Github
    <https://github.com/James-Yu/LaTeX-Workshop/issues/1932#issuecomment-582416434>`_
    for additional information.

    """
    latex_document = to_list(depends_on)[0]
    compiled_document = to_list(produces)[0]

    if latex_document.stem != compiled_document.stem:
        latex.append(f"--jobname={compiled_document.stem}")

    # See comment in doc string.
    out_relative_to_latex_source = compiled_document.parent.relative_to(
        latex_document.parent
    )
    subprocess.run(
        [
            "latexmk",
            *latex,
            f"--output-directory={out_relative_to_latex_source.as_posix()}",
            f"{latex_document.as_posix()}",
        ],
        check=True,
    )


@hookimpl
def pytask_collect_task(session, path, name, obj):
    """Collect a task which is a function.

    There is some discussion on how to detect functions in this `thread
    <https://stackoverflow.com/q/624926/7523785>`_. :class:`types.FunctionType` does not
    detect built-ins which is not possible anyway.

    """
    if name.startswith("task_") and callable(obj) and has_marker(obj, "latex"):
        # Collect the task.
        task = PythonFunctionTask.from_path_name_function_session(
            path, name, obj, session
        )
        latex_function = _copy_func(compile_latex_document)
        latex_function.pytaskmark = copy.deepcopy(task.function.pytaskmark)

        merged_mark = _merge_all_markers(task)
        args = latex(*merged_mark.args, **merged_mark.kwargs)
        latex_function = functools.partial(latex_function, latex=args)

        task.function = latex_function

        return task


@hookimpl
def pytask_collect_task_teardown(task):
    """Perform some checks.

    Remove check for task is none with pytask 0.0.9.

    """
    if task is not None and get_specific_markers_from_task(task, "latex"):
        if (len(task.depends_on) == 0) or (
            not (
                isinstance(task.depends_on[0], FilePathNode)
                and task.depends_on[0].value.suffix == ".tex"
            )
        ):
            raise ValueError(
                "The first or sole dependency of a LaTeX task must be the document "
                "which will be compiled and has a .tex extension."
            )

        if (len(task.produces) == 0) or (
            not (
                isinstance(task.produces[0], FilePathNode)
                and task.produces[0].value.suffix in [".pdf", ".ps", ".dvi"]
            )
        ):
            raise ValueError(
                "The first or sole product of a LaTeX task must point to a .pdf, .ps "
                "or .dvi file which is the compiled document."
            )


def _merge_all_markers(task):
    """Combine all information from markers for the compile latex function."""
    latex_marks = get_specific_markers_from_task(task, "latex")
    mark = latex_marks[0]
    for mark_ in latex_marks[1:]:
        mark = mark.combined_with(mark_)
    return mark
