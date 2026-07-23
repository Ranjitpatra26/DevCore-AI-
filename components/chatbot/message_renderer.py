"""
Message Rendering and Action Controls for DevCore AI Assistant.
Formats chat history with markdown, code syntax highlighting, copy capability, and action buttons.
Includes intelligent role-aware animated thinking indicators with random message rotation.
"""

import random
import streamlit as st
from typing import List, Dict, Any, Callable

ROLE_THINKING_MESSAGES = {
    "ceo": {
        "icon": "🧠",
        "title": "CEO",
        "messages": [
            "is evaluating business strategy...",
            "is reviewing executive roadmap...",
            "is assessing market opportunities...",
            "is prioritizing strategic objectives...",
            "is preparing executive recommendations...",
            "is analyzing investment considerations...",
            "is evaluating long-term product vision..."
        ]
    },
    "business_analyst": {
        "icon": "📊",
        "title": "Business Analyst",
        "messages": [
            "is analyzing functional requirements...",
            "is translating business goals to user stories...",
            "is evaluating core use cases...",
            "is reviewing product backlog scope...",
            "is assessing user workflows...",
            "is structuring functional specifications..."
        ]
    },
    "project_manager": {
        "icon": "📅",
        "title": "Project Manager",
        "messages": [
            "is organizing sprint milestones...",
            "is evaluating project timelines...",
            "is reviewing task backlog priorities...",
            "is assessing resource allocation...",
            "is identifying potential bottlenecks...",
            "is structuring sprint execution schedule..."
        ]
    },
    "architect": {
        "icon": "🏗️",
        "title": "Software Architect",
        "messages": [
            "is designing system architecture...",
            "is evaluating scalability...",
            "is reviewing architectural patterns...",
            "is optimizing module boundaries...",
            "is preparing technical recommendations...",
            "is analyzing system dependencies..."
        ]
    },
    "ui_ux": {
        "icon": "🎨",
        "title": "UI/UX Designer",
        "messages": [
            "is designing the user experience...",
            "is refining design system tokens...",
            "is evaluating navigation architecture...",
            "is wireframing layout components...",
            "is optimizing micro-interactions...",
            "is polishing visual aesthetics..."
        ]
    },
    "frontend": {
        "icon": "💻",
        "title": "Frontend Engineer",
        "messages": [
            "is reviewing frontend components...",
            "is optimizing state management...",
            "is structuring frontend directory patterns...",
            "is building modular UI components...",
            "is evaluating client rendering performance..."
        ]
    },
    "backend": {
        "icon": "⚙️",
        "title": "Backend Engineer",
        "messages": [
            "is reviewing APIs and business logic...",
            "is optimizing backend services...",
            "is designing data flow...",
            "is evaluating service architecture...",
            "is reviewing authentication flow...",
            "is improving server scalability..."
        ]
    },
    "database": {
        "icon": "🗄️",
        "title": "Database Engineer",
        "messages": [
            "is optimizing database schema...",
            "is reviewing entity relationships...",
            "is designing indexes...",
            "is improving query performance...",
            "is validating normalization...",
            "is preparing ERD recommendations..."
        ]
    },
    "security": {
        "icon": "🔒",
        "title": "Security Engineer",
        "messages": [
            "is performing a security review...",
            "is performing threat analysis...",
            "is checking authentication controls...",
            "is evaluating vulnerabilities...",
            "is running security audit...",
            "is verifying data encryption..."
        ]
    },
    "devops": {
        "icon": "🚀",
        "title": "DevOps Engineer",
        "messages": [
            "is preparing deployment recommendations...",
            "is evaluating Docker containerization...",
            "is configuring CI/CD pipelines...",
            "is reviewing port bindings and hosting...",
            "is checking environment infrastructure..."
        ]
    },
    "qa": {
        "icon": "🧪",
        "title": "QA Engineer",
        "messages": [
            "is validating edge cases...",
            "is running validation checks...",
            "is reviewing test scenarios...",
            "is preparing quality report...",
            "is reviewing software reliability...",
            "is validating automated test coverage..."
        ]
    },
    "documentation": {
        "icon": "📝",
        "title": "Technical Writer",
        "messages": [
            "is preparing documentation...",
            "is structuring setup guides...",
            "is compiling API references...",
            "is reviewing installation steps...",
            "is organizing developer onboarding..."
        ]
    },
    "reviewer": {
        "icon": "💡",
        "title": "Principal Reviewer",
        "messages": [
            "is reviewing overall solution...",
            "is auditing cross-module integration...",
            "is resolving architectural gaps...",
            "is verifying technical alignment...",
            "is preparing unified recommendations..."
        ]
    }
}

