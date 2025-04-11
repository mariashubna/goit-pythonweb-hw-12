from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService
from src.database.models import User
from src.schemas import User as UserResponse
import json
import redis


r = redis.Redis(host="localhost", port=6379, db=0)


class Hash:
    """Utility class for password hashing and verification.

    Uses bcrypt for secure password hashing and verification.

    Attributes:
        pwd_context (CryptContext): Passlib context for password hashing.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """Verify a password against its hash.

        Args:
            plain_password (str): Plain text password to verify.
            hashed_password (str): Hashed password to verify against.

        Returns:
            bool: True if password matches hash, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """Generate a password hash.

        Args:
            password (str): Plain text password to hash.

        Returns:
            str: Bcrypt hash of the password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """Create a new JWT access token.

    Args:
        data (dict): Data to encode in the token, typically includes user identifier.
        expires_delta (Optional[int], optional): Token expiration time in seconds.
            Defaults to None, using the JWT_EXPIRATION_SECONDS from settings.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Get the current authenticated user from a JWT token and verify it with Redis.

    This is a FastAPI dependency that validates the JWT token and returns the user.

    Args:
        token (str): JWT token from Authorization header.
        db (Session): Database session.

    Raises:
        HTTPException: 401 if token is invalid, expired, revoked, or user not found.

    Returns:
        User: Current authenticated user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    redis_key = f"user:{username}"
    user_data = r.get(redis_key)
    if user_data:
        # Якщо користувач є в кеші, повертаємо дані
        user_dict = json.loads(user_data.decode("utf-8"))
        # Instead of creating a new User instance, get the existing one from DB
        user_service = UserService(db)
        user = await user_service.get_user_by_username(username=username)
        if user is None:
            raise credentials_exception
        return user

    # Якщо користувача немає в кеші, отримуємо з бази даних
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username=username)
    if user is None:
        raise credentials_exception

    # Convert to a dictionary for Redis storage
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "avatar": user.avatar,
        "confirmed": user.confirmed
    }
    
    # Кешуємо користувача в Redis на 15 хвилин
    r.set(redis_key, json.dumps(user_data), ex=900)

    return user


def create_email_token(data: dict):
    """Create a JWT token for email verification.

    Args:
        data (dict): Data to encode in the token, typically includes email address.

    Returns:
        str: Encoded JWT token with 7-day expiration.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str):
    """Extract email from an email verification token.

    Args:
        token (str): JWT token containing email address.

    Raises:
        HTTPException: 422 if token is invalid.

    Returns:
        str: Email address from token.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )
