import smtplib
from email.mime.text import MIMEText
from app.core.config import settings
from jinja2 import Template
from app.utils.render_template import render_template


def send_email(to, subject, html_template_path, **kwargs):
    """Envoie un email en utilisant un fichier HTML et des variables dynamiques."""
    smtp_server = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT
    sender_email = settings.SMTP_USER
    sender_password = settings.SMTP_PASSWORD

    try:
        html_content = render_template(
            html_template_path, **kwargs
        )  # Utilise Jinja2 avec autoescape
    except Exception as e:
        print(f"Erreur lors du rendu du template : {e}")
        return

    msg = MIMEText(html_content, _subtype="plain")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to, msg.as_string())
    except smtplib.SMTPException as e:
        print(f"Erreur SMTP : {e}")
    except Exception as e:
        print(f"Erreur générale : {e}")
