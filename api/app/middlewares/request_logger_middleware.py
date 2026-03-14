import time
from uuid import uuid4
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import app_logger

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Middleware para interceptar cada requisição HTTP da aplicação,
        processá-la e registrar em log:
        - O IP do cliente.
        - O método e caminho da requisição (ex: GET /users).
        - O código de status da resposta (ex: 200, 404, 500).
        - O tempo total que a aplicação levou para processar a resposta (ms).
        """
        
        # Gera um ID único para cada request (útil se você for debugar requisições em paralelo no futuro)
        request_id = str(uuid4())
        
        # Pega as informações básicas da requisição que acabou de chegar
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url_path = request.url.path
        
        # Anota a hora que o request chegou
        start_time = time.time()
        
        app_logger.info(f"[{request_id}] Recebida: {method} {url_path} de IP: {client_ip}")

        try:
            # Passa a requisição adiante para as rotas processarem
            response = await call_next(request)
            
            # Anota a hora que a resposta ficou pronta
            process_time_ms = round((time.time() - start_time) * 1000, 2)
            status_code = response.status_code
            
            # Formata o log de sucesso
            app_logger.info(
                f"[{request_id}] Concluída: {method} {url_path} | Status: {status_code} | Tempo: {process_time_ms}ms"
            )
            
            # Se quiser, podemos adicionar cabeçalhos extras para o cliente final saber o tempo de processamento livremente
            response.headers["X-Process-Time"] = str(process_time_ms)
            
            return response
            
        except Exception as e:
            # Loga qualquer Exceção que a sua aplicação soltar antes de derrubar o Request e soltar 500
            process_time_ms = round((time.time() - start_time) * 1000, 2)
            app_logger.error(
                f"[{request_id}] Falha CRÍTICA: {method} {url_path} | Tempo: {process_time_ms}ms | Erro: {str(e)}"
            )
            raise e
