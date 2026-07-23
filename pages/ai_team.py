import streamlit as st
from agents.prompts import SYSTEM_PROMPTS
from agents.base import get_role_display_name
from database.connection import execute_query

# 13 Specialist Node Complete Dataset
TEAM_DATA = [
    {
        "role": "ceo",
        "name": "CEO",
        "title": "Chief Executive Officer & Vision Node",
        "icon": "👑",
        "step": 1,
        "summary": "Defines vision, market context, KPIs, risks, and corporate monetizations.",
        "responsibilities": [
            "Formulates strategic product goals and core value propositions",
            "Identifies target user personas and operational pain points",
            "Establishes SaaS monetization models and pricing tier structures",
            "Evaluates high-level business risks and mitigation strategies"
        ],
        "why_important": "Without the CEO node, software projects risk lacking strategic market direction, business intent, and monetization pathways. The CEO aligns engineering execution with user value and corporate profitability.",
        "fast_facts": "⚡ Processes executive intent in ~2.5 seconds.<br/>💰 Generates multi-tier pricing structures (Freemium, Pro SaaS, Enterprise SLA).<br/>🎯 Identifies target persona pain points and corporate risk mitigation matrices.",
        "deliverables": [
            "CEO Strategic Blueprint",
            "Business Risk Matrix",
            "Revenue & Pricing Model",
            "Target Persona Specifications"
        ],
        "capabilities": ["Executive Strategy", "Risk Assessment", "Market Positioning", "SaaS Monetization"]
    },
    {
        "role": "business_analyst",
        "name": "Business Analyst",
        "title": "Lead Business Requirements Analyst",
        "icon": "📊",
        "step": 2,
        "summary": "Specifies user stories, functional outlines, NFR targets, and BRDs.",
        "responsibilities": [
            "Extracts functional requirements (FRs) from user prompts and uploaded SRS documents",
            "Defines non-functional requirements (NFRs) for performance, security, and throughput",
            "Drafts structured agile user stories with acceptance criteria",
            "Correlates RAG vector context with system capabilities"
        ],
        "why_important": "The Business Analyst translates high-level user ideas into precise, unambiguous technical specifications. They eliminate costly rework and scope creep by setting strict acceptance criteria.",
        "fast_facts": "📄 Scans uploaded PDF/DOCX specs using RAG embeddings.<br/>📋 Generates BRDs with functional (FR) and non-functional (NFR) requirements.<br/>🏃 Drafts agile user stories mapped directly to developer task backlogs.",
        "deliverables": [
            "Business Requirements Document (BRD)",
            "Functional & NFR Outlines",
            "User Story Backlog"
        ],
        "capabilities": ["RAG Context Extraction", "BRD Drafting", "User Story Breakdown", "NFR Auditing"]
    },
    {
        "role": "project_manager",
        "name": "Project Manager",
        "title": "Agile Backlog & Sprint Manager",
        "icon": "📅",
        "step": 3,
        "summary": "Maintains roadmaps, structures sprints, and prioritizes backlog tasks.",
        "responsibilities": [
            "Organizes multi-sprint delivery roadmaps (Sprint 1 through Sprint 4)",
            "Estimates story points and assigns task priorities (High, Medium, Low)",
            "Maps inter-task dependencies across engineering teams",
            "Formulates structured task tracking backlog tables"
        ],
        "why_important": "The Project Manager maintains execution momentum. By partitioning project specifications into 4 structured sprints and estimating story points, they keep the entire engineering workforce synchronized.",
        "fast_facts": "🗓️ Structures 4 sequential sprint milestones.<br/>🔢 Calculates story point weightings across all 13 developer nodes.<br/>📊 Maintains priority backlog matrices to avoid execution bottlenecks.",
        "deliverables": [
            "Sprint Execution Roadmap",
            "Prioritized Task Backlog Table",
            "Milestone Timeline"
        ],
        "capabilities": ["Agile Sprint Planning", "Story Point Estimation", "Dependency Mapping", "Milestone Tracking"]
    },
    {
        "role": "architect",
        "name": "Software Architect",
        "title": "Principal System Architect",
        "icon": "🏗️",
        "step": 4,
        "summary": "Formulates framework targets, deployment layout topologies, and caching.",
        "responsibilities": [
            "Designs overall system architecture (Layered / Clean Architecture)",
            "Selects framework libraries, state machines, and local inference models",
            "Defines caching strategies, loopback sockets, and vector store layers",
            "Drafts system topology and execution node flow diagrams"
        ],
        "why_important": "The Software Architect lays down the structural backbone of the codebase. They ensure the platform is modular, scalable, maintainable, and resilient against technical debt.",
        "fast_facts": "🏛️ Designs Clean/Layered architecture boundaries.<br/>⚡ Specifies local vector store indexing & caching topologies.<br/>🧩 Formulates framework selection and component data flow maps.",
        "deliverables": [
            "System Architecture Specification",
            "ASCII / Mermaid Topology Diagrams",
            "Tech Stack & Caching Specs"
        ],
        "capabilities": ["Clean Architecture Design", "Topology Diagramming", "Framework Evaluation", "Cache Optimization"]
    },
    {
        "role": "ui_ux",
        "name": "UI UX Designer",
        "title": "Product & Design System Director",
        "icon": "🎨",
        "step": 5,
        "summary": "Constructs wireframe maps, color systems, and component rules.",
        "responsibilities": [
            "Defines core design system tokens (colors, typography, borders, shadows)",
            "Constructs layout wireframes and spatial navigation mockups",
            "Establishes accessibility rules (contrast standards, scrollbars, focus states)",
            "Designs reusable UI component guidelines"
        ],
        "why_important": "The UI/UX Designer crafts the visual identity and interaction quality. They create curated color palettes, design tokens, and spatial wireframes that make the product feel premium and accessible.",
        "fast_facts": "🎨 Configures Neo-Brutalist & Glassmorphic CSS design tokens.<br/>🖥️ Generates spatial ASCII layout wireframes.<br/>👁️ Enforces WCAG accessibility contrast standards across light and dark modes.",
        "deliverables": [
            "Design Tokens Specification",
            "ASCII Layout Wireframes",
            "Component Style Guide"
        ],
        "capabilities": ["Design Token Systems", "Wireframe Architecture", "Accessibility Audit", "Visual Styling"]
    },
    {
        "role": "frontend",
        "name": "Frontend Engineer",
        "title": "Lead Frontend Application Engineer",
        "icon": "💻",
        "step": 6,
        "summary": "Organizes directory structures, state systems, and component blocks.",
        "responsibilities": [
            "Structures frontend file and directory hierarchies",
            "Implements state management patterns (Session state, routing handlers)",
            "Provides clean code implementation snippets for interactive views",
            "Integrates responsive design guidelines into frontend views"
        ],
        "why_important": "The Frontend Engineer transforms visual wireframes into real, working client-side interfaces. They manage session state, routing, and interactive component rendering.",
        "fast_facts": "📁 Establishes clean view & component folder structures.<br/>🔄 Implements Streamlit reactive session state logic.<br/>🧩 Delivers reusable component implementation code blocks.",
        "deliverables": [
            "Frontend Codebase Hierarchy",
            "Component Code Snippets",
            "State & Routing Design"
        ],
        "capabilities": ["Component Architecture", "State Management", "Routing Optimization", "UI Code Generation"]
    },
    {
        "role": "backend",
        "name": "Backend Engineer",
        "title": "Lead Backend & API Engineer",
        "icon": "⚙️",
        "step": 7,
        "summary": "Designs API structures, endpoint matrices, auth flows, and controllers.",
        "responsibilities": [
            "Defines RESTful & RPC endpoint specifications",
            "Drafts JSON request payloads and response contracts",
            "Designs session authentication, local state management, and controllers",
            "Provides backend service driver implementation code"
        ],
        "why_important": "The Backend Engineer powers the application logic, API endpoints, and controller drivers. They ensure secure data exchange, schema validation, and server reliability.",
        "fast_facts": "🔌 Outlines RESTful endpoint routes and payload schemas.<br/>🔒 Designs local session authentication & state controllers.<br/>🛠️ Generates Python backend service driver code.",
        "deliverables": [
            "API Endpoint Matrix",
            "JSON Payload Schema Contracts",
            "Backend Controller Code"
        ],
        "capabilities": ["API Design", "Payload Validation", "Controller Architecture", "Service Drivers"]
    },
    {
        "role": "database",
        "name": "Database Engineer",
        "title": "Database Administrator & Data Architect",
        "icon": "🗄️",
        "step": 8,
        "summary": "Writes relational DDL SQL matrices, keys, indexes, and ER diagrams.",
        "responsibilities": [
            "Drafts relational DDL SQL creation statements (CREATE TABLE, constraints)",
            "Defines primary keys, foreign keys, and indexing strategies",
            "Constructs Entity-Relationship (ER) diagram schemas",
            "Designs local SQLite database performance optimizations"
        ],
        "why_important": "The Database Engineer guarantees data persistence and fast retrieval. They write normalized SQL DDL scripts that prevent data corruption and optimize database performance.",
        "fast_facts": "🗃️ Crafts normalized SQLite / SQL DDL creation scripts.<br/>🔑 Establishes primary key, foreign key, and index constraints.<br/>📐 Constructs Entity-Relationship (ER) structural diagrams.",
        "deliverables": [
            "Relational DDL SQL Matrix",
            "Entity-Relationship (ER) Diagram",
            "Database Index Guide"
        ],
        "capabilities": ["SQL DDL Generation", "Schema Normalization", "Index Optimization", "ER Diagramming"]
    },
    {
        "role": "security",
        "name": "Security Engineer",
        "title": "Cybersecurity & STRIDE Threat Analyst",
        "icon": "🛡️",
        "step": 9,
        "summary": "Models threat factors using STRIDE, lists OWASP checklists, and encryption.",
        "responsibilities": [
            "Performs STRIDE threat modeling (Spoofing, Tampering, Repudiation, etc.)",
            "Evaluates OWASP Top 10 vulnerabilities (SQLi, LLM injection, data leaks)",
            "Defines local encryption and secure parameterization policies",
            "Drafts security audit verification checklists"
        ],
        "why_important": "The Security Engineer protects the application against cyber threats, data breaches, and prompt injection exploits. They enforce strict OWASP compliance and data privacy.",
        "fast_facts": "🛡️ Performs STRIDE threat vector analysis.<br/>🔍 Audits OWASP Top 10 vulnerabilities (SQLi, XSS, LLM injection).<br/>🔐 Mandates parameterized SQL queries `(?, ?)` and local data privacy.",
        "deliverables": [
            "STRIDE Threat Matrix",
            "OWASP Security Audit Checklist",
            "Encryption Policy"
        ],
        "capabilities": ["STRIDE Modeling", "OWASP Compliance", "Vulnerability Mitigation", "Data Privacy"]
    },
    {
        "role": "devops",
        "name": "DevOps Engineer",
        "title": "Infrastructure & CI/CD Automation Specialist",
        "icon": "🚀",
        "step": 10,
        "summary": "Builds Docker scripts, compose environments, CI/CD pipelines, and monitors.",
        "responsibilities": [
            "Writes production Dockerfile setup configurations",
            "Drafts docker-compose multi-container orchestration configs",
            "Constructs GitHub Actions CI/CD pipeline automation scripts",
            "Defines local log rotation and container health check metrics"
        ],
        "why_important": "The DevOps Engineer automates build, deployment, and containerization. They ensure the application runs reliably and consistently in any desktop or cloud environment.",
        "fast_facts": "🐳 Authors production multi-stage Dockerfiles.<br/>⚙️ Configures docker-compose container environments.<br/>🔁 Writes GitHub Actions CI/CD automated build scripts.",
        "deliverables": [
            "Production Dockerfile",
            "Docker Compose Configuration",
            "CI/CD Pipeline Script"
        ],
        "capabilities": ["Docker Containerization", "CI/CD Automation", "Environment Scripting", "Log Rotation"]
    },
    {
        "role": "qa",
        "name": "QA Engineer",
        "title": "Quality Assurance & Test Specialist",
        "icon": "🧪",
        "step": 11,
        "summary": "Formulates test matrices, functional validation suites, and unit templates.",
        "responsibilities": [
            "Designs comprehensive test case matrices (Functional, Integration, Edge-case)",
            "Writes unit test code templates (PyTest / Jest style)",
            "Specifies performance and memory benchmark boundaries",
            "Drafts input validation error boundary test plans"
        ],
        "why_important": "The QA Engineer guarantees application stability. They design rigorous test matrices that catch bugs, edge-case failures, and performance bottlenecks before release.",
        "fast_facts": "🧪 Formulates unit, integration, and edge-case test matrices.<br/>💻 Generates PyTest code templates for automated validation.<br/>📈 Sets latency and memory performance benchmark boundaries.",
        "deliverables": [
            "Functional & Edge-Case Test Matrix",
            "Automated Unit Test Snippets",
            "Benchmark Guide"
        ],
        "capabilities": ["Test Case Formulation", "Unit Testing", "Boundary Analysis", "Quality Assurance"]
    },
    {
        "role": "documentation",
        "name": "Documentation Engineer",
        "title": "Technical Writer & Docs Specialist",
        "icon": "📚",
        "step": 12,
        "summary": "Generates README.md files, setup instruction cards, and admin logs.",
        "responsibilities": [
            "Compiles master README.md project documentation",
            "Drafts step-by-step developer installation & setup guides",
            "Documents CLI commands, environment variables, and usage flows",
            "Creates admin operational logs and troubleshooting guides"
        ],
        "why_important": "The Documentation Engineer makes the software accessible and maintainable. They craft clear onboarding guides, API docs, and operational manuals for users and developers.",
        "fast_facts": "📝 Generates master project README.md documentation.<br/>🛠️ Writes step-by-step CLI setup & installation procedures.<br/>📖 Authors admin troubleshooting manuals.",
        "deliverables": [
            "Master Project README.md",
            "Developer Setup Guide",
            "Operational Reference"
        ],
        "capabilities": ["Markdown Generation", "Technical Writing", "Onboarding Documentation", "CLI Reference"]
    },
    {
        "role": "reviewer",
        "name": "Reviewer Agent",
        "title": "Senior Code & Architecture Reviewer",
        "icon": "🔍",
        "step": 13,
        "summary": "Examines plans, fixes architectural logic gaps, and bundles consolidated specifications.",
        "responsibilities": [
            "Audits cross-agent output consistency (e.g. database schema matching API payloads)",
            "Identifies architectural gaps or conflicting requirements",
            "Provides final blueprint quality score and recommendation rating",
            "Bundles consolidated multi-agent execution reports"
        ],
        "why_important": "The Reviewer Agent is the final safeguard. They audit all preceding 12 agent blueprints to resolve contradictions, verify technical alignment, and output the final quality scorecard.",
        "fast_facts": "🔍 Conducts cross-functional consistency audits.<br/>⚖️ Identifies architectural gaps and conflicting specs.<br/>⭐ Computes final quality scorecard ratings.",
        "deliverables": [
            "Cross-Agent Audit Report",
            "Gap Analysis Document",
            "Final Quality Scorecard"
        ],
        "capabilities": ["Cross-Agent Audit", "Consistency Verification", "Consolidated Evaluation", "Quality Scoring"]
    }
]

