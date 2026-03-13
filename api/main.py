from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import settings
from app.database.connections.database import Base, db_instance
from app.controllers.user import user_controller

app = FastAPI(
    title="Middleware API",
    description="Example of professional structure with FastAPI in layers",
    version="1.0.0",
    docs_url=None if settings.ENVIRONMENT == "PRD" else "/docs",
    redoc_url=None if settings.ENVIRONMENT == "PRD" else "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_controller.router)

@app.get("/")
def root():
    return {
        "message": "API is online!",
        "db_type": settings.DB
    }
