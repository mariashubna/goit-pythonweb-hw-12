import pickle

import pytest
from jose import jwt
from unittest.mock import AsyncMock, patch, MagicMock

from fastapi import HTTPException, status

from src.services.auth import (
    create_access_token,
    get_current_user,
    get_email_from_token,
    create_email_token,
    get_current_admin_user,
)
from src.database.models import User, UserRole
from src.conf.config import settings


@pytest.mark.asyncio
async def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = await create_access_token(data, expires_delta=60)
    decoded = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token="invalid.token.here", db=AsyncMock())
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_admin_user_success():
    user = User(id=1, username="admin", role=UserRole.ADMIN)
    result = get_current_admin_user(user)
    assert result == user


def test_get_current_admin_user_forbidden():
    user = User(id=1, username="user", role=UserRole.USER)
    with pytest.raises(HTTPException) as exc:
        get_current_admin_user(user)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_email_from_token_valid():
    token = jwt.encode(
        {"sub": "test@example.com"},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    email = await get_email_from_token(token)
    assert email == "test@example.com"


@pytest.mark.asyncio
async def test_get_email_from_token_invalid():
    with pytest.raises(HTTPException) as exc:
        await get_email_from_token("invalid.token")
    assert exc.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_email_token():
    token = create_email_token({"sub": "test@example.com"})
    decoded = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded
    assert "iat" in decoded
