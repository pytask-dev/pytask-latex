"""Collect tasks."""
import copy
import functools
import os
import subprocess
from pathlib import Path
from typing import Iterable
from typing import Optional
from typing import Union

from _pytask.config import hookimpl
from _pytask.mark import get_specific_markers_from_task
from _pytask.mark import has_marker
from _pytask.nodes import FilePathNode
from _pytask.nodes import PythonFunctionTask
from _pytask.parametrize import _copy_func


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


def compile_latex_document(latex):
    """Replaces the dummy function provided by the user."""
    subprocess.run(latex, check=True)


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

        return task


@hookimpl
def pytask_collect_task_teardown(session, task):
    """Perform some checks."""
    if get_specific_markers_from_task(task, "latex"):
        source = _get_node_from_dictionary(
            task.depends_on, session.config["latex_source_key"]
        )
        if not (isinstance(source, FilePathNode) and source.value.suffix == ".tex"):
            raise ValueError(
                "The first or sole dependency of a LaTeX task must be the document "
                "which will be compiled and has a .tex extension."
            )

        document = _get_node_from_dictionary(
            task.produces, session.config["latex_document_key"]
        )
        if not (
            isinstance(document, FilePathNode)
            and document.value.suffix in [".pdf", ".ps", ".dvi"]
        ):
            raise ValueError(
                "The first or sole product of a LaTeX task must point to a .pdf, .ps "
                "or .dvi file which is the compiled document."
            )

        latex_function = _copy_func(compile_latex_document)
        latex_function.pytaskmark = copy.deepcopy(task.function.pytaskmark)

        merged_mark = _merge_all_markers(task)
        args = latex(*merged_mark.args, **merged_mark.kwargs)
        options = _prepare_cmd_options(session, task, args)
        latex_function = functools.partial(latex_function, latex=options)

        task.function = latex_function


def _get_node_from_dictionary(obj, key, fallback=0):
    if isinstance(obj, Path):
        pass
    elif isinstance(obj, dict):
        obj = obj.get(key) or obj.get(fallback)
    return obj


def _merge_all_markers(task):
    """Combine all information from markers for the compile latex function."""
    latex_marks = get_specific_markers_from_task(task, "latex")
    mark = latex_marks[0]
    for mark_ in latex_marks[1:]:
        mark = mark.combined_with(mark_)
    return mark


def _prepare_cmd_options(session, task, args):
    """Prepare the command line arguments to compile the LaTeX document.

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
    latex_document = _get_node_from_dictionary(
        task.depends_on, session.config["latex_source_key"]
    ).value
    compiled_document = _get_node_from_dictionary(
        task.produces, session.config["latex_document_key"]
    ).value

    # Jobname controls the name of the compiled document. No suffix!
    if latex_document.stem != compiled_document.stem:
        jobname = [f"--jobname={compiled_document.stem}"]
    else:
        jobname = []

    # The path to the output directory must be relative from the location of the source
    # file. See docstring for more information.
    out_relative_to_latex_source = Path(
        os.path.relpath(compiled_document.parent, latex_document.parent)
    ).as_posix()

    return (
        [
            "latexmk",
            *args,
        ]
        + jobname
        + [
            f"--output-directory={out_relative_to_latex_source}",
            latex_document.as_posix(),
        ]
    )
