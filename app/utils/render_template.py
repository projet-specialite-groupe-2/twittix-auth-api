from jinja2 import Environment, FileSystemLoader, select_autoescape


env = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape(["html", "xml", "txt"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_template(template_name: str, **kwargs):
    """Charge et rend un template HTML avec Jinja2."""
    template = env.get_template(template_name)
    return template.render(**kwargs)
