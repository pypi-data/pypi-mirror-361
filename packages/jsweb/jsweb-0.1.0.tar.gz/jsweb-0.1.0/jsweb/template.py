from jinja2 import Environment, FileSystemLoader
import os

# Assuming templates are in ./templates/ relative to current run dir
_env = None


def get_env():
    global _env
    if _env is None:
        _env = Environment(loader=FileSystemLoader(os.path.join(os.getcwd(), "templates")))
    return _env


def add_filter(name, func):
    env = get_env()
    env.filters[name] = func


def render(template_name, context=None):
    if context is None:
        context = {}
    env = get_env()
    template = env.get_template(template_name)
    return template.render(**context)
