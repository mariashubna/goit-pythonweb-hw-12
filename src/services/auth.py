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
from src.database.models import User, UserRole
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


async def create_access_token(
    data: dict, expires_delta: Optional[int] = None, scope: str = "access"
):
    """Create a new JWT token with a specific scope (access or refresh).

    Args:
        data (dict): Payload data for the token (usually includes 'sub').
        expires_delta (Optional[int]): Lifetime of the token in seconds.
        scope (str): Token scope: 'access' or 'refresh'.

    Returns:
        str: JWT token string.
    """
    to_encode = data.copy()
    if scope == "access":
        expire = datetime.now(UTC) + timedelta(
            seconds=expires_delta or settings.JWT_EXPIRATION_SECONDS
        )
    elif scope == "refresh":
        expire = datetime.now(UTC) + timedelta(days=7)
    else:
        raise ValueError("Invalid token scope")

    to_encode.update({"exp": expire, "scope": scope})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def create_refresh_token(username: str) -> str:
    """Create and store a refresh token for a user.

    Args:
        username (str): The username to associate with the refresh token.

    Returns:
        str: JWT refresh token.
    """
    token_data = {"sub": username}
    refresh_token = await create_access_token(token_data, scope="refresh")

    redis_key = f"refresh:{username}"
    r.set(redis_key, refresh_token, ex=7 * 24 * 3600)  # 7 days
    return refresh_token


async def refresh_access_token(
    refresh_token: str, db: Session = Depends(get_db)
) -> str:
    """Validate refresh token and return a new access token.

    Args:
        refresh_token (str): JWT refresh token.
        db (Session): Database session.

    Returns:
        str: New access token.

    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("scope") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Невірний тип токену"
            )
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний або протермінований токен",
        )

    redis_key = f"refresh:{username}"
    stored_token = r.get(redis_key)
    if not stored_token or stored_token.decode("utf-8") != refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недійсний або відкликаний токен",
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username=username)
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    return await create_access_token({"sub": username})


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
        "confirmed": user.confirmed,
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


async def create_password_reset_token(data: dict) -> str:
    """Create a JWT token for password reset.

    Args:
        data (dict): Data to encode in the token, typically includes email address.

    Returns:
        str: Encoded JWT token with 1-hour expiration.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(hours=1)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    return token


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """Check if the current user is an administrator.

    This is a FastAPI dependency that can be used to protect admin-only endpoints.
    It builds on top of get_current_user to first authenticate the user,
    then verifies if they have administrator privileges.

    Args:
        current_user (User): The authenticated user from get_current_user dependency.
            This parameter is injected by FastAPI's dependency system.

    Returns:
        User: The current user if they are an administrator.

    Raises:
        HTTPException: 403 Forbidden if the user is not an administrator.
            This includes a Ukrainian error message "Недостатньо прав доступу"
            (Insufficient access rights).

    Example:
        ```python
        @router.get("/admin-only")
        async def admin_endpoint(admin: User = Depends(get_current_admin_user)):
            return {"message": "You are an admin"}
        ```
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
    return current_user


# async def create_access_token(data: dict, expires_delta: Optional[int] = None):
#     """Create a new JWT access token.

#     Args:
#         data (dict): Data to encode in the token, typically includes user identifier.
#         expires_delta (Optional[int], optional): Token expiration time in seconds.
#             Defaults to None, using the JWT_EXPIRATION_SECONDS from settings.

#     Returns:
#         str: Encoded JWT token.
#     """
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
#     else:
#         expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(
#         to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
#     )

#     return encoded_jwt
