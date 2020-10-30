"""Configure pytask."""
from _pytask.config import hookimpl


@hookimpl
def pytask_parse_config(config, config_from_file):
    """Register the latex marker in the configuration."""
    config["markers"]["latex"] = "Tasks which compile LaTeX documents."
    config["latex_source_key"] = config_from_file.get("latex_source_key", "source")
    config["latex_document_key"] = config_from_file.get(
        "latex_document_key", "document"
    )
