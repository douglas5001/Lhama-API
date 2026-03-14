from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connections.database import db_instance
from app.database.models.user.user_model import User
from app.dto.auth.auth_dto import TokenPayload
from app.repositories.user.user_repository import UserRepository

# Este objeto diz ao FastAPI que as rotas que dependem disto vão procurar o token no cabeçalho Authorization
# O tokenUrl aponta para a rota que o SwaggerUI vai usar para permitir que as pessoas façam Login
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login/access-token"
)

def get_current_user(
    db: Session = Depends(db_instance.get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependência central para rotas seguras:
    Lê o token JWT enviado no request, decodifica ele e retorna as informações do Usuário vinculado a ele do banco de dados.
    Verifica expiração junto via Logica da biblioteca Jose na linha do decode.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais do token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodifica o token usando a chave secreta e o algoritmo HS256 do config.py
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        
        # Bloqueia se o usuário tentar usar o Refresh Token como se fosse um Access Token
        if payload.get("type") != "access":
            raise credentials_exception
            
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
        token_data = TokenPayload(sub=sub)
        
    except (JWTError, ValueError):
        raise credentials_exception
        
    user_repo = UserRepository(db)
    # Buscamos usando o Subject ("sub") que definimos na hora da criação de salvar o Token, que era o email!
    user = user_repo.get_by_email(email=token_data.sub)
    if not user:
        raise credentials_exception
        
    # Se o administrador desativou essa pessoa (False), ela tenta logar ou acessar rota logada e cai.
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário Inativo")
        
    return user
