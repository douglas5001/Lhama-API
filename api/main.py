from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import settings
from app.database.connections.database import Base, db_instance
from app.controllers.user import user_controller
from app.controllers.auth import auth_controller
from app.middlewares.security_middleware import SecurityMiddleware

app = FastAPI(
    title="Middleware API",
    description="Example of professional structure with FastAPI in layers",
    version="1.0.0",
    docs_url=None if settings.ENVIRONMENT == "PRD" else "/docs",
    redoc_url=None if settings.ENVIRONMENT == "PRD" else "/redoc",
)

# --- MIDDLEWARES ---
# A ordem dos Middlewares importa! 
# Os últimos registrados com `add_middleware` rodam PRIMEIRO (são de Fora para Dentro).

# 1. Loga primeiro toda e qualquer requisição antes mesmo da checagem de Segurança
from app.middlewares.request_logger_middleware import RequestLoggerMiddleware
app.add_middleware(RequestLoggerMiddleware)

app.add_middleware(
    SecurityMiddleware,
    rate_limit_requests=settings.RATE_LIMIT_REQUESTS,
    rate_limit_window=settings.RATE_LIMIT_WINDOW
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_controller.router)
app.include_router(auth_controller.router)

@app.get("/")
def root():
    return {
        "message": "API is online!",
        "db_type": settings.DB
    }
