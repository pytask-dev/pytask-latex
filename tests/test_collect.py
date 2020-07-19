import pytest
from pytask.mark import Mark
from pytask_latex.collect import _create_command_line_arguments


class DummyTask:
    pass


@pytest.mark.unit
@pytest.mark.parametrize(
    "args, expected",
    [
        ((), ["--pdf", "--interaction=nonstopmode", "--synctex=1"]),
        (("--xelatex",), ["--xelatex"]),
    ],
)
def test_create_command_line_arguments(args, expected):
    task = DummyTask()
    task.markers = [Mark("latex", args, {})]

    out = _create_command_line_arguments(task)

    assert out == expected
