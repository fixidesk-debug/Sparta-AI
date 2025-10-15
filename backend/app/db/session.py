from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# For psycopg3, ensure the URL uses postgresql+psycopg dialect
# If DATABASE_URL uses postgresql://, SQLAlchemy 2.0 will use psycopg3 automatically
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
