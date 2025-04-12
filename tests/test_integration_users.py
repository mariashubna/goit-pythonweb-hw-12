from unittest.mock import patch
from src.database.models import UserRole
import pytest
import io
from conftest import test_user, admin_user
from unittest.mock import AsyncMock, Mock
from sqlalchemy import select
from src.database.models import User
from tests.conftest import TestingSessionLocal


def test_get_me(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/users/me", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "avatar" in data


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).filter_by(email=admin_user.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": admin_user.get("username"),
            "password": admin_user.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    return data
