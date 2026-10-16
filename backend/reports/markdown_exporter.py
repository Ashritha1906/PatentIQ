from typing import Dict, Any
from backend.reports.models import ResearchIntelligenceReport

def generate_markdown_report(report: ResearchIntelligenceReport) -> str:
    """Renders a structured ResearchIntelligenceReport as a clean GitHub-flavored Markdown document."""
    lines = []

    # Title & Metadata
    lines.append(f"# {report.title}")
    lines.append("")
    lines.append(f"**Report ID:** `{report.report_id}`  ")
    lines.append(f"**Date Generated:** {report.generated_at}  ")
    lines.append(f"**Invention Topic:** {report.cover_page.invention_topic}  ")
    lines.append(f"**Classification:** {report.cover_page.confidentiality}  ")
    lines.append(f"**Engine:** {report.cover_page.organization}  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Table of Contents
    lines.append("## Table of Contents")
    lines.append("1. [Executive Summary](#1-executive-summary)")
    lines.append("2. [Research Objective](#2-research-objective)")
    lines.append("3. [Methodology & Scope](#3-methodology--scope)")
    lines.append("4. [Prior-Art Landscape](#4-prior-art-landscape)")
    lines.append("5. [Detailed Patent Summaries](#5-detailed-patent-summaries)")
    if report.patent_comparison:
        lines.append("6. [Patent Comparison & Deep-Dive](#6-patent-comparison--deep-dive)")
    if report.novelty_indicator:
        lines.append("7. [AI-Estimated Novelty Indicator](#7-ai-estimated-novelty-indicator)")
    if report.concept_coverage:
        lines.append("8. [Concept Coverage Landscape](#8-concept-coverage-landscape)")
    if report.combination_gaps:
        lines.append("9. [Innovation Whitespace & Combination Gaps](#9-innovation-whitespace--combination-gaps)")
    if report.differentiation_directions:
        lines.append("10. [Technical Differentiation Directions](#10-technical-differentiation-directions)")
    if report.research_questions:
        lines.append("11. [Empirical Research Questions](#11-empirical-research-questions)")
    if report.applicant_trends:
        lines.append("12. [Key Applicants & Distribution](#12-key-applicants--distribution)")
    lines.append("13. [Limitations & Data Coverage](#13-limitations--data-coverage)")
    lines.append("14. [Legal Disclaimer](#14-legal-disclaimer)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 1. Executive Summary
    lines.append("## 1. Executive Summary")
    lines.append("")
    lines.append(report.executive_summary.overview)
    lines.append("")
    lines.append("### Key Findings")
    for kf in report.executive_summary.key_findings:
        lines.append(f"- {kf}")
    lines.append("")
    if report.executive_summary.top_relevant_patents:
        lines.append(f"**Top Prior-Art Documents:** {', '.join(report.executive_summary.top_relevant_patents)}")
        lines.append("")
    lines.append(f"**Novelty Summary:** {report.executive_summary.novelty_summary}")
    lines.append("")
    lines.append(f"**Differentiation Summary:** {report.executive_summary.differentiation_summary}")
    lines.append("")

    # 2. Research Objective
    lines.append("## 2. Research Objective")
    lines.append("")
    lines.append(f"**Invention Statement:** {report.research_objective.statement}")
    lines.append("")
    lines.append(f"**Technical Domain:** {report.research_objective.technical_domain}")
    lines.append("")
    if report.research_objective.key_concepts:
        lines.append(f"**Extracted Concepts:** {', '.join(report.research_objective.key_concepts)}")
        lines.append("")

    # 3. Methodology & Scope
    lines.append("## 3. Methodology & Scope")
    lines.append("")
    lines.append(f"- **Retrieval Strategy:** {report.methodology.retrieval_strategy}")
    lines.append(f"- **Data Sources Searched:** {', '.join(report.methodology.sources_searched)}")
    lines.append(f"- **Patents Evaluated:** {report.methodology.total_patents_evaluated}")
    lines.append(f"- **Scoring Framework:** {report.methodology.scoring_framework}")
    lines.append(f"- **Scope Boundaries:** {report.methodology.limitations_summary}")
    lines.append("")

    # 4. Prior-Art Landscape
    lines.append("## 4. Prior-Art Landscape")
    lines.append("")
    if report.prior_art_landscape:
        lines.append("| Publication # | Title | Applicant | Date | Relevance | Source |")
        lines.append("| :--- | :--- | :--- | :--- | :---: | :--- |")
        for pa in report.prior_art_landscape:
            pub = pa.publication_number
            title = pa.title.replace("|", "/")
            appl = (pa.applicant or "Unknown").replace("|", "/")
            dt = pa.publication_date or "—"
            rel = f"{int(pa.relevance_score * 100)}%" if pa.relevance_score <= 1.0 else f"{int(pa.relevance_score)}%"
            src = pa.source
            lines.append(f"| `{pub}` | {title} | {appl} | {dt} | {rel} | {src} |")
        lines.append("")
    else:
        lines.append("_No prior-art documents retrieved for this query._\n")

    # 5. Detailed Patent Summaries
    lines.append("## 5. Detailed Patent Summaries")
    lines.append("")
    for ps in report.detailed_patent_summaries:
        lines.append(f"### {ps.publication_number} — {ps.title}")
        lines.append(f"- **Applicant:** {ps.applicant}")
        lines.append(f"- **Evidence Source:** {ps.evidence_source}")
        lines.append(f"- **Core Technical Idea:** {ps.core_technical_idea}")
        lines.append(f"- **Problem Addressed:** {ps.problem_addressed}")
        lines.append(f"- **Proposed Approach:** {ps.proposed_approach}")
        lines.append(f"- **Relevance to Research Objective:** {ps.relevance_to_objective}")
        if ps.key_methods:
            lines.append(f"- **Key Technical Methods:** {', '.join(ps.key_methods)}")
        lines.append("")

    # 6. Patent Comparison
    if report.patent_comparison:
        lines.append("## 6. Patent Comparison & Deep-Dive")
        lines.append("")
        lines.append(f"**Compared Patents:** {', '.join(report.patent_comparison.compared_patents)}")
        lines.append("")
        if report.patent_comparison.shared_concepts:
            lines.append(f"**Shared Concepts:** {', '.join(report.patent_comparison.shared_concepts)}")
            lines.append("")
        lines.append("### Distinct Concepts per Patent")
        for pid, concepts in report.patent_comparison.distinct_concepts.items():
            lines.append(f"- **`{pid}`:** {', '.join(concepts) if concepts else 'None noted'}")
        lines.append("")
        if report.patent_comparison.technical_differences:
            lines.append("### Key Technical Differences")
            for diff in report.patent_comparison.technical_differences:
                lines.append(f"- {diff}")
            lines.append("")

    # 7. Novelty Indicator
    if report.novelty_indicator:
        lines.append("## 7. AI-Estimated Novelty Indicator")
        lines.append("")
        lines.append(f"> **Indicator Score:** {report.novelty_indicator.overall_novelty_score}/100  ")
        lines.append(f"> **Classification Band:** {report.novelty_indicator.band}  ")
        lines.append(f"> **Automated Rationale:** {report.novelty_indicator.explanation}")
        lines.append("")
        lines.append(f"*Notice: {report.novelty_indicator.disclaimer}*")
        lines.append("")

    # 8. Concept Coverage Landscape
    if report.concept_coverage:
        lines.append("## 8. Concept Coverage Landscape")
        lines.append("")
        lines.append("| Concept | Representation Status | Saturation Score | Supporting Prior Art |")
        lines.append("| :--- | :--- | :---: | :--- |")
        for cc in report.concept_coverage:
            rep = cc.status
            sat = f"{int(cc.max_similarity * 100)}%"
            pats = ", ".join(cc.representative_patents) if cc.representative_patents else "None"
            lines.append(f"| **{cc.concept}** | {rep} | {sat} | {pats} |")
        lines.append("")

    # 9. Combination Gaps
    if report.combination_gaps:
        lines.append("## 9. Innovation Whitespace & Combination Gaps")
        lines.append("")
        for cg in report.combination_gaps:
            lines.append(f"### {cg.gap_title}")
            lines.append(f"- **Concept Pair:** `{cg.concept_pair}`")
            lines.append(f"- **Joint Overlap Level:** {cg.joint_saturation}")
            lines.append(f"- **Rationale:** {cg.rationale}")
            lines.append(f"- **Research Classification:** {cg.status}")
            lines.append("")

    # 10. Differentiation Directions
    if report.differentiation_directions:
        lines.append("## 10. Technical Differentiation Directions")
        lines.append("")
        for dd in report.differentiation_directions:
            lines.append(f"### [{dd.category}] {dd.direction}")
            lines.append(f"- **Evidence Gap Level:** `{dd.evidence_gap_level}`")
            lines.append(f"- **Why Investigate:** {dd.why_investigate}")
            lines.append(f"- **Related Concepts:** {', '.join(dd.related_concepts)}")
            lines.append(f"- **Research Question:** *\"{dd.research_question}\"*")
            if dd.linked_patent_ids:
                lines.append(f"- **Linked Prior-Art References:** {', '.join(dd.linked_patent_ids)}")
            lines.append("")

    # 11. Research Questions
    if report.research_questions:
        lines.append("## 11. Empirical Research Questions")
        lines.append("")
        for idx, rq in enumerate(report.research_questions, 1):
            lines.append(f"{idx}. {rq}")
        lines.append("")

    # 12. Applicant Trends
    if report.applicant_trends:
        lines.append("## 12. Key Applicants & Distribution")
        lines.append("")
        for at in report.applicant_trends:
            lines.append(f"- **{at.applicant}:** {at.patent_count} patent(s) (`{', '.join(at.sample_patents)}`)")
        lines.append("")

    # 13. Limitations & Data Coverage
    lines.append("## 13. Limitations & Data Coverage")
    lines.append("")
    lines.append(report.limitations.dataset_coverage)
    lines.append("")
    for note in report.limitations.missing_data_notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append(f"*{report.limitations.legal_boundaries}*")
    lines.append("")

    # 14. Mandatory Legal Disclaimer
    lines.append("## 14. Legal Disclaimer")
    lines.append("")
    lines.append(f"> **IMPORTANT:** {report.disclaimer}")
    lines.append("")

    if report.unavailable_sections:
        lines.append("---")
        lines.append("")
        lines.append(f"**Note on Unavailable Sections:** The following sections could not be derived from the available evidence and were omitted: {', '.join(report.unavailable_sections)}.")
        lines.append("")

    return "\n".join(lines)
