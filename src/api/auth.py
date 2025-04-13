"""Authentication and authorization endpoints.

This module provides endpoints for user authentication and account management:
- User registration with email verification
- Login with JWT token generation
- Email confirmation
- Password reset functionality
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import (
    UserCreate,
    Token,
    User,
    RequestEmail,
    PasswordResetRequest,
    PasswordReset,
)
from src.services.auth import (
    create_access_token,
    Hash,
    get_email_from_token,
    create_password_reset_token,
    get_current_admin_user,
    create_refresh_token,
    refresh_access_token,
    get_current_user,
    r,
)
from src.services.users import UserService
from src.database.db import get_db
from src.services.email import send_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Register a new user.

    Creates a new user account and sends a verification email.
    The user's email must be confirmed before they can log in.

    Args:
        user_data (UserCreate): User registration data containing:
            - username: Desired username
            - email: Valid email address
            - password: Password (will be hashed)
            - role: User role (admin/user)
        background_tasks (BackgroundTasks): FastAPI background tasks handler
        request (Request): FastAPI request object for base URL
        db (Session): Database session

    Returns:
        User: Created user object with:
            - id: User's unique identifier
            - username: Chosen username
            - email: Email address
            - avatar: Default Gravatar URL
            - role: User's role

    Raises:
        HTTPException:
            - 409: If username or email already exists
            - 422: If validation fails
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate user and return JWT access and refresh tokens."""
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)

    if user is None or not Hash().verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірне імʼя користувача або пароль",
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Підтвердіть вашу електронну адресу для входу",
        )

    access_token = await create_access_token({"sub": user.username})
    refresh_token = await create_refresh_token(user.username)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    db: Session = Depends(get_db),
):
    """Refresh access token using a valid refresh token from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Refresh токен відсутній")

    refresh_token_str = auth_header.split(" ")[1]
    new_access_token = await refresh_access_token(refresh_token_str, db=db)

    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """Confirm a user's email address using a verification token.

    Validates the token and marks the user's email as confirmed.

    Args:
        token (str): Email verification token from the confirmation link
        db (Session): Database session

    Returns:
        dict: Success message indicating confirmation status

    Raises:
        HTTPException:
            - 400: Invalid verification token
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Request a new email confirmation link.

    Sends a new verification email if the user exists and isn't already confirmed.

    Args:
        body (RequestEmail): Request containing:
            - email: User's email address
        background_tasks (BackgroundTasks): FastAPI background tasks handler
        request (Request): FastAPI request object for base URL
        db (Session): Database session

    Returns:
        dict: Success message (same response for security regardless of email existence)

    Note:
        Always returns success to prevent email enumeration
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user and not user.confirmed:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.post("/password-reset-request")
async def request_password_reset(
    body: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Request a password reset email.

    Sends an email with a password reset link if the email exists.
    For security, returns success even if the email doesn't exist.

    Args:
        body (PasswordResetRequest): Request containing:
            - email: User's email address
        background_tasks (BackgroundTasks): FastAPI background tasks handler
        request (Request): FastAPI request object for base URL
        db (Session): Database session

    Returns:
        dict: Success message (same response regardless of email existence)

    Note:
        Always returns success to prevent email enumeration
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user:
        token = await create_password_reset_token({"sub": user.email})
        background_tasks.add_task(
            send_password_reset_email,
            user.email,
            user.username,
            request.base_url,
            token,
        )

    return {
        "message": "If the email exists in our system, you will receive password reset instructions"
    }


@router.get("/password-reset")
async def validate_reset_token(token: str):
    """Validate a password reset token.

    This endpoint is called when user clicks the reset link in their email.
    It validates the token before allowing the user to set a new password.

    Args:
        token (str): Password reset token from email

    Returns:
        dict: Success message and email if token is valid

    Raises:
        HTTPException:
            - 400: Invalid or expired token
    """
    try:
        email = await get_email_from_token(token)
        return {"message": "Token is valid", "email": email}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )


@router.post("/password-reset")
async def reset_password(
    body: PasswordReset,
    db: Session = Depends(get_db),
):
    """Reset a user's password using a valid reset token.

    Validates the reset token and updates the user's password if valid.

    Args:
        body (PasswordReset): Request containing:
            - token: Password reset token from email
            - new_password: New password to set
        db (Session): Database session

    Returns:
        dict: Success message if password was reset

    Raises:
        HTTPException:
            - 400: Invalid token or user not found
    """
    try:
        email = await get_email_from_token(body.token)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    hashed_password = Hash().get_password_hash(body.new_password)
    await user_service.update_password(user.email, hashed_password)
    return {"message": "Password has been reset successfully"}


@router.get("/admin")
def read_admin(current_user: User = Depends(get_current_admin_user)):
    return {"message": f"Вітаємо, {current_user.username}! Це адміністративний маршрут"}


# @router.post("/logout")
# # async def logout(current_user: User = Depends(get_current_user)):
# async def logout(request: Request, current_user: User = Depends(get_current_user)):
#
#     # redis_key = f"refresh:{current_user.username}"
#     # removed = r.delete(redis_key)
#     token = request.headers.get("Authorization", "").replace("Bearer ", "")
#     removed = r.delete(token)  # або твій метод типу remove_refresh_token(token)

#     redis_key_refresh = f"refresh:{current_user.username}"
#     removed_refresh = r.delete(redis_key_refresh)

#     if not token:
#         raise HTTPException(status_code=400, detail="Токен відсутній у запиті")

#     if not removed:
#         raise HTTPException(status_code=400, detail="Токен не знайдений у Redis")

#     if removed_refresh:
#         return {"message": "Користувач успішно вийшов із системи"}
#     else:
#         return JSONResponse(
#             status_code=400,
#             content={"detail": "Немає активного токена для відкликання"},
#         )


# @router.post("/login", response_model=Token)
# async def login_user(
#     form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
# ):
#     """Authenticate a user and return a JWT token.

#     Validates username and password, checks email confirmation,
#     and returns a JWT token for authenticated requests.

#     Args:
#         form_data (OAuth2PasswordRequestForm): Form containing:
#             - username: User's username
#             - password: User's password
#         db (Session): Database session

#     Returns:
#         Token: JWT token response containing:
#             - access_token: JWT token string
#             - token_type: Token type (bearer)

#     Raises:
#         HTTPException:
#             - 401: Invalid credentials or unconfirmed email
#     """
#     user_service = UserService(db)
#     user = await user_service.get_user_by_username(form_data.username)
#     if not user or not Hash().verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Неправильний логін або пароль",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     if not user.confirmed:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Електронна адреса не підтверджена",
#         )
#     access_token = await create_access_token(data={"sub": user.username})
#     return {"access_token": access_token, "token_type": "bearer"}
