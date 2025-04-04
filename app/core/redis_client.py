import redis
from app.core.config import settings

# Connexion au serveur Redis
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,  # Permet de lire les valeurs en string
)
