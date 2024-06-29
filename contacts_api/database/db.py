from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contacts_api.conf.config import settings

SQL_DB_URL = settings.sqlalchemy_database_url
engine = create_engine(SQL_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()