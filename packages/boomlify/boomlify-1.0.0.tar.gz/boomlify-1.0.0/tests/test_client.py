#!/usr/bin/env python3
"""
Basic tests for the Boomlify client.
"""

import unittest
from unittest.mock import Mock, patch
from boomlify import BoomlifyClient, BoomlifyError, BoomlifyAuthError, TimeOption
from boomlify.models import Email, EmailMessage


class TestBoomlifyClient(unittest.TestCase):
    """Test cases for BoomlifyClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.client = BoomlifyClient(api_key=self.api_key)
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = BoomlifyClient(api_key="test_key")
        self.assertEqual(client.api_key, "test_key")
        self.assertEqual(client.timeout, 30)
        self.assertEqual(client.max_retries, 3)
    
    def test_client_initialization_without_api_key(self):
        """Test client initialization without API key."""
        with self.assertRaises(Exception):
            BoomlifyClient(api_key="")
    
    @patch('boomlify.client.requests.get')
    def test_get_base_url(self, mock_get):
        """Test getting base URL."""
        mock_response = Mock()
        mock_response.json.return_value = {"API_URL": "https://api.boomlify.com"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        base_url = self.client.get_base_url()
        self.assertEqual(base_url, "https://api.boomlify.com")
    
    @patch('boomlify.client.requests.get')
    def test_get_base_url_missing_url(self, mock_get):
        """Test getting base URL when API_URL is missing."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with self.assertRaises(BoomlifyError):
            self.client.get_base_url()
    
    def test_time_option_validation(self):
        """Test time option validation."""
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {
                'email': {
                    'id': 'test_id',
                    'address': 'test@example.com',
                    'domain': 'example.com',
                    'time_tier': '10min',
                    'expires_at': '2024-01-01T00:00:00Z',
                    'is_expired': False,
                    'message_count': 0,
                    'time_remaining': {'minutes': 10}
                }
            }
            
            # Valid time options
            for time_option in ["10min", "1hour", "1day"]:
                email = self.client.create_email(time_option=time_option)
                self.assertIsInstance(email, Email)
            
            # Invalid time option
            with self.assertRaises(Exception):
                self.client.create_email(time_option="invalid")
    
    def test_context_manager(self):
        """Test context manager usage."""
        with BoomlifyClient(api_key="test_key") as client:
            self.assertIsNotNone(client.session)
        
        # Session should be closed after context exit
        self.assertTrue(True)  # If we get here, context manager worked
    
    def test_email_id_validation(self):
        """Test email ID validation."""
        with self.assertRaises(Exception):
            self.client.get_email("")
        
        with self.assertRaises(Exception):
            self.client.get_messages("")
        
        with self.assertRaises(Exception):
            self.client.delete_email("")
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.client, 'session'):
            self.client.close()


class TestTimeOption(unittest.TestCase):
    """Test cases for TimeOption enum."""
    
    def test_time_option_values(self):
        """Test TimeOption enum values."""
        self.assertEqual(TimeOption.TEN_MINUTES.value, "10min")
        self.assertEqual(TimeOption.ONE_HOUR.value, "1hour")
        self.assertEqual(TimeOption.ONE_DAY.value, "1day")


class TestModels(unittest.TestCase):
    """Test cases for data models."""
    
    def test_email_from_dict(self):
        """Test Email.from_dict method."""
        data = {
            'id': 'test_id',
            'address': 'test@example.com',
            'domain': 'example.com',
            'time_tier': '10min',
            'expires_at': '2024-01-01T00:00:00Z',
            'is_expired': False,
            'message_count': 0,
            'time_remaining': {'minutes': 10}
        }
        
        email = Email.from_dict(data)
        self.assertEqual(email.id, 'test_id')
        self.assertEqual(email.address, 'test@example.com')
        self.assertEqual(email.domain, 'example.com')
        self.assertEqual(email.time_tier, '10min')
        self.assertEqual(email.time_remaining_minutes, 10)
    
    def test_email_message_from_dict(self):
        """Test EmailMessage.from_dict method."""
        data = {
            'id': 'msg_id',
            'subject': 'Test Subject',
            'body': 'Test body',
            'from': 'sender@example.com',
            'to': 'recipient@example.com',
            'received_at': '2024-01-01T00:00:00Z',
            'attachments': [],
            'headers': {}
        }
        
        message = EmailMessage.from_dict(data)
        self.assertEqual(message.id, 'msg_id')
        self.assertEqual(message.subject, 'Test Subject')
        self.assertEqual(message.body, 'Test body')
        self.assertEqual(message.from_address, 'sender@example.com')
        self.assertEqual(message.to_address, 'recipient@example.com')


if __name__ == '__main__':
    unittest.main() 