.. image:: https://img.shields.io/pypi/v/pytask-latex?color=blue
    :alt: PyPI
    :target: https://pypi.org/project/pytask-latex

.. image:: https://img.shields.io/pypi/pyversions/pytask-latex
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/pytask-latex

.. image:: https://img.shields.io/conda/vn/conda-forge/pytask-latex.svg
    :target: https://anaconda.org/conda-forge/pytask-latex

.. image:: https://img.shields.io/conda/pn/conda-forge/pytask-latex.svg
    :target: https://anaconda.org/conda-forge/pytask-latex

.. image:: https://img.shields.io/pypi/l/pytask-latex
    :alt: PyPI - License
    :target: https://pypi.org/project/pytask-latex

.. image:: https://img.shields.io/github/workflow/status/pytask-dev/pytask-latex/Continuous%20Integration%20Workflow/main
   :target: https://github.com/pytask-dev/pytask-latex/actions?query=branch%3Amain

.. image:: https://codecov.io/gh/pytask-dev/pytask-latex/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/pytask-dev/pytask-latex

.. image:: https://results.pre-commit.ci/badge/github/pytask-dev/pytask-latex/main.svg
    :target: https://results.pre-commit.ci/latest/github/pytask-dev/pytask-latex/main
    :alt: pre-commit.ci status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

------

pytask-latex
============

pytask-latex allows you to compile LaTeX documents.

It also tries to infer the dependency of the LaTeX document such as included images,
bibliography files and other ``.tex`` files automatically to compile LaTeX documents
when it is possible.


Installation
------------

pytask-latex is available on `PyPI <https://pypi.org/project/pytask-latex>`_ and
`Anaconda.org <https://anaconda.org/conda-forge/pytask-latex>`_. Install it with

.. code-block:: console

    $ pip install pytask-latex

    # or

    $ conda install -c conda-forge pytask-latex

You also need to have ``latexmk`` installed which determines the necessary number of
compilation steps (`here <https://tex.stackexchange.com/a/249243/194826>`_ is an
explanation for what latexmk achieves). To test whether it is installed, type the
following on the command line

.. code-block:: console

    $ latexmk --help

If an error is shown instead of a help page, you can install ``latexmk`` with one of the
popular LaTeX distributions, like `MiKTeX <https://miktex.org/>`_, `TeX Live
<https://www.tug.org/texlive/>`_, `MacTeX <http://www.tug.org/mactex/>`_ or others.


Usage
-----

Compiling your PDF can be as simple as writing the following task.

.. code-block:: python

    import pytask


    @pytask.mark.latex
    @pytask.mark.depends_on("document.tex")
    @pytask.mark.produces("document.pdf")
    def task_compile_latex_document():
        pass

Use ``@pytask.mark.latex`` to indicate that this task compiles a LaTeX document.
``@pytask.mark.depends_on`` points to the source file which is compiled and
``@pytask.mark.produces`` is the path of the compiled PDF.


Multiple dependencies and products
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In general, you might not need to add dependencies other than the main LaTeX file
because pytask-latex tries to infer other dependencies automatically. See the
explanation for ``infer_latex_dependencies`` below.

What happens if you need to add more dependencies to a task because they are not found
automatically? You could use a list, but ensure that the LaTeX document which should be
compiled is in the first position of the list.

.. code-block:: python

    @pytask.mark.latex
    @pytask.mark.depends_on(["document.tex", "image.png"])
    @pytask.mark.produces("document.pdf")
    def task_compile_latex_document():
        pass

If you use a dictionary to pass dependencies to the task, pytask-latex will, first, look
for a ``"source"`` key in the dictionary and, secondly, under the key ``0``.

.. code-block:: python

    @pytask.mark.depends_on({"source": "document.tex", "image": "image.png"})
    def task_compile_document():
        pass


    # or


    @pytask.mark.depends_on({0: "document.tex", "image": "image.png"})
    def task_compile_document():
        pass


    # or two decorators for the function, if you do not assign a name to the image.


    @pytask.mark.depends_on({"source": "document.tex"})
    @pytask.mark.depends_on("image.png")
    def task_compile_document():
        pass

