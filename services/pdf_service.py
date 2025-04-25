import os
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem

def generate_pdf(meeting: Any, output_path: str) -> None:
    """
    Generate PDF report from meeting data
    
    Args:
        meeting: Meeting object with transcript, summary, etc.
        output_path: Path to save the PDF
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='Heading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8
    ))
    
    # Build content
    content = []
    
    # Title
    content.append(Paragraph(meeting.title, styles['Title']))
    content.append(Spacer(1, 12))
    
    # Meeting details
    details = [
        ["Date:", meeting.date],
        ["Duration:", meeting.duration or "Unknown"],
        ["Language:", meeting.language],
    ]
    details_table = Table(details, colWidths=[80, 400])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    content.append(details_table)
    content.append(Spacer(1, 12))
    
    # Participants
    if meeting.participants:
        content.append(Paragraph("Participants", styles['Heading2']))
        participants_list = []
        for participant in meeting.participants:
            participants_list.append(Paragraph(participant.get("name", "Unknown"), styles['Normal']))
        content.append(ListFlowable(participants_list, bulletType='bullet', leftIndent=20))
        content.append(Spacer(1, 12))
    
    # Summary
    if meeting.summary:
        content.append(Paragraph("Summary", styles['Heading2']))
        content.append(Paragraph(meeting.summary, styles['Normal']))
        content.append(Spacer(1, 12))
    
    # Action Items
    if meeting.action_items:
        content.append(Paragraph("Action Items", styles['Heading2']))
        action_items_list = []
        for item in meeting.action_items:
            text = item.get("text", "")
            assignee = item.get("assignee", "")
            due_date = item.get("due_date", "")
            
            item_text = f"{text}"
            if assignee:
                item_text += f" (Assignee: {assignee}"
                if due_date:
                    item_text += f", Due: {due_date}"
                item_text += ")"
            
            action_items_list.append(Paragraph(item_text, styles['Normal']))
        
        content.append(ListFlowable(action_items_list, bulletType='bullet', leftIndent=20))
        content.append(Spacer(1, 12))
    
    # Decisions
    if meeting.decisions:
        content.append(Paragraph("Key Decisions", styles['Heading2']))
        decisions_list = []
        for decision in meeting.decisions:
            decisions_list.append(Paragraph(decision.get("text", ""), styles['Normal']))
        
        content.append(ListFlowable(decisions_list, bulletType='bullet', leftIndent=20))
        content.append(Spacer(1, 12))
    
    # Transcript
    if meeting.transcript:
        content.append(Paragraph("Transcript", styles['Heading2']))
        lines = meeting.transcript.strip().split('\n')
        for line in lines:
            if line.strip():
                content.append(Paragraph(line, styles['Normal']))
            else:
                content.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(content)
