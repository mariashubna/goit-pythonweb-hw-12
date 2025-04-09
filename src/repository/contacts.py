from typing import List
from sqlalchemy import select, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self, skip: int, limit: int, user: User, q: str | None = None
    ) -> List[Contact]:
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
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        contact = Contact(**body.dict(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(contact.id, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, user: User
    ) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def get_birthday_list(self, user: User) -> List[Contact]:
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
