"""
SOCsentinel — PDF Report Generator.

Generates professional PDF reports using WeasyPrint.
"""

import os
from io import BytesIO
from typing import Any

from jinja2 import Environment, FileSystemLoader

from app.core.logger import get_logger

logger = get_logger(__name__)

# Template directory path
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

# Try to import WeasyPrint - may fail on Windows without GTK
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    logger.warning(
        "WeasyPrint not available - PDF generation will be disabled. "
        "Install system dependencies (cairo, pango) to enable PDF export.",
        error=str(e),
    )


def generate_pdf(context: dict[str, Any]) -> BytesIO:
    """Generate a PDF report from the report context.

    Uses Jinja2 templates and WeasyPrint to create a professionally
    formatted PDF document.

    Args:
        context: The report context dictionary with all investigation data.

    Returns:
        BytesIO buffer containing the generated PDF.

    Raises:
        RuntimeError: If WeasyPrint is not available (system deps missing).
    """
    if not WEASYPRINT_AVAILABLE:
        raise RuntimeError(
            "PDF generation is not available. "
            "WeasyPrint system dependencies (cairo, pango) are not installed. "
            "PDF export works in Docker/Linux environments."
        )

    # Load templates
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("report.html")

    # Read CSS content
    css_path = os.path.join(TEMPLATE_DIR, "report.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    # Add CSS to context
    context["css_content"] = css_content

    # Render HTML
    html_string = template.render(**context)

    # Generate PDF
    html = HTML(string=html_string, base_url=TEMPLATE_DIR)
    pdf_bytes = html.write_pdf(
        stylesheets=[CSS(string=css_content)],
        presentational_hints=True,
    )

    # Return as BytesIO
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)

    logger.debug(
        "PDF generated successfully",
        investigation_id=context.get("investigation_id"),
        size_bytes=len(pdf_bytes),
    )

    return buffer
