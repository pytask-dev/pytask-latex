"""Collect tasks."""
from __future__ import annotations

import functools
from pathlib import Path
from subprocess import CalledProcessError
from types import FunctionType
from typing import Any
from typing import Callable
from typing import Sequence

import latex_dependency_scanner as lds
from pybaum.tree_util import tree_map
from pytask import depends_on
from pytask import FilePathNode
from pytask import has_mark
from pytask import hookimpl
from pytask import Mark
from pytask import MetaNode
from pytask import NodeNotCollectedError
from pytask import parse_nodes
from pytask import produces
from pytask import remove_marks
from pytask import Session
from pytask import Task
from pytask_latex import compilation_steps as cs
from pytask_latex.utils import to_list


def latex(
    *,
    script: str | Path,
    document: str | Path,
    compilation_steps: str
    | Callable[..., Any]
    | Sequence[str | Callable[..., Any]]
    | None = None,
) -> tuple[
    str | Path,
    str | Path,
    str | Callable[..., Any] | Sequence[str | Callable[..., Any]] | None,
]:
    """Specify command line options for latexmk.

    Parameters
    ----------
    script : str | Path
        The LaTeX file that will be compiled.
    document : str | Path
        The path to the compiled document.
    compilation_steps
        Compilation steps to compile the document.

    """
    return script, document, compilation_steps


def compile_latex_document(
    compilation_steps: list[Callable[..., Any]],
    path_to_tex: Path,
    path_to_document: Path,
) -> None:
    """Compile a LaTeX document iterating over compilations steps.

    Replaces the placeholder function provided by the user.

    """
    for step in compilation_steps:
        try:
            step(path_to_tex=path_to_tex, path_to_document=path_to_document)
        except CalledProcessError as e:
            raise RuntimeError(f"Compilation step {step.__name__} failed.") from e


@hookimpl
def pytask_collect_task(
    session: Session, path: Path, name: str, obj: Any
) -> Task | None:
    """Perform some checks."""
    __tracebackhide__ = True

    if (
        (name.startswith("task_") or has_mark(obj, "task"))
        and callable(obj)
        and has_mark(obj, "latex")
    ):
        obj, marks = remove_marks(obj, "latex")

        if len(marks) > 1:
            raise ValueError(
                f"Task {name!r} has multiple @pytask.mark.latex marks, but only one is "
                "allowed."
            )
        latex_mark = marks[0]
        script, document, compilation_steps = latex(**latex_mark.kwargs)

        parsed_compilation_steps = _parse_compilation_steps(compilation_steps)

        obj.pytask_meta.markers.append(latex_mark)

        dependencies = parse_nodes(session, path, name, obj, depends_on)
        products = parse_nodes(session, path, name, obj, produces)

        markers = obj.pytask_meta.markers if hasattr(obj, "pytask_meta") else []
        kwargs = obj.pytask_meta.kwargs if hasattr(obj, "pytask_meta") else {}

        task = Task(
            base_name=name,
            path=path,
            function=_copy_func(compile_latex_document),  # type: ignore[arg-type]
            depends_on=dependencies,
            produces=products,
            markers=markers,
            kwargs=kwargs,
        )

        script_node = session.hook.pytask_collect_node(
            session=session, path=path, node=script
        )
        document_node = session.hook.pytask_collect_node(
            session=session, path=path, node=document
        )

        if not (
            isinstance(script_node, FilePathNode)
            and script_node.value.suffix == ".tex"  # noqa: PLR2004
        ):
            raise ValueError(
                "The 'script' keyword of the @pytask.mark.latex decorator must point "
                "to LaTeX file with the .tex suffix."
            )

        if not (
            isinstance(document_node, FilePathNode)
            and document_node.value.suffix in (".pdf", ".ps", ".dvi")
        ):
            raise ValueError(
                "The 'document' keyword of the @pytask.mark.latex decorator must point "
                "to a .pdf, .ps or .dvi file."
            )

        if isinstance(task.depends_on, dict):
            task.depends_on["__script"] = script_node
        else:
            task.depends_on = {0: task.depends_on, "__script": script_node}
        if isinstance(task.produces, dict):
            task.produces["__document"] = document_node
        else:
            task.produces = {0: task.produces, "__document": document_node}

        task.function = functools.partial(
            task.function,
            compilation_steps=parsed_compilation_steps,
            path_to_tex=script_node.path,
            path_to_document=document_node.path,
        )

        if session.config["infer_latex_dependencies"]:
            task = _add_latex_dependencies_retroactively(task, session)

        return task
    return None


