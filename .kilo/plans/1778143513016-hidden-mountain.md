# SOCsentinel — Phase 3: Report Export & Advanced Upgrades Plan

## STATUS: READY FOR IMPLEMENTATION

---

## Strategic Context

### Current State (Phase 1 + Phase 2 Complete)
- 9 agents: Orchestrator, L1 Triage, Evidence, MITRE Mapper, Detection, Report Writer, Response Planner, Validator, Threat Generator
- SSE real-time streaming pipeline
- MITRE ATT&CK RAG with ChromaDB + BGE-M3
- Human-in-the-Loop decision panel with self-improving feedback loop
- GPU Performance panel (AMD MI300X metrics)
- Pipeline Flow Visualization
- Threat Hunting UI page
- Sigma rule export (YAML download + copy)
- SOAR export (Splunk, XSOAR, Sentinel)
- 9 attack scenarios (brute_force, lateral_movement, data_exfiltration, phishing, ransomware, privilege_escalation, supply_chain, insider_threat, cryptomining)

### What's Missing — Key Gaps for Hackathon Win

| Gap | Why It Matters | Judging Criteria |
|-----|---------------|------------------|
| No professional document export (PDF/DOCX) | Judges can't take away a tangible deliverable | Business Value + Presentation |
| Reports only viewable in-app | Real SOC teams need to share reports with management/legal | Business Value |
| No executive-ready formatting | Raw JSON data isn't impressive to non-technical judges | Presentation |
| No investigation comparison/analytics | Can't show improvement over time | Originality |
| main.py description says "5 agents" | Inconsistency undermines credibility | Presentation |

---

## FEATURE: Professional Investigation Report Export (PDF + DOCX)

### Concept

Add a backend endpoint that generates beautifully formatted investigation reports as PDF and DOCX documents. The frontend gets "Export PDF" and "Export DOCX" buttons on each completed investigation in the Reports view.

**Why this wins:**
1. **Business Value (25%)** — Real SOC teams share reports with CISOs, legal, compliance. A downloadable PDF is immediately operationally useful.
2. **Presentation (25%)** — A beautiful, branded PDF with the SOCsentinel logo, MITRE ATT&CK mapping table, Sigma rule code block, and timeline is visually stunning in a 3-minute demo.
3. **Technical Execution** — Shows full-stack capability: backend PDF generation → API endpoint → frontend download.

---

## Architecture Decision

### PDF Generation: WeasyPrint (HTML → PDF)
**Rationale:**
- Uses HTML/CSS templates — leverages existing web skills
- Supports modern CSS3 (flexbox, grid, custom fonts, colors)
- Produces beautiful, print-quality PDFs
- No external binary dependencies (unlike wkhtmltopdf/PDFKit)
- Well-maintained, MIT licensed
- Perfect for styled reports with tables, code blocks, colored sections

### DOCX Generation: python-docx
**Rationale:**
- Industry standard for Word document generation
- Supports tables, headers, footers, styles, images
- No external dependencies
- Lightweight and fast
- Allows SOC teams to edit reports before sharing

### Template Engine: Jinja2
**Rationale:**
- Already a dependency of FastAPI (via Starlette)
- Powerful template inheritance and macros
- Same template can serve both HTML (for PDF) and data context (for DOCX)

---

## Implementation Plan

### Files to CREATE

| File | Purpose |
|------|---------|
| `backend/app/features/report_export/__init__.py` | Feature module init |
| `backend/app/features/report_export/router.py` | API endpoints for PDF/DOCX export |
| `backend/app/features/report_export/service.py` | Export orchestration logic |
| `backend/app/features/report_export/pdf_generator.py` | HTML→PDF generation with WeasyPrint |
| `backend/app/features/report_export/docx_generator.py` | DOCX generation with python-docx |
| `backend/app/features/report_export/schemas.py` | Request/response Pydantic models |
| `backend/app/features/report_export/templates/report.html` | Jinja2 HTML template for PDF |
| `backend/app/features/report_export/templates/report.css` | CSS styling for PDF |
| `frontend/src/features/reports/components/ExportButtons.tsx` | Export button component |

### Files to MODIFY

