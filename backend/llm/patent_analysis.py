import logging
from backend.llm.gemini_client import generate_text

logger = logging.getLogger("PatentAnalysis")

SYSTEM_INSTRUCTION = (
    "You are a Senior Patent Attorney and Novelty Analyst. Your task is to analyze "
    "a user's invention idea against a list of retrieved patents.\n"
    "CRITICAL REQUIREMENT:\n"
    "1. You must reason ONLY using the provided retrieved patent context. Do not make "
    "assumptions or draw conclusions unsupported by the text.\n"
    "2. Every similarity or overlap you identify must cite the corresponding Patent ID (e.g. [1/CHE/2010]).\n"
    "3. Do not invent or refer to patents not listed in the context.\n"
    "4. Clearly separate facts derived from the context from your analytical reasoning.\n\n"
    "Structure your analysis into these 6 categories:\n"
    "1. Similar Technologies\n"
    "2. Overlapping Concepts\n"
    "3. Technical Similarities\n"
    "4. Potential Novel Areas\n"
    "5. Innovation Opportunities\n"
    "6. Technology Classification"
)

def analyze_invention_novelty(user_idea, compressed_context_block):
    """
    Invokes Gemini to run a strict context-constrained analysis of the user's invention against retrieved patent context.
    """
    prompt = (
        f"USER INVENTION IDEA:\n"
        f"\"{user_idea}\"\n\n"
        f"RETRIEVED PATENT CONTEXT:\n"
        f"{compressed_context_block}\n\n"
        f"Run a detailed, evidence-based novelty and similarity analysis according to the instructions."
    )
    
    logger.info("Executing patent similarity and novelty analysis...")
    analysis_report = generate_text(prompt, system_instruction=SYSTEM_INSTRUCTION)
    return analysis_report
