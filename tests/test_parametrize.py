from __future__ import annotations

import textwrap

import pytest
from pytask import ExitCode
from pytask import build

from tests.conftest import needs_latexmk
from tests.conftest import skip_on_github_actions_with_win


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end()
def test_parametrized_compilation_of_latex_documents_w_loop(tmp_path):
    source = """
    import pytask

    for i in range(1, 3):

        @pytask.mark.task
        @pytask.mark.latex(script=f"document_{i}.tex", document=f"document_{i}.pdf")
        def task_compile_latex_document():
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    for name, content in (
        ("document_1.tex", "Like a worn out recording"),
        ("document_2.tex", "Of a favorite song"),
    ):
        latex_source = rf"""
        \documentclass{{report}}
        \begin{{document}}
        {content}
        \end{{document}}
        """
        tmp_path.joinpath(name).write_text(textwrap.dedent(latex_source))

    session = build(paths=tmp_path)

    assert session.exit_code == ExitCode.OK
    assert tmp_path.joinpath("document_1.pdf").exists()
    assert tmp_path.joinpath("document_2.pdf").exists()


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end()
def test_parametrizing_latex_options_w_loop(tmp_path):
    source = """
    import pytask
    from pytask_latex import compilation_steps as cs

    for ending in ("pdf", "dvi"):

        @pytask.mark.task
        @pytask.mark.latex(
            script="document.tex",
            document=f"document.{ending}",
            compilation_steps=cs.latexmk(
                (f"--{ending}", "--interaction=nonstopmode", "--synctex=1", "--cd")
            )
        )
        def compile_latex_document():
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    I can't stop this feeling. Deep inside of me.
    \end{document}
    """
    tmp_path.joinpath("document.tex").write_text(textwrap.dedent(latex_source))

    session = build(paths=tmp_path)

    assert session.exit_code == ExitCode.OK
    assert tmp_path.joinpath("document.pdf").exists()
    assert tmp_path.joinpath("document.dvi").exists()
