from sqlalchemy.orm import Session
from app.database.models.usuario_model import Usuario
from app.dto.usuario_dto import UsuarioCreate

class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, usuario_id: int):
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def get_by_email(self, email: str):
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Usuario).offset(skip).limit(limit).all()

    def create(self, dados_usuario: UsuarioCreate):
        db_usuario = Usuario(
            nome=dados_usuario.nome,
            email=dados_usuario.email,
            senha=dados_usuario.senha,
            ativo=dados_usuario.ativo
        )
        self.db.add(db_usuario)
        self.db.commit()
        self.db.refresh(db_usuario)
        return db_usuario
