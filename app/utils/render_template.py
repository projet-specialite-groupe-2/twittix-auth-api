from jinja2 import Environment, FileSystemLoader, select_autoescape

# Configuration de Jinja2 avec auto-échappement activé pour HTML
env = Environment(
    loader=FileSystemLoader("app/templates"),  # Dossier contenant les templates
    autoescape=select_autoescape(["html", "xml", "txt"]),  # Active autoescape pour HTML
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_template(template_name: str, **kwargs):
    """Charge et rend un template HTML avec Jinja2."""
    template = env.get_template(template_name)
    return template.render(**kwargs)
