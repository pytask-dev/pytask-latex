from __future__ import annotations

import pytest
from pytask import build


@pytest.mark.end_to_end
def test_marker_is_configured(tmp_path):
    session = build(paths=tmp_path)
    assert "latex" in session.config["markers"]
