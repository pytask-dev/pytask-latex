# pytask-latex

[![PyPI](https://img.shields.io/pypi/v/pytask-latex?color=blue)](https://pypi.org/project/pytask-latex)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytask-latex)](https://pypi.org/project/pytask-latex)
[![image](https://img.shields.io/conda/vn/conda-forge/pytask-latex.svg)](https://anaconda.org/conda-forge/pytask-latex)
[![image](https://img.shields.io/conda/pn/conda-forge/pytask-latex.svg)](https://anaconda.org/conda-forge/pytask-latex)
[![PyPI - License](https://img.shields.io/pypi/l/pytask-latex)](https://pypi.org/project/pytask-latex)
[![image](https://img.shields.io/github/actions/workflow/status/pytask-dev/pytask-latex/main.yml?branch=main)](https://github.com/pytask-dev/pytask-latex/actions?query=branch%3Amain)
[![image](https://codecov.io/gh/pytask-dev/pytask-latex/branch/main/graph/badge.svg)](https://codecov.io/gh/pytask-dev/pytask-latex)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pytask-dev/pytask-latex/main.svg)](https://results.pre-commit.ci/latest/github/pytask-dev/pytask-latex/main)
[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

______________________________________________________________________

pytask-latex allows you to compile LaTeX documents with pytask

It also uses
[latex-dependency-scanner](https://github.com/pytask-dev/latex-dependency-scanner) to
automatically infer the dependencies of the LaTeX document such as images,
bibliographies and other `.tex` files which are necessary to compile the LaTeX document.

## Installation

pytask-latex is available on [PyPI](https://pypi.org/project/pytask-latex) and
[Anaconda.org](https://anaconda.org/conda-forge/pytask-latex). Install it with

```console
$ pip install pytask-latex

# or

$ conda install -c conda-forge pytask-latex
```

You also need to have `latexmk` installed which determines the necessary number of
compilation steps ([here](https://tex.stackexchange.com/a/249243/194826) is an
explanation for what latexmk achieves). To test whether it is installed, type the
following on the command line

```console
$ latexmk --help
```

If an error is shown instead of a help page, you can install `latexmk` with one of the
popular LaTeX distributions, like [TeX Live](https://www.tug.org/texlive/),
[MiKTeX](https://miktex.org/), [MacTeX](http://www.tug.org/mactex/) or others.

## Usage

Compiling your PDF can be as simple as writing the following task.

```python
from pathlib import Path
from pytask import mark


@mark.latex(script=Path("document.tex"), document=Path("document.pdf"))
def task_compile_latex_document():
    pass
```

Use `@mark.latex` to indicate that this task compiles a LaTeX document. The `script` and
the `document` keywords provide absolute paths or paths relative to the task module to
the LaTeX file and the compiled document.

### Dependencies and Products

Dependencies and products can be added as usual. Read this
[tutorial](https://pytask-dev.readthedocs.io/en/stable/tutorials/defining_dependencies_products.html).

For example, with the `@task` decorator. (The choice of the kwarg name, here `path`, is
arbitrary.)

```python
from pytask import mark
from pytask import task
from pathlib import Path


@task(kwargs={"path": Path("path_to_another_dependency.tex")})
@mark.latex(script=Path("document.tex"), document=Path("document.pdf"))
def task_compile_latex_document():
    pass
```

### Customizing the compilation

pytask-latex uses latexmk by default to compile the document because it handles most
use-cases automatically. The following is equivalent to a bare `@mark.latex` decorator.

```python
@mark.latex(
    script=Path("document.tex"),
    document=Path("document.pdf"),
    compilation_steps="latexmk",
)
def task_compile_latex_document():
    ...
```

The `@mark.latex` decorator has a keyword argument called `compilation_steps` which
accepts which accepts strings or list of strings pointing to internally implemented
compilation steps. Using strings will use the default configuration of this compilation
step. It is equivalent to the following.

```python
from pytask_latex import compilation_steps as cs


@mark.latex(
    script=Path("document.tex"),
    document=Path("document.pdf"),
    compilation_steps=cs.latexmk(
        options=("--pdf", "--interaction=nonstopmode", "--synctex=1", "--cd")
    ),
)
def task_compile_latex_document():
    ...
```

In this example, `compilation_steps.latexmk` is a compilation step constructor which
accepts a set of options and creates a compilation step function.

You can pass different options to change the compilation process with latexmk. Here is
an example for generating a `.dvi`.

```python
@mark.latex(
    script=Path("document.tex"),
    document=Path("document.pdf"),
    compilation_steps=cs.latexmk(
        options=("--dvi", "--interaction=nonstopmode", "--synctex=1", "--cd")
    ),
)
def task_compile_latex_document():
    ...
```

`compilation_step.latexmk(options)` generates a compilation step which is a function
with the following signature:

```python
from pathlib import Path
import subprocess


def custom_compilation_step(path_to_tex: Path, path_to_document: Path) -> None:
    ...
    subproces.run(..., check=True)
```

You can also pass your custom compilation step with the same signature to the
`compilation_steps` keyword argument of the decorator.

Each compilation step receives the path to the LaTeX source file and the path to the
final document which it uses to call some program on the command line to run another
step in the compilation process.

In the future, pytask-latex will provide more compilation steps for compiling
bibliographies, glossaries and the like.

### Repeating tasks with different scripts or inputs

You can compile multiple LaTeX documents as well as compiling a single `.tex` document
with different command line arguments.

The following task compiles two latex documents.

```python
for i in range(2):

    @task
    @mark.latex(script=Path(f"document_{i}.tex"), document=Path(f"document_{i}.pdf"))
    def task_compile_latex_document():
        pass
```

If you want to compile the same document with different command line options, you have
to include the latex decorator in the parametrization. Pass a dictionary for possible
compilation steps and their options.

```python
for format_ in ("pdf", "dvi"):

    @task
    @mark.latex(
        script=Path("document.tex"),
        document=Path(f"document.{format_}"),
        compilation_steps=cs.latexmk(
            (f"--{format_}", "--interaction=nonstopmode", "--synctex=1", "--cd")
        ),
    )
    def task_compile_latex_document():
        pass
```

## Configuration

*`infer_latex_dependencies`*

pytask-latex tries to scan your LaTeX document for included files with the help of
[latex-dependency-scanner](https://github.com/pytask-dev/latex-dependency-scanner) if
the following configuration value is true which is also the default.

```toml
[tool.pytask.ini_options]
infer_latex_dependencies = true
```

Since the package is in its early development phase and LaTeX provides a myriad of ways
to include files as well as providing shortcuts for paths (e.g., `\graphicspath`), there
are definitely some rough edges left. File an issue here or in the other project in case
of a problem.

## Changes

Consult the [release notes](CHANGES.md) to find out about what is new.
