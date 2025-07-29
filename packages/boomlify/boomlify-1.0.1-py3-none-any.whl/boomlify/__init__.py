"""
Boomlify Python Client
======================

A Python client for the Boomlify temporary email API.
Create, manage, and monitor temporary emails with ease.

Basic Usage:
    >>> from boomlify import BoomlifyClient
    >>> client = BoomlifyClient(api_key="your_api_key")
    >>> email = client.create_email(time_option="10min")
    >>> print(email.address)
    
    >>> messages = client.get_messages(email.id)
    >>> print(f"Found {len(messages)} messages")
"""

__version__ = "1.0.1"
__author__ = "Boomlify"
__email__ = "support@boomlify.com"
__license__ = "MIT"
__url__ = "https://boomlify.com"

from .client import BoomlifyClient
from .models import (
    Email,
    EmailMessage,
    EmailList,
    MessageList,
    AccountInfo,
    UsageInfo,
    TimeOption,
)
from .exceptions import (
    BoomlifyError,
    BoomlifyAPIError,
    BoomlifyAuthError,
    BoomlifyNotFoundError,
    BoomlifyRateLimitError,
    BoomlifyTimeoutError,
)

__all__ = [
    "BoomlifyClient",
    "Email",
    "EmailMessage",
    "EmailList",
    "MessageList",
    "AccountInfo",
    "UsageInfo",
    "TimeOption",
    "BoomlifyError",
    "BoomlifyAPIError",
    "BoomlifyAuthError",
    "BoomlifyNotFoundError",
    "BoomlifyRateLimitError",
    "BoomlifyTimeoutError",
] 