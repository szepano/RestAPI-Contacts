from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQL_DB_URL = "postgresql://postgres:12345678@localhost:5432/postgres"
engine = create_engine(SQL_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()