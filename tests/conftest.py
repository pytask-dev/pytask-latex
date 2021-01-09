"""Configuration file for pytest."""
import os
import shutil
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner


TEST_RESOURCES = Path(__file__).parent / "resources"


needs_latexmk = pytest.mark.skipif(
    shutil.which("latexmk") is None, reason="latexmk needs to be installed."
)

skip_on_github_actions_with_win = pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS", "false") == "true" and sys.platform == "win32",
    reason="TinyTeX does not work on Windows.",
)


@pytest.fixture()
def runner():
    return CliRunner()
