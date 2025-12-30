from __future__ import annotations

import textwrap
from pathlib import Path
from typing import cast

import pytest
from pytask import ExitCode
from pytask import Mark
from pytask import Skipped
from pytask import Task
from pytask import build
from pytask import cli

from pytask_latex.execute import pytask_execute_task_setup
from tests.conftest import TEST_RESOURCES
from tests.conftest import needs_latexmk
from tests.conftest import skip_on_github_actions_with_win


def test_pytask_execute_task_setup(monkeypatch):
    """Make sure that the task setup raises errors."""
    # Act like latexmk is installed since we do not test this.
    monkeypatch.setattr(
        "pytask_latex.execute.shutil.which",
        lambda x: None,  # noqa: ARG005
    )
    task = Task(
        base_name="example",
        path=Path(),
        function=lambda: None,
        markers=[Mark("latex", (), {})],
    )
    with pytest.raises(RuntimeError, match="latexmk is needed"):
        pytask_execute_task_setup(task)


@needs_latexmk
@skip_on_github_actions_with_win
def test_compile_latex_document(runner, tmp_path):
    """Test simple compilation."""
    task_source = """
    from pytask import mark

    @mark.latex(script="document.tex", document="document.pdf")
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
def test_compile_latex_document_w_relative(runner, tmp_path):
    """Test simple compilation."""
    task_source = f"""
    from pytask import mark

    @mark.latex(
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
def test_compile_latex_document_to_different_name(runner, tmp_path):
    """Compile a LaTeX document where source and output name differ."""
    task_source = """
    from pytask import mark

    @mark.latex(script="in.tex", document="out.pdf")
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
def test_compile_w_bibliography(runner, tmp_path):
    """Compile a LaTeX document with bibliography."""
    task_source = """
    from pytask import task, mark
    from pathlib import Path

    @task(kwargs={"path": Path("references.bib")})
    @mark.latex(script="in_w_bib.tex", document="out_w_bib.pdf")
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
    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK


@skip_on_github_actions_with_win
def test_raise_error_if_latexmk_is_not_found(tmp_path, monkeypatch):
    task_source = """
    from pytask import mark

    @mark.latex(script="document.tex", document="document.pdf")
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
        "pytask_latex.execute.shutil.which",
        lambda x: None,  # noqa: ARG005
    )

    session = build(paths=tmp_path)

    assert session.exit_code == ExitCode.FAILED
    assert session.execution_reports is not None
    execution_reports = cast("list", session.execution_reports)
    assert isinstance(execution_reports[0].exc_info[1], RuntimeError)


@skip_on_github_actions_with_win
def test_skip_even_if_latexmk_is_not_found(tmp_path, monkeypatch):
    task_source = """
    from pytask import mark

    @mark.skip(reason="Skip it.")
    @mark.latex(script="document.tex", document="document.pdf")
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
        "pytask_latex.execute.shutil.which",
        lambda x: None,  # noqa: ARG005
    )

    session = build(paths=tmp_path)

    assert session.exit_code == ExitCode.OK
    assert session.execution_reports is not None
    execution_reports = cast("list", session.execution_reports)
    assert isinstance(execution_reports[0].exc_info[1], Skipped)


@needs_latexmk
@skip_on_github_actions_with_win
def test_compile_latex_document_w_xelatex(runner, tmp_path):
    task_source = """
    from pytask import mark
    from pytask_latex import compilation_steps

    @mark.latex(
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
def test_compile_latex_document_w_two_dependencies(runner, tmp_path):
    task_source = """
    from pytask import mark
    from pathlib import Path

    @mark.latex(script="document.tex", document="document.pdf")
    def task_compile_document(path: Path = Path("in.txt")):
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
def test_fail_because_script_is_not_latex(tmp_path):
    task_source = """
    from pytask import mark
    from pathlib import Path

    @mark.latex(script="document.text", document="document.pdf")
    def task_compile_document(path: Path = Path("in.txt")):
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

    session = build(paths=tmp_path)
    assert session.exit_code == ExitCode.COLLECTION_FAILED
    assert session.collection_reports is not None
    collection_reports = cast("list", session.collection_reports)
    assert isinstance(collection_reports[0].exc_info[1], ValueError)


@needs_latexmk
@skip_on_github_actions_with_win
def test_compile_document_to_out_if_document_has_relative_resources(tmp_path):
    """Test that motivates the ``"--cd"`` flag.

    If you have a document which includes other resources via relative paths and you
    compile the document to a different output folder, latexmk will not find the
    relative resources. Thus, use the ``"--cd"`` flag to enter the source directory
    before the compilation.

    """
    tmp_path.joinpath("sub", "resources").mkdir(parents=True)

    task_source = """
    from pytask import mark
    from pathlib import Path

    @mark.latex(script="document.tex", document="out/document.pdf")
    def task_compile_document(path: Path = Path("resources/content.tex")):
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

    session = build(paths=tmp_path)
    assert session.exit_code == ExitCode.OK
    assert len(session.tasks) == 1


