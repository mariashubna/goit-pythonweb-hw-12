"""Pydantic models for data validation and serialization.

This module defines the data models used throughout the application for:
- Contact management (creation, updates, responses)
- User management (registration, authentication)
- Token handling
- Email operations

Each model includes field validations and type checking using Pydantic.
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import date, datetime
from typing import Optional


class ContactModel(BaseModel):
    """Base model for contact creation and validation.

    Attributes:
        first_name (str): Contact's first name (2-50 characters)
        last_name (str): Contact's last name (2-50 characters)
        email (EmailStr): Contact's email address (validated format)
        phone (str): Contact's phone number (max 50 characters)
        birthday (date): Contact's birthday
        additional_info (str): Additional contact information (max 250 characters)
    """

    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(max_length=50)
    birthday: date
    additional_info: str = Field(max_length=250)


class ContactResponse(ContactModel):
    """Model for contact data responses.

    Extends ContactModel to include database-specific fields and metadata.
    Allows for attribute-based instantiation from SQLAlchemy models.

    Additional Attributes:
        id (int): Unique identifier for the contact
        created_at (datetime): Timestamp of contact creation
        updated_at (datetime): Timestamp of last update
    """

    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    birthday: Optional[date] = None
    additional_info: Optional[str] = None
    created_at: datetime | None
    updated_at: Optional[datetime] | None

    model_config = ConfigDict(from_attributes=True)


class ContactUpdate(ContactModel):
    """Model for contact update operations.

    All fields are optional to allow partial updates.
    Maintains the same validation rules as ContactModel.

    Note:
        Fields not included in the update request will retain their current values.
    """

    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    birthday: Optional[date] = None
    additional_info: Optional[str] = None


# Схема користувача
class User(BaseModel):
    """Model for user data responses.

    Used for serializing user data in API responses.
    Configured to work with SQLAlchemy model attributes.

    Attributes:
        id (int): Unique identifier for the user
        username (str): User's chosen username
        email (str): User's email address
        avatar (str): URL to user's avatar image
    """

    id: int
    username: str
    email: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)


# Схема для запиту реєстрації
class UserCreate(BaseModel):
    """Model for user registration requests.

    Contains the minimum required fields for creating a new user.
    Password will be hashed before storage.

    Attributes:
        username (str): Desired username for the new account
        email (str): Email address for verification and communication
        password (str): User's chosen password (will be hashed)
    """

    username: str
    email: str
    password: str


# Схема для токену
class Token(BaseModel):
    """Model for authentication tokens.

    Used for JWT token responses after successful authentication.

    Attributes:
        access_token (str): The JWT access token
        token_type (str): Token type (typically "bearer")
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """Model for email-based requests.

    Used for operations that require only an email address,
    such as password reset or email verification.

    Attributes:
        email (EmailStr): Email address (validated format)
    """

    email: EmailStr


class PasswordResetRequest(BaseModel):
    """Model for password reset requests.

    Used when a user requests a password reset via email.

    Attributes:
        email (EmailStr): Email address of the account to reset
    """

    email: EmailStr


class PasswordReset(BaseModel):
    """Model for password reset operations.

    Used when setting a new password with a valid reset token.

    Attributes:
        token (str): Password reset token from email
        new_password (str): New password to set
    """

    token: str
    new_password: str = Field(min_length=3)
