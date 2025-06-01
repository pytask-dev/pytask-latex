"""Execute tasks."""

from __future__ import annotations

import shutil

from pytask import PTask
from pytask import has_mark
from pytask import hookimpl


@hookimpl(trylast=True)
def pytask_execute_task_setup(task: PTask) -> None:
    """Check that latexmk is found on the PATH if a LaTeX task should be executed."""
    _rich_traceback_omit = True
    if has_mark(task, "latex") and shutil.which("latexmk") is None:
        msg = (
            "latexmk is needed to compile LaTeX documents, but it is not found on "
            "your PATH."
        )
        raise RuntimeError(msg)
