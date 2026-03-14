import redis.asyncio as redis
from app.core.config import settings

# Criação de um Pool de Conexões assíncronas do Redis
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True # Garante que as strings sejam lidas como UTF-8
)

def get_redis() -> redis.Redis:
    """
    Retorna uma instância da conexão Assíncrona com o Redis utilizando o Pool estabelecido.
    A mesma premissa do get_db: O pool gerencia o reaproveitamento e fechamento por conta própria sob alta carga.
    """
    return redis.Redis(connection_pool=redis_pool)
