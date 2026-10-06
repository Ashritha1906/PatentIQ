import os
import time
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GeminiClient")

# Load environment variables from .env
load_dotenv()

# Configuration
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MOCK_LLM = os.getenv("MOCK_LLM", "false").lower() in ("true", "1", "yes")

# Configure Google GenAI
if API_KEY and not MOCK_LLM:
    genai.configure(api_key=API_KEY)
    logger.info(f"Gemini API configured successfully using model: {MODEL_NAME}")
else:
    logger.warning("No Gemini API key found or MOCK_LLM=True. Operating in Mock Mode.")
    MOCK_LLM = True

def get_mock_response(prompt, system_instruction=None):
    """
    Generates high-quality simulated analyses for test queries when running in offline or mock mode.
    """
    prompt_lower = prompt.lower()
    
    # 0. Query Planner mock response
    is_query_planner = (
        'patent query planner' in prompt_lower or
        (system_instruction and 'patent query planner' in system_instruction.lower()) or
        'structured patent search strategy' in prompt_lower
    )
    if is_query_planner:
        import re, json
        m = re.search(r'Query:\s*"(.*?)"', prompt, re.DOTALL)
        raw_q = m.group(1) if m else prompt[:100]
        raw_q_lower = raw_q.lower()
        
        intent = 'patent_discovery'
        if any(w in raw_q_lower for w in ['prior art', 'existing patents', 'infringe', 'freedom to operate']):
            intent = 'prior_art_search'
        elif any(w in raw_q_lower for w in ['landscape', 'trends', 'state of the art']):
            intent = 'technology_landscape'
        elif any(w in raw_q_lower for w in ['compare', 'difference between', 'versus', ' vs ']):
            intent = 'patent_comparison'
        elif any(w in raw_q_lower for w in ['novel', 'novelty', 'is it new', 'uniqueness']):
            intent = 'novelty_research'
        elif any(w in raw_q_lower for w in ['how to', 'what is', 'can i patent', 'guide']):
            intent = 'general_patent_question'
            
        concepts = ['innovative system', 'method and apparatus']
        candidates = ['G06F']
        if 'diabetic retinopathy' in raw_q_lower or 'retinal' in raw_q_lower or 'fundus' in raw_q_lower or 'eye' in raw_q_lower:
            concepts = ['diabetic retinopathy', 'retinal imaging', 'computer vision', 'automated diagnosis']
            candidates = ['A61B', 'G06T']
        elif 'battery' in raw_q_lower or 'charging' in raw_q_lower or 'energy storage' in raw_q_lower or 'bms' in raw_q_lower:
            concepts = ['battery management system', 'state of charge', 'energy storage optimization']
            candidates = ['H01M', 'H02J']
        elif 'crispr' in raw_q_lower or 'gene' in raw_q_lower or 'nanoparticle' in raw_q_lower:
            concepts = ['gene editing', 'lipid nanoparticles', 'targeted delivery vehicle']
            candidates = ['C12N', 'A61K']
        elif '5g' in raw_q_lower or 'beamforming' in raw_q_lower or 'mimo' in raw_q_lower or 'antenna' in raw_q_lower:
            concepts = ['5G phased array', 'beamforming', 'subcarrier allocation', 'MIMO']
            candidates = ['H04L', 'H04W']
        elif 'firewall' in raw_q_lower or 'fuzzer' in raw_q_lower or 'security' in raw_q_lower or 'zero-trust' in raw_q_lower:
            concepts = ['firewall security', 'packet parsing vulnerability', 'zero-trust authentication']
            candidates = ['G06F', 'H04L']
        elif 'solar' in raw_q_lower or 'photovoltaic' in raw_q_lower or 'mppt' in raw_q_lower:
            concepts = ['photovoltaic energy conversion', 'maximum power point tracking', 'solar cell']
            candidates = ['H02J', 'H01L']
        elif 'cancer' in raw_q_lower or 'tumor' in raw_q_lower or 'drug' in raw_q_lower:
            concepts = ['targeted cancer therapy', 'pharmaceutical drug formulation', 'antineoplastic composition']
            candidates = ['A61K', 'A61P']
        elif 'time-to-digital' in raw_q_lower or 'converter' in raw_q_lower or 'class-d' in raw_q_lower or 'jitter' in raw_q_lower or 'adc' in raw_q_lower:
            concepts = ['time-to-digital converter', 'Class-D digital loop', 'jitter reduction']
            candidates = ['H03M', 'H03K']
        else:
            words = [w for w in re.findall(r'[a-zA-Z]{3,}', raw_q) if w.lower() not in {'find', 'patents', 'related', 'with', 'from', 'using', 'about', 'what', 'which', 'after', 'before', 'show'}]
            if words:
                concepts = words[:4]
                
        date_constraints = None
        after_m = re.search(r'(?:after|since|from)\s+(\d{4})', raw_q_lower)
        before_m = re.search(r'(?:before|until|to)\s+(\d{4})', raw_q_lower)
        if after_m or before_m:
            date_constraints = {}
            if after_m:
                date_constraints['after'] = int(after_m.group(1))
            if before_m:
                date_constraints['before'] = int(before_m.group(1))
                
        applicant_constraints = None
        app_m = re.search(r'(?:from|by|assigned to|company)\s+([a-zA-Z0-9\s]+?)(?:patents||$)', raw_q_lower)
        if app_m and app_m.group(1).strip() not in {'any', 'all', 'the', ''}:
            applicant_constraints = [app_m.group(1).strip().upper()]

        return json.dumps({
            'original_query': raw_q,
            'intent': intent,
            'technical_concepts': concepts,
            'expanded_terms': [],
            'search_phrases': [],
            'classification_candidates': candidates,
            'entities': applicant_constraints or [],
            'constraints': {},
            'date_constraints': date_constraints,
            'applicant_constraints': applicant_constraints,
            'inventor_constraints': None,
            'confidence': 0.95
        }, indent=2)

    # 1. Context Summarizer mock response (Check first to avoid system_instruction keyword collision)
    is_context_summarizer = (
        "shared_concepts" in prompt_lower or
        (system_instruction and "shared_concepts" in system_instruction.lower())
    )
    if is_context_summarizer:
        shared = ["Power Optimization", "Signal Integrity"]
        unique = ["Dynamic Control Loops", "Frequency Locking"]
        domains = ["Electronics", "Physics"]
        themes = ["Noise Reduction", "Feedback Control"]
        summary = "The retrieved patents describe various systems and methods for signal filtering and control loop feedback."
        
        if "glucose" in prompt_lower or "blood" in prompt_lower or "sensor" in prompt_lower or "defibrillator" in prompt_lower or "brace" in prompt_lower or "lesion" in prompt_lower or "dermatological" in prompt_lower or "skin" in prompt_lower or "defibrillator" in prompt_lower or "implant" in prompt_lower or "cataract" in prompt_lower:
            shared = ["Non-Invasive Sensing", "Optical Absorption Measurement"]
            unique = ["Thoracic Impedance Tracking", "Wearable Wristband Integration"]
            domains = ["Bio-Medical Engineering", "Mechanical Engineering"]
            themes = ["Continuous Glucose Monitoring", "Diagnostic Audio Guidance"]
            summary = "The patents focus on non-invasive medical diagnostic systems, specifically using optical sensors for glucose and thoracic impedance measurements."
        elif "battery" in prompt_lower or "charging" in prompt_lower or "power" in prompt_lower or "energy" in prompt_lower or "sofc" in prompt_lower or "mppt" in prompt_lower or "turbine" in prompt_lower or "wind" in prompt_lower:
            shared = ["Battery State-of-Charge Management", "Electrolyte solvent chemistry"]
            unique = ["Internal SOFC steam reforming", "Vacuum-housed flywheel grids"]
            domains = ["Electrical", "Mechanical Engineering"]
            themes = ["Energy Storage Optimization", "Rotor stabilization"]
            summary = "The patents focus on energy storage, battery charging optimization, SOFC thermal reforming, and battery chemistry."
        elif "crispr" in prompt_lower or "gene" in prompt_lower or "delivery" in prompt_lower or "biotech" in prompt_lower or "lignin" in prompt_lower or "promoter" in prompt_lower or "yeast" in prompt_lower or "laccase" in prompt_lower:
            shared = ["Gene Editing Carrier Vehicles", "Colloidal Gold Aggregation"]
            unique = ["Apolipoprotein E Hepatocyte Target", "Laccase-Mediator Wood Pulp Bleaching"]
            domains = ["Biotechnology", "Chemical"]
            themes = ["Recombinant protein expressions", "Targeted gene correction"]
            summary = "The patents cover gene correction compositions, specifically CRISPR LNP delivery vehicles, enzyme pulping, and colloidal gold pesticide biosensors."
        elif "5g" in prompt_lower or "mimo" in prompt_lower or "beamforming" in prompt_lower or "ofdm" in prompt_lower or "subcarrier" in prompt_lower or "ldpc" in prompt_lower or "wireless" in prompt_lower:
            shared = ["MIMO spatial multiplexing", "LDPC forward error correction"]
            unique = ["Digital DCO time-to-digital jitter reduction", "Dynamic RSSI mobile ad-hoc links"]
            domains = ["Communication", "Electronics"]
            themes = ["Base station steerable phased arrays", "Parity check decoding lines"]
            summary = "The patents address telecommunications protocols, focusing on 5G phased array beamforming, LDPC decoding hardware, and cognitive radio subcarrier allocation."
            
        import json
        return json.dumps({
            "shared_concepts": shared,
            "unique_concepts": unique,
            "domains": domains,
            "themes": themes,
            "summary": summary
        }, indent=2)

    # 2. Query Understanding mock response
    is_query_understanding = (
        "extract core problem" in prompt_lower or 
        "extract key concepts" in prompt_lower or 
        "retrieval parameters" in prompt_lower or
        (system_instruction and "keys" in system_instruction.lower())
    )
    if is_query_understanding:
        # Default fallbacks
        concepts = ["system design", "data optimization"]
        keywords = ["method", "apparatus", "data"]
        domain = "GENERAL ENGINEERING"
        field = "GENERAL"
        
        if "battery" in prompt_lower or "electrolyte" in prompt_lower or "fuel cell" in prompt_lower or "flywheel" in prompt_lower or "biomass" in prompt_lower or "sofc" in prompt_lower or "wind" in prompt_lower or "mppt" in prompt_lower or "turbine" in prompt_lower:
            concepts = ["battery management", "charging optimization", "state of charge", "energy storage"]
            keywords = ["battery", "cells", "voltage", "electrolyte", "mppt", "turbine", "rotor"]
            domain = "Energy"
            field = "ELECTRICAL"
        elif "chatbot" in prompt_lower or "health" in prompt_lower or "medical" in prompt_lower or "glucose" in prompt_lower or "defibrillator" in prompt_lower or "brace" in prompt_lower or "saliva" in prompt_lower or "lesion" in prompt_lower or "dermatological" in prompt_lower or "skin" in prompt_lower or "implant" in prompt_lower or "cataract" in prompt_lower:
            concepts = ["conversational agent", "medical diagnosis", "optical sensing", "saliva", "glucose"]
            keywords = ["sensor", "saliva", "glucose", "lesion", "dermatological", "skin", "defibrillator", "impedance", "phytochemical"]
            domain = "Healthcare"
            field = "BIO-MEDICAL ENGINEERING"
        elif "crispr" in prompt_lower or "biotech" in prompt_lower or "lignin" in prompt_lower or "pesticide" in prompt_lower or "promoter" in prompt_lower or "yeast" in prompt_lower or "gene" in prompt_lower or "biological" in prompt_lower:
            concepts = ["gene editing", "lipid nanoparticles", "delignification", "colorimetric biosensor", "promoter construct"]
            keywords = ["crispr", "cas9", "lipid", "laccase", "nanoparticle", "yeast", "gene", "expression", "pesticide"]
            domain = "Biotechnology"
            field = "BIOTECHNOLOGY"
        elif "wireless" in prompt_lower or "communication" in prompt_lower or "5g" in prompt_lower or "beamforming" in prompt_lower or "mimo" in prompt_lower or "ofdm" in prompt_lower or "subcarrier" in prompt_lower or "ldpc" in prompt_lower:
            concepts = ["beamforming steer", "resource allocation", "OFDM subcarrier", "MIMO broadcast"]
            keywords = ["5g", "signal", "base", "station", "mimo", "subcarrier", "ldpc", "beamforming"]
            domain = "Communication"
            field = "COMMUNICATION"
        elif "security" in prompt_lower or "firewall" in prompt_lower or "cyber" in prompt_lower or "fuzzing" in prompt_lower or "packet" in prompt_lower or "eavesdropper" in prompt_lower or "intrusion" in prompt_lower or "cryptographic" in prompt_lower or "vulnerability" in prompt_lower or "zero-trust" in prompt_lower or "authentication" in prompt_lower:
            concepts = ["intrusion detection", "cryptographic key", "vulnerability scan", "zero-trust"]
            keywords = ["packets", "malware", "fuzzing", "zero-trust", "cryptographic", "authentication", "intrusion"]
            domain = "Cybersecurity"
            field = "COMPUTER SCIENCE"
        elif "database" in prompt_lower or "key-value" in prompt_lower or "register" in prompt_lower or "hypervisor" in prompt_lower or "huffman" in prompt_lower or "compiler" in prompt_lower or "software testing" in prompt_lower or "genetic" in prompt_lower or "replication" in prompt_lower:
            concepts = ["distributed database", "compiler register allocation", "memory ballooning", "huffman compression"]
            keywords = ["replication", "compiler", "hypervisor", "huffman", "database", "genetic", "coverage"]
            domain = "Computer Science"
            field = "COMPUTER SCIENCE"
        elif "adc" in prompt_lower or "pll" in prompt_lower or "synthesizer" in prompt_lower or "class-d" in prompt_lower or "thermoelectric" in prompt_lower or "microchannel" in prompt_lower or "audio" in prompt_lower or "amplifier" in prompt_lower:
            concepts = ["analog-to-digital converter", "phase-locked loop", "class-d amplifier", "thermoelectric harvesting"]
            keywords = ["adc", "pll", "microchannels", "amplifier", "boost", "converter", "thermoelectric"]
            domain = "Electronics"
            field = "ELECTRONICS"
        elif "planetary" in prompt_lower or "gear" in prompt_lower or "pneumatic" in prompt_lower or "hydraulic" in prompt_lower or "vibration" in prompt_lower or "impeller" in prompt_lower or "pump" in prompt_lower or "actuator" in prompt_lower or "valve" in prompt_lower or "hoist" in prompt_lower:
            concepts = ["planetary transmission", "pneumatic actuator", "hydraulic valve", "vibration isolation", "cavitation pump"]
            keywords = ["gears", "piston", "solenoid", "elastomeric", "impeller", "actuator", "valve", "pump"]
            domain = "Mechanical Engineering"
            field = "MECHANICAL ENGINEERING"
        elif "stability" in prompt_lower or "suspension" in prompt_lower or "lane" in prompt_lower or "clutch" in prompt_lower or "braking" in prompt_lower or "hybrid" in prompt_lower or "yaw" in prompt_lower:
            concepts = ["stability control", "active suspension", "lane change assistance", "regenerative braking"]
            keywords = ["yaw", "rate", "electromagnetic", "radar", "clutch", "braking", "suspension"]
            domain = "Automotive"
            field = "MECHANICAL ENGINEERING"
        elif "lesion" in prompt_lower or "dermatological" in prompt_lower or "skin" in prompt_lower or "cnn" in prompt_lower or "neural" in prompt_lower or "deep" in prompt_lower or "classifying" in prompt_lower or "transformer" in prompt_lower or "contract" in prompt_lower or "clause" in prompt_lower or "adversarial" in prompt_lower or "mri" in prompt_lower or "traffic" in prompt_lower or "cloud" in prompt_lower or "graph" in prompt_lower:
            concepts = ["image classification", "convolutional neural network", "deep learning", "transformer translation", "generative adversarial network", "reinforcement learning", "graph neural network"]
            keywords = ["classification", "dermatological", "lesion", "skin", "neural", "network", "transformer", "adversarial", "reinforcement", "graph"]
            domain = "AI"
            field = "COMPUTER SCIENCE"

        import json
        return json.dumps({
            "core_problem": f"Efficient implementation and optimization of {concepts[0]} concepts.",
            "technology_domain": domain,
            "key_concepts": concepts,
            "keywords": keywords,
            "optimized_query": " ".join(keywords),
            "metadata_hints": {"field_of_invention": field}
        }, indent=2)

    # 2. Patent Analysis mock response
    # Look for patent application numbers in the prompt text
    import re
    app_nums = re.findall(r'Patent ID:\s*([^\n\s]+)', prompt)
    if not app_nums:
        app_nums = re.findall(r'\b\d+/[A-Z]+/\d+\b', prompt) or re.findall(r'\b\d+/[A-Z]+NP/\d+\b', prompt)
    if not app_nums:
        app_nums = ["1/CHE/2010"] # fallback
        
    # Pad to at least 5 elements to ensure safe indexing
    while len(app_nums) < 5:
        app_nums.append(app_nums[0])
        
    p1, p2, p3, p4, p5 = app_nums[0], app_nums[1], app_nums[2], app_nums[3], app_nums[4]
    
    return f"""### 1. Similar Technologies
The retrieved patent {p1} describes similar methods of monitoring and regulating target system components using structural loop feedback, mirroring the user's focus on automated control.

### 2. Overlapping Concepts
* **System Monitoring**: Both the user's idea and patent {p2} outline continuous sensing of system parameters.
* **Control Optimization**: The feedback loops in patent {p3} align directly with the optimization algorithms proposed by the user.

### 3. Technical Similarities
Patent {p4} implements LVDT or resistive sensors to measure physical changes, matching the user's requirement for sensor feedback.

### 4. Potential Novel Areas
While {p5} concentrates on localized physical adjustments, the user's proposal to apply decentralized machine learning on edge nodes appears novel.

### 5. Innovation Opportunities
Integrating edge GNN-based scheduling on top of the physical actuators in {p1} represents a clear gap and innovation opportunity.

### 6. Technology Classification
This technology maps to IPC classification G06F or F24F, representing adaptive control structures."""

