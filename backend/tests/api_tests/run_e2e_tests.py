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

# Disable standard logging output to keep console clean
logging.basicConfig(level=logging.ERROR)

# Setup uvicorn server in a daemon thread
TEST_PORT = 8125
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

# List of 50 diverse invention ideas for thorough pipeline evaluation
INVENTION_IDEAS = [
    # Biotech (10 ideas)
    "A recombinant promoter construct in yeast to enhance enzyme secretion for wood pulp bleaching.",
    "A CRISPR lipid nanoparticle delivery vehicle target for hepatocytes using apolipoprotein E receptors.",
    "A colorimetric gold nanoparticle biosensor for detecting pesticide residues in organic fruits.",
    "Enzymatic lignin degradation using laccase-mediator systems in bioreactors under high pressure.",
    "An engineered microalgae strain designed for accelerated carbon sequestration in industrial flue gas.",
    "A synthetic biology promoter system for high-yield expression of insulin in E. coli.",
    "A DNA barcode system for tracing pharmaceutical supply chains and identifying counterfeits.",
    "Liposome-encapsulated antimicrobial peptides targeting multidrug-resistant bacteria in wounds.",
    "A biological sensor using engineered yeast to detect traces of heavy metals in wastewater.",
    "A CRISPR-Cas12 based point-of-care diagnostics kit for rapid detection of viral RNA.",
    
    # Communications (10 ideas)
    "A 5G phased array beamforming steerable antenna system with dynamic subcarrier resource allocation.",
    "A time-to-digital converter in Class-D digital loops to reduce high-frequency clock jitter.",
    "LDPC forward error correction decoder architecture optimized for low-power FPGA hardware.",
    "A cognitive radio network utilizing dynamic RSSI mapping to bypass localized cell jamming.",
    "An optical wireless transceiver using LED arrays for high-speed underwater data links.",
    "MIMO spatial multiplexing protocol optimizing subcarrier feedback loops in high-mobility trains.",
    "A low-density parity check decoding line architecture utilizing parallel routing paths.",
    "An adaptive OFDM subcarrier allocation mechanism for low-latency drone swarm telemetry.",
    "A steerable phased array antenna for satellite tracking on autonomous marine vessels.",
    "A dynamic routing protocol for mobile ad-hoc networks (MANET) using predictive link quality.",
    
    # Energy (10 ideas)
    "Internal steam reforming in solid oxide fuel cells (SOFC) with sensor-feedback thermal management.",
    "A battery management system using state-of-charge calculation loops based on Coulomb counting.",
    "A dual-rotor wind turbine with variable-pitch blades controlled by neural network feedback loops.",
    "An electrolyte solvent mixture for lithium-ion batteries featuring high fluorinated carbonate content.",
    "A vacuum-housed mechanical flywheel energy grid storage stabilizer with magnetic levitation.",
    "A maximum power point tracking (MPPT) solar charger utilizing fuzzy logic step control.",
    "An electrochemical cell design for high-yield green hydrogen production using nickel-iron catalysts.",
    "A hybrid battery-supercapacitor energy storage system for heavy duty electric trucks.",
    "A biomass gasification reactor with integrated tar removal filters and heat recovery loops.",
    "A thermoelectric energy harvester capturing waste heat from high-voltage power lines.",
    
    # Medical Devices (10 ideas)
    "A non-invasive wearable blood glucose sensor using optical absorption and spectrophotometry.",
    "A thoracic impedance tracking wearable wristband for early detection of congestive heart failure.",
    "A smart orthopedic knee brace with integrated flex sensors and diagnostic audio guidance.",
    "A skin lesion classifier utilizing convolutional neural networks trained on multi-spectral images.",
    "A dental imaging sensor with automated caries detection using low-dose radiography.",
    "An implantable pacemaker with thoracic impedance sensing to modulate pacing rates.",
    "A surgical guidance camera system with real-time tumor boundary detection using fluorescein.",
    "A smart insulin pump adjusting infusion rates based on continuous glucose telemetry.",
    "A portable dermatological skin analyzer utilizing AI to classify benign vs malignant moles.",
    "A robotic prosthetic hand with electromyographic (EMG) muscle-sensor feedback loops.",
    
    # Computer Science & Cybersecurity (10 ideas)
    "A zero-trust multi-factor user authentication system mapping keys across microservice endpoints.",
    "An automated software security fuzzer targeting packet parsing vulnerabilities in firewalls.",
    "A distributed database replication mechanism resolving split-brain scenarios using Paxos.",
    "A compiler register allocation optimizer using genetic algorithms to minimize cache misses.",
    "An intrusion detection system using graph neural networks to map network packet flows.",
    "A memory ballooning hypervisor optimizing virtual machine density in cloud computing.",
    "A compression system using adaptive Huffman coding for low-latency video streaming.",
    "A cloud database query planner utilizing reinforcement learning for index selection.",
    "An adversarial defense firewall wrapper using generative networks to filter malware payloads.",
    "A decentralized ledger smart contract validator utilizing proof-of-authority consensus."
]

