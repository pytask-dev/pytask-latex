from __future__ import annotations

import textwrap

import pytest
from conftest import needs_latexmk
from conftest import skip_on_github_actions_with_win
from pytask import ExitCode
from pytask import main


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
@pytest.mark.parametrize("infer_dependencies", ["true", "false"])
@pytest.mark.parametrize(
    "config_file, content",
    [
        ("pytask.ini", "[pytask]\ninfer_latex_dependencies = {}"),
        ("pyproject.toml", "[tool.pytask.ini_options]\ninfer_latex_dependencies = {}"),
    ],
)
def test_infer_dependencies_from_task(
    tmp_path, infer_dependencies, config_file, content
):
    task_source = """
    import pytask

    @pytask.mark.latex(script="document.tex", document="document.pdf")
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

    tmp_path.joinpath(config_file).write_text(content.format(infer_dependencies))

    session = main({"paths": tmp_path})
    assert session.exit_code == ExitCode.OK
    assert len(session.tasks) == 1
    if infer_dependencies:
        assert len(session.tasks[0].depends_on) == 2
    else:
        assert len(session.tasks[0].depends_on) == 1
