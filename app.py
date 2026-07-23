# DevCore AI Autonomous Platform - Live Reload Trigger 2026
import os
import sys
import asyncio
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

import streamlit as st
from database.schema import init_db
from database.connection import get_current_theme
from components.navigation import render_navigation, init_navigation_state
from styles import inject_design_system_css
from pages.dashboard import show_dashboard
from pages.new_project import show_new_project
from pages.projects import show_projects
from pages.ai_team import show_ai_team
from pages.chat import show_chat
from pages.settings import show_settings

# 1. Page Configuration (Must be first call in Streamlit)
st.set_page_config(
    page_title="DevCore AI - Multi-Agent Software Planner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Database Auto-Migration / Seeding
init_db()

# Initialize session state theme if not present
if "theme" not in st.session_state:
    st.session_state.theme = get_current_theme()

# 3. Inject Centralized Design System Custom CSS Variables & Rules
inject_design_system_css(st.session_state.theme)

# 4. Initialize Navigation State & Render Navbar Component & Floating AI Chatbot
init_navigation_state()
render_navigation()
from components.chatbot import render_floating_chatbot
render_floating_chatbot()

# 5. SPA Route Map Handling
page = st.session_state.current_page

try:
    if page == "Dashboard":
        show_dashboard()
    elif page == "New Project":
        show_new_project()
    elif page == "Projects":
        show_projects()
    elif page == "AI Team":
        show_ai_team()
    elif page == "Chat":
        show_chat()
    elif page == "Settings":
        show_settings()
    else:
        st.session_state.current_page = "Dashboard"
        st.rerun()
except Exception as err:
    st.error(f"Routing Exception Encountered: {str(err)}")
    if st.button("Return to Safety Dashboard"):
        st.session_state.current_page = "Dashboard"
        st.rerun()

# 6. Clean & Professional Enterprise Footer
st.html("<div class='saas-divider' style='margin: 45px 0 25px 0;'></div>")

from utils.config import ensure_ollama_server_online
is_ollama_online = ensure_ollama_server_online()
ollama_dot = "🟢" if is_ollama_online else "🔴"
ollama_label = "Ollama Connected" if is_ollama_online else "Ollama Offline"
ollama_color = "#10B981" if is_ollama_online else "#EF4444"

st.html(f"""
<div class="enterprise-footer" style="
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 22px 28px;
    margin-bottom: 30px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    transition: border-color 0.2s ease;
">
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 20px;">
        
        <!-- Left Side: Brand & Metadata -->
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <span style="font-weight: 800; color: var(--text-color); font-family: 'Space Grotesk', sans-serif; font-size: 1.05rem; letter-spacing: -0.01em;">
                    DevCore AI
                </span>
                <span style="color: var(--text-secondary); font-size: 0.88rem; font-weight: 500;">
                    &bull; AI Software Engineering Operating System
                </span>
            </div>
            <div style="font-size: 0.78rem; color: var(--muted-color); font-weight: 500; letter-spacing: 0.01em;">
                Multi-Agent &bull; Local AI &bull; Knowledge Engine &bull; Built with Python
            </div>
        </div>

        <!-- Center: Platform Tag -->
        <div style="font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); font-family: 'Space Grotesk', sans-serif; background: var(--hover-bg); padding: 4px 14px; border-radius: 20px; border: 1px solid var(--border-color);">
            ⚡ Autonomous Multi-Agent OS
        </div>

        <!-- Right Side: Compact Status Chips -->
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span style="font-size: 0.74rem; font-weight: 600; color: var(--text-secondary); background: var(--hover-bg); border: 1px solid var(--border-color); padding: 3px 10px; border-radius: 14px; display: inline-flex; align-items: center; gap: 5px;">
                <span style="font-size: 0.6rem; color: #10B981;">🟢</span> AI Ready
            </span>
            <span style="font-size: 0.74rem; font-weight: 600; color: var(--text-secondary); background: var(--hover-bg); border: 1px solid var(--border-color); padding: 3px 10px; border-radius: 14px; display: inline-flex; align-items: center; gap: 5px;">
                <span style="font-size: 0.6rem; color: #10B981;">🟢</span> Local Runtime
            </span>
            <span style="font-size: 0.74rem; font-weight: 600; color: var(--text-secondary); background: var(--hover-bg); border: 1px solid var(--border-color); padding: 3px 10px; border-radius: 14px; display: inline-flex; align-items: center; gap: 5px;">
                <span style="font-size: 0.6rem; color: #10B981;">🟢</span> Knowledge Indexed
            </span>
            <span style="font-size: 0.74rem; font-weight: 600; color: var(--text-secondary); background: var(--hover-bg); border: 1px solid var(--border-color); padding: 3px 10px; border-radius: 14px; display: inline-flex; align-items: center; gap: 5px;">
                <span style="font-size: 0.6rem; color: {ollama_color};">{ollama_dot}</span> {ollama_label}
            </span>
    </div>
</div>
""")