| File | Change |
|------|--------|
| `backend/requirements.txt` | Add `weasyprint>=62.0`, `python-docx>=1.1.0` |
| `backend/app/main.py` | Register report_export router, fix "5 agents" → "9 agents" description |
| `frontend/src/features/reports/components/ReportsView.tsx` | Add ExportButtons to each ReportCard |
| `Dockerfile` | Add system deps for WeasyPrint (libcairo2, libpango, etc.) |

---

## Detailed Design

### 1. Backend API Endpoints

```python
# backend/app/features/report_export/router.py

@router.get("/export/{investigation_id}/pdf")
async def export_pdf(investigation_id: str) -> StreamingResponse:
    """Export investigation report as a professionally formatted PDF."""

@router.get("/export/{investigation_id}/docx")
async def export_docx(investigation_id: str) -> StreamingResponse:
    """Export investigation report as a Word document."""
```

Both endpoints:
- Fetch the full `PipelineState` from `_pipeline_store`
- Transform data into a structured report context
- Generate the document in-memory (BytesIO)
- Return as `StreamingResponse` with appropriate Content-Type and Content-Disposition headers

### 2. PDF Template Design (HTML/CSS)

The PDF will be a professional cybersecurity investigation report with:

**Page 1 — Cover Page:**
- SOCsentinel logo/branding
- "SECURITY INVESTIGATION REPORT" title
- Investigation ID, date, severity badge
- Classification: CONFIDENTIAL

**Page 2 — Executive Summary:**
- Alert overview (rule name, severity, source/dest IPs)
- AI confidence score gauge
- Key findings summary (2-3 sentences)
- Recommended actions (bullet list)

**Page 3 — Triage & Evidence:**
- Triage classification table (classification, severity, confidence, FP probability)
- IOC table (type, value, reputation, source)
- Evidence chain (numbered steps)

**Page 4 — MITRE ATT&CK Mapping:**
- Techniques table (ID, name, tactic, confidence)
- Kill chain phase indicator
- Attack timeline

**Page 5 — Detection Engineering:**
- Sigma rule in styled code block (monospace, syntax-highlighted)
- Detection metadata (techniques mapped, FP risk, log sources)
- Detection logic explanation

**Page 6 — Response & Validation:**
- Containment playbook steps table
- Validator approval status (green/red badge)
- Risk score
- Safe alternatives (if any)

**Footer:** Page numbers, "Generated by SOCsentinel — AMD MI300X Powered"

**Color Scheme (matching app theme):**
- Header backgrounds: `#0A1628` (Deep Navy)
- Accent: `#00D4FF` (Cyan Electric)
- Critical: `#EF4444`
- High: `#FF6B35`
- Tables: alternating `#F0F4F8` / white rows
- Code blocks: `#1E293B` background with `#FDE68A` text

### 3. DOCX Structure

Professional Word document with:
- Title page with investigation metadata
- Table of Contents (auto-generated)
- Sections matching the PDF structure
- Tables for IOCs, MITRE techniques, playbook steps
- Monospace font for Sigma rules
- Headers/footers with page numbers and "CONFIDENTIAL"
- Consistent heading styles (Heading 1, 2, 3)

### 4. Frontend Export Buttons

```tsx
// Placed in the ReportCard header, next to the expand/collapse button
<ExportButtons investigationId={investigation.investigation_id} />
```

Design:
- Two small buttons: "PDF" (red/orange icon) and "DOCX" (blue icon)
- Loading state while generating
- Downloads file directly via browser
- Uses `window.open()` or `<a download>` pattern

### 5. Report Context Builder

```python
def build_report_context(state: PipelineState) -> dict:
    """Transform PipelineState into a structured report context.
    
    Normalizes all agent outputs into a consistent format
    suitable for template rendering.
    """
    return {
        "investigation_id": state.investigation_id,
        "generated_at": datetime.utcnow().isoformat(),
        "alert": { ... },
        "triage": { ... },
        "evidence": { ... },
        "mitre": { ... },
        "detection": { ... },
        "report": { ... },
        "response": { ... },
        "validator": { ... },
        "audit_trail": [ ... ],
        "total_processing_time_ms": state.total_processing_time_ms,
    }
```

---

## Additional Quick Wins (While Implementing Export)

### Fix 1: main.py Description Inconsistency
**File:** `backend/app/main.py:67-69`
**Change:** Update description from "5 specialized AI agents" to "9 specialized AI agents"

