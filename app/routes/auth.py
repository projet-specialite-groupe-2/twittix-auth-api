import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.return_serializer import (
    temporary_token_response,
    token_is_valid_response,
)
from app.services.auth_service import (
    authenticate_user,
    send_2fa_code,
    send_confirmation_mail,
    verify_2fa_code,
)
from app.models.user import Token, UserCredentials, TwoFactorCode
from app.services.token_manager import (
    confirm_token_url,
    generate_auth_token,
    generate_temporary_token,
    verify_auth_token,
    verify_temporary_auth_token,
)
from app.services.user_manager import create_user, patch_user

auth_router = APIRouter()


@auth_router.post("/login", response_model=temporary_token_response)
async def login(credentials: UserCredentials):
    user = authenticate_user(credentials)
    if not user["result"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides"
        )
    # Envoi du code 2FA
    send_2fa_code(credentials.email)

    temporary_token = generate_temporary_token(credentials.email)
    return {"temporary_token": temporary_token}


@auth_router.post("/verify-2fa", response_model=Token)
async def verify_2fa(
    data: TwoFactorCode, token: str = Depends(verify_temporary_auth_token)
):

    if verify_2fa_code(data.email, data.code):
        token = generate_auth_token(data.email)
        return {"token": token}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Code 2FA invalide"
        )


@auth_router.post("/register")
async def register_user(credentials: UserCredentials):
    # Enregistrement de l'utilisateur dans la base de données
    response = create_user(credentials)

    if "error" in response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=response["error"]
        )

    send_confirmation_mail(credentials.email, credentials.username)
    return {"message": "Utilisateur créé avec succès"}


@auth_router.get("/confirm-email")
async def confirm_email(token: str, email: str):
    confirm_token_url(email, token)
    patch_user_data = {"active": True}
    result = patch_user(patch_user_data, email)
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"]
        )
    else:
        return {
            "message": "Email confirmé avec succès ! Vous pouvez maintenant vous connecter."
        }


@auth_router.post("/token-is-valid", response_model=token_is_valid_response)
async def token_is_valid(token: Token):
    """
    Vérifie si le token est valide
    """

    result = verify_auth_token(token.token)

    if not verify_auth_token(token.token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide"
        )

    return {"email": result["email"], "token": token.token, "exp_time": result["exp"]}
