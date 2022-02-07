from __future__ import annotations

import textwrap

import pytest
from conftest import needs_latexmk
from conftest import skip_on_github_actions_with_win
from pytask import main


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
def test_infer_dependencies_from_task(tmp_path):
    task_source = """
    import pytask

    @pytask.mark.latex
    @pytask.mark.depends_on("document.tex")
    @pytask.mark.produces("document.pdf")
    def task_compile_document():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    \input{sub_document}
    \end{document}
    """
    tmp_path.joinpath("document.tex").write_text(textwrap.dedent(latex_source))
    tmp_path.joinpath("sub_document.tex").write_text("Lorem ipsum.")

    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert len(session.tasks) == 1
    assert len(session.tasks[0].depends_on) == 2
