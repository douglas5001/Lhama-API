from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

class Database:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.Base = declarative_base()
        self._initialize_connection()

    def _initialize_connection(self):
        db_type = settings.DB.lower()
        
        if db_type == "sqlite":
            database_url = f"sqlite+aiosqlite:///./{settings.DATABASE}.db"
            self.engine = create_async_engine(database_url, connect_args={"check_same_thread": False})
            
        elif db_type in ["postgres", "postgresql"]:
            database_url = f"postgresql+asyncpg://{settings.DB_USER}:{settings.PASSWORD}@{settings.HOST}:{settings.PORT}/{settings.DATABASE}"
            self.engine = create_async_engine(database_url)
            
        else:
            raise ValueError(f"Database '{db_type}' is not supported.")

        # Utilizamos o async_sessionmaker ao invés do normal "sessionmaker"
        self.SessionLocal = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine, class_=AsyncSession
        )

    async def get_db(self):
        if self.SessionLocal is None:
            raise RuntimeError("Database connection not initialized.")
        
        async with self.SessionLocal() as db:
             yield db

db_instance = Database()

Base = db_instance.Base