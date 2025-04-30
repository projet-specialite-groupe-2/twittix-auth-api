from app.core.config import settings
from app.models.user import BackendUser
import requests


def create_user(user):
    """Crée un nouvel utilisateur via une API externe."""
    response = requests.post(settings.BACKEND_URL + "/api/users", json=user)
    if response.status_code == 201:
        return response.json()
    else:
        return {"error": "Erreur lors de la création de l'utilisateur"}


def patch_user(user_data, email):
    """Met à jour les informations d'un utilisateur via une API externe."""

    user = requests.get(settings.BACKEND_URL + "/api/users?email=" + email)
    user = user.json()
    user = BackendUser(**user[0])

    response = requests.patch(
        settings.BACKEND_URL + "/api/users/" + str(user.id),
        json=user_data,
        headers={"Content-Type": "application/merge-patch+json"},
    )
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Erreur lors de la mise à jour de l'utilisateur"}
