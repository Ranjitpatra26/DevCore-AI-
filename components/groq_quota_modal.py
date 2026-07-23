"""
Groq API Quota & Rate Limit Modal Dialog Component for DevCore AI.
Provides step-by-step instructions for getting a free Groq API key and an interactive form for all 4 Groq API keys.
Guarantees 100% centered modal positioning, high-contrast text, and zero color visibility issues.
"""

import os
import streamlit as st
from database.connection import execute_query, execute_update
from utils.config import update_env_file

def mask_api_key(key: str) -> str:
    """Mask key for privacy display."""
    if not key or not key.strip():
        return ""
    k = key.strip()
    if len(k) <= 8:
        return "••••••••"
    return f"{k[:4]}••••••••{k[-4:]}"

def render_groq_quota_modal_content():
    """Render the step-by-step guide and 4-key update form with high contrast CSS."""
    st.html("""
    <style>
    /* Centering & Contrast Fixes for Dialog Pop-up Container */
    div[data-testid="stDialog"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stDialog"] > div:first-child,
    div[role="dialog"] {
        background: var(--card-bg, #0F172A) !important;
        border: 2px solid var(--border-color, #334155) !important;
        border-radius: 18px !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.45) !important;
        max-width: 680px !important;
        width: 92vw !important;
        padding: 24px !important;
        color: var(--text-color, #F8FAFC) !important;
        margin: auto !important;
        overflow-x: hidden !important;
    }

    /* Modal Text Formatting */
    .groq-modal-wrapper,
    .groq-modal-wrapper h1,
    .groq-modal-wrapper h2,
    .groq-modal-wrapper h3,
    .groq-modal-wrapper h4,
    .groq-modal-wrapper p,
    .groq-modal-wrapper span,
    .groq-modal-wrapper li,
    .groq-modal-wrapper strong,
    .groq-modal-wrapper label {
        color: var(--text-color) !important;
        font-family: 'Space Grotesk', 'Inter', sans-serif !important;
    }

    /* Password Eye Visibility Button & Dropdown Arrow Inherit Background & High Contrast Fix */
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="input"] > div:last-child,
    div[data-baseweb="input"] button,
    div[data-baseweb="input"] [data-baseweb="button"],
    button[aria-label*="password" i],
    button[aria-label*="visibility" i],
    button[title*="password" i],
    button[title*="visibility" i],
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div:last-child,
    div[data-baseweb="select"] [data-baseweb="icon"] {
        background: inherit !important;
        background-color: inherit !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    div[data-baseweb="input"] svg,
    div[data-baseweb="input"] svg *,
    div[data-baseweb="input"] path,
    div[data-baseweb="input"] button svg,
    div[data-baseweb="input"] button svg *,
    button[aria-label*="password" i] svg,
    button[aria-label*="visibility" i] svg,
    div[data-baseweb="select"] svg,
    div[data-baseweb="select"] path {
        fill: var(--text-color, #1E293B) !important;
        color: var(--text-color, #1E293B) !important;
        stroke: var(--text-color, #1E293B) !important;
        opacity: 1 !important;
        background-color: transparent !important;
    }

    /* Modal Callout Header */
    .groq-quota-alert-banner {
        background: rgba(239, 68, 68, 0.15) !important;
        border: 2.5px solid #EF4444 !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        margin-bottom: 20px !important;
    }
    </style>

    <div class="groq-modal-wrapper">
        <div class="groq-quota-alert-banner">
            <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
                <span style="font-size: 2.2rem;">⚠️</span>
                <div style="flex: 1;">
                    <h3 style="color: var(--text-color, #F8FAFC) !important; margin: 0 0 4px 0 !important; font-size: 1.25rem !important; font-weight: 800 !important;">Groq API Token / Rate Limit Reached</h3>
                    <p style="color: var(--text-secondary, #CBD5E1) !important; margin: 0 !important; font-size: 0.9rem !important; line-height: 1.4;">
                        Your active Groq Cloud API key reached its maximum token capacity or rate limit. Update your API keys below to resume instant AI generation.
                    </p>
                </div>
            </div>
        </div>
    </div>
    """)

    st.markdown("""
### 🔑 Step-by-Step Guide to Get a FREE Groq API Key:

1. **Step 1:** Visit official Groq Console: 👉 [**https://console.groq.com/keys**](https://console.groq.com/keys)
2. **Step 2:** Sign in with Google, GitHub, or Email.
3. **Step 3:** Click **"Create API Key"**, type a name label, and copy your key (starts with `gsk_...`).
4. **Step 4:** Paste your new key in the form below and click **Save & Update All 4 Keys**.

---
""")

    # Fetch stored settings
    try:
        g_rows = execute_query("SELECT key, value FROM settings WHERE key LIKE 'groq_api_key%' OR key = 'groq_model'")
        key_map = {r['key']: r['value'] for r in g_rows} if g_rows else {}
    except Exception:
        key_map = {}

    db_bp = key_map.get("groq_api_key_blueprint") or os.getenv("GROQ_API_KEY_BLUEPRINT") or os.getenv("GROQ_API_KEY") or ""
    db_studio = key_map.get("groq_api_key_studio") or os.getenv("GROQ_API_KEY_STUDIO") or os.getenv("GROQ_API_KEY") or ""
    db_chatbot = key_map.get("groq_api_key_chatbot") or os.getenv("GROQ_API_KEY_CHATBOT") or os.getenv("GROQ_API_KEY") or ""
    db_consult = key_map.get("groq_api_key_consultation") or os.getenv("GROQ_API_KEY_CONSULTATION") or os.getenv("GROQ_API_KEY") or ""
    db_model = key_map.get("groq_model") or "llama-3.3-70b-versatile"

    with st.form(key="groq_quota_popup_form"):
        st.markdown("#### ⚡ Update All 4 Groq API Keys")

        # 1. Blueprint Key
        st.markdown("**1. 13-Node Blueprint Generation Groq API Key**")
        bp_val = st.text_input(
            "Blueprint API Key",
            value="",
            type="password",
            placeholder=f"Active Key: ({mask_api_key(db_bp)}). Enter new key...",
            key="popup_bp_key_input",
            label_visibility="collapsed"
        )

        # 2. Studio Key
        st.markdown("**2. Implementation Studio Code Generation Groq API Key**")
        studio_val = st.text_input(
            "Studio API Key",
            value="",
            type="password",
            placeholder=f"Active Key: ({mask_api_key(db_studio)}). Enter new key...",
            key="popup_studio_key_input",
            label_visibility="collapsed"
        )

        # 3. Chatbot Key
        st.markdown("**3. Floating DevCore Chatbot Groq API Key**")
        chatbot_val = st.text_input(
            "Chatbot API Key",
            value="",
            type="password",
            placeholder=f"Active Key: ({mask_api_key(db_chatbot)}). Enter new key...",
            key="popup_chatbot_key_input",
            label_visibility="collapsed"
        )

        # 4. Consultation Key
        st.markdown("**4. Specialist Agent Node Consultation Groq API Key**")
        consult_val = st.text_input(
            "Consultation API Key",
            value="",
            type="password",
            placeholder=f"Active Key: ({mask_api_key(db_consult)}). Enter new key...",
            key="popup_consult_key_input",
            label_visibility="collapsed"
        )

        model_opts = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "deepseek-r1-distill-llama-70b", "gemma2-9b-it", "mixtral-8x7b-32768"]
        selected_model = st.selectbox(
            "Target Groq Model Selection",
            options=model_opts,
            index=model_opts.index(db_model) if db_model in model_opts else 0
        )

        col_sub1, col_sub2 = st.columns([2, 1])
        with col_sub1:
            submit_save = st.form_submit_button("💾 Save & Update All 4 API Keys", type="primary", use_container_width=True)
        with col_sub2:
            cancel_btn = st.form_submit_button("✖ Close", type="secondary", use_container_width=True)

    if cancel_btn:
        st.session_state["show_groq_quota_modal"] = False
        st.rerun()

    if submit_save:
        bp_new = bp_val.strip() or db_bp
        studio_new = studio_val.strip() or db_studio
        chatbot_new = chatbot_val.strip() or db_chatbot
        consult_new = consult_val.strip() or db_consult
        primary_new = bp_new or studio_new or chatbot_new or consult_new

        update_env_file({
            "GROQ_API_KEY_BLUEPRINT": bp_new,
            "GROQ_API_KEY_STUDIO": studio_new,
            "GROQ_API_KEY_CHATBOT": chatbot_new,
            "GROQ_API_KEY_CONSULTATION": consult_new,
            "GROQ_API_KEY": primary_new
        })

        execute_update("UPDATE settings SET value = ? WHERE key = 'groq_api_key_blueprint'", (bp_new,))
        execute_update("UPDATE settings SET value = ? WHERE key = 'groq_api_key_studio'", (studio_new,))
        execute_update("UPDATE settings SET value = ? WHERE key = 'groq_api_key_chatbot'", (chatbot_new,))
        execute_update("UPDATE settings SET value = ? WHERE key = 'groq_api_key_consultation'", (consult_new,))
        execute_update("UPDATE settings SET value = ? WHERE key = 'groq_api_key'", (primary_new,))
        execute_update("UPDATE settings SET value = ? WHERE key = 'groq_model'", (selected_model,))

        st.session_state["show_groq_quota_modal"] = False
        st.success("🎉 All Groq API keys updated successfully!")
        st.toast("New API keys saved to settings!")
        st.rerun()

# Use Streamlit dialog if supported
if hasattr(st, "dialog"):
    @st.dialog("⚠️ Groq API Token Limit Reached")
    def show_groq_quota_dialog():
        render_groq_quota_modal_content()
else:
    def show_groq_quota_dialog():
        render_groq_quota_modal_content()

def check_and_render_groq_quota_modal():
    """Trigger popup if rate limit state is flagged in session state."""
    if st.session_state.get("show_groq_quota_modal"):
        show_groq_quota_dialog()
