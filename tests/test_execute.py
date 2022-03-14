from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from conftest import needs_latexmk
from conftest import skip_on_github_actions_with_win
from conftest import TEST_RESOURCES
from pytask import cli
from pytask import ExitCode
from pytask import main
from pytask import Mark
from pytask import Task
from pytask_latex.execute import pytask_execute_task_setup


@pytest.mark.unit
def test_pytask_execute_task_setup(monkeypatch):
    """Make sure that the task setup raises errors."""
    # Act like latexmk is installed since we do not test this.
    monkeypatch.setattr(
        "pytask_latex.execute.shutil.which", lambda x: None  # noqa: U100
    )
    task = Task(
        base_name="example", path=Path(), function=None, markers=[Mark("latex", (), {})]
    )
    with pytest.raises(RuntimeError, match="latexmk is needed"):
        pytask_execute_task_setup(task)


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
def test_compile_latex_document(runner, tmp_path):
    """Test simple compilation."""
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
    I was tired of my lady
    \end{document}
    """
    tmp_path.joinpath("document.tex").write_text(textwrap.dedent(latex_source))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
def test_compile_latex_document_w_relative(runner, tmp_path):
    """Test simple compilation."""
    task_source = f"""
    import pytask

    @pytask.mark.latex(
        script="document.tex",
        document="{tmp_path.joinpath("bld", "document.pdf").as_posix()}"
    )
    def task_compile_document():
        pass

    """
    tmp_path.joinpath("bld").mkdir()
    tmp_path.joinpath("src").mkdir()
    tmp_path.joinpath("src", "task_dummy.py").write_text(textwrap.dedent(task_source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    I was tired of my lady
    \end{document}
    """
    tmp_path.joinpath("src", "document.tex").write_text(textwrap.dedent(latex_source))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
def test_compile_latex_document_to_different_name(runner, tmp_path):
    """Compile a LaTeX document where source and output name differ."""
    task_source = """
    import pytask

    @pytask.mark.latex(script="in.tex", document="out.pdf")
    def task_compile_document():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    We'd been together too long
    \end{document}
    """
    tmp_path.joinpath("in.tex").write_text(textwrap.dedent(latex_source))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
