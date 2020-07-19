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

.. code-block:: bash

    $ conda config --add channels conda-forge --add channels pytask
    $ conda install pytask-latex

You also need to have ``latexmk`` installed which determines the necessary number of
compilation steps. To test whether it is installed, type the following on the command
line

.. code-block:: bash

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


To customize the compilation, you can pass some command line arguments to ``latexmk``
via the ``@pytask.mark.latex`` marker. The default is the following.

.. code-block:: python

    @pytask.mark.latex("--pdf", "--interaction=nonstopmode", "--synctex=1")
    def task_compile_latex_document():
        pass

For example, to compile your document with XeLaTeX, use

.. code-block:: python

    @pytask.mark.latex("--xelatex", "--interaction=nonstopmode", "--synctex=1")
    def task_compile_latex_document():
        pass

The options ``jobname``, ``output-directory`` and the ``.tex`` file which will be
compiled are handled by the ``@pytask.mark.depends_on`` and ``@pytask.mark.produces``
markers and cannot be changed.


Changes
-------

Consult the `release notes <CHANGES.rst>`_ to find out about what is new.
