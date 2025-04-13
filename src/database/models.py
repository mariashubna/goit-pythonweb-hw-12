from datetime import date, datetime
from sqlalchemy import String, Integer, Date, DateTime, func, Boolean, Enum as SqlEnum
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy.sql.schema import ForeignKey
from enum import Enum


class Base(DeclarativeBase):
    """Base class for all database models.

    This class provides common functionality and metadata for all models.
    """

    pass


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class Contact(Base):
    """Model representing a contact in the address book.

    This class defines the structure and behavior of contact records in the database.
    Each contact is associated with a user and contains personal information.

    Attributes:
        id (int): Primary key for the contact.
        first_name (str): Contact's first name, limited to 25 characters.
        last_name (str): Contact's last name, limited to 25 characters.
        email (str): Contact's email address, must be unique, limited to 100 characters.
        phone (str): Contact's phone number, must be unique, limited to 20 characters.
        birthday (date): Contact's birth date.
        additional_info (str): Optional additional information about the contact.
        created_at (datetime): Timestamp of when the contact was created.
        updated_at (datetime): Timestamp of the last update to the contact.
        user_id (int): Foreign key referencing the user who owns this contact.
        user (User): Relationship to the User model.
    """

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(25), nullable=False)
    last_name: Mapped[str] = mapped_column(String(25), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    additional_info: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=func.now()
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    user = relationship("User")


class User(Base):
    """Model representing a user in the system.

    This class defines the structure and behavior of user accounts in the database.
    It includes authentication and profile information.

    Attributes:
        id (int): Primary key for the user.
        username (str): Unique username for the user, limited to 100 characters.
        email (str): Unique email address for the user, limited to 100 characters.
        hashed_password (str): Securely hashed password for the user.
        created_at (datetime): Timestamp of when the user account was created.
        avatar (str): Path to the user's avatar image file.
        confirmed (bool): Flag indicating whether the user's email has been confirmed.
    """

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    avatar: Mapped[str] = mapped_column(String, unique=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole), default=UserRole.USER, nullable=False
    )
