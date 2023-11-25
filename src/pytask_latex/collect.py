"""Collect tasks."""
from __future__ import annotations

import warnings
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any
from typing import Callable
from typing import Sequence

import latex_dependency_scanner as lds
from pytask import has_mark
from pytask import hookimpl
from pytask import is_task_function
from pytask import Mark
from pytask import NodeInfo
from pytask import NodeNotCollectedError
from pytask import parse_dependencies_from_task_function
from pytask import parse_products_from_task_function
from pytask import PathNode
from pytask import PNode
from pytask import PPathNode
from pytask import PTask
from pytask import PTaskWithPath
from pytask import remove_marks
from pytask import Session
from pytask import Task
from pytask import TaskWithoutPath
from pytask.tree_util import tree_leaves
from pytask.tree_util import tree_map
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
    _compilation_steps: list[Callable[..., Any]],
    _path_to_tex: Path,
    _path_to_document: Path,
    **kwargs: Any,  # noqa: ARG001
) -> None:
    """Compile a LaTeX document iterating over compilations steps.

    Replaces the placeholder function provided by the user.

    """
    try:
        for step in _compilation_steps:
            step(path_to_tex=_path_to_tex, path_to_document=_path_to_document)
    except CalledProcessError as e:
        msg = f"Compilation step {step.__name__} failed."
        raise RuntimeError(msg) from e


@hookimpl
def pytask_collect_task(
    session: Session, path: Path | None, name: str, obj: Any
) -> PTask | None:
    """Perform some checks."""
    __tracebackhide__ = True

    if (
        (name.startswith("task_") or has_mark(obj, "task"))
        and is_task_function(obj)
        and has_mark(obj, "latex")
    ):
        # Parse the @pytask.mark.latex decorator.
        obj, marks = remove_marks(obj, "latex")
        if len(marks) > 1:
            msg = (
                f"Task {name!r} has multiple @pytask.mark.latex marks, but only one is "
                "allowed."
            )
            raise ValueError(msg)
        latex_mark = marks[0]
        script, document, compilation_steps = latex(**latex_mark.kwargs)
        parsed_compilation_steps = _parse_compilation_steps(compilation_steps)

        obj.pytask_meta.markers.append(latex_mark)

        # Collect the nodes in @pytask.mark.latex and validate them.
        path_nodes = Path.cwd() if path is None else path.parent

        if isinstance(script, str):
            warnings.warn(
                "Passing a string for the latex parameter 'script' is deprecated. "
                "Please, use a pathlib.Path instead.",
                stacklevel=1,
            )
            script = Path(script)

        script_node = session.hook.pytask_collect_node(
            session=session,
            path=path_nodes,
            node_info=NodeInfo(
                arg_name="script", path=(), value=script, task_path=path, task_name=name
            ),
        )

        if isinstance(document, str):
            warnings.warn(
                "Passing a string for the latex parameter 'document' is deprecated. "
                "Please, use a pathlib.Path instead.",
                stacklevel=1,
            )
            document = Path(document)

        document_node = session.hook.pytask_collect_node(
            session=session,
            path=path_nodes,
            node_info=NodeInfo(
                arg_name="document",
                path=(),
                value=document,
                task_path=path,
                task_name=name,
            ),
        )

        if not (
            isinstance(script_node, PathNode) and script_node.path.suffix == ".tex"
        ):
            msg = (
                "The 'script' keyword of the @pytask.mark.latex decorator must point "
                f"to LaTeX file with the .tex suffix, but it is {script_node}."
            )
            raise ValueError(msg)

        if not (
            isinstance(document_node, PathNode)
            and document_node.path.suffix in (".pdf", ".ps", ".dvi")
        ):
            msg = (
                "The 'document' keyword of the @pytask.mark.latex decorator must point "
                "to a .pdf, .ps or .dvi file."
            )
            raise ValueError(msg)

        compilation_steps_node = session.hook.pytask_collect_node(
            session=session,
            path=path_nodes,
            node_info=NodeInfo(
                arg_name="_compilation_steps",
                path=(),
                value=parsed_compilation_steps,
                task_path=path,
                task_name=name,
            ),
        )

        # Parse other dependencies and products.
        dependencies = parse_dependencies_from_task_function(
            session, path, name, path_nodes, obj
        )
        products = parse_products_from_task_function(
            session, path, name, path_nodes, obj
        )

        # Add script and document
        dependencies["_path_to_tex"] = script_node
        dependencies["_compilation_steps"] = compilation_steps_node
        products["_path_to_document"] = document_node

        markers = obj.pytask_meta.markers if hasattr(obj, "pytask_meta") else []

        task: PTask
        if path is None:
            task = TaskWithoutPath(
                name=name,
                function=compile_latex_document,
                depends_on=dependencies,
                produces=products,
                markers=markers,
            )
        else:
            task = Task(
                base_name=name,
                path=path,
                function=compile_latex_document,
                depends_on=dependencies,
                produces=products,
                markers=markers,
            )

        return task
    return None


