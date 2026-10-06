import httpx
import logging
from typing import Dict
from backend.knowledge_expansion.config import LENS_API_KEY, LENS_API_URL

logger = logging.getLogger("AuthLayer")

class AuthenticationError(Exception):
    """Exception raised when API authentication credentials fail or are invalid."""
    pass

def get_auth_headers() -> Dict[str, str]:
    """
    Generate request headers containing authorization details for the Lens Patent API.
    Raises AuthenticationError if no token is loaded.
    """
    if not LENS_API_KEY:
        raise AuthenticationError("LENS_API_KEY is not defined in environment configurations (.env).")
    
    return {
        "Authorization": f"Bearer {LENS_API_KEY}",
        "Content-Type": "application/json"
    }

def verify_auth() -> bool:
    """
    Validates API key authenticity against the live Lens Patent search endpoint.
    Sends a test request with size=0 to prevent resource usage.
    """
    try:
        headers = get_auth_headers()
        payload = {
            "query": {
                "match_all": {}
            },
            "size": 0
        }
        
        logger.info("Verifying Lens API authentication token...")
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(LENS_API_URL, headers=headers, json=payload)
            
            if resp.status_code == 200:
                logger.info("Lens API token verification successful.")
                return True
            elif resp.status_code in (401, 403):
                logger.error(f"Lens API token verification failed with status {resp.status_code}: {resp.text}")
                return False
            else:
                logger.warning(f"Lens API returned unexpected status {resp.status_code} during authentication: {resp.text}")
                return False
                
    except AuthenticationError as e:
        logger.error(f"Authentication setup error: {e}")
        return False
    except Exception as e:
        logger.error(f"Authentication test encountered connection error: {e}")
        return False
