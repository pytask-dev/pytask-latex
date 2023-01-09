# Changes

This is a record of all past pytask-latex releases and what went into them in reverse
chronological order. Releases follow [semantic versioning](https://semver.org/) and all
releases are available on [Anaconda.org](https://anaconda.org/conda-forge/pytask-latex).

## 0.3.0 - 2022-12-xx

- {pull}`49` removes support for INI configurations.
- {pull}`50` removes the deprecation message and related code to the old API.

## 0.2.1 - 2022-04-19

- {pull}`40` fixes the error message which advises user to transition to the new
  interface.

## 0.2.0 - 2022-04-16

- {pull}`33` aligns pytask-latex with the pytask v0.2.
- {pull}`34` deprecates the old api.

## 0.1.2 - 2022-03-26

- {pull}`32` implements a new interface to the compilation process which consists of
  composable compilation steps. (Many thanks to `axtimhaus`{.interpreted-text
  role="user"}!:tada:)
- {pull}`36` fixes some issues.
- {pull}`37` updates the release notes.

## 0.1.1 - 2022-02-08

- {pull}`30` skips concurrent CI builds.
- {pull}`31` deprecates Python 3.6 and add support for Python 3.10.

## 0.1.0 - 2021-07-21

- {pull}`23` updates the `README.rst`.
- {pull}`24` replaces versioneer with setuptools-scm.
- {pull}`26` aligns pytask-latex with pytask v0.1.0.

## 0.0.12 - 2021-03-05

- {pull}`19` fixes some post-release issues.
- {pull}`21` adds dependencies to `setup.py` and install via `conda-forge`.

## 0.0.11 - 2021-02-25

- {pull}`18` prepares pytask-latex to be published on PyPI, adds versioneer and more.

## 0.0.10 - 2021-01-16

- {pull}`16` fixes the scanner by keeping only scanned dependencies which exist. Convert
  args to strings.

## 0.0.9 - 2020-12-28

- {pull}`12` integrates the latex-dependency-scanner to automatically detect
  dependencies of a LaTeX document and releases v0.0.9.
- {pull}`13` fixes the CI.

## 0.0.8 - 2020-10-29

- {pull}`11` makes pytask-latex work with pytask v0.0.9.

## 0.0.7 - 2020-10-14

- {pull}`10` fixes error that `outputdirectory` has to be relative to latex document due
  to security problems.

## 0.0.6 - 2020-10-14

- {pull}`9` fixes the last release and the `pytask_collect_task_teardown` call.

## 0.0.5 - 2020-10-04

- {pull}`5` fixes some errors in the test suite due to pytask v0.0.6.
- {pull}`6` check that exit codes are equal to zero.
- {pull}`7` fixes the README.
- {pull}`8` works with pytask v0.0.7 and releases v0.0.5.

## 0.0.4 - 2020-08-21

- {pull}`4` changes the default options. latexmk will step into the source directory
  before compiling the document. Releases 0.0.4.

## 0.0.3 - 2020-08-12

- {pull}`3` prepares pytask-latex for pytask v0.0.5 and releases v0.0.3.

## 0.0.2 - 2020-07-22

- {pull}`1` allowed LaTeX tasks to have more than one dependency and allows to
  parametrize over latex options and latex documents. It also prepares release v0.0.2.
- {pull}`2` fixes the release.

## 0.0.1 - 2020-07-20

- Releases v0.0.1.
