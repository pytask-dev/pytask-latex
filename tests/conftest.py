import os
import shutil
import sys

import pytest

needs_latexmk = pytest.mark.skipif(
    shutil.which("latexmk") is None, reason="latexmk needs to be installed."
)

skip_on_github_actions_with_win = pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS", False) and sys.platform == "win32"
)
