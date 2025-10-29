import os
import stat

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import emails  # type: ignore
import jwt
from jinja2 import Template
from jwt.exceptions import InvalidTokenError

from app.core import security
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent.parent / "email-templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    assert settings.emails_enabled, "no provided configuration for email variables"
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def generate_test_email(email_to: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.FRONTEND_HOST,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None


def generate_approval_token(email: str, user_id: str) -> str:
    """Generate secure approval token with expiration."""
    delta = timedelta(hours=settings.APPROVAL_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()

    encoded_jwt = jwt.encode(
        {
            "exp": exp,
            "nbf": now,
            "sub": email,
            "user_id": str(user_id),
            "type": "registration_approval",
        },
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt


def verify_approval_token(token: str) -> dict | None:
    """Verify and decode approval token."""
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        if decoded_token.get("type") != "registration_approval":
            return None
        return {"email": decoded_token["sub"], "user_id": decoded_token["user_id"]}
    except InvalidTokenError:
        return None


def generate_admin_approval_email(
    user_email: str, user_name: str, approval_token: str
) -> EmailData:
    """Generate email to admin requesting approval for new registration."""
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New Registration Requires Approval"

    approval_link = (
        f"{settings.FRONTEND_HOST}/admin/approve-registration?token={approval_token}"
    )
    rejection_link = (
        f"{settings.FRONTEND_HOST}/admin/reject-registration?token={approval_token}"
    )

    html_content = render_email_template(
        template_name="admin_approval_request.html",
        context={
            "project_name": project_name,
            "user_name": user_name,
            "user_email": user_email,
            "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "approval_link": approval_link,
            "rejection_link": rejection_link,
            "expiry_hours": settings.APPROVAL_TOKEN_EXPIRE_HOURS,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def send_admin_approval_email(
    user_email: str, user_name: str, approval_token: str
) -> None:
    """Send approval request email to all admins."""
    email_data = generate_admin_approval_email(
        user_email=user_email, user_name=user_name, approval_token=approval_token
    )
    # Send to each admin in the list
    for admin_email in settings.ADMIN_EMAILS:
        send_email(
            email_to=admin_email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )


def generate_registration_approved_email(email_to: str, full_name: str) -> EmailData:
    """Generate welcome email after registration approval."""
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Account Approved!"

    html_content = render_email_template(
        template_name="registration_approved.html",
        context={
            "project_name": project_name,
            "user_name": full_name,
            "user_email": email_to,
            "login_link": f"{settings.FRONTEND_HOST}/login",
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def send_registration_approved_email(email_to: str, full_name: str) -> None:
    """Send approval notification to user."""
    email_data = generate_registration_approved_email(
        email_to=email_to, full_name=full_name
    )
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
