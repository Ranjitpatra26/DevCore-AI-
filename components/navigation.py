import streamlit as st
from database.connection import get_current_theme, toggle_theme_db
from components.ui import render_logo

def init_navigation_state():
    """Ensure navigation state variables exist in session state."""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    if "active_project_id" not in st.session_state:
        st.session_state.active_project_id = None
    if "theme" not in st.session_state:
        st.session_state.theme = get_current_theme()

def render_navigation():
    """Render high-contrast Neo-Brutalist navigation bar with logo, tabs, and floating theme switcher."""
    init_navigation_state()
    
    # 7 Columns: Logo + 6 page links centered
    cols = st.columns([2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    
    with cols[0]:
        st.html(render_logo())
        
    pages = [
        ("Dashboard", "Dashboard"),
        ("New Project", "New Project"),
        ("Projects", "Projects"),
        ("AI Team", "AI Team"),
        ("Chat", "Chat"),
        ("Settings", "Settings")
    ]
    
    for idx, (label, target) in enumerate(pages):
        with cols[idx + 1]:
            is_active = st.session_state.current_page == target
            btn_key = f"nav_btn_{target.lower().replace(' ', '_')}"
            
            if st.button(
                label,
                key=btn_key,
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_page = target
                st.rerun()

    # Floating Bottom-Right Theme Switcher Control
    current_theme = st.session_state.get("theme", "light")
    theme_label = "🌙" if str(current_theme).lower() == "light" else "☀️"
    
    if st.button(theme_label, key="floating_theme_toggle_btn"):
        new_theme = toggle_theme_db(current_theme)
        st.session_state.theme = new_theme
        from styles import inject_design_system_css
        inject_design_system_css(new_theme)
        st.rerun()

    st.html("<div class='saas-divider'></div>")


