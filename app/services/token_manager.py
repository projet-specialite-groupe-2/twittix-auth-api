import jwt
import datetime
import secrets
from app.core.config import settings
from app.core.redis_client import redis_client
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer

temporary_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = "HS256"  # Algorithme de signature sécurisé
TOKEN_EXPIRATION_SECONDS = 3600  # 1 heure d'expiration
TEMPORARY_TOKEN_EXPIRATION_SECONDS = 600  # 1 minute d'expiration
URL_TOKEN_EXPIRATION = 99999999999999999


def generate_auth_token(email):
    """Génère un token JWT et le stocke dans Redis avec expiration."""
    expiration_time = datetime.datetime.now() + datetime.timedelta(
        seconds=TOKEN_EXPIRATION_SECONDS
    )

    payload = {
        "email": email,
        "exp": expiration_time,  # Date d'expiration
        "iat": datetime.datetime.now(),  # Date d'émission
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    redis_client.setex(f"auth_token:{email}", TOKEN_EXPIRATION_SECONDS, token)

    return token


def verify_auth_token(token):
    """Vérifie si le token JWT est valide."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email:
            return redis_client.get(f"auth_token:{email}") == token
    except jwt.PyJWTError:
        return False
    return False


def verify_temporary_auth_token(token: str = Depends(temporary_oauth2_scheme)):
    """Vérifie le token Bearer et retourne l'ID utilisateur."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["email"]
        print(email)
        # Vérifier si le token est toujours valide dans Redis

        stored_token = redis_client.get(f"auth_token:{email}")
        if stored_token and stored_token == token:
            return email
        else:
            raise HTTPException(status_code=401, detail="Token expiré ou invalide.")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide.")


def generate_temporary_token(email):
    """Génère un token JWT temporaire sans stockage."""
    expiration_time = datetime.datetime.now() + datetime.timedelta(
        seconds=TEMPORARY_TOKEN_EXPIRATION_SECONDS
    )

    payload = {
        "email": email + "temporary",
        "exp": expiration_time,  # Date d'expiration
        "iat": datetime.datetime.now(),  # Date d'émission
    }
    temporary_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    redis_client.setex(
        f"auth_token:{email}temporary",
        TEMPORARY_TOKEN_EXPIRATION_SECONDS,
        temporary_token,
    )

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
