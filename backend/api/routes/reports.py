import re
from fastapi import APIRouter, HTTPException, Response, status
from backend.reports.models import ReportGenerateRequest, ResearchIntelligenceReport
from backend.reports.service import report_service

router = APIRouter()

def sanitize_filename(name: str) -> str:
    """Sanitizes report ID or title for safe HTTP header Content-Disposition."""
    cleaned = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name)
    return cleaned[:60]

@router.post("/reports/generate", response_model=ResearchIntelligenceReport, status_code=status.HTTP_201_CREATED)
async def generate_report_endpoint(request: ReportGenerateRequest):
    """Generates an evidence-grounded Research Intelligence Report from available search/comparison/refinement data."""
    try:
        report = report_service.generate_report(request)
        return report
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate intelligence report: {str(e)}")

@router.get("/reports/{report_id}", response_model=ResearchIntelligenceReport)
async def get_report_endpoint(report_id: str):
    """Retrieves an existing Research Intelligence Report by ID."""
    report = report_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report with ID '{report_id}' not found or session expired.")
    return report

@router.get("/reports/{report_id}/markdown")
async def get_report_markdown_endpoint(report_id: str):
    """Exports an existing Research Intelligence Report as a Markdown (.md) document."""
    report = report_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report with ID '{report_id}' not found.")
    
    md_content = report_service.get_report_markdown(report_id)
    if not md_content:
        raise HTTPException(status_code=500, detail="Failed to render report as Markdown.")

    safe_id = sanitize_filename(report_id)
    filename = f"{safe_id}.md"

    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

@router.get("/reports/{report_id}/pdf")
async def get_report_pdf_endpoint(report_id: str):
    """Exports an existing Research Intelligence Report as a multi-page PDF document."""
    report = report_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report with ID '{report_id}' not found.")

    try:
        pdf_bytes = report_service.get_report_pdf(report_id)
        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="Failed to render report as PDF.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")

    safe_id = sanitize_filename(report_id)
    filename = f"{safe_id}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
