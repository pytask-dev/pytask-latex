import pytask


@pytask.hookimpl
def pytask_generate_tasks_add_marker(obj, kwargs):
    if callable(obj):
        if "latex" in kwargs:
            pytask.mark.__getattr__("latex")(*kwargs.pop("latex"))(obj)
