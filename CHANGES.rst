Changes
=======

This is a record of all past pytask-latex releases and what went into them in reverse
chronological order. Releases follow `semantic versioning <https://semver.org/>`_ and
all releases are available on `Anaconda.org
<https://anaconda.org/pytask/pytask-latex>`_.


0.0.11 - 2021-xx-xx
-------------------

- :gh:`18` prepares pytask-latex to be published on PyPI, adds versioneer and more.


0.0.10 - 2021-01-16
-------------------

- :gh:`16` fixes the scanner by keeping only scanned dependencies which exist. Convert
  args to strings.


0.0.9 - 2020-12-28
------------------

- :gh:`12` integrates the latex-dependency-scanner to automatically detect dependencies
  of a LaTeX document and releases v0.0.9.
- :gh:`13` fixes the CI.


0.0.8 - 2020-10-29
------------------

- :gh:`11` makes pytask-latex work with pytask v0.0.9.


0.0.7 - 2020-10-14
------------------

- :gh:`10` fixes error that ``outputdirectory`` has to be relative to latex document due
  to security problems.


0.0.6 - 2020-10-14
------------------

- :gh:`9` fixes the last release and the ``pytask_collect_task_teardown`` call.


0.0.5 - 2020-10-04
------------------

- :gh:`5` fixes some errors in the test suite due to pytask v0.0.6.
- :gh:`6` check that exit codes are equal to zero.
- :gh:`7` fixes the README.
- :gh:`8` works with pytask v0.0.7 and releases v0.0.5.


0.0.4 - 2020-08-21
------------------

- :gh:`4` changes the default options. latexmk will step into the source directory
  before compiling the document. Releases 0.0.4.


0.0.3 - 2020-08-12
------------------

- :gh:`3` prepares pytask-latex for pytask v0.0.5 and releases v0.0.3.


0.0.2 - 2020-07-22
------------------

- :gh:`1` allowed LaTeX tasks to have more than one dependency and allows to parametrize
  over latex options and latex documents. It also prepares release v0.0.2.
- :gh:`2` fixes the release.


0.0.1 - 2020-07-20
------------------

- Releases v0.0.1.
