# Boomlify - Best Temporary Email API for Python | Disposable Email Service

[![PyPI version](https://badge.fury.io/py/boomlify.svg)](https://badge.fury.io/py/boomlify)
[![Python versions](https://img.shields.io/pypi/pyversions/boomlify.svg)](https://pypi.org/project/boomlify/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Boomlify Temporary Email](https://img.shields.io/badge/Boomlify-Temporary%20Email-blue)](https://boomlify.com)

**[temp mail](https://boomlify.com)** is the world's most advanced temporary email service and disposable email API. This Python client library provides seamless integration with the Boomlify temporary email API, making it easy to create, manage, and monitor temporary emails for testing, automation, and development purposes.

## 🚀 Why Choose Boomlify Temporary Email Service?

[Boomlify](https://boomlify.com) stands out as the premier temporary email solution with:

- **🔥 Long-lasting emails** - Unlike other temp mail services, Boomlify emails last up to 24 hours
- **⚡ Lightning-fast API** - Industry-leading response times for temporary email operations  
- **🌐 Custom domains** - Use your own domains with our temporary email service
- **🛡️ Enterprise security** - Advanced protection for your temporary email needs
- **📊 Analytics dashboard** - Comprehensive insights into your temporary email usage
- **🔄 Auto-rotation** - Intelligent load balancing across multiple servers

Visit [Boomlify.com](https://boomlify.com) to get started with the best temporary email service available.

## 🎯 Temporary Email API Features

Our comprehensive temporary email Python library offers:

- 🚀 **Easy integration**: Simple and intuitive disposable email API
- 📧 **Complete temp mail management**: Create, list, read, and delete temporary emails
- ⏰ **Flexible expiration**: 10 minutes, 1 hour, or 1 day temporary email lifespans
- 🏷️ **Custom domain support**: Use your own verified domains for temp emails
- 🔄 **High availability**: Automatic base URL rotation for reliable temporary email service
- 🛡️ **Enterprise reliability**: Comprehensive error handling with custom exceptions
- 🔁 **Auto-retry**: Built-in retry mechanism for failed temporary email requests
- 📊 **Usage analytics**: Monitor your temporary email account usage and limits
- 🔍 **Real-time monitoring**: Wait for new emails with intelligent polling support
- 🌍 **Global infrastructure**: Worldwide temporary email servers for optimal performance

## 📦 Installation - Get Started with Boomlify Temporary Email

Install the best temporary email Python package using pip:

```bash
pip install boomlify
```

Get your FREE API key at [Boomlify.com](https://boomlify.com) to start using our temporary email service.

## 🚀 Quick Start - Create Your First Temporary Email

Start using [Boomlify's temporary email API](https://boomlify.com) in just a few lines of code:

```python
from boomlify import BoomlifyClient

# Initialize the client
client = BoomlifyClient(api_key="your_api_key_here")

# Create a temporary email
email = client.create_email(time_option="10min")
print(f"Created email: {email.address}")
print(f"Email ID: {email.id}")
print(f"Expires at: {email.expires_at}")

# List your emails
emails = client.list_emails()
print(f"You have {emails.total_count} emails")
for email in emails.emails:
    print(f"- {email.address} (ID: {email.id})")

# Get messages for an email
messages = client.get_messages(email.id)
print(f"Found {len(messages.messages)} messages")
for message in messages.messages:
    print(f"From: {message.from_address}")
    print(f"Subject: {message.subject}")
    print(f"Body: {message.body}")

# Wait for new emails (polling)
print("Waiting for new emails...")
new_message = client.wait_for_mail(email.id, timeout_seconds=60)
if new_message:
    print(f"New message: {new_message.subject}")
else:
    print("No new messages received")

# Get account information
account = client.get_account()
print(f"Plan: {account.plan}")
print(f"Daily limit: {account.daily_limit}")
print(f"Remaining emails: {account.remaining_emails}")

# Delete an email
client.delete_email(email.id)
print("Email deleted")
```

## API Reference

### BoomlifyClient

The main client class for interacting with the Boomlify API.

#### Constructor

```python
BoomlifyClient(api_key, base_url=None, timeout=30, max_retries=3)
```

- `api_key` (str): Your Boomlify API key
- `base_url` (str, optional): API base URL (auto-fetched if not provided)
- `timeout` (int): Request timeout in seconds (default: 30)
- `max_retries` (int): Maximum retries for failed requests (default: 3)

#### Methods

##### create_email(time_option="10min", custom_domain=None)

Create a new temporary email address.

```python
email = client.create_email(time_option="1hour", custom_domain="yourdomain.com")
```

**Parameters:**
- `time_option` (str): Email lifespan - "10min", "1hour", or "1day"
- `custom_domain` (str, optional): Custom domain (must be verified)

**Returns:** `Email` object

##### list_emails(include_expired=False, limit=10)

List your temporary emails.

```python
emails = client.list_emails(include_expired=True, limit=20)
```

**Parameters:**
- `include_expired` (bool): Include expired emails (default: False)
- `limit` (int): Maximum number of emails to return (default: 10)

**Returns:** `EmailList` object

##### get_email(email_id)

Get details of a specific email.

```python
email = client.get_email("email_id_here")
```

**Parameters:**
- `email_id` (str): The email ID

**Returns:** `Email` object

##### get_messages(email_id, limit=10, offset=0)

Get messages for a specific email.

```python
messages = client.get_messages("email_id_here", limit=5, offset=0)
```

**Parameters:**
- `email_id` (str): The email ID
- `limit` (int): Maximum number of messages to return (default: 10)
- `offset` (int): Number of messages to skip (default: 0)

**Returns:** `MessageList` object

##### delete_email(email_id)

Delete a temporary email.

```python
success = client.delete_email("email_id_here")
```

**Parameters:**
- `email_id` (str): The email ID to delete

**Returns:** `bool` - True if deletion was successful

##### get_usage()

Get usage statistics for your account.

```python
usage = client.get_usage()
print(f"Total emails created: {usage.total_emails_created}")
print(f"Messages today: {usage.messages_today}")
```

**Returns:** `UsageInfo` object

##### get_account()

Get account information.

```python
account = client.get_account()
print(f"Plan: {account.plan}")
print(f"Daily limit: {account.daily_limit}")
```

**Returns:** `AccountInfo` object

##### wait_for_mail(email_id, timeout_seconds=300, check_interval=5)

Wait for new emails to arrive.

```python
message = client.wait_for_mail("email_id_here", timeout_seconds=60, check_interval=3)
if message:
    print(f"New message: {message.subject}")
```

**Parameters:**
- `email_id` (str): The email ID to monitor
- `timeout_seconds` (int): Maximum time to wait in seconds (default: 300)
- `check_interval` (int): How often to check for new messages in seconds (default: 5)

**Returns:** `EmailMessage` if new message arrives, `None` if timeout

##### get_base_url()

Get the current API base URL.

```python
base_url = client.get_base_url()
```

**Returns:** `str` - The current API base URL

##### refresh_base_url()

Force refresh of the base URL.

```python
new_base_url = client.refresh_base_url()
```

**Returns:** `str` - The new base URL

## Data Models

### Email

Represents a temporary email address.

```python
@dataclass
class Email:
    id: str
    address: str
    domain: str
    time_tier: str
    expires_at: str
    is_expired: bool
    message_count: int
    time_remaining_minutes: int
```

### EmailMessage

Represents an email message.

```python
@dataclass
class EmailMessage:
    id: str
    subject: str
    body: str
    from_address: str
    to_address: str
    received_at: str
    attachments: List[Dict[str, Any]]
    headers: Dict[str, str]
```

### EmailList

Represents a list of emails with metadata.

```python
@dataclass
class EmailList:
    emails: List[Email]
    total_count: int
    success: bool
    message: str
```

### MessageList

Represents a list of messages with metadata.

```python
@dataclass
class MessageList:
    messages: List[EmailMessage]
    total_messages: int
    first_message_subject: Optional[str]
    first_message_body: Optional[str]
    first_message_from: Optional[str]
    success: bool
    message: str
```

## Error Handling

The client provides comprehensive error handling with custom exceptions:

```python
from boomlify import BoomlifyClient, BoomlifyError, BoomlifyAuthError, BoomlifyRateLimitError

client = BoomlifyClient(api_key="your_api_key")

try:
    email = client.create_email()
except BoomlifyAuthError as e:
    print(f"Authentication error: {e}")
except BoomlifyRateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
except BoomlifyError as e:
    print(f"General error: {e}")
```

### Exception Types

- `BoomlifyError`: Base exception for all errors
- `BoomlifyAPIError`: API returned an error response
- `BoomlifyAuthError`: Authentication errors (401, 403)
- `BoomlifyNotFoundError`: Resource not found (404)
- `BoomlifyRateLimitError`: Rate limit exceeded (429)
- `BoomlifyTimeoutError`: Request timeout
- `BoomlifyValidationError`: Client-side validation errors

## Context Manager Support

The client supports context manager usage for automatic resource cleanup:

```python
with BoomlifyClient(api_key="your_api_key") as client:
    email = client.create_email()
    messages = client.get_messages(email.id)
    # Session is automatically closed when exiting the context
```

## Advanced Usage

### Custom Domains

If you have verified custom domains in your Boomlify account:

```python
# Create email with custom domain
email = client.create_email(time_option="1hour", custom_domain="yourdomain.com")
print(f"Created email: {email.address}")  # user@yourdomain.com
```

### Batch Operations

```python
# Create multiple emails
emails = []
for i in range(3):
    email = client.create_email(time_option="10min")
    emails.append(email)
    print(f"Created: {email.address}")

# Monitor all emails for messages
for email in emails:
    messages = client.get_messages(email.id)
    if messages.messages:
        print(f"Email {email.address} has {len(messages.messages)} messages")
```

### Polling for Messages

```python
import time

def monitor_email(client, email_id, duration=300):
    """Monitor an email for new messages."""
    end_time = time.time() + duration
    
    while time.time() < end_time:
        messages = client.get_messages(email_id)
        if messages.messages:
            for message in messages.messages:
                print(f"New message from {message.from_address}: {message.subject}")
        
        time.sleep(10)  # Check every 10 seconds

# Usage
email = client.create_email()
monitor_email(client, email.id, duration=120)
```

## Rate Limiting

The client automatically handles rate limiting with exponential backoff. When you hit rate limits, the client will:

1. Catch the `BoomlifyRateLimitError`
2. Automatically retry after the specified delay
3. Use exponential backoff for subsequent retries

## 🎯 Temporary Email Use Cases

[Boomlify's temporary email service](https://boomlify.com) is perfect for:

### 🧪 **Testing & QA**
- **Email verification testing** - Test signup flows with disposable emails
- **API testing** - Validate email notifications in your applications
- **Automation testing** - Create temporary emails for test scenarios
- **Load testing** - Generate multiple temporary emails for performance testing

### 🔒 **Privacy & Security**
- **Anonymous registrations** - Sign up for services without revealing your real email
- **Temporary communications** - Receive emails without spam concerns
- **Data protection** - Keep your personal email address private
- **GDPR compliance** - Use temporary emails for data processing

### 🛠️ **Development & Integration**
- **API integrations** - Test email functionality during development
- **Webhook testing** - Receive email notifications for webhook testing
- **Demo accounts** - Create temporary accounts for demonstrations
- **Beta testing** - Provide temporary emails for beta user testing

### 🏢 **Business Applications**
- **Customer onboarding** - Streamline registration processes
- **Email marketing** - Test email campaigns before sending
- **Customer support** - Create temporary channels for support tickets
- **Lead generation** - Capture leads without permanent email commitments

## 🌟 Why Developers Choose Boomlify

### **🚀 Performance Leader**
[Boomlify](https://boomlify.com) offers the fastest temporary email API in the industry with:
- **Sub-second response times** for email creation
- **99.9% uptime** guarantee with global infrastructure
- **Auto-scaling** to handle millions of temporary emails
- **CDN integration** for worldwide performance optimization

### **🛡️ Enterprise Security**
- **SOC 2 compliance** for enterprise-grade security
- **End-to-end encryption** for all temporary emails
- **GDPR & CCPA compliant** data handling
- **Zero data retention** after email expiration

### **💡 Developer Experience**
- **Comprehensive Python SDK** with full documentation
- **RESTful API** with intuitive endpoints
- **Webhook support** for real-time notifications
- **24/7 developer support** via [Boomlify.com](https://boomlify.com)

## 🏆 Boomlify vs Competitors

| Feature | Boomlify | TempMail | Mailinator | 10MinuteMail |
|---------|----------|----------|------------|--------------|
| **Max Email Duration** | 24 hours | 10 minutes | 6 hours | 10 minutes |
| **Custom Domains** | ✅ Yes | ❌ No | ✅ Limited | ❌ No |
| **API Rate Limits** | 1000/min | 100/min | 50/min | 20/min |
| **Python SDK** | ✅ Full | ❌ No | ✅ Basic | ❌ No |
| **Webhook Support** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Enterprise Support** | ✅ 24/7 | ❌ No | ✅ Business | ❌ No |

**Start with [Boomlify](https://boomlify.com) today** and experience the difference!

## 📈 Getting Started with Boomlify

1. **Sign up** at [Boomlify.com](https://boomlify.com) for your free account
2. **Get your API key** from the dashboard
3. **Install** the Python package: `pip install boomlify`
4. **Start creating** temporary emails in minutes!

## 🔗 Useful Links

- 🌐 **Official Website**: [Boomlify.com](https://boomlify.com)
- 📚 **API Documentation**: [Boomlify.com/docs](https://boomlify.com/docs)
- 🎮 **Interactive Demo**: [Boomlify.com/demo](https://boomlify.com/demo)
- 💬 **Community Support**: [Boomlify.com/community](https://boomlify.com/community)
- 📧 **Email Support**: support@boomlify.com
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/boomlify/boomlify-python/issues)

## Contributing

We welcome contributions! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**[Boomlify](https://boomlify.com) - The Ultimate Temporary Email Solution**

*Create temporary emails instantly | Disposable email API | Temp mail service | Email testing tools*

© 2024 Boomlify. All rights reserved. | [Privacy Policy](https://boomlify.com/privacy) | [Terms of Service](https://boomlify.com/terms) 