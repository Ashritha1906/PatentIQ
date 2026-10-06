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

# Force real Gemini execution by overriding environment variable
os.environ["MOCK_LLM"] = "false"

from backend.api.main import app

# Keep logging clean but show startup info
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("RealE2ETests")

# Setup uvicorn server in a daemon thread
TEST_PORT = 8127
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
    Helper to make HTTP requests to the running test server.
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

# 20 diverse ideas selected across 5 industries
REAL_TEST_IDEAS = [
    # Biotech (4 ideas)
    "A recombinant promoter construct in yeast to enhance enzyme secretion for wood pulp bleaching.",
    "A CRISPR lipid nanoparticle delivery vehicle target for hepatocytes using apolipoprotein E receptors.",
    "A colorimetric gold nanoparticle biosensor for detecting pesticide residues in organic fruits.",
    "Enzymatic lignin degradation using laccase-mediator systems in bioreactors under high pressure.",
    
    # Communications (4 ideas)
    "A 5G phased array beamforming steerable antenna system with dynamic subcarrier resource allocation.",
    "A time-to-digital converter in Class-D digital loops to reduce high-frequency clock jitter.",
    "LDPC forward error correction decoder architecture optimized for low-power FPGA hardware.",
    "A cognitive radio network utilizing dynamic RSSI mapping to bypass localized cell jamming.",
    
    # Energy (4 ideas)
    "Internal steam reforming in solid oxide fuel cells (SOFC) with sensor-feedback thermal management.",
    "A battery management system using state-of-charge calculation loops based on Coulomb counting.",
    "A dual-rotor wind turbine with variable-pitch blades controlled by neural network feedback loops.",
    "An electrolyte solvent mixture for lithium-ion batteries featuring high fluorinated carbonate content.",
    
    # Medical Devices (4 ideas)
    "A non-invasive wearable blood glucose sensor using optical absorption and spectrophotometry.",
    "A thoracic impedance tracking wearable wristband for early detection of congestive heart failure.",
    "A smart orthopedic knee brace with integrated flex sensors and diagnostic audio guidance.",
    "A skin lesion classifier utilizing convolutional neural networks trained on multi-spectral images.",
    
    # Computer Science (4 ideas)
    "A zero-trust multi-factor user authentication system mapping keys across microservice endpoints.",
    "An automated software security fuzzer targeting packet parsing vulnerabilities in firewalls.",
    "A distributed database replication mechanism resolving split-brain scenarios using Paxos.",
    "A compiler register allocation optimizer using genetic algorithms to minimize cache misses."
]

def run_real_e2e():
    print("==================================================")
    print("Executing 20 E2E Tests using REAL Gemini + ChromaDB")
    print("==================================================")
    
    latencies = []
    failures = 0
    consistency_successes = 0
    mock_fallbacks = 0
    
    required_keys = [
        "user_idea", "technology_domain", "similar_patents", 
        "evidence_ranking", "concept_clusters", "novelty_score", 
        "innovation_gaps", "analysis", "confidence_score"
    ]

    for idx, idea in enumerate(REAL_TEST_IDEAS):
        start_time = time.time()
        print(f"[{idx + 1}/20] Running: '{idea[:60]}...'")
        
        payload = {
            "idea_text": idea,
            "top_k": 3
        }
        
        status_code, data = api_request("POST", "/analyze", payload)
        elapsed = time.time() - start_time
        latencies.append(elapsed)
        
        if status_code == 200:
            # Check if any part of response contains mock text patterns to verify it didn't fallback to mock
            is_mocked = "shared_concepts" in data or "Dynamic Control Loops" in data.get("analysis", "") or "Apolipoprotein E Hepatocyte" in data.get("analysis", "")
            if is_mocked:
                mock_fallbacks += 1
                print(f"  [MOCK FALLBACK] Executed via Mock Fallback due to quota limits.")
            
            # Check schema consistency
            is_consistent = all(key in data for key in required_keys)
            if is_consistent:
                consistency_successes += 1
                
            print(f"  [OK] Completed in {elapsed:.2f}s | Novelty Score: {data['novelty_score']['novelty_score']}")
        else:
            failures += 1
            print(f"  [ERROR] Status Code {status_code}: {data}")
            
    # Calculate statistics
    total_runs = len(REAL_TEST_IDEAS)
    success_rate = ((total_runs - failures) / total_runs) * 100
    consistency_rate = (consistency_successes / total_runs) * 100
    real_live_rate = ((total_runs - failures - mock_fallbacks) / total_runs) * 100
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0

    # Write report
    report_lines = []
    report_lines.append("==================================================")
    report_lines.append("Real Service E2E Test Report (Gemini + ChromaDB)")
    report_lines.append("==================================================")
    report_lines.append(f"Total Invention Ideas Run : {total_runs}")
    report_lines.append(f"Successful Requests       : {total_runs - failures}")
    report_lines.append(f"Failed Requests           : {failures}")
    report_lines.append(f"Mock Fallbacks (429/quota): {mock_fallbacks}")
    report_lines.append(f"Real Live Success Rate    : {real_live_rate:.2f}%")
    report_lines.append(f"Overall Success Rate      : {success_rate:.2f}%")
    report_lines.append(f"Schema Consistency Rate   : {consistency_rate:.2f}%")
    report_lines.append(f"Average Latency           : {avg_latency:.2f} seconds")
    report_lines.append(f"Minimum Latency           : {min_latency:.2f} seconds")
    report_lines.append(f"Maximum Latency           : {max_latency:.2f} seconds")
    report_lines.append("==================================================")
    
    # Save to dedicated file
    report_path = os.path.join(os.path.dirname(__file__), "real_e2e_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"\nReal Service E2E Report saved successfully at: {report_path}")
    print(f"Average Latency: {avg_latency:.2f}s | Real Live Success Rate: {real_live_rate:.2f}%")
    
if __name__ == "__main__":
    run_real_e2e()
