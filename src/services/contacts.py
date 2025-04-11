from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactUpdate
from src.database.models import User


class ContactService:
    """Service class for managing contact operations.

    This class provides high-level business logic for contact management,
    including creation, retrieval, update, and deletion of contacts.
    It delegates database operations to ContactRepository.

    Attributes:
        contact_repository (ContactRepository): Repository instance for contact database operations.
    """

    def __init__(self, db: AsyncSession):
        """Initialize ContactService with database session.

        Args:
            db (AsyncSession): SQLAlchemy async database session.
        """
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User):
        """Create a new contact for a user.

        Args:
            body (ContactModel): Contact data including name, email, phone, etc.
            user (User): User who owns the contact.

        Returns:
            Contact: Created contact instance.
        """
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(
        self, skip: int, limit: int, user: User, q: str | None = None
    ):
        """Retrieve a paginated list of contacts with optional search.

        Args:
            skip (int): Number of contacts to skip for pagination.
            limit (int): Maximum number of contacts to return.
            user (User): User whose contacts to retrieve.
            q (str | None, optional): Search query string. Defaults to None.

        Returns:
            List[Contact]: List of contacts matching the criteria.
        """
        return await self.contact_repository.get_contacts(skip, limit, q, user)

    async def get_contact(self, contact_id: int, user: User):
        """Retrieve a specific contact by ID.

        Args:
            contact_id (int): ID of the contact to retrieve.
            user (User): User who owns the contact.

        Returns:
            Contact | None: Contact if found and owned by user, None otherwise.
        """
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        """Update an existing contact.

        Args:
            contact_id (int): ID of the contact to update.
            body (ContactUpdate): Updated contact data.
            user (User): User who owns the contact.

        Returns:
            Contact | None: Updated contact if found and owned by user, None otherwise.
        """
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """Delete a contact.

        Args:
            contact_id (int): ID of the contact to delete.
            user (User): User who owns the contact.

        Returns:
            Contact | None: Deleted contact if found and owned by user, None otherwise.
        """
        return await self.contact_repository.remove_contact(contact_id, user)

    async def get_birthday_list(self, user: User):
        """Get list of contacts with upcoming birthdays.

        Retrieves contacts whose birthdays are within the configured
        notification period (typically next 7 days).

        Args:
            user (User): User whose contacts to check.

        Returns:
            List[Contact]: List of contacts with upcoming birthdays.
        """
        return await self.contact_repository.get_birthday_list(user)
