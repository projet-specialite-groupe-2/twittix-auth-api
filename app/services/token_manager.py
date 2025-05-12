import jwt
from datetime import datetime, timedelta

import secrets
from app.core.config import settings
from app.core.redis_client import redis_client
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer

temporary_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"  # Algorithme de signature sécurisé
TOKEN_EXPIRATION_HOURS = 1  # 1 heure d'expiration
TEMPORARY_TOKEN_EXPIRATION_SECONDS = 600  # 1 minute d'expiration
URL_TOKEN_EXPIRATION = 99999999999999999
REFRESH_TOKEN_EXPIRE_DAYS = 10


def generate_auth_token(user_id: int, hashed_password: str):
    payload = {
        "sub": str(user_id),
        "pwd": hashed_password,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS),
        "type": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def generate_refresh_token(user_id: int, hashed_password: str):
    """Génère un token JWT et le stocke dans Redis avec expiration."""
    payload = {
        "sub": str(user_id),
        "pwd": hashed_password,
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh",
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


def verify_auth_token(token):
    """Vérifie si le token JWT est valide."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def verify_temporary_auth_token(token: str = Depends(temporary_oauth2_scheme)):
    """Vérifie le token Bearer et retourne l'ID utilisateur."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide.")


def generate_temporary_token(user_id: int, hashed_password: str):
    """Génère un token JWT et le stocke dans Redis avec expiration."""
    payload = {
        "sub": str(user_id) + "temp",
        "pwd": hashed_password,
        "exp": datetime.utcnow()
        + timedelta(seconds=TEMPORARY_TOKEN_EXPIRATION_SECONDS),
        "type": "refresh",
    }

    temporary_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return temporary_token


def generate_token_url(email):
    token = secrets.token_urlsafe(32)

    redis_client.setex(f"email_confirm:{email}", 3600, token)

    return token


def confirm_token_url(email, token):
    stored_token = redis_client.get(f"email_confirm:{email}")

    if not stored_token:
        raise HTTPException(status_code=400, detail="Lien invalide ou expiré")

    if stored_token != token:
        raise HTTPException(status_code=400, detail="Token incorrect")

    # TODO: Mettre à jour l'utilisateur en base (email confirmé)

    # Supprimer le token de Redis
    redis_client.delete(f"email_confirm:{email}")
