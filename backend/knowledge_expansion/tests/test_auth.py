import unittest
from unittest.mock import patch, MagicMock
from backend.knowledge_expansion.authentication import get_auth_headers, verify_auth, AuthenticationError

class TestAuthLayer(unittest.TestCase):
    """Unit tests for the API authentication layer."""

    @patch("backend.knowledge_expansion.authentication.LENS_API_KEY", "mock_key_123")
    def test_get_auth_headers_success(self):
        """Verifies correct headers are generated when the API key is present."""
        headers = get_auth_headers()
        self.assertEqual(headers["Authorization"], "Bearer mock_key_123")
        self.assertEqual(headers["Content-Type"], "application/json")

    @patch("backend.knowledge_expansion.authentication.LENS_API_KEY", "")
    def test_get_auth_headers_missing(self):
        """Verifies AuthenticationError is raised if the API key is empty."""
        with self.assertRaises(AuthenticationError):
            get_auth_headers()

    @patch("httpx.Client.post")
    @patch("backend.knowledge_expansion.authentication.LENS_API_KEY", "mock_key_123")
    def test_verify_auth_success(self, mock_post):
        """Verifies verify_auth returns True when the server returns HTTP 200."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp
        
        self.assertTrue(verify_auth())

    @patch("httpx.Client.post")
    @patch("backend.knowledge_expansion.authentication.LENS_API_KEY", "mock_key_123")
    def test_verify_auth_denied(self, mock_post):
        """Verifies verify_auth returns False on HTTP 401/403 authorization failures."""
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_post.return_value = mock_resp
        
        self.assertFalse(verify_auth())

if __name__ == "__main__":
    unittest.main()
