import re
import base64
import streamlit as st
import streamlit.components.v1 as components
from database.connection import execute_query, execute_update
from components.ui import saas_card
from exports.markdown import package_project_blueprint_zip
from exports.pdf_generator import build_pdf_blueprint
from agents.base import get_role_display_name

def strip_emojis(text: str) -> str:
    """Strip all emojis from text to guarantee clean Mermaid syntax parsing and professional diagram rendering."""
    if not text:
        return ""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"
        "\U00002600-\U000026FF"  # misc symbols
        "\U0001F900-\U0001F9FF"
        "\U0001FA70-\U0001FAFF"
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

def get_project_specific_diagram(project_details: dict, runs_map: dict, diag_choice: str) -> str:
    """
    Dynamically extract or generate a project-customized Mermaid diagram (strictly emoji-free).
    1. First checks if any completed agent run contains a valid Mermaid code block matching the diagram choice.
    2. If not found, dynamically synthesizes a project-tailored Mermaid diagram using project metadata.
    """
    proj_name = project_details.get('name', 'Project').strip()
    tech = project_details.get('tech_preference', 'Modern Tech Stack').strip()
    industry = project_details.get('industry', 'General').strip()

    clean_id = re.sub(r'[^a-zA-Z0-9]', '', proj_name) or "App"
    
    # 1. Search in agent runs markdown for dynamic Mermaid code blocks
    search_roles = []
    if "Database" in diag_choice or "ERD" in diag_choice:
        search_roles = ['database', 'architect', 'reviewer']
    elif "Authentication" in diag_choice or "Security" in diag_choice:
        search_roles = ['security', 'backend', 'architect', 'reviewer']
    else:
        search_roles = ['architect', 'reviewer', 'tech_lead', 'backend', 'database', 'frontend']

    for role in search_roles:
        if role in runs_map and runs_map[role].get('output_markdown'):
            content = runs_map[role]['output_markdown']
            mermaid_blocks = re.findall(r'```mermaid\s*(.*?)```', content, re.DOTALL)
            for block in mermaid_blocks:
                block_clean = strip_emojis(block.strip())
                if "ERD" in diag_choice or "Database" in diag_choice:
                    if "erDiagram" in block_clean:
                        return block_clean
                elif "Sequence" in diag_choice or "Authentication" in diag_choice:
                    if "sequenceDiagram" in block_clean:
                        return block_clean
                elif "Topology" in diag_choice or "Component" in diag_choice or "Flow" in diag_choice:
                    if "graph" in block_clean or "flowchart" in block_clean:
                        return block_clean

    # 2. Fallback: Dynamically synthesize custom Mermaid diagram using project metadata (Emoji-Free)
    if diag_choice == "High-Level System Topology":
        return f"""graph TD
    Client["Client Interface ({proj_name})"] --> Gateway["API Gateway / Router"]
    Gateway --> Auth["Authentication & RBAC Service"]
    Gateway --> CoreService["Core {industry} Service ({tech})"]
    CoreService --> Cache[("Redis In-Memory Cache")]
    CoreService --> PrimaryDB[("{proj_name} Primary DB")]
    CoreService --> AIModule[("AI & RAG Engine")]"""

    elif diag_choice == "User Authentication Flow":
        return f"""sequenceDiagram
    actor User as {proj_name} User
    User->>Client: Input Credentials ({proj_name})
    Client->>Gateway: POST /api/v1/auth/login
    Gateway->>Auth: Validate Credentials
    Auth->>DB: Query User Record ({industry})
    DB-->>Auth: Return Password Hash & User Roles
    Auth-->>Gateway: Generate JWT Token (Bearer)
    Gateway-->>Client: 200 OK + JWT Access Token
    Client-->>User: Load Customized {proj_name} Dashboard"""

    elif diag_choice == "Vector RAG Ingestion Pipeline":
        return f"""graph LR
    Input["Ingest Docs for {proj_name}"] --> Chunk["Recursive Text Chunker"]
    Chunk --> Embed["Embeddings API ({tech})"]
    Embed --> VectorDB[("Vector Store ({proj_name})")]
    VectorDB --> Retrieve["Similarity Match Search"]
    Retrieve --> AgentContext["Context-Aware AI Agent Prompt"]"""

    elif diag_choice == "Database Entity Relationship Diagram (ERD)":
        cid = clean_id.upper()
        return f"""erDiagram
    {cid}_USERS ||--o{{ {cid}_PROJECTS : "owns"
    {cid}_PROJECTS ||--o{{ {cid}_DATA : "contains"
    {cid}_PROJECTS ||--o{{ {cid}_LOGS : "records"

    {cid}_USERS {{
        string user_id PK
        string email
        string hashed_password
        string role
        timestamp created_at
    }}
    {cid}_PROJECTS {{
        string project_id PK
        string user_id FK
        string title
        string industry
        string tech_stack
    }}
    {cid}_DATA {{
        string record_id PK
        string project_id FK
        string payload_json
        string status
    }}
    {cid}_LOGS {{
        string log_id PK
        string project_id FK
        string agent_role
        string log_message
    }}"""

    elif diag_choice == "Component Architecture & Microservices":
        return f"""graph TD
    UI["Streamlit UI ({proj_name})"] --> Router["SPA Router & State Manager"]
    Router --> Orchestrator["LangGraph Multi-Agent Orchestrator"]
    Orchestrator --> BusinessLayer["Business & Requirements Layer ({industry})"]
    Orchestrator --> TechLayer["Architecture Layer ({tech})"]
    Orchestrator --> SecurityLayer["CSO & QA Audit Layer"]
    Orchestrator --> DB[(SQLite & Vector DB)]"""

    elif diag_choice == "Agent Workforce State Graph Workflow":
        return f"""graph LR
    CEO["CEO Agent"] --> BA["Business Analyst"]
    BA --> PM["Project Manager"]
    PM --> Arch["Lead Architect ({tech})"]
    Arch --> UIUX["UI/UX Designer"]
    UIUX --> FE["Frontend Engineer"]
    FE --> BE["Backend Engineer"]
    BE --> DB["Database Lead"]
    DB --> Sec["CSO Security"]
    Sec --> DevOps["DevOps Engineer"]
    DevOps --> QA["QA Lead"]
    QA --> Doc["Tech Writer"]
    Doc --> Rev["Systems Reviewer ({proj_name})"]"""

    elif diag_choice == "End-to-End Data Flow Diagram":
        return f"""graph TD
    UserSpec["User Prompt: {proj_name}"] --> DBInit["Create SQLite Record ({industry})"]
    DBInit --> VectorIndex["RAG Document Indexing"]
    VectorIndex --> ExecutionGraph["13-Agent State Graph Execution"]
    ExecutionGraph --> Persistence["Save Specs & Code Blueprints"]
    Persistence --> Studio["Live Implementation Studio & PDF Export"]"""

    elif diag_choice == "Security & Access Control Sequence Diagram":
        return f"""sequenceDiagram
    actor Admin as {proj_name} Admin
    Admin->>App: Update Security Policy ({industry})
    App->>DB: UPDATE app_settings table
    App->>Ollama: Check Local Server Health
    Ollama-->>App: 200 OK Response
    App-->>Admin: Display Security Audit Status"""

    return ""

