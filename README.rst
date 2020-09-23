.. image:: https://anaconda.org/pytask/pytask-latex/badges/version.svg
    :target: https://anaconda.org/pytask/pytask-latex

.. image:: https://anaconda.org/pytask/pytask-latex/badges/platforms.svg
    :target: https://anaconda.org/pytask/pytask-latex

.. image:: https://github.com/pytask-dev/pytask-latex/workflows/Continuous%20Integration%20Workflow/badge.svg?branch=main
    :target: https://github.com/pytask-dev/pytask/actions?query=branch%3Amain

.. image:: https://codecov.io/gh/pytask-dev/pytask-latex/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/pytask-dev/pytask-latex

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

------

pytask-latex
============

pytask-latex allows you to compile LaTeX documents.


Installation
------------

Install the plugin with

.. code-block:: console

    $ conda config --add channels conda-forge --add channels pytask
    $ conda install pytask-latex

You also need to have ``latexmk`` installed which determines the necessary number of
compilation steps. To test whether it is installed, type the following on the command
line

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


Note that, the first dependency is always assumed to be the LaTeX document. With
multiple dependencies it may look like this

.. code-block:: python

    @pytask.mark.latex
    @pytask.mark.depends_on("document.tex", "image.png")
    @pytask.mark.produces("document.pdf")
    def task_compile_latex_document():
        pass


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

The options ``jobname``, ``output-directory`` and the ``.tex`` file which will be
compiled are handled by the ``@pytask.mark.depends_on`` and ``@pytask.mark.produces``
markers and cannot be changed.

You can either pass a string or a list of strings to the ``@pytask.mark.latex``
decorator.

For more options and their explanations, visit the `manual for latexmk
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
            ("document.pdf", (["--pdf", "interaction=nonstopmode"],)),
            ("document.dvi", (["--dvi", "interaction=nonstopmode"],)),
        ],
    )
    def task_compile_latex_document():
        pass


Changes
-------

Consult the `release notes <CHANGES.rst>`_ to find out about what is new.
