from typing import Optional
import redis.asyncio as redis

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from contacts_api.database.db import get_db
from contacts_api.repository import users as repository_users
from contacts_api.conf.config import settings


class Auth:
    """
    Handles authentication operations such as password hashing, token creation, and verification.
    """

    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY: str = settings.secret_key
    ALGORITHM: str = settings.algorithm
    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r: redis.Redis = redis.Redis(
        host=settings.redis_host, port=settings.redis_port, db=0
    )

    def verify_password(self, plain_pass: str, hash_pass: str) -> bool:
        """
        Verifies if the plain password matches the hashed password.
        :param plain_pass: Plain password to verify.
        :param hash_pass: Hashed password to compare against.
        :return: True if the passwords match, False otherwise.
        """

        return self.pwd_context.verify(plain_pass, hash_pass)

    def get_password_hash(self, password: str) -> str:
        """
        Hashes the provided password.
        :param password: Password to hash.
        :return: Hashed password.
        """

        return self.pwd_context.hash(password)

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        """
        Creates an access token based on the provided data.
        :param data: Data to encode into the token.
        :param expires_delta: Expiration time delta in seconds (optional).
        :return: Encoded access token.
        """

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token: str = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        """
        Creates a refresh token based on the provided data.
        :param data: Data to encode into the token.
        :param expires_delta: Expiration time delta in seconds (optional).
        :return: Encoded refresh token.
        """

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token: str = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        Decodes the refresh token to retrieve the email associated with it.
        :param refresh_token: Refresh token to decode.
        :return: Decoded email from the token.
        :raises HTTPException 401: If the token is invalid or has an incorrect scope.
        """

        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, self.ALGORITHM)
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token"
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ) -> Session:
        """
        Retrieves the current authenticated user based on the provided access token.
        :param token: Access token for authentication (dependency).
        :param db: Database session (dependency).
        :return: Current authenticated user session.
        :raises HTTPException 401: If credentials cannot be validated or user does not exist.
        """

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception from e
        
        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    def create_email_token(self, data: dict) -> str:
        """
        Creates an email verification token.
        :param data: Data to encode into the token.
        :return: Encoded email verification token.
        """

        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token: str = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str) -> str:
        """
        Retrieves the email from the provided email verification token.
        :param token: Email verification token to decode.
        :return: Decoded email from the token.
        :raises HTTPException 422: If the token is invalid.
        """

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )

auth_service: Auth = Auth()
