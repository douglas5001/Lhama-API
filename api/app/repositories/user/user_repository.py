from sqlalchemy.orm import Session
from app.database.models.user.user_model import User
from app.dto.user.user_dto import UserCreate

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(User).offset(skip).limit(limit).all()

    def create(self, user_data: UserCreate):
        hashed_password = User.get_password_hash(user_data.password)

        db_user = User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_password,
            is_active=user_data.is_active,
            is_admin=user_data.is_admin
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
