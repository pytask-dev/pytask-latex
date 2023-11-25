"""Contains functions related to handling paths."""
from __future__ import annotations

import os
from pathlib import Path


def relative_to(path: Path, relative_to_: Path) -> str:
    """Create a relative path from one path to another as a string.

    The output folder needs to be declared as a relative path to the directory where
    the latex source lies.

    1. It must be relative because bibtex / biber, which is necessary for
       bibliographies, does not accept full paths as a safety measure.
    2. Due to the ``--cd`` flag, latexmk will change the directory to the one where the
       source files are. Thus, relative to the latex sources.

    See this `discussion on Github
    <https://github.com/James-Yu/LaTeX-Workshop/issues/1932#issuecomment-582416434>`_
    for additional information.

    Example
    -------
    >>> import sys
    >>> from pathlib import Path
    >>> if sys.platform == "win32":
    ...     p = Path("C:/Users/user/documents/file.tex")
    ... else:
    ...     p = Path("/home/user/documents/file.tex")
    >>> out = p.parents[2].joinpath("bld", "docs")
    >>> relative_to(p, out)
    '../../bld/docs'

    """
    return Path(os.path.relpath(relative_to_, path.parent)).as_posix()
