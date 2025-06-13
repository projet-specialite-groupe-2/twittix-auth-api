from app.core.config import settings
from app.models.user import BackendUser
import requests


def create_user(user, token):
    """Crée un nouvel utilisateur via une API externe."""
    headers = {"Authorization": f"Bearer {token}", "X-Api-Key": settings.API_KEY}
    try:
        response = requests.post(
            settings.BACKEND_URL + "/api/users/register", json=user, headers=headers
        )
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Erreur de connexion à l'API : {str(e)}"
        }, response.status_code
    if response.status_code == 201:
        return response.json(), response.status_code
    else:
        try:
            error = response.json().get("detail", "Erreur inconnue")
            return (
                {"error": f"Erreur lors de la création de l'utilisateur: {error}"},
                response.status_code,
            )
        except:
            return (
                {"error": f"Erreur lors de la création de l'utilisateur: {response}"},
                response.status_code,
            )


def patch_user(user_data, email, token):
    """Met à jour les informations d'un utilisateur via une API externe."""
    headers = {"Authorization": f"Bearer {token}", "X-Api-Key": settings.API_KEY}
    user = requests.get(
        settings.BACKEND_URL + "/api/users?email=" + email, headers=headers
    )
    user = user.json()
    user = BackendUser(**user[0])

    response = requests.patch(
        settings.BACKEND_URL + "/api/users/" + str(user.id),
        json=user_data,
        headers={
            "Content-Type": "application/merge-patch+json",
            "Authorization": f"Bearer {token}",
            "X-Api-Key": settings.API_KEY,
        },
    )
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Erreur lors de la mise à jour de l'utilisateur"}
