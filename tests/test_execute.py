import shutil
import textwrap

import pytest
from pytask.main import main


pytestmark = pytest.mark.skipif(
    shutil.which("latexmk") is None, reason="latexmk needs to be installed."
)


@pytest.mark.end_to_end
def test_compile_latex_document(tmp_path):
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
    I was tired of my lady
    \end{document}
    """
    tmp_path.joinpath("document.tex").write_text(textwrap.dedent(latex_source))

    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("document.pdf").exists()


@pytest.mark.end_to_end
def test_compile_latex_document_to_different_name(tmp_path):
    task_source = """
    import pytask

    @pytask.mark.latex
    @pytask.mark.depends_on("in.tex")
    @pytask.mark.produces("out.pdf")
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

    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("out.pdf").exists()


@pytest.mark.end_to_end
def test_parametrized_compilation_of_latex_document(tmp_path):
    task_source = """
    import pytask

    @pytask.mark.latex
    @pytask.mark.parametrize("depends_on, produces", [
        ("document_1.tex", "document_1.pdf"),
        ("document_2.tex", "document_2.pdf"),
    ])
    def task_compile_latex_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    for name, content in [
        ("document_1.tex", "Like a worn out recording"),
        ("document_2.tex", "Of a favorite song"),
    ]:
        latex_source = fr"""
        \documentclass{{report}}
        \begin{{document}}
        {content}
        \end{{document}}
        """
        tmp_path.joinpath(name).write_text(textwrap.dedent(latex_source))

    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("document_1.pdf").exists()
    assert tmp_path.joinpath("document_2.pdf").exists()


@pytest.mark.end_to_end
def test_compile_w_bibiliography(tmp_path):
    task_source = """
    import pytask

    @pytask.mark.latex
    @pytask.mark.depends_on("in_w_bib.tex")
    @pytask.mark.produces("out_w_bib.pdf")
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
    \bibliography{bib}
    \end{document}
    """
    tmp_path.joinpath("in_w_bib.tex").write_text(textwrap.dedent(latex_source))

    bib_source = r"""
    @Article{pytask,
      author = {Tobias Raabe},
      title  = {pytask},
      year   = {2020},
    }
    """
    tmp_path.joinpath("bib.bib").write_text(textwrap.dedent(bib_source))

    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("out_w_bib.pdf").exists()


@pytest.mark.end_to_end
def test_raise_error_if_latexmk_is_not_found(tmp_path, monkeypatch):
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
    Ein Fuchs muss tun, was ein Fuchs tun muss. Luxus und Ruhm und rulen bis zum
    Schluss.
    \end{document}
    """
    tmp_path.joinpath("document.tex").write_text(textwrap.dedent(latex_source))

    # Hide latexmk if available.
    monkeypatch.setattr("pytask_latex.execute.shutil.which", lambda x: None)

    session = main({"paths": tmp_path})

    assert session.exit_code == 1
    assert isinstance(session.execution_reports[0].exc_info[1], RuntimeError)


@pytest.mark.end_to_end
def test_compile_latex_document_w_xelatex(tmp_path):
    task_source = """
    import pytask

    @pytask.mark.latex("--xelatex", "--interaction=nonstopmode", "--synctex=1")
    @pytask.mark.depends_on("document.tex")
    @pytask.mark.produces("document.pdf")
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

    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("document.pdf").exists()
