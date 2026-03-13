import logging
from app.database.connections.database import db_instance
from app.database.seeds.user_seed import seed_users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_seeds():
    logger.info("Starting database seeds...")
    
    # Get a database session
    db = next(db_instance.get_db())
    try:
        # Run independent seeds
        seed_users(db)
        
        # Add future seeds here:
        # seed_roles(db)
        # seed_permissions(db)
        
        logger.info("Database seeding completed.")
    except Exception as e:
        logger.error(f"Error while running seeds: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_seeds()
