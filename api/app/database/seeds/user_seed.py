import logging
from sqlalchemy.orm import Session
from app.database.models.user.user_model import User
from app.dto.user.user_dto import UserCreate
from app.repositories.user.user_repository import UserRepository

logger = logging.getLogger(__name__)

def seed_users(db: Session):
    repository = UserRepository(db)
    
    # Check if we already have the admin user
    admin_email = "admin@example.com"
    existing_user = repository.get_by_email(admin_email)
    
    if not existing_user:
        logger.info(f"Seeding user: {admin_email}")
        user_data = UserCreate(
            name="Admin User",
            email=admin_email,
            password="adminpassword", # In production, this must be a hash!
            is_active=True,
            is_admin=True
        )
        repository.create(user_data)
        logger.info("Admin user seeded successfully!")
    else:
        logger.info(f"User {admin_email} already exists. Skipping seed.")
