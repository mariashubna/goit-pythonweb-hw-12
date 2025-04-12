"""User repository module for database operations.

This module provides the data access layer for user-related operations,
implementing user management functionality including registration,
authentication, email confirmation, and profile updates.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    """Repository class for user-related database operations.

    This class handles all database interactions for users, including:
    - User registration and retrieval
    - Email confirmation
    - Avatar management
    - User lookup by various identifiers

    Attributes:
        db (AsyncSession): SQLAlchemy async database session.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session.

        Args:
            session (AsyncSession): SQLAlchemy async session for database operations.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieve a user by their ID.

        Args:
            user_id (int): Unique identifier of the user.

        Returns:
            User | None: User instance if found, None otherwise.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """Retrieve a user by their username.

        Args:
            username (str): Unique username of the user.

        Returns:
            User | None: User instance if found, None otherwise.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email address.

        Args:
            email (str): Unique email address of the user.

        Returns:
            User | None: User instance if found, None otherwise.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """Create a new user.

        Creates a new user with the provided data and optional avatar.
        The password in the body should already be hashed.

        Args:
            body (UserCreate): User creation data including username, email, and hashed password.
            avatar (str, optional): URL of user's avatar image. Defaults to None.

        Returns:
            User: Created user instance with all fields populated.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """Mark a user's email as confirmed.

        Args:
            email (str): Email address of the user to confirm.

        Note:
            This method assumes the email exists in the database.
            It should only be called after verifying the email token.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """Update a user's avatar URL.

        Args:
            email (str): Email of the user whose avatar to update.
            url (str): New avatar URL.

        Returns:
            User: Updated user instance.

        Note:
            This method assumes the email exists in the database.
            The URL should be validated before calling this method.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_password(self, email: str, hashed_password: str) -> User:
        """Update a user's password.

        Args:
            email (str): Email of the user to update.
            hashed_password (str): New hashed password to set.

        Returns:
            User: Updated user instance.
        """
        user = await self.get_user_by_email(email)
        if user:
            user.hashed_password = hashed_password
            await self.db.commit()
            await self.db.refresh(user)
        return user
