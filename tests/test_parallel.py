"""Contains test which ensure that the plugin works with pytask-parallel."""

from __future__ import annotations

import os
import textwrap

import pytest
from pytask import ExitCode
from pytask import cli

from tests.conftest import needs_latexmk
from tests.conftest import skip_on_github_actions_with_win

try:
    import pytask_parallel  # noqa: F401
except ImportError:  # pragma: no cover
    _IS_PYTASK_PARALLEL_INSTALLED = False
else:
    _IS_PYTASK_PARALLEL_INSTALLED = True


pytestmark = pytest.mark.skipif(
    not _IS_PYTASK_PARALLEL_INSTALLED, reason="Tests require pytask-parallel."
)

xfail_on_remote = pytest.mark.xfail(
    condition=os.environ.get("CI") == "true", reason="Does not succeed on CI."
)


@xfail_on_remote
@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end()
def test_parallel_parametrization_over_source_files_w_loop(runner, tmp_path):
    source = """
    from pytask import mark, task

    for i in range(1, 3):

        @task
        @mark.latex(script=f"document_{i}.tex", document=f"document_{i}.pdf")
        def task_compile_latex_document():
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    He said yeah.
    \end{document}
    """
    tmp_path.joinpath("document_1.tex").write_text(textwrap.dedent(latex_source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    You better come out with your hands up.
    \end{document}
    """
    tmp_path.joinpath("document_2.tex").write_text(textwrap.dedent(latex_source))
    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])
    assert result.exit_code == ExitCode.OK


@xfail_on_remote
@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end()
def test_parallel_parametrization_over_source_file_w_loop(runner, tmp_path):
    source = """
    from pytask import mark, task
    from pytask_latex import compilation_steps as cs

    for ending in ("pdf", "dvi"):

        @task
        @mark.latex(
            script="document.tex",
            document=f"document.{ending}",
            compilation_steps=cs.latexmk(
                (f"--{ending}", "--interaction=nonstopmode", "--synctex=1", "--cd")
            )
        )
        def task_compile_latex_document():
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    Ma il mio mistero e chiuso in me
    \end{document}
    """
    tmp_path.joinpath("document.tex").write_text(textwrap.dedent(latex_source))
    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])
    assert result.exit_code == ExitCode.OK
