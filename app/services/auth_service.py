from jinja2 import Template
import requests
from app.services.token_manager import generate_token_url
from app.utils.email_sender import send_email
from random import randint
from app.core.config import settings
import secrets

# Simuler une base de données pour stocker les codes 2FA temporairement
two_factor_storage = {}


def authenticate_user(credentials):
    """Vérifie les identifiants via une API externe."""
    response = requests.post(
        settings.BACKEND_URL + "/api/users/active", json=credentials.dict()
    )
    if response.status_code == 200:
        return response.json()
    else:
        return {"result": False}


def send_2fa_code(email):
    """Génère et envoie un code 2FA par email."""
    code = randint(100000, 999999)
    two_factor_storage[email] = code
    send_email(
        to=email,
        subject="Votre code de vérification 2FA",
        html_template_path="2FA_email_template.html",
        code=code,
    )


def verify_2fa_code(email, code):
    """Vérifie si le code 2FA est valide."""
    return two_factor_storage.get(email) == code


def send_confirmation_mail(email, username):
    token = generate_token_url(email)

    confirmation_url = (
        f"{settings.BASE_URL}/auth/confirm-email?token={token}&email={email}"
    )
    print(confirmation_url)
    send_email(
        to=email,
        subject="Confirmation d'email",
        html_template_path="confirmation_mail.html",
        confirmation_url=confirmation_url,
        username=username,
    )

    # Envoyer l'email
