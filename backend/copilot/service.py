import re
import logging
from typing import Dict, Any, List, Optional
from backend.copilot.models import (
    CopilotIntent,
    CopilotChatRequest,
    CopilotChatResponse,
    ResearchContextSummary
)
from backend.copilot.context import CopilotSession, session_manager
from backend.copilot.intent import classify_intent
from backend.copilot.resolver import (
    resolve_target_patent,
    resolve_comparison_targets,
    extract_specific_technical_inquiry
)
from backend.api.services.dependencies import get_patent_service
from backend.llm.gemini_client import generate_text

logger = logging.getLogger("CopilotService")

COPILOT_SYSTEM_INSTRUCTION = (
    "You are PatentIQ Research Copilot, an AI assistant for patent research.\n"
    "Your job is to help users understand patent information, discover prior art, compare patents, "
    "interpret concept coverage, and explore potential technology gaps.\n"
    "Use only the research context, retrieved patent information, and user-provided information available to you.\n"
    "Never fabricate patent numbers, titles, applicants, claims, technical methods, dates, or other patent facts.\n"
    "If the available evidence is insufficient, explicitly say that you do not have enough information.\n"
    "Clearly distinguish retrieved facts from AI interpretation.\n"
    "When discussing novelty, use the term 'AI-Estimated Novelty Indicator' or 'AI Prior-Art Novelty Indicator'.\n"
    "Never claim that an invention is legally novel, patentable, infringement-free, or guaranteed to receive patent protection.\n"
    "The novelty indicator is an automated prior-art similarity indicator and is not a legal determination of patentability or novelty.\n"
    "Explain complex patent concepts in clear natural language unless the user requests technical detail."
)

DISCLAIMER_TEXT = (
    "This is an automated prior-art similarity indicator and is not a legal determination of patentability or novelty."
)

