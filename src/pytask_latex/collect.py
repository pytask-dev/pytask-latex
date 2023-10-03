"""Collect tasks."""
from __future__ import annotations

import functools
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
from pytask import MetaNode
from pytask import NodeInfo
from pytask import NodeNotCollectedError
from pytask import parse_dependencies_from_task_function
from pytask import parse_products_from_task_function
from pytask import PathNode
from pytask import PPathNode
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
    compilation_steps: list[Callable[..., Any]],
    path_to_tex: Path,
    path_to_document: Path,
    **kwargs: Any,  # noqa: ARG001
) -> None:
    """Compile a LaTeX document iterating over compilations steps.

    Replaces the placeholder function provided by the user.

    """
    try:
        for step in compilation_steps:
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
        and is_task_function(obj)
        and has_mark(obj, "latex")
    ):
        # Parse the @pytask.mark.latex decorator.
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
            raise ValueError(
                "The 'script' keyword of the @pytask.mark.latex decorator must point "
                f"to LaTeX file with the .tex suffix, but it is {script_node}."
            )

        if not (
            isinstance(document_node, PathNode)
            and document_node.path.suffix in (".pdf", ".ps", ".dvi")
        ):
            raise ValueError(
                "The 'document' keyword of the @pytask.mark.latex decorator must point "
                "to a .pdf, .ps or .dvi file."
            )

        # Parse other dependencies and products.
        dependencies = parse_dependencies_from_task_function(
            session, path, name, path_nodes, obj
        )
        products = parse_products_from_task_function(
            session, path, name, path_nodes, obj
        )

        # Add script and document
        dependencies["__script"] = script_node
        products["__document"] = document_node

        markers = obj.pytask_meta.markers if hasattr(obj, "pytask_meta") else []

        # Prepare the task function.
        task_function = functools.partial(
            compile_latex_document,
            compilation_steps=parsed_compilation_steps,
            path_to_tex=script_node.path,
            path_to_document=document_node.path,
        )

        if path is None:
            task = TaskWithoutPath(
                name=name,
                function=task_function,
                depends_on=dependencies,
                produces=products,
                markers=markers,
            )
        else:
            task = Task(
                base_name=name,
                path=path,
                function=task_function,
                depends_on=dependencies,
                produces=products,
                markers=markers,
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
    latex_dependencies = set(
        lds.scan(task.depends_on["__script"].path)  # type: ignore[attr-defined]
    )

    # Remove duplicated dependencies which have already been added by the user and those
    # which do not exist.
    existing_paths = {
        i.path for i in tree_leaves(task.depends_on) if isinstance(i, PPathNode)
    }
    new_deps = latex_dependencies - existing_paths
    new_existing_deps = {i for i in new_deps if i.exists()}
    new_numbered_deps = dict(enumerate(new_existing_deps))

    # Collect new dependencies and add them to the task.
    path_nodes = task.path.parent if isinstance(task, PTaskWithPath) else Path.cwd()

    collected_dependencies = tree_map(
        lambda x: _collect_node(
            session,
            path_nodes,
            NodeInfo(
                arg_name="__scanned_dependencies",
                path=(),
                value=x,
                task_path=task.path,
                task_name=task.name,
            ),
        ),
        new_numbered_deps,
    )
    task.depends_on[
        "__scanned_dependencies"
    ] = collected_dependencies  # type: ignore[assignment]

    # Mark the task as being delayed to avoid conflicts with unmatched dependencies.
    task.markers.append(Mark("try_last", (), {}))

    return task


def _collect_node(
    session: Session, path: Path, node_info: NodeInfo
) -> dict[str, MetaNode]:
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
        raise NodeNotCollectedError(
            f"{node_info.arg_name!r} cannot be parsed as a dependency or product for "
            f"task {node_info.task_name!r} in {node_info.task_path!r}."
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
