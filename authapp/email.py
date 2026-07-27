import logging

import resend
from django.conf import settings

logger = logging.getLogger(__name__)


def send_resend_email(*, to, subject, html, text=None):
    """Send an email via Resend. Returns the API response or None on failure."""
    if not settings.RESEND_API_KEY:
        logger.error("RESEND_API_KEY is not configured")
        return None

    resend.api_key = settings.RESEND_API_KEY
    payload = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [to] if isinstance(to, str) else list(to),
        "subject": subject,
        "html": html,
    }
    if text:
        payload["text"] = text

    try:
        return resend.Emails.send(payload)
    except Exception:
        logger.exception("Failed to send email via Resend to %s", to)
        return None