def _add_latex_dependencies_retroactively(task: Task, session: Session) -> Task:
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
    session : pytask.Session
        The session.

    """
    # Scan the LaTeX document for included files.
    latex_dependencies = set(lds.scan(task.depends_on["__script"].path))

    # Remove duplicated dependencies which have already been added by the user and those
    # which do not exist.
    existing_paths = {
        i.path for i in task.depends_on.values() if isinstance(i, FilePathNode)
    }
    new_deps = latex_dependencies - existing_paths
    new_existing_deps = {i for i in new_deps if i.exists()}
    new_numbered_deps = dict(enumerate(new_existing_deps))

    # Collect new dependencies and add them to the task.
    collected_dependencies = tree_map(
        lambda x: _collect_node(session, task.path, task.name, x), new_numbered_deps
    )
    task.depends_on["__scanned_dependencies"] = collected_dependencies

    # Mark the task as being delayed to avoid conflicts with unmatched dependencies.
    task.markers.append(Mark("try_last", (), {}))

    return task


def _copy_func(func: FunctionType) -> FunctionType:
    """Create a copy of a function.

    Based on https://stackoverflow.com/a/13503277/7523785.

    Example
    -------
    >>> def _func(): pass
    >>> copied_func = _copy_func(_func)
    >>> _func is copied_func
    False

    """
    new_func = FunctionType(
        func.__code__,
        func.__globals__,
        name=func.__name__,
        argdefs=func.__defaults__,
        closure=func.__closure__,
    )
    new_func = functools.update_wrapper(new_func, func)
    new_func.__kwdefaults__ = func.__kwdefaults__
    return new_func


def _collect_node(
    session: Session, path: Path, name: str, node: str | Path
) -> dict[str, MetaNode]:
    """Collect nodes for a task.

    Parameters
    ----------
    session : pytask.Session
        The session.
    path : Path
        The path to the task whose nodes are collected.
    name : str
        The name of the task.
    nodes : Dict[str, Union[str, Path]]
        A dictionary of nodes parsed from the ``depends_on`` or ``produces`` markers.

    Returns
    -------
    Dict[str, MetaNode]
        A dictionary of node names and their paths.

    Raises
    ------
    NodeNotCollectedError
        If the node could not collected.

    """
    collected_node = session.hook.pytask_collect_node(
        session=session, path=path, node=node
    )
    if collected_node is None:
        raise NodeNotCollectedError(
            f"{node!r} cannot be parsed as a dependency or product for task "
            f"{name!r} in {path!r}."
        )

    return collected_node


def _parse_compilation_steps(
    compilation_steps: str | Callable[..., Any] | Sequence[str | Callable[..., Any]]
) -> list[Callable[..., Any]]:
    """Parse compilation steps."""
    __tracebackhide__ = True

    compilation_steps = ["latexmk"] if compilation_steps is None else compilation_steps

    parsed_compilation_steps = []
    for step in to_list(compilation_steps):
        if isinstance(step, str):
            try:
                parsed_step = getattr(cs, step)
            except AttributeError:
                raise ValueError(f"Compilation step {step!r} is unknown.") from None
            parsed_compilation_steps.append(parsed_step())
        elif callable(step):
            parsed_compilation_steps.append(step)
        else:
            raise ValueError(f"Compilation step {step!r} is not a valid step.")

    return parsed_compilation_steps
