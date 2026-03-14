from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.connections.database import get_db
from app.dto.user.user_dto import UserCreate, UserResponse
from app.services.user.user_service import UserService
from app.core.deps import get_current_user
from app.database.models.user.user_model import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Mantivemos a criação aberta caso você queira permitir cadastros livres.
    service = UserService(db)
    return await service.create_user(user)

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    service = UserService(db)
    return await service.list_users(skip, limit)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    service = UserService(db)
    return await service.get_user_by_id(user_id)