class CopilotService:
    def __init__(self):
        self._orchestrator = None

    @property
    def orchestrator(self):
        if self._orchestrator is None:
            self._orchestrator = get_patent_service()
        return self._orchestrator

    def handle_chat(self, request: CopilotChatRequest) -> CopilotChatResponse:
        session = session_manager.get_or_create(
            session_id=request.session_id,
            source_mode=request.source_mode or "hybrid"
        )
        user_msg = (request.message or "").strip()
        if not user_msg:
            return CopilotChatResponse(
                session_id=session.session_id,
                message="Please provide a patent research question, invention description, or follow-up query.",
                intent="IDLE",
                research_context=session.get_summary(),
                suggested_followups=[
                    "Find patents for AI wildfire detection using satellite images",
                    "Search patents related to non-invasive glucose monitoring",
                    "Explain the difference between local and EPO patent sources"
                ]
            )

        # 1. Classify intent
        intent, intent_details = classify_intent(user_msg, session)
        session.add_turn(role="user", content=user_msg, intent=intent.value)

        # 2. Dispatch to dedicated intent handler
        if intent == CopilotIntent.PRIOR_ART_SEARCH:
            response = self._handle_search(user_msg, session, request.top_k or 5, intent_details)
        elif intent == CopilotIntent.EXPLAIN:
            response = self._handle_explain(user_msg, session, intent_details)
        elif intent == CopilotIntent.COMPARE:
            response = self._handle_compare(user_msg, session, intent_details)
        elif intent == CopilotIntent.SUMMARIZE:
            response = self._handle_summarize(user_msg, session)
        elif intent == CopilotIntent.WHITESPACE:
            response = self._handle_whitespace(user_msg, session)
        elif intent == CopilotIntent.IMPROVE_IDEA:
            response = self._handle_improve_idea(user_msg, session)
        elif intent == CopilotIntent.REPORT:
            response = self._handle_report(user_msg, session)
        else:
            response = self._handle_follow_up(user_msg, session, intent_details)

        # Record assistant response in session turn history
        session.add_turn(role="copilot", content=response.message, intent=intent.value)
        response.research_context = session.get_summary()
        return response

    def _handle_search(
        self,
        query: str,
        session: CopilotSession,
        top_k: int,
        intent_details: Dict[str, Any]
    ) -> CopilotChatResponse:
        logger.info(f"Copilot executing prior art search for: '{query[:60]}'")
        try:
            nl_response = self.orchestrator.search_natural_language(
                query=query,
                top_k=top_k,
                include_rag=False,
                source_mode=session.source_mode
            )
            patents_raw = [p.model_dump() for p in nl_response.results]
            query_und = nl_response.interpreted_query.model_dump() if getattr(nl_response, "interpreted_query", None) else {}
            concepts = nl_response.interpreted_query.technical_concepts if getattr(nl_response, "interpreted_query", None) else []
            provenance = nl_response.provenance_metadata

            session.set_retrieved_patents(
                patents=patents_raw,
                query=query,
                concepts=concepts,
                provenance=provenance
            )

            if not patents_raw:
                msg = (
                    f"No highly relevant patents were found for '{query}' in the currently available PatentIQ sources. "
                    "Try describing the technical components or operational methods of your idea in more detail."
                )
                followups = ["Search with broader technical keywords", "Check EPO live sources"]
            else:
                top_p = patents_raw[0]
                top_title = top_p.get("title", "Untitled")
                top_id = top_p.get("publication_number") or top_p.get("application_number") or "N/A"
                top_sim = round((top_p.get("semantic_score") or 0.0) * 100)

                lines = [
                    f"I found {len(patents_raw)} relevant patents matching your research query.",
                    f"\nThe most relevant result is **{top_id}**: *\"{top_title}\"* ({top_sim}% semantic similarity).",
                    "\nKey retrieved prior art:"
                ]
                for i, p in enumerate(patents_raw[:3], start=1):
                    pid = p.get("publication_number") or p.get("application_number") or "N/A"
                    ptitle = p.get("title", "Untitled")
                    papp = p.get("applicant") or "Unknown"
                    psim = round((p.get("semantic_score") or 0.0) * 100)
                    lines.append(f"{i}. **{pid}** — *{ptitle}* (Applicant: {papp}, Relevance: {psim}%)")

                lines.append(
                    f"\nThe strongest overlap is in {', '.join(concepts[:3]) if concepts else 'the primary technology field'}."
                )
                msg = "\n".join(lines)
                followups = [
                    "Which one is closest to my idea?",
                    "Explain the closest patent in simple words",
                    "Compare the top 2 patents",
                    "What areas are not well covered?"
                ]

            return CopilotChatResponse(
                session_id=session.session_id,
                message=msg,
                intent=CopilotIntent.PRIOR_ART_SEARCH.value,
                query_understanding=query_und,
                patents=patents_raw,
                selected_patent=session.selected_patent,
                provenance=provenance,
                research_context=session.get_summary(),
                suggested_followups=followups
            )

        except Exception as e:
            logger.error(f"Copilot search error: {e}", exc_info=True)
            return CopilotChatResponse(
                session_id=session.session_id,
                message=f"I encountered an error retrieving prior art patents: {str(e)}. Please try refining your query.",
                intent=CopilotIntent.PRIOR_ART_SEARCH.value,
                research_context=session.get_summary(),
                suggested_followups=["Try a simpler technical search query"]
            )

    def _handle_explain(
        self,
        query: str,
        session: CopilotSession,
        intent_details: Dict[str, Any]
    ) -> CopilotChatResponse:
        patent = resolve_target_patent(query, session, intent_details)
        if not patent:
            return CopilotChatResponse(
                session_id=session.session_id,
                message="I don't have any retrieved patents in our session context to explain yet. Please start by searching for an invention topic.",
                intent=CopilotIntent.EXPLAIN.value,
                research_context=session.get_summary(),
                suggested_followups=["Search patents for AI forest fire detection", "Find healthcare diagnostic patents"]
            )

        session.selected_patent = patent
        pid = patent.get("publication_number") or patent.get("application_number") or "Unknown"
        title = patent.get("title", "Untitled")
        abstract = patent.get("abstract") or patent.get("patent_text") or "Abstract not available."
        applicant = patent.get("applicant") or "Unknown"
        classification = patent.get("classification") or "Unknown IPC"

        prompt = (
            f"Explain the following patent in simple, clear language for a non-legal researcher:\n"
            f"Patent ID: {pid}\n"
            f"Title: {title}\n"
            f"Applicant: {applicant}\n"
            f"Classification: {classification}\n"
            f"Abstract: {abstract[:1200]}\n\n"
            f"Structure your explanation with:\n"
            f"1. Core Technical Problem & Solution\n"
            f"2. How the System Works\n"
            f"3. Key Technical Components\n"
            f"4. Why It Matters\n"
            f"Strictly avoid legal patentability conclusions and do not invent details outside the abstract."
        )

        try:
            explanation = generate_text(prompt, system_instruction=COPILOT_SYSTEM_INSTRUCTION)
        except Exception:
            explanation = (
                f"### Explanation for {pid}: {title}\n\n"
                f"**Applicant:** {applicant} | **IPC Classification:** {classification}\n\n"
                f"**What it is about:**\n{abstract}\n\n"
                f"**Core Technical Mechanism:**\nThis patent addresses technical operations categorized under {classification}. "
                f"It details functional steps designed to automate or improve performance in this field."
            )

        return CopilotChatResponse(
            session_id=session.session_id,
            message=explanation,
            intent=CopilotIntent.EXPLAIN.value,
            selected_patent=patent,
            patents=session.retrieved_patents,
            provenance=session.provenance,
            research_context=session.get_summary(),
            suggested_followups=[
                "Does it use deep learning?",
                "How is my idea different?",
                "Compare it with the second patent",
                "What concepts are missing?"
            ]
        )

    def _handle_compare(
        self,
        query: str,
        session: CopilotSession,
        intent_details: Dict[str, Any]
    ) -> CopilotChatResponse:
        targets = resolve_comparison_targets(query, session, intent_details)
        if len(targets) < 2:
            return CopilotChatResponse(
                session_id=session.session_id,
                message="I need at least two retrieved patents in context to perform a comparison. Try searching for a technical topic first.",
                intent=CopilotIntent.COMPARE.value,
                research_context=session.get_summary(),
                suggested_followups=["Search patents for diabetic retinopathy", "Find drone surveillance patents"]
            )

        p1, p2 = targets[0], targets[1]
        p1_id = p1.get("publication_number") or p1.get("application_number") or "Patent 1"
        p2_id = p2.get("publication_number") or p2.get("application_number") or "Patent 2"

        prompt = (
            f"Perform a technical comparison between these two retrieved patents based strictly on their provided text:\n\n"
            f"PATENT A:\n- ID: {p1_id}\n- Title: {p1.get('title')}\n- Applicant: {p1.get('applicant')}\n- IPC: {p1.get('classification')}\n- Text: {p1.get('abstract', '')[:800]}\n\n"
            f"PATENT B:\n- ID: {p2_id}\n- Title: {p2.get('title')}\n- Applicant: {p2.get('applicant')}\n- IPC: {p2.get('classification')}\n- Text: {p2.get('abstract', '')[:800]}\n\n"
            f"Provide:\n"
            f"1. Common Technical Concepts (Overlap)\n"
            f"2. Key Differences in Approach\n"
            f"3. Unique Features of Each\n"
            f"4. Summary of Technological Trade-offs\n"
            f"Do not make any claims regarding legal infringement or validity."
        )

        try:
            comparison_text = generate_text(prompt, system_instruction=COPILOT_SYSTEM_INSTRUCTION)
        except Exception:
            comparison_text = (
                f"### Technical Comparison: {p1_id} vs {p2_id}\n\n"
                f"- **{p1_id}**: *\"{p1.get('title')}\"* (Applicant: {p1.get('applicant')})\n"
                f"- **{p2_id}**: *\"{p2.get('title')}\"* (Applicant: {p2.get('applicant')})\n\n"
                f"**Overlapping Scope:** Both patents operate in classification {p1.get('classification', 'N/A')} / {p2.get('classification', 'N/A')}.\n\n"
                f"**Technical Differences:**\n"
                f"- {p1_id} focuses on: {p1.get('abstract', '')[:200]}...\n"
                f"- {p2_id} focuses on: {p2.get('abstract', '')[:200]}..."
            )

        return CopilotChatResponse(
            session_id=session.session_id,
            message=comparison_text,
            intent=CopilotIntent.COMPARE.value,
            patents=[p1, p2],
            analysis={"compared_patents": [p1_id, p2_id]},
            research_context=session.get_summary(),
            suggested_followups=[
                "Which one is closer to my research idea?",
                "What technology areas are not well covered?",
                "How can I differentiate from these?"
            ]
        )

    def _handle_summarize(self, query: str, session: CopilotSession) -> CopilotChatResponse:
        if not session.retrieved_patents:
            return CopilotChatResponse(
                session_id=session.session_id,
                message="There are no retrieved patents in the current session to summarize. Please enter a patent query first.",
                intent=CopilotIntent.SUMMARIZE.value,
                research_context=session.get_summary()
            )

        patents = session.retrieved_patents[:5]
        summary_lines = [
            f"### Prior Art Landscape Summary ({len(patents)} Patents Retrieved)\n",
            f"**Research Topic:** {session.current_query or 'General Patent Search'}\n"
        ]
        for i, p in enumerate(patents, start=1):
            pid = p.get("publication_number") or p.get("application_number") or "N/A"
            title = p.get("title", "Untitled")
            app = p.get("applicant") or "Unknown"
            score = round((p.get("semantic_score") or 0.0) * 100)
            summary_lines.append(f"{i}. **{pid}** — *{title}* ({app}, {score}% relevance)")

        summary_lines.append("\n**Key Technological Patterns:**")
        summary_lines.append(
            f"The retrieved set demonstrates prior art coverage primarily concentrated around {', '.join(session.technical_concepts[:4]) if session.technical_concepts else 'the core domain concepts'}."
        )

        return CopilotChatResponse(
            session_id=session.session_id,
            message="\n".join(summary_lines),
            intent=CopilotIntent.SUMMARIZE.value,
            patents=session.retrieved_patents,
            research_context=session.get_summary(),
            suggested_followups=[
                "What areas are not well covered?",
                "Explain the top patent",
                "Compare the top 2 patents"
            ]
        )

    def _handle_whitespace(self, query: str, session: CopilotSession) -> CopilotChatResponse:
        if not session.retrieved_patents:
            return CopilotChatResponse(
                session_id=session.session_id,
                message="To identify technology whitespace and coverage gaps, please first search for an invention topic.",
                intent=CopilotIntent.WHITESPACE.value,
                research_context=session.get_summary()
            )

        from backend.intelligence.innovation_gap import detect_innovation_gaps

        query_understanding = {
            "technology_domain": "GENERAL TECHNOLOGY",
            "key_concepts": session.technical_concepts or [session.current_query or "system"]
        }
        gaps = detect_innovation_gaps(session.retrieved_patents, query_understanding)
        session.cached_whitespace = {"gaps": gaps}

        lines = [
            "### Technology Whitespace & Concept Coverage Analysis\n",
            "Based on the retrieved prior-art set, here is the distribution of concept coverage:\n"
        ]

        for g in gaps:
            name = g.get("concept") or g.get("gap_title") or "Concept"
            status = g.get("status") or g.get("opportunity_level") or "Analyzed"
            score = round(g.get("coverage_score", 0.0) * 100)
            opp = g.get("description") or g.get("recommendation") or ""
            lines.append(f"- **{name}** (`{status}` - Coverage: {score}%): {opp}")

        lines.append(
            "\n*Combination Gaps:* Where individual concepts exist separately in prior art but their specific integration is minimally represented."
        )

        return CopilotChatResponse(
            session_id=session.session_id,
            message="\n".join(lines),
            intent=CopilotIntent.WHITESPACE.value,
            analysis={"whitespace_gaps": gaps},
            patents=session.retrieved_patents,
            research_context=session.get_summary(),
            suggested_followups=[
                "How can I make my idea more differentiated?",
                "Explain the closest patent",
                "Generate a research report"
            ]
        )

    def _handle_improve_idea(self, query: str, session: CopilotSession) -> CopilotChatResponse:
        if not session.retrieved_patents:
            return CopilotChatResponse(
                session_id=session.session_id,
                message="Please search for prior art related to your idea first so I can analyze how to differentiate it.",
                intent=CopilotIntent.IMPROVE_IDEA.value,
                research_context=session.get_summary()
            )

        from backend.intelligence.novelty_scoring import calculate_novelty_score
        from backend.intelligence.innovation_gap import detect_innovation_gaps

        query_und = {
            "technology_domain": "GENERAL TECHNOLOGY",
            "key_concepts": session.technical_concepts or [session.current_query or "concept"]
        }
        novelty_data = calculate_novelty_score(session.retrieved_patents, query_und)
        gap_data = detect_innovation_gaps(session.retrieved_patents, query_und)

        novelty_score = novelty_data.get("overall_novelty_score", 50)
        indicator_name = "AI-Estimated Novelty Indicator"

        weak_concepts = [
            g.get("concept") for g in gap_data 
            if g.get("status") in ("Weakly Represented", "No Meaningful Evidence", "Combination Gap")
        ]

        lines = [
            f"### Research Differentiation Directions\n",
            f"**{indicator_name}:** {novelty_score}/100 ({novelty_data.get('band', 'Moderate Differentiation')})\n",
            "Based on the retrieved prior-art set, here are technically grounded avenues to enhance differentiation:\n"
        ]

        if weak_concepts:
            lines.append("**1. Target Minimally Represented Concepts:**")
            for c in weak_concepts[:3]:
                lines.append(f"- Prior art shows limited saturation around **{c}**. Emphasizing novel implementations here reduces overlap.")
        else:
            lines.append(
                "**1. Hybrid Architectural Combinations:** Explore multi-modal data fusion or decentralized edge architectures to diverge from existing monolithic patents."
            )

        lines.append(
            "\n**2. Specific Operational Constraints:** Rather than general algorithmic claims, focus on domain-specific edge cases, constrained latency parameters, or proprietary feedback loops."
        )
        lines.append(
            "\n*Note: Based on the retrieved prior-art set, these observations reflect technical differentiation and do NOT constitute legal advice or guarantee patentability.*"
        )

        return CopilotChatResponse(
            session_id=session.session_id,
            message="\n".join(lines),
            intent=CopilotIntent.IMPROVE_IDEA.value,
            analysis={"novelty": novelty_data, "gaps": gap_data},
            patents=session.retrieved_patents,
            research_context=session.get_summary(),
            suggested_followups=[
                "What areas are not well covered?",
                "Which patent is closest?",
                "Explain the closest patent"
            ]
        )

    def _handle_report(self, query: str, session: CopilotSession) -> CopilotChatResponse:
        if not session.retrieved_patents:
            return CopilotChatResponse(
                session_id=session.session_id,
                message="Cannot generate a report without retrieved patent records. Please search for an invention topic first.",
                intent=CopilotIntent.REPORT.value,
                research_context=session.get_summary()
            )

        patents = session.retrieved_patents
        top_p = patents[0]
        report_text = (
            f"## PATENTIQ RESEARCH INTELLIGENCE REPORT\n"
            f"**Research Topic:** {session.current_query}\n"
            f"**Source Mode:** {session.source_mode.upper()}\n"
            f"**Total Prior Art Patents Retrieved:** {len(patents)}\n\n"
            f"### 1. Primary Prior Art Document\n"
            f"- **Publication Number:** {top_p.get('publication_number') or top_p.get('application_number')}\n"
            f"- **Title:** {top_p.get('title')}\n"
            f"- **Applicant:** {top_p.get('applicant', 'Unknown')}\n"
            f"- **Semantic Similarity:** {round((top_p.get('semantic_score') or 0.0) * 100)}%\n\n"
            f"### 2. Prior Art Set Overview\n"
        )
        for i, p in enumerate(patents[:5], start=1):
            report_text += f"{i}. {p.get('publication_number')}: *{p.get('title')}* ({round((p.get('semantic_score') or 0.0) * 100)}% similarity)\n"

        report_text += f"\n\n> {DISCLAIMER_TEXT}"

        return CopilotChatResponse(
            session_id=session.session_id,
            message=report_text,
            intent=CopilotIntent.REPORT.value,
            patents=patents,
            research_context=session.get_summary(),
            suggested_followups=["Explain the closest patent", "What areas are not well covered?"]
        )

    def _handle_follow_up(
        self,
        query: str,
        session: CopilotSession,
        intent_details: Dict[str, Any]
    ) -> CopilotChatResponse:
        if not session.retrieved_patents:
            return self._handle_search(query, session, 5, intent_details)

        q_lower = query.lower()
        target_patent = resolve_target_patent(query, session, intent_details) or session.retrieved_patents[0]
        target_id = target_patent.get("publication_number") or target_patent.get("application_number") or "N/A"
        target_title = target_patent.get("title", "Untitled")
        target_abstract = target_patent.get("abstract") or target_patent.get("patent_text") or ""

        # Case A: "Which one is closest?"
        if any(k in q_lower for k in ["which one is closest", "which is closest", "most relevant", "closest to my idea"]):
            top_p = session.retrieved_patents[0]
            pid = top_p.get("publication_number") or top_p.get("application_number") or "N/A"
            score = round((top_p.get("semantic_score") or 0.0) * 100)
            msg = (
                f"The closest patent to your research idea is **{pid}**: *\"{top_p.get('title')}\"* with a semantic similarity score of {score}%.\n\n"
                f"It was filed by **{top_p.get('applicant', 'Unknown')}** and covers: {top_p.get('abstract', '')[:250]}..."
            )
            session.selected_patent = top_p
            return CopilotChatResponse(
                session_id=session.session_id,
                message=msg,
                intent=CopilotIntent.FOLLOW_UP.value,
                selected_patent=top_p,
                patents=session.retrieved_patents,
                research_context=session.get_summary(),
                suggested_followups=["Why is it closest?", "Explain that patent in simple words", "Is my idea different?"]
            )

        # Case B: "Why?" / "Why is it closest?"
        if q_lower.strip() in ["why", "why?", "why is it closest?", "why is it closest", "why is that?"]:
            p = session.selected_patent or session.retrieved_patents[0]
            pid = p.get("publication_number") or p.get("application_number") or "N/A"
            score = round((p.get("semantic_score") or 0.0) * 100)
            concepts = session.technical_concepts or ["the core technology"]
            msg = (
                f"Patent **{pid}** is ranked as the closest match ({score}% semantic similarity) because its abstract and claims "
                f"directly describe methods involving {', '.join(concepts[:3])}.\n\n"
                f"Specifically, it addresses: \"{p.get('abstract', '')[:300]}...\"\n\n"
                "This represents the highest dense embedding alignment and lexical overlap with your original query."
            )
            return CopilotChatResponse(
                session_id=session.session_id,
                message=msg,
                intent=CopilotIntent.FOLLOW_UP.value,
                selected_patent=p,
                patents=session.retrieved_patents,
                research_context=session.get_summary(),
                suggested_followups=["Is my idea different?", "Explain this patent", "Compare with the second patent"]
            )

        # Case C: "Is my idea different?"
        if any(k in q_lower for k in ["is my idea different", "how is my idea different", "am i different"]):
            p = session.selected_patent or session.retrieved_patents[0]
            pid = p.get("publication_number") or p.get("application_number") or "N/A"
            msg = (
                f"Based on the retrieved prior-art set, your idea shares conceptual overlap with **{pid}** regarding "
                f"{', '.join(session.technical_concepts[:2]) if session.technical_concepts else 'primary technical functions'}.\n\n"
                f"However, differences depend on specific implementation: **{pid}** explicitly covers: \"{p.get('abstract', '')[:250]}...\".\n\n"
                "If your system introduces unique algorithm architectures, different data constraints, or combination elements not recited here, "
                "those aspects represent technological differentiation. (Note: this is an automated prior-art comparison, not a legal novelty determination)."
            )
            return CopilotChatResponse(
                session_id=session.session_id,
                message=msg,
                intent=CopilotIntent.FOLLOW_UP.value,
                selected_patent=p,
                patents=session.retrieved_patents,
                research_context=session.get_summary(),
                suggested_followups=["How can I make my idea more differentiated?", "What areas are not well covered?"]
            )

        # Case D: Specific technical inquiry (e.g. "Does it use CNN?")
        specific_tech = extract_specific_technical_inquiry(query)
        if specific_tech:
            tech_lower = specific_tech.lower()
            text_to_check = (target_title + " " + target_abstract).lower()
            
            if tech_lower in text_to_check or any(alias in text_to_check for alias in [tech_lower.replace(" ", ""), tech_lower.replace("-", " ")]):
                msg = (
                    f"Yes. Based on the retrieved patent document for **{target_id}**, there is explicit evidence referencing "
                    f"**{specific_tech}** in the patent disclosure: \"...{target_abstract[:250]}...\""
                )
            else:
                msg = (
                    f"The retrieved patent information for **{target_id}** does not provide enough evidence for me to confirm "
                    f"whether it uses **{specific_tech}**.\n\n"
                    "The available abstract and metadata focus on: "
                    f"\"{target_abstract[:200]}...\" without explicitly reciting {specific_tech}."
                )

            return CopilotChatResponse(
                session_id=session.session_id,
                message=msg,
                intent=CopilotIntent.FOLLOW_UP.value,
                selected_patent=target_patent,
                patents=session.retrieved_patents,
                research_context=session.get_summary(),
                suggested_followups=["Explain this patent", "Compare with the second patent", "What concepts are missing?"]
            )

        # Case E: General follow-up inquiry resolved with Gemini RAG grounding
        prompt = (
            f"You are answering a follow-up patent research question.\n"
            f"Active Research Topic: {session.current_query}\n"
            f"Active Selected Patent: {target_id} - {target_title}\n"
            f"Retrieved Document Text: {target_abstract[:1200]}\n"
            f"User Question: \"{query}\"\n\n"
            f"Answer accurately and concisely strictly based on the retrieved patent text.\n"
            f"If the retrieved document does not contain enough evidence to answer, state clearly:\n"
            f"'I don't have enough information in the retrieved patent data to determine that.'\n"
            f"Do not guess or fabricate facts."
        )

        try:
            answer = generate_text(prompt, system_instruction=COPILOT_SYSTEM_INSTRUCTION)
        except Exception:
            answer = (
                f"Regarding **{target_id}**: based strictly on the retrieved summary, "
                f"it discloses: {target_abstract[:300]}..."
            )

        return CopilotChatResponse(
            session_id=session.session_id,
            message=answer,
            intent=CopilotIntent.FOLLOW_UP.value,
            selected_patent=target_patent,
            patents=session.retrieved_patents,
            research_context=session.get_summary(),
            suggested_followups=["Explain this patent in simple words", "Compare the top 2 patents", "What areas are not well covered?"]
        )

copilot_service = CopilotService()
