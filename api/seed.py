import asyncio
from app.core.logger import app_logger as logger
from app.database.connections.database import db_instance
from app.database.seeds.user_seed import seed_users

async def run_seeds():
    logger.info("Starting database seeds...")
    
    # get_db agora é um gerador assíncrono, extraímos a sessão de forma manual aqui para scripts CLI
    db_gen = db_instance.get_db()
    db = await anext(db_gen)
    
    try:
        await seed_users(db)
        logger.info("Database seeding completed.")
    except Exception as e:
        logger.error(f"Error while running seeds: {e}")
        await db.rollback()
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(run_seeds())
