from fastapi import APIRouter, Depends, HTTPException, status
from app.services.auth_service import (
    authenticate_user,
    send_2fa_code,
    send_confirmation_mail,
    verify_2fa_code,
)
from app.models.user import (
    Token,
    TokenAndRefresh,
    UserCredentials,
    TwoFactorCode,
    temporary_token_response,
    token_is_valid_response,
)
from app.services.token_manager import (
    confirm_token_url,
    generate_auth_token,
    generate_refresh_token,
    generate_temporary_token,
    verify_temporary_auth_token,
    verify_auth_token,
)
from app.services.user_manager import create_user, patch_user
from app.database import database
from app.schema.schema import *
from sqlalchemy.orm import Session
from app.models.models import User
from passlib.hash import bcrypt

auth_router = APIRouter()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@auth_router.post("/login", response_model=temporary_token_response)
async def login(credentials: UserCredentials, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=credentials.email).first()
    if not user or not bcrypt.verify(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides"
        )

    user_authenticate = authenticate_user(
        {"email": credentials.email, "password": "test1234"}
    )
    if not user_authenticate["result"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User is blocked"
        )
    # Envoi du code 2FA
    send_2fa_code(credentials.email)

    temporary_token = generate_temporary_token(user.id, user.hashed_password)
    return {"temporary_token": temporary_token}


@auth_router.post("/verify-2fa", response_model=TokenAndRefresh)
async def verify_2fa(
    data: TwoFactorCode,
    payload: str = Depends(verify_temporary_auth_token),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter_by(id=payload["sub"].replace("temp", "")).first()
    if not user or user.email != data.email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur non trouvé"
        )

    if verify_2fa_code(data.email, data.code):
        token = generate_auth_token(user.id, user.hashed_password)
        refresh_token = generate_refresh_token(user.id, user.hashed_password)
        return {"token": token, "refresh_token": refresh_token}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Code 2FA invalide"
        )


@auth_router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Enregistrement de l'utilisateur dans la base de données
    db.query(User).filter_by(email=user.email).delete()
    existing_user = db.query(User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    hashed_pw = bcrypt.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(db_user)

    db.commit()
    db.refresh(db_user)
    token = generate_auth_token(db_user.id, db_user.hashed_password)
    response, code = create_user(
        {
            "email": user.email,
            "username": user.username,
            "birthdate": user.birthdate,
            "password": user.password,
        },
        token,
    )
    if code != 201:
        db.query(User).filter_by(email=user.email).delete()
        db.commit()
        raise HTTPException(
            status_code=code,
            detail=response,
        )

    send_confirmation_mail(user.email)
    return db_user


@auth_router.get("/confirm-email")
async def confirm_email(token: str, email: str, db: Session = Depends(get_db)):
    confirm_token_url(email, token)
    patch_user_data = {"active": True}
    user = db.query(User).filter_by(email=email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé"
        )
    token = generate_auth_token(user.id, user.hashed_password)
    result = patch_user(patch_user_data, email, token=token)
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"]
        )
    else:
        return {
            "message": "Email confirmé avec succès ! Vous pouvez maintenant vous connecter."
        }


@auth_router.post("/token-is-valid", response_model=token_is_valid_response)
async def token_is_valid(token: Token, db: Session = Depends(get_db)):
    """
    Vérifie si le token est valide
    """

    payload = verify_auth_token(token.token)

    if payload.get("type") == "refresh":
        raise HTTPException(status_code=400, detail="Invalid token type")

    user_id = int(payload["sub"])
    hashed_password = payload["pwd"]

    user = db.query(User).filter_by(id=user_id).first()
    if not user or user.hashed_password != hashed_password:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"email": user.email, "token": token.token, "exp_time": payload["exp"]}


@auth_router.post("/token/refresh", response_model=Token)
def refresh_token(refresh_token: Token, db: Session = Depends(get_db)):
    try:
        payload = verify_auth_token(refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Invalid token type")

    user_id = int(payload["sub"])
    hashed_password = payload["pwd"]

    user = db.query(User).filter_by(id=user_id).first()
    if not user or user.hashed_password != hashed_password:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = generate_auth_token(user.id, user.hashed_password)
    return {
        "token": new_access_token,
    }
