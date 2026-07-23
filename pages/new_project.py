import uuid
import streamlit as st
from database.connection import execute_update
from rag.vector_store import index_project_file
from workflow.graph import run_project_planning
from components.ui import saas_card

def show_new_project():
    """Render the project planning builder form as a spatial wizard studio."""
    
    st.html("""
    <div class="floating-os-panel rotated-panel-left" style="padding: 22px 28px; margin-bottom: 16px; margin-top: -10px;">
        <span class="editorial-label" style="display: block; margin-bottom: 4px;">⚡ Spatial Project Initialization Studio</span>
        <h1 style="margin: 4px 0 6px 0; font-size: 3.2rem; line-height: 1.1;">Architect New Software Blueprint</h1>
        <p style="color: var(--text-secondary); margin: 0; font-size: 1.1rem; max-width: 700px; line-height: 1.5;">
            Specify your software vision and target architecture parameters below. The DevCore AI workforce will formulate full technical specs, database schemas, and API code.
        </p>
    </div>
    """)
    
    # Form Container
    with st.container():
        # STEP 1: Core Vision & Identity
        st.html("""
        <div class="floating-os-panel rotated-panel-right" style="padding: 16px 20px; margin-bottom: 16px;">
            <div style="border-left: 5px solid var(--primary-color); padding-left: 14px;">
                <span class="editorial-label" style="color: var(--primary-color);">Step 01 &bull; System Scope</span>
                <h3 style="margin: 2px 0 0 0;">Product Intent & Requirements</h3>
            </div>
        </div>
        """)
        
        col1, col2 = st.columns([1.2, 1.8])
        with col1:
            project_name = st.text_input("Project Blueprint Name", value="", placeholder="e.g. DevCore AI Workspace Desktop App")
            industry = st.selectbox("Industry Vertical", ["Technology", "Healthcare", "Finance", "Education", "E-commerce", "Logistics", "Entertainment", "Real Estate"])
        with col2:
            description = st.text_area("Detailed Software Description", height=135, placeholder="Explain the primary features, workflows, target audience, and business intent of your application...")

        st.html("<div style='margin-bottom: 30px;'></div>")

        # STEP 2: Architecture & Constraints
        st.html("""
        <div class="floating-os-panel rotated-panel-left" style="padding: 28px; margin-bottom: 25px;">
            <div style="border-left: 6px solid var(--secondary-color); padding-left: 18px;">
                <span class="editorial-label" style="color: var(--secondary-color);">Step 02 &bull; Technical Constraints</span>
                <h3 style="margin: 4px 0 0 0;">Tech Stack & Execution Schedules</h3>
            </div>
        </div>
        """)
        
        col3, col4, col5, col6 = st.columns(4)
        with col3:
            tech_preference = st.text_input("Tech Stack Preferences", value="", placeholder="e.g. Streamlit, Python, SQLite, Ollama")
        with col4:
            difficulty = st.selectbox("Implementation Complexity", ["Beginner", "Intermediate", "Advanced", "Enterprise Scale"])
        with col5:
            budget = st.selectbox("Estimated Budget Tier", ["Low ($5K - $15K)", "Medium ($15K - $50K)", "High ($50K - $150K)", "Enterprise ($150K+)"])
        with col6:
            timeline = st.selectbox("Target Delivery Schedule", ["1 Month (MVP)", "3 Months (Standard)", "6 Months (Robust)", "12+ Months (Enterprise)"])

        # STEP 3: Context & RAG Files
        st.html("""
        <div class="floating-os-panel" style="padding: 28px; margin-bottom: 25px;">
            <div style="border-left: 6px solid var(--accent-color); padding-left: 18px;">
                <span class="editorial-label" style="color: var(--accent-color);">Step 03 &bull; Context Documents</span>
                <h3 style="margin: 4px 0 0 0;">Attach Project Specs & Datasets</h3>
            </div>
        </div>
        """)
        
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            srs_file = st.file_uploader("SRS Document", type=["pdf", "docx", "txt", "md"])
        with col_f2:
            readme_file = st.file_uploader("README Spec", type=["pdf", "docx", "txt", "md"])
        with col_f3:
            docs_file = st.file_uploader("Design Docs", type=["pdf", "docx", "txt", "md"])
        with col_f4:
            dataset_file = st.file_uploader("Dataset (CSV / Excel)", type=["csv", "xlsx", "xls"])

        st.html("<div style='margin-top: 30px;'></div>")
        
        # Explicit Engine Selector Dropdown - Centered & Mid-Sized Right Before Execution Button
        try:
            from utils.config import get_execution_provider
        except Exception:
            def get_execution_provider():
                import os
                return os.getenv("EXECUTION_PROVIDER", "ollama")

        current_prov = get_execution_provider()
        
        c_pad1, c_mid_engine, c_pad2 = st.columns([1, 2.2, 1])
        with c_mid_engine:
            exec_engine_choice = st.selectbox(
                "⚡ Select Blueprint Generation Engine Provider:",
                options=["ollama", "groq"],
                index=0 if current_prov == "ollama" else 1,
                format_func=lambda x: "🦙 Local Ollama Engine (Uncapped Laptop Power & 8K Tokens)" if x == "ollama" else "⚡ Groq Cloud API (High-Speed Deployed Cloud Engine)",
                help="Choose whether local laptop Ollama or Groq Cloud API generates the 13-node blueprints."
            )

        st.html("<div style='margin-top: 20px;'></div>")

        # Action Trigger
        generate_clicked = st.button("Initialize Multi-Agent Drafting Sequence", use_container_width=True, type="primary")
        
        if generate_clicked:
            if not project_name.strip() or not description.strip():
                st.error("Project Blueprint Name and Detailed Description are required to initialize the CEO vision node.")
                return

            # Save chosen execution provider preference
            from utils.config import update_env_file
            execute_update("UPDATE settings SET value = ? WHERE key = 'execution_provider'", (exec_engine_choice,))
            update_env_file({"EXECUTION_PROVIDER": exec_engine_choice})

            project_id = str(uuid.uuid4())
            
            # 1. Save Project in SQLite Database
            try:
                execute_update(
                    """
                    INSERT INTO projects (id, name, description, industry, tech_preference, budget, timeline, difficulty, model_used)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (project_id, project_name, description, industry, tech_preference, budget, timeline, difficulty, exec_engine_choice)
                )
            except Exception as e:
                st.error(f"Failed to initialize SQLite Project entry: {str(e)}")
                return
                
            # 2. Parse and Index Uploaded RAG Files
            files_indexed = 0
            file_upload_configs = [
                (srs_file, "SRS"),
                (readme_file, "README"),
                (docs_file, "ExistingDocs"),
                (dataset_file, "Dataset")
            ]
            
            for file_obj, doc_type in file_upload_configs:
                if file_obj is not None:
                    file_bytes = file_obj.read()
                    filename = file_obj.name
                    index_project_file(project_id, filename, doc_type, file_bytes)
                    files_indexed += 1
            
            st.toast(f"Saved project metadata. Indexed {files_indexed} background document attachments.")
            
            # 3. Create placeholders for progress bar, status, and running logs
            st.html("<div class='saas-divider'></div>")
            st.html("<h2>AI Workforce Execution Console</h2>")
            
            import time
            start_timestamp = time.time()
            
            progress_container = st.empty()
            logs_container = st.empty()
            
            log_entries = []
            
            def update_progress_ui(role: str, percent: int, log_text: str):
                elapsed_s = int(time.time() - start_timestamp)
                
                # Dynamic adaptive countdown calculation based on actual parallel execution speed
                if percent > 0:
                    est_total_s = max(50, int(elapsed_s / (percent / 100.0)))
                else:
                    est_total_s = 60
                
                rem_s = max(0, est_total_s - elapsed_s) if percent < 100 else 0
                
                mins_elapsed, secs_elapsed = divmod(elapsed_s, 60)
                mins_rem, secs_rem = divmod(rem_s, 60)
                
                time_badge = f"⏱️ Elapsed: {mins_elapsed:02d}m {secs_elapsed:02d}s | ⏳ Countdown: {mins_rem:02d}m {secs_rem:02d}s remaining"
                
                role_display = {
                    "ceo": "CEO Strategic Planner",
                    "business_analyst": "Business Requirements Analyst",
                    "project_manager": "Project Backlog Manager",
                    "architect": "Lead Software Architect",
                    "ui_ux": "Product & Wireframe Designer",
                    "frontend": "Lead Frontend Engineer",
                    "backend": "Lead Backend Engineer",
                    "database": "Database Administrator",
                    "security": "Security Analyst",
                    "devops": "DevOps Engineer",
                    "qa": "QA Test Specialist",
                    "documentation": "Technical Writer",
                    "reviewer": "Senior Code Reviewer"
                }.get(role.lower(), role)
                
                log_entries.append(f"[{percent}%] [{role_display}] {log_text} ({mins_elapsed}m {secs_elapsed}s)")
                
                with progress_container.container():
                    st.html(f"""
                    <div class="floating-os-panel" style="margin-bottom: 20px; padding: 22px; border-radius: 14px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span class="editorial-label" style="font-size: 0.92rem; font-weight: 700; color: var(--primary-color);">⚡ ACTIVE NODE: {role_display.upper()}</span>
                            <span style="font-weight: 800; font-family: 'Space Grotesk', sans-serif; font-size: 1.15rem; color: var(--text-color);">{percent}%</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
                            <span style="font-size: 0.88rem; color: var(--text-secondary); font-weight: 500;">
                                Synthesizing multi-agent specifications... Node: <strong style="color: var(--text-color);">{role_display}</strong>
                            </span>
                            <span style="font-size: 0.82rem; font-weight: 700; color: var(--text-color); background: var(--hover-bg); padding: 4px 12px; border-radius: 20px; border: 1px solid var(--border-color);">
                                {time_badge}
                            </span>
                        </div>
                        <div class="nb-progress-container">
                            <div class="nb-progress-fill" style="width: {percent}%;"></div>
                            <div class="nb-progress-text">{percent}% Completed</div>
                        </div>
                    </div>
                    """)
                    
                with logs_container.container():
                    logs_html = "<div class='terminal-console' style='height: 220px; overflow-y: auto; padding: 14px; font-family: monospace; font-size: 0.85rem;'>" + "<br/>".join(log_entries[-10:]) + "</div>"
                    st.html(logs_html)
                    
            # Run the multi-agent graph computation synchronously with live progress UI
            final_state = run_project_planning(
                project_id=project_id,
                project_name=project_name,
                description=description,
                industry=industry,
                tech_preference=tech_preference,
                budget=budget,
                timeline=timeline,
                difficulty=difficulty,
                progress_callback=update_progress_ui
            )
                
            st.success("🎉 Production specification package compiled! Proceeding to project workspace.")
            st.session_state.active_project_id = project_id
            st.session_state.current_page = "Projects"
            st.rerun()
