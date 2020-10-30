.. image:: https://anaconda.org/pytask/pytask-latex/badges/version.svg
    :target: https://anaconda.org/pytask/pytask-latex

.. image:: https://anaconda.org/pytask/pytask-latex/badges/platforms.svg
    :target: https://anaconda.org/pytask/pytask-latex

.. image:: https://github.com/pytask-dev/pytask-latex/workflows/Continuous%20Integration%20Workflow/badge.svg?branch=main
    :target: https://github.com/pytask-dev/pytask-latex/actions?query=branch%3Amain

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

The options ``jobname``, ``output-directory`` and the ``.tex`` file which will be
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
                (["--pdf", "--interaction=nonstopmode", "--synctex=1", "--cd"],),
            ),
            (
                "document.dvi",
                (["--dvi", "--interaction=nonstopmode", "--synctex=1", "--cd"],),
            ),
        ],
    )
    def task_compile_latex_document():
        pass


Configuration
-------------

If you want to change the names of the keys which identify the source file and the
compiled document, change the following default configuration in your pytask
configuration file.

.. code-block:: ini

    latex_source_key = source
    latex_document_key = document



Changes
-------

Consult the `release notes <CHANGES.rst>`_ to find out about what is new.
