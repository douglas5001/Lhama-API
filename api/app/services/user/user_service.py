from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.user.user_repository import UserRepository
from app.dto.user.user_dto import UserCreate

class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, user_dto: UserCreate):
        existing_user = await self.repository.get_by_email(user_dto.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email already registered in the platform"
            )
        
        return await self.repository.create(user_dto)

    async def list_users(self, skip: int = 0, limit: int = 100):
        return await self.repository.get_all(skip, limit)

    async def get_user_by_id(self, user_id: int):
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        return user
