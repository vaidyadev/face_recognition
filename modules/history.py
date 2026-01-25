import os
import json
from time import strftime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def load_history(history_file):
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            return json.load(f)
    return []

def save_history(history_file, history_data):
    with open(history_file, 'w') as f:
        json.dump(history_data, f)

def generate_pdf(filename, history_data):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = styles['Title']
    story.append(Paragraph("Chat History Export", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Content
    normal_style = styles['Normal']
    user_style = ParagraphStyle(
        'UserStyle',
        parent=styles['Normal'],
        textColor=colors.blue,
        spaceAfter=6
    )
    bot_style = ParagraphStyle(
        'BotStyle',
        parent=styles['Normal'],
        textColor=colors.black,
        spaceAfter=12
    )
    
    session_title_style = ParagraphStyle(
        'SessionTitle',
        parent=styles['Heading2'],
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.darkgreen
    )

    for session in history_data:
        # Session Header
        session_time = session.get('timestamp', 'Unknown Time')
        session_name = session.get('title', 'Unknown Session')
        story.append(Paragraph(f"Session: {session_name} ({session_time})", session_title_style))
        story.append(Spacer(1, 0.1 * inch))

        for msg in session.get('messages', []):
            role = msg.get('role', 'unknown').capitalize()
            content = msg.get('content', '')
            
            # Sanitize content for PDF (replace newlines with <br/> for ReportLab)
            content = content.replace('\n', '<br/>')
            
            if role.lower() == 'user':
                story.append(Paragraph(f"<b>You:</b> {content}", user_style))
            else:
                story.append(Paragraph(f"<b>HelpBot:</b> {content}", bot_style))
        
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("_" * 60, normal_style))
        story.append(Spacer(1, 0.2 * inch))

    doc.build(story)

def generate_txt(filename, history_data):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Chat History Export\n")
        f.write("=" * 30 + "\n\n")
        
        for session in history_data:
            f.write(f"Session: {session.get('title', 'Untitled')} ({session.get('timestamp', '')})\n")
            f.write("-" * 50 + "\n")
            
            for msg in session.get('messages', []):
                role = "You" if msg.get('role') == 'user' else "HelpBot"
                content = msg.get('content', '')
                f.write(f"{role}: {content}\n\n")
            
            f.write("\n" + "=" * 30 + "\n\n")

def generate_json(filename, history_data):
    export_data = {
        "export_date": strftime('%Y-%m-%d %H:%M:%S'),
        "sessions": history_data
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=4, ensure_ascii=False)
