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
bibliography files and other .tex files automatically to compile LaTeX documents when it
is possible.


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

Here is an example where you want to compile ``document.tex`` to a PDF.

.. code-block:: python

    import pytask


    @pytask.mark.latex
    @pytask.mark.depends_on("document.tex")
    @pytask.mark.produces("document.pdf")
    def task_compile_latex_document():
        pass

When the task is executed, you find a ``document.pdf`` in the same folder as your
``document.text``, but you could also compile the report into a another folder by
changing the path in ``produces``.


Multiple dependencies and products
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What happens if a task has more dependencies? Using a list, the LaTeX document which
should be compiled must be found in the first position of the list.

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


Command Line Arguments
~~~~~~~~~~~~~~~~~~~~~~

To customize the compilation, you can pass some command line arguments to ``latexmk``
via the ``@pytask.mark.latex`` marker. The default is the following.

.. code-block:: python

    @pytask.mark.latex(["--pdf", "--interaction=nonstopmode", "--synctex=1", "--cd"])
    def task_compile_latex_document():
        pass

For example, to compile your document with XeLaTeX, use

.. code-block:: python

    @pytask.mark.latex(["--xelatex", "--interaction=nonstopmode"])
    def task_compile_latex_document():
        pass

The options ``--jobname``, ``--output-directory`` and the ``.tex`` file which will be
compiled are automatically handled and inferred from the ``@pytask.mark.depends_on`` and
``@pytask.mark.produces`` markers.

The ``@pytask.mark.latex`` accepts both, a string or a list of strings with options.

For more options and their explanations, visit the `latexmk manual
<https://man.cx/latexmk>`_ or type the following commands.

.. code-block:: console

    $ latexmk -h
    $ latexmk -showextraoptions


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
``@pytask.mark.depends_on`` and ``@pytask.mark.produces``.

.. code-block:: python

    @pytask.mark.depends_on("document.tex")
    @pytask.mark.parametrize(
        "produces, latex",
        [
            (
                "document.pdf",
                ("--pdf", "--interaction=nonstopmode", "--synctex=1", "--cd"),
            ),
            (
                "document.dvi",
                ("--dvi", "--interaction=nonstopmode", "--synctex=1", "--cd"),
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
