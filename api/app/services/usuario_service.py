from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.usuario_repository import UsuarioRepository
from app.dto.usuario_dto import UsuarioCreate

class UsuarioService:
    def __init__(self, db: Session):
        self.repository = UsuarioRepository(db)

    def criar_usuario(self, usuario_dto: UsuarioCreate):
        # Verifica regra de negócio (e-mail duplicado)
        usuario_existente = self.repository.get_by_email(usuario_dto.email)
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email já cadastrado na plataforma"
            )
        
        # Em um cenário real, criptografaríamos a senha aqui
        # usuario_dto.senha = get_password_hash(usuario_dto.senha)
        
        return self.repository.create(usuario_dto)

    def listar_usuarios(self, skip: int = 0, limit: int = 100):
        return self.repository.get_all(skip, limit)

    def obter_usuario_por_id(self, usuario_id: int):
        usuario = self.repository.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Usuário não encontrado"
            )
        return usuario
