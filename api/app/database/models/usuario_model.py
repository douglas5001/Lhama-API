from sqlalchemy import Column, Integer, String, Boolean
from app.database.conections.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    senha = Column(String(200), nullable=False)
    ativo = Column(Boolean, default=True)
