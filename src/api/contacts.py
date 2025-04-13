from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import (
    ContactModel,
    ContactUpdate,
    ContactResponse,
)
from src.services.contacts import ContactService
from src.database.models import User
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts")


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 10,
    q: str | None = Query(None, max_length=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Retrieve a paginated list of contacts for the authenticated user.

    Args:
        skip (int, optional): Number of contacts to skip. Defaults to 0.
        limit (int, optional): Maximum number of contacts to return. Defaults to 10.
        q (str | None, optional): Search query string. Defaults to None.
        db (AsyncSession): Database session dependency.
        user (User): Current authenticated user.

    Returns:
        List[ContactResponse]: List of contacts matching the query parameters.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, q, user)
    return contacts


@router.get("/birthdays", response_model=List[ContactResponse])
async def birthdays_now(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a list of contacts who have birthdays in the current period.

    Args:
        db (AsyncSession): Database session dependency.
        user (User): Current authenticated user.

    Returns:
        List[ContactResponse]: List of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_birthday_list(user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Retrieve a specific contact by ID.

    Args:
        contact_id (int): ID of the contact to retrieve.
        db (AsyncSession): Database session dependency.
        user (User): Current authenticated user.

    Raises:
        HTTPException: If contact is not found (404).

    Returns:
        ContactResponse: Contact details if found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new contact.

    Args:
        body (ContactModel): Contact data to create.
        db (AsyncSession): Database session dependency.
        user (User): Current authenticated user.

    Returns:
        ContactResponse: Newly created contact details.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update all fields of an existing contact.

    Args:
        body (ContactModel): Updated contact data.
        contact_id (int): ID of the contact to update.
        db (AsyncSession): Database session dependency.
        user (User): Current authenticated user.

    Raises:
        HTTPException: If contact is not found (404).

    Returns:
        ContactResponse: Updated contact details.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Partially update an existing contact.

    Args:
        body (ContactUpdate): Partial contact data to update.
        contact_id (int): ID of the contact to update.
        db (AsyncSession): Database session dependency.
        user (User): Current authenticated user.

    Raises:
        HTTPException: If contact is not found (404).

    Returns:
        ContactResponse: Updated contact details.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a contact.

    Args:
        contact_id (int): ID of the contact to delete.
        db (AsyncSession): Database session dependency.
        user (User): Current authenticated user.

    Raises:
        HTTPException: If contact is not found (404).

    Returns:
        ContactResponse: Deleted contact details.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
