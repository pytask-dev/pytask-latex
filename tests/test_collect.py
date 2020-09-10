import pytest
from _pytask.mark import Mark
from pytask_latex.collect import _create_command_line_arguments
from pytask_latex.collect import DEFAULT_OPTIONS


class DummyTask:
    pass


@pytest.mark.unit
@pytest.mark.parametrize(
    "args, expected",
    [((), DEFAULT_OPTIONS.copy()), (("--xelatex",), ["--xelatex"])],
)
def test_create_command_line_arguments(args, expected):
    task = DummyTask()
    task.markers = [Mark("latex", args, {})]

    out = _create_command_line_arguments(task)

    assert out == expected
