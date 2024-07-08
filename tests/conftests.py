import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from contacts_api.main import app

from contacts_api.database.models import Base
from contacts_api.database.db import get_db
from contacts_api.conf.config import settings

DB_URL = 'sqlite:///./test.db'

engine = create_engine(DB_URL, connect_args={'check_same_thread': False})
TestingSesssionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope='module')
def session():

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSesssionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(session):

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

@pytest.fixture
def user():
    return {'username': 'test_user', 'email': 'test@example.com', 'password': '123456789'}