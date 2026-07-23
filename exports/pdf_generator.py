import re
from io import BytesIO
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from agents.base import get_role_display_name

def clean_markdown_for_pdf(text: str) -> str:
    """Preprocess markdown into basic HTML tags that ReportLab Paragraph supports."""
    # Convert code blocks to simple preformatted-looking spans or text blocks
    text = re.sub(r'```[\w]*\n(.*?)```', r'<font face="Courier">\1</font>', text, flags=re.DOTALL)
    # Convert bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Convert italics
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Strip headers formatting since we handle them in paragraph loop
    # Convert list bullets
    text = re.sub(r'^\s*-\s+(.*?)$', r'&bull; \1', text, flags=re.MULTILINE)
    # Clean XML character issues
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Restore the tags reportlab needs
    text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    text = text.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
    text = text.replace("&lt;font", "<font").replace("&lt;/font&gt;", "</font>").replace("&gt;", ">")
    return text

def build_pdf_blueprint(project_name: str, agent_runs: List[Dict[str, Any]]) -> bytes:
    """Compile agent blueprint markdown runs into a clean, multi-page ReportLab PDF document."""
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Neo-Brutalist Colors and Typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=colors.HexColor('#111827'),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2563EB'), # Primary blue
        spaceAfter=30
    )
    
    heading1_style = ParagraphStyle(
        'AgentHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#111827'),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    heading2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#8B5CF6'), # Secondary purple
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#374151'),
        spaceAfter=8
    )
    
    story = []
    
    # 1. Cover Page Elements
    story.append(Spacer(1, 1.5 * inch))
    # Neo Brutalist Title Box Accent
    cover_data = [[Paragraph(f"<b>SOFTWARE PLANNING BLUEPRINT</b>", title_style)]]
    cover_table = Table(cover_data, colWidths=[500])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FACC15')), # Bright Yellow Accent
        ('BOX', (0,0), (-1,-1), 3, colors.HexColor('#111827')),
        ('PADDING', (0,0), (-1,-1), 20),
        ('BOTTOMPADDING', (0,0), (-1,-1), 25),
    ]))
    
    story.append(cover_table)
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph(f"PROJECT NAME: {project_name.upper()}", subtitle_style))
    story.append(Paragraph("COLLABORATIVE MULTI-AGENT SPECIFICATION PACKAGE", body_style))
    story.append(Paragraph("GENERATE DIRECTLY ON DEVICE VIA DEVCORE AI ENGINE", body_style))
    story.append(PageBreak())
    
    # Sort agent runs according to default workflow sequence
    role_order = [
        "ceo", "business_analyst", "project_manager", "architect", "ui_ux",
        "frontend", "backend", "database", "security", "devops", "qa",
        "documentation", "reviewer"
    ]
    
    runs_map = {run['agent_role'].lower(): run for run in agent_runs}
    
    # 2. Add Content of Each Agent Run (Ensure all 13 roles are represented)
    processed_roles = set()
    all_roles_to_render = role_order + [r for r in runs_map if r not in role_order]
    
    for role in all_roles_to_render:
        if role in processed_roles:
            continue
        processed_roles.add(role)
        
        display_name = get_role_display_name(role)
        story.append(Paragraph(f"{display_name} Blueprint", heading1_style))
        story.append(Spacer(1, 5))
        
        if role not in runs_map or not runs_map[role].get('output_markdown'):
            story.append(Paragraph("Blueprint section pending synthesis.", body_style))
            story.append(Spacer(1, 15))
            story.append(PageBreak())
            continue
            
        run = runs_map[role]
        lines = run['output_markdown'].split('\n')
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
                
            try:
                if line_str.startswith('##'):
                    clean_heading = clean_markdown_for_pdf(line_str.lstrip('#').strip())
                    story.append(Paragraph(clean_heading, heading2_style))
                elif line_str.startswith('#'):
                    clean_heading = clean_markdown_for_pdf(line_str.lstrip('#').strip())
                    story.append(Paragraph(clean_heading, heading2_style))
                else:
                    clean_text = clean_markdown_for_pdf(line_str)
                    story.append(Paragraph(clean_text, body_style))
            except Exception:
                # Safe fallback if line formatting fails
                story.append(Paragraph(line_str.replace("<", "&lt;").replace(">", "&gt;"), body_style))
                
        story.append(Spacer(1, 15))
        story.append(PageBreak())
        
    doc.build(story)
    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()
    return pdf_bytes
