import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.database.connections.redis_connection import get_redis
from app.core.logger import app_logger

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit_requests: int = 100, rate_limit_window: int = 60):
        """
        Middleware com funções de segurança.
        
        :param rate_limit_requests: Quantidade de solicitações permitidas por IP.
        :param rate_limit_window: Janela de tempo (em segundos) para validação.
        """
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_key = f"global_rate_limit:{client_ip}"
        
        redis_client = get_redis()
        
        try:
            tentativas = await redis_client.incr(rate_limit_key)
            
            if tentativas == 1:
                await redis_client.expire(rate_limit_key, self.rate_limit_window)
                
            if tentativas > self.rate_limit_requests:
                app_logger.warning(f"SECURITY: Bloqueio temporário (Rate Limit Global Redis). IP: {client_ip} excedeu as requisições permitidas ({self.rate_limit_requests}).")
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too Many Requests",
                        "message": f"IP {client_ip} bloqueado temporariamente por excesso de requisições globais."
                    }
                )
        except Exception as e:
            app_logger.error(f"Erro na conexão com Redis no SecurityMiddleware: {e}")
        
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response
