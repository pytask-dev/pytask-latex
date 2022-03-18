from __future__ import annotations

from contextlib import ExitStack as does_not_raise  # noqa: N813

import pytest
from pytask_latex.collect import latex


@pytest.mark.unit
@pytest.mark.parametrize(
    "kwargs, expectation, expected",
    [
        ({}, pytest.raises(RuntimeError, match="The old syntax"), None),
        (
            {"document": "document.pdf"},
            pytest.raises(RuntimeError, match="The old syntax"),
            None,
        ),
        (
            {"script": "script.tex"},
            pytest.raises(RuntimeError, match="The old syntax"),
            None,
        ),
        (
            {"script": "script.tex", "document": "document.pdf"},
            does_not_raise(),
            ("script.tex", "document.pdf", None),
        ),
        (
            {
                "script": "script.tex",
                "document": "document.pdf",
                "compilation_steps": "latexmk",
            },
            does_not_raise(),
            ("script.tex", "document.pdf", "latexmk"),
        ),
    ],
)
def test_latex(kwargs, expectation, expected):
    with expectation:
        result = latex(**kwargs)
        assert result == expected
