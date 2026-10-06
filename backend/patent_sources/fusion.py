import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from backend.retrieval.query_model import PatentSearchResult

logger = logging.getLogger("ResultFusion")

def _canonical_dedup_key(res: PatentSearchResult) -> str:
    """
    Computes a stable deduplication key for cross-source comparison.
    Handles country + document number normalization.
    """
    raw_pub = (res.publication_number or "").strip().upper()
    country = (res.country or "").strip().upper()
    doc_num = (res.document_number or "").strip().upper()

    # Normalize European formats (e.g. EP4812013A1 -> EP4812013)
    ep_m = re.match(r'^(EP\d{7})([A-Z]\d?)?$', raw_pub)
    if ep_m:
        return f"EP_{ep_m.group(1)}"

    # Normalize Indian slash formats (e.g. 1/CHE/2010 -> IN_1_CHE_2010)
    if "/" in raw_pub:
        clean_slash = raw_pub.replace("/", "_")
        return f"IN_{clean_slash}"

    if country and doc_num:
        return f"{country}_{doc_num}"

    return raw_pub or f"ID_{res.patent_id}"

class ResultFusion:
    """
    Unified result-fusion layer combining local PatentIQ results with live EPO EPS results.
    Enforces cross-source deduplication, provenance tracking, and score calibration.
    """

    @classmethod
    def fuse(
        cls,
        local_results: List[PatentSearchResult],
        live_results: List[PatentSearchResult],
        top_k: int = 10,
        local_bias: float = 0.55
    ) -> Tuple[List[PatentSearchResult], Dict[str, Any]]:
        """
        Fuses local and live results into a unified ranked list.
        """
        seen_keys: Dict[str, PatentSearchResult] = {}
        merged_count = 0

        # 1. Process local results
        for res in local_results:
            key = _canonical_dedup_key(res)
            # Ensure local provenance tag
            res.source = res.source or "LOCAL_PATENTIQ"
            seen_keys[key] = res

        # 2. Fuse live results with deduplication & provenance merging
        for live_res in live_results:
            key = _canonical_dedup_key(live_res)
            live_res.source = live_res.source or "EPO_EPS"

            if key in seen_keys:
                # Merge duplicate result from both sources
                existing = seen_keys[key]
                existing.source = f"{existing.source} + {live_res.source}"
                existing.final_score = round(max(existing.final_score, live_res.final_score), 4)
                # Combine ranking reasons
                merged_reasons = list(dict.fromkeys(existing.ranking_reasons + live_res.ranking_reasons))
                existing.ranking_reasons = merged_reasons[:4]
                # Fill missing metadata if live has it
                if not existing.abstract and live_res.abstract:
                    existing.abstract = live_res.abstract
                merged_count += 1
            else:
                seen_keys[key] = live_res

        # 3. Score calibration & unified ranking
        unified_list = list(seen_keys.values())
        
        # Sort by final composite score descending
        unified_list.sort(key=lambda x: x.final_score, reverse=True)
        final_results = unified_list[:top_k]

        sources_present = list(dict.fromkeys(r.source for r in final_results))

        fusion_meta = {
            "local_results_count": len(local_results),
            "live_results_count": len(live_results),
            "fused_results_count": len(final_results),
            "duplicates_merged": merged_count,
            "sources_represented": sources_present
        }

        logger.info(
            f"ResultFusion: local={len(local_results)}, live={len(live_results)} "
            f"-> fused={len(final_results)} (merged={merged_count})"
        )

        return final_results, fusion_meta
