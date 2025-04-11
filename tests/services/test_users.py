import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock
from src.services.users import UserService
from src.schemas import UserCreate


@pytest.mark.asyncio
async def test_create_user():
    # Мокування сесії бази даних
    mock_db = AsyncMock(spec=AsyncSession)

    # Створення тестових даних
    user_create_data = UserCreate(
        username="test_user", email="test@example.com", password="securepassword"
    )

    # Створення об'єкта UserService
    user_service = UserService(mock_db)

    # Виклик функції для створення користувача
    user = await user_service.create_user(user_create_data)

    # Перевірка, що результат не є None
    assert user is not None
    assert user.username == "test_user"
    assert user.email == "test@example.com"
