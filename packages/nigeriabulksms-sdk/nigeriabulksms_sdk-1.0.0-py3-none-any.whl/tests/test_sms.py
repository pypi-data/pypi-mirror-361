import unittest
from unittest.mock import Mock, patch
import requests
from nigeriabulksms_sdk.services.sms import SMS
from nigeriabulksms_sdk.exceptions import NigeriaBulkSMSException


class TestSMS(unittest.TestCase):
    """Test cases for SMS service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_session = Mock()
        self.base_url = "https://portal.nigeriabulksms.com/api/"
        self.username = "test_user"
        self.password = "test_password"
        self.sms_service = SMS(self.mock_session, self.base_url, self.username, self.password)
    
    def test_sms_initialization(self):
        """Test SMS service initialization"""
        self.assertEqual(self.sms_service._session, self.mock_session)
        self.assertEqual(self.sms_service._base_url, self.base_url)
        self.assertEqual(self.sms_service._auth_params["username"], self.username)
        self.assertEqual(self.sms_service._auth_params["password"], self.password)
    
    def test_send_sms_success(self):
        """Test successful SMS sending"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"status": "OK", "message": "SMS sent successfully"}
        mock_response.raise_for_status.return_value = None
        self.mock_session.get.return_value = mock_response
        
        result = self.sms_service.send(
            message="Test message",
            sender="TestSender",
            mobiles=["2348030000000"]
        )
        
        # Verify the result
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["message"], "SMS sent successfully")
        
        # Verify the request was made with correct parameters
        self.mock_session.get.assert_called_once()
        call_args = self.mock_session.get.call_args
        self.assertEqual(call_args[0][0], self.base_url)
        
        params = call_args[1]["params"]
        self.assertEqual(params["message"], "Test message")
        self.assertEqual(params["sender"], "TestSender")
        self.assertEqual(params["mobiles"], "2348030000000")
        self.assertEqual(params["username"], self.username)
        self.assertEqual(params["password"], self.password)
    
    def test_send_sms_with_multiple_mobiles(self):
        """Test SMS sending with multiple mobile numbers"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"status": "OK", "message": "SMS sent successfully"}
        mock_response.raise_for_status.return_value = None
        self.mock_session.get.return_value = mock_response
        
        mobiles = ["2348030000000", "2348030000001", "2348030000002"]
        result = self.sms_service.send(
            message="Test message",
            sender="TestSender",
            mobiles=mobiles
        )
        
        # Verify the mobiles were joined correctly
        call_args = self.mock_session.get.call_args
        params = call_args[1]["params"]
        self.assertEqual(params["mobiles"], "2348030000000,2348030000001,2348030000002")
    
    def test_send_sms_with_single_mobile_string(self):
        """Test SMS sending with a single mobile number as string"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"status": "OK", "message": "SMS sent successfully"}
        mock_response.raise_for_status.return_value = None
        self.mock_session.get.return_value = mock_response
        
        result = self.sms_service.send(
            message="Test message",
            sender="TestSender",
            mobiles="2348030000000"
        )
        
        # Verify the mobiles parameter was handled correctly
        call_args = self.mock_session.get.call_args
        params = call_args[1]["params"]
        self.assertEqual(params["mobiles"], "2348030000000")
    
    def test_send_sms_api_error(self):
        """Test SMS sending with API error response"""
        # Mock error response
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Insufficient funds", "errno": 150}
        mock_response.raise_for_status.return_value = None
        self.mock_session.get.return_value = mock_response
        
        with self.assertRaises(NigeriaBulkSMSException) as context:
            self.sms_service.send(
                message="Test message",
                sender="TestSender",
                mobiles=["2348030000000"]
            )
        
        self.assertEqual(str(context.exception), "Insufficient funds")
        self.assertEqual(context.exception.code, 150)
    
    def test_send_sms_unknown_error(self):
        """Test SMS sending with unknown error format"""
        # Mock response with unknown format
        mock_response = Mock()
        mock_response.json.return_value = {"status": "UNKNOWN", "data": "Some data"}
        mock_response.raise_for_status.return_value = None
        self.mock_session.get.return_value = mock_response
        
        with self.assertRaises(NigeriaBulkSMSException) as context:
            self.sms_service.send(
                message="Test message",
                sender="TestSender",
                mobiles=["2348030000000"]
            )
        
        self.assertEqual(str(context.exception), "Unknown API error or unexpected response format.")
    
    def test_send_sms_http_error(self):
        """Test SMS sending with HTTP request error"""
        # Mock HTTP error
        self.mock_session.get.side_effect = requests.exceptions.RequestException("Connection error")
        
        with self.assertRaises(NigeriaBulkSMSException) as context:
            self.sms_service.send(
                message="Test message",
                sender="TestSender",
                mobiles=["2348030000000"]
            )
        
        self.assertIn("HTTP Request failed", str(context.exception))
    
    def test_send_sms_http_status_error(self):
        """Test SMS sending with HTTP status error"""
        # Mock HTTP status error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        self.mock_session.get.return_value = mock_response
        
        with self.assertRaises(NigeriaBulkSMSException) as context:
            self.sms_service.send(
                message="Test message",
                sender="TestSender",
                mobiles=["2348030000000"]
            )
        
        self.assertIn("HTTP Request failed", str(context.exception))


if __name__ == '__main__':
    unittest.main() 