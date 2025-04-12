from unittest.mock import Mock
from src.database.models import UserRole
import pytest
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": UserRole.USER,
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Користувач з таким email вже існує"


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Електронна адреса не підтверджена"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"


def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


def test_request_email_confirmation(client):
    response = client.post("api/auth/request_email", json={"email": user_data["email"]})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Перевірте свою електронну пошту для підтвердження"


def test_signup_email_sent(client, monkeypatch):
    """Test that email is sent during registration."""
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    test_user = {
        "username": "newuser",
        "email": "newuser@gmail.com",
        "password": "12345678",
        "role": UserRole.USER,
    }

    response = client.post("api/auth/register", json=test_user)
    assert response.status_code == 201

    mock_send_email.assert_called_once()
    call_args = mock_send_email.call_args[0]
    assert call_args[0] == test_user["email"]
    assert call_args[1] == test_user["username"]
    assert "http" in str(call_args[2])


def test_signup_weak_password(client):
    weak_user_data = {
        "username": "weakuser",
        "email": "weakuser@gmail.com",
        "password": "1",
        "role": UserRole.USER,
    }
    response = client.post("api/auth/register", json=weak_user_data)
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


def test_signup_missing_field(client):
    incomplete_user_data = {
        "username": "user_without_email",
        "password": "12345678",
        "role": UserRole.USER,
    }
    response = client.post("api/auth/register", json=incomplete_user_data)
    assert response.status_code == 422, response.text  # Ошибка валидации
    data = response.json()
    assert "detail" in data
