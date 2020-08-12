from _pytask.config import hookimpl


@hookimpl
def pytask_parse_config(config):
    config["markers"]["latex"] = "latex: Tasks which compile LaTeX documents."