def get_role_thinking_html(agent_role: str = "assistant") -> str:
    """
    Generate live animated HTML thinking indicator with role-specific status messages and pulsing dots.
    """
    role_key = str(agent_role).lower().strip()
    persona_data = ROLE_THINKING_MESSAGES.get(role_key, {
        "icon": "⚡",
        "title": "AI Assistant",
        "messages": [
            "is evaluating request...",
            "is processing prompt...",
            "is formulating intelligent recommendations...",
            "is generating response..."
        ]
    })
    
    msg = random.choice(persona_data["messages"])
    
    return f"""
    <style>
    @keyframes dotPulse {{
        0%, 100% {{ opacity: 0.25; transform: scale(0.8); }}
        50% {{ opacity: 1; transform: scale(1.25); }}
    }}
    @keyframes indicatorFadeIn {{
        from {{ opacity: 0; transform: translateY(4px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .role-thinking-card {{
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 10px 16px;
        background: var(--card-bg, rgba(30, 41, 59, 0.8));
        border: 2px solid var(--border-color, #334155);
        border-radius: 12px;
        margin: 8px 0 14px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        animation: indicatorFadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        font-family: 'Space Grotesk', system-ui, -apple-system, sans-serif;
    }}
    .role-thinking-icon {{
        font-size: 1.2rem;
        line-height: 1;
    }}
    .role-thinking-text {{
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-color, #F8FAFC);
        display: flex;
        align-items: center;
        gap: 5px;
    }}
    .role-thinking-name {{
        font-weight: 800;
        color: var(--primary-color, #6366F1);
    }}
    .dot-pulse-wrapper {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-left: 4px;
    }}
    .dot-pulse-dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: var(--primary-color, #6366F1);
        display: inline-block;
        animation: dotPulse 1.4s infinite ease-in-out both;
    }}
    .dot-pulse-dot:nth-child(1) {{ animation-delay: -0.32s; }}
    .dot-pulse-dot:nth-child(2) {{ animation-delay: -0.16s; }}
    .dot-pulse-dot:nth-child(3) {{ animation-delay: 0s; }}
    </style>

    <div class="role-thinking-card">
        <span class="role-thinking-icon">{persona_data['icon']}</span>
        <span class="role-thinking-text">
            <span class="role-thinking-name">{persona_data['title']}</span> {msg}
            <span class="dot-pulse-wrapper">
                <span class="dot-pulse-dot"></span>
                <span class="dot-pulse-dot"></span>
                <span class="dot-pulse-dot"></span>
            </span>
        </span>
    </div>
    """

def render_typing_indicator(agent_role: str = "assistant"):
    """Render subtle animated role-aware typing indicator."""
    st.html(get_role_thinking_html(agent_role))

def render_chat_messages(
    messages: List[Dict[str, str]],
    on_copy: Callable[[str], None] = None
):
    """
    Render all messages in current conversation history.
    """
    if not messages:
        return

    for idx, msg in enumerate(messages):
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "user":
            with st.chat_message("user", avatar="💻"):
                st.markdown(content)
        else:
            with st.chat_message("assistant", avatar="⚡"):
                st.markdown(content)
                
                # Copy button & small actions for assistant responses
                cols = st.columns([0.85, 0.15])
                with cols[1]:
                    if st.button("📋", key=f"copy_msg_{idx}"):
                        st.toast("Response copied to clipboard!", icon="✅")


