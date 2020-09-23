import pytest
from _pytask.mark import Mark
from pytask_latex.collect import _merge_all_markers
from pytask_latex.collect import DEFAULT_OPTIONS
from pytask_latex.collect import latex


class DummyTask:
    pass


@pytest.mark.unit
@pytest.mark.parametrize(
    "marks, expected",
    [
        (
            [Mark("latex", ("--a",), {}), Mark("latex", ("--b",), {})],
            Mark("latex", ("--a", "--b"), {}),
        ),
        (
            [Mark("latex", ("--a",), {}), Mark("latex", (), {"latex": "--b"})],
            Mark("latex", ("--a",), {"latex": "--b"}),
        ),
    ],
)
def test_merge_all_markers(marks, expected):
    task = DummyTask()
    task.markers = marks
    out = _merge_all_markers(task)
    assert out == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "latex_args, expected",
    [
        (None, DEFAULT_OPTIONS),
        ("--some-option", ["--some-option"]),
        (["--a", "--b"], ["--a", "--b"]),
    ],
)
def test_latex(latex_args, expected):
    options = latex(latex_args)
    assert options == expected
