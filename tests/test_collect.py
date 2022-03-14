from __future__ import annotations

from contextlib import ExitStack as does_not_raise  # noqa: N813

import pytest
from _pytask.mark import Mark
from _pytask.nodes import FilePathNode
from pytask_latex.collect import _get_node_from_dictionary
from pytask_latex.collect import _merge_all_markers
from pytask_latex.collect import pytask_collect_task_teardown


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
@pytest.mark.parametrize("latex_source_key", ["source", "script", "main"])
@pytest.mark.parametrize("latex_document_key", ["document", "compiled_doc"])
@pytest.mark.parametrize("infer_latex_dependencies", [True, False])
def test_pytask_collect_task_teardown(
    tmp_path,
    depends_on,
    produces,
    expectation,
    latex_source_key,
    latex_document_key,
    infer_latex_dependencies,
):
    if infer_latex_dependencies:
        tmp_path.joinpath(depends_on[0]).touch()

    session = DummyClass()
    session.config = {
        "latex_source_key": latex_source_key,
        "latex_document_key": latex_document_key,
        "infer_latex_dependencies": infer_latex_dependencies,
    }

    task = DummyClass()
    task.path = tmp_path / "task_dummy.py"
    task.name = tmp_path.as_posix() + "task_dummy.py::task_dummy"
    task.depends_on = {
        i: FilePathNode.from_path(tmp_path / n) for i, n in enumerate(depends_on)
    }
    task.produces = {
        i: FilePathNode.from_path(tmp_path / n) for i, n in enumerate(produces)
    }
    task.markers = [Mark("latex", (), {})]
    task.function = task_dummy
    task.function.pytaskmark = task.markers

    with expectation:
        pytask_collect_task_teardown(session, task)


@pytest.mark.unit
@pytest.mark.parametrize(
    "obj, key, expected",
    [(1, "asds", 1), (1, None, 1), ({"a": 1}, "a", 1), ({0: 1}, "a", 1)],
)
def test_get_node_from_dictionary(obj, key, expected):
    result = _get_node_from_dictionary(obj, key)
    assert result == expected
