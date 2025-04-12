import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.users import UserRepository


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def contact():
    return Contact(id=1, email="Test@test.com")


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="Test")
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_id(user_id=1)
    assert user is not None
    assert user.id == 1
    assert user.username == "Test"


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="Test")
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_username(username="Test2")
    assert user is not None
    assert user.id == 1
    assert user.username == "Test"
