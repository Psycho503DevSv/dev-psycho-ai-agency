from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings


def get_engine():
    settings = get_settings()
    return create_engine(settings.database_url)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=None)


class Base(DeclarativeBase):
    pass


def get_db():
    engine = get_engine()
    SessionLocal.configure(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
