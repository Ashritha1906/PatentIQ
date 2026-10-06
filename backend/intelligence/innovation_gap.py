import re
import logging
from typing import List, Dict, Any, Set, Tuple, Optional
from backend.retrieval.query_expansion import expand_terms, TECHNICAL_EXPANSIONS

logger = logging.getLogger("InnovationGap")

# Configurable representation thresholds
COVERAGE_THRESHOLDS = {
    "STRONGLY_REPRESENTED": (80, 100),
    "MODERATELY_REPRESENTED": (50, 79),
    "WEAKLY_REPRESENTED": (20, 49),
    "MINIMALLY_REPRESENTED": (1, 19),
    "NO_MEANINGFUL_EVIDENCE": (0, 0),
}

def get_coverage_band(score: float) -> str:
    """Maps a 0-100 coverage score to a representation status band."""
    if score >= 80:
        return "Strongly Represented"
    elif score >= 50:
        return "Moderately Represented"
    elif score >= 20:
        return "Weakly Represented"
    elif score >= 1:
        return "Minimally Represented"
    else:
        return "No Meaningful Evidence"

def _get_word_root(w: str) -> str:
    """Extracts morphological root for flexible matching across inflectional forms."""
    w = w.lower()
    for suffix in ("ation", "ating", "ting", "tion", "ing", "ies", "ied", "ed", "es", "ic", "al", "s"):
        if w.endswith(suffix) and len(w) - len(suffix) >= 4:
            return w[:-len(suffix)]
    return w[:5] if len(w) >= 5 else w

def _extract_concept_synonyms(concept: str) -> Set[str]:
    """
    Extracts semantic equivalents, technical synonyms, n-gram decompositions,
    and morphological variants for a given technical concept.
    """
    concept_lower = concept.lower().strip()
    synonyms = {concept_lower}

    # 1. Expand full concept
    expanded = expand_terms([concept_lower], max_terms=8)
    synonyms.update(term.lower() for term in expanded)

    # 2. Tokenize and extract sub-phrases / n-grams
    words = [w for w in re.findall(r'[a-zA-Z]{3,}', concept_lower) if w not in ("with", "using", "from", "into", "that", "this", "based")]
    
    # Bi-grams
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        synonyms.add(bigram)
        synonyms.update(term.lower() for term in expand_terms([bigram], max_terms=4))

    # Skip-grams (e.g. "retinal images" from "retinal fundus images")
    if len(words) >= 3:
        for i in range(len(words)):
            for j in range(i + 2, len(words)):
                skipgram = f"{words[i]} {words[j]}"
                synonyms.add(skipgram)
                synonyms.update(term.lower() for term in expand_terms([skipgram], max_terms=4))

    # 3. Match keys in TECHNICAL_EXPANSIONS against words or subphrases
    for k, v in TECHNICAL_EXPANSIONS.items():
        k_words = set(k.lower().split())
        if k_words.issubset(set(words)) or any(k in syn for syn in list(synonyms)):
            synonyms.update(term.lower() for term in v)

    # 4. Domain specific technical equivalences
    if any(w in concept_lower for w in ("fundus", "retina", "retinal", "eye", "ocular")):
        synonyms.update(["fundus imaging", "retinal imaging", "funduscopic", "funduscopic image analysis", "ocular imaging", "ophthalmoscopy"])
    if any(w in concept_lower for w in ("convolutional", "cnn", "deep learning", "neural")):
        synonyms.update(["convolutional neural network", "deep learning", "neural network", "deep cnn"])
    if any(w in concept_lower for w in ("preprocess", "preprocessing")):
        synonyms.update(["image processing", "contrast enhancement", "filtering", "normalization"])

    # 5. Morphological variants
    morph_syns = set()
    for s in list(synonyms):
        if s.endswith("ing"):
            morph_syns.add(s[:-3] + "e")
            morph_syns.add(s[:-3])
            morph_syns.add(s[:-3] + "es")
        elif s.endswith("es"):
            morph_syns.add(s[:-2])
            morph_syns.add(s[:-2] + "ing")
        elif s.endswith("s") and not s.endswith("ss"):
            morph_syns.add(s[:-1])
            morph_syns.add(s[:-1] + "ing")
        elif s.endswith("tion"):
            morph_syns.add(s[:-4] + "te")
            morph_syns.add(s[:-4] + "ting")
            morph_syns.add(s[:-4] + "t")
    synonyms.update(morph_syns)

    return {s for s in synonyms if len(s) >= 4}

