import io
from typing import Dict

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_pdf(report: Dict):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, 760, "Multi-Agent Loan Decision Report")

    pdf.setFont("Helvetica", 11)
    lines = [
        f"Applicant: {report['name']}",
        f"Decision: {report['decision']}",
        f"Risk score: {report['risk_score']} ({report['risk_band']})",
        f"Interest rate: {report['interest_rate']}%",
        f"Estimated EMI: INR {report['emi']}",
        f"KYC status: {report['kyc_status']}",
        "",
        "Explanation:",
    ]

    y = 730
    for line in lines:
        pdf.drawString(40, y, line)
        y -= 20

    text = pdf.beginText(40, y)
    text.setFont("Helvetica", 10)
    for line in report["explanation"].splitlines():
        text.textLine(line[:110])
    pdf.drawText(text)

    pdf.save()
    buffer.seek(0)
    return buffer