def test_compile_w_bibliography(runner, tmp_path):
    """Compile a LaTeX document with bibliography."""
    task_source = """
    import pytask

    @pytask.mark.latex(script="in_w_bib.tex", document="out_w_bib.pdf")
    @pytask.mark.depends_on("references.bib")
    def task_compile_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    latex_source = r"""
    \documentclass{report}
    \usepackage{natbib}
    \begin{document}
    \cite{pytask}
    \bibliographystyle{plain}
    \bibliography{references}
    \end{document}
    """
    tmp_path.joinpath("in_w_bib.tex").write_text(textwrap.dedent(latex_source))

    bib_source = r"""
    @Article{pytask,
      author  = {Tobias Raabe},
      title   = {pytask},
      journal = {Unpublished},
      year    = {2020},
    }
    """
    tmp_path.joinpath("references.bib").write_text(textwrap.dedent(bib_source))

    session = runner.invoke(cli, [tmp_path.as_posix()])
    assert session.exit_code == ExitCode.OK


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
def test_raise_error_if_latexmk_is_not_found(tmp_path, monkeypatch):
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
    Ein Fuchs muss tun, was ein Fuchs tun muss. Luxus und Ruhm und rulen bis zum
    Schluss.
    \end{document}
    """
    tmp_path.joinpath("document.tex").write_text(textwrap.dedent(latex_source))

    # Hide latexmk if available.
    monkeypatch.setattr(
        "pytask_latex.execute.shutil.which", lambda x: None  # noqa: U100
    )

    session = main({"paths": tmp_path})

    assert session.exit_code == ExitCode.FAILED
    assert isinstance(session.execution_reports[0].exc_info[1], RuntimeError)


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
def test_compile_latex_document_w_xelatex(runner, tmp_path):
    task_source = """
    import pytask
    from pytask_latex import compilation_steps

    @pytask.mark.latex(
        script="document.tex",
        document="document.pdf",
        compilation_steps=compilation_steps.latexmk(
            ["--xelatex", "--interaction=nonstopmode", "--synctex=1", "--cd"]
        )
    )
    def task_compile_document():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    I got, I got, I got, I got loyalty, got royalty inside my DNA.
    \end{document}
    """
    tmp_path.joinpath("document.tex").write_text(textwrap.dedent(latex_source))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("document.pdf").exists()


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
def test_compile_latex_document_w_two_dependencies(runner, tmp_path):
    task_source = """
    import pytask

    @pytask.mark.latex(script="document.tex", document="document.pdf")
    @pytask.mark.depends_on("in.txt")
    def task_compile_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    Mother earth is pregnant for the third time.
    \end{document}
    """
    tmp_path.joinpath("document.tex").write_text(textwrap.dedent(latex_source))
    tmp_path.joinpath("in.txt").touch()

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("document.pdf").exists()


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
def test_fail_because_script_is_not_latex(tmp_path):
    task_source = """
    import pytask

    @pytask.mark.latex(script="document.text", document="document.pdf")
    @pytask.mark.depends_on("in.txt")
    def task_compile_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    For y'all have knocked her up
    \end{document}
    """
    tmp_path.joinpath("document.tex").write_text(textwrap.dedent(latex_source))
    tmp_path.joinpath("in.txt").touch()

    session = main({"paths": tmp_path})
    assert session.exit_code == ExitCode.COLLECTION_FAILED
    assert isinstance(session.collection_reports[0].exc_info[1], ValueError)


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
def test_compile_document_to_out_if_document_has_relative_resources(tmp_path):
    """Test that motivates the ``"--cd"`` flag.

    If you have a document which includes other resources via relative paths and you
    compile the document to a different output folder, latexmk will not find the
    relative resources. Thus, use the ``"--cd"`` flag to enter the source directory
    before the compilation.

    """
    tmp_path.joinpath("sub", "resources").mkdir(parents=True)

    task_source = """
    import pytask

    @pytask.mark.latex(script="document.tex", document="out/document.pdf")
    @pytask.mark.depends_on("resources/content.tex")
    def task_compile_document():
        pass
    """
    tmp_path.joinpath("sub", "task_dummy.py").write_text(textwrap.dedent(task_source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    \input{resources/content}
    \end{document}
    """
    tmp_path.joinpath("sub", "document.tex").write_text(textwrap.dedent(latex_source))

    resources = r"""
    In Ottakring, in Ottakring, wo das Bitter so viel suesser schmeckt als irgendwo in
    Wien.
    """
    tmp_path.joinpath("sub", "resources", "content.tex").write_text(resources)

    session = main({"paths": tmp_path})
    assert session.exit_code == ExitCode.OK
    assert len(session.tasks) == 1


@needs_latexmk
@skip_on_github_actions_with_win
@pytest.mark.end_to_end
def test_compile_document_w_wrong_flag(tmp_path):
    """Test that wrong flags raise errors."""
    tmp_path.joinpath("sub").mkdir(parents=True)

    task_source = """
    import pytask
    from pytask_latex import compilation_steps

    @pytask.mark.latex(
        script="document.tex",
        document="out/document.pdf",
        compilation_steps=compilation_steps.latexmk("--wrong-flag"),
    )
    def task_compile_document():
        pass

    """
    tmp_path.joinpath("sub", "task_dummy.py").write_text(textwrap.dedent(task_source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    The book of love is long and boring ...
    \end{document}
    """
    tmp_path.joinpath("sub", "document.tex").write_text(textwrap.dedent(latex_source))

    session = main({"paths": tmp_path})
    assert session.exit_code == ExitCode.FAILED
    assert len(session.tasks) == 1
    assert isinstance(session.execution_reports[0].exc_info[1], RuntimeError)


@needs_latexmk
@pytest.mark.end_to_end
def test_compile_document_w_image(runner, tmp_path):
    task_source = f"""
    import pytask
    import shutil

    @pytask.mark.produces("image.png")
    def task_create_image():
        shutil.copy(
            "{TEST_RESOURCES.joinpath("image.png").as_posix()}",
            "{tmp_path.joinpath("image.png").as_posix()}"
        )

    @pytask.mark.latex(script="document.tex", document="document.pdf")
    def task_compile_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    latex_source = r"""
    \documentclass{report}
    \usepackage{graphicx}
    \begin{document}
    \includegraphics{image}
    \end{document}
    """
    tmp_path.joinpath("document.tex").write_text(textwrap.dedent(latex_source))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK
