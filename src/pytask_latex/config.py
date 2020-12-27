"""Configure pytask."""
from _pytask.config import hookimpl
from _pytask.shared import convert_truthy_or_falsy_to_bool
from _pytask.shared import get_first_non_none_value


@hookimpl
def pytask_parse_config(config, config_from_file):
    """Register the latex marker in the configuration."""
    config["markers"]["latex"] = "Tasks which compile LaTeX documents."
    config["latex_source_key"] = config_from_file.get("latex_source_key", "source")
    config["latex_document_key"] = config_from_file.get(
        "latex_document_key", "document"
    )
    config["infer_latex_dependencies"] = get_first_non_none_value(
        config_from_file,
        key="infer_latex_dependencies",
        callback=convert_truthy_or_falsy_to_bool,
        default=True,
    )
