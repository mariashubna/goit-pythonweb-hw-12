"""Contact repository module for database operations.

This module provides the data access layer for contact-related operations,
implementing CRUD operations and specialized queries for contact management.
It uses SQLAlchemy for database interactions and provides type-safe operations.
"""

from typing import List
from sqlalchemy import select, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate


class ContactRepository:
    """Repository class for contact-related database operations.

    This class handles all database interactions for contacts, including:
    - CRUD operations (Create, Read, Update, Delete)
    - Search functionality
    - Birthday notifications
    - User-specific contact filtering

    All operations are user-scoped for data isolation.

    Attributes:
        db (AsyncSession): SQLAlchemy async database session.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session.

        Args:
            session (AsyncSession): SQLAlchemy async session for database operations.
        """
        self.db = session

    async def get_contacts(
        self, skip: int, limit: int, user: User, q: str | None = None
    ) -> List[Contact]:
        """Retrieve a paginated list of contacts with optional search.

        Args:
            skip (int): Number of records to skip (offset).
            limit (int): Maximum number of records to return.
            user (User): User whose contacts to retrieve.
            q (str | None, optional): Search query for filtering contacts.
                Searches in first_name, last_name, and email fields.

        Returns:
            List[Contact]: List of contacts matching the criteria.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)

        if q:
            stmt = stmt.where(
                (Contact.first_name.ilike(f"%{q}%"))
                | (Contact.last_name.ilike(f"%{q}%"))
                | (Contact.email.ilike(f"%{q}%"))
            )

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """Retrieve a specific contact by ID.

        Args:
            contact_id (int): ID of the contact to retrieve.
            user (User): User who owns the contact.

        Returns:
            Contact | None: Contact if found and owned by user, None otherwise.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """Create a new contact.

        Args:
            body (ContactModel): Contact data for creation.
            user (User): User who will own the contact.

        Returns:
            Contact: Created contact instance with all fields populated.
        """
        contact = Contact(**body.dict(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(contact.id, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """Delete a contact.

        Args:
            contact_id (int): ID of the contact to delete.
            user (User): User who owns the contact.

        Returns:
            Contact | None: Deleted contact if found and owned by user, None otherwise.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, user: User
    ) -> Contact | None:
        """Update an existing contact.

        Args:
            contact_id (int): ID of the contact to update.
            body (ContactUpdate): Updated contact data.
            user (User): User who owns the contact.

        Returns:
            Contact | None: Updated contact if found and owned by user, None otherwise.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def get_birthday_list(self, user: User) -> List[Contact]:
        """Get contacts with birthdays in the next 7 days.

        This method finds contacts whose birthdays fall within the next week,
        including today. It handles month transitions correctly.

        Args:
            user (User): User whose contacts to check.

        Returns:
            List[Contact]: List of contacts with upcoming birthdays.
        """
        today = date.today()
        next_week = today + timedelta(days=7)

        stmt = select(Contact).where(
            and_(
                Contact.user == user,
                Contact.birthday.isnot(None),
                (
                    (extract("month", Contact.birthday) == today.month)
                    & (extract("day", Contact.birthday) >= today.day)
                )
                | (
                    (extract("month", Contact.birthday) == next_week.month)
                    & (extract("day", Contact.birthday) <= next_week.day)
                ),
            )
        )

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
