from sqlalchemy import Column, Integer, String, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
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
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref='contacts')
    additional_info = Column(String(), nullable=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer(), autoincrement=True, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    refresh_token = Column(String(255), nullable=True)

Base.metadata.create_all(bind=engine)