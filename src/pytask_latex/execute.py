import shutil
from pathlib import Path

import pytask
from pytask.mark import get_markers_from_task


@pytask.hookimpl
def pytask_execute_task_setup(task):
    if get_markers_from_task(task, "latex"):
        if shutil.which("latexmk") is None:
            raise RuntimeError(
                "latexmk is needed to compile LaTeX documents, but it is not found on "
                "your PATH."
            )

    if isinstance(task.depends_on, Path):
        raise ValueError("'depends_on' must be a path to a single .tex document.")

    if isinstance(task.produces, Path):
        raise ValueError("'produces' must be a path to a single .pdf document.")
