import shutil

import pytest

needs_latexmk = pytest.mark.skipif(
    shutil.which("latexmk") is None, reason="latexmk needs to be installed."
)
