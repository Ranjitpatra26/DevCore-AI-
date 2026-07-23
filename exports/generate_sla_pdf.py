import sys
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

def build_pdf(filename="DevCore_AI_SLA_Stage2_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#1E293B")     # Dark Slate
    SECONDARY = colors.HexColor("#2563EB")   # Royal Blue
    ACCENT = colors.HexColor("#0EA5E9")      # Cyan
    TEXT_COLOR = colors.HexColor("#0F172A")  # Dark Body Text
    BG_LIGHT = colors.HexColor("#F8FAFC")    # Light Gray Table Header
    BORDER_COLOR = colors.HexColor("#CBD5E1")# Border Slate

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=PRIMARY,
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        textColor=SECONDARY,
        spaceAfter=15
    )

    heading1_style = ParagraphStyle(
        'SecHeading1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    heading2_style = ParagraphStyle(
        'SecHeading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=TEXT_COLOR,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        alignment=TA_LEFT,
        textColor=TEXT_COLOR,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        alignment=TA_LEFT,
        textColor=TEXT_COLOR
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=table_cell_style,
        alignment=TA_CENTER
    )

    story = []

    # ---------------------------------------------------------
    # Academic Header Metadata Table
    # ---------------------------------------------------------
    header_data = [
        [Paragraph("<b>Academic Year 2026-2027</b>", table_header_style), "", "", ""],
        [Paragraph("<b>Program: B.Tech. Information Technology</b>", table_header_style), "", "", ""],
        [
            Paragraph("<b>Year of Study:</b> Third Year", table_cell_style),
            "",
            Paragraph("<b>Semester:</b> V", table_cell_style),
            ""
        ],
        [
            Paragraph("<b>Course:</b> Fundamentals of Artificial Intelligence", table_cell_style),
            "",
            Paragraph("<b>Course Code:</b> ITCOR2PC302", table_cell_style),
            ""
        ],
        [
            Paragraph("<b>Class:</b> TYIT-1", table_cell_style),
            "",
            Paragraph("<b>Course In-Charge:</b> Dr. Jalpa Mehta, Ms. Manya Gidwani", table_cell_style),
            ""
        ]
    ]

    t_header = Table(header_data, colWidths=[130, 140, 130, 140])
    t_header.setStyle(TableStyle([
        ('SPAN', (0, 0), (3, 0)),
        ('SPAN', (0, 1), (3, 1)),
        ('SPAN', (0, 2), (1, 2)),
        ('SPAN', (2, 2), (3, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('SPAN', (2, 3), (3, 3)),
        ('SPAN', (0, 4), (1, 4)),
        ('SPAN', (2, 4), (3, 4)),
        ('BACKGROUND', (0, 0), (3, 1), PRIMARY),
        ('BACKGROUND', (0, 2), (3, 4), BG_LIGHT),
        ('ALIGN', (0, 0), (3, 1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # Course Outcomes Table
    # ---------------------------------------------------------
    co_data = [
        [
            Paragraph("<b>CO No.</b>", table_header_style),
            Paragraph("<b>Course Statement (At the end of the course, Learners will be able to ...)</b>", table_header_style),
            Paragraph("<b>BL</b>", table_header_style)
        ],
        [
            Paragraph("<b>CO1</b>", table_cell_center),
            Paragraph("Apply artificial intelligence concepts and search algorithms such as uninformed, informed, and adversarial search to solve problem-solving scenarios.", table_cell_style),
            Paragraph("<b>3</b>", table_cell_center)
        ],
        [
            Paragraph("<b>CO2</b>", table_cell_center),
            Paragraph("Apply knowledge representation techniques, logical inference mechanisms, and expert system reasoning to model intelligent systems.", table_cell_style),
            Paragraph("<b>3</b>", table_cell_center)
        ],
        [
            Paragraph("<b>CO3</b>", table_cell_center),
            Paragraph("Analyze planning strategies and sequential decision-making algorithms to determine optimal policies for knowledge-based agents.", table_cell_style),
            Paragraph("<b>4</b>", table_cell_center)
        ],
        [
            Paragraph("<b>CO4</b>", table_cell_center),
            Paragraph("Evaluate modern artificial intelligence technologies including Large Language Models in terms of applications, ethical implications, and challenges.", table_cell_style),
            Paragraph("<b>5</b>", table_cell_center)
        ],
        [
            Paragraph("<b>CO5</b>", table_cell_center),
            Paragraph("Design solutions by integrating artificial intelligence techniques including search, reasoning, planning, and data analysis for real-world engineering problems.", table_cell_style),
            Paragraph("<b>6</b>", table_cell_center)
        ]
    ]

    t_co = Table(co_data, colWidths=[45, 445, 50])
    t_co.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_co)
    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # Title Section & Student Metadata Table
    # ---------------------------------------------------------
    story.append(Paragraph("SELF LEARNING ASSESSMENT (SLA) MICROPROJECT", ParagraphStyle('SubHead1', parent=subtitle_style, fontSize=11, textColor=PRIMARY)))
    story.append(Paragraph("DevCore AI – An Autonomous Multi-Agent AI Software Engineering Operating System for Automated System Design & Code Synthesis", title_style))
    story.append(Paragraph("Course: Fundamentals of Artificial Intelligence (Semester – V)", subtitle_style))

    author_data = [
        [Paragraph("<b>Student Name</b>", table_header_style), Paragraph("<b>Class</b>", table_header_style), Paragraph("<b>Roll No. / PRN</b>", table_header_style)],
        [Paragraph("Ranjit Patra", table_cell_center), Paragraph("TYIT1-1", table_cell_center), Paragraph("124BTIT10XX", table_cell_center)]
    ]
    t_author = Table(author_data, colWidths=[240, 150, 150])
    t_author.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_author)
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1.5, color=SECONDARY, spaceAfter=15))

    # ---------------------------------------------------------
    # Section 1: Problem Statement
    # ---------------------------------------------------------
    story.append(Paragraph("1. Problem Statement", heading1_style))
    
    p1 = ("In traditional software development environments, building production-grade software applications requires extensive human coordination across multiple engineering disciplines. The lifecycle spans business requirements gathering, functional decomposition, architectural topology design, frontend component rendering, backend microservice implementation, database schema normalization, security threat modeling, quality assurance testing, and DevOps deployment scripting. Each phase relies on distinct engineering personas working sequentially, leading to communication bottlenecks, specification drift, high labor overhead, and extended delivery timelines.")
    story.append(Paragraph(p1, body_style))

    p2 = ("Existing commercial AI code generators and prompt-based tools suffer from significant limitations. Single-prompt large language model (LLM) interfaces operate without long-term architectural memory, producing isolated code snippets that fail to compile or integrate into larger codebases. Furthermore, standard AI assistants lack cross-disciplinary domain grounding—a backend prompt fails to consider database indexes created by a DBA, while a frontend prompt generates components disconnected from backend API contracts.")
    story.append(Paragraph(p2, body_style))

    p3 = ("To bridge these structural gaps, there is an urgent need for <b>DevCore AI</b>—an autonomous multi-agent AI software engineering operating system. DevCore AI orchestrates 13 specialized engineering personas (including CEO, Business Analyst, Project Manager, Software Architect, UI/UX Designer, Frontend Engineer, Backend Engineer, Database Administrator, Security Lead, DevOps Engineer, QA Engineer, Technical Writer, and Code Reviewer) inside a synchronized state graph execution pipeline. The system automates end-to-end software development, transforming raw project ideas into production-ready blueprints, executable multi-file code packages, interactive system flowcharts, and real-time interactive specialist consultation channels with zero contextual drift.")
    story.append(Paragraph(p3, body_style))

    story.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # Section 2: Comparative Analysis
    # ---------------------------------------------------------
    story.append(Paragraph("2. Comparative Analysis", heading1_style))
    story.append(Paragraph("A comprehensive comparative analysis evaluating DevCore AI against existing benchmark multi-agent frameworks and autonomous developer platforms:", body_style))

    comp_headers = [
        Paragraph("<b>Parameter</b>", table_header_style),
        Paragraph("<b>DevCore AI<br/>(Our System)</b>", table_header_style),
        Paragraph("<b>ChatDev</b>", table_header_style),
        Paragraph("<b>MetaGPT</b>", table_header_style),
        Paragraph("<b>AutoGen</b>", table_header_style),
        Paragraph("<b>Devin AI</b>", table_header_style)
    ]

    comp_rows = [
        ["Research Focus", "Synchronized 13-Agent OS & Multi-File IDE Workspace", "Chat-based Virtual Software Company", "SOP-based Multi-Agent Development Pipeline", "Conversational Multi-Agent Framework", "Autonomous AI Software Engineer Sandbox"],
        ["AI Technique", "LangGraph State Graph + Local LLM (Qwen 3.5 9B) + RAG", "Sequential Multi-Agent Chat Chains", "Standard Operating Procedure (SOP) Chains", "Conversational Agent Event Loops", "Reinforcement Learning + LLM Tool Use"],
        ["Workspace & IDE", "Built-in VS Code-style IDE & Multi-File Parser", "CLI Text Logs", "File System Artifact Export", "Console / Terminal Output", "Browser Sandbox Environment"],
        ["Blueprint Sync", "Full 13-Role Grounded Context Synchronization", "Phase-based Chat History", "Artifact-based Output Schemas", "Text Conversation Loops", "Issue-based Code Commits"],
        ["Dynamic Diagrams", "Live Mermaid.js Flowcharts (PNG & SVG Download)", "Static Image Graphs", "Basic UML Visuals", "None", "Terminal Logs"],
        ["Consultation Terminal", "Interactive Node Consultation & Real-time Work Status Reports", "Phase Chat Only", "Non-Interactive SOP Execution", "Multi-Agent Loop", "Task Prompt Interface"],
        ["Main Technologies", "Python, Streamlit, LangGraph, Ollama, SQLite, Mermaid.js", "Python, OpenAI API", "Python, OpenAI API", "Python, AutoGen SDK", "Custom Cloud Sandbox"],
        ["Major Advantage", "Sub-30s parallel synthesis, zero context leak, local privacy", "Simple phase configuration", "Structured documentation output", "Flexible agent definitions", "Autonomous shell execution"],
        ["Major Limitation", "Higher local VRAM requirement for offline LLMs", "API token cost & sequential delay", "Rigid execution flow", "Requires complex custom setup", "Proprietary subscription model"],
        ["Relevance Score", "Very High", "High", "High", "Medium", "Very High"]
    ]

    comp_data = [comp_headers]
    for r in comp_rows:
        row_cells = [Paragraph(f"<b>{r[0]}</b>", table_cell_style)]
        for val in r[1:]:
            c_style = table_cell_center if val in ["Very High", "High", "Medium"] else table_cell_style
            row_cells.append(Paragraph(val, c_style))
        comp_data.append(row_cells)

    t_comp = Table(comp_data, colWidths=[75, 95, 74, 74, 74, 148])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.6, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (1, 1), (1, -1), colors.HexColor("#EFF6FF")), # Highlight DevCore AI
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # Section 3: Features of the Application
    # ---------------------------------------------------------
    story.append(Paragraph("3. Detailed Features of the Application", heading1_style))

    story.append(Paragraph("<b>3.1 Synchronized 13-Agent Blueprint Generation Pipeline</b>", heading2_style))
    story.append(Paragraph("• <b>4-Stage Parallel ThreadPoolExecutor Execution:</b> Distributes 13 specialized engineering personas across concurrent worker pools, reducing complete system specification generation time from >10 minutes to sub-30 seconds.", bullet_style))
    story.append(Paragraph("• <b>Comprehensive Architectural Coverage:</b> Produces grounded, enterprise-grade blueprints spanning Business Strategy (CEO), Functional Requirements (BA), Product Roadmaps (PM), System Topology (Architect), UI Design Tokens (UI/UX), FastAPI REST Contracts (Backend), PostgreSQL DDL Schemas (DBA), STRIDE Threat Models (Security), Docker Containerization (DevOps), Pytest Test Suites (QA), API Reference Docs (Writer), and Quality Gate Audits (Reviewer).", bullet_style))

    story.append(Paragraph("<b>3.2 VS Code-Style Code-First Implementation Studio</b>", heading2_style))
    story.append(Paragraph("• <b>Interactive Multi-File Code Workspace:</b> Features 12 engineering persona modes, 11 specialized categories (Backend, Frontend, Database, AI/RAG, QA, DevOps, Security, Docs, Architecture, Structure, Debug), and 80+ sub-module selection chips.", bullet_style))
    story.append(Paragraph("• <b>Intelligent File Structure Parser:</b> Automatically detects ASCII folder tree diagrams and routes them to <code>docs/file_structure_architecture.txt</code>, ensuring primary workspace files (<code>app/main.py</code>, <code>routers/auth_router.py</code>, <code>database/schema.sql</code>) contain 100% executable production source code.", bullet_style))

    story.append(Paragraph("<b>3.3 Dynamic System Architecture & Flowchart Visualizer</b>", heading2_style))
    story.append(Paragraph("• <b>Native Mermaid.js Theme Rendering:</b> Renders interactive system flowcharts, sequence diagrams, and Entity-Relationship Diagrams (ERDs) with theme-matched color palettes and dynamic CSS max-height boundaries.", bullet_style))
    story.append(Paragraph("• <b>High-Resolution Corner Exporter:</b> Features floating top-right corner action buttons for exporting diagrams directly as high-resolution 2x PNG images (via HTML5 Canvas) or vector SVG files.", bullet_style))

    story.append(Paragraph("<b>3.4 Specialist Agent Consultation Terminal</b>", heading2_style))
    story.append(Paragraph("• <b>Direct Node Consultation:</b> Provides an interactive terminal for continuous Q&A with any of the 13 individual specialist nodes.", bullet_style))
    story.append(Paragraph("• <b>Real-Time Domain Work Status Reports:</b> When asked about progress or implementation status, specialist nodes reply directly as active team members, stating their completion percentage (e.g. 75% complete) alongside a structured breakdown of Completed Features, In-Progress Tasks, and Next Steps.", bullet_style))
    story.append(Paragraph("• <b>Animated Live Stream Indicator:</b> Displays an active bouncing dot typing indicator (<code>DevCore AI is typing... 💬</code>) during real-time LLM token generation.", bullet_style))

    story.append(Paragraph("<b>3.5 Enterprise Export & PDF Documentation Package</b>", heading2_style))
    story.append(Paragraph("• <b>Multi-Format Project Export:</b> Enables one-click package export to Markdown (<code>.md</code>), raw Mermaid (<code>.mmd</code>), and formal academic PDF documentation for seamless submission and deployment.", bullet_style))

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # Section 4: Tools Used
    # ---------------------------------------------------------
    story.append(Paragraph("4. Tools and Technologies Used", heading1_style))

    tools_data = [
        [Paragraph("<b>Category</b>", table_header_style), Paragraph("<b>Technology Used</b>", table_header_style), Paragraph("<b>Technical Function & Purpose</b>", table_header_style)],
        [Paragraph("Programming Language", table_cell_style), Paragraph("Python 3.10+", table_cell_style), Paragraph("Core runtime environment for agent orchestration, RAG indexing, and web framework logic.", table_cell_style)],
        [Paragraph("Frontend Framework", table_cell_style), Paragraph("Streamlit 1.57+", table_cell_style), Paragraph("Spatial UI rendering, dark/light theme engine, custom CSS tokens, iframe visualizers, and state management.", table_cell_style)],
        [Paragraph("Agent Orchestration", table_cell_style), Paragraph("LangGraph & ThreadPoolExecutor", table_cell_style), Paragraph("State graph workflow execution, parallel multi-threaded node execution, and script context synchronization.", table_cell_style)],
        [Paragraph("Large Language Model", table_cell_style), Paragraph("Qwen 3.5 9B (Ollama) / Groq API", table_cell_style), Paragraph("Offline open-weights LLM inference for code synthesis, architectural reasoning, and specialist consultation.", table_cell_style)],
        [Paragraph("Embedding & RAG Engine", table_cell_style), Paragraph("SentenceTransformers (all-MiniLM-L6-v2) & FAISS", table_cell_style), Paragraph("High-speed vector embeddings, semantic search, and contextual document retrieval store.", table_cell_style)],
        [Paragraph("Database Storage", table_cell_style), Paragraph("SQLite3 (Local Thread-Safe Pool)", table_cell_style), Paragraph("Persistent database storing project metadata, agent blueprint runs, and consultation conversation logs.", table_cell_style)],
        [Paragraph("Diagram Visualization", table_cell_style), Paragraph("Mermaid.js 10.x & HTML5 Canvas", table_cell_style), Paragraph("Client-side rendering of architecture flowcharts, sequence diagrams, and PNG/SVG export rendering.", table_cell_style)],
        [Paragraph("Document Export", table_cell_style), Paragraph("ReportLab 5.0 & PyMuPDF (fitz)", table_cell_style), Paragraph("Automated PDF document generation, layout formatting, canvas rendering, and text parsing.", table_cell_style)],
        [Paragraph("Data & Utility Libraries", table_cell_style), Paragraph("Pandas, NumPy, Regex, PyYAML, JSON", table_cell_style), Paragraph("Data manipulation, prompt serialization, regex block parsing, and configuration loading.", table_cell_style)]
    ]

    t_tools = Table(tools_data, colWidths=[110, 140, 290])
    t_tools.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.6, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_tools)
    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # Section 5: Basic Framework & Detailed Execution Pipeline
    # ---------------------------------------------------------
    story.append(Paragraph("5. Basic Framework & System Architecture Pipeline", heading1_style))
    
    story.append(Paragraph("The system architecture of DevCore AI operates as a synchronized, multi-phase agentic pipeline designed to guarantee zero contextual drift between initial requirements and final code execution:", body_style))

    story.append(Paragraph("<b>Stage 1: Requirement Ingestion & Context Grounding</b>", heading2_style))
    story.append(Paragraph("The user inputs project title, industry sector, target audience, technical preferences, and feature specifications. The Context Engine initializes an isolated workspace, generates vector embeddings using <code>all-MiniLM-L6-v2</code>, and indexes background reference documents into the local FAISS vector store.", body_style))

    story.append(Paragraph("<b>Stage 2: Parallel 13-Agent LangGraph Orchestration</b>", heading2_style))
    story.append(Paragraph("The system executes a 4-stage parallel LangGraph state graph using Python <code>ThreadPoolExecutor</code> worker pools:", body_style))
    story.append(Paragraph("• <i>Stage 2.1 (Strategic Alignment):</i> CEO, Lead Business Analyst, and Project Manager synthesize executive strategy, functional requirements, and sprint roadmaps.", bullet_style))
    story.append(Paragraph("• <i>Stage 2.2 (System Architecture & Security):</i> Software Architect, UI/UX Designer, and Security Lead generate clean architecture topologies, CSS design tokens, and STRIDE threat models.", bullet_style))
    story.append(Paragraph("• <i>Stage 2.3 (Implementation Engineering):</i> Backend Engineer, Frontend Engineer, and Database DBA construct FastAPI REST contracts, Streamlit page layouts, and PostgreSQL DDL schemas.", bullet_style))
    story.append(Paragraph("• <i>Stage 2.4 (Ops, QA & Unified Review):</i> DevOps Engineer, QA Engineer, Technical Writer, and Principal Systems Reviewer generate Docker containerization scripts, Pytest suites, README documentation, and final system integration verification.", bullet_style))

    story.append(Paragraph("<b>Stage 3: Multi-File Code & Diagram Parsing Engine</b>", heading2_style))
    story.append(Paragraph("The output parser receives raw LLM responses, extracts code fence blocks, and separates ASCII folder structure diagrams into <code>docs/file_structure_architecture.txt</code> while mapping actual source code blocks to <code>app/main.py</code>, <code>routers/auth_router.py</code>, and <code>database/schema.sql</code>. Concurrently, Mermaid.js code blocks are validated for diagram rendering.", body_style))

    story.append(Paragraph("<b>Stage 4: Interactive IDE & Specialist Consultation Interface</b>", heading2_style))
    story.append(Paragraph("The processed artifacts are rendered in the Streamlit Spatial UI workspace: the VS Code Implementation Studio provides interactive multi-file editing, the System Architecture tab renders flowcharts with high-resolution PNG/SVG export buttons, and the Consultation Terminal connects users directly to specialist nodes for interactive progress reports and technical guidance.", body_style))

    doc.build(story)
    print(f"Successfully generated PDF report: {filename}")

if __name__ == "__main__":
    out_pdf = "DevCore_AI_SLA_Stage2_Report.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)
