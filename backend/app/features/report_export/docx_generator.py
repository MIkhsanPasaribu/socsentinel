"""
SOCsentinel — DOCX Report Generator.

Generates professional Word documents using python-docx.
"""

from io import BytesIO
from typing import Any

from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE

from app.core.logger import get_logger

logger = get_logger(__name__)

# SOCsentinel brand colors
COLOR_DEEP_NAVY = RGBColor(0x0A, 0x16, 0x28)
COLOR_CYAN = RGBColor(0x00, 0xD4, 0xFF)
COLOR_CRITICAL = RGBColor(0xDC, 0x26, 0x26)
COLOR_HIGH = RGBColor(0xEA, 0x58, 0x0C)
COLOR_MEDIUM = RGBColor(0xD9, 0x77, 0x06)
COLOR_LOW = RGBColor(0x05, 0x96, 0x69)
COLOR_GRAY = RGBColor(0x6B, 0x72, 0x80)


def get_severity_color(severity: str) -> RGBColor:
    """Get RGB color for severity level."""
    severity_lower = severity.lower()
    if severity_lower == "critical":
        return COLOR_CRITICAL
    elif severity_lower == "high":
        return COLOR_HIGH
    elif severity_lower == "medium":
        return COLOR_MEDIUM
    elif severity_lower == "low":
        return COLOR_LOW
    return COLOR_GRAY


def add_heading_custom(doc: Document, text: str, level: int = 1) -> Any:
    """Add a styled heading to the document."""
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.color.rgb = COLOR_DEEP_NAVY
        if level == 1:
            run.font.size = Pt(18)
            run.font.bold = True
        elif level == 2:
            run.font.size = Pt(14)
            run.font.bold = True
        else:
            run.font.size = Pt(12)
            run.font.bold = True
    return heading


def add_info_table(doc: Document, items: list[tuple[str, str]]) -> None:
    """Add a two-column info table."""
    table = doc.add_table(rows=len(items), cols=2)
    table.style = "Table Grid"

    for i, (label, value) in enumerate(items):
        row = table.rows[i]
        row.cells[0].text = label
        row.cells[1].text = value

        # Style label cell
        label_cell = row.cells[0]
        label_cell.width = Inches(1.5)
        for paragraph in label_cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.size = Pt(10)
                run.font.color.rgb = COLOR_GRAY

        # Style value cell
        value_cell = row.cells[1]
        for paragraph in value_cell.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(10)


def generate_docx(context: dict[str, Any]) -> BytesIO:
    """Generate a DOCX report from the report context.

    Creates a professional Word document with all investigation details,
    formatted for SOC teams to edit and share.

    Args:
        context: The report context dictionary with all investigation data.

    Returns:
        BytesIO buffer containing the generated DOCX.
    """
    doc = Document()

    # Set default font
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

    # Set narrow margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)

    # === COVER PAGE ===
    # Add some space at top
    for _ in range(3):
        doc.add_paragraph()

    # Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("SOCsentinel")
    run.font.size = Pt(36)
    run.font.bold = True
    run.font.color.rgb = COLOR_DEEP_NAVY

    # Subtitle
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run("Security Investigation Report")
    run.font.size = Pt(24)
    run.font.bold = True
    run.font.color.rgb = COLOR_CYAN

    # Spacing
    for _ in range(2):
        doc.add_paragraph()

    # Severity badge
    severity_para = doc.add_paragraph()
    severity_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    severity_run = severity_para.add_run(
        context["alert"]["severity"].upper()
    )
    severity_run.font.size = Pt(16)
    severity_run.font.bold = True
    severity_run.font.color.rgb = get_severity_color(context["alert"]["severity"])

    # Spacing
    for _ in range(2):
        doc.add_paragraph()

    # Meta info
    meta_items = [
        ("Investigation ID:", context["investigation_id"]),
        ("Alert:", context["alert"]["rule_name"]),
        ("Generated:", context["generated_at_formatted"]),
        ("Processing Time:", f"{context['total_processing_time_ms']:.0f}ms"),
    ]

    for label, value in meta_items:
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        label_run = para.add_run(f"{label} ")
        label_run.font.size = Pt(11)
        label_run.font.color.rgb = COLOR_GRAY
        value_run = para.add_run(value)
        value_run.font.size = Pt(11)
        value_run.font.bold = True

    # Page break
    doc.add_page_break()

    # === EXECUTIVE SUMMARY ===
    add_heading_custom(doc, "Executive Summary", level=1)

    # Summary box
    summary_para = doc.add_paragraph()
    summary_run = summary_para.add_run(context["report"]["title"])
    summary_run.font.bold = True
    summary_run.font.size = Pt(12)

    doc.add_paragraph(context["report"]["executive_summary"])

    # Key metrics
    add_heading_custom(doc, "Key Metrics", level=2)

    metrics = [
        ("AI Confidence", f"{context['overall_confidence'] * 100:.0f}%"),
        ("Classification", context["triage"]["classification"].upper()),
        ("MITRE Techniques", str(len(context["mitre"]["techniques"]))),
        ("IOCs Found", str(len(context["evidence"]["iocs"]))),
    ]

    for label, value in metrics:
        para = doc.add_paragraph(style="List Bullet")
        para.add_run(f"{label}: ").bold = True
        para.add_run(value)

    # Recommendations
    if context["report"]["recommendations"]:
        add_heading_custom(doc, "Key Recommendations", level=2)
        for rec in context["report"]["recommendations"][:5]:
            para = doc.add_paragraph(style="List Bullet")
            para.add_run(rec)

    # === ALERT DETAILS ===
    doc.add_page_break()
    add_heading_custom(doc, "Alert Details", level=1)

    alert_info = [
        ("Alert ID", context["alert"]["alert_id"]),
        ("Rule Name", context["alert"]["rule_name"]),
        ("Source IP", context["alert"]["source_ip"] or "N/A"),
        ("Destination IP", context["alert"]["destination_ip"] or "N/A"),
        ("Username", context["alert"]["username"] or "N/A"),
        ("Hostname", context["alert"]["hostname"] or "N/A"),
        ("Protocol", context["alert"]["protocol"] or "N/A"),
        ("Timestamp", context["alert"]["timestamp"]),
    ]
    add_info_table(doc, alert_info)

    if context["alert"]["description"]:
        doc.add_paragraph()
        desc_para = doc.add_paragraph()
        desc_para.add_run("Description: ").bold = True
        doc.add_paragraph(context["alert"]["description"])

    # === TRIAGE ANALYSIS ===
    add_heading_custom(doc, "Triage Analysis (L1)", level=1)

    triage_info = [
        ("Classification", context["triage"]["classification"].upper()),
        ("Severity", context["triage"]["severity"].upper()),
        ("AI Confidence", f"{context['triage']['confidence'] * 100:.0f}%"),
        ("False Positive Probability", f"{context['triage']['false_positive_probability'] * 100:.0f}%"),
        ("False Positive", "Yes" if context["triage"]["is_false_positive"] else "No"),
    ]
    add_info_table(doc, triage_info)

    if context["triage"]["reasoning"]:
        doc.add_paragraph()
        reason_para = doc.add_paragraph()
        reason_para.add_run("Reasoning: ").bold = True
        doc.add_paragraph(context["triage"]["reasoning"])

    # Evidence chain
    if context["triage"]["evidence_chain"]:
        add_heading_custom(doc, "Evidence Chain", level=2)
        for step in context["triage"]["evidence_chain"]:
            para = doc.add_paragraph(style="List Bullet")
            para.add_run(f"{step['step']}: ").bold = True
            para.add_run(f"{step['observation']} → {step['conclusion']}")

    # === INDICATORS OF COMPROMISE ===
    if context["evidence"]["iocs"]:
        doc.add_page_break()
        add_heading_custom(doc, "Indicators of Compromise", level=1)

        # IOC table
        ioc_table = doc.add_table(rows=1, cols=4)
        ioc_table.style = "Table Grid"
        ioc_table.autofit = True

        # Header
        header_cells = ioc_table.rows[0].cells
        headers = ["Type", "Value", "Reputation", "Source"]
        for i, header in enumerate(headers):
            header_cells[i].text = header
            for paragraph in header_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.color.rgb = COLOR_DEEP_NAVY
                    run.font.size = Pt(10)

        # Data rows
        for ioc in context["evidence"]["iocs"]:
            row_cells = ioc_table.add_row().cells
            row_cells[0].text = ioc.get("type", "").upper()
            row_cells[1].text = ioc.get("value", "")
            row_cells[2].text = ioc.get("reputation", "unknown").upper()
            row_cells[3].text = ioc.get("source", "N/A")

            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)

        if context["evidence"]["enrichment_summary"]:
            doc.add_paragraph()
            enrich_para = doc.add_paragraph()
            enrich_para.add_run("Enrichment Summary: ").bold = True
            doc.add_paragraph(context["evidence"]["enrichment_summary"])

    # === MITRE ATT&CK MAPPING ===
    doc.add_page_break()
    add_heading_custom(doc, "MITRE ATT&CK Mapping", level=1)

    if context["mitre"]["kill_chain_phase"]:
        para = doc.add_paragraph()
        para.add_run("Kill Chain Phase: ").bold = True
        para.add_run(context["mitre"]["kill_chain_phase"].replace("_", " ").title())

    if context["mitre"]["techniques"]:
        add_heading_custom(doc, "Techniques", level=2)

        tech_table = doc.add_table(rows=1, cols=4)
        tech_table.style = "Table Grid"

        header_cells = tech_table.rows[0].cells
        headers = ["Technique ID", "Name", "Tactic", "Confidence"]
        for i, header in enumerate(headers):
            header_cells[i].text = header
            for paragraph in header_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.color.rgb = COLOR_DEEP_NAVY
                    run.font.size = Pt(10)

        for tech in context["mitre"]["techniques"]:
            row_cells = tech_table.add_row().cells
            row_cells[0].text = tech.get("technique_id", "")
            row_cells[1].text = tech.get("technique_name", "")
            row_cells[2].text = tech.get("tactic", "")
            row_cells[3].text = f"{tech.get('confidence', 0) * 100:.0f}%"

            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)

    if context["mitre"]["attack_timeline"]:
        add_heading_custom(doc, "Attack Timeline", level=2)

        timeline_table = doc.add_table(rows=1, cols=3)
        timeline_table.style = "Table Grid"

        header_cells = timeline_table.rows[0].cells
        headers = ["Timestamp", "Event", "Technique"]
        for i, header in enumerate(headers):
            header_cells[i].text = header
            for paragraph in header_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.color.rgb = COLOR_DEEP_NAVY
                    run.font.size = Pt(10)

        for event in context["mitre"]["attack_timeline"]:
            row_cells = timeline_table.add_row().cells
            row_cells[0].text = event.get("timestamp", "")
            row_cells[1].text = event.get("event", "")
            row_cells[2].text = event.get("technique", "")

            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)

    # === DETECTION ENGINEERING ===
    if context["detection"]["sigma_rule"]:
        doc.add_page_break()
        add_heading_custom(doc, "Detection Engineering", level=1)

        detection_info = [
            ("Confidence", f"{context['detection']['confidence'] * 100:.0f}%"),
            ("False Positive Risk", context["detection"]["false_positive_risk"].upper()),
        ]
        add_info_table(doc, detection_info)

        if context["detection"]["mitre_techniques_mapped"]:
            doc.add_paragraph()
            tech_para = doc.add_paragraph()
            tech_para.add_run("Mapped MITRE Techniques: ").bold = True
            tech_para.add_run(", ".join(context["detection"]["mitre_techniques_mapped"]))

        if context["detection"]["recommended_log_sources"]:
            doc.add_paragraph()
            log_para = doc.add_paragraph()
            log_para.add_run("Recommended Log Sources: ").bold = True
            log_para.add_run(", ".join(context["detection"]["recommended_log_sources"]))

        add_heading_custom(doc, "Sigma Rule", level=2)
        sigma_para = doc.add_paragraph()
        sigma_run = sigma_para.add_run(context["detection"]["sigma_rule"])
        sigma_run.font.name = "Courier New"
        sigma_run.font.size = Pt(9)

        if context["detection"]["detection_logic"]:
            add_heading_custom(doc, "Detection Logic", level=2)
            doc.add_paragraph(context["detection"]["detection_logic"])

    # === RESPONSE PLAYBOOK ===
    doc.add_page_break()
    add_heading_custom(doc, "Response Playbook", level=1)

    if context["response"]["playbook_name"]:
        response_info = [
            ("Playbook", context["response"]["playbook_name"]),
            ("Priority", context["response"]["priority"].upper()),
            ("Estimated Time", context["response"]["estimated_containment_time"] or "N/A"),
            ("Status", context["response"]["containment_status"].replace("_", " ").title()),
        ]
        add_info_table(doc, response_info)

    if context["response"]["steps"]:
        add_heading_custom(doc, "Containment Steps", level=2)

        for step in context["response"]["steps"]:
            para = doc.add_paragraph()
            para.add_run(f"{step.get('order', 0)}. ").bold = True
            para.add_run(step.get("action", "")).bold = True

            details = []
            if step.get("tool"):
                details.append(f"Tool: {step['tool']}")
            if step.get("risk_level"):
                details.append(f"Risk: {step['risk_level'].upper()}")
            if step.get("automated"):
                details.append("Automated")

            if details:
                detail_para = doc.add_paragraph()
                detail_para.add_run(", ".join(details))
                detail_para.paragraph_format.left_indent = Inches(0.25)

            if step.get("details"):
                details_para = doc.add_paragraph(step["details"])
                details_para.paragraph_format.left_indent = Inches(0.25)
                details_para.paragraph_format.space_after = Pt(8)

    if context["response"]["post_incident"]:
        add_heading_custom(doc, "Post-Incident Actions", level=2)
        for action in context["response"]["post_incident"]:
            para = doc.add_paragraph(style="List Bullet")
            para.add_run(action)

    # === VALIDATOR AUDIT ===
    if context["validator"]:
        doc.add_page_break()
        add_heading_custom(doc, "Adversarial Audit", level=1)

        validator_info = [
            ("Validation Status", "APPROVED" if context["validator"]["is_approved"] else "REJECTED"),
            ("Risk Score", f"{context['validator']['risk_score'] * 100:.0f}%"),
        ]
        add_info_table(doc, validator_info)

        if context["validator"]["critic_comments"]:
            doc.add_paragraph()
            comment_para = doc.add_paragraph()
            comment_para.add_run("Critic Comments: ").bold = True
            doc.add_paragraph(context["validator"]["critic_comments"])

        if context["validator"]["safe_alternatives"]:
            add_heading_custom(doc, "Safer Alternatives", level=2)
            for alt in context["validator"]["safe_alternatives"]:
                para = doc.add_paragraph(style="List Bullet")
                para.add_run(alt)

        if context["validator"]["sigma_rule"]:
            add_heading_custom(doc, "Validator-Generated Sigma Rule", level=2)
            sigma_para = doc.add_paragraph()
            sigma_run = sigma_para.add_run(context["validator"]["sigma_rule"])
            sigma_run.font.name = "Courier New"
            sigma_run.font.size = Pt(9)

    # === AUDIT TRAIL ===
    if context["audit_trail"]:
        doc.add_page_break()
        add_heading_custom(doc, "Audit Trail", level=1)

        audit_table = doc.add_table(rows=1, cols=5)
        audit_table.style = "Table Grid"

        header_cells = audit_table.rows[0].cells
        headers = ["Time", "Agent", "Step", "Status", "Time (ms)"]
        for i, header in enumerate(headers):
            header_cells[i].text = header
            for paragraph in header_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.color.rgb = COLOR_DEEP_NAVY
                    run.font.size = Pt(10)

        for entry in context["audit_trail"]:
            row_cells = audit_table.add_row().cells
            # Extract time from timestamp
            ts = entry.get("timestamp", "")
            if "T" in ts:
                ts = ts.split("T")[1].split(".")[0]
            row_cells[0].text = ts
            row_cells[1].text = entry.get("agent", "")
            row_cells[2].text = entry.get("step", "")
            row_cells[3].text = entry.get("status", "").upper()
            row_cells[4].text = str(entry.get("processing_time_ms", 0))

            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)

    # === FOOTER ===
    doc.add_paragraph()
    footer_para = doc.add_paragraph()
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer_para.add_run(
        f"This report was generated automatically by SOCsentinel's Multi-Agent AI System.\n"
        f"Powered by Qwen3 on AMD MI300X (ROCm) | MITRE ATT&CK v16 | Investigation ID: {context['investigation_id']}"
    )
    footer_run.font.size = Pt(9)
    footer_run.font.color.rgb = COLOR_GRAY
    footer_run.italic = True

    # Save to buffer
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    logger.debug(
        "DOCX generated successfully",
        investigation_id=context.get("investigation_id"),
        size_bytes=buffer.getbuffer().nbytes,
    )

    return buffer
