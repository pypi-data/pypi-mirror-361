"""
Main Boomlify client class for interacting with the temporary email API.
"""

import json
import time
from typing import Optional, Dict, Any, Union, List
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .models import (
    Email, EmailMessage, EmailList, MessageList, AccountInfo, UsageInfo, 
    TimeOption, CreateEmailResponse
)
from .exceptions import (
    BoomlifyError, BoomlifyAPIError, BoomlifyAuthError, BoomlifyNotFoundError,
    BoomlifyRateLimitError, BoomlifyTimeoutError, BoomlifyValidationError
)


class BoomlifyClient:
    """
    Main client for interacting with the Boomlify temporary email API.
    
    This client provides methods to create, manage, and monitor temporary emails
    with automatic base URL rotation and comprehensive error handling.
    
    Args:
        api_key: Your Boomlify API key
        base_url: Optional base URL override (auto-fetched if not provided)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retries for failed requests (default: 3)
        
    Example:
        >>> client = BoomlifyClient(api_key="your_api_key")
        >>> email = client.create_email(time_option="10min")
        >>> print(f"Created email: {email.address}")
        
        >>> messages = client.get_messages(email.id)
        >>> print(f"Found {len(messages.messages)} messages")
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        if not api_key:
            raise BoomlifyValidationError("API key is required")
            
        self.api_key = api_key
        self._base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Default headers
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'boomlify-python/1.0.0'
        })
    
    def get_base_url(self) -> str:
        """
        Get the current API base URL with automatic rotation.
        
        Returns:
            The current API base URL
            
        Raises:
            BoomlifyError: If unable to fetch the base URL
        """
        try:
            # Remove API key from headers temporarily for config request
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36'
            }
            
            response = requests.get(
                "https://gen.boomlify.com/api-config.json",
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            config_data = response.json()
            api_url = config_data.get('API_URL')
            
            if not api_url:
                raise BoomlifyError("API URL not found in configuration")
                
            self._base_url = api_url
            return api_url
            
        except requests.exceptions.RequestException as e:
            raise BoomlifyError(f"Failed to fetch base URL: {str(e)}")
    
    @property
    def base_url(self) -> str:
        """Get the base URL, fetching it if not already cached."""
        if not self._base_url:
            return self.get_base_url()
        return self._base_url
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: URL parameters
            data: Request body data
            
        Returns:
            Parsed JSON response
            
        Raises:
            BoomlifyError: For various API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.timeout
            )
            
            # Handle different HTTP status codes
            if response.status_code == 401:
                raise BoomlifyAuthError("Invalid API key", response.status_code)
            elif response.status_code == 403:
                raise BoomlifyAuthError("Access forbidden", response.status_code)
            elif response.status_code == 404:
                raise BoomlifyNotFoundError("Resource not found", response.status_code)
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After')
                retry_after_int = int(retry_after) if retry_after else None
                raise BoomlifyRateLimitError(
                    "Rate limit exceeded", 
                    response.status_code, 
                    retry_after_int
                )
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    message = error_data.get('message', f'HTTP {response.status_code}')
                except:
                    message = f'HTTP {response.status_code}'
                raise BoomlifyAPIError(message, response.status_code)
            
            # Parse JSON response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                raise BoomlifyError("Invalid JSON response from API")
            
            # Check for API-level errors
            if not response_data.get('success', True):
                message = response_data.get('message', 'Unknown API error')
                raise BoomlifyAPIError(message, response.status_code, response_data)
            
            return response_data
            
        except requests.exceptions.Timeout:
            raise BoomlifyTimeoutError("Request timed out")
        except requests.exceptions.RequestException as e:
            raise BoomlifyError(f"Request failed: {str(e)}")
    
    def create_email(
        self, 
        time_option: Union[str, TimeOption] = "10min",
        custom_domain: Optional[str] = None
    ) -> Email:
        """
        Create a new temporary email address.
        
        Args:
            time_option: Email lifespan ('10min', '1hour', '1day')
            custom_domain: Optional custom domain (must be verified)
            
        Returns:
            Email object with the created email details
            
        Raises:
            BoomlifyError: If email creation fails
        """
        # Validate time option
        if isinstance(time_option, TimeOption):
            time_option = time_option.value
        
        if time_option not in ["10min", "1hour", "1day"]:
            raise BoomlifyValidationError(
                "time_option must be '10min', '1hour', or '1day'"
            )
        
        # Build endpoint with parameters
        endpoint = f"/api/v1/emails/create?time={time_option}"
        if custom_domain:
            endpoint += f"&domain={custom_domain}"
        
        response_data = self._make_request("POST", endpoint)
        
        # Extract email data
        email_data = response_data.get('email', {})
        return Email.from_dict(email_data)
    
    def list_emails(
        self,
        include_expired: bool = False,
        limit: int = 10
    ) -> EmailList:
        """
        List your temporary emails.
        
        Args:
            include_expired: Whether to include expired emails
            limit: Maximum number of emails to return
            
        Returns:
            EmailList object with emails and metadata
        """
        params = {
            'include_expired': str(include_expired).lower(),
            'limit': str(limit)
        }
        
        response_data = self._make_request("GET", "/api/v1/emails", params=params)
        return EmailList.from_dict(response_data)
    
    def get_email(self, email_id: str) -> Email:
        """
        Get details of a specific email.
        
        Args:
            email_id: The email ID
            
        Returns:
            Email object with email details
        """
        if not email_id:
            raise BoomlifyValidationError("Email ID is required")
        
        endpoint = f"/api/v1/emails/{email_id}"
        response_data = self._make_request("GET", endpoint)
        
        email_data = response_data.get('email', {})
        return Email.from_dict(email_data)
    
    def get_messages(
        self,
        email_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> MessageList:
        """
        Get messages for a specific email.
        
        Args:
            email_id: The email ID
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            MessageList object with messages and metadata
        """
        if not email_id:
            raise BoomlifyValidationError("Email ID is required")
        
        params = {
            'limit': str(limit),
            'offset': str(offset)
        }
        
        endpoint = f"/api/v1/emails/{email_id}/messages"
        response_data = self._make_request("GET", endpoint, params=params)
        
        return MessageList.from_dict(response_data)
    
    def delete_email(self, email_id: str) -> bool:
        """
        Delete a temporary email.
        
        Args:
            email_id: The email ID to delete
            
        Returns:
            True if deletion was successful
        """
        if not email_id:
            raise BoomlifyValidationError("Email ID is required")
        
        endpoint = f"/api/v1/emails/{email_id}"
        response_data = self._make_request("DELETE", endpoint)
        
        return response_data.get('success', False)
    
    def get_usage(self) -> UsageInfo:
        """
        Get usage statistics for your account.
        
        Returns:
            UsageInfo object with usage details
        """
        response_data = self._make_request("GET", "/api/v1/usage")
        return UsageInfo.from_dict(response_data)
    
    def get_account(self) -> AccountInfo:
        """
        Get account information.
        
        Returns:
            AccountInfo object with account details
        """
        response_data = self._make_request("GET", "/api/v1/account")
        return AccountInfo.from_dict(response_data)
    
    def wait_for_mail(
        self,
        email_id: str,
        timeout_seconds: int = 300,
        check_interval: int = 5
    ) -> Optional[EmailMessage]:
        """
        Wait for new emails to arrive.
        
        Args:
            email_id: The email ID to monitor
            timeout_seconds: Maximum time to wait in seconds
            check_interval: How often to check for new messages in seconds
            
        Returns:
            EmailMessage if new message arrives, None if timeout
        """
        if not email_id:
            raise BoomlifyValidationError("Email ID is required")
        
        end_time = time.time() + timeout_seconds
        
        while time.time() < end_time:
            try:
                messages = self.get_messages(email_id, limit=1)
                if messages.messages:
                    return messages.messages[0]
                    
                time.sleep(check_interval)
            except BoomlifyError:
                # Continue waiting even if there's an error
                time.sleep(check_interval)
        
        return None
    
    def refresh_base_url(self) -> str:
        """
        Force refresh of the base URL.
        
        Returns:
            The new base URL
        """
        self._base_url = None
        return self.get_base_url()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            self.session.close()
    
    def close(self):
        """Close the HTTP session."""
        if self.session:
            self.session.close() 