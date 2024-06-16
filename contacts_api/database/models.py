from sqlalchemy import Column, Integer, String, Date
from .db import engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer(), autoincrement=True, primary_key=True)
    first_name = Column(String(), nullable=False)
    last_name = Column(String(), nullable=False)
    email = Column(String(), unique=True, nullable=False)
    phone = Column(String(), nullable=False)
    birth_date = Column(Date(), nullable=False)
    additional_info = Column(String(), nullable=True)

Base.metadata.create_all(bind=engine)