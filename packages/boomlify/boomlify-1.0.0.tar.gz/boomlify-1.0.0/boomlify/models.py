"""
Data models for Boomlify API responses and requests.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class TimeOption(Enum):
    """Available time options for email expiration."""
    TEN_MINUTES = "10min"
    ONE_HOUR = "1hour"
    ONE_DAY = "1day"


@dataclass
class Email:
    """Represents a temporary email address."""
    
    id: str
    address: str
    domain: str
    time_tier: str
    expires_at: str
    is_expired: bool
    message_count: int
    time_remaining_minutes: int
    
    def __post_init__(self):
        """Convert string timestamps to datetime objects if needed."""
        if isinstance(self.expires_at, str):
            try:
                # Handle ISO format timestamps
                self.expires_at_dt = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
            except ValueError:
                self.expires_at_dt = None
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Email':
        """Create an Email instance from API response data."""
        return cls(
            id=data['id'],
            address=data['address'],
            domain=data['domain'],
            time_tier=data['time_tier'],
            expires_at=data['expires_at'],
            is_expired=data['is_expired'],
            message_count=data['message_count'],
            time_remaining_minutes=data['time_remaining']['minutes']
        )


@dataclass
class EmailMessage:
    """Represents an email message."""
    
    id: str
    subject: str
    body: str
    from_address: str
    to_address: str
    received_at: str
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert string timestamps to datetime objects if needed."""
        if isinstance(self.received_at, str):
            try:
                self.received_at_dt = datetime.fromisoformat(self.received_at.replace('Z', '+00:00'))
            except ValueError:
                self.received_at_dt = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailMessage':
        """Create an EmailMessage instance from API response data."""
        return cls(
            id=data['id'],
            subject=data['subject'],
            body=data['body'],
            from_address=data['from'],
            to_address=data['to'],
            received_at=data['received_at'],
            attachments=data.get('attachments', []),
            headers=data.get('headers', {})
        )


@dataclass
class EmailList:
    """Represents a list of emails with metadata."""
    
    emails: List[Email]
    total_count: int
    success: bool
    message: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailList':
        """Create an EmailList instance from API response data."""
        emails = [Email.from_dict(email_data) for email_data in data.get('emails_list', [])]
        return cls(
            emails=emails,
            total_count=data['total_count'],
            success=data['success'],
            message=data['message']
        )


@dataclass
class MessageList:
    """Represents a list of messages with metadata."""
    
    messages: List[EmailMessage]
    total_messages: int
    first_message_subject: Optional[str] = None
    first_message_body: Optional[str] = None
    first_message_from: Optional[str] = None
    success: bool = True
    message: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageList':
        """Create a MessageList instance from API response data."""
        messages = [EmailMessage.from_dict(msg_data) for msg_data in data.get('messages_list', [])]
        return cls(
            messages=messages,
            total_messages=data['total_messages'],
            first_message_subject=data.get('first_message_subject'),
            first_message_body=data.get('first_message_body'),
            first_message_from=data.get('first_message_from'),
            success=data['success'],
            message=data['message']
        )


@dataclass
class AccountInfo:
    """Represents account information."""
    
    api_key: str
    plan: str
    daily_limit: int
    emails_created_today: int
    remaining_emails: int
    success: bool
    message: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountInfo':
        """Create an AccountInfo instance from API response data."""
        return cls(
            api_key=data['api_key'],
            plan=data['plan'],
            daily_limit=data['daily_limit'],
            emails_created_today=data['emails_created_today'],
            remaining_emails=data['remaining_emails'],
            success=data['success'],
            message=data['message']
        )


@dataclass
class UsageInfo:
    """Represents usage statistics."""
    
    total_emails_created: int
    total_messages_received: int
    emails_today: int
    messages_today: int
    daily_limit: int
    remaining_emails: int
    success: bool
    message: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsageInfo':
        """Create a UsageInfo instance from API response data."""
        return cls(
            total_emails_created=data['total_emails_created'],
            total_messages_received=data['total_messages_received'],
            emails_today=data['emails_today'],
            messages_today=data['messages_today'],
            daily_limit=data['daily_limit'],
            remaining_emails=data['remaining_emails'],
            success=data['success'],
            message=data['message']
        )


@dataclass
class CreateEmailResponse:
    """Response from creating an email."""
    
    email: Email
    success: bool
    message: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CreateEmailResponse':
        """Create a CreateEmailResponse instance from API response data."""
        return cls(
            email=Email.from_dict(data),
            success=data['success'],
            message=data['message']
        ) 