import shutil
import textwrap

import pytest
from pytask.main import main


pytestmark = pytest.mark.skipif(
    shutil.which("latexmk") is None, reason="latexmk needs to be installed."
)


@pytest.mark.end_to_end
def test_parametrized_compilation_of_latex_documents(tmp_path):
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
def test_parametrizing_latex_options(tmp_path):
    task_source = """
    import pytask

    @pytask.mark.parametrize("depends_on, produces, latex", [
        ("document.tex", "document.pdf", ("--interaction=nonstopmode", "--pdf")),
        ("document.tex", "document.dvi", ("--interaction=nonstopmode", "--dvi")),
    ])
    def task_compile_latex_document():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    latex_source = r"""
    \documentclass{report}
    \begin{document}
    I can't stop this feeling. Deep inside of me.
    \end{document}
    """
    tmp_path.joinpath("document.tex").write_text(textwrap.dedent(latex_source))

    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("document.pdf").exists()
    assert tmp_path.joinpath("document.dvi").exists()
