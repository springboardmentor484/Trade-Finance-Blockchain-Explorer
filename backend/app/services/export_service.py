import csv
import io
from typing import List, Any
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib import pagesizes


def generate_csv(data: List[Any], columns: List[str]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(columns)

    for item in data:
        writer.writerow([getattr(item, col) for col in columns])

    return output.getvalue().encode("utf-8")


def generate_pdf(data: List[Any], columns: List[str]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=pagesizes.A4)

    table_data = [columns]

    for item in data:
        table_data.append([str(getattr(item, col)) for col in columns])

    table = Table(table_data)

    table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    elements = [table]
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf
