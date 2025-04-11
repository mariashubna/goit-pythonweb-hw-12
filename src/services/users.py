from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate


class UserService:
    """Service class for handling user-related business logic.

    This class provides high-level operations for user management, including
    user creation, retrieval, and profile updates. It uses Gravatar for default
    user avatars and delegates database operations to UserRepository.

    Attributes:
        repository (UserRepository): Repository instance for user database operations.
    """

    def __init__(self, db: AsyncSession):
        """Initialize UserService with database session.

        Args:
            db (AsyncSession): SQLAlchemy async database session.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """Create a new user with Gravatar avatar.

        Args:
            body (UserCreate): User creation data including email, username, and password.

        Returns:
            User: Created user instance with generated avatar.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """Retrieve a user by their ID.

        Args:
            user_id (int): User's unique identifier.

        Returns:
            User | None: User instance if found, None otherwise.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """Retrieve a user by their username.

        Args:
            username (str): User's unique username.

        Returns:
            User | None: User instance if found, None otherwise.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """Retrieve a user by their email address.

        Args:
            email (str): User's unique email address.

        Returns:
            User | None: User instance if found, None otherwise.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """Mark a user's email as confirmed.

        Args:
            email (str): Email address to confirm.

        Returns:
            User: Updated user instance with confirmed email.
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """Update a user's avatar URL.

        Args:
            email (str): Email of the user to update.
            url (str): New avatar URL.

        Returns:
            User: Updated user instance with new avatar URL.
        """
        return await self.repository.update_avatar_url(email, url)
