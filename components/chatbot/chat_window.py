"""
Floating Chat Window Content for DevCore AI Assistant.
Renders terminal title bar, status pill, model selector, suggestion chips, message history, and chat form with Send button.
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from components.chatbot.ollama_client import check_ollama_connection, select_best_default_model, stream_ollama_response
from utils.ollama_client import get_ollama_config
from components.chatbot.prompt_templates import build_system_context
from components.chatbot.message_renderer import render_chat_messages, get_role_thinking_html

SUGGESTIONS = [
    "What are the core features of this project?",
    "Show the technology stack & tools used",
    "What is the development progress & status?",
    "Explain the system architecture overview",
    "What backend APIs & schemas are built?",
    "How is data security & privacy handled?"
]

def render_chat_window_content():
    """
    Render all chatbot controls inside the floating terminal popover window.
    """
    # 1. Initialize session states
    if "devcore_chat_messages" not in st.session_state:
        st.session_state.devcore_chat_messages = []
    if "devcore_chat_model" not in st.session_state:
        st.session_state.devcore_chat_model = None
    if "pending_suggestion" not in st.session_state:
        st.session_state.pending_suggestion = None

    # Retrieve configured Ollama URL (Local or Online/Remote)
    config = get_ollama_config()
    target_url = config.get("url", "http://localhost:11434")

    # Check Ollama status & available models
    is_online, available_models = check_ollama_connection(target_url)
    if is_online and available_models:
        if not st.session_state.devcore_chat_model or st.session_state.devcore_chat_model not in available_models:
            st.session_state.devcore_chat_model = select_best_default_model(available_models)

    # 2. Terminal Header Bar
    st.html("""
    <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #111827;
        padding: 8px 12px;
        border-radius: 10px;
        border: 1px solid #374151;
        margin-bottom: 10px;
    ">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="display: flex; gap: 5px;">
                <span style="width: 10px; height: 10px; border-radius: 50%; background: #EF4444; display: inline-block;"></span>
                <span style="width: 10px; height: 10px; border-radius: 50%; background: #F59E0B; display: inline-block;"></span>
                <span style="width: 10px; height: 10px; border-radius: 50%; background: #10B981; display: inline-block;"></span>
            </div>
            <span style="font-weight: 700; font-size: 0.88rem; color: #F9FAFB; font-family: monospace;">
                >_ DevCore AI Terminal
            </span>
        </div>
    </div>
    """)

    # Check active provider from SQLite settings
    active_provider = "ollama"
    active_groq_key = ""
    active_groq_model = "llama-3.3-70b-versatile"
    try:
        from database.connection import execute_query
        p_r = execute_query("SELECT value FROM settings WHERE key = 'chatbot_provider'")
        k_r = execute_query("SELECT value FROM settings WHERE key = 'groq_api_key'")
        m_r = execute_query("SELECT value FROM settings WHERE key = 'groq_model'")
        if p_r and p_r[0].get('value'):
            active_provider = p_r[0]['value']
        if k_r and k_r[0].get('value'):
            active_groq_key = k_r[0]['value']
        if not active_groq_key:
            import os
            active_groq_key = os.getenv("GROQ_API_KEY_CHATBOT") or os.getenv("GROQ_API_KEY") or ""
        if m_r and m_r[0].get('value'):
            active_groq_model = m_r[0]['value']
    except Exception:
        import os
        active_groq_key = os.getenv("GROQ_API_KEY_CHATBOT") or os.getenv("GROQ_API_KEY") or ""


    # 3. Model Selector & Status Pill
    hdr_cols = st.columns([1.5, 2.5])
    with hdr_cols[0]:
        if (active_provider == "groq" or not is_online or os.getenv("EXECUTION_PROVIDER") == "groq") and active_groq_key:
            st.html("""
            <span style="font-size: 0.74rem; font-weight: 700; color: #38BDF8; background: rgba(56,189,248,0.15); padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(56,189,248,0.3); display: inline-flex; align-items: center; gap: 4px;">
                ⚡ Groq LPU Active
            </span>
            """)
        elif is_online:
            st.html("""
            <span style="font-size: 0.74rem; font-weight: 600; color: #10B981; background: rgba(16,185,129,0.15); padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(16,185,129,0.3); display: inline-flex; align-items: center; gap: 4px;">
                🟢 Local AI Ready
            </span>
            """)
        else:
            st.html("""
            <span style="font-size: 0.74rem; font-weight: 600; color: #EF4444; background: rgba(239,68,68,0.15); padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(239,68,68,0.3); display: inline-flex; align-items: center; gap: 4px;">
                🔴 Ollama Offline
            </span>
            """)

    with hdr_cols[1]:
        if (active_provider == "groq" or not is_online or os.getenv("EXECUTION_PROVIDER") == "groq") and active_groq_key:
            from components.chatbot.groq_client import AVAILABLE_GROQ_MODELS
            selected_groq = st.selectbox(
                "Groq Model",
                options=AVAILABLE_GROQ_MODELS,
                index=AVAILABLE_GROQ_MODELS.index(active_groq_model) if active_groq_model in AVAILABLE_GROQ_MODELS else 0,
                key="devcore_popover_groq_model_selector",
                label_visibility="collapsed"
            )
            if selected_groq != active_groq_model:
                try:
                    from database.connection import execute_update
                    execute_update("UPDATE settings SET value = ? WHERE key = 'groq_model'", (selected_groq,))
                    st.rerun()
                except Exception:
                    pass
        elif is_online and available_models:
            selected_model = st.selectbox(
                "Model",
                options=available_models,
                index=available_models.index(st.session_state.devcore_chat_model) if st.session_state.devcore_chat_model in available_models else 0,
                key="devcore_popover_model_selector",
                label_visibility="collapsed"
            )
            st.session_state.devcore_chat_model = selected_model
        else:
            st.html("<span style='color: #94A3B8; font-size: 0.8rem;'>No Ollama models found</span>")

    st.html("<div style='height: 1px; background: #374151; margin: 10px 0;'></div>")

    # 4. Instant Suggestion Chips (if chat empty)
    if len(st.session_state.devcore_chat_messages) == 0:
        st.html("""
        <div style="font-size: 0.78rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin: 6px 0 8px 0;">
            💡 Instant Project Insights:
        </div>
        """)
        chip_cols = st.columns(2)
        for i, chip_text in enumerate(SUGGESTIONS):
            with chip_cols[i % 2]:
                if st.button(f"⚡ {chip_text}", key=f"pop_chip_{i}", use_container_width=True):
                    st.session_state.pending_suggestion = chip_text
                    st.rerun()

    # 5. Clear / Retry Action Buttons (if history exists)
    if len(st.session_state.devcore_chat_messages) > 0:
        act_cols = st.columns([1, 1, 2])
        with act_cols[0]:
            if st.button("🗑️ Clear", key="pop_clear_chat", use_container_width=True):
                st.session_state.devcore_chat_messages = []
                st.rerun()
        with act_cols[1]:
            if st.button("🔄 Retry", key="pop_retry_chat", use_container_width=True):
                if len(st.session_state.devcore_chat_messages) >= 2:
                    if st.session_state.devcore_chat_messages[-1]["role"] == "assistant":
                        st.session_state.devcore_chat_messages.pop()
                        st.session_state.pending_suggestion = st.session_state.devcore_chat_messages[-1]["content"]
                        st.session_state.devcore_chat_messages.pop()
                        st.rerun()

    # 6. Terminal Scrollable Chat Messages Container (Height: 165 for top clearance)
    msg_container = st.container(height=165)
    with msg_container:
        render_chat_messages(st.session_state.devcore_chat_messages)



    # 7. Terminal Input Form with Send Button
    prompt = None
    if st.session_state.pending_suggestion:
        prompt = st.session_state.pending_suggestion
        st.session_state.pending_suggestion = None
    else:
        with st.form(key="devcore_terminal_chat_form", clear_on_submit=True):
            f_cols = st.columns([3.4, 1.0])
            with f_cols[0]:
                user_input = st.text_input(
                    "Prompt",
                    placeholder="Ask architecture, schema, codebase...",
                    key="devcore_popover_text_input",
                    label_visibility="collapsed"
                )
            with f_cols[1]:
                submit_btn = st.form_submit_button("Send ➔", use_container_width=True, type="primary")
            if submit_btn and user_input.strip():
                prompt = user_input.strip()

    # 8. Stream Ollama Response
    if prompt:
        st.session_state.devcore_chat_messages.append({"role": "user", "content": prompt})
        with msg_container:
            with st.chat_message("user", avatar="💻"):
                st.markdown(prompt)

        with msg_container:
            with st.chat_message("assistant", avatar="⚡"):
                # Fetch active Groq API key & provider
                groq_key = ""
                groq_model = "llama-3.3-70b-versatile"
                provider = "groq"
                try:
                    from database.connection import execute_query
                    p_row = execute_query("SELECT value FROM settings WHERE key = 'chatbot_provider'")
                    k_row = execute_query("SELECT value FROM settings WHERE key = 'groq_api_key_chatbot'")
                    if not k_row or not k_row[0].get('value'):
                        k_row = execute_query("SELECT value FROM settings WHERE key = 'groq_api_key'")
                    m_row = execute_query("SELECT value FROM settings WHERE key = 'groq_model'")
                    if p_row and p_row[0].get('value'):
                        provider = p_row[0]['value']
                    if k_row and k_row[0].get('value'):
                        groq_key = k_row[0]['value']
                    if not groq_key:
                        groq_key = os.getenv("GROQ_API_KEY_CHATBOT") or os.getenv("GROQ_API_KEY") or ""
                    if m_row and m_row[0].get('value'):
                        groq_model = m_row[0]['value']
                except Exception:
                    groq_key = os.getenv("GROQ_API_KEY_CHATBOT") or os.getenv("GROQ_API_KEY") or ""

                use_groq = (provider == "groq" or not is_online or os.getenv("EXECUTION_PROVIDER") == "groq") and bool(groq_key)

                if not is_online and not use_groq:
                    err_msg = f"⚠️ **Groq API Key Required**: Please enter your Groq API key in **Settings** or your `.env` file to enable cloud responses."
                    st.markdown(err_msg)
                    st.session_state.devcore_chat_messages.append({"role": "assistant", "content": err_msg})
                else:
                    thinking_ph = st.empty()
                    thinking_ph.html(get_role_thinking_html("assistant"))

                    system_prompt = build_system_context(user_prompt=prompt, active_project_id=st.session_state.get("active_project_id"))

                    if use_groq:
                        from components.chatbot.groq_client import stream_groq_response
                        response_stream = stream_groq_response(
                            messages=st.session_state.devcore_chat_messages,
                            api_key=groq_key,
                            model=groq_model,
                            system_prompt=system_prompt,
                            is_chatbot=True
                        )
                    else:
                        active_model = st.session_state.devcore_chat_model or "qwen3.5:9b"
                        response_stream = stream_ollama_response(
                            messages=st.session_state.devcore_chat_messages,
                            model=active_model,
                            url=target_url,
                            system_prompt=system_prompt
                        )

                    full_response = st.write_stream(response_stream)
                    thinking_ph.empty()
                    st.session_state.devcore_chat_messages.append({"role": "assistant", "content": full_response})
                    st.rerun()

def render_chat_window():
    """Fallback export for compatibility."""
    render_chat_window_content()
