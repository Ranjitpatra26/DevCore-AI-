"""
Floating Button Controller & Entry Point for DevCore AI Assistant Chatbot.
Injects chatbot styles and mounts fixed circular popover trigger button at bottom-right.
"""

import os
import streamlit as st
from components.chatbot.chat_window import render_chat_window_content

def inject_chatbot_css():
    """Inject dedicated chatbot CSS stylesheet into DOM."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "..", "styles", "chatbot.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.html(f"<style>{f.read()}</style>")

def render_floating_chatbot():
    """
    Main isolated entry point for the DevCore AI Floating Assistant Chatbot.
    Renders fixed circular popover trigger button directly above theme switcher.
    Uses st.popover to natively contain the entire terminal popup window.
    """
    inject_chatbot_css()

    with st.popover("🤖", key="devcore_chatbot_popover", help=None):
        render_chat_window_content()