def render_mermaid_in_streamlit(mermaid_code: str, element_id: str, height: int = 480):
    """Inject a container script with Mermaid CDN to render diagram blocks dynamically with interactive Pan & Zoom controls."""
    theme = st.session_state.get("theme", "light")
    
    if theme == "dark":
        background_color = "#0F172A"
        border_color = "#334155"
        shadow_color = "rgba(0,0,0,0.4)"
        mermaid_theme = "dark"
        primary_color = "#1E293B"
        text_color = "#F8FAFC"
        line_color = "#38BDF8"
        node_border = "#6366F1"
        cluster_bkg = "#1E293B"
        entity_bkg = "#1E293B"
        entity_stroke = "#6366F1"
    else:
        background_color = "#FFFFFF"
        border_color = "#CBD5E1"
        shadow_color = "rgba(0,0,0,0.06)"
        mermaid_theme = "default"
        primary_color = "#EFF6FF"
        text_color = "#0F172A"
        line_color = "#2563EB"
        node_border = "#3B82F6"
        cluster_bkg = "#F8FAFC"
        entity_bkg = "#EFF6FF"
        entity_stroke = "#2563EB"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <style>
        html, body {{
            background-color: {background_color};
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            color: {text_color};
            box-sizing: border-box;
            width: 100%;
            height: 100%;
        }}

        /* Dedicated Control Toolbar (Placed strictly above the diagram) */
        .diagram-toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 16px;
            background: {primary_color};
            border-bottom: 1.5px solid {border_color};
            box-sizing: border-box;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .toolbar-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .tool-btn {{
            background: {background_color};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 0.82rem;
            font-weight: 600;
            font-family: 'Inter', system-ui, sans-serif;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px {shadow_color};
        }}

        .tool-btn:hover {{
            border-color: {line_color};
            color: {line_color};
            transform: translateY(-1px);
        }}

        .tool-btn-primary {{
            background: {line_color};
            color: #FFFFFF !important;
            border: none;
        }}

        .tool-btn-primary:hover {{
            opacity: 0.9;
            color: #FFFFFF !important;
        }}

        .zoom-badge {{
            font-size: 0.8rem;
            font-weight: 700;
            color: {text_color};
            padding: 4px 10px;
            background: {background_color};
            border: 1px solid {border_color};
            border-radius: 12px;
            min-width: 48px;
            text-align: center;
        }}

        /* Diagram Viewport & Interactive Canvas */
        .diagram-viewport {{
            position: relative;
            width: 100%;
            height: calc(100vh - 54px);
            overflow: hidden;
            cursor: grab;
            background-color: {background_color};
            user-select: none;
        }}

        .diagram-viewport:active {{
            cursor: grabbing;
        }}

        .diagram-canvas {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            transform-origin: 0 0;
            transition: transform 0.05s ease-out;
        }}

        .mermaid {{
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            background: transparent !important;
        }}

        .mermaid svg {{
            max-width: none !important;
            max-height: none !important;
            display: block !important;
            margin: auto !important;
        }}

        /* High-Contrast Explicit ERD & Class Diagram Overrides */
        .er.entityBox, rect.entityBox, g.entityBox rect {{
            fill: {entity_bkg} !important;
            stroke: {entity_stroke} !important;
            stroke-width: 2px !important;
        }}
        .er.entityLabel, text.entityName, text.attributeName, text.er, g.entityBox text {{
            fill: {text_color} !important;
            color: {text_color} !important;
            font-size: 13px !important;
            font-weight: 600 !important;
        }}
        .er.relationshipLine, path.relationshipLine, path.er {{
            stroke: {line_color} !important;
            stroke-width: 2px !important;
        }}
        .er.relationshipLabel, text.relationshipLabel {{
            fill: {text_color} !important;
            font-size: 12px !important;
        }}
        </style>
    </head>
    <body>
        <div class="diagram-toolbar">
            <div class="toolbar-group">
                <button class="tool-btn" onclick="zoomIn()" title="Zoom In (or use mouse scroll wheel)">🔍 Zoom In</button>
                <button class="tool-btn" onclick="zoomOut()" title="Zoom Out (or use mouse scroll wheel)">🔍 Zoom Out</button>
                <button class="tool-btn" onclick="resetZoom()" title="Reset Zoom & Pan">🔄 Reset View</button>
                <span class="zoom-badge" id="zoom-text">100%</span>
            </div>
            <div class="toolbar-group">
                <button class="tool-btn tool-btn-primary" onclick="downloadPNG('{element_id}')">📷 Download PNG</button>
                <button class="tool-btn tool-btn-primary" onclick="downloadSVG('{element_id}')">📥 Download SVG</button>
            </div>
        </div>

        <div class="diagram-viewport" id="viewport-{element_id}">
            <div class="diagram-canvas" id="canvas-{element_id}">
                <div class="mermaid" id="mermaid-{element_id}">
{mermaid_code}
                </div>
            </div>
        </div>

        <script>
            var zoomScale = 1.0;
            var panX = 0;
            var panY = 0;
            var isDragging = false;
            var startX = 0;
            var startY = 0;

            var viewport = document.getElementById('viewport-{element_id}');
            var canvas = document.getElementById('canvas-{element_id}');
            var zoomBadge = document.getElementById('zoom-text');

            function updateTransform() {{
                canvas.style.transform = "translate(" + panX + "px, " + panY + "px) scale(" + zoomScale + ")";
                zoomBadge.innerText = Math.round(zoomScale * 100) + "%";
            }}

            function zoomIn() {{
                zoomScale = Math.min(zoomScale * 1.2, 5.0);
                updateTransform();
            }}

            function zoomOut() {{
                zoomScale = Math.max(zoomScale / 1.2, 0.2);
                updateTransform();
            }}

            function resetZoom() {{
                zoomScale = 1.0;
                panX = 0;
                panY = 0;
                updateTransform();
            }}

            // Mouse Scroll Wheel Zoom Listener
            viewport.addEventListener('wheel', function(e) {{
                e.preventDefault();
                var delta = e.deltaY < 0 ? 1.15 : 0.85;
                var newScale = Math.min(Math.max(zoomScale * delta, 0.2), 5.0);
                
                var rect = viewport.getBoundingClientRect();
                var mouseX = e.clientX - rect.left;
                var mouseY = e.clientY - rect.top;

                panX = mouseX - (mouseX - panX) * (newScale / zoomScale);
                panY = mouseY - (mouseY - panY) * (newScale / zoomScale);
                zoomScale = newScale;
                updateTransform();
            }}, {{ passive: false }});

            // Click & Drag Pan Listeners
            viewport.addEventListener('mousedown', function(e) {{
                if (e.button !== 0) return; // Left click only
                isDragging = true;
                startX = e.clientX - panX;
                startY = e.clientY - panY;
            }});

            window.addEventListener('mousemove', function(e) {{
                if (!isDragging) return;
                panX = e.clientX - startX;
                panY = e.clientY - startY;
                updateTransform();
            }});

            window.addEventListener('mouseup', function() {{
                isDragging = false;
            }});

            // SVG & PNG Export Functions
            function downloadSVG(filename) {{
                try {{
                    var svg = document.querySelector('.mermaid svg');
                    if (!svg) {{
                        alert("Diagram is rendering... Please wait a moment.");
                        return;
                    }}
                    var clone = svg.cloneNode(true);
                    var bbox = svg.getBBox ? svg.getBBox() : {{ width: 1000, height: 700 }};
                    var rect = svg.getBoundingClientRect();
                    var w = Math.ceil(rect.width || bbox.width || 1000) + 40;
                    var h = Math.ceil(rect.height || bbox.height || 700) + 40;

                    clone.setAttribute("width", w);
                    clone.setAttribute("height", h);
                    if (!clone.getAttribute("viewBox")) {{
                        clone.setAttribute("viewBox", "0 0 " + w + " " + h);
                    }}
                    clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");

                    var bg = '{background_color}';
                    var styleEl = document.createElementNS("http://www.w3.org/2000/svg", "style");
                    styleEl.textContent = "svg {{ background-color: " + bg + " !important; font-family: 'Inter', system-ui, sans-serif !important; }}";
                    clone.insertBefore(styleEl, clone.firstChild);

                    var serializer = new XMLSerializer();
                    var svgStr = serializer.serializeToString(clone);
                    var blob = new Blob([svgStr], {{type: "image/svg+xml;charset=utf-8"}});
                    var url = URL.createObjectURL(blob);
                    var link = document.createElement("a");
                    link.href = url;
                    link.download = (filename || "diagram") + "_architecture_diagram.svg";
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    setTimeout(function() {{ URL.revokeObjectURL(url); }}, 2000);
                }} catch(e) {{
                    console.error("SVG Download Error:", e);
                }}
            }}

            function downloadPNG(filename) {{
                try {{
                    var svg = document.querySelector('.mermaid svg');
                    if (!svg) {{
                        alert("Diagram is rendering... Please wait a moment.");
                        return;
                    }}

                    var bbox = svg.getBBox ? svg.getBBox() : {{ width: 1000, height: 700 }};
                    var rect = svg.getBoundingClientRect();
                    var width = Math.ceil(rect.width || bbox.width || 1000) + 60;
                    var height = Math.ceil(rect.height || bbox.height || 700) + 60;

                    var clone = svg.cloneNode(true);
                    clone.setAttribute("width", width);
                    clone.setAttribute("height", height);
                    if (!clone.getAttribute("viewBox")) {{
                        clone.setAttribute("viewBox", "0 0 " + width + " " + height);
                    }}
                    clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");

                    var bg = '{background_color}';
                    var styleEl = document.createElementNS("http://www.w3.org/2000/svg", "style");
                    styleEl.textContent = "svg {{ background-color: " + bg + " !important; font-family: 'Inter', system-ui, sans-serif !important; }}";
                    clone.insertBefore(styleEl, clone.firstChild);

                    var serializer = new XMLSerializer();
                    var svgString = serializer.serializeToString(clone);
                    var svgDataUrl = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgString);

                    var scale = 2; // High-resolution Retina export (2x)
                    var img = new Image();
                    img.crossOrigin = 'anonymous';

                    img.onload = function() {{
                        try {{
                            var canvas = document.createElement('canvas');
                            canvas.width = width * scale;
                            canvas.height = height * scale;
                            var ctx = canvas.getContext('2d');

                            ctx.fillStyle = bg;
                            ctx.fillRect(0, 0, canvas.width, canvas.height);
                            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                            var pngUrl = canvas.toDataURL("image/png");
                            var link = document.createElement("a");
                            link.href = pngUrl;
                            link.download = (filename || "diagram") + "_architecture_diagram.png";
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        }} catch(canvasErr) {{
                            downloadSVG(filename);
                        }}
                    }};

                    img.onerror = function() {{ downloadSVG(filename); }};
                    img.src = svgDataUrl;

                }} catch(e) {{
                    downloadSVG(filename);
                }}
            }}

            try {{
                mermaid.initialize({{ 
                    startOnLoad: true, 
                    theme: '{mermaid_theme}',
                    flowchart: {{ useMaxWidth: false, htmlLabels: true, curve: 'basis' }},
                    sequence: {{ useMaxWidth: false, showSequenceNumbers: false }},
                    gantt: {{ useMaxWidth: false }},
                    er: {{ useMaxWidth: false, htmlLabels: true }},
                    themeVariables: {{
                        darkMode: {'true' if theme == 'dark' else 'false'},
                        background: '{background_color}',
                        primaryColor: '{primary_color}',
                        primaryTextColor: '{text_color}',
                        primaryBorderColor: '{node_border}',
                        lineColor: '{line_color}',
                        textColor: '{text_color}',
                        nodeBorder: '{node_border}',
                        clusterBkg: '{cluster_bkg}',
                        clusterBorder: '{border_color}',
                        defaultLinkColor: '{line_color}',
                        titleColor: '{text_color}',
                        edgeLabelBackground: '{background_color}',
                        actorBkg: '{primary_color}',
                        actorBorder: '{node_border}',
                        actorTextColor: '{text_color}',
                        actorLineColor: '{line_color}',
                        signalColor: '{text_color}',
                        signalTextColor: '{text_color}',
                        labelBoxBkgColor: '{primary_color}',
                        labelBoxBorderColor: '{border_color}',
                        labelTextColor: '{text_color}',
                        loopTextColor: '{text_color}',
                        noteBkgColor: '{primary_color}',
                        noteTextColor: '{text_color}',
                        fontSize: '14px',
                        fontFamily: 'Inter, system-ui, sans-serif'
                    }}
                }});
            }} catch(e) {{
                console.error("Mermaid initialization error:", e);
            }}
        </script>
    </body>
    </html>
    """
    import urllib.parse
    data_url = "data:text/html;charset=utf-8," + urllib.parse.quote(html_code)
    st.iframe(data_url, height=height)

def show_projects():
    """Render the project listing and workspace blueprint explorer page."""
    st.html("<h1>Project Workspace Explorer</h1>")
    st.html("<p style='font-size: 1.1rem; color: var(--text-secondary); margin-top: -15px;'>Inspect blueprints, preview data flow structures, render Mermaid charts, and extract deliverables.</p>")

    
    # 1. Fetch available projects (Direct live query)
    try:
        projects = execute_query("SELECT * FROM projects ORDER BY created_at DESC")
    except Exception:
        projects = []
        
    if not projects:
        st.html(saas_card(
            "No Projects Active",
            "You haven't planned any applications yet. Go to the **New Project** page to construct your first project blueprint.",
            "Alert", "danger", "var(--danger-color)"
        ))
        return

    # Create workspace selector row with distinct project IDs and completion labels
    project_map = {p['id']: p for p in projects}
    project_ids = list(project_map.keys())
    
    # Session state workspace tracker
    if 'active_project_id' not in st.session_state or st.session_state['active_project_id'] not in project_map:
        st.session_state['active_project_id'] = project_ids[0]

    col_sel1, col_sel2 = st.columns([3.5, 1])
    with col_sel1:
        selected_proj_id = st.selectbox(
            f"Select Active Project Blueprint Workspace ({len(projects)} Total Projects Saved)",
            options=project_ids,
            format_func=lambda pid: f"📦 {project_map[pid]['name']} | {project_map[pid]['industry']} ({project_map[pid].get('created_at', '')[:10]})",
            index=project_ids.index(st.session_state['active_project_id'])
        )
        st.session_state['active_project_id'] = selected_proj_id
    with col_sel2:
        st.html("<div style='margin-top: 28px;'></div>")
        if st.button("🔄 Refresh Projects", use_container_width=True):
            st.rerun()

    project_details = project_map[selected_proj_id]
    active_id = project_details['id']

    # Fetch agent runs for active project
    agent_runs = execute_query(
        "SELECT * FROM agent_runs WHERE project_id = ? ORDER BY timestamp ASC",
        (active_id,)
    )
    runs_map = {r['agent_role'].lower(): r for r in agent_runs}

    # Header Card for active project
    st.html(f"""
    <div class="floating-os-panel" style="padding: 22px 28px; margin-bottom: 25px; border-radius: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
            <div>
                <span class="editorial-label" style="color: var(--primary-color);">Workspace Spec Package</span>
                <h2 style="margin: 4px 0 6px 0; font-size: 2.2rem;">{project_details['name']}</h2>
                <p style="color: var(--text-secondary); margin: 0; font-size: 0.98rem; max-width: 800px;">
                    {project_details['description']}
                </p>
            </div>
            <div>
                <span class="saas-badge saas-badge-success" style="font-size: 0.85rem; padding: 6px 14px;">
                    🟢 Blueprint Active
                </span>
            </div>
        </div>
        <div class="saas-divider" style="margin: 16px 0;"></div>
        <div style="display: flex; gap: 20px; font-size: 0.85rem; color: var(--text-secondary); flex-wrap: wrap;">
            <div><strong>Vertical:</strong> {project_details['industry']}</div>
            <div><strong>Complexity:</strong> {project_details['difficulty']}</div>
            <div><strong>Timeline:</strong> {project_details['timeline']}</div>
            <div><strong>Budget:</strong> {project_details['budget']}</div>
        </div>
    </div>
    """)
    
    # Tabs for Workspace Layout
    tab_docs, tab_diagrams, tab_impl, tab_exports, tab_delete = st.tabs([
        "📄 Agent Blueprints", 
        "📊 System Diagrams", 
        "🛠 Implementation Studio",
        "📥 Download Deliverables",
        "⚠️ Project Management"
    ])
    
    with tab_docs:
        if not agent_runs:
            st.warning("No agent blueprints are drafted for this project yet.")
            st.info("Click below to start the DevCore AI workforce and generate technical specifications for this project.")
            if st.button("🚀 Run AI Agent Workforce for this Project", type="primary"):
                with st.spinner("Synthesizing multi-agent specifications via Ollama..."):
                    from workflow.graph import run_project_planning
                    run_project_planning(
                        project_id=active_id,
                        project_name=project_details['name'],
                        description=project_details['description'],
                        industry=project_details['industry'],
                        tech_preference=project_details['tech_preference'],
                        budget=project_details['budget'],
                        timeline=project_details['timeline'],
                        difficulty=project_details['difficulty']
                    )
                st.success("🎉 Specifications successfully generated!")
                st.rerun()
        else:
            # 1. Blueprint Audit Checklist Status Row
            all_13_roles = [
                "ceo", "business_analyst", "project_manager", "architect", "ui_ux",
                "frontend", "backend", "database", "security", "devops", "qa",
                "documentation", "reviewer"
            ]
            completed_count = sum(1 for r in all_13_roles if r in runs_map)
            
            st.html(f"""
            <div class="saas-card" style="padding: 12px 20px; margin-bottom: 20px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="saas-badge saas-badge-success">Audit Verified</span>
                    <strong style="font-size: 0.9rem; color: var(--text-color);">13-Agent Blueprint Coverage: {completed_count} / 13 Completed</strong>
                </div>
                <span style="font-size: 0.8rem; color: var(--text-secondary);">Local LLM &middot; SQLite Synchronized</span>
            </div>
            """)
            
            # Engine Provider Selector for Regeneration
            try:
                from utils.config import get_execution_provider, update_env_file
                active_prov = get_execution_provider()
            except Exception:
                active_prov = "groq"
                def update_env_file(d): pass

            col_engine_sel, col_radio_view = st.columns([1.5, 2])
            with col_engine_sel:
                selected_engine = st.selectbox(
                    "⚡ Active Blueprint Engine Provider:",
                    options=["groq", "ollama"],
                    index=0 if active_prov == "groq" else 1,
                    format_func=lambda x: "⚡ Groq Cloud API" if x == "groq" else "🦙 Local Ollama Engine",
                    help="Choose whether Groq Cloud API or Local Laptop Ollama executes blueprint regeneration."
                )
                if selected_engine != active_prov:
                    execute_update("UPDATE settings SET value = ? WHERE key = 'execution_provider'", (selected_engine,))
                    update_env_file({"EXECUTION_PROVIDER": selected_engine})

            with col_radio_view:
                view_mode = st.radio(
                    "Blueprint View Mode",
                    ["Single Agent Layer", "Combined Overview (All 13 Blueprints)"],
                    horizontal=True
                )
            
            if view_mode == "Single Agent Layer":
                # Ensure pipeline order with CEO first
                roles_available = [r for r in all_13_roles if r in runs_map]
                if not roles_available:
                    roles_available = all_13_roles

                col_role_sel, col_role_reg = st.columns([2.5, 1])
                with col_role_sel:
                    selected_view_role = st.selectbox(
                        "Select Agent Blueprint Layer",
                        options=roles_available,
                        format_func=get_role_display_name
                    )
                with col_role_reg:
                    st.html("<div style='margin-top: 28px;'></div>")
                    regen_single_clicked = st.button(
                        f"🔄 Regenerate {get_role_display_name(selected_view_role)}",
                        use_container_width=True,
                        type="secondary"
                    )

                if regen_single_clicked:
                    with st.spinner(f"Regenerating live blueprint for {get_role_display_name(selected_view_role)} via AI Engine..."):
                        from agents.base import run_agent
                        state = {
                            'project_name': project_details['name'],
                            'description': project_details['description'],
                            'industry': project_details['industry'],
                            'tech_preference': project_details['tech_preference'],
                            'budget': project_details['budget'],
                            'timeline': project_details['timeline'],
                            'difficulty': project_details['difficulty']
                        }
                        run_agent(active_id, selected_view_role, state)
                    st.success(f"🎉 Regenerated {get_role_display_name(selected_view_role)} Blueprint!")
                    st.rerun()

                active_run = runs_map.get(selected_view_role.lower())
                
                st.markdown(f"### {get_role_display_name(selected_view_role)} Spec Sheet")
                if active_run:
                    st.html(f"<div style='font-size: 0.8rem; color: var(--text-secondary); margin-top: -10px; margin-bottom: 20px;'>Generated on: {active_run['timestamp']} | Execution: {active_run['execution_time_s']}s</div>")
                    if active_run['output_markdown'] and active_run['output_markdown'].strip():
                        st.markdown(active_run['output_markdown'])
                    else:
                        st.warning(f"Blueprint section for {get_role_display_name(selected_view_role)} is being generated...")
                else:
                    st.info(f"Blueprint content for {get_role_display_name(selected_view_role)} has not been generated yet.")
                    if st.button(f"⚡ Generate {get_role_display_name(selected_view_role)} Blueprint Now", type="primary"):
                        with st.spinner(f"Generating blueprint for {get_role_display_name(selected_view_role)}..."):
                            from agents.base import run_agent
                            state = {
                                'project_name': project_details['name'],
                                'description': project_details['description'],
                                'industry': project_details['industry'],
                                'tech_preference': project_details['tech_preference'],
                                'budget': project_details['budget'],
                                'timeline': project_details['timeline'],
                                'difficulty': project_details['difficulty']
                            }
                            run_agent(active_id, selected_view_role, state)
                        st.rerun()
            else:
                st.markdown("### Combined Technical Specification Package")
                col_all_reg1, col_all_reg2 = st.columns([3, 1])
                with col_all_reg2:
                    if st.button("⚡ Regenerate ALL 13 Blueprints", type="primary", use_container_width=True):
                        with st.spinner("Regenerating all 13 agent blueprints live via AI Engine..."):
                            from workflow.graph import run_project_planning
                            run_project_planning(
                                project_id=active_id,
                                project_name=project_details['name'],
                                description=project_details['description'],
                                industry=project_details['industry'],
                                tech_preference=project_details['tech_preference'],
                                budget=project_details['budget'],
                                timeline=project_details['timeline'],
                                difficulty=project_details['difficulty']
                            )
                        st.success("🎉 All 13 Agent Blueprints Regenerated Successfully!")
                        st.rerun()

                for role in all_13_roles:
                    role_title = get_role_display_name(role)
                    with st.expander(f"📌 {role_title} Blueprint Section", expanded=(role == "ceo")):
                        if role in runs_map and runs_map[role]['output_markdown']:
                            st.markdown(runs_map[role]['output_markdown'])
                        else:
                            st.info(f"Blueprint content for {role_title} is pending synthesis.")

    with tab_diagrams:
        st.markdown("### Dynamic System Architecture & Flowcharts")
        st.html("<p style='font-size: 0.9rem; color: var(--text-secondary); margin-top: -10px; margin-bottom: 20px;'>Natively compiled from your blueprint specs via Mermaid.js.</p>")
        
        diag_choice = st.selectbox(
            "Choose Architecture Diagram View",
            [
                "High-Level System Topology", 
                "User Authentication Flow", 
                "Vector RAG Ingestion Pipeline", 
                "Database Entity Relationship Diagram (ERD)",
                "Component Architecture & Microservices",
                "Agent Workforce State Graph Workflow",
                "End-to-End Data Flow Diagram",
                "Security & Access Control Sequence Diagram"
            ]
        )
        
        code = get_project_specific_diagram(project_details, runs_map, diag_choice)
        element_id = f"diag_{active_id[:8]}_{diag_choice.lower().replace(' ', '_').replace('&', 'and')}"
        render_mermaid_in_streamlit(code, element_id, height=460)
            
        d_cols = st.columns([2.5, 1])
        with d_cols[0]:
            with st.expander("🔍 View Raw Diagram Code & Syntax", expanded=False):
                st.code(code, language="mermaid")
        with d_cols[1]:
            st.download_button(
                label="📥 Download Diagram (MMD)",
                data=code,
                file_name=f"{diag_choice.lower().replace(' ', '_')}.mmd",
                mime="text/plain",
                use_container_width=True
            )
            
    with tab_impl:
        try:
            from components.implementation_studio import render_implementation_studio
            render_implementation_studio(active_id, project_details, agent_runs, runs_map)
        except Exception as e:
            import traceback
            st.error(f"Error rendering Implementation Studio: {e}")
            st.code(traceback.format_exc(), language="python")

    with tab_exports:
        st.markdown("### Export Specifications Package")
        st.html("<p style='font-size: 0.9rem; color: var(--text-secondary); margin-top: -10px; margin-bottom: 25px;'>Download compiled markdown workspace structures, report files or tabular task items.</p>")
        
        # 1. Compile ZIP bytes
        zip_bytes = package_project_blueprint_zip(project_details['name'], agent_runs)
        
        # 2. Compile PDF bytes
        pdf_bytes = build_pdf_blueprint(project_details['name'], agent_runs)
        
        col_down1, col_down2 = st.columns(2)
        with col_down1:
            st.html(saas_card(
                "Export PDF Specification",
                "Compiles all 13 agent blueprints into a unified design document with a bright, custom cover sheet using ReportLab.",
                "Consolidated Doc", "warning", "var(--warning-color)"
            ))
            st.download_button(
                label="Download Consolidated PDF",
                data=pdf_bytes,
                file_name=f"{project_details['name'].lower().replace(' ', '_')}_blueprint.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        with col_down2:
            st.html(saas_card(
                "Download ZIP Archive",
                "Includes all 13 workspace markdown segments, Mermaid UML charts, and a structured `tasks.json` agile backlog package.",
                "Specs Pack", "primary", "var(--primary-color)"
            ))
            st.download_button(
                label="Download Markdown ZIP Pack",
                data=zip_bytes,
                file_name=f"{project_details['name'].lower().replace(' ', '_')}_markdown.zip",
                mime="application/zip",
                use_container_width=True
            )
            
    with tab_delete:
        st.markdown("### Destructive Workspace Actions")
        st.html(saas_card(
            "Warning: Delete Workspace Blueprint",
            "This action deletes the selected project, uploaded SRS data segments, vectorized cache rows, and agent log history permanently. There is no undo.",
            "Destructive Action", "danger", "var(--danger-color)"
        ))
        
        confirm_del = st.checkbox("I confirm that I want to delete this workspace and its complete generated blueprint history.")
        if st.button("Delete Project Blueprint Permanent", disabled=not confirm_del):
            execute_update("DELETE FROM projects WHERE id = ?", (active_id,))
            st.success("Project workspace successfully wiped.")
            st.session_state.active_project_id = None
            st.session_state.current_page = "Projects"
            st.rerun()
            
    st.html("<div class='saas-divider'></div>")