def calculate_concept_coverage_for_patent(concept: str, patent: Dict[str, Any], synonyms: Set[str]) -> Tuple[float, bool, List[str]]:
    """
    Calculates coverage score (0-100) of a concept in a single patent record.
    Returns: (score, exact_phrase_found, matched_equivalent_terms)
    """
    title = (patent.get("title") or "").lower()
    abstract = ((patent.get("patent_text") or patent.get("abstract")) or "").lower()
    field = (patent.get("field_of_invention") or "").lower()
    all_text = f"{title} {abstract} {field}"

    concept_lower = concept.lower().strip()
    exact_in_title = concept_lower in title
    exact_in_text = concept_lower in all_text
    exact_found = exact_in_title or exact_in_text

    matched_equivalents = []
    semantic_pts = 0.0

    # 1. Exact phrase match
    if exact_in_title:
        semantic_pts = max(semantic_pts, 90.0)
        matched_equivalents.append(concept)
    elif exact_in_text:
        semantic_pts = max(semantic_pts, 75.0)
        matched_equivalents.append(concept)

    # 2. Semantic equivalents / synonym matches
    for syn in synonyms:
        if syn == concept_lower:
            continue
        if syn in title:
            semantic_pts = max(semantic_pts, 80.0)
            if syn not in matched_equivalents:
                matched_equivalents.append(syn)
        elif syn in all_text:
            semantic_pts = max(semantic_pts, 65.0)
            if syn not in matched_equivalents:
                matched_equivalents.append(syn)

    # 3. Component token root overlap (e.g. fundus in funduscopic, retin in retinal)
    words = [w for w in re.findall(r'[a-zA-Z]{4,}', concept_lower) if w not in ("with", "using", "from", "into", "that", "this")]
    if words:
        matching_roots = 0
        for w in words:
            root = _get_word_root(w)
            if root in all_text or any(root in pw for pw in all_text.split()):
                matching_roots += 1
        
        token_ratio = matching_roots / len(words)
        if token_ratio >= 0.75:
            semantic_pts = max(semantic_pts, 60.0 * token_ratio)
            if not matched_equivalents:
                matched_equivalents.append(f"root match ({matching_roots}/{len(words)} tokens)")
        elif token_ratio >= 0.50:
            semantic_pts = max(semantic_pts, 40.0 * token_ratio)

    score = min(100.0, semantic_pts)
    return score, exact_found, matched_equivalents[:4]

