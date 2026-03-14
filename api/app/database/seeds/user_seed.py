from app.core.logger import app_logger as logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user.user_model import User
from app.dto.user.user_dto import UserCreate
from app.repositories.user.user_repository import UserRepository

async def seed_users(db: AsyncSession):
    repository = UserRepository(db)
    
    admin_email = "admin@example.com"
    existing_user = await repository.get_by_email(admin_email)
    
    if not existing_user:
        logger.info(f"Seeding user: {admin_email}")
        user_data = UserCreate(
            name="Admin User",
            email=admin_email,
            password="adminpassword",
            is_active=True,
            is_admin=True
        )
        await repository.create(user_data, is_admin=True)
        logger.info("Admin user seeded successfully!")
    else:
        logger.info(f"User {admin_email} already exists. Skipping seed.")
