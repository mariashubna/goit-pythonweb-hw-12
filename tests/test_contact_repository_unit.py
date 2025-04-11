import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactUpdate

contact_info = {
    "first_name": "Test",
    "last_name": "Contact",
    "email": "test@example.com",
    "phone": "+1234567890",
    "birthday": "1990-01-01",
    "additional_info": "Test contact info",
}


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(**contact_info, user=user)
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)

    # Assertions
    assert len(contacts) == 1
    assert contacts[0].first_name == "Test"
    assert contacts[0].last_name == "Contact"
    assert contacts[0].email == "test@example.com"
    assert contacts[0].phone == "+1234567890"
    assert contacts[0].birthday == "1990-01-01"
    assert contacts[0].additional_info == "Test contact info"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    # Setup
    mock_result = MagicMock()
    contact = Contact(**contact_info, user=user)
    contact.id = 1
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    # Assertions
    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == "Test"
    assert contact.last_name == "Contact"
    assert contact.email == "test@example.com"
    assert contact.phone == "+1234567890"
    assert contact.birthday == "1990-01-01"
    assert contact.additional_info == "Test contact info"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    # Setup
    contact_data = ContactModel(
        first_name="Test2",
        last_name="Contact2",
        email="test2@example.com",
        phone="+2134567890",
        birthday="1990-01-01",
        additional_info="Test contact info",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1,
        first_name=contact_data.first_name,
        last_name=contact_data.last_name,
        email=contact_data.email,
        phone=contact_data.phone,
        user=user,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.create_contact(body=contact_data, user=user)

    # Assertions
    assert isinstance(result, Contact)
    assert result.first_name == "Test2"
    assert result.last_name == "Contact2"
    assert result.email == "test2@example.com"
    assert result.phone == "+2134567890"


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    # Setup
    existing_contact = Contact(id=1, **contact_info, user=user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.remove_contact(contact_id=1, user=user)

    # Assertions
    assert result is not None
    assert result.first_name == "Test"
    assert result.last_name == "Contact"
    assert result.email == "test@example.com"
    assert result.phone == "+1234567890"

    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    # Setup
    contact_data = ContactUpdate(
        first_name="Test3",
        last_name="Contact3",
        email="test3@example.com",
        phone="+3134567890",
    )
    existing_contact = Contact(id=1, **contact_info, user=user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.update_contact(
        contact_id=1, body=contact_data, user=user
    )

    # Assertions
    assert result is not None
    assert result.first_name == "Test3"
    assert result.last_name == "Contact3"
    assert result.email == "test3@example.com"
    assert result.phone == "+3134567890"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)
