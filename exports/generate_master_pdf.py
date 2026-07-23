import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Preformatted, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

def generate_master_pdf(filename="DevCore_AI_Master_Developer_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Color Palette
    PRIMARY = colors.HexColor("#0F172A")       # Dark Slate
    SECONDARY = colors.HexColor("#2563EB")     # Royal Blue
    ACCENT = colors.HexColor("#0EA5E9")        # Cyan
    TEXT_DARK = colors.HexColor("#1E293B")     # Body Text
    BG_LIGHT = colors.HexColor("#F8FAFC")      # Table/Box Background
    BG_CODE = colors.HexColor("#1E293B")       # Code Box Background
    TEXT_CODE = colors.HexColor("#F8FAFC")     # Code Text
    BORDER_COLOR = colors.HexColor("#CBD5E1")  # Border Slate

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=PRIMARY,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=SECONDARY,
        spaceAfter=12
    )

    ch_style = ParagraphStyle(
        'ChapterH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=SECONDARY,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
        spaceAfter=5,
        alignment=TA_LEFT
    )

    bullet_style = ParagraphStyle(
        'BulletDark',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=body_style,
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=PRIMARY
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=TEXT_CODE,
        spaceBefore=3,
        spaceAfter=3
    )

    story = []

    # COVER / HEADER BANNER
    story.append(Paragraph("DevCore AI — Master Architectural Handbook & Visual Diagram Manual", title_style))
    story.append(Paragraph("Comprehensive Technical Guide, Visual Flowchart Diagrams, 13-Agent Mechanics, Dual AI Inference & Viva Defense Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=SECONDARY, spaceAfter=10))

    # CHAPTER 1: EXECUTIVE SUMMARY & SYSTEM VISION
    story.append(Paragraph("Chapter 1: Executive Summary & System Vision", ch_style))
    story.append(Paragraph("<b>1.1 Project Definition:</b> DevCore AI is an autonomous, full-stack multi-agent software engineering operating system designed to transform high-level software ideas into production-ready architectural blueprints, data schemas, API specifications, and working implementation code files.", body_style))
    story.append(Paragraph("<b>1.2 Purpose of Building:</b> Traditional software engineering planning requires human architects, database engineers, product managers, and security leads to spend weeks drafting requirements, software architecture documents (SAD), database ERDs, and boilerplate code. DevCore AI automates 80%+ of this initial engineering lifecycle, reducing human effort from weeks to minutes.", body_style))

    # 60-Second Pitch Box
    pitch_text = "<b>60-Second Elevator Pitch (For Professors / Colleagues):</b><br/><i>'DevCore AI replaces weeks of initial software engineering planning by deploying a team of 13 specialized AI agents—ranging from CEO and Architect to Database Engineer and Security Chief. Instead of writing naive single-prompt code, DevCore AI orchestrates a dual-engine architecture (Local GPU Ollama + Groq LPU Cloud) paired with Vector RAG to generate enterprise-grade software architecture, normalized database schemas, and runnable code in seconds.'</i>"
    t_pitch = Table([[Paragraph(pitch_text, callout_style)]], colWidths=[540])
    t_pitch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BORDER', (0,0), (-1,-1), 1, SECONDARY),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_pitch)
    story.append(Spacer(1, 8))

    # 3-Minute Script Box
    script_text = "<b>3-Minute Presentation Script (For Viva & Technical Demonstrations):</b><br/>" \
                  "1. <i>Introduction (30s):</i> 'Good morning! DevCore AI is an autonomous multi-agent software engineering platform. Developers spend 80% of their time writing specs, designing schemas, and writing repetitive boilerplate code. DevCore AI automates this entire lifecycle.'<br/>" \
                  "2. <i>Core Architecture (60s):</i> 'Unlike single-prompt AI tools, DevCore AI deploys a specialized 13-agent pipeline. Each agent node—such as the Software Architect or Security Chief—focuses on its exact domain. Furthermore, we built a hybrid dual-engine runtime: on local PCs, it leverages NVIDIA GPU acceleration via Ollama; when deployed to the cloud, it seamlessly falls back to Groq Cloud LPUs delivering 500+ tokens per second.'<br/>" \
                  "3. <i>Live Features (60s):</i> 'The platform features an Autonomous 13-Agent Blueprint Pipeline, an interactive Implementation Studio for generating runnable code files, a Specialist Consultation Terminal with RAG context retrieval, and an instant floating AI Assistant stored in a thread-safe SQLite WAL database.'<br/>" \
                  "4. <i>Conclusion (30s):</i> 'DevCore AI bridges the gap between high-level human vision and production engineering, delivering speed, architectural rigor, and enterprise security.'"
    t_script = Table([[Paragraph(script_text, body_style)]], colWidths=[540])
    t_script.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BORDER', (0,0), (-1,-1), 1, SECONDARY),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_script)

    story.append(PageBreak())

    # CHAPTER 3: FULL SYSTEM ARCHITECTURE & DATA FLOW (WITH VISUAL DIAGRAM)
    story.append(Paragraph("Chapter 3: System Architecture & Visual Tier Diagram", ch_style))
    story.append(Paragraph("Below is the visual architectural diagram illustrating DevCore AI's 4-tier decoupled stack:", body_style))
    story.append(Spacer(1, 4))

    # Embed System Architecture Diagram Image
    img_arch = "assets/diagrams/system_architecture.png"
    if os.path.exists(img_arch):
        story.append(RLImage(img_arch, width=520, height=280))
        story.append(Spacer(1, 8))

    arch_data = [
        ["System Layer", "Core Technologies Used", "Primary Responsibilities"],
        ["1. Presentation Layer", "Streamlit SPA, Custom CSS Neobrutalism Tokens", "Renders SPA navigation, dynamic containers, Mermaid SVG charts"],
        ["2. Orchestration Layer", "LangChain, LangGraph Event State Machine", "Coordinates sequential 13-agent graph transitions"],
        ["3. AI Inference & RAG", "Ollama GPU (Local) + Groq Cloud LPU + SentenceTransformers", "Performs hybrid LLM inference and 384-dim vector RAG retrieval"],
        ["4. Data Persistence", "SQLite3 (WAL Mode), Thread-Safe Connections", "Stores projects, files, agent blueprints, chats, and vector embeddings"]
    ]
    t_arch = Table(arch_data, colWidths=[110, 180, 250])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('FONTSIZE', (0,1), (-1,-1), 7.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_arch)

    story.append(PageBreak())

    # CHAPTER 4: 13-AGENT PIPELINE (WITH VISUAL DIAGRAM)
    story.append(Paragraph("Chapter 4: The 13-Agent Autonomous Pipeline Flowchart", ch_style))
    story.append(Paragraph("Below is the visual workflow flowchart showing how the 13 specialized AI agent nodes execute sequentially:", body_style))
    story.append(Spacer(1, 4))

    # Embed 13-Agent Pipeline Image
    img_pipeline = "assets/diagrams/agent_pipeline.png"
    if os.path.exists(img_pipeline):
        story.append(RLImage(img_pipeline, width=520, height=280))
        story.append(Spacer(1, 8))

    story.append(PageBreak())

    # CHAPTER 5: DUAL INFERENCE (WITH VISUAL DIAGRAM)
    story.append(Paragraph("Chapter 5: Dual AI Inference & Failover Diagram", ch_style))
    story.append(Paragraph("Below is the visual hardware & cloud inference failover diagram:", body_style))
    story.append(Spacer(1, 4))

    # Embed Dual Engine Image
    img_dual = "assets/diagrams/dual_engine.png"
    if os.path.exists(img_dual):
        story.append(RLImage(img_dual, width=520, height=280))
        story.append(Spacer(1, 8))

    story.append(PageBreak())

    # CHAPTER 6: VECTOR RAG (WITH VISUAL DIAGRAM)
    story.append(Paragraph("Chapter 6: Vector RAG Retrieval Engine Flowchart", ch_style))
    story.append(Paragraph("Below is the visual data flow diagram of SentenceTransformers 384-dimensional vector indexing and Cosine Similarity retrieval:", body_style))
    story.append(Spacer(1, 4))

    # Embed RAG Image
    img_rag = "assets/diagrams/rag_retrieval.png"
    if os.path.exists(img_rag):
        story.append(RLImage(img_rag, width=520, height=280))
        story.append(Spacer(1, 8))

    story.append(PageBreak())

    # CHAPTER 10: VIVA DEFENSE GUIDE
    story.append(Paragraph("Chapter 10: Professor & Colleague Presentation Defense Guide", ch_style))
    story.append(Paragraph("Below are the top viva and presentation defense questions with authoritative technical answers:", body_style))

    q1 = "<b>Q1: Why use a 13-Agent Multi-Agent pipeline instead of a single prompt?</b><br/><i>Answer: Single prompts mix architectural scopes, leading to shallow code and hallucinated security/database designs. Specialized agents focus on domain-specific constraints (e.g. CSO handles STRIDE, Database Lead handles WAL mode normalization), resulting in enterprise-grade software quality.</i>"
    story.append(Paragraph(q1, body_style))
    story.append(Spacer(1, 4))

    q2 = "<b>Q2: How does the system handle cloud deployment without a GPU?</b><br/><i>Answer: Through an automatic dual-engine failover mechanism. When deployed to a cloud server without local Ollama, the application seamlessly routes inference calls to the Groq Cloud LPU API (llama-3.3-70b-versatile), delivering sub-second responses for web users.</i>"
    story.append(Paragraph(q2, body_style))
    story.append(Spacer(1, 4))

    q3 = "<b>Q3: What makes your RAG implementation effective?</b><br/><i>Answer: We use SentenceTransformers (all-MiniLM-L6-v2) to generate 384-dimensional dense vectors stored in SQLite. Cosine similarity matching retrieves exact project metadata, blueprints, and code files to ground agent consultations without context truncation.</i>"
    story.append(Paragraph(q3, body_style))
    story.append(Spacer(1, 4))

    q4 = "<b>Q4: How is database concurrency handled in SQLite?</b><br/><i>Answer: We enable Write-Ahead Logging (WAL mode) and utilize thread-local connections with timeout retry logic in database/connection.py, preventing database locks during parallel agent queries.</i>"
    story.append(Paragraph(q4, body_style))

    # Build Document
    doc.build(story)
    print(f"Master Developer PDF Manual with visual diagrams generated: {filename}")

if __name__ == "__main__":
    generate_master_pdf()
