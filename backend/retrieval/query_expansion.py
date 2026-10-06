import os
import re
from typing import List, Dict, Set, Tuple, Optional

# Configurable limit for query expansion
MAX_EXPANSION_TERMS = int(os.getenv("MAX_EXPANSION_TERMS", "8"))

# Common technical abbreviations and domain synonym mappings
TECHNICAL_EXPANSIONS: Dict[str, List[str]] = {
    "ai": ["artificial intelligence", "machine learning", "deep learning"],
    "ml": ["machine learning", "pattern recognition", "neural networks"],
    "cnn": ["convolutional neural network", "deep convolutional network"],
    "rnn": ["recurrent neural network", "lstm", "sequence model"],
    "llm": ["large language model", "transformer", "foundation model"],
    "gnn": ["graph neural network", "relational graph learning"],
    "diabetic retinopathy": ["fundus imaging", "retinal image analysis", "ophthalmic imaging", "fundus photography", "automated retinal disease detection"],
    "retinal images": ["retinal imaging", "fundus photographs", "ophthalmoscopy", "ocular imaging"],
    "crispr": ["cas9", "cas12", "gene editing", "targeted endonuclease", "guide rna"],
    "battery": ["energy storage", "lithium-ion", "electrolyte", "electrochemical cell", "state of charge"],
    "bms": ["battery management system", "coulomb counting", "state of charge estimation"],
    "5g": ["new radio", "nr", "beamforming", "phased array", "mimo"],
    "mimo": ["multiple input multiple output", "spatial multiplexing", "antenna diversity"],
    "iot": ["internet of things", "sensor network", "telemetry nodes"],
    "fuel cell": ["solid oxide fuel cell", "sofc", "proton exchange membrane", "electrocatalyst"],
    "solar": ["photovoltaic", "pv cell", "mppt", "solar module"],
    "wind turbine": ["variable pitch blade", "dual rotor", "wind energy converter"],
    "glucose": ["blood sugar", "spectrophotometry", "continuous glucose monitoring", "optical absorption"],
    "cancer": ["oncological", "tumor", "antineoplastic", "chemotherapeutic"],
    "firewall": ["packet filter", "network security", "intrusion detection system"],
    "zero trust": ["identity verification", "least privilege", "cryptographic authentication"],
    "blockchain": ["distributed ledger", "consensus protocol", "smart contract"],
    "pacos": ["paxos", "raft", "distributed consensus"],
    "mri": ["magnetic resonance imaging", "radiofrequency coil", "spin echo"],
    "prosthetic": ["myoelectric", "electromyographic", "emg sensor", "biomechatronic"],
    "pacemaker": ["cardiac pacing", "thoracic impedance", "implantable pulse generator"],
    "lidar": ["light detection and ranging", "laser scanning", "point cloud sensor"],
    "radar": ["radio detection and ranging", "doppler radar", "millimeter wave"],
    "ev": ["electric vehicle", "hybrid vehicle", "regenerative braking"],
    "autonomous vehicle": ["self driving", "driverless", "collision avoidance", "sensor fusion"]
}

# Known common IPC subclasses for fast validation
KNOWN_IPC_PREFIXES: Set[str] = {
    "A61B", "A61K", "A61M", "A61N", "A61P", "A61F",
    "G06F", "G06K", "G06N", "G06T", "G06Q", "G01N", "G01R", "G01S",
    "H04L", "H04W", "H04B", "H04N", "H01L", "H01M", "H02J", "H02K",
    "B60W", "B60K", "B60L", "B01D", "B01J", "C12N", "C12P", "C07D", "C07K"
}

def expand_terms(concepts: List[str], max_terms: int = MAX_EXPANSION_TERMS) -> List[str]:
    """
    Expands technical concepts into controlled domain synonyms and related terms.
    Restricts results to max_terms to avoid query drift.
    """
    expanded = []
    seen = {c.strip().lower() for c in concepts}
    
    for concept in concepts:
        c_clean = concept.strip().lower()
        
        # 1. Exact match in dictionary
        if c_clean in TECHNICAL_EXPANSIONS:
            for syn in TECHNICAL_EXPANSIONS[c_clean]:
                if syn not in seen:
                    seen.add(syn)
                    expanded.append(syn)
                    if len(expanded) >= max_terms:
                        return expanded
                        
        # 2. Check substring matching
        for key, syns in TECHNICAL_EXPANSIONS.items():
            if key in c_clean or c_clean in key:
                for syn in syns:
                    if syn not in seen:
                        seen.add(syn)
                        expanded.append(syn)
                        if len(expanded) >= max_terms:
                            return expanded

    return expanded[:max_terms]

def build_search_phrases(concepts: List[str], expanded: List[str]) -> List[str]:
    """
    Creates focused lexical search phrases by pairing core concepts with expanded terms.
    """
    phrases = []
    if not concepts:
        return phrases
        
    primary = concepts[0].strip()
    
    # Phrase with secondary concept
    if len(concepts) > 1:
        phrases.append(f'"{primary}" AND "{concepts[1].strip()}"')
        phrases.append(f'{primary} {concepts[1].strip()}')
    else:
        phrases.append(f'"{primary}"')
        
    # Phrases with top expanded terms
    for exp in expanded[:3]:
        phrases.append(f'{primary} {exp}')
        
    return phrases[:5]

def validate_classification(ipc_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validates candidate IPC classification codes.
    Checks if the code format is structurally valid (e.g. A61K or G06F 17/00)
    and checks if it belongs to known IPC subclasses.
    Returns (is_validated, normalized_code).
    """
    if not ipc_code or not isinstance(ipc_code, str):
        return False, None
        
    cleaned = ipc_code.strip().upper()
    match = re.match(r'^([A-H]\d{2}[A-Z]?)(\s*\d+/\d+)?$', cleaned)
    if not match:
        return False, None
        
    subclass = match.group(1)
    if subclass in KNOWN_IPC_PREFIXES:
        return True, cleaned
    # Soft valid format even if not in high-frequency cache
    if re.match(r'^[A-H]\d{2}[A-Z]$', subclass):
        return True, subclass
        
    return False, None
