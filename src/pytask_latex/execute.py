"""Execute tasks."""
import shutil

from _pytask.config import hookimpl
from _pytask.mark import get_specific_markers_from_task
from _pytask.nodes import FilePathNode


@hookimpl
def pytask_execute_task_setup(task):
    """Perform some checks before a LaTeX document is compiled.

    Perform the following checks.

    1. latexmk needs to be found on your PATH.
    2. The first dependency must be the source document.
    3. The first product must point to a .pdf, .ps, or .dvi file.

    """
    if get_specific_markers_from_task(task, "latex"):
        if shutil.which("latexmk") is None:
            raise RuntimeError(
                "latexmk is needed to compile LaTeX documents, but it is not found on "
                "your PATH."
            )

        if not (
            isinstance(task.depends_on[0], FilePathNode)
            and task.depends_on[0].value.suffix == ".tex"
        ):
            raise ValueError(
                "The first or sole dependency must point to the .tex document which "
                "will be compiled."
            )

        if not (
            isinstance(task.produces[0], FilePathNode)
            and task.produces[0].value.suffix in [".pdf", ".ps", ".dvi"]
        ):
            raise ValueError(
                "The first or sole product must point to a .pdf, .ps or .dvi file "
                "which is the compilation."
            )
