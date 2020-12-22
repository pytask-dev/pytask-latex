from contextlib import ExitStack as does_not_raise  # noqa: N813
from pathlib import Path

import pytest
from _pytask.mark import Mark
from _pytask.nodes import FilePathNode
from pytask_latex.collect import _get_node_from_dictionary
from pytask_latex.collect import _merge_all_markers
from pytask_latex.collect import _prepare_cmd_options
from pytask_latex.collect import DEFAULT_OPTIONS
from pytask_latex.collect import latex
from pytask_latex.collect import pytask_collect_task
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
    "name, expected",
    [("task_dummy", True), ("invalid_name", None)],
)
def test_pytask_collect_task(name, expected):
    session = DummyClass()
    path = Path("some_path")
    task_dummy.pytaskmark = [Mark("latex", (), {})]

    task = pytask_collect_task(session, path, name, task_dummy)

    if expected:
        assert task
    else:
        assert not task


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
def test_pytask_collect_task_teardown(
    depends_on, produces, expectation, latex_source_key, latex_document_key
):
    session = DummyClass()
    session.config = {
        "latex_source_key": latex_source_key,
        "latex_document_key": latex_document_key,
    }

    task = DummyClass()
    task.depends_on = {
        i: FilePathNode(n.split(".")[0], Path(n), Path(n))
        for i, n in enumerate(depends_on)
    }
    task.produces = {
        i: FilePathNode(n.split(".")[0], Path(n), Path(n))
        for i, n in enumerate(produces)
    }
    task.markers = [Mark("latex", (), {})]
    task.function = task_dummy
    task.function.pytaskmark = task.markers

    with expectation:
        pytask_collect_task_teardown(session, task)


@pytest.mark.unit
@pytest.mark.parametrize(
    "obj, key, expected",
    [
        (1, "asds", 1),
        (1, None, 1),
        ({"a": 1}, "a", 1),
        ({0: 1}, "a", 1),
    ],
)
def test_get_node_from_dictionary(obj, key, expected):
    result = _get_node_from_dictionary(obj, key)
    assert result == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "args",
    [
        [],
        ["a"],
        ["a", "b"],
    ],
)
@pytest.mark.parametrize("latex_source_key", ["source", "script"])
@pytest.mark.parametrize("latex_document_key", ["document", "compiled_doc"])
@pytest.mark.parametrize("input_name", ["source", "main"])
@pytest.mark.parametrize("output_name", ["source", "doc"])
def test_prepare_cmd_options(
    args, latex_source_key, latex_document_key, input_name, output_name
):
    session = DummyClass()
    session.config = {
        "latex_source_key": latex_source_key,
        "latex_document_key": latex_document_key,
    }

    dependency = DummyClass()
    dependency.value = Path(f"{input_name}.tex")
    product = DummyClass()
    product.value = Path(f"{output_name}.pdf")
    task = DummyClass()
    task.depends_on = {latex_source_key: dependency}
    task.produces = {latex_document_key: product}
    task.name = "task"

    result = _prepare_cmd_options(session, task, args)

    jobname = (
        []
        if dependency.value.stem == product.value.stem
        else [f"--jobname={product.value.stem}"]
    )

    assert result == ["latexmk", *args] + jobname + [
        "--output-directory=.",
        f"{input_name}.tex",
    ]
