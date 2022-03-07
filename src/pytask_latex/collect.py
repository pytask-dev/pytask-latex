"""Collect tasks."""
from __future__ import annotations

import copy
import functools
import warnings
from subprocess import CalledProcessError
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Sequence

import latex_dependency_scanner as lds
from _pytask.config import hookimpl
from _pytask.mark import Mark
from _pytask.mark_utils import get_specific_markers_from_task
from _pytask.mark_utils import has_marker
from _pytask.nodes import _collect_nodes
from _pytask.nodes import FilePathNode
from _pytask.nodes import PythonFunctionTask
from _pytask.parametrize import _copy_func
from pytask_latex import build_steps as bs
from pytask_latex.utils import to_list


_DEPRECATION_WARNING = """The old syntax for using @pytask.mark.latex is deprecated \
and will be removed in v0.2.0. To pass custom options to latexmk and the compilation \
process convert

    @pytask.mark.latex(options)
    def task_func():
        ...

to

    from pytask_latex import build_steps

    @pytask.mark.latex(build_steps.latexmk(options))
    def task_func():
        ...

"""


def latex(
    options: str | Iterable[str] | None = None,
    *,
    build_steps: str | Callable[..., Any] | Sequence[str | Callable[..., Any]] = None,
):
    """Specify command line options for latexmk.

    Parameters
    ----------
    options
        One or multiple command line options passed to latexmk.
    build_steps
        Build steps to compile the document.

    """
    build_steps = ["latexmk"] if build_steps is None else build_steps

    if options is not None:
        warnings.warn(_DEPRECATION_WARNING, DeprecationWarning)
        out = [bs.latexmk(options)]

    else:
        out = []
        for step in to_list(build_steps):
            if isinstance(step, str):
                parsed_step = getattr(bs, step)
                if parsed_step is None:
                    raise ValueError(f"Build step {step!r} is unknown.")
                out.append(parsed_step())
            elif callable(step):
                out.append(step)
            else:
                raise ValueError(f"Build step {step!r} is not a valid step.")

    return out


def compile_latex_document(build_steps, path_to_tex, path_to_document):
    """Replaces the dummy function provided by the user."""

    for step in build_steps:
        try:
            step(path_to_tex=path_to_tex, path_to_document=path_to_document)
        except CalledProcessError as e:
            raise RuntimeError(f"Build step {step.__name__} failed.") from e


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

        task_function = _copy_func(compile_latex_document)
        task_function.pytaskmark = copy.deepcopy(task.function.pytaskmark)

        merged_mark = _merge_all_markers(task)
        steps = latex(*merged_mark.args, **merged_mark.kwargs)
        args = get_build_step_args(session, task)
        task_function = functools.partial(task_function, build_steps=steps, **args)

        task.function = task_function

        if session.config["infer_latex_dependencies"]:
            task = _add_latex_dependencies_retroactively(task, session)


def _get_node_from_dictionary(obj, key, fallback=0):
    if isinstance(obj, dict):
        obj = obj.get(key) or obj.get(fallback)
    return obj


def _add_latex_dependencies_retroactively(task, session):
    """Add dependencies from LaTeX document to task.

    Unfortunately, the dependencies have to be added retroactively, after the task has
    been created, since one needs access to the LaTeX document which is validated after
    the task is created.

    1. Collect all possible files from the LaTeX document.
    2. Keep only files which exist or which are produced by some other task. Note that
       only tasks are considered which have been collected until this point.
    3. Mark the task such that it will be evaluated at last.

    Parameters
    ----------
    task
        The LaTeX task.
    session : _pytask.session.Session
        The session.

    """
    source = _get_node_from_dictionary(
        task.depends_on, session.config["latex_source_key"]
    )

    # Scan the LaTeX document for included files.
    latex_dependencies = set(lds.scan(source.path))

    # Remove duplicated dependencies which have already been added by the user and those
    # which do not exist.
    existing_paths = {
        i.path for i in task.depends_on.values() if isinstance(i, FilePathNode)
    }
    new_deps = latex_dependencies - existing_paths
    new_existing_deps = {i for i in new_deps if i.exists()}

    # Put scanned dependencies in a dictionary with incrementing keys.
    used_integer_keys = [i for i in task.depends_on if isinstance(i, int)]
    max_int = max(used_integer_keys) if used_integer_keys else 0
    new_existing_deps = dict(enumerate(new_existing_deps, max_int + 1))

    # Collect new dependencies and add them to the task.
    collected_dependencies = _collect_nodes(
        session, task.path, task.name, new_existing_deps
    )
    task.depends_on = {**task.depends_on, **collected_dependencies}

    # Mark the task as being delayed to avoid conflicts with unmatched dependencies.
    task.markers.append(Mark("try_last", (), {}))

    return task


def _merge_all_markers(task):
    """Combine all information from markers for the compile latex function."""
    latex_marks = get_specific_markers_from_task(task, "latex")
    mark = latex_marks[0]
    for mark_ in latex_marks[1:]:
        mark = mark.combined_with(mark_)
    return mark


def get_build_step_args(session, task):
    """Prepare arguments passe to each build step."""
    latex_document = _get_node_from_dictionary(
        task.depends_on, session.config["latex_source_key"]
    ).value
    compiled_document = _get_node_from_dictionary(
        task.produces, session.config["latex_document_key"]
    ).value

    return {"path_to_tex": latex_document, "path_to_document": compiled_document}
