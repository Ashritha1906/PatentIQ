import time
import logging
from typing import Dict, Any, List, Optional
from backend.api.services.vector_store import VectorStore
from backend.rag.context_compressor import compress_context
from backend.rag.context_summarizer import summarize_context
from backend.rag.evidence_ranker import rank_evidence
from backend.intelligence.concept_clustering import generate_concept_map_and_landscape
from backend.intelligence.novelty_scoring import calculate_novelty_score
from backend.intelligence.innovation_gap import detect_innovation_gaps
from backend.llm.patent_analysis import analyze_invention_novelty
from backend.reports.report_generator import calculate_confidence_assessment
from backend.retrieval.identifier_normalizer import normalize_patent_record
from backend.retrieval.query_model import PatentQuery, NLSearchResponse
from backend.retrieval.nl_retrieval import execute_nl_hybrid_search, RAG_CONTEXT_K

logger = logging.getLogger("Orchestrator")

class PatentIntelligenceService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def _retrieve_context(
        self,
        idea_text: str,
        top_k: int = 5,
        domain_filter: Optional[str] = None,
        applicant_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes query understanding, performs vector search using the abstraction layer,
        and applies deduplication logic.
        """
        # Ensure top_k is valid and positive
        if not isinstance(top_k, int) or top_k <= 0:
            logger.warning(f"Orchestrator: invalid top_k value ({top_k}) requested. Falling back to default (5).")
            top_k = 5

        # 1. Understand user idea using LLM
        from backend.llm.query_understanding import understand_query
        logger.info(f"Orchestrator: analyzing query parameters via LLM for idea: '{idea_text[:50]}'")
        query_params = understand_query(idea_text)
        
        optimized_query = query_params.get("optimized_query", idea_text)
        hints = query_params.get("metadata_hints", {})
        
        # User manual filters take precedence over LLM hints
        final_domain = domain_filter if domain_filter is not None else hints.get("field_of_invention")
        final_applicant = applicant_filter if applicant_filter is not None else hints.get("applicant_name")
        
        # 2. Query Vector Database (retrieve double for deduplication)
        logger.info(f"Orchestrator: querying vector store with query '{optimized_query[:50]}'...")
        raw_results = self.vector_store.search(
            query=optimized_query,
            top_k=top_k * 2,
            field_filter=final_domain,
            applicant_filter=final_applicant
        )
        
        # 3. Deduplicate based on Patent ID and Title
        seen_titles = set()
        seen_app_nums = set()
        deduped_results = []
        
        for res in raw_results:
            app_num = res["application_number"]
            title_normalized = res["title"].strip().upper()
            
            if app_num in seen_app_nums or title_normalized in seen_titles:
                continue
                
            seen_titles.add(title_normalized)
            seen_app_nums.add(app_num)
            deduped_results.append(normalize_patent_record(res))
            
            if len(deduped_results) >= top_k:
                break
                
        logger.info(f"Orchestrator: retrieved {len(deduped_results)} unique patents after deduplication.")
        return {
            "query_understanding": query_params,
            "retrieved_patents": deduped_results
        }

    def search_similar(
        self,
        query: str,
        top_k: int = 5,
        domain_filter: Optional[str] = None,
        applicant_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves similar patents list only (POST /search legacy mode).
        """
        context = self._retrieve_context(
            idea_text=query,
            top_k=top_k,
            domain_filter=domain_filter,
            applicant_filter=applicant_filter
        )
        return context["retrieved_patents"]

    def search_natural_language(
        self,
        query: str,
        top_k: int = 10,
        include_rag: bool = False,
        domain_filter: Optional[str] = None,
        applicant_filter: Optional[str] = None,
        source_mode: str = "hybrid"
    ) -> NLSearchResponse:
        """
        Phase 6B Federated Natural Language Search:
        Combines local PatentIQ corpus with live European Patent Office (EPO EPS) publications.
        Maintains backward compatibility and graceful fallback if live retrieval is unavailable.
        """
        logger.info(f"Orchestrator: executing federated search for '{query[:60]}' (top_k={top_k}, rag={include_rag}, mode={source_mode})")
        
        # 1. Query planning
        from backend.llm.query_understanding import plan_patent_query
        patent_query = plan_patent_query(query)
        
        # Apply explicit manual filter overrides
        if domain_filter:
            patent_query.constraints["domain_filter"] = domain_filter
        if applicant_filter:
            patent_query.applicant_constraints = [applicant_filter.strip().upper()]

        # 2. Local retrieval baseline
        db_path = getattr(self.vector_store, "db_path", "data/vectordb")
        response = execute_nl_hybrid_search(
            query_input=patent_query,
            top_k=top_k,
            db_path=db_path
        )
        local_results = response.results

        provenance_meta: Dict[str, Any] = {
            "source_mode": source_mode,
            "live_retrieval_used": False,
            "live_retrieval_status": "bypassed",
            "local_results_count": len(local_results),
            "live_results_count": 0,
            "fused_results_count": len(local_results)
        }

        # 3. Provider Layer & Federated Result Fusion (Phase 6B)
        if source_mode == "local":
            fused_results = local_results
        elif source_mode in ("hybrid", "live"):
            try:
                from backend.patent_sources.epo_publication_source import EPOPublicationSource
                from backend.patent_sources.fusion import ResultFusion

                epo_source = EPOPublicationSource()
                live_candidates = epo_source.search(
                    query=query,
                    concepts=patent_query.technical_concepts,
                    top_k=min(5, top_k)
                )
                provenance_meta["live_retrieval_used"] = True
                provenance_meta["live_retrieval_status"] = "success" if live_candidates else "no_results"
                provenance_meta["live_results_count"] = len(live_candidates)

                if source_mode == "live" and live_candidates:
                    fused_results = live_candidates
                else:
                    # Hybrid fusion with local baseline
                    fused_results, fusion_info = ResultFusion.fuse(
                        local_results=local_results,
                        live_results=live_candidates,
                        top_k=top_k
                    )
                    provenance_meta.update(fusion_info)
            except Exception as e:
                logger.warning(f"EPO live retrieval error in federated flow: {e}. Falling back to local results.")
                fused_results = local_results
                provenance_meta["live_retrieval_used"] = True
                provenance_meta["live_retrieval_status"] = f"failed: {str(e)}"
        else:
            fused_results = local_results

        response.results = fused_results
        response.total_results = len(fused_results)
        response.source_mode = source_mode
        response.provenance_metadata = provenance_meta

        # 4. RAG Integration with existing RAG pipeline
        if include_rag and response.results:
            logger.info("Orchestrator: integrating top retrieved prior art into existing Gemini RAG pipeline...")
            top_patents = response.results[:RAG_CONTEXT_K]
            patent_dicts = [
                {
                    "application_number": p.publication_number,
                    "title": p.title,
                    "applicant_name": p.applicant or "Unknown",
                    "classification_ipc": p.classification or "Unknown",
                    "field_of_invention": domain_filter or "GENERAL ENGINEERING",
                    "patent_text": p.abstract or p.title,
                    "similarity_score": p.semantic_score
                }
                for p in top_patents
            ]
            compression_res = compress_context(patent_dicts)
            compressed_block = compression_res["compressed_block"]
            response.rag_answer = analyze_invention_novelty(query, compressed_block)

        return response

    def evaluate_novelty(
        self,
        idea_text: str,
        top_k: int = 5,
        domain_filter: Optional[str] = None,
        applicant_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates novelty score only (POST /novelty).
        """
        context = self._retrieve_context(
            idea_text=idea_text,
            top_k=top_k,
            domain_filter=domain_filter,
            applicant_filter=applicant_filter
        )
        retrieved_patents = context["retrieved_patents"]
        query_understanding = context["query_understanding"]
        
        if not retrieved_patents:
            return {
                "novelty_score": 100,
                "band": "Highly Differentiated",
                "explanation": "No prior art patents found in the index.",
                "breakdown": {"similarity_overlap": 0.0, "concept_uniqueness": 100.0, "domain_saturation": 0.0}
            }
            
        return calculate_novelty_score(retrieved_patents, query_understanding)

    def analyze_idea(
        self,
        idea_text: str,
        top_k: int = 5,
        domain_filter: Optional[str] = None,
        applicant_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the full pipeline and returns structured data matching PatentIQResponse schema (POST /analyze).
        """
        start_time = time.time()
        
        # 1. Retrieve Context
        context = self._retrieve_context(
            idea_text=idea_text,
            top_k=top_k,
            domain_filter=domain_filter,
            applicant_filter=applicant_filter
        )
        retrieved_patents = context["retrieved_patents"]
        query_understanding = context["query_understanding"]
        
        if not retrieved_patents:
            raise ValueError("No matching patents found in vector database. Ingestion verify required.")

        # 2. Compress context for prompt budget
        compression_res = compress_context(retrieved_patents)
        compressed_block = compression_res["compressed_block"]

        # 3. Evidence Ranking
        ranked_patents = rank_evidence(retrieved_patents, query_understanding)

        # 4. Concept Clustering (Chroma-specific path passed via db_path if needed, fallback to default)
        db_path = getattr(self.vector_store, "db_path", "data/vectordb")
        clustering_data = generate_concept_map_and_landscape(retrieved_patents, db_path=db_path)

        # 5. Novelty Scoring
        novelty_data = calculate_novelty_score(retrieved_patents, query_understanding)

        # 6. Innovation Gap Detection
        gap_data = detect_innovation_gaps(retrieved_patents, query_understanding)

        # 7. AI Analysis (Gemini API)
        gemini_analysis = analyze_invention_novelty(idea_text, compressed_block)

        # 8. Confidence Assessment
        confidence_data = calculate_confidence_assessment(ranked_patents, novelty_data)
        
        logger.info(f"Orchestrator: Full pipeline analysis finished in {time.time() - start_time:.2f} seconds.")

        # Formulate structured response dictionary
        return {
            "user_idea": idea_text,
            "technology_domain": {
                "primary_domain": query_understanding.get("technology_domain", "GENERAL ENGINEERING"),
                "key_concepts": query_understanding.get("key_concepts", []),
                "keywords": query_understanding.get("keywords", [])
            },
            "similar_patents": retrieved_patents,
            "evidence_ranking": ranked_patents,
            "concept_clusters": {
                "concept_map": clustering_data.get("concept_map", ""),
                "cluster_summary": clustering_data.get("cluster_summary", "")
            },
            "novelty_score": novelty_data,
            "innovation_gaps": gap_data,
            "analysis": gemini_analysis,
            "confidence_score": confidence_data
        }
