"""Centralised, failure-tolerant SMTP delivery for KAUSHALYA."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app.config.settings import get_settings
from app.database.connection import get_db

logger = logging.getLogger(__name__)


def _mail_client() -> FastMail | None:
    settings = get_settings()
    if not settings.smtp_configured:
        return None
    return FastMail(ConnectionConfig(
        MAIL_USERNAME=settings.SMTP_USERNAME, MAIL_PASSWORD=settings.SMTP_PASSWORD,
        MAIL_FROM=settings.SMTP_FROM_EMAIL, MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
        MAIL_PORT=settings.SMTP_PORT, MAIL_SERVER=settings.SMTP_HOST,
        MAIL_STARTTLS=settings.SMTP_USE_TLS, MAIL_SSL_TLS=not settings.SMTP_USE_TLS,
        USE_CREDENTIALS=bool(settings.SMTP_USERNAME), VALIDATE_CERTS=True,
        TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates" / "emails",
    ))


async def _log(recipient: str, subject: str, email_type: str, status: str, *, user_id: str | None = None,
               metadata: dict[str, Any] | None = None, error_message: str | None = None) -> None:
    try:
        await get_db().email_logs.insert_one({"recipient": recipient, "subject": subject,
            "email_type": email_type, "status": status, "error_message": error_message,
            "user_id": user_id, "sent_at": datetime.now(timezone.utc), "metadata": metadata or {}})
    except Exception:
        logger.exception("Unable to write email delivery log")


async def _deliver(*, recipient: str, subject: str, email_type: str, template: str, context: dict[str, Any],
                   user_id: str | None = None, metadata: dict[str, Any] | None = None) -> None:
    await _log(recipient, subject, email_type, "PENDING", user_id=user_id, metadata=metadata)
    client = _mail_client()
    if client is None:
        logger.warning("SMTP is not configured; email type=%s was not delivered", email_type)
        await _log(recipient, subject, email_type, "FAILED", user_id=user_id, metadata=metadata,
                   error_message="SMTP is not configured")
        return
    try:
        await client.send_message(MessageSchema(subject=subject, recipients=[recipient], template_body=context,
                                  subtype=MessageType.html), template_name=template)
        await _log(recipient, subject, email_type, "SENT", user_id=user_id, metadata=metadata)
    except Exception:
        logger.exception("SMTP delivery failed for email type=%s", email_type)
        await _log(recipient, subject, email_type, "FAILED", user_id=user_id, metadata=metadata,
                   error_message="SMTP delivery failed")


class EmailService:
    """Schedules reusable notifications; SMTP stays out of route handlers."""
    def _schedule(self, tasks: BackgroundTasks, recipient: str, subject: str, email_type: str, template: str,
                  context: dict[str, Any], user_id: str | None = None, metadata: dict[str, Any] | None = None) -> None:
        tasks.add_task(_deliver, recipient=recipient, subject=subject, email_type=email_type, template=template,
                       context=context, user_id=user_id, metadata=metadata)

    def send_welcome_email(self, tasks, recipient, name, user_id=None):
        self._schedule(tasks, recipient, "Welcome to KAUSHALYA", "WELCOME", "welcome.html", {"name": name}, user_id)
    def send_verification_email(self, tasks, recipient, name, token, user_id=None):
        self._schedule(tasks, recipient, "Verify your KAUSHALYA account", "EMAIL_VERIFICATION", "verify_email.html",
                       {"name": name, "action_url": f"{get_settings().FRONTEND_URL}/verify-email?token={token}", "action_label": "Verify Email"}, user_id)
    def send_password_reset_email(self, tasks, recipient, name, token, user_id=None):
        self._schedule(tasks, recipient, "Reset your KAUSHALYA password", "PASSWORD_RESET", "password_reset.html",
                       {"name": name, "action_url": f"{get_settings().FRONTEND_URL}/reset-password?token={token}", "action_label": "Reset Password"}, user_id)
    def send_password_changed_email(self, tasks, recipient, name, user_id=None):
        self._schedule(tasks, recipient, "Your KAUSHALYA password was changed", "PASSWORD_CHANGED", "password_changed.html",
                       {"name": name}, user_id)
    def send_job_application_email(self, tasks, recipient, name, details, user_id=None):
        self._schedule(tasks, recipient, "New job application", "JOB_APPLICATION", "job_application.html", {"name": name, "details": details}, user_id)
    def send_job_selection_email(self, tasks, recipient, name, details, user_id=None):
        self._schedule(tasks, recipient, "Congratulations — you have been selected", "JOB_SELECTED", "job_selected.html", {"name": name, "details": details}, user_id)
    def send_job_rejection_email(self, tasks, recipient, name, details, user_id=None):
        self._schedule(tasks, recipient, "Update on your job application", "JOB_REJECTED", "job_rejected.html", {"name": name, "details": details}, user_id)
    def send_training_enrollment_email(self, tasks, recipient, name, details, user_id=None):
        self._schedule(tasks, recipient, "Training enrollment confirmed", "TRAINING_ENROLLMENT", "training_enrollment.html", {"name": name, "details": details}, user_id)
    def send_training_completion_email(self, tasks, recipient, name, details, user_id=None):
        self._schedule(tasks, recipient, "Congratulations on completing your training", "TRAINING_COMPLETION", "training_completion.html", {"name": name, "details": details}, user_id)
    def send_employment_outcome_email(self, tasks, recipient, name, details, user_id=None):
        self._schedule(tasks, recipient, "Employment outcome recorded", "EMPLOYMENT_OUTCOME", "employment_outcome.html", {"name": name, "details": details}, user_id)
    def send_admin_notification(self, tasks, recipient, name, details, user_id=None):
        self._schedule(tasks, recipient, "KAUSHALYA administrative notification", "ADMIN_NOTIFICATION", "admin_notification.html", {"name": name, "details": details}, user_id)
    def send_test_email(self, tasks, recipient, user_id=None):
        self.send_admin_notification(tasks, recipient, "Administrator", {"Message": "SMTP configuration is ready for KAUSHALYA."}, user_id)


email_service = EmailService()
