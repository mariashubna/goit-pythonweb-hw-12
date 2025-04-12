from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import User
from src.services.auth import get_current_user, get_current_admin_user
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.conf.config import settings
from src.services.upload_file import UploadFileService
from src.services.users import UserService
from src.database.db import get_db
from src.database.models import UserRole

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me",
    response_model=User,
    description="No more than 5 requests per minute",
)
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user's avatar.
    
    Only administrators can change their avatars. Regular users will keep their default Gravatar.
    The new avatar will be uploaded to Cloudinary and resized to 250x250 pixels.
    
    Args:
        file (UploadFile): New avatar image file. Supported formats: JPG, PNG, GIF
        user (User): Current authenticated user from token
        db (AsyncSession): Database session for user updates
        
    Returns:
        User: Updated user object containing:
            - id: User's unique identifier
            - username: User's username
            - email: User's email address
            - avatar: New avatar URL from Cloudinary
            - role: User's role (admin/user)
        
    Raises:
        HTTPException: 
            - 403: If non-admin user tries to change avatar
            - 422: If file upload fails or format is not supported
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change their avatar"
        )

    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
