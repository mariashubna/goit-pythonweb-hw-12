import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.contacts import ContactService
from src.schemas import ContactModel
from src.database.models import User


@pytest.mark.asyncio
async def test_create_contact():
    # Мокування сесії бази даних
    mock_db = AsyncMock(spec=AsyncSession)

    # Створення тестових даних
    user = User(id=1, username="test_user", email="test@example.com")
    contact_data = ContactModel(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday="1990-01-01",
    )

    # Створення об'єкта ContactService
    contact_service = ContactService(mock_db)

    # Виклик функції для створення контакту
    contact = await contact_service.create_contact(contact_data, user)

    # Перевірка, що результат не є None
    assert contact is not None
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.email == "john@example.com"