### Fix 2: Add Report Export to SOAR Integration
**File:** `backend/app/features/soar_integration/service.py`
**Change:** Add a `pdf` export format option that generates a PDF alongside the SOAR payload — shows judges that reports can be attached to SOAR tickets.

---

## Dependencies to Add

### Backend (requirements.txt)
```
# === Document Export ===
weasyprint>=62.0
python-docx>=1.1.0
```

Note: `jinja2` is already available via FastAPI/Starlette dependency chain.

### Frontend
No new dependencies needed — uses existing `apiClient` (axios) for download.

---

## Implementation Order

| # | Task | Effort | Files |
|---|------|--------|-------|
| 1 | Create `report_export` feature folder + schemas | 10 min | 3 files |
| 2 | Build report context builder (service.py) | 15 min | 1 file |
| 3 | Create HTML/CSS template for PDF | 45 min | 2 files |
| 4 | Implement PDF generator (WeasyPrint) | 20 min | 1 file |
| 5 | Implement DOCX generator (python-docx) | 30 min | 1 file |
| 6 | Create API router with endpoints | 15 min | 1 file |
| 7 | Register router in main.py + fix description | 5 min | 1 file |
| 8 | Add ExportButtons component to frontend | 20 min | 1 file |
| 9 | Integrate ExportButtons into ReportsView | 10 min | 1 file |
| 10 | Update requirements.txt | 2 min | 1 file |

**Total estimated time: ~3 hours**

---

## PDF Template CSS Design (Key Styles)

```css
/* SOCsentinel Report — Professional Dark Theme */
@page {
    size: A4;
    margin: 2cm;
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9px;
        color: #6B7280;
    }
    @bottom-right {
        content: "Generated by SOCsentinel";
        font-size: 9px;
        color: #6B7280;
    }
}

body {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: #1F2937;
    line-height: 1.6;
}

.cover-page {
    page-break-after: always;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #0A1628 0%, #1E3A5F 100%);
    color: white;
}

.severity-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
}
.severity-critical { background: #FEE2E2; color: #DC2626; }
.severity-high { background: #FED7AA; color: #EA580C; }
.severity-medium { background: #FEF3C7; color: #D97706; }
.severity-low { background: #D1FAE5; color: #059669; }

.code-block {
    background: #1E293B;
    color: #FDE68A;
    padding: 16px;
    border-radius: 8px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 10px;
    white-space: pre-wrap;
    border-left: 4px solid #EAB308;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
}
th {
    background: #0A1628;
    color: white;
    padding: 8px 12px;
    text-align: left;
    font-size: 11px;
}
td {
    padding: 8px 12px;
    border-bottom: 1px solid #E5E7EB;
    font-size: 11px;
}
tr:nth-child(even) td {
    background: #F9FAFB;
}

.section-header {
    color: #0A1628;
    border-bottom: 2px solid #00D4FF;
    padding-bottom: 8px;
    margin-top: 24px;
}

.metric-card {
    display: inline-block;
    background: #F0F4F8;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 4px;
    text-align: center;
}
.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: #0A1628;
}
.metric-label {
    font-size: 10px;
    color: #6B7280;
    text-transform: uppercase;
}
```

---

## DOCX Generator Design

```python
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

def generate_docx(context: dict) -> BytesIO:
    """Generate a professional DOCX investigation report."""
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    # Title Page
    doc.add_heading('SECURITY INVESTIGATION REPORT', level=0)
    doc.add_paragraph(f'Investigation ID: {context["investigation_id"]}')
    doc.add_paragraph(f'Date: {context["generated_at"]}')
    doc.add_paragraph(f'Severity: {context["alert"]["severity"].upper()}')
    doc.add_paragraph(f'Classification: CONFIDENTIAL')
    doc.add_page_break()
    
    # Executive Summary
    doc.add_heading('Executive Summary', level=1)
    doc.add_paragraph(context["report"]["executive_summary"])
    
    # ... (full implementation with tables, IOCs, MITRE, Sigma, etc.)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
```

---

## Frontend ExportButtons Component