# Streamlit Modal Dialog Popup for Detailed Dossier Inspection
@st.dialog("Specialist Operational Dossier", width="large")
def show_specialist_modal(member: dict):
    role_key = member["role"]
    name = member["name"]
    title = member["title"]
    icon = member["icon"]
    step = member["step"]
    
    st.html("""
    <style>
    /* Widen AI Specialist Operational Dossier Modal popup toward left & right on AI Team page */
    div[data-testid="stDialog"] > div:first-child,
    div[role="dialog"] {
        max-width: 1150px !important;
        width: 94vw !important;
    }

    /* Ensure stExpander inside stDialog renders clean native > / v chevron arrow toggle on the left */
    div[data-testid="stDialog"] div[data-testid="stExpander"] summary {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        cursor: pointer !important;
    }

    div[data-testid="stDialog"] div[data-testid="stExpander"] summary [data-testid="stExpanderToggleIcon"] {
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        font-size: 1rem !important;
        width: auto !important;
        height: auto !important;
        color: var(--text-color, #1E293B) !important;
    }
    </style>
    """)
    st.html(f"""
    <div style="background-color: var(--hover-bg); border: 3.5px solid var(--border-color); border-radius: 14px; padding: 18px 22px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 15px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="font-size: 2.6rem; background: var(--card-bg); width: 62px; height: 62px; border-radius: 12px; border: 3px solid var(--border-color); display: flex; align-items: center; justify-content: center;">
                    {icon}
                </div>
                <div>
                    <span class="editorial-label" style="color: var(--primary-color);">Pipeline Execution Step 0{step} / 13</span>
                    <h2 style="margin: 2px 0 0 0; border: none; padding: 0; font-size: 1.85rem; color: var(--text-color); font-family: 'Space Grotesk', sans-serif;">{title}</h2>
                </div>
            </div>
        </div>
    </div>
    """)
    
    # 1. What does this specialist do?
    st.markdown("### 🎯 What Does This Specialist Do?")
    st.write(member["summary"])
    st.markdown("**Core Responsibilities:**")
    for resp in member["responsibilities"]:
        st.markdown(f"- **{resp}**")
        
    st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)
    
    # 2. Why is this person important?
    st.markdown("### ⭐ Why Is This Specialist Critical?")
    st.html(f"""
    <div style="background-color: var(--hover-bg); border: 3.5px solid var(--border-color); border-left: 8px solid var(--accent-color); border-radius: 12px; padding: 20px; margin-bottom: 22px;">
        <p style="margin: 0; font-size: 1.05rem; color: var(--text-color); font-weight: 700; line-height: 1.6;">
            {member['why_important']}
        </p>
    </div>
    """)
    
    # 3. Fast Facts & Key Deliverables
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown("### 📌 Fast Facts")
        st.html(f"""
        <div style="background-color: var(--hover-bg); border: 3px solid var(--border-color); border-radius: 12px; padding: 18px;">
            <p style="margin: 0; font-size: 0.95rem; color: var(--text-color); font-weight: 600; line-height: 1.6;">
                {member['fast_facts']}
            </p>
        </div>
        """)
    with col_f2:
        st.markdown("### 📦 Key Deliverables")
        st.html(f"""
        <div style="background-color: var(--hover-bg); border: 3px solid var(--border-color); border-radius: 12px; padding: 18px;">
            <ul style="margin: 0; padding-left: 18px; color: var(--text-color); font-size: 0.95rem; font-weight: 600; line-height: 1.6;">
                {"".join(f'<li style="margin-bottom: 6px;"><b>{d}</b></li>' for d in member['deliverables'])}
            </ul>
        </div>
        """)

    st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)

    # 4. Domain Capabilities
    st.markdown("**Domain Capabilities & Intelligence Modules:**")
    st.html(f"""
    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 25px;">
        {"".join(f'<span class="saas-badge saas-badge-secondary" style="font-size: 0.85rem; padding: 6px 12px; font-weight: 800;">{cap}</span>' for cap in member['capabilities'])}
    </div>
    """)
    
    # Action Buttons
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button(f"💬 Consult & Chat with {name}", key=f"dlg_chat_{role_key}", use_container_width=True, type="primary"):
            st.session_state.chat_agent = role_key
            st.session_state.current_page = "Chat"
            st.rerun()
            
    with col_act2:
        with st.expander(f"📜 Inspect Raw System Prompt ({name})"):
            raw_prompt = SYSTEM_PROMPTS.get(role_key, "No prompt found.")
            safe_prompt = raw_prompt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            st.html(f"""
            <div style="background-color: #0B0F19 !important; border: 3px solid var(--border-color); border-radius: 12px; padding: 18px; margin-top: 8px; box-shadow: inset 0 2px 8px rgba(0,0,0,0.6); overflow-x: auto;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #1E293B;">
                    <div style="display: flex; gap: 6px;">
                        <div style="width: 10px; height: 10px; border-radius: 50%; background-color: #EF4444;"></div>
                        <div style="width: 10px; height: 10px; border-radius: 50%; background-color: #F59E0B;"></div>
                        <div style="width: 10px; height: 10px; border-radius: 50%; background-color: #10B981;"></div>
                    </div>
                    <span style="font-family: monospace; font-size: 0.72rem; color: #94A3B8; font-weight: 700; letter-spacing: 0.05em;">SYSTEM_PROMPT.md</span>
                </div>
                <pre style="margin: 0; padding: 0; background: transparent !important; color: #F9FAFB !important; font-family: 'Fira Code', 'Cascadia Code', Consolas, monospace !important; font-size: 0.85rem !important; line-height: 1.6 !important; white-space: pre-wrap !important; word-break: break-word !important; text-decoration: none !important; border: none !important; outline: none !important;"><code style="background: transparent !important; color: #F9FAFB !important; text-decoration: none !important; border: none !important; outline: none !important; font-family: inherit !important;">{safe_prompt}</code></pre>
            </div>
            """)