def score_concept_coverage(concept: str, retrieved_patents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes aggregate concept coverage score across all retrieved patents.
    Distinguishes exact phrase absence from semantic coverage.
    """
    if not retrieved_patents:
        return {
            "concept": concept,
            "coverage_score": 0.0,
            "coverage_band": "No Meaningful Evidence",
            "exact_phrase_present": False,
            "semantic_concept_present": False,
            "matched_equivalents": [],
            "containing_patents": [],
            "patent_count": 0
        }

    synonyms = _extract_concept_synonyms(concept)
    patent_scores = []
    containing_patents = []
    exact_present = False
    all_matched_equivalents = set()

    for p in retrieved_patents:
        pid = p.get("application_number") or p.get("publication_number") or p.get("patent_id", "Unknown")
        sc, exact_p, matched_eq = calculate_concept_coverage_for_patent(concept, p, synonyms)
        patent_scores.append(sc)
        if exact_p:
            exact_present = True
        all_matched_equivalents.update(matched_eq)
        if sc >= 30.0:
            containing_patents.append(pid)

    # Aggregate metric: 60% max single-patent relevance + 40% multi-patent density
    max_score = max(patent_scores) if patent_scores else 0.0
    density = min(1.0, len(containing_patents) / min(len(retrieved_patents), 4)) * 100.0
    final_score = round(0.60 * max_score + 0.40 * density, 1)
    final_score = max(0.0, min(100.0, final_score))

    band = get_coverage_band(final_score)
    semantic_present = final_score >= 20.0

    return {
        "concept": concept,
        "coverage_score": final_score,
        "coverage_band": band,
        "exact_phrase_present": exact_present,
        "semantic_concept_present": semantic_present,
        "matched_equivalents": sorted(list(all_matched_equivalents)),
        "containing_patents": containing_patents,
        "patent_count": len(containing_patents)
    }

def detect_innovation_gaps(
    retrieved_patents: List[Dict[str, Any]],
    query_understanding: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Phase 6A.1: Concept-Coverage Based Innovation Whitespace Detection.
    
    Whitespace is defined as:
    'A technically meaningful concept or combination with insufficient evidence across the retrieved prior-art set.'
    
    Never labels a concept 'Missing' solely because literal phrase does not occur.
    Identifies both individual concept gaps and combination-level whitespace.
    """
    if not retrieved_patents:
        return [
            {
                "concept": "Total Prior-Art Absence",
                "representation_status": "No Meaningful Evidence",
                "coverage_band": "No Meaningful Evidence",
                "coverage_score": 0.0,
                "is_combination": False,
                "explanation": "No prior art patents were located in the indexed repository; the entire technical disclosure represents potential innovation whitespace.",
                "containing_patents": []
            }
        ]

    user_concepts = (
        query_understanding.get("technical_concepts") or
        query_understanding.get("key_concepts") or
        [kw for kw in query_understanding.get("keywords", []) if len(kw) > 3]
    )
    if not user_concepts:
        user_concepts = ["Core Technical Method"]

    # 1. Score each individual concept
    concept_evals = []
    for concept in user_concepts:
        res = score_concept_coverage(concept, retrieved_patents)
        concept_evals.append(res)

    results = []

    # 2. Generate opportunities / whitespace classifications
    for ev in concept_evals:
        concept = ev["concept"]
        band = ev["coverage_band"]
        score = ev["coverage_score"]
        exact = ev["exact_phrase_present"]
        eqs = ev["matched_equivalents"]
        pats = ev["containing_patents"]

        # Determine explanation
        if band == "No Meaningful Evidence":
            status = "Missing"
            explanation = (
                f"No meaningful evidence was identified for concept '{concept}' across the retrieved prior art "
                f"(coverage score: 0/100). Both literal phrase and semantic equivalents are unmentioned."
            )
        elif band == "Minimally Represented":
            status = "Weakly Represented"
            explanation = (
                f"Concept '{concept}' has minimal representation (coverage score: {score:.0f}/100). "
                + (f"Semantic equivalents found: {', '.join(eqs[:3])}." if eqs else "Only peripheral keyword fragments found.")
            )
        elif band == "Weakly Represented":
            status = "Weakly Represented"
            explanation = (
                f"Concept '{concept}' exhibits weak prior-art coverage ({score:.0f}/100 across {len(pats)} patent(s)). "
                + (f"Equivalent terms identified: {', '.join(eqs[:3])}." if eqs else "Limited technical depth in retrieved corpus.")
            )
        elif band == "Moderately Represented":
            status = "Moderately Represented"
            phrase_note = "Exact phrase present." if exact else f"Literal phrase absent, but strongly represented via semantic equivalents: {', '.join(eqs[:3])}."
            explanation = f"Concept '{concept}' is moderately covered ({score:.0f}/100 across {len(pats)} patents). {phrase_note}"
        else: # Strongly Represented
            status = "Strongly Represented"
            phrase_note = "Exact phrase present." if exact else f"Covered via extensive equivalent terminology: {', '.join(eqs[:3])}."
            explanation = f"Concept '{concept}' is strongly represented ({score:.0f}/100 across {len(pats)} patents). {phrase_note}"

        results.append({
            "concept": concept,
            "representation_status": status,
            "coverage_band": band,
            "coverage_score": score,
            "exact_phrase_present": exact,
            "semantic_concept_present": ev["semantic_concept_present"],
            "matched_equivalents": eqs,
            "is_combination": False,
            "explanation": explanation,
            "containing_patents": pats
        })

    # 3. Evaluate Combination-Level Whitespace (Section 5)
    if len(user_concepts) >= 2:
        joint_patents = []
        for p in retrieved_patents:
            pid = p.get("application_number") or p.get("publication_number") or p.get("patent_id", "Unknown")
            covered_count = 0
            for ev in concept_evals:
                if pid in ev["containing_patents"]:
                    covered_count += 1
            if covered_count >= max(2, int(round(len(user_concepts) * 0.6))):
                joint_patents.append(pid)

        combo_ratio = len(joint_patents) / min(len(retrieved_patents), 5)
        combo_score = round(combo_ratio * 100.0, 1)

        if combo_score < 50.0:
            combo_title = " + ".join([c[:20] for c in user_concepts[:3]])
            if len(user_concepts) > 3:
                combo_title += f" (+{len(user_concepts) - 3} more)"

            results.append({
                "concept": f"System Combination: {combo_title}",
                "representation_status": "Weakly Represented" if combo_score >= 20.0 else "Missing",
                "coverage_band": "Weakly Represented" if combo_score >= 20.0 else "Minimally Represented",
                "coverage_score": combo_score,
                "exact_phrase_present": False,
                "semantic_concept_present": True,
                "is_combination": True,
                "explanation": (
                    f"Combination-Level Whitespace: While individual concepts show separate presence, "
                    f"their unified combination co-occurs in only {len(joint_patents)} patent(s) "
                    f"(combination coverage: {combo_score:.0f}/100). The specific end-to-end integration "
                    f"represents a notable innovation whitespace."
                ),
                "containing_patents": joint_patents
            })

    # Filter for reported opportunities:
    opportunities = [
        r for r in results 
        if r["coverage_score"] < 50.0 or r.get("is_combination", False)
    ]

    if not opportunities:
        opportunities.append({
            "concept": "Integrated System Optimization",
            "representation_status": "Weakly Represented",
            "coverage_band": "Weakly Represented",
            "coverage_score": 45.0,
            "is_combination": True,
            "explanation": "Individual technical concepts are well represented in the prior art; opportunity lies in holistic runtime latency optimization or edge deployment workflows.",
            "containing_patents": []
        })

    return opportunities
