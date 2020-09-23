from contextlib import ExitStack as does_not_raise  # noqa: N813
from pathlib import Path

import pytest
from _pytask.mark import Mark
from _pytask.nodes import FilePathNode
from pytask_latex.collect import _merge_all_markers
from pytask_latex.collect import DEFAULT_OPTIONS
from pytask_latex.collect import latex
from pytask_latex.collect import pytask_collect_task


class DummyClass:
    pass


def task_dummy():
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
    task = DummyClass()
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


@pytest.mark.unit
@pytest.mark.parametrize(
    "depends_on, produces, expectation",
    [
        (["document.tex"], ["document.pdf"], does_not_raise()),
        (["document.tex"], ["document.ps"], does_not_raise()),
        (["document.tex"], ["document.dvi"], does_not_raise()),
        (["document.txt"], ["document.pdf"], pytest.raises(ValueError)),
        (["document.txt"], ["document.ps"], pytest.raises(ValueError)),
        (["document.txt"], ["document.dvi"], pytest.raises(ValueError)),
        (["document.tex"], ["document.txt"], pytest.raises(ValueError)),
        (["document.txt", "document.tex"], ["document.pdf"], pytest.raises(ValueError)),
        (["document.tex"], ["document.out", "document.pdf"], pytest.raises(ValueError)),
    ],
)
def test_pytask_collect_task(monkeypatch, depends_on, produces, expectation):
    session = DummyClass()
    path = Path("some_path")

    task_dummy.pytaskmark = [Mark("latex", (), {})] + [
        Mark("depends_on", tuple(d for d in depends_on), {}),
        Mark("produces", tuple(d for d in produces), {}),
    ]

    task = DummyClass()
    task.depends_on = [FilePathNode(n.split(".")[0], Path(n)) for n in depends_on]
    task.produces = [FilePathNode(n.split(".")[0], Path(n)) for n in produces]
    task.markers = [Mark("latex", (), {})]
    task.function = task_dummy

    monkeypatch.setattr(
        "pytask_latex.collect.PythonFunctionTask.from_path_name_function_session",
        lambda *x: task,
    )

    with expectation:
        pytask_collect_task(session, path, "task_dummy", task_dummy)