def show_ai_team():
    """Render the AI Workforce dashboard with interactive staff directory, real execution status badges, and modal dialog popups."""
    
    st.html("""
    <div class="editorial-hero-container" style="padding: 40px 32px; margin-bottom: 30px;">
        <span class="editorial-label" style="display: block; margin-bottom: 8px;">⚡ Autonomous Engineering Roster</span>
        <h1 class="ai-workforce-title">AI Specialist Workforce</h1>
        <p style="color: var(--text-secondary); margin: 0; font-size: 1.2rem; max-width: 720px; line-height: 1.5;">
            Meet the 13 specialized AI developer nodes. Click on any staff card below to pop up their full operational dossier, key facts, and responsibility matrix.
        </p>
    </div>
    """)

    # Query completed agent runs for active project (if any)
    completed_agent_roles = set()
    active_project_id = st.session_state.get("active_project_id")
    if active_project_id:
        try:
            runs = execute_query("SELECT agent_role FROM agent_runs WHERE project_id = ?", (active_project_id,))
            completed_agent_roles = {r['agent_role'].lower() for r in runs}
        except Exception:
            pass

    st.markdown("## Operational Staff Directory")
    st.html("<p style='font-size: 1rem; color: var(--text-secondary); margin-top: -10px; margin-bottom: 24px;'>Click any staff card to pop up the specialist's detailed role, responsibilities, and importance.</p>")
    
    # Check if a card was clicked via trigger state
    if "open_modal_role" in st.session_state and st.session_state.open_modal_role:
        target_role = st.session_state.open_modal_role
        st.session_state.open_modal_role = None
        matched_member = next((m for m in TEAM_DATA if m["role"] == target_role), None)
        if matched_member:
            show_specialist_modal(matched_member)

    # 4-Column Grid of Interactive Staff Cards
    for idx in range(0, len(TEAM_DATA), 4):
        cols = st.columns(4)
        for sub_idx in range(4):
            item_idx = idx + sub_idx
            if item_idx < len(TEAM_DATA):
                member = TEAM_DATA[item_idx]
                role_key = member["role"]
                
                # Real dynamic execution status for current active project workspace
                is_completed = role_key.lower() in completed_agent_roles
                status_text = "Completed" if is_completed else "Ready Node"
                status_bg = "rgba(16, 185, 129, 0.15)" if is_completed else "rgba(99, 102, 241, 0.15)"
                status_color = "var(--success-color)" if is_completed else "var(--primary-color)"
                
                with cols[sub_idx]:
                    # Draw beautiful Neo-Brutalist staff card
                    st.html(f"""
                    <div style="background-color: var(--card-bg); border: 3.5px solid var(--border-color); border-radius: 14px;
                                padding: 18px; margin-bottom: 10px; box-shadow: var(--shadow-soft);
                                transition: all 0.2s ease; position: relative;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span style="font-size: 1.5rem;">{member['icon']}</span>
                            <span style="font-size: 0.75rem; color: {status_color}; font-weight: 800; background: {status_bg}; padding: 4px 8px; border-radius: 6px; border: 1.5px solid {status_color};">{status_text}</span>
                        </div>
                        <h4 style="margin: 0 0 6px 0; font-size: 1.15rem; color: var(--text-color); font-family: 'Space Grotesk', sans-serif;">{member['name']}</h4>
                        <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0; line-height: 1.45; height: 44px; overflow: hidden;">{member['summary']}</p>
                    </div>
                    """)
                    
                    if st.button(f"⚡ Inspect {member['name']}", key=f"btn_staff_{role_key}", use_container_width=True, type="secondary"):
                        st.session_state.open_modal_role = role_key
                        st.session_state.inspect_role = role_key
                        st.rerun()

    st.html("<div class='saas-divider' style='margin: 35px 0;'></div>")

    # Quick Selectbox Fallback Trigger
    st.markdown("### Quick Specialist Inspector")
    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        selected_role_quick = st.selectbox(
            "Select Specialist Node to Open Pop-up Dossier",
            options=[m["role"] for m in TEAM_DATA],
            format_func=get_role_display_name
        )
    with col_sel2:
        st.write("") # Alignment spacer
        st.write("")
        if st.button("Open Specialist Pop-up Box", use_container_width=True, type="primary"):
            st.session_state.open_modal_role = selected_role_quick
            st.rerun()