The same applies to the compiled document which is either in the first position, under
the key ``"document"`` or ``0``.


Customizing the compilation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

pytask-latex uses latexmk by default to compile the document because it handles most
use-cases automatically. The following is equivalent to a bare ``@pytask.mark.latex``
decorator.

.. code-block:: python

    @pytask.mark.latex(build_steps="latexmk")
    def task_compile_latex_document():
        ...

The ``@pytask.mark.latex`` decorator has a keyword argument called ``build_steps`` which
accepts which accepts strings or list of strings pointing to internally implemented
build steps. Using strings will use the default configuration of this build step. It is
equivalent to the following.

.. code-block::

    from pytask_latex import build_steps


    @pytask.mark.latex(
        build_steps=build_steps.latexmk(
            options=("--pdf", "--interaction=nonstopmode", "--synctex=1", "--cd")
        )
    )
    def task_compile_latex_document():
        ...

In this example, ``build_steps.latexmk`` is a build step constructor which accepts a set
of options and creates a build step function out of it.

You can pass different options to change the compilation process with latexmk. Here is
an example for generating a ``.dvi``.

.. code-block:: python

    @pytask.mark.latex(
        build_steps=build_steps.latexmk(
            options=("--dvi", "--interaction=nonstopmode", "--synctex=1", "--cd")
        )
    )
    def task_compile_latex_document():
        ...

``build_step.latexmk(options)`` generates a build step which is a function with the
following signature:

.. code-block::

    from pathlib import Path
    import subprocess


    def custom_build_step(path_to_tex: Path, path_to_document: Path) -> None:
        ...
        subproces.run(..., check=True)

Each build step receives the path to the LaTeX source file and the path to the final
document which it uses to call some program on the command line to run another step in
the compilation process.

In the future, pytask-latex will provide more build steps for compiling bibliographies,
glossaries and the like.


Parametrization
~~~~~~~~~~~~~~~

You can also parametrize the compilation, meaning compiling multiple .tex documents
as well as compiling a .tex document with different command line arguments.

The following task compiles two latex documents.

.. code-block:: python

    @pytask.mark.latex
    @pytask.mark.parametrize(
        "depends_on, produces",
        [("document_1.tex", "document_1.pdf"), ("document_2.tex", "document_2.pdf")],
    )
    def task_compile_latex_document():
        pass


If you want to compile the same document with different command line options, you have
to include the latex decorator in the parametrization just like with
``@pytask.mark.depends_on`` and ``@pytask.mark.produces``. Pass a dictionary for
possible build steps and their options.

.. code-block:: python

    @pytask.mark.depends_on("document.tex")
    @pytask.mark.parametrize(
        "produces, latex",
        [
            (
                "document.pdf",
                {
                    "build_steps": build_steps.latexmk(
                        ("--pdf", "--interaction=nonstopmode", "--synctex=1", "--cd")
                    )
                },
            ),
            (
                "document.dvi",
                {
                    "build_steps": build_steps.latexmk(
                        ("--dvi", "--interaction=nonstopmode", "--synctex=1", "--cd")
                    )
                },
            ),
        ],
    )
    def task_compile_latex_document():
        pass


Configuration
-------------

latex_source_key
    If you want to change the name of the key which identifies the source file, change
    the following default configuration in your pytask configuration file.

    .. code-block:: ini

        latex_source_key = source

latex_document_key
    If you want to change the name of the key which identifies the compiled document,
    change the following default configuration in your pytask configuration file.

    .. code-block:: ini

        latex_source_key = source

infer_latex_dependencies
    pytask-latex tries to scan your LaTeX document for included files with the help of
    `latex-dependency-scanner <https://github.com/pytask-dev/latex-dependency-scanner>`_
    if the following configuration value is true which is also the default.

    .. code-block:: ini

        infer_latex_dependencies = true

    Since the package is in its early development phase and LaTeX provides a myriad of
    ways to include files as well as providing shortcuts for paths (e.g.,
    ``\graphicspath``), there are definitely some rough edges left. File an issue here
    or in the other project in case of a problem.


Changes
-------

Consult the `release notes <CHANGES.rst>`_ to find out about what is new.
