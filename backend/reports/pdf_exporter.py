import io
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from backend.reports.models import ResearchIntelligenceReport

class NumberedCanvas(canvas.Canvas):
    """Canvas that performs a two-pass calculation of total page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Don't draw headers/footers on cover page (page 1)
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))

            # Running header
            self.drawString(54, 755, "PatentIQ — Research Intelligence Report")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 748, 558, 748)

            # Running footer
            self.line(54, 45, 558, 45)
            self.drawString(54, 32, "CONFIDENTIAL — FOR RESEARCH & REFINEMENT ONLY — NOT LEGAL ADVICE")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 32, page_text)
            self.restoreState()

def generate_pdf_report(report: ResearchIntelligenceReport) -> bytes:
    """Renders a structured ResearchIntelligenceReport as a multi-page PDF document."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Hierarchy
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f172a"),
        alignment=0
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569")
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#334155"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1e293b")
    )
    body_muted = ParagraphStyle(
        'Body_Muted',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#64748b")
    )
    callout_style = ParagraphStyle(
        'Callout_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e293b")
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # ==================== COVER PAGE ====================
    story.append(Spacer(1, 40))
    story.append(Paragraph("PATENTIQ RESEARCH INTELLIGENCE", ParagraphStyle('CoverBadge', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor("#4f46e5"))))
    story.append(Spacer(1, 10))
    story.append(Paragraph(report.title, title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Invention Topic:</b> {report.cover_page.invention_topic}", subtitle_style))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#4f46e5"), spaceAfter=25))

    cover_meta = [
        [Paragraph("<b>Report Identifier:</b>", table_cell), Paragraph(report.report_id, table_cell)],
        [Paragraph("<b>Generated On:</b>", table_cell), Paragraph(report.generated_at, table_cell)],
        [Paragraph("<b>Intelligence Engine:</b>", table_cell), Paragraph(report.cover_page.organization, table_cell)],
        [Paragraph("<b>Classification:</b>", table_cell), Paragraph(report.cover_page.confidentiality, table_cell)],
        [Paragraph("<b>Primary Source Scope:</b>", table_cell), Paragraph(report.provenance.get("primary_source", "Federated"), table_cell)],
    ]
    t_cover = Table(cover_meta, colWidths=[140, 364])
    t_cover.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_cover)
    story.append(Spacer(1, 35))

    # Cover Page Disclaimer Box
    disc_text = (
        "<b>RESEARCH NOTICE:</b> This intelligence report is generated for empirical research, technology differentiation, "
        "and prior-art refinement purposes only. It is NOT legal advice and does NOT constitute a legal determination of patentability, "
        "novelty, validity, or freedom-to-operate. Analysis is grounded in the retrieved patent dataset."
    )
    t_disc = Table([[Paragraph(disc_text, callout_style)]], colWidths=[504])
    t_disc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_disc)

    story.append(PageBreak())

    # ==================== 1. EXECUTIVE SUMMARY ====================
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
    story.append(Paragraph(report.executive_summary.overview, body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Key Intelligence Findings:</b>", h2_style))
    for kf in report.executive_summary.key_findings:
        story.append(Paragraph(f"• {kf}", body_style))
    story.append(Spacer(1, 8))

    if report.executive_summary.top_relevant_patents:
        story.append(Paragraph(f"<b>Key Relevant Patents:</b> {', '.join(report.executive_summary.top_relevant_patents)}", body_style))
        story.append(Spacer(1, 6))

    story.append(Paragraph(f"<b>Novelty Overview:</b> {report.executive_summary.novelty_summary}", body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Differentiation Summary:</b> {report.executive_summary.differentiation_summary}", body_style))
    story.append(Spacer(1, 14))

    # ==================== 2. RESEARCH OBJECTIVE ====================
    story.append(Paragraph("2. Research Objective & Query Definition", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
    story.append(Paragraph(f"<b>Invention Statement:</b> {report.research_objective.statement}", body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Technical Domain:</b> {report.research_objective.technical_domain}", body_style))
    story.append(Spacer(1, 6))
    if report.research_objective.key_concepts:
        story.append(Paragraph(f"<b>Extracted Technical Concepts:</b> {', '.join(report.research_objective.key_concepts)}", body_style))
    story.append(Spacer(1, 14))

    # ==================== 3. METHODOLOGY & SCOPE ====================
    story.append(Paragraph("3. Methodology & Corpus Scope", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
    method_data = [
        [Paragraph("<b>Retrieval Strategy:</b>", table_cell), Paragraph(report.methodology.retrieval_strategy, table_cell)],
        [Paragraph("<b>Databases Searched:</b>", table_cell), Paragraph(", ".join(report.methodology.sources_searched), table_cell)],
        [Paragraph("<b>Documents Evaluated:</b>", table_cell), Paragraph(str(report.methodology.total_patents_evaluated), table_cell)],
        [Paragraph("<b>Scoring Framework:</b>", table_cell), Paragraph(report.methodology.scoring_framework, table_cell)],
        [Paragraph("<b>Corpus Boundaries:</b>", table_cell), Paragraph(report.methodology.limitations_summary, table_cell)],
    ]
    t_method = Table(method_data, colWidths=[130, 374])
    t_method.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_method)
    story.append(Spacer(1, 14))

    # ==================== 4. PRIOR-ART LANDSCAPE ====================
    story.append(Paragraph("4. Prior-Art Landscape", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

    if report.prior_art_landscape:
        pa_rows = [[
            Paragraph("Publication #", table_header),
            Paragraph("Title", table_header),
            Paragraph("Applicant", table_header),
            Paragraph("Date", table_header),
            Paragraph("Score", table_header),
            Paragraph("Source", table_header)
        ]]
        for pa in report.prior_art_landscape:
            rel = f"{int(pa.relevance_score * 100)}%" if pa.relevance_score <= 1.0 else f"{int(pa.relevance_score)}%"
            pa_rows.append([
                Paragraph(pa.publication_number, table_cell),
                Paragraph(pa.title, table_cell),
                Paragraph(pa.applicant or "Unknown", table_cell),
                Paragraph(pa.publication_date or "—", table_cell),
                Paragraph(rel, table_cell),
                Paragraph(pa.source, table_cell)
            ])
        t_pa = Table(pa_rows, colWidths=[75, 175, 105, 55, 40, 54])
        t_pa.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_pa)
    else:
        story.append(Paragraph("<i>No prior-art matches found for this query in the evaluated corpus.</i>", body_muted))
    story.append(Spacer(1, 16))

    # ==================== 5. DETAILED PATENT SUMMARIES ====================
    story.append(Paragraph("5. Detailed Patent Summaries", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

    for idx, ps in enumerate(report.detailed_patent_summaries, 1):
        summary_rows = [
            [Paragraph(f"<b>{idx}. {ps.publication_number}: {ps.title}</b>", table_header), Paragraph(f"Source: {ps.evidence_source}", table_cell)],
            [Paragraph("<b>Applicant:</b>", table_cell), Paragraph(ps.applicant, table_cell)],
            [Paragraph("<b>Core Technical Idea:</b>", table_cell), Paragraph(ps.core_technical_idea, table_cell)],
            [Paragraph("<b>Problem Addressed:</b>", table_cell), Paragraph(ps.problem_addressed, table_cell)],
            [Paragraph("<b>Proposed Approach:</b>", table_cell), Paragraph(ps.proposed_approach, table_cell)],
            [Paragraph("<b>Relevance to Objective:</b>", table_cell), Paragraph(ps.relevance_to_objective, table_cell)],
        ]
        if ps.key_methods:
            summary_rows.append([Paragraph("<b>Key Methods:</b>", table_cell), Paragraph(", ".join(ps.key_methods), table_cell)])

        t_summary = Table(summary_rows, colWidths=[120, 384])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(KeepTogether([t_summary, Spacer(1, 10)]))

    story.append(Spacer(1, 10))

    # ==================== 6. PATENT COMPARISON ====================
    if report.patent_comparison:
        story.append(Paragraph("6. Patent Comparison Analysis", h1_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
        story.append(Paragraph(f"<b>Compared Patents:</b> {', '.join(report.patent_comparison.compared_patents)}", body_style))
        story.append(Spacer(1, 6))

        if report.patent_comparison.shared_concepts:
            story.append(Paragraph(f"<b>Shared Technical Concepts:</b> {', '.join(report.patent_comparison.shared_concepts)}", body_style))
            story.append(Spacer(1, 6))

        story.append(Paragraph("<b>Distinct Technical Concepts per Patent:</b>", h2_style))
        for pid, concepts in report.patent_comparison.distinct_concepts.items():
            story.append(Paragraph(f"• <b>{pid}:</b> {', '.join(concepts) if concepts else 'None identified'}", body_style))
        story.append(Spacer(1, 6))

        if report.patent_comparison.technical_differences:
            story.append(Paragraph("<b>Observed Technical Differences:</b>", h2_style))
            for diff in report.patent_comparison.technical_differences:
                story.append(Paragraph(f"• {diff}", body_style))
        story.append(Spacer(1, 14))

    # ==================== 7. NOVELTY INDICATOR ====================
    if report.novelty_indicator:
        story.append(Paragraph("7. AI-Estimated Novelty Indicator", h1_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

        nov_box = [
            [Paragraph("<b>Similarity Metric:</b>", table_cell), Paragraph(f"<b>{report.novelty_indicator.overall_novelty_score} / 100</b> ({report.novelty_indicator.band})", table_cell)],
            [Paragraph("<b>Automated Rationale:</b>", table_cell), Paragraph(report.novelty_indicator.explanation, table_cell)],
            [Paragraph("<b>Disclaimer:</b>", table_cell), Paragraph(f"<i>{report.novelty_indicator.disclaimer}</i>", body_muted)],
        ]
        t_nov = Table(nov_box, colWidths=[120, 384])
        t_nov.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_nov)
        story.append(Spacer(1, 14))

    # ==================== 8. CONCEPT COVERAGE ====================
    if report.concept_coverage:
        story.append(Paragraph("8. Semantic Concept Coverage Landscape", h1_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

        cc_rows = [[
            Paragraph("Technical Concept", table_header),
            Paragraph("Coverage Status", table_header),
            Paragraph("Saturation", table_header),
            Paragraph("Supporting Prior Art", table_header)
        ]]
        for cc in report.concept_coverage:
            cc_rows.append([
                Paragraph(f"<b>{cc.concept}</b>", table_cell),
                Paragraph(cc.status, table_cell),
                Paragraph(f"{int(cc.max_similarity * 100)}%", table_cell),
                Paragraph(", ".join(cc.representative_patents) if cc.representative_patents else "—", table_cell)
            ])
        t_cc = Table(cc_rows, colWidths=[140, 130, 60, 174])
        t_cc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_cc)
        story.append(Spacer(1, 14))

    # ==================== 9. COMBINATION GAPS ====================
    if report.combination_gaps:
        story.append(Paragraph("9. Innovation Whitespace & Combination Gaps", h1_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

        for cg in report.combination_gaps:
            cg_rows = [
                [Paragraph(f"<b>{cg.gap_title}</b>", table_header), Paragraph(f"Overlap: {cg.joint_saturation}", table_cell)],
                [Paragraph("<b>Concept Pair:</b>", table_cell), Paragraph(cg.concept_pair, table_cell)],
                [Paragraph("<b>Rationale:</b>", table_cell), Paragraph(cg.rationale, table_cell)],
                [Paragraph("<b>Status:</b>", table_cell), Paragraph(cg.status, body_muted)],
            ]
            t_cg = Table(cg_rows, colWidths=[120, 384])
            t_cg.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(KeepTogether([t_cg, Spacer(1, 8)]))
        story.append(Spacer(1, 10))

    # ==================== 10. DIFFERENTIATION DIRECTIONS ====================
    if report.differentiation_directions:
        story.append(Paragraph("10. Technical Differentiation Directions", h1_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

        for dd in report.differentiation_directions:
            dd_rows = [
                [Paragraph(f"<b>[{dd.category}] {dd.direction}</b>", table_header), Paragraph(f"Gap Level: {dd.evidence_gap_level}", table_cell)],
                [Paragraph("<b>Why Investigate:</b>", table_cell), Paragraph(dd.why_investigate, table_cell)],
                [Paragraph("<b>Research Question:</b>", table_cell), Paragraph(f"<i>\"{dd.research_question}\"</i>", table_cell)],
                [Paragraph("<b>Related Concepts:</b>", table_cell), Paragraph(", ".join(dd.related_concepts), table_cell)],
            ]
            if dd.linked_patent_ids:
                dd_rows.append([Paragraph("<b>Linked Prior Art:</b>", table_cell), Paragraph(", ".join(dd.linked_patent_ids), table_cell)])

            t_dd = Table(dd_rows, colWidths=[120, 384])
            t_dd.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(KeepTogether([t_dd, Spacer(1, 8)]))
        story.append(Spacer(1, 10))

    # ==================== 11. RESEARCH QUESTIONS ====================
    if report.research_questions:
        story.append(Paragraph("11. Empirical Research Questions", h1_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
        for idx, rq in enumerate(report.research_questions, 1):
            story.append(Paragraph(f"<b>{idx}.</b> {rq}", body_style))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 12))

    # ==================== 12. APPLICANT TRENDS ====================
    if report.applicant_trends:
        story.append(Paragraph("12. Key Applicants & Field Distribution", h1_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
        at_rows = [[Paragraph("Applicant / Assignee", table_header), Paragraph("Patent Count", table_header), Paragraph("Sample Patents", table_header)]]
        for at in report.applicant_trends:
            at_rows.append([
                Paragraph(f"<b>{at.applicant}</b>", table_cell),
                Paragraph(str(at.patent_count), table_cell),
                Paragraph(", ".join(at.sample_patents), table_cell)
            ])
        t_at = Table(at_rows, colWidths=[200, 80, 224])
        t_at.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_at)
        story.append(Spacer(1, 14))

    # ==================== 13. LIMITATIONS & DATA COVERAGE ====================
    story.append(Paragraph("13. Limitations & Data Coverage", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
    story.append(Paragraph(report.limitations.dataset_coverage, body_style))
    story.append(Spacer(1, 6))
    for note in report.limitations.missing_data_notes:
        story.append(Paragraph(f"• {note}", body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<i>{report.limitations.legal_boundaries}</i>", body_muted))
    story.append(Spacer(1, 14))

    # ==================== 14. LEGAL DISCLAIMER ====================
    story.append(Paragraph("14. Mandatory Legal Disclaimer", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
    t_legal = Table([[Paragraph(f"<b>LEGAL DISCLAIMER:</b> {report.disclaimer}", callout_style)]], colWidths=[504])
    t_legal.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_legal)

    if report.unavailable_sections:
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<i>Unavailable Sections: {', '.join(report.unavailable_sections)} were omitted due to lack of verified prior-art evidence.</i>", body_muted))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
