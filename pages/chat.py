import streamlit as st
from database.connection import execute_query, execute_update
from agents.base import get_role_display_name
from utils.ollama_client import query_ollama
from components.ui import saas_card

try:
    from components.chatbot.message_renderer import get_role_thinking_html
except Exception:
    def get_role_thinking_html(agent_role: str = "assistant") -> str:
        return """
        <div style="display: inline-flex; align-items: center; gap: 8px; padding: 8px 14px; background: var(--card-bg, #1E293B); border: 2px solid var(--border-color, #334155); border-radius: 10px; margin: 6px 0 12px 0;">
            <span style="font-weight: 700; color: var(--primary-color, #6366F1);">⚡ AI Specialist</span> is thinking...
        </div>
        """

CONSULTATION_ROLE_PERSONAS = {
    "ceo": {
        "title": "Chief Executive Officer (CEO)",
        "scope": "Business strategy, product vision, roadmap, target market, monetization, investment, and high-level architectural direction."
    },
    "business_analyst": {
        "title": "Lead Business Analyst",
        "scope": "Functional and non-functional requirements, user stories, user personas, product backlog, and business workflows."
    },
    "project_manager": {
        "title": "Project Manager (PM)",
        "scope": "Sprint planning, task backlog, execution roadmaps, timelines, resource allocation, and project risk management."
    },
    "architect": {
        "title": "Lead Software Architect",
        "scope": "Software architecture patterns, system design, technology stack selection, scalability, performance, and system topology."
    },
    "ui_ux": {
        "title": "Lead UI/UX Designer",
        "scope": "Design system tokens, visual identity, color palettes, typography, UI wireframes, user flows, and micro-interactions."
    },
    "frontend": {
        "title": "Senior Frontend Engineer",
        "scope": "Frontend code patterns, React/Streamlit components, state management, directory layout, and UI integration."
    },
    "backend": {
        "title": "Senior Backend Engineer",
        "scope": "REST API endpoint specifications, controller logic, session security, database integration, and server performance."
    },
    "database": {
        "title": "Lead Database Engineer",
        "scope": "Entity Relationship Diagrams (ERD), SQL DDL schema queries, table indexes, normalization, and database query performance."
    },
    "security": {
        "title": "Chief Security Officer (CSO)",
        "scope": "Threat modeling (STRIDE), OWASP top 10 security compliance, data encryption, access control, and vulnerability mitigations."
    },
    "devops": {
        "title": "DevOps Engineer",
        "scope": "Docker containerization, docker-compose configuration, CI/CD automated pipelines, hosting infrastructure, and monitoring."
    },
    "qa": {
        "title": "QA Engineer",
        "scope": "Testing strategy, test case coverage, test automation scripts, performance/load testing, and quality validation."
    },
    "documentation": {
        "title": "Technical Documentation Engineer",
        "scope": "Developer documentation, README setup guides, API reference docs, and installation troubleshooting."
    },
    "reviewer": {
        "title": "Principal Systems Reviewer",
        "scope": "Cross-module consistency, system integration audit, resolving technical gaps, and unified architectural sign-off."
    }
}

