import os
import streamlit as st
from theme import get_theme_colors

def inject_design_system_css(theme_name: str):
    """Dynamically inject design variables and styles.css rules into Streamlit canvas."""
    colors = get_theme_colors(theme_name)
    
    # 1. Inject root properties matching active palette
    root_vars = f"""
    <style>
    :root {{
        --bg-color: {colors['bg_color']};
        --card-bg: {colors['card_bg']};
        --border-color: {colors['border_color']};
        --primary-color: {colors['primary_color']};
        --secondary-color: {colors['secondary_color']};
        --accent-color: {colors['accent_color']};
        --hover-bg: {colors['hover_bg']};
        --text-color: {colors['text_color']};
        --text-secondary: {colors['text_secondary']};
        --muted-color: {colors['muted_color']};
        --success-color: {colors['success_color']};
        --danger-color: {colors['danger_color']};
        --warning-color: {colors['warning_color']};
        --shadow-soft: {colors['shadow_soft']};
        --ai-team-gradient: {colors['ai_team_gradient']};
        --chat-terminal-gradient: {colors['chat_terminal_gradient']};
    }}
    </style>
    """
    st.html(root_vars)
    
    # 2. Load styles.css static sheet from file root
    css_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles.css")
    if os.path.exists(css_file_path):
        with open(css_file_path, "r", encoding="utf-8") as f:
            styles_content = f.read()
        st.html(f"<style>{styles_content}</style>")
    else:
        # Fallback if path resolved incorrectly
        st.html("<style>/* CSS file missing */</style>")

    # 3. Load dedicated neobrutalism.css stylesheet
    neobrutalism_css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles", "neobrutalism.css")
    if os.path.exists(neobrutalism_css_path):
        with open(neobrutalism_css_path, "r", encoding="utf-8") as f:
            neobrutalism_css_content = f.read()
        st.html(f"<style>{neobrutalism_css_content}</style>")

    # 4. Load dedicated chatbot.css stylesheet
    chatbot_css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles", "chatbot.css")
    if os.path.exists(chatbot_css_path):
        with open(chatbot_css_path, "r", encoding="utf-8") as f:
            chatbot_css_content = f.read()
        st.html(f"<style>{chatbot_css_content}</style>")



