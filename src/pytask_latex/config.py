"""Configure pytask."""
from _pytask.config import hookimpl


@hookimpl
def pytask_parse_config(config):
    """Register the latex marker in the configuration."""
    config["markers"]["latex"] = "latex: Tasks which compile LaTeX documents."