@hookimpl
def pytask_collect_modify_tasks(session: Session, tasks: list[PTask]) -> None:
    """Add dependencies from from LaTeX documents to tasks."""
    if session.config["infer_latex_dependencies"]:
        all_products = {
            product.path
            for task in tasks
            for product in tree_leaves(task.produces)
            if isinstance(product, PPathNode)
        }
        latex_tasks = [task for task in tasks if has_mark(task, "latex")]
        for task in latex_tasks:
            _add_latex_dependencies_retroactively(task, session, all_products)


def _add_latex_dependencies_retroactively(
    task: PTask, session: Session, all_products: set[Path]
) -> None:
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
    try:
        scanned_deps = set(
            lds.scan(task.depends_on["_path_to_tex"].path)  # type: ignore[attr-defined]
        )
    except Exception:  # noqa: BLE001
        warnings.warn(
            "pytask-latex failed to scan latex document for dependencies.", stacklevel=1
        )
        scanned_deps = set()

    # Remove duplicated dependencies which have already been added by the user and those
    # which do not exist.
    task_deps = {
        i.path for i in tree_leaves(task.depends_on) if isinstance(i, PPathNode)
    }
    additional_deps = scanned_deps - task_deps
    new_deps = [i for i in additional_deps if i in all_products or i.exists()]

    # Collect new dependencies and add them to the task.
    task_path = task.path if isinstance(task, PTaskWithPath) else None
    path_nodes = task.path.parent if isinstance(task, PTaskWithPath) else Path.cwd()

    collected_dependencies = tree_map(
        lambda x: _collect_node(
            session,
            path_nodes,
            NodeInfo(
                arg_name="_scanned_dependencies",
                path=(),
                value=x,
                task_path=task_path,
                task_name=task.name,
            ),
        ),
        new_deps,
    )
    task.depends_on["_scanned_dependencies"] = collected_dependencies

    # Mark the task as being delayed to avoid conflicts with unmatched dependencies.
    task.markers.append(Mark("try_last", (), {}))


def _collect_node(
    session: Session, path: Path, node_info: NodeInfo
) -> dict[str, PNode]:
    """Collect nodes for a task.

    Raises
    ------
    NodeNotCollectedError
        If the node could not collected.

    """
    collected_node = session.hook.pytask_collect_node(
        session=session, path=path, node_info=node_info
    )
    if collected_node is None:
        msg = (
            f"{node_info.arg_name!r} cannot be parsed as a dependency or product for "
            f"task {node_info.task_name!r} in {node_info.task_path!r}."
        )
        raise NodeNotCollectedError(msg)

    return collected_node


def _parse_compilation_steps(
    compilation_steps: str
    | Callable[..., Any]
    | Sequence[str | Callable[..., Any]]
    | None,
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
                msg = f"Compilation step {step!r} is unknown."
                raise ValueError(msg) from None
            parsed_compilation_steps.append(parsed_step())
        elif callable(step):
            parsed_compilation_steps.append(step)
        else:
            msg = f"Compilation step {step!r} is not a valid step."
            raise TypeError(msg)

    return parsed_compilation_steps
