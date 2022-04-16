from __future__ import annotations

from contextlib import ExitStack as does_not_raise  # noqa: N813

import pytest
from pytask import main
from pytask_latex.config import _convert_truthy_or_falsy_to_bool


@pytest.mark.end_to_end
def test_marker_is_configured(tmp_path):
    session = main({"paths": tmp_path})
    assert "latex" in session.config["markers"]


@pytest.mark.unit
@pytest.mark.parametrize(
    "value, expectation, expected",
    [
        (True, does_not_raise(), True),
        ("True", does_not_raise(), True),
        ("true", does_not_raise(), True),
        ("1", does_not_raise(), True),
        (False, does_not_raise(), False),
        ("False", does_not_raise(), False),
        ("false", does_not_raise(), False),
        ("0", does_not_raise(), False),
        (None, does_not_raise(), None),
        ("None", does_not_raise(), None),
        ("none", does_not_raise(), None),
        ("asklds", pytest.raises(ValueError, match="Input"), None),
    ],
)
def test_convert_truthy_or_falsy_to_bool(value, expectation, expected):
    with expectation:
        result = _convert_truthy_or_falsy_to_bool(value)
        assert result == expected
