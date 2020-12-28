"""Contains test which ensure that the plugin works with pytask-parallel."""
import textwrap
import time

import pytest
from conftest import needs_latexmk
from conftest import skip_on_github_actions_with_win
from pytask import cli

try:
    import pytask_parallel  # noqa: F401
except ImportError:
    _IS_PYTASK_PARALLEL_INSTALLED = False
else:
    _IS_PYTASK_PARALLEL_INSTALLED = True


pytestmark = pytest.mark.skipif(
    not _IS_PYTASK_PARALLEL_INSTALLED, reason="Tests require pytask-parallel."
)


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
def test_parallel_parametrization_over_source_files(runner, tmp_path):
    source = """
    import pytask

    @pytask.mark.latex
    @pytask.mark.parametrize(
        "depends_on, produces",
        [(f"document_{i}.tex", f"document_{i}.pdf") for i in range(3)],
    )
    def task_compile_latex_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    for i in range(3):
        latex_source = "\\documentclass{report}\n\\begin{document}.\\end{document}"
        tmp_path.joinpath(f"document_{i}.tex").write_text(textwrap.dedent(latex_source))

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == 0
    duration_normal = time.time() - start

    for name in ["document_1.pdf", "document_2.pdf"]:
        tmp_path.joinpath(name).unlink()

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])
    assert result.exit_code == 0
    duration_parallel = time.time() - start

    assert duration_parallel < duration_normal


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
def test_parallel_parametrization_over_source_file(runner, tmp_path):
    source = """
    import pytask

    @pytask.mark.latex
    @pytask.mark.depends_on("document.tex")
    @pytask.mark.parametrize("produces", [f"document_{i}.pdf" for i in range(4)])
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

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == 0
    duration_normal = time.time() - start

    for name in [f"document_{i}.pdf" for i in range(4)]:
        tmp_path.joinpath(name).unlink()

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])
    assert result.exit_code == 0
    duration_parallel = time.time() - start

    assert duration_parallel < duration_normal
