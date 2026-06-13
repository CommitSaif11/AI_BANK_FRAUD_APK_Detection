import hashlib
import functools

# Some OpenSSL builds reject the `usedforsecurity` kwarg on hashlib.md5,
# which reportlab's PDF writer passes unconditionally.
_original_md5 = hashlib.md5
_patched_md5 = functools.wraps(_original_md5)(
    lambda *args, **kwargs: _original_md5(*args, **{k: v for k, v in kwargs.items() if k != "usedforsecurity"})
)
hashlib.md5 = _patched_md5

from reportlab.lib import colors
import reportlab.pdfbase.pdfdoc as _pdfdoc

_pdfdoc.md5 = _patched_md5
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

RISK_COLORS = {
    "CRITICAL": colors.HexColor("#D32F2F"),
    "HIGH": colors.HexColor("#F57C00"),
    "MEDIUM": colors.HexColor("#FBC02D"),
    "LOW": colors.HexColor("#388E3C"),
    "CLEAN": colors.HexColor("#388E3C"),
}


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawString(0.75 * inch, 0.5 * inch, "CONFIDENTIAL — Bank Fraud Prevention Unit")
    canvas.drawRightString(letter[0] - 0.75 * inch, 0.5 * inch, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def generate_pdf_report(full_pipeline_result: dict, output_path: str) -> str:
    report = full_pipeline_result.get("report", {})
    risk_level = full_pipeline_result.get("risk_level", "UNKNOWN")
    final_risk_score = full_pipeline_result.get("final_risk_score", "N/A")

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = styles["BodyText"]

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    elements = []

    elements.append(Paragraph("APK THREAT INVESTIGATION REPORT", title_style))
    elements.append(Paragraph(report.get("report_title", ""), styles["Heading3"]))
    elements.append(Spacer(1, 12))

    banner_color = RISK_COLORS.get(risk_level, colors.grey)
    banner_table = Table(
        [[f"RISK LEVEL: {risk_level}"]],
        colWidths=[6.5 * inch],
    )
    banner_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), banner_color),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(banner_table)
    elements.append(Spacer(1, 16))

    def add_section(title, text):
        elements.append(Paragraph(title, heading_style))
        elements.append(Paragraph(text or "N/A", body_style))

    def add_list_section(title, items, numbered=False):
        elements.append(Paragraph(title, heading_style))
        if not items:
            elements.append(Paragraph("N/A", body_style))
            return
        for i, item in enumerate(items, start=1):
            prefix = f"{i}. " if numbered else "• "
            elements.append(Paragraph(f"{prefix}{item}", body_style))

    add_section("Executive Summary", report.get("executive_summary"))

    elements.append(Paragraph("Risk Score", heading_style))
    score_style = ParagraphStyle(
        "RiskScore",
        parent=styles["Normal"],
        fontSize=36,
        fontName="Helvetica-Bold",
        textColor=banner_color,
    )
    elements.append(Paragraph(f"{final_risk_score} / 100", score_style))
    elements.append(Paragraph(f"Risk Level: {risk_level}", body_style))

    add_section("Threat Overview", report.get("threat_overview"))
    add_section("Technical Findings", report.get("technical_findings"))
    add_section("Risk Assessment", report.get("risk_assessment_narrative"))
    add_section("Impact Assessment", report.get("impact_assessment"))
    add_list_section("Indicators of Compromise", report.get("indicators_of_compromise"))
    add_list_section("Recommended Actions", report.get("recommended_actions_detailed"), numbered=True)
    add_section("Customer Communication Draft", report.get("customer_communication"))
    add_section("Analyst Notes", report.get("analyst_notes"))

    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)

    return output_path
