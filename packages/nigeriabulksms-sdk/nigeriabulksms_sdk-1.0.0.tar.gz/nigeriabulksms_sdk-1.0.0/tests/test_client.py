import unittest
from unittest.mock import Mock, patch
from nigeriabulksms_sdk import NigeriaBulkSMSClient
from nigeriabulksms_sdk.services.sms import SMS
from nigeriabulksms_sdk.services.call import Call
from nigeriabulksms_sdk.services.audio import Audio
from nigeriabulksms_sdk.services.data import Data


class TestNigeriaBulkSMSClient(unittest.TestCase):
    """Test cases for NigeriaBulkSMSClient class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.username = "test_user"
        self.password = "test_password"
        self.client = NigeriaBulkSMSClient(self.username, self.password)
    
    def test_client_initialization(self):
        """Test client initialization"""
        self.assertEqual(self.client.username, self.username)
        self.assertEqual(self.client.password, self.password)
        self.assertEqual(self.client.base_url, "https://portal.nigeriabulksms.com/api/")
        
        # Check that all services are initialized
        self.assertIsInstance(self.client.sms, SMS)
        self.assertIsInstance(self.client.call, Call)
        self.assertIsInstance(self.client.audio, Audio)
        self.assertIsInstance(self.client.data, Data)
    
    def test_client_initialization_with_custom_base_url(self):
        """Test client initialization with custom base URL"""
        custom_url = "https://custom.api.com/"
        client = NigeriaBulkSMSClient(self.username, self.password, base_url=custom_url)
        self.assertEqual(client.base_url, custom_url)
    
    def test_get_auth_params(self):
        """Test the _get_auth_params method"""
        auth_params = self.client._get_auth_params()
        expected_params = {
            "username": self.username,
            "password": self.password,
        }
        self.assertEqual(auth_params, expected_params)


if __name__ == '__main__':
    unittest.main() 