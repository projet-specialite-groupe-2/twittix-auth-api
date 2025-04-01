from fastapi import FastAPI
from .routes.auth import auth_router

app = FastAPI(
    title="API d'authentification avec 2FA",
    description="Une API utilisant FastAPI pour l'authentification et 2FA par email.",
)

# Inclusion des routes d'authentification
app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API"}
