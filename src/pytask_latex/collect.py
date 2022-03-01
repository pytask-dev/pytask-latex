"""Collect tasks."""
from __future__ import annotations

import copy
import functools
import warnings
from typing import Callable
from typing import Sequence

from _pytask.config import hookimpl
from _pytask.mark import Mark
from _pytask.mark_utils import get_specific_markers_from_task
from _pytask.mark_utils import has_marker
from _pytask.nodes import _collect_nodes
from _pytask.nodes import FilePathNode
from _pytask.nodes import PythonFunctionTask
from _pytask.parametrize import _copy_func
from latex_dependency_scanner import scan
from pytask_latex import build_steps


def compile_latex_document(build_steps, main_file, job_name, out_dir):
    """Replaces the dummy function provided by the user."""

    for step in build_steps:
        try:
            step(main_file, job_name, out_dir)
        except Exception as e:
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
        steps = get_build_steps(merged_mark)
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
    latex_dependencies = set(scan(source.path))

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


def get_build_steps(latex_mark: Mark):
    if isinstance(list, latex_mark.args[0]):
        warnings.warn(
            "The old argument syntax for latexmk is deprecated and will be removed in "
            "the next minor update. Afterwards a given list will be interpreted as "
            "list of build steps."
        )
        yield build_steps.latexmk(_to_list(latex_mark.args[0]))

    elif "build_steps" in latex_mark.kwargs:
        for step in latex_mark.kwargs["build_steps"]:
            if isinstance(step, str):
                yield getattr(build_steps, step)()  # create step with default args
                continue

            if isinstance(step, Callable):
                yield step  # already step function
                continue

            raise ValueError("Unrecognized item given in build_steps")

    else:
        yield from build_steps.default_steps()


def get_build_step_args(session, task):
    """Prepare arguments for build step functions"""
    latex_document = _get_node_from_dictionary(
        task.depends_on, session.config["latex_source_key"]
    ).value
    compiled_document = _get_node_from_dictionary(
        task.produces, session.config["latex_document_key"]
    ).value

    job_name = compiled_document.stem

    out_dir = compiled_document.parent

    return {"main_file": latex_document, "job_name": job_name, "out_dir": out_dir}


def _to_list(scalar_or_iter):
    """Convert scalars and iterables to list.

    Parameters
    ----------
    scalar_or_iter : str or list

    Returns
    -------
    list

    Examples
    --------
    >>> _to_list("a")
    ['a']
    >>> _to_list(["b"])
    ['b']

    """
    return (
        [scalar_or_iter]
        if isinstance(scalar_or_iter, str) or not isinstance(scalar_or_iter, Sequence)
        else list(scalar_or_iter)
    )
