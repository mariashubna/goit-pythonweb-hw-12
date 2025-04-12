from datetime import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel


contact_data = ContactModel(
    email="test@test.de",
    first_name="Test",
    last_name="Contact",
    phone="123321",
    birthday=datetime(day=12, month=12, year=2012),
    additional_info="",
)


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="test")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(first_name="Test", user=user)
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)

    assert len(contacts) == 1
    assert contacts[0].user.id == 1
    assert contacts[0].first_name == "Test"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1, first_name="Test", user=user
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == "Test"


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    existing_contact = Contact(id=1, first_name="Test", last_name="Contact", user=user)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.remove_contact(contact_id=1, user=user)

    assert result is not None
    assert result.last_name == "Contact"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    existing_contact = Contact(
        id=1, first_name="OldName", last_name="OldLastName", user=user
    )

    contact_data = ContactModel(
        email="updated@test.de",
        first_name="UpdatedName",
        last_name="UpdatedLastName",
        phone="987654321",
        birthday=datetime(day=1, month=1, year=1990),
        additional_info="Updated info",
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.update_contact(
        contact_id=1, body=contact_data, user=user
    )

    assert result is not None
    assert result.first_name == "UpdatedName"
    assert result.last_name == "UpdatedLastName"
    assert result.email == "updated@test.de"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_remove_contact_not_found(contact_repository, mock_session, user):
    non_existing_contact = None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = non_existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.remove_contact(contact_id=999, user=user)

    assert result is None
    mock_session.delete.assert_not_awaited()
    mock_session.commit.assert_not_awaited()