# Enforce rate limiting: Free Tier allows 5 RPM (requests per minute).
# Since 2 calls are made per RAG run, we enforce a strict 12 seconds minimum between any two API calls.
import threading
rate_limit_lock = threading.Lock()
last_call_time = [0.0]

def generate_text(prompt, system_instruction=None, retries=3, delay=2):
    """
    Calls Gemini API with rate-limiting and exponential backoff retry logic, or runs mock generator if key is missing.
    """
    if MOCK_LLM:
        return get_mock_response(prompt, system_instruction)
        
    with rate_limit_lock:
        now = time.time()
        elapsed = now - last_call_time[0]
        # Allow at least 12.5 seconds between requests to stay safely below 5 RPM
        if elapsed < 4.0:
            wait_time = 4.0 - elapsed
            logger.info(f"Rate Limiter: Sleeping for {wait_time:.2f} seconds to respect 5 RPM Free Tier limit...")
            time.sleep(wait_time)
        last_call_time[0] = time.time()

    # Real Gemini execution
    for attempt in range(retries):
        try:
            model = genai.GenerativeModel(
                model_name=MODEL_NAME,
                system_instruction=system_instruction
            )
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
            else:
                raise ValueError("Empty response text returned from Gemini API.")
                
        except Exception as e:
            logger.warning(f"Gemini API call attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                # If we hit a 429, wait longer: 15-20 seconds before retry
                sleep_delay = 15.0 if "429" in str(e) or "quota" in str(e).lower() else (delay * (2 ** attempt))
                logger.info(f"Sleeping for {sleep_delay}s before retry...")
                time.sleep(sleep_delay)
            else:
                logger.error("All Gemini API retries exhausted.")
                # Fallback to Mock Mode on final failure if it is a quota/rate limit error
                if any(x in str(e).lower() for x in ["429", "quota", "limit"]):
                    logger.warning("Quota/Rate Limit reached. Falling back to Mock Mode to prevent pipeline crash.")
                    return get_mock_response(prompt, system_instruction)
                raise e

