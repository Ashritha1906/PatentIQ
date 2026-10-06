import unittest
from unittest.mock import patch, MagicMock
import httpx
from backend.knowledge_expansion.lens_client import LensPatentClient, LensRateLimitError, LensClientError

class TestFetchEngine(unittest.TestCase):
    """Unit tests for the patent fetch client and retry engines."""

    @patch("httpx.Client.post")
    @patch("backend.knowledge_expansion.authentication.LENS_API_KEY", "mock_key")
    def test_search_by_keyword_payload(self, mock_post):
        """Verifies search payload query structures and parameters."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"total": 5, "results": []}
        mock_post.return_value = mock_resp

        client = LensPatentClient()
        res = client.search_by_keyword("wearable sensors", size=5)
        
        self.assertEqual(res["total"], 5)
        # Verify post payload arguments
        args, kwargs = mock_post.call_args
        payload = kwargs.get("json", {})
        self.assertEqual(payload["size"], 5)
        self.assertIn("query_string", payload["query"])

    @patch("backend.knowledge_expansion.lens_client.time.sleep") # speed up tests by skipping actual sleep delays
    @patch("httpx.Client.post")
    @patch("backend.knowledge_expansion.authentication.LENS_API_KEY", "mock_key")
    def test_rate_limit_backoff_recovery(self, mock_post, mock_sleep):
        """Verifies that the client retries on HTTP 429 and eventually recovers on 200."""
        # Setup mocks: first returns 429, second returns 200
        resp_429 = MagicMock()
        resp_429.status_code = 429
        
        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.json.return_value = {"results": [{"lens_id": "1"}]}
        
        mock_post.side_effect = [resp_429, resp_200]
        
        client = LensPatentClient()
        res = client.search_by_keyword("consensus")
        
        self.assertEqual(len(res["results"]), 1)
        self.assertEqual(mock_post.call_count, 2)
        mock_sleep.assert_called_once()

    @patch("backend.knowledge_expansion.lens_client.time.sleep")
    @patch("httpx.Client.post")
    @patch("backend.knowledge_expansion.authentication.LENS_API_KEY", "mock_key")
    def test_rate_limit_exhausted(self, mock_post, mock_sleep):
        """Verifies that LensRateLimitError is raised after max rate limit retries."""
        resp_429 = MagicMock()
        resp_429.status_code = 429
        mock_post.return_value = resp_429
        
        client = LensPatentClient()
        with self.assertRaises(LensRateLimitError):
            client.search_by_keyword("blockchain")

if __name__ == "__main__":
    unittest.main()
