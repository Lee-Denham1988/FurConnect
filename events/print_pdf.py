from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter, landscape, A3
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Convention, Room

def printable_schedule_pdf(request, pk):
    convention = get_object_or_404(Convention, pk=pk)
    days = convention.days.all().order_by('date')
    from io import BytesIO
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    import base64
    from reportlab.platypus import Image as RLImage
    from io import BytesIO
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.textColor = colors.HexColor('#4b2991')
    elements.append(Paragraph(f"<b>{convention.name}</b>", title_style))
    # Add banner image if present and valid
    if convention.banner_image and convention.banner_image.startswith('data:image'):
        try:
            header, b64data = convention.banner_image.split(',', 1)
            img_bytes = base64.b64decode(b64data)
            img_stream = BytesIO(img_bytes)
            banner = RLImage(img_stream, width=480, height=90)  # Adjust size as needed
            elements.append(banner)
            elements.append(Spacer(1, 12))
        except Exception:
            pass
    elements.append(Spacer(1, 18))

    card_width = 560
    from reportlab.lib.enums import TA_CENTER
    for day in days:
        day_style = styles['Heading2'].clone('CenteredHeading2')
        day_style.textColor = colors.HexColor('#222')
        day_style.alignment = TA_CENTER
        elements.append(Paragraph(day.date.strftime('%A, %B %d, %Y'), day_style))
        panels = list(day.panels.all().order_by('start_time'))
        if not panels:
            elements.append(Paragraph("<i>No panels scheduled.</i>", styles['Normal']))
            elements.append(Spacer(1, 12))
            continue
        for panel in panels:
            hosts = ', '.join([h.name for h in panel.host.all().order_by('panelhostorder__priority')])
            tags = ', '.join([t.name for t in panel.tags.all().order_by('paneltag__priority')])
            start_12 = panel.start_time.strftime('%I:%M %p').lstrip('0')
            end_12 = panel.end_time.strftime('%I:%M %p').lstrip('0')
            card_data = [
                [Paragraph(f"<b><font color='#4b2991' size=13>{panel.title}</font></b>", styles['Normal'])],
                [Paragraph(f"<b>Time:</b> {start_12} - {end_12}", styles['Normal'])],
                [Paragraph(f"<b>Room:</b> {panel.room.name if panel.room else 'N/A'}", styles['Normal'])],
                [Paragraph(f"<b>Host(s):</b> {hosts if hosts else 'N/A'}", styles['Normal'])],
                [Paragraph(f"<b>Tag(s):</b> {tags if tags else 'N/A'}", styles['Normal'])],
            ]
            if panel.description:
                card_data.append([Paragraph(panel.description, styles['Normal'])])
            card = Table(card_data, colWidths=[card_width])
            card.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor('#4b2991')),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ede7f6')),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 11),
            ]))
            elements.append(card)
            elements.append(Spacer(1, 16))

    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#4b2991'))
        canvas.drawRightString(doc.pagesize[0] - 36, 20, text)

from reportlab.lib.pagesizes import A3, landscape

def full_schedule_pdf_a3(request, pk):
    convention = get_object_or_404(Convention, pk=pk)
    if not convention.enable_schedule_pdf_export:
        raise Http404("PDF export not enabled for this convention")
    
    days = convention.days.all().order_by('date')
    from io import BytesIO
    buffer = BytesIO()
    # Use A3 landscape for larger display
    page_size = landscape(A3)
    doc = SimpleDocTemplate(buffer, pagesize=page_size, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    import base64
    from reportlab.platypus import Image as RLImage
    from io import BytesIO
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.textColor = colors.HexColor('#4b2991')
    title_style.fontSize = 24  # Larger for A3
    elements.append(Paragraph(f"<b>{convention.name} - Full Schedule</b>", title_style))
    # Add banner image if present and valid
    if convention.banner_image and convention.banner_image.startswith('data:image'):
        try:
            header, b64data = convention.banner_image.split(',', 1)
            img_bytes = base64.b64decode(b64data)
            img_stream = BytesIO(img_bytes)
            banner = RLImage(img_stream, width=720, height=135)  # Larger for A3
            elements.append(banner)
            elements.append(Spacer(1, 18))
        except Exception:
            pass
    elements.append(Spacer(1, 24))

    card_width = 800  # Wider for A3 landscape
    from reportlab.lib.enums import TA_CENTER
    for day in days:
        day_style = styles['Heading2'].clone('CenteredHeading2')
        day_style.textColor = colors.HexColor('#222')
        day_style.alignment = TA_CENTER
        day_style.fontSize = 18
        elements.append(Paragraph(day.date.strftime('%A, %B %d, %Y'), day_style))
        panels = list(day.panels.all().order_by('start_time'))
        if not panels:
            elements.append(Paragraph("<i>No panels scheduled.</i>", styles['Normal']))
            elements.append(Spacer(1, 18))
            continue
        for panel in panels:
            hosts = ', '.join([h.name for h in panel.host.all().order_by('panelhostorder__priority')])
            tags = ', '.join([t.name for t in panel.tags.all().order_by('paneltag__priority')])
            start_12 = panel.start_time.strftime('%I:%M %p').lstrip('0')
            end_12 = panel.end_time.strftime('%I:%M %p').lstrip('0')
            card_data = [
                [Paragraph(f"<b><font color='#4b2991' size=16>{panel.title}</font></b>", styles['Normal'])],
                [Paragraph(f"<b>Time:</b> {start_12} - {end_12}", styles['Normal'])],
                [Paragraph(f"<b>Room:</b> {panel.room.name if panel.room else 'N/A'}", styles['Normal'])],
                [Paragraph(f"<b>Host(s):</b> {hosts if hosts else 'N/A'}", styles['Normal'])],
                [Paragraph(f"<b>Tag(s):</b> {tags if tags else 'N/A'}", styles['Normal'])],
            ]
            if panel.description:
                card_data.append([Paragraph(panel.description, styles['Normal'])])
            card = Table(card_data, colWidths=[card_width])
            card.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#4b2991')),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ede7f6')),
                ('LEFTPADDING', (0,0), (-1,-1), 15),
                ('RIGHTPADDING', (0,0), (-1,-1), 15),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 12),
            ]))
            elements.append(card)
            elements.append(Spacer(1, 20))

    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.HexColor('#4b2991'))
        canvas.drawRightString(doc.pagesize[0] - 50, 25, text)

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{convention.name}_full_schedule_A3.pdf"'
    return response