```tsx
function ExportButtons({ investigationId }: { investigationId: string }) {
  const [loadingPdf, setLoadingPdf] = useState(false);
  const [loadingDocx, setLoadingDocx] = useState(false);

  const handleExport = async (format: "pdf" | "docx") => {
    const setLoading = format === "pdf" ? setLoadingPdf : setLoadingDocx;
    setLoading(true);
    try {
      const res = await apiClient.get(
        `/report-export/export/${investigationId}/${format}`,
        { responseType: "blob" }
      );
      const url = URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = `SOCsentinel_Report_${investigationId}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(`Export ${format} failed:`, err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center gap-1.5">
      <button onClick={() => handleExport("pdf")} disabled={loadingPdf} ...>
        {loadingPdf ? <Loader2 .../> : <FileDown .../>} PDF
      </button>
      <button onClick={() => handleExport("docx")} disabled={loadingDocx} ...>
        {loadingDocx ? <Loader2 .../> : <FileText .../>} DOCX
      </button>
    </div>
  );
}
```

---

## Dockerfile Impact

The current Dockerfile uses `python:3.11-slim` with minimal system deps. WeasyPrint requires cairo/pango system libraries. We need to add them:

```dockerfile
# System deps (add to existing RUN)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*
```

This adds ~30MB to the Docker image but enables professional PDF generation. The tradeoff is worth it for the hackathon demo impact.

**Alternative (if Docker size is critical):** Use `fpdf2` (pure Python, no system deps) but with significantly less CSS control. Given this is a hackathon where visual impact matters, WeasyPrint is the better choice.

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| WeasyPrint requires system-level dependencies (cairo, pango) | Add to Dockerfile apt-get; ~30MB increase |
| Large PDF generation could be slow | Generate in-memory with BytesIO; reports are small (~6 pages) |
| DOCX tables may not render perfectly | Use simple table styles; test with Word and LibreOffice |
| Frontend download may fail on large files | Reports are <1MB; use blob download pattern |
| HF Spaces may have memory constraints | PDF generation is lightweight; single report ~2MB RAM |

---

## Demo Script Addition (for 3-min video)

**At 2:20-2:40 mark:**
> "And here's the killer feature for real SOC operations — one click to export a professional PDF report that you can share with your CISO, attach to a JIRA ticket, or submit to compliance. The report includes the full investigation timeline, MITRE ATT&CK mapping, the generated Sigma rule, and the containment playbook — all beautifully formatted and ready to print."

*[Click "Export PDF" → show the generated PDF with cover page, tables, code blocks]*

---

## Judging Criteria Impact

| Criteria | How This Helps | Score Boost |
|----------|---------------|-------------|
| Application of Technology (25%) | Full-stack: LLM → structured data → document generation pipeline | +5% |
| Originality (25%) | No other hackathon SOC tool generates professional PDF reports from AI investigation | +8% |
| Business Value (25%) | Directly addresses real SOC workflow: investigate → report → share with management | +10% |
| Presentation (25%) | Beautiful PDF in demo is visually stunning and memorable | +7% |

---

## Duplicate Code Check

After reviewing the codebase:
- `downloadAsFile()` in `ReportsView.tsx` — will be reused for the export pattern (no duplication)
- `soar_integration/service.py` already has export logic — the report_export feature is distinct (document generation vs SOAR platform format)
- No duplicate files found in the project structure

---

## Validation Checklist

- [ ] PDF generates correctly with all sections
- [ ] DOCX opens in Microsoft Word and LibreOffice
- [ ] Export buttons show loading state
- [ ] 404 returned for non-existent investigation IDs
- [ ] Content-Disposition header sets correct filename
- [ ] No broken imports after adding new feature
- [ ] Frontend TypeScript compiles without errors
- [ ] Backend Python syntax valid
- [ ] No hardcoded secrets or credentials
- [ ] All functions have docstrings

---

## Implementation Summary

**Total new files:** 9
**Total modified files:** 4
**New dependencies:** `weasyprint>=62.0`, `python-docx>=1.1.0`
**Docker changes:** Add cairo/pango system libraries
**Estimated time:** ~3 hours
**Impact on existing code:** Minimal — only adds a new feature module and 2 buttons to existing UI

**Key Decision:** WeasyPrint for PDF (confirmed by user) — enables beautiful CSS-styled reports that will visually impress hackathon judges.

**No breaking changes:** The export feature is entirely additive. It reads from the existing `_pipeline_store` (same as stats, decision, and SOAR endpoints) and adds new API routes. The frontend change is a small component addition to the existing ReportsView.
