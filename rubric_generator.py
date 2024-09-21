from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO

def generate_toastmaster_rubric_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Heading1'], fontSize=14, alignment=1)
    subtitle_style = ParagraphStyle(name='Subtitle', parent=styles['Heading2'], fontSize=12, spaceBefore=6, spaceAfter=6)
    normal_style = ParagraphStyle(name='Normal', parent=styles['Normal'], fontSize=10, spaceBefore=3, spaceAfter=3)

    elements.append(Paragraph("Grade Sheet – Toastmaster", title_style))
    elements.append(Spacer(1, 0.25*inch))

    # Name and Date
    name_date = Table([
        [f"Name: {data.get('student_name', '_________________')}", f"Date: {data.get('date', '_________________')}"]
    ], colWidths=[3*inch, 3*inch])
    name_date.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'), ('FONTNAME', (0,0), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,0), (-1,-1), 10)]))
    elements.append(name_date)
    elements.append(Spacer(1, 0.1*inch))

    # Moderation of the Speaking Session
    elements.append(Paragraph("a. Moderation of the Speaking Session:", subtitle_style))

    moderation_data = [
        ["First/Last Impression", "0 1 2 3 4 5 6 7 8 9 10", data.get('first_last_impression', '')],
        ["Self-introduction, wrap-up", "", ""],
        ["Transitions between Speakers", "0 1 2 3 4 5 6 7 8 9 10", data.get('transitions', '')],
        ["Speaker/topic introductions", "", ""],
        ["Timing and Follow-up Questions", "0 1 2 3 4 5 6 7 8 9 10", data.get('timing_questions', '')],
        ["Enforcing approx. 2min. of questions", "", ""],
        ["Stature and Vocal Quality", "0 1 2 3 4 5 6 7 8 9 10", data.get('stature_vocal', '')],
        ["Eye contact, body movements, voice level, 'ums'", "", ""],
        ["Subtotal – Moderation", f"out of 40pts", data.get('subtotal_moderation', '')]
    ]

    moderation_table = Table(moderation_data, colWidths=[2.5*inch, 2*inch, 1*inch])
    moderation_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (1,0), (1,-2), colors.lightgrey),
    ]))
    elements.append(moderation_table)
    elements.append(Spacer(1, 0.1*inch))

    # Feedback on YouTube
    elements.append(Paragraph("b. Feedback on YouTube:", subtitle_style))
    elements.append(Paragraph("Constructive comments including one positive aspect and one possible improvement", normal_style))
    elements.append(Paragraph("□ check if no footage available", normal_style))
    elements.append(Paragraph("Average score will be credited at the end of the semester", normal_style))

    feedback_data = [
        [f"Feedback for {data.get('feedback_for', '________________')}", "0 1 2 3 4 5 6 7 8 9 10", data.get('feedback', '')],
        ["Self-Assessment", "0 1 2 3 4 5 6 7 8 9 10", data.get('self_assessment', '')],
        ["Subtotal – Comments", "out of 20pts", data.get('subtotal_comments', '')]
    ]

    feedback_table = Table(feedback_data, colWidths=[2.5*inch, 2*inch, 1*inch])
    feedback_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (1,0), (1,-2), colors.lightgrey),
    ]))
    elements.append(feedback_table)
    elements.append(Spacer(1, 0.1*inch))

    # Deductions
    elements.append(Paragraph("c. Deductions:", subtitle_style))
    deductions_data = [
        ["Table Topics not approved 24 hours prior to class", "-20pt penalty", data.get('table_topics_not_approved', '')],
        ["Comments posted late", "-5pts / comment", data.get('late_comments', '')]
    ]
    deductions_table = Table(deductions_data, colWidths=[3.5*inch, 1*inch, 1*inch])
    deductions_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    elements.append(deductions_table)
    elements.append(Spacer(1, 0.1*inch))

    # Total Grade
    elements.append(Paragraph("d. Total Grade", subtitle_style))
    total_grade = Table([["", "out of 40pts", data.get('total_grade', '')]], colWidths=[3.5*inch, 1*inch, 1*inch])
    total_grade.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'LEFT'), ('FONTNAME', (0,0), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,0), (-1,-1), 10)]))
    elements.append(total_grade)
    elements.append(Spacer(1, 0.1*inch))

    # Comments
    elements.append(Paragraph("e. Comments:", subtitle_style))
    comments = Paragraph(data.get('comments', ''), normal_style)
    elements.append(comments)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# You can create similar functions for other roles (e.g., generate_table_topic_rubric_pdf, generate_camera_assistant_rubric_pdf, etc.)

def generate_rubric_pdf(role, data):
    if role == "Toastmaster":
        return generate_toastmaster_rubric_pdf(data)
    # Add elif statements for other roles as you implement them
    else:
        raise ValueError(f"Rubric generation for {role} not implemented yet.")