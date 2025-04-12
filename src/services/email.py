from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import create_email_token
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """Send an email verification message to a newly registered user.

    Creates a verification token and sends an HTML email using a template.
    The email contains a link that the user must click to verify their email address.

    Args:
        email (EmailStr): User's email address to send verification to
        username (str): User's username for personalization
        host (str): Base URL of the application for constructing verification link

    Note:
        Uses the verify_email.html template with the following context:
        - host: Base URL for constructing the verification link
        - username: User's name for personalization
        - token: JWT token for email verification

    Raises:
        ConnectionErrors: If there are issues connecting to the email server
            (errors are currently logged but not propagated)
    """
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)  # Consider using proper logging here


async def send_password_reset_email(email: EmailStr, username: str, host: str, token: str):
    """Send a password reset email to the user.

    Args:
        email (EmailStr): User's email address
        username (str): User's username
        host (str): Base URL of the application
        token (str): Password reset token
    """
    try:
        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(err)
