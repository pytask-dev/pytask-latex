import shutil

import pytask
from pytask.mark import get_markers_from_task
from pytask.nodes import FilePathNode


@pytask.hookimpl
def pytask_execute_task_setup(task):
    if get_markers_from_task(task, "latex"):
        if shutil.which("latexmk") is None:
            raise RuntimeError(
                "latexmk is needed to compile LaTeX documents, but it is not found on "
                "your PATH."
            )

        first_dep = task.depends_on[0]
        if not (
            isinstance(first_dep, FilePathNode) and first_dep.value.suffix == ".tex"
        ):
            raise ValueError(
                "The first or sole dependency must point to the .tex document which "
                "will be compiled."
            )

        first_prod = task.produces[0]
        if not (
            isinstance(first_prod, FilePathNode)
            and first_prod.value.suffix in [".pdf", ".ps", ".dvi"]
        ):
            raise ValueError(
                "The first or sole product must point to a .pdf, .ps or .dvi file "
                "which is the compilation."
            )
