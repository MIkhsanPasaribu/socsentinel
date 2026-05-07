"""
SOCsentinel — Report Export API router.

Endpoints for exporting investigation reports as PDF and DOCX.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.shared.schemas import APIResponse
from app.shared.exceptions.base import NotFoundError
from app.core.logger import get_logger

from .service import export_investigation_docx
from .pdf_generator import WEASYPRINT_AVAILABLE

# Only import PDF export if WeasyPrint is available
if WEASYPRINT_AVAILABLE:
    from .service import export_investigation_pdf
else:
    export_investigation_pdf = None

logger = get_logger(__name__)

router = APIRouter(prefix="/report-export", tags=["Report Export"])


@router.get("/export/{investigation_id}/pdf")
async def export_pdf_endpoint(investigation_id: str) -> StreamingResponse:
    """Export investigation report as a professionally formatted PDF.

    Generates a PDF report with cover page, executive summary,
    MITRE ATT&CK mapping, detection rules, and response playbook.

    Args:
        investigation_id: The unique investigation ID.

    Returns:
        StreamingResponse with PDF content and download headers.

    Raises:
        HTTPException: If investigation not found or generation fails.
    """
    if not WEASYPRINT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="PDF export is not available. WeasyPrint system dependencies (cairo, pango) are not installed. PDF export works in Docker/Linux environments.",
        )

    try:
        pdf_buffer = await export_investigation_pdf(investigation_id)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f"attachment; filename=SOCsentinel_Report_{investigation_id}.pdf"
                ),
            },
        )
    except ValueError as e:
        logger.warning(
            "PDF export failed - investigation not found",
            investigation_id=investigation_id,
            error=str(e),
        )
        raise NotFoundError("Investigation", investigation_id) from e
    except Exception as e:
        logger.error(
            "PDF export failed",
            investigation_id=investigation_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}",
        ) from e


@router.get("/export/{investigation_id}/docx")
async def export_docx_endpoint(investigation_id: str) -> StreamingResponse:
    """Export investigation report as a Word document.

    Generates a DOCX report that can be edited and shared
    with management, legal, or compliance teams.

    Args:
        investigation_id: The unique investigation ID.

    Returns:
        StreamingResponse with DOCX content and download headers.

    Raises:
        HTTPException: If investigation not found or generation fails.
    """
    try:
        docx_buffer = await export_investigation_docx(investigation_id)

        return StreamingResponse(
            docx_buffer,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            headers={
                "Content-Disposition": (
                    f"attachment; filename=SOCsentinel_Report_{investigation_id}.docx"
                ),
            },
        )
    except ValueError as e:
        logger.warning(
            "DOCX export failed - investigation not found",
            investigation_id=investigation_id,
            error=str(e),
        )
        raise NotFoundError("Investigation", investigation_id) from e
    except Exception as e:
        logger.error(
            "DOCX export failed",
            investigation_id=investigation_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate DOCX: {str(e)}",
        ) from e


@router.get("/formats", response_model=APIResponse)
async def list_export_formats() -> APIResponse:
    """List available export formats.

    Returns information about supported export formats.
    """
    formats = [
        {
            "id": "docx",
            "name": "Microsoft Word",
            "description": "Editable Word document for sharing and editing",
            "mime_type": (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            "extension": "docx",
            "available": True,
        },
    ]

    if WEASYPRINT_AVAILABLE:
        formats.insert(0, {
            "id": "pdf",
            "name": "PDF Document",
            "description": "Professional formatted PDF report with branding",
            "mime_type": "application/pdf",
            "extension": "pdf",
            "available": True,
        })
    else:
        formats.insert(0, {
            "id": "pdf",
            "name": "PDF Document (Unavailable)",
            "description": "PDF export requires system dependencies (cairo, pango). Available in Docker/Linux.",
            "mime_type": "application/pdf",
            "extension": "pdf",
            "available": False,
        })

    return APIResponse(
        success=True,
        message="Available export formats",
        data={"formats": formats, "pdf_available": WEASYPRINT_AVAILABLE},
    )
