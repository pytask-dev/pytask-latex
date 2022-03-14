"""Contains tests which do not require the plugin and ensure normal execution."""
from __future__ import annotations

import textwrap

import pytest
from pytask import cli
from pytask import ExitCode


@pytest.mark.end_to_end
@pytest.mark.parametrize(
    "dependencies",
    [[], ["in.txt"], ["in_1.txt", "in_2.txt"]],
)
@pytest.mark.parametrize("products", [["out.txt"], ["out_1.txt", "out_2.txt"]])
def test_execution_w_varying_dependencies_products(
    runner, tmp_path, dependencies, products
):
    source = f"""
    import pytask
    from pathlib import Path

    @pytask.mark.depends_on({dependencies})
    @pytask.mark.produces({products})
    def task_dummy(depends_on, produces):
        if isinstance(produces, dict):
            produces = produces.values()
        elif isinstance(produces, Path):
            produces = [produces]
        for product in produces:
            product.touch()
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))
    for dependency in dependencies:
        tmp_path.joinpath(dependency).touch()

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK
