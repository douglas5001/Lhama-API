from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user.user_repository import UserRepository
from app.dto.user.user_dto import UserCreate

class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def create_user(self, user_dto: UserCreate):
        # Check business rule (duplicate e-mail)
        existing_user = self.repository.get_by_email(user_dto.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email already registered in the platform"
            )
        
        # In a real scenario, we would encrypt the password here
        # user_dto.password = get_password_hash(user_dto.password)
        
        return self.repository.create(user_dto)

    def list_users(self, skip: int = 0, limit: int = 100):
        return self.repository.get_all(skip, limit)

    def get_user_by_id(self, user_id: int):
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        return user