def run_e2e_evaluation():
    print("==================================================")
    print("Starting End-to-End Evaluation of 50 Ideas...")
    print("==================================================")

    latencies = []
    failures = 0
    consistency_successes = 0
    
    required_keys = [
        "user_idea", "technology_domain", "similar_patents", 
        "evidence_ranking", "concept_clusters", "novelty_score", 
        "innovation_gaps", "analysis", "confidence_score"
    ]

    for idx, idea in enumerate(INVENTION_IDEAS):
        start_time = time.time()
        print(f"[{idx + 1}/50] Processing: {idea[:50]}...")
        
        try:
            payload = {
                "idea_text": idea,
                "top_k": 3
            }
            status_code, data = api_request("POST", "/analyze", payload)
            elapsed = time.time() - start_time
            latencies.append(elapsed)
            
            if status_code == 200:
                # Validate response schema consistency
                is_consistent = all(key in data for key in required_keys)
                if is_consistent:
                    consistency_successes += 1
                else:
                    missing = [k for k in required_keys if k not in data]
                    print(f"  [WARNING] Schema inconsistency. Missing keys: {missing}")
                
                print(f"  [OK] Completed in {elapsed:.2f}s | Score: {data['novelty_score']['novelty_score']}/100")
            else:
                failures += 1
                print(f"  [ERROR] Status Code {status_code}: {data}")
                
        except Exception as e:
            failures += 1
            print(f"  [EXCEPTION] Error: {e}")
            
    # Calculate statistics
    total_runs = len(INVENTION_IDEAS)
    success_rate = ((total_runs - failures) / total_runs) * 100
    consistency_rate = (consistency_successes / total_runs) * 100
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0

    # Write results to validation report (which is located in backend/tests/api_tests/api_validation_report.txt)
    report_path = os.path.join(os.path.dirname(__file__), "api_validation_report.txt")
    
    report_append = []
    report_append.append("\n")
    report_append.append("==================================================")
    report_append.append("Phase 5G - End-to-End Stress Test (50 Invention Ideas)")
    report_append.append("==================================================")
    report_append.append(f"Total Invention Ideas Run : {total_runs}")
    report_append.append(f"Successful Requests       : {total_runs - failures}")
    report_append.append(f"Failed Requests           : {failures}")
    report_append.append(f"Success Rate              : {success_rate:.2f}%")
    report_append.append(f"Schema Consistency Rate   : {consistency_rate:.2f}%")
    report_append.append(f"Average Latency           : {avg_latency:.2f} seconds")
    report_append.append(f"Minimum Latency           : {min_latency:.2f} seconds")
    report_append.append(f"Maximum Latency           : {max_latency:.2f} seconds")
    report_append.append("==================================================")

    # Append to existing validation report file
    if os.path.exists(report_path):
        with open(report_path, "a", encoding="utf-8") as f:
            f.write("\n".join(report_append))
    else:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_append))

    print("\nE2E Evaluation finished.")
    print(f"Validation report updated successfully at: {report_path}")
    print(f"Average Latency: {avg_latency:.2f}s | Success Rate: {success_rate:.2f}%")

if __name__ == "__main__":
    run_e2e_evaluation()
