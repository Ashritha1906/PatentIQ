import os
import sys
import time
import json
import logging
import threading
import urllib.request
import urllib.parse
import uvicorn

# Adjust path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from backend.api.main import app
from backend.api.services.dependencies import get_patent_service

# Disable excessive logs during testing
logging.basicConfig(level=logging.ERROR)

# Setup uvicorn server in a daemon thread
TEST_PORT = 8124
server_thread = threading.Thread(
    target=uvicorn.run,
    args=(app,),
    kwargs={"host": "127.0.0.1", "port": TEST_PORT, "log_level": "error"},
    daemon=True
)
server_thread.start()
time.sleep(2.0)  # Wait for server to bind and start

def api_request(method, path, payload=None):
    """
    Helper to make HTTP requests to the running test server using urllib.
    """
    url = f"http://127.0.0.1:{TEST_PORT}/api{path}"
    headers = {"Content-Type": "application/json"}
    
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            body = e.read().decode("utf-8") or e.reason
        return e.code, body
    except Exception as e:
        return 500, str(e)

def run_tests():
    report_lines = []
    report_lines.append("==================================================")
    report_lines.append("PatentIQ API Validation Report")
    report_lines.append("==================================================")
    report_lines.append(f"Testing environment initialized (Threaded Server Port {TEST_PORT}).")
    report_lines.append("")

    failed_tests = 0
    passed_tests = 0

    def assert_test(name, assertion_fn):
        nonlocal failed_tests, passed_tests
        try:
            assertion_fn()
            msg = f"[PASS] {name}"
            print(msg)
            report_lines.append(msg)
            passed_tests += 1
        except Exception as e:
            msg = f"[FAIL] {name}: {str(e)}"
            print(msg)
            report_lines.append(msg)
            failed_tests += 1

    # Test 1: GET /health
    def test_health():
        status_code, data = api_request("GET", "/health")
        assert status_code == 200, f"Expected 200, got {status_code}"
        assert "status" in data, "No 'status' field in response"
        assert "database" in data, "No 'database' field in response"
        assert "llm_mode" in data, "No 'llm_mode' field in response"
    assert_test("GET /health Endpoint Integrity", test_health)

    # Test 2: POST /search Valid Request
    def test_search_valid():
        payload = {
            "idea_text": "Non-invasive wearable blood glucose sensor using optical absorption",
            "top_k": 3
        }
        status_code, data = api_request("POST", "/search", payload)
        assert status_code == 200, f"Expected 200, got {status_code}"
        assert isinstance(data, list), "Response is not a list"
        assert len(data) <= 3, f"Expected <= 3 patents, got {len(data)}"
        if len(data) > 0:
            assert "application_number" in data[0], "No 'application_number' in patent"
            assert "title" in data[0], "No 'title' in patent"
            assert "similarity_score" in data[0], "No 'similarity_score' in patent"
    assert_test("POST /search Valid Request", test_search_valid)

    # Test 3: POST /novelty Valid Request
    def test_novelty_valid():
        payload = {
            "idea_text": "A wind turbine rotor with variable-pitch blades controlled by neural networks",
            "top_k": 3
        }
        status_code, data = api_request("POST", "/novelty", payload)
        assert status_code == 200, f"Expected 200, got {status_code}"
        assert "novelty_score" in data, "No 'novelty_score' in response"
        assert "band" in data, "No 'band' in response"
        assert "explanation" in data, "No 'explanation' in response"
        assert "breakdown" in data, "No 'breakdown' in response"
    assert_test("POST /novelty Valid Request", test_novelty_valid)

    # Test 4: POST /analyze Valid Request
    def test_analyze_valid():
        payload = {
            "idea_text": "A CRISPR-based lipid nanoparticle delivery vehicle target for hepatocytes using apolipoprotein E",
            "top_k": 2
        }
        status_code, data = api_request("POST", "/analyze", payload)
        assert status_code == 200, f"Expected 200, got {status_code}"
        assert data["user_idea"] == payload["idea_text"]
        assert "technology_domain" in data
        assert "similar_patents" in data
        assert "evidence_ranking" in data
        assert "concept_clusters" in data
        assert "novelty_score" in data
        assert "innovation_gaps" in data
        assert "analysis" in data
        assert "confidence_score" in data
    assert_test("POST /analyze Valid Request (Full Pipeline)", test_analyze_valid)

    # Test 5: Empty request validation
    def test_empty_request():
        status_code, data = api_request("POST", "/analyze", {})
        # FastAPI returns 422 for missing fields required by Pydantic models
        assert status_code == 422, f"Expected Pydantic validation error (422), got {status_code}"
    assert_test("POST /analyze Empty/Missing Request Body Validation", test_empty_request)

    # Test 6: Long invention description handling
    def test_long_description():
        long_text = "This is an invention for an improved battery system. " * 300  # ~3000 words
        payload = {
            "idea_text": long_text,
            "top_k": 3
        }
        status_code, data = api_request("POST", "/novelty", payload)
        assert status_code == 200, f"Expected 200, got {status_code}"
    assert_test("POST /novelty Long Invention Description Support", test_long_description)

    # Test 7: Invalid filter check (e.g. negative top_k, invalid params)
    def test_invalid_filter():
        payload = {
            "idea_text": "Some idea text",
            "top_k": -5
        }
        status_code, data = api_request("POST", "/search", payload)
        # Should execute successfully by falling back safely to default count, or returning 400
        assert status_code in (200, 400), f"Expected 200 or 400, got {status_code}"
    assert_test("POST /search Boundary Filter Configuration", test_invalid_filter)

    # Test 8: Error handling
    def test_error_handling():
        original_service = get_patent_service()
        
        class FailingService:
            def search_similar(self, *args, **kwargs):
                raise ValueError("Test internal error simulation")
                
        # Re-register dependency mock
        app.dependency_overrides[get_patent_service] = lambda: FailingService()
        try:
            payload = {
                "idea_text": "Simulated error idea",
                "top_k": 3
            }
            status_code, data = api_request("POST", "/search", payload)
            assert status_code == 500, f"Expected 500 internal server error, got {status_code}"
            assert "detail" in data, "No error details in response"
        finally:
            app.dependency_overrides.clear()
    assert_test("API Error Isolation and Response Formatting", test_error_handling)

    # Compile Summary
    summary = f"\nTesting complete: {passed_tests} passed, {failed_tests} failed."
    print(summary)
    report_lines.append("")
    report_lines.append("==================================================")
    report_lines.append("API Validation Test Summary")
    report_lines.append("==================================================")
    report_lines.append(f"Passed Tests : {passed_tests}")
    report_lines.append(f"Failed Tests : {failed_tests}")
    report_lines.append(f"Success Rate : {(passed_tests / (passed_tests + failed_tests)) * 100:.2f}%")
    report_lines.append("==================================================")

    # Save to file
    report_path = os.path.join(os.path.dirname(__file__), "api_validation_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"Validation report generated successfully at: {report_path}")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
