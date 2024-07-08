from unittest.mock import MagicMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# I had to use the above code, because without that python could not import
# anything from 'contacts_api' module

from contacts_api.database.models import User
from conftests import client, user, session

def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('contacts_api.routes.auth.send_email', mock_send_email)
    response = client.post(
        '/api/auth/signup',
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data['user']['email'] == user.get('email')
    assert 'id' in data['user']

def test_create_user_repeat(client, user):
    response = client.post(
        '/api/auth/signup',
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data['detail'] == 'Account already exists'

def test_login_user_not_confirmed(client, user):
    response = client.post(
        '/api/auth/login',
        data={'username': user.get('email'), 'password': user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data['detail'] == 'Email not confirmed'

def test_login_user(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        '/api/auth/login',
        data={'username': user.get('email'), 'password': user.get('password')}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['token_type'] == 'bearer'

def test_login_wrong_password(client, user):
    response = client.post(
        '/api/auth/login',
        data={'username': user.get('email'), 'password': 'wrong_password'}
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data['detail'] == 'Invalid password'

def test_login_wrong_email(client, user):
    response = client.post(
        '/api/auth/login',
        data={'username': 'invalid@email.com', 'password': user.get('password')}
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data['detail'] == 'Invalid email'
