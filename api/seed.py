from app.core.logger import app_logger as logger
from app.database.connections.database import db_instance
from app.database.seeds.user_seed import seed_users

def run_seeds():
    logger.info("Starting database seeds...")
    
    db = next(db_instance.get_db())
    try:
        seed_users(db)
        
        logger.info("Database seeding completed.")
    except Exception as e:
        logger.error(f"Error while running seeds: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_seeds()
