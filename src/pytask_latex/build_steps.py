"""This module contains build steps for compiling a LaTeX document.

Each build step must have the following signature:

.. code-block::

    def build_step(main_file: Path, job_name: Optional[str], out_dir: Optional[Path]):
        ...

A build step constructor must yield a function with this signature.

"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _get_relative_out_dir(main_file, out_dir):
    """The output folder needs to be declared as a relative path to the directory where
    the latex source lies.

    1. It must be relative because bibtex / biber, which is necessary for
       bibliographies, does not accept full paths as a safety measure.
    2. Due to the ``--cd`` flag, latexmk will change the directory to the one where the
       source files are. Thus, relative to the latex sources.

    See this `discussion on Github
    <https://github.com/James-Yu/LaTeX-Workshop/issues/1932#issuecomment-582416434>`_
    for additional information.

    """
    return Path(os.path.relpath(out_dir, main_file.parent)).as_posix()


def latexmk(options=("--pdf", "--interaction=nonstopmode", "--synctex=1", "--cd")):
    """Build step that calls latexmk."""
    options = [str(i) for i in options]

    def run_latexmk(main_file, job_name, out_dir):
        job_name_opt = [f"--jobname={job_name}"] if job_name else []
        out_dir_opt = (
            [f"--output-directory={_get_relative_out_dir(main_file, out_dir)}"]
            if out_dir
            else []
        )
        cmd = (
            ["latexmk", *options] + job_name_opt + out_dir_opt + [main_file.as_posix()]
        )
        subprocess.run(cmd, check=True)

    return run_latexmk
