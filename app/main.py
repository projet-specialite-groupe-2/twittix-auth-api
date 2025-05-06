from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.auth import auth_router
from app.database import database
from app.models import models

app = FastAPI(
    title="API d'authentification avec 2FA",
    description="Une API utilisant FastAPI pour l'authentification et 2FA par email.",
)

# Configuration du middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)

# Inclusion des routes d'authentification
app.include_router(auth_router, prefix="/auth", tags=["auth"])
