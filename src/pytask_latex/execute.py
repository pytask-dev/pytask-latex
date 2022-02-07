"""Execute tasks."""
from __future__ import annotations

import shutil

from _pytask.config import hookimpl
from _pytask.mark_utils import get_specific_markers_from_task


@hookimpl
def pytask_execute_task_setup(task):
    """Check that latexmk is found on the PATH if a LaTeX task should be executed."""
    if get_specific_markers_from_task(task, "latex"):
        if shutil.which("latexmk") is None:
            raise RuntimeError(
                "latexmk is needed to compile LaTeX documents, but it is not found on "
                "your PATH."
            )
