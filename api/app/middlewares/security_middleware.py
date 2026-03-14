import time
from collections import defaultdict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

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
        
        # Armazena as requisições em memória { "ip": [timestamp1, timestamp2] }
        # NOTA: Para ambientes em Produção distribuídos (vários works no Docker),
        # o recomendado é usar o Redis para gravar os IPs globalmente.
        self.request_records = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # 1. Função de Segurança de IP (Rate Limiter)
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Limpa os timestamps mais velhos que a janela definida
        self.request_records[client_ip] = [
            ts for ts in self.request_records[client_ip]
            if current_time - ts < self.rate_limit_window
        ]
        
        # Se ultrapassou o limite, bloqueia o acesso
        if len(self.request_records[client_ip]) >= self.rate_limit_requests:
            
            # Loga a tentativa de acesso bloqueada (Aviso de Segurança)
            from app.core.logger import app_logger
            app_logger.warning(f"SECURITY: Bloqueio temporário (Rate Limit). IP: {client_ip} excedeu as requisições permitidas.")
            
            return JSONResponse(
                status_code=429, # HTTP 429 Too Many Requests
                content={
                    "detail": "Too Many Requests",
                    "message": f"IP {client_ip} bloqueado temporariamente por excesso de requisições."
                }
            )
            
        # Registra a requisição atual
        self.request_records[client_ip].append(current_time)
        
        # Deixa a requisição seguir o fluxo normal para as rotas
        response = await call_next(request)
        
        # 2. Outras funções de segurança: Injetando Segurança nos Cabeçalhos da Resposta
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response