def show_chat():
    """Render the agent consultation chat terminal with persistent background blueprint context and memory."""
    
    st.html("""
    <div class="editorial-hero-container" style="padding: 36px 30px; margin-bottom: 30px;">
        <span class="editorial-label" style="display: block; margin-bottom: 8px;">⚡ Direct Specialist Communication</span>
        <h1 class="chat-terminal-title">Agent Consultation Terminal</h1>
        <p style="color: var(--text-secondary); margin: 0; font-size: 1.15rem; max-width: 650px;">
            Engage in continuous interactive consultation with specialized developer nodes. The generated blueprint acts as background knowledge context.
        </p>
    </div>
    """)
    
    # 1. Select active project workspace
    try:
        projects = execute_query("SELECT * FROM projects ORDER BY created_at DESC")
    except Exception:
        projects = []
        
    if not projects:
        st.html(saas_card(
            "No Active Project Workspace",
            "To chat with agents, please set up a project planning sheet first on the **New Project** page.",
            "Alert", "danger", "var(--danger-color)"
        ))
        return

    project_options = {p['name']: p['id'] for p in projects}
    
    default_idx = 0
    if st.session_state.active_project_id in project_options.values():
        default_idx = list(project_options.values()).index(st.session_state.active_project_id)
        
    col_sel1, col_sel2, col_sel3 = st.columns([2.2, 2.2, 1.2])
    with col_sel1:
        selected_name = st.selectbox(
            "Select Conversation Project Context",
            options=list(project_options.keys()),
            index=default_idx
        )
        active_id = project_options[selected_name]
        st.session_state.active_project_id = active_id
        
    with col_sel2:
        roles = [
            "ceo", "business_analyst", "project_manager", "architect", "ui_ux",
            "frontend", "backend", "database", "security", "devops", "qa",
            "documentation", "reviewer"
        ]
        selected_agent = st.selectbox(
            "Consult Agent Specialist Node",
            options=roles,
            format_func=get_role_display_name
        )

    with col_sel3:
        st.write("")
        st.write("")
        st.html("""
        <style>
        button[aria-label*="Clear Chat"] {
            background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
            color: #FFFFFF !important;
            border: 2.5px solid var(--border-color, #1E293B) !important;
            box-shadow: 3px 3px 0px 0px var(--border-color, #1E293B) !important;
            font-size: 0.92rem !important;
            font-weight: 800 !important;
            letter-spacing: 0.03em !important;
            padding: 8px 16px !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
        }
        button[aria-label*="Clear Chat"]:hover {
            transform: translate(-2px, -2px) !important;
            box-shadow: 5px 5px 0px 0px var(--border-color, #1E293B) !important;
            background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%) !important;
            color: #FFFFFF !important;
        }
        button[aria-label*="Clear Chat"] * {
            color: #FFFFFF !important;
        }
        </style>
        """)
        if st.button("🗑️ Clear Chat", key="clear_consultation_history"):
            execute_update(
                "DELETE FROM chats WHERE project_id = ? AND agent_role = ?",
                (active_id, selected_agent)
            )
            st.rerun()

    st.html("<div class='saas-divider'></div>")
    
    # Load Chat History from SQLite
    try:
        chat_history = execute_query(
            "SELECT sender, message, timestamp FROM chats WHERE project_id = ? AND agent_role = ? AND sender != 'system' ORDER BY id ASC",
            (active_id, selected_agent)
        )
    except Exception:
        chat_history = []
        
    # Render scrollable Chat Box
    chat_container = st.container()
    with chat_container:
        if chat_history:
            for msg in chat_history:
                is_user = msg['sender'] == 'user'
                align = 'right' if is_user else 'left'
                bg = 'var(--card-bg)'
                border_accent = 'var(--primary-color)' if is_user else 'var(--secondary-color)'
                sender_label = 'YOU (USER)' if is_user else get_role_display_name(selected_agent).upper()
                
                st.html(f"""
                <div style="background-color: {bg}; border: 3.5px solid var(--border-color); border-radius: 14px;
                            padding: 18px 24px; margin-bottom: 20px; max-width: 75%;
                            align-self: {'flex-end' if is_user else 'flex-start'};
                            float: {align}; clear: both;
                            box-shadow: var(--shadow-soft);
                            border-left: 8px solid {border_accent};">
                    <span style="font-size: 0.78rem; font-weight: 800; color: {border_accent}; letter-spacing: 0.08em; text-transform: uppercase; font-family: 'Space Grotesk', sans-serif;">{sender_label}</span>
                    <div style="font-size: 1rem; color: var(--text-color); margin-top: 8px; line-height: 1.6; white-space: pre-wrap; font-family: 'Outfit', sans-serif;">{msg['message']}</div>
                </div>
                """)
        else:
            persona = CONSULTATION_ROLE_PERSONAS.get(selected_agent, {"title": get_role_display_name(selected_agent), "scope": ""})
            st.html(saas_card(
                f"Consultation Terminal: {persona['title']}",
                f"Start an interactive consultation with the **{persona['title']}**. Focus area: *{persona['scope']}*. Ask specific questions about strategy, implementation, features, or trade-offs.",
                "Prompt", "info", "var(--primary-color)"
            ))

    st.html("<div style='clear: both; margin-bottom: 15px;'></div>")
    
    # Quick Consultation Suggestion Chips
    CONSULTATION_SUGGESTION_CHIPS = [
        "📊 What is your work status & completion %?",
        "🟢 What all features have been implemented?",
        "🔄 What tasks are currently in-progress?",
        "📌 What are your next steps & sprint goals?",
        "🛠️ Show technology stack & architecture choices",
        "🔒 Explain security & risk mitigations"
    ]

    st.html("""
    <div style="font-size: 0.82rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin: 10px 0 6px 0;">
        💡 Quick Node Consultation Suggestions:
    </div>
    """)
    chip_cols = st.columns(3)
    for idx, chip in enumerate(CONSULTATION_SUGGESTION_CHIPS):
        with chip_cols[idx % 3]:
            if st.button(chip, key=f"consult_chip_{idx}", use_container_width=True):
                st.session_state['pending_consultation_prompt'] = chip
                st.rerun()

    st.html("""
    <style>
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
        color: #FFFFFF !important;
        border: 3.5px solid var(--border-color) !important;
        box-shadow: 6px 6px 0px 0px var(--border-color) !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.06em !important;
        padding: 14px 24px !important;
        transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        transform: translate(-3px, -3px) !important;
        box-shadow: 9px 9px 0px 0px var(--border-color) !important;
        background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%) !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stFormSubmitButton"] button * {
        color: #FFFFFF !important;
    }
    </style>
    """)

    user_message = None
    if st.session_state.get('pending_consultation_prompt'):
        user_message = st.session_state['pending_consultation_prompt']
        st.session_state['pending_consultation_prompt'] = None
    else:
        with st.form(key="chat_input_form", clear_on_submit=True):
            form_input = st.text_input("Type your question or request changes...", key="chat_user_msg_input")
            send_btn = st.form_submit_button("⚡ Consult Specialist Node", use_container_width=True, type="primary")
            if send_btn and form_input.strip():
                user_message = form_input.strip()

    if user_message:
        persona = CONSULTATION_ROLE_PERSONAS.get(selected_agent, {
            "title": get_role_display_name(selected_agent),
            "scope": "Technical domain consultation and system guidance."
        })
            
        # 1. Insert User Message
        execute_update(
            "INSERT INTO chats (project_id, agent_role, sender, message) VALUES (?, ?, ?, ?)",
            (active_id, selected_agent, 'user', user_message)
        )
        
        # 2. Fetch Project Metadata & Build Consultation System Prompt & Context
        proj_data = {}
        try:
            p_res = execute_query("SELECT * FROM projects WHERE id = ?", (active_id,))
            if p_res:
                proj_data = p_res[0]
        except Exception:
            pass

        thinking_ph = st.empty()
        thinking_ph.html(get_role_thinking_html(selected_agent))

        system_prompt = f"""You are the active {persona['title']} working directly on the engineering team for the software project '{proj_data.get('name', 'Synchronized System')}'.

ROLE & DOMAIN SCOPE:
- Title: {persona['title']}
- Domain Focus: {persona['scope']}

CRITICAL PERSONA & CONVERSATION RULES:
1. STRICT NODE PERSONA ALIGNMENT: Speak specifically, authentically, and authoritatively as the {persona['title']}.
   - If you are the CEO, speak from executive business strategy, market growth, and strategic vision!
   - If you are the Software Architect, speak from system topology, component decoupling, and tech stack choices!
   - If you are the Database Engineer, speak from SQL schemas, ERDs, table indexing, and data integrity!
   - If you are the Backend Engineer, speak from REST API endpoints, router controllers, and payload validation!
   - If you are the UI/UX Designer, speak from design system tokens, visual hierarchy, and spatial layout!
   - If you are the CSO (Security), speak from STRIDE threat modeling, OWASP compliance, and zero cloud data leakage!
   - Maintain your domain focus for every specialist node.

2. WARM, ENCOURAGING, HUMAN-LIKE & EMOJI-RICH CONVERSATION:
   - Use warm, friendly, supportive, and human-like language with helpful emojis (e.g. 🚀, 💡, 🟢, 🎯, 🛠️, ✨, 🤝, 🙌, 👏, 📊, 🔒).
   - Be an enthusiastic senior technical co-founder and engineering partner who motivates the user and celebrates development milestones!

3. DEEP PROJECT RAG REFERENCE & CREATIVE KNOWLEDGE SYNTHESIS:
   - Reference the project metadata, your generated node blueprint summary, and Implementation Studio code files provided in context.
   - KNOWLEDGE GAP SYNTHESIS: If any detail, feature, or code is missing from the reference context, use your own vast domain intelligence and creative engineering insights to synthesize complete, brilliant answers for '{proj_data.get('name', 'Synchronized System')}'.

4. DIRECT & UNIVERSAL RESPONSE COVERAGE:
   - Answer WHATEVER the user asks directly (greetings like "hi" or "hello", work status & in-progress tasks breakdown, tech stack specs, or out-of-the-box domain questions).
   - Do NOT output generic static blueprint headers unless explicitly asked. Answer conversationally, concisely, and directly."""

        # 1. Fetch recent agent blueprint run output
        context_output = "No previous specification run recorded."
        try:
            runs = execute_query(
                "SELECT output_markdown FROM agent_runs WHERE project_id = ? AND agent_role = ? ORDER BY timestamp DESC LIMIT 1",
                (active_id, selected_agent)
            )
            if runs and runs[0].get('output_markdown'):
                context_output = runs[0]['output_markdown']
        except Exception:
            pass

        # 2. Fetch recent generated implementation code files
        code_context = "No implementation files generated yet."
        try:
            p_files = execute_query(
                "SELECT filename, file_type, content FROM project_files WHERE project_id = ? ORDER BY uploaded_at DESC LIMIT 3",
                (active_id,)
            )
            if p_files:
                file_summaries = [f"- File: `{f['filename']}` ({f['file_type']})" for f in p_files]
                code_context = "\n".join(file_summaries)
        except Exception:
            pass

        metadata_text = f"Project Name: {proj_data.get('name', 'N/A')}\nDescription: {proj_data.get('description', 'N/A')}\nTech Stack: {proj_data.get('tech_preference', 'N/A')}\nIndustry: {proj_data.get('industry', 'N/A')}"

        messages_payload = [
            {
                "role": "user",
                "content": f"BACKGROUND KNOWLEDGE CONTEXT (Reference Only):\n{metadata_text}\n\nNode Blueprint Summary ({persona['title']}):\n{context_output[:800]}\n\nImplementation Studio Code Files:\n{code_context}"
            },
            {
                "role": "assistant",
                "content": f"Understood! I have full active context for '{proj_data.get('name', 'Synchronized System')}', including our {persona['title']} blueprint and implementation files. As your senior engineering partner, I am ready to assist you!"
            }
        ]

        # Append past conversation history turns natively
        if chat_history:
            for turn in chat_history[-6:]:
                r = "user" if turn['sender'] == 'user' else "assistant"
                messages_payload.append({"role": r, "content": turn['message']})

        # Append latest user question
        messages_payload.append({"role": "user", "content": user_message})

        # Fetch active provider from settings
        provider = "ollama"
        groq_key = ""
        groq_model = "llama-3.3-70b-versatile"
        try:
            p_r = execute_query("SELECT value FROM settings WHERE key = 'chatbot_provider'")
            k_r = execute_query("SELECT value FROM settings WHERE key = 'groq_api_key_consultation'")
            if not k_r:
                k_r = execute_query("SELECT value FROM settings WHERE key = 'groq_api_key'")
            m_r = execute_query("SELECT value FROM settings WHERE key = 'groq_model'")
            if p_r and p_r[0].get('value'):
                provider = p_r[0]['value']
            if k_r and k_r[0].get('value'):
                groq_key = k_r[0]['value']
            if not groq_key:
                import os
                groq_key = os.getenv("GROQ_API_KEY_CONSULTATION") or os.getenv("GROQ_API_KEY") or ""
            if m_r and m_r[0].get('value'):
                groq_model = m_r[0]['value']
        except Exception:
            import os
            groq_key = os.getenv("GROQ_API_KEY_CONSULTATION") or os.getenv("GROQ_API_KEY") or ""


        from utils.config import ensure_ollama_server_online
        is_ollama_up = ensure_ollama_server_online()
        use_groq = (provider == "groq" or not is_ollama_up or os.getenv("EXECUTION_PROVIDER") == "groq") and bool(groq_key)

        if use_groq:
            from components.chatbot.groq_client import stream_groq_response
            res_chunks = list(stream_groq_response(
                messages=messages_payload,
                api_key=groq_key,
                model=groq_model,
                system_prompt=system_prompt
            ))
            agent_response = "".join(res_chunks).strip()
        else:
            agent_response = query_ollama(
                system_prompt=system_prompt,
                user_prompt=user_message,
                agent_role=selected_agent,
                is_consultation=True,
                project_name=proj_data.get('name', 'Synchronized System'),
                messages_payload=messages_payload
            )

        
        # Remove live thinking indicator as soon as generation completes
        thinking_ph.empty()

        # Clean up any accidental markdown title headers if generated by LLM
        if agent_response.startswith("# ") and "Blueprint" in agent_response.split("\n")[0]:
            lines = agent_response.split("\n")
            agent_response = "\n".join(lines[1:]).strip()

        # Insert Agent Response into SQLite chats table
        execute_update(
            "INSERT INTO chats (project_id, agent_role, sender, message) VALUES (?, ?, ?, ?)",
            (active_id, selected_agent, selected_agent, agent_response)
        )
        
        st.rerun()
