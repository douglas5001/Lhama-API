from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
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
            database_url = f"sqlite:///./{settings.DATABASE}.db"
            self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
            
        elif db_type in ["postgres", "postgresql"]:
            database_url = f"postgresql://{settings.USER}:{settings.PASSWORD}@{settings.HOST}:{settings.PORT}/{settings.DATABASE}"
            self.engine = create_engine(database_url)
            
        else:
            raise ValueError(f"Banco de dados '{db_type}' não é suportado.")

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_db(self):
        if self.SessionLocal is None:
            raise RuntimeError("Conexão do banco de dados não inicializada.")
        
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

db_instance = Database()

Base = db_instance.Base
get_db = db_instance.get_db