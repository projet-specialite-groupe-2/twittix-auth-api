from fastapi import FastAPI
from .routes.auth import auth_router
from app.database import database
from app.models import models

app = FastAPI(
    title="API d'authentification avec 2FA",
    description="Une API utilisant FastAPI pour l'authentification et 2FA par email.",
)

models.Base.metadata.create_all(bind=database.engine)

# Inclusion des routes d'authentification
app.include_router(auth_router, prefix="/auth", tags=["auth"])
