import os
import requests
import streamlit as st
from database.connection import execute_query, execute_update
from components.ui import saas_card
from utils.config import ensure_ollama_server_online, update_env_file, load_env_file

@st.cache_data(ttl=10)
def verify_ollama_connectivity_cached(url: str):
    """Diagnose connectivity to local Ollama runtime, cached for 10s to prevent blocking UI thread."""
    ensure_ollama_server_online(url)
    raw_url = url.rstrip('/')
    urls_to_try = [raw_url]
    if "localhost" in raw_url:
        urls_to_try.append(raw_url.replace("localhost", "127.0.0.1"))
    elif "127.0.0.1" in raw_url:
        urls_to_try.append(raw_url.replace("127.0.0.1", "localhost"))

    last_err = ""
    for u in urls_to_try:
        try:
            resp = requests.get(f"{u}/api/tags", timeout=2.5)
            if resp.status_code == 200:
                models_data = resp.json().get("models", [])
                installed_models = [m.get("name") for m in models_data]
                return True, installed_models, ""
            else:
                last_err = f"Inference engine returned HTTP code {resp.status_code}"
        except Exception as e:
            last_err = str(e)
            
    return False, [], last_err

def show_settings():
    """Render settings configuration page and run engine diagnostics."""
    load_env_file()
    
    # Header layout with Animated Odd-Colored Max Power Button in Top Right (Red Circle Location)
    col_head1, col_head2 = st.columns([1.7, 1.3])
    with col_head1:
        st.html("<h1>System Config & Engine Diagnostics</h1>")
        st.html("<p style='font-size: 1.1rem; color: var(--text-secondary); margin-top: -15px;'>Configure execution engine provider (Local Ollama vs Groq API), cloud API keys, and local model installations.</p>")
    with col_head2:
        st.html("""
        <style>
        @keyframes neonCrazyPulse {
            0% {
                background: linear-gradient(135deg, #FF0055 0%, #FF5E00 50%, #9D00FF 100%) !important;
                box-shadow: 0 0 20px #FF0055, 0 0 40px #FF5E00 !important;
                border-color: #FFFF00 !important;
                transform: scale(1);
            }
            50% {
                background: linear-gradient(135deg, #00DFD8 0%, #FF007A 50%, #FF5E00 100%) !important;
                box-shadow: 0 0 30px #00DFD8, 0 0 55px #FF007A !important;
                border-color: #FFFFFF !important;
                transform: scale(1.03);
            }
            100% {
                background: linear-gradient(135deg, #FF0055 0%, #FF5E00 50%, #9D00FF 100%) !important;
                box-shadow: 0 0 20px #FF0055, 0 0 40px #FF5E00 !important;
                border-color: #FFFF00 !important;
                transform: scale(1);
            }
        }

        .st-key-max_power_odd_btn button,
        div[data-testid="stColumn"] .st-key-max_power_odd_btn button,
        .st-key-max_power_odd_btn > button {
            background: linear-gradient(135deg, #FF0055 0%, #FF5E00 40%, #9D00FF 100%) !important;
            color: #FFFFFF !important;
            font-weight: 900 !important;
            font-size: 0.98rem !important;
            letter-spacing: 0.5px !important;
            border: 3px solid #FFFF00 !important;
            border-radius: 14px !important;
            padding: 14px 18px !important;
            animation: neonCrazyPulse 1.8s infinite ease-in-out !important;
            box-shadow: 0 0 25px rgba(255, 0, 85, 0.9) !important;
            text-shadow: 0 2px 4px rgba(0,0,0,0.8) !important;
        }
        </style>
        """)
        if st.button("🚀 MAX POWER LOCAL SETUP & MODEL GUIDE (8K UNLIMITED TOKENS)", key="max_power_odd_btn", use_container_width=True, type="primary"):
            st.session_state["show_max_power_guide_modal"] = not st.session_state.get("show_max_power_guide_modal", False)

    # 1. Fetch current settings from Environment (.env) & SQLite database
    try:
        url_row = execute_query("SELECT value FROM settings WHERE key = 'ollama_url'")
        model_row = execute_query("SELECT value FROM settings WHERE key = 'ollama_model'")
        temp_row = execute_query("SELECT value FROM settings WHERE key = 'temperature'")
        top_p_row = execute_query("SELECT value FROM settings WHERE key = 'top_p'")
        max_tokens_row = execute_query("SELECT value FROM settings WHERE key = 'max_tokens'")
        exec_provider_row = execute_query("SELECT value FROM settings WHERE key = 'execution_provider'")
        provider_row = execute_query("SELECT value FROM settings WHERE key = 'chatbot_provider'")
        
        groq_key_bp_row = execute_query("SELECT value FROM settings WHERE key = 'groq_api_key_blueprint'")
        groq_key_studio_row = execute_query("SELECT value FROM settings WHERE key = 'groq_api_key_studio'")
        groq_key_chatbot_row = execute_query("SELECT value FROM settings WHERE key = 'groq_api_key_chatbot'")
        groq_key_consult_row = execute_query("SELECT value FROM settings WHERE key = 'groq_api_key_consultation'")
        groq_model_row = execute_query("SELECT value FROM settings WHERE key = 'groq_model'")

        db_url = url_row[0]['value'] if url_row else os.getenv("OLLAMA_URL", "http://localhost:11434")
        db_model = model_row[0]['value'] if model_row else "qwen3.5:9b"
        db_temp = float(temp_row[0]['value']) if temp_row else 0.2
        db_top_p = float(top_p_row[0]['value']) if top_p_row else 0.9
        db_max_tokens = int(max_tokens_row[0]['value']) if max_tokens_row else 4096
        db_exec_provider = exec_provider_row[0]['value'] if exec_provider_row else "ollama"
        db_provider = provider_row[0]['value'] if provider_row else "groq"
        
        env_bp_key = os.getenv("GROQ_API_KEY_BLUEPRINT") or os.getenv("GROQ_API_KEY") or ""
        env_studio_key = os.getenv("GROQ_API_KEY_STUDIO") or os.getenv("GROQ_API_KEY") or ""
        env_chatbot_key = os.getenv("GROQ_API_KEY_CHATBOT") or os.getenv("GROQ_API_KEY") or ""
        env_consult_key = os.getenv("GROQ_API_KEY_CONSULTATION") or os.getenv("GROQ_API_KEY") or ""
        
        db_groq_key_bp = (groq_key_bp_row[0]['value'] if groq_key_bp_row and groq_key_bp_row[0]['value'] else env_bp_key)
        db_groq_key_studio = (groq_key_studio_row[0]['value'] if groq_key_studio_row and groq_key_studio_row[0]['value'] else env_studio_key)
        db_groq_key_chatbot = (groq_key_chatbot_row[0]['value'] if groq_key_chatbot_row and groq_key_chatbot_row[0]['value'] else env_chatbot_key)
        db_groq_key_consult = (groq_key_consult_row[0]['value'] if groq_key_consult_row and groq_key_consult_row[0]['value'] else env_consult_key)
        db_groq_model = groq_model_row[0]['value'] if groq_model_row else "llama-3.3-70b-versatile"
    except Exception:
        db_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        db_model = "qwen3.5:9b"
        db_temp = 0.2
        db_top_p = 0.9
        db_max_tokens = 4096
        db_exec_provider = "ollama"
        db_provider = "groq"
        db_groq_key_bp = os.getenv("GROQ_API_KEY_BLUEPRINT") or os.getenv("GROQ_API_KEY") or ""
        db_groq_key_studio = os.getenv("GROQ_API_KEY_STUDIO") or os.getenv("GROQ_API_KEY") or ""
        db_groq_key_chatbot = os.getenv("GROQ_API_KEY_CHATBOT") or os.getenv("GROQ_API_KEY") or ""
        db_groq_key_consult = os.getenv("GROQ_API_KEY_CONSULTATION") or os.getenv("GROQ_API_KEY") or ""
        db_groq_model = "llama-3.3-70b-versatile"

    # Render Interactive Max Power Guide Modal if triggered from header button
    if st.session_state.get("show_max_power_guide_modal"):
        st.html("""
        <div style="background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%); border: 3px solid #818CF8; border-radius: 16px; padding: 24px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4);">
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 15px; flex-wrap: wrap;">
                <div>
                    <h2 style="color: #FFD700 !important; font-size: 1.6rem !important; font-weight: 900 !important; margin: 0 0 8px 0; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">🚀 MAX POWER LOCAL LAPTOP ENGINE & MODEL GUIDE</h2>
                    <p style="color: #FFFFFF !important; font-size: 1.1rem !important; font-weight: 600 !important; margin: 0; opacity: 0.95;">Exhaustive setup guide, benchmark facts, pros & cons, and alternative local model configurations.</p>
                </div>
            </div>
        </div>
        """)
        with st.expander("📖 OPEN EXHAUSTIVE MAX POWER MODEL & INSTALLATION GUIDE", expanded=True):
            st.html("""
            <div style="background: rgba(99, 102, 241, 0.12); border: 2.5px solid #6366F1; border-radius: 12px; padding: 14px 18px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
                <div>
                    <strong style="color: var(--text-color); font-size: 0.98rem; font-weight: 800;">📦 Download Source Files for Local Execution:</strong>
                    <div style="color: var(--text-secondary); font-size: 0.88rem; margin-top: 2px;">Access full codebase, SQLite database, and run locally with local Ollama.</div>
                </div>
                <a href="https://github.com/Ranjitpatra26/DevCore-AI-" target="_blank" style="background: #6366F1; color: #FFFFFF !important; text-decoration: none; padding: 9px 18px; border-radius: 8px; font-weight: 800; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);">
                    🐙 Open GitHub Repository
                </a>
            </div>
            """)
            st.markdown("""
### 📦 Step 0: Download & Clone Source Code from GitHub

To run DevCore AI locally with your local Ollama engine, clone or download the official source repository:

👉 **GitHub Link:** [https://github.com/Ranjitpatra26/DevCore-AI-](https://github.com/Ranjitpatra26/DevCore-AI-)

```bash
# 1. Clone the repository from GitHub:
git clone https://github.com/Ranjitpatra26/DevCore-AI-.git
cd DevCore-AI-

# 2. Install required Python dependencies:
pip install -r requirements.txt

# 3. Launch DevCore AI application:
streamlit run app.py
```

---

### ⚡ Why Running Local Ollama Unlocks Maximum Power & Value

1. **Uncapped Output Depth (8,192 Tokens)**: Cloud APIs enforce Tokens-Per-Minute (TPM) limits. Local Ollama allows models to utilize full **8,192 token capacity per request**, generating massive, complete blueprints and multi-file source code.
2. **$0 API Cost**: Infinite blueprint regenerations and team collaboration without incurring monthly API bills.
3. **100% Privacy & Security**: Your project ideas, proprietary logic, and SRS documents never leave your computer.
4. **Zero Quota Exhaustion**: Never get blocked by `HTTP 429 Too Many Requests` during sprint crunches.

---

### 🏆 Recommended Local Models & Comparisons

| Model Name | Size / VRAM | Best Used For | Facts & Pros | Cons |
| :--- | :--- | :--- | :--- | :--- |
| **`qwen3.5:9b`** *(Recommended)* | 9B (~6GB VRAM) | **Full 13-Node Blueprints & DDL** | Extremely fast, high mathematical/coding accuracy, excellent SQL schemas | Requires 8GB RAM minimum |
| **`gemma4:e4b` / `gemma4:latest`** | 8B (~5GB VRAM) | **Implementation Code Studio** | Google Gemma architecture, deep multi-file source code generation | Slightly slower initial load |
| **`llama3:8b`** | 8B (~5GB VRAM) | **General Architecture & QA** | Meta Llama 3, robust multi-agent persona adherence | Strict token safety bounds |
| **`deepseek-r1:8b`** | 8B (~6GB VRAM) | **Complex Reasoning & AI RAG** | Advanced reasoning & step-by-step logic chains | Longer generation time |
| **`mistral:7b`** | 7B (~4GB VRAM) | **Lightweight Laptops** | Ultra-lean, runs smoothly even on CPU-only laptops | Shorter context depth |

---

### 💻 Step-by-Step Local Installation Commands

```bash
# 1. Download & Install Ollama from official site: https://ollama.com/download

# 2. Open PowerShell or Terminal and pull recommended models:
ollama pull qwen3.5:9b
ollama pull gemma4:e4b
ollama pull llama3

# 3. Verify local runtime port:
curl http://localhost:11434/api/tags
```
            """)
            if st.button("✖ Close Max Power Guide Modal", type="secondary"):
                st.session_state["show_max_power_guide_modal"] = False
                st.rerun()

    # Main Tab Navigation
    tab_config, tab_guide = st.tabs(["⚙️ Execution Engine & Key Configuration", "🚀 Max Power Local Installation Guide"])

    with tab_config:
        col_left, col_right = st.columns([1.2, 1])
        
        with col_left:
            st.markdown("### Execution Provider & 4 Cloud API Keys")
            
            def mask_api_key(key: str) -> str:
                if not key or not key.strip():
                    return ""
                k = key.strip()
                if len(k) <= 8:
                    return "••••••••"
                return f"{k[:4]}••••••••{k[-4:]}"

            with st.form(key="settings_form"):
                st.subheader("⚡ Blueprint & Code Engine Selection")
                
                exec_provider_opt = st.selectbox(
                    "13-Node Blueprint Generation AI Engine:",
                    options=["ollama", "groq"],
                    index=0 if db_exec_provider == "ollama" else 1,
                    format_func=lambda x: "🦙 Local Ollama Engine (Uncapped Laptop Power & 8K Tokens)" if x == "ollama" else "⚡ Groq Cloud API (High-Speed Deployed Cloud Engine)",
                    help="Select whether 13-node blueprints run via local Ollama or Groq Cloud API."
                )

                chatbot_provider_opt = st.selectbox(
                    "Floating Chatbot & Specialist Consultation AI Engine:",
                    options=["groq", "ollama"],
                    index=0 if db_provider == "groq" else 1,
                    format_func=lambda x: "⚡ Groq Cloud API (Ultra-Fast 70B Models)" if x == "groq" else "🦙 Local Ollama Engine (Local Laptop GPU)",
                    help="Select whether floating chatbot & specialist consultations use Groq Cloud API or local Ollama."
                )

                st.divider()
                st.subheader("🔑 4 Dedicated Groq API Keys (Cloud Mode & Fallback)")

                # 1. 13-Node Blueprint Generation Groq API Key Input
                st.markdown("<p style='font-size: 0.95rem; font-weight: 600; margin-bottom: 4px;'>1. 13-Node Blueprint Generation Groq API Key</p>", unsafe_allow_html=True)
                if db_groq_key_bp:
                    bp_masked = mask_api_key(db_groq_key_bp)
                    st.markdown(f"<div style='margin-bottom: 6px;'><span style='background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); padding: 3px 10px; border-radius: 6px; font-size: 0.82rem; font-weight: 600;'>🔒 Active & Saved ({bp_masked})</span></div>", unsafe_allow_html=True)
                    groq_bp_key_input = st.text_input(
                        "13-Node Blueprint Groq API Key",
                        value="",
                        type="password",
                        placeholder=f"Key stored ({bp_masked}). Enter new key to update...",
                        help="API key used exclusively for generating 13-node multi-agent blueprints.",
                        label_visibility="collapsed"
                    )
                else:
                    st.markdown("<div style='margin-bottom: 6px;'><span style='background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); padding: 3px 10px; border-radius: 6px; font-size: 0.82rem; font-weight: 600;'>⚠️ Not Configured</span></div>", unsafe_allow_html=True)
                    groq_bp_key_input = st.text_input(
                        "13-Node Blueprint Groq API Key",
                        value="",
                        type="password",
                        placeholder="Enter Groq API Key for 13-Node Blueprints (e.g. gsk_...)",
                        help="API key used exclusively for generating 13-node multi-agent blueprints.",
                        label_visibility="collapsed"
                    )

                # 2. Implementation Studio Code Generation Groq API Key Input
                st.markdown("<p style='font-size: 0.95rem; font-weight: 600; margin-top: 14px; margin-bottom: 4px;'>2. Implementation Studio Code Generation Groq API Key</p>", unsafe_allow_html=True)
                if db_groq_key_studio:
                    st_masked = mask_api_key(db_groq_key_studio)
                    st.markdown(f"<div style='margin-bottom: 6px;'><span style='background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); padding: 3px 10px; border-radius: 6px; font-size: 0.82rem; font-weight: 600;'>🔒 Active & Saved ({st_masked})</span></div>", unsafe_allow_html=True)
                    groq_studio_key_input = st.text_input(
                        "Implementation Studio Groq API Key",
                        value="",
                        type="password",
                        placeholder=f"Key stored ({st_masked}). Enter new key to update...",
                        help="API key used for generating multi-file source code modules in Implementation Studio.",
                        label_visibility="collapsed"
                    )
                else:
                    st.markdown("<div style='margin-bottom: 6px;'><span style='background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); padding: 3px 10px; border-radius: 6px; font-size: 0.82rem; font-weight: 600;'>⚠️ Not Configured</span></div>", unsafe_allow_html=True)
                    groq_studio_key_input = st.text_input(
                        "Implementation Studio Groq API Key",
                        value="",
                        type="password",
                        placeholder="Enter Groq API Key for Implementation Studio (e.g. gsk_...)",
                        help="API key used for generating multi-file source code modules in Implementation Studio.",
                        label_visibility="collapsed"
                    )
                
                # 3. Floating DevCore Chatbot Groq API Key Input
                st.markdown("<p style='font-size: 0.95rem; font-weight: 600; margin-top: 14px; margin-bottom: 4px;'>3. Floating DevCore Chatbot Groq API Key</p>", unsafe_allow_html=True)
                if db_groq_key_chatbot:
                    cb_masked = mask_api_key(db_groq_key_chatbot)
                    st.markdown(f"<div style='margin-bottom: 6px;'><span style='background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); padding: 3px 10px; border-radius: 6px; font-size: 0.82rem; font-weight: 600;'>🔒 Active & Saved ({cb_masked})</span></div>", unsafe_allow_html=True)
                    groq_chatbot_key_input = st.text_input(
                        "Floating Chatbot Groq API Key",
                        value="",
                        type="password",
                        placeholder=f"Key stored ({cb_masked}). Enter new key to update...",
                        help="Key used for floating chatbot popover.",
                        label_visibility="collapsed"
                    )
                else:
                    st.markdown("<div style='margin-bottom: 6px;'><span style='background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); padding: 3px 10px; border-radius: 6px; font-size: 0.82rem; font-weight: 600;'>⚠️ Not Configured</span></div>", unsafe_allow_html=True)
                    groq_chatbot_key_input = st.text_input(
                        "Floating Chatbot Groq API Key",
                        value="",
                        type="password",
                        placeholder="Enter Groq API Key for Chatbot (e.g. gsk_...)",
                        help="Key used for floating chatbot popover.",
                        label_visibility="collapsed"
                    )

                # 4. Specialist Agent Node Consultation Groq API Key Input
                st.markdown("<p style='font-size: 0.95rem; font-weight: 600; margin-top: 14px; margin-bottom: 4px;'>4. Specialist Agent Node Consultation Groq API Key</p>", unsafe_allow_html=True)
                if db_groq_key_consult:
                    cs_masked = mask_api_key(db_groq_key_consult)
                    st.markdown(f"<div style='margin-bottom: 6px;'><span style='background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); padding: 3px 10px; border-radius: 6px; font-size: 0.82rem; font-weight: 600;'>🔒 Active & Saved ({cs_masked})</span></div>", unsafe_allow_html=True)
                    groq_consult_key_input = st.text_input(
                        "Specialist Agent Consultation Groq API Key",
                        value="",
                        type="password",
                        placeholder=f"Key stored ({cs_masked}). Enter new key to update...",
                        help="Key used for specialist agent consultations.",
                        label_visibility="collapsed"
                    )
                else:
                    st.markdown("<div style='margin-bottom: 6px;'><span style='background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); padding: 3px 10px; border-radius: 6px; font-size: 0.82rem; font-weight: 600;'>⚠️ Not Configured</span></div>", unsafe_allow_html=True)
                    groq_consult_key_input = st.text_input(
                        "Specialist Agent Consultation Groq API Key",
                        value="",
                        type="password",
                        placeholder="Enter Groq API Key for Specialist Consultations (e.g. gsk_...)",
                        help="Key used for specialist agent consultations.",
                        label_visibility="collapsed"
                    )
                
                groq_model_input = st.selectbox(
                    "Groq Cloud Model Selection",
                    options=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "deepseek-r1-distill-llama-70b", "gemma2-9b-it", "mixtral-8x7b-32768"],
                    index=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "deepseek-r1-distill-llama-70b", "gemma2-9b-it", "mixtral-8x7b-32768"].index(db_groq_model) if db_groq_model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "deepseek-r1-distill-llama-70b", "gemma2-9b-it", "mixtral-8x7b-32768"] else 0
                )

                st.divider()
                st.subheader("🦙 Local Ollama Engine Settings")
                ollama_url = st.text_input("Ollama Connection URL", value=db_url)
                ollama_model = st.text_input("Active Local Inference Model", value=db_model, help="E.g. qwen3.5:9b, gemma4:e4b, llama3.")
                
                temperature = st.slider("Temperature (Creativity Control)", min_value=0.0, max_value=1.0, value=db_temp, step=0.05)
                top_p = st.slider("Top-P Nucleus Sampling", min_value=0.0, max_value=1.0, value=db_top_p, step=0.05)
                max_tokens = st.slider("Max Output Tokens Limit", min_value=1024, max_value=8192, value=db_max_tokens, step=128)
                
                save_clicked = st.form_submit_button("Save Engine Configurations", use_container_width=True)
                
            if save_clicked:
                try:
                    bp_raw = groq_bp_key_input.strip()
                    studio_raw = groq_studio_key_input.strip()
                    chatbot_raw = groq_chatbot_key_input.strip()
                    consult_raw = groq_consult_key_input.strip()

                    bp_k = bp_raw if bp_raw else db_groq_key_bp
                    studio_k = studio_raw if studio_raw else db_groq_key_studio
                    chatbot_k = chatbot_raw if chatbot_raw else db_groq_key_chatbot
                    consult_k = consult_raw if consult_raw else db_groq_key_consult

                    update_env_file({
                        "GROQ_API_KEY_BLUEPRINT": bp_k,
                        "GROQ_API_KEY_STUDIO": studio_k,
                        "GROQ_API_KEY_CHATBOT": chatbot_k,
                        "GROQ_API_KEY_CONSULTATION": consult_k,
                        "GROQ_API_KEY": bp_k or studio_k or chatbot_k,
                        "OLLAMA_URL": ollama_url.strip(),
                        "EXECUTION_PROVIDER": exec_provider_opt
                    })
                    
                    execute_update("UPDATE settings SET value = ? WHERE key = 'ollama_url'", (ollama_url.strip(),))
                    execute_update("UPDATE settings SET value = ? WHERE key = 'ollama_model'", (ollama_model.strip(),))
                    execute_update("UPDATE settings SET value = ? WHERE key = 'temperature'", (str(temperature),))
                    execute_update("UPDATE settings SET value = ? WHERE key = 'top_p'", (str(top_p),))
                    execute_update("UPDATE settings SET value = ? WHERE key = 'max_tokens'", (str(max_tokens),))
                    execute_update("UPDATE settings SET value = ? WHERE key = 'execution_provider'", (exec_provider_opt,))
                    execute_update("UPDATE settings SET value = ? WHERE key = 'chatbot_provider'", (chatbot_provider_opt,))
                    execute_update("UPDATE settings SET value = ? WHERE key = 'groq_api_key_blueprint'", (bp_k,))
                    execute_update("UPDATE settings SET value = ? WHERE key = 'groq_api_key_studio'", (studio_k,))
                    execute_update("UPDATE settings SET value = ? WHERE key = 'groq_api_key_chatbot'", (chatbot_k,))
                    execute_update("UPDATE settings SET value = ? WHERE key = 'groq_api_key_consultation'", (consult_k,))
                    execute_update("UPDATE settings SET value = ? WHERE key = 'groq_api_key'", (bp_k or studio_k or chatbot_k,))
                    execute_update("UPDATE settings SET value = ? WHERE key = 'groq_model'", (groq_model_input,))
                    
                    verify_ollama_connectivity_cached.clear()
                    if "ollama_config" in st.session_state:
                        del st.session_state.ollama_config
                    
                    st.success("Configurations updated successfully!")
                    st.toast("Settings saved to .env file and SQLite database.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error persisting configuration parameters: {str(e)}")

        with col_right:
            st.markdown("### Live Engine Diagnostics")
            connected, installed_models, err_msg = verify_ollama_connectivity_cached(db_url)
                
            if connected:
                status_html = f"""
                <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 20px;'>
                    <div style='width: 14px; height: 14px; background-color: var(--success-color); border-radius: 50%; border: 2px solid var(--border-color); box-shadow: 0 0 10px var(--success-color);'></div>
                    <strong style='font-size: 1.15rem; color: var(--success-color); font-family: "Space Grotesk", sans-serif;'>LOCAL OLLAMA ONLINE</strong>
                </div>
                """
                st.html(saas_card(
                    "Local Laptop Ollama Runtime",
                    status_html + f"<p style='color: var(--text-secondary); margin-top: -10px;'>DevCore AI is successfully connected to your local Ollama port at <code>{db_url}</code>.</p>",
                    "Active Laptop Engine", "success", "var(--success-color)"
                ))
                
                st.html("<strong style='font-family: \"Space Grotesk\", sans-serif; font-size: 1.1rem; display: block; margin-top: 15px;'>Installed Models on Laptop</strong>")
                if installed_models:
                    models_list_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;'>"
                    for m in installed_models:
                        badge_type = "primary" if m == db_model else "secondary"
                        models_list_html += f'<span class="saas-badge saas-badge-{badge_type}">{m}</span>'
                    models_list_html += "</div>"
                    st.html(models_list_html)
            else:
                status_html = f"""
                <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 20px;'>
                    <div style='width: 14px; height: 14px; background-color: var(--warning-color); border-radius: 50%; border: 2px solid var(--border-color); box-shadow: 0 0 10px var(--warning-color);'></div>
                    <strong style='font-size: 1.15rem; color: var(--warning-color); font-family: "Space Grotesk", sans-serif;'>LOCAL OLLAMA OFFLINE</strong>
                </div>
                """
                st.html(saas_card(
                    "Local Laptop Ollama Runtime",
                    status_html + f"<p style='color: var(--text-secondary); margin-top: -10px;'>Local Ollama server is offline at <code>{db_url}</code>. System will automatically route to Groq Cloud API if configured.</p>",
                    "Auto-Fallback Enabled", "warning", "var(--warning-color)"
                ))

            # Groq API Status Indicator
            if db_groq_key_bp or db_groq_key_studio or db_groq_key_chatbot or db_groq_key_consult:
                st.html(saas_card(
                    "Groq Cloud API Status",
                    f"<p style='color: #22c55e; margin-top: 5px;'>🟢 Groq Cloud API Keys configured & active ({db_groq_model}).</p>",
                    "Cloud Engine Active", "success", "#22c55e"
                ))

    # TAB 2: Max Power Local Installation Guide
    with tab_guide:
        st.markdown("## 🚀 How to Run DevCore AI at 100% Maximum Local Laptop Power")
        st.html("""
        <div style="background: rgba(99, 102, 241, 0.12); border: 2.5px solid #6366F1; border-radius: 12px; padding: 16px 20px; margin-top: 10px; margin-bottom: 22px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;">
            <div>
                <strong style="color: var(--text-color); font-size: 1.05rem; font-weight: 800;">📦 GitHub Source Code Repository:</strong>
                <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 2px;">Download or clone the source files to run DevCore AI locally with your local Ollama instance.</div>
            </div>
            <a href="https://github.com/Ranjitpatra26/DevCore-AI-" target="_blank" style="background: #6366F1; color: #FFFFFF !important; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-weight: 800; font-size: 0.92rem; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);">
                🐙 Download from GitHub Repository
            </a>
        </div>
        """)
        st.markdown("""
        Running DevCore AI with a **Local Ollama Engine** unlocks **uncapped 8,192 token output depth**, **zero API costs**, **no rate limits**, and **100% privacy** directly on your computer.

        ---

        ### 📦 Step 0: Clone & Download Source Code from GitHub
        To run DevCore AI locally on your computer, clone or download the official GitHub repository:

        👉 **Official GitHub Repository Link:** [https://github.com/Ranjitpatra26/DevCore-AI-](https://github.com/Ranjitpatra26/DevCore-AI-)

        ```bash
        # 1. Clone the repository from GitHub:
        git clone https://github.com/Ranjitpatra26/DevCore-AI-.git
        cd DevCore-AI-

        # 2. Install required Python dependencies:
        pip install -r requirements.txt

        # 3. Launch DevCore AI application:
        streamlit run app.py
        ```

        ---

        ### 🏆 Local Model Benchmarks & Comparison

        - **`qwen3.5:9b`**: High-speed, exceptional SQL DDL & complex architectural reasoning.
        - **`gemma4:e4b`**: Deep source code structures & multi-file generation.
        - **`llama3:8b`**: Meta Llama 3 multi-agent persona adherence.
        - **`deepseek-r1:8b`**: Advanced step-by-step logic reasoning.

        ---

        ### Step 1: Install Ollama on Your Computer
        1. Visit the official Ollama website: [https://ollama.com/download](https://ollama.com/download)
        2. Download and install Ollama for **Windows**, **macOS**, or **Linux**.

        ---

        ### Step 2: Download Recommended High-Output AI Models
        Open your Terminal or PowerShell command prompt and run one of the following commands to pull high-capacity coding models:

        ```bash
        # Recommended Primary Model (Qwen 3.5 9B - Fast & Highly Accurate)
        ollama pull qwen3.5:9b

        # High-Value Alternative Model (Gemma 4:e4b)
        ollama pull gemma4:e4b

        # Meta Llama 3 Model
        ollama pull llama3
        ```

        ---

        ### Step 3: Verify Local Connection
        1. Make sure Ollama is running in your background taskbar.
        2. In Settings tab, ensure **Ollama Connection URL** is set to `http://localhost:11434`.
        3. Select **🦙 Local Ollama Engine** as your Primary Execution Engine.
        4. Click **Save Engine Configurations**. Your system is now running at 100% uncapped maximum power!
        """)

    st.markdown("---")
    st.html("""
    <div style="background: var(--card-bg); border: 1.5px solid var(--border-color); border-radius: 12px; padding: 20px 24px; margin-top: 20px;">
        <h4 style="margin: 0 0 8px 0; color: var(--text-color); font-family: 'Space Grotesk', sans-serif;">✉️ Developer Support & Contact</h4>
        <p style="margin: 0; font-size: 0.9rem; color: var(--text-secondary);">
            If you encounter any exceptions, errors, or have feature requests, feel free to reach out directly to the lead developer:
        </p>
        <div style="margin-top: 10px; font-size: 0.95rem;">
            📬 <strong>Email:</strong> 
            <a href="mailto:ranjitspatra9077@gmail.com?subject=DevCore%20AI%20Developer%20Support" style="color: var(--primary-color); font-weight: 800; text-decoration: underline;">
                ranjitspatra9077@gmail.com
            </a>
        </div>
    </div>
    """)
