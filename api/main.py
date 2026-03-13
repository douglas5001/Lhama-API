from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import settings
from app.database.conections.database import Base, db_instance
from app.controllers import usuario_controller

app = FastAPI(
    title="Middleware API",
    description="Exemplo de estrutura profissional com FastAPI em camadas",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=db_instance.engine)

app.include_router(usuario_controller.router)

@app.get("/")
def root():
    return {
        "message": "API está no ar!",
        "db_tipo": settings.DB
    }
