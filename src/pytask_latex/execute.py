"""Execute tasks."""
from __future__ import annotations

import shutil

from pytask import PTask, has_mark
from pytask import hookimpl
from pytask import Task


@hookimpl
def pytask_execute_task_setup(task: PTask) -> None:
    """Check that latexmk is found on the PATH if a LaTeX task should be executed."""
    if has_mark(task, "latex") and shutil.which("latexmk") is None:
        raise RuntimeError(
            "latexmk is needed to compile LaTeX documents, but it is not found on "
            "your PATH."
        )
