from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.core.logger import app_logger
from app.database.connections.database import db_instance
from app.repositories.user.user_repository import UserRepository
from app.dto.auth.auth_dto import Token, LoginRequest, RefreshRequest

router = APIRouter(prefix="/login", tags=["Authenticacao"])

@router.post("/access-token", response_model=Token)
async def login_access_token(
    login_data: LoginRequest,
    db: AsyncSession = Depends(db_instance.get_db)
) -> dict:
    """
    Endpoint para resgatar um Access Token via E-mail e Senha enviando um JSON no Body.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(email=login_data.email) 
    
    if not user or not user.verify_password(login_data.password):
        app_logger.warning(f"Tentativa de login frustrada para o email: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ou senha Incorretos",
        )
    elif not user.is_active:
        app_logger.warning(f"Tentativa de login frustrada (Usuário Inativo): {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário Inativo",
        )
        
    app_logger.info(f"O usuário {user.email} acabou de logar e emitir um par de Tokens iniciais.")
    
    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
        "token_type": "bearer",
    }

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    request_data: RefreshRequest,
    db: AsyncSession = Depends(db_instance.get_db)
) -> dict:
    """
    Endpoint para gerar um NOVO Access Token usando um Refresh Token válido que ainda não expirou.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodifica o refresh_token validando logo a chave secreta e expiração (7 dias)
        payload = jwt.decode(
            request_data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        
        # Garante que não tão tentando nos enganar com um Token de Acesso vencido
        if payload.get("type") != "refresh":
            raise credentials_exception
            
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except (JWTError, ValueError):
        raise credentials_exception
        
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(email=email)
    
    if not user or not user.is_active:
        raise credentials_exception
        
    app_logger.info(f"O usuário {user.email} acabou usar seu Refresh Token (válido) para estender sua sessão.")

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
        "token_type": "bearer",
    }