@needs_latexmk
@skip_on_github_actions_with_win
def test_compile_document_w_wrong_flag(tmp_path):
    """Test that wrong flags raise errors."""
    tmp_path.joinpath("sub").mkdir(parents=True)

    task_source = """
    from pytask import mark
    from pytask_latex import compilation_steps

    @mark.latex(
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

    session = build(paths=tmp_path)
    assert session.exit_code == ExitCode.FAILED
    assert len(session.tasks) == 1
    assert session.execution_reports is not None
    execution_reports = cast("list", session.execution_reports)
    assert isinstance(execution_reports[0].exc_info[1], RuntimeError)


@needs_latexmk
def test_compile_document_w_image(runner, tmp_path):
    task_source = f"""
    from pytask import Product
    import shutil
    from typing_extensions import Annotated
    from pathlib import Path
    from pytask import mark

    def task_create_image(image: Annotated[Path, Product] = Path("image.png")):
        shutil.copy(
            "{TEST_RESOURCES.joinpath("image.png").as_posix()}",
            "{tmp_path.joinpath("image.png").as_posix()}"
        )

    @mark.latex(script="document.tex", document="document.pdf")
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


@needs_latexmk
@skip_on_github_actions_with_win
def test_compile_latex_document_w_multiple_marks(runner, tmp_path):
    """Test simple compilation."""
    task_source = """
    from pytask import mark

    @mark.latex(script="document.text")
    @mark.latex(script="document.tex", document="document.pdf")
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
    assert result.exit_code == ExitCode.COLLECTION_FAILED
    assert "has multiple @pytask.mark.latex marks" in result.output


@needs_latexmk
@skip_on_github_actions_with_win
def test_compile_latex_document_with_wrong_extension(runner, tmp_path):
    """Test simple compilation."""
    task_source = """
    from pytask import mark

    @mark.latex(script="document.tex", document="document.file")
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
    assert result.exit_code == ExitCode.COLLECTION_FAILED
    assert "The 'document' keyword of the" in result.output


@needs_latexmk
@skip_on_github_actions_with_win
def test_compile_w_bibliography_and_keep_bbl(runner, tmp_path):
    """Compile a LaTeX document with bibliography."""
    task_source = """
    from pytask import mark, Product
    from pathlib import Path
    from typing_extensions import Annotated

    @mark.latex(script="in_w_bib.tex", document="out_w_bib.pdf")
    def task_compile_document(
        bibliography: Path = Path("references.bib"),
        bbl: Annotated[Path, Product] = Path("out_w_bib.bbl"),
    ):
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
@pytest.mark.parametrize(
    ("step", "message"),
    [
        ("'unknown'", "Compilation step 'unknown' is unknown."),
        (1, "Compilation step 1 is not a valid step."),
    ],
)
def test_compile_latex_document_w_unknown_compilation_step(
    runner, tmp_path, step, message
):
    """Test simple compilation."""
    task_source = f"""
    from pytask import mark

    @mark.latex(
        script="document.tex",
        document="document.pdf",
        compilation_steps={step},
    )
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
    assert result.exit_code == ExitCode.COLLECTION_FAILED
    assert message in result.output


@needs_latexmk
@skip_on_github_actions_with_win
def test_compile_latex_document_with_task_decorator(runner, tmp_path):
    """Test simple compilation."""
    task_source = """
    from pytask import mark, task

    @mark.latex(script="document.tex", document="document.pdf")
    @task
    def compile_document():
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
def test_use_task_without_path(tmp_path):
    task_source = """
    import pytask
    from pytask import task

    task_compile_document = pytask.mark.latex(
        script="document.tex", document="document.pdf"
    )(
        task()(lambda *x: None)
    )
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
    session = build(paths=tmp_path)
    assert session.exit_code == ExitCode.OK


@needs_latexmk
@skip_on_github_actions_with_win
def test_collect_latex_document_with_product_from_another_task(runner, tmp_path):
    """Test simple compilation."""
    task_source = """
    from pathlib import Path
    from pytask import Product, mark
    from typing_extensions import Annotated

    @mark.latex(script="document.tex", document="document.pdf")
    def task_compile_document(): pass


    def task_create_input_tex(
        path: Annotated[Path, Product] = Path("duesterboys.tex")
    ) -> None:
        path.write_text("weil du meine Mitten extrahierst.")
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    \input{duesseldorf}
    \input{duesterboys}
    \end{document}
    """
    tmp_path.joinpath("document.tex").write_text(textwrap.dedent(latex_source))
    tmp_path.joinpath("duesseldorf.tex").write_text(
        "Bin ich wieder nur so nett zu dir, "
    )

    result = runner.invoke(cli, ["collect", "--nodes", tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK
    assert "duesseldorf.tex" in result.output
    assert "duesterboys.tex" in result.output
