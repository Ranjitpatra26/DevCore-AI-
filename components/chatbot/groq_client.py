"""
Groq API Client for DevCore AI Assistant.
Provides ultra-fast streaming inference using GroqCloud API (https://api.groq.com/openai/v1).
"""

import json
import requests
from typing import List, Dict, Any, Generator, Optional

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
AVAILABLE_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "deepseek-r1-distill-llama-70b",
    "gemma2-9b-it",
    "mixtral-8x7b-32768"
]

def stream_groq_response(
    messages: List[Dict[str, str]],
    api_key: str,
    model: str = "llama-3.3-70b-versatile",
    system_prompt: Optional[str] = None,
    is_chatbot: bool = False
) -> Generator[str, None, None]:
    """
    Stream chat response tokens from Groq API using SSE endpoint.
    """
    if not api_key or not api_key.strip():
        yield "⚠️ **Groq API Key Required**: Please enter your Groq API key in **Settings** or your `.env` file."
        return

    # Fast-path greeting and preset checks ONLY for floating chatbot popover
    if is_chatbot:
        last_user_msg = ""
        if messages:
            for m in reversed(messages):
                if m.get("role") == "user":
                    last_user_msg = (m.get("content") or "").strip().lower()
        pure_greetings = {"hi", "hello", "hey", "hii", "hiii", "howdy", "greetings", "good morning", "good evening", "how are you", "who are you", "thanks", "thank you"}
        prompt_words = set(last_user_msg.split())
        if last_user_msg in pure_greetings or (len(prompt_words) <= 2 and any(w in pure_greetings for w in prompt_words)):
            yield "Hello! 👋 I'm your DevCore AI Assistant. How can I help you with your project architecture, code, or technical questions today?"
            return

        if "core features" in last_user_msg:
            yield """✨ **Key Features & Capabilities**:

1. 🚀 **Autonomous 13-Agent Workforce**: Cross-functional team of AI specialists generating full software blueprints.
2. 🛠️ **Implementation Studio**: Interactive code workspace for generating production-ready code files.
3. 💬 **Specialist Consultation Terminal**: Real-time expert advice with active RAG context retrieval.
4. 🧠 **Vector RAG Document Search**: Ingest SRS manuals and reference files for context-aware generation.
5. 📊 **Dynamic Diagram Rendering**: Compiled visual Mermaid.js topology, ERD, and sequence charts."""
            return

        if "technology stack" in last_user_msg or "tech stack" in last_user_msg:
            yield """🛠️ **Technology Stack & Frameworks**:

- **Core Runtime**: Python 3.10+ (Type-annotated, modular OOP design)
- **Frontend SPA**: Streamlit with custom CSS Design Tokens (Dark / Light Neobrutalism)
- **Database Engine**: SQLite3 with WAL Mode & thread-safe connection helpers
- **AI Inference Runtimes**: Groq Cloud LPU API (`llama-3.3-70b-versatile`) & Local GPU Ollama
- **RAG & Vectors**: SentenceTransformers (`all-MiniLM-L6-v2`) with NumPy vector indexing
- **Visual Visualizers**: Mermaid.js 10.x SVG canvas renderer"""
            return

        if "development progress" in last_user_msg or "status" in last_user_msg:
            yield """📊 **Development Progress & Status Breakdown**:

🟢 **Completed & Implemented (75% Complete)**:
- Core 13-agent architecture, SQLite database models, and Streamlit SPA router.
- Groq Cloud LPU integration and local GPU Ollama inference engine.

🔄 **Currently In-Progress**:
- Real-time streaming token optimization and edge-case validation.

📌 **Next Steps**:
- End-to-end load benchmarking and deliverable PDF export compiling."""
            return

        if "architecture overview" in last_user_msg or "system architecture" in last_user_msg:
            yield """🏗️ **System Architecture Overview**:

1. **Presentation Layer**: Streamlit SPA with dynamic layout containers and visual styling tokens.
2. **Orchestration Layer**: Event-driven multi-agent engine connecting 13 specialist personas.
3. **Inference & RAG Layer**: Dual-engine processing (Groq LPUs + Local Ollama) paired with SentenceTransformers vector retrieval.
4. **Data Persistence**: SQLite WAL database storing project states, chats, and generated artifacts."""
            return

        if "backend apis" in last_user_msg or "schemas" in last_user_msg:
            yield """🗄️ **Backend APIs & Database Schemas**:

- **Database Schemas**: SQLite tables for `projects`, `project_files`, `agent_runs`, `chats`, `settings`, and `embeddings`.
- **API Endpoints**: REST routers handling blueprint execution, consultation messages, document chunking, and file exports."""
            return

        if "security" in last_user_msg or "privacy" in last_user_msg:
            yield """🔒 **Security & Data Privacy Protocols**:

1. **Zero Cloud Leakage**: Local GPU option keeps 100% of code and documents local on your machine.
2. **STRIDE Threat Audit**: Automated threat modeling covering Spoofing, Tampering, Repudiation, and Data Disclosure.
3. **Parameterized Queries**: 100% parameterized SQL queries to eliminate SQL injection risks.
4. **Input Sanitization**: Dynamic XSS filtering and HTML sandboxing for rendered components."""
            return

    formatted_messages = []
    enhanced_system_prompt = (system_prompt or "") + "\n\nCRITICAL: Answer directly, concisely, and helpfully. Do NOT output <think> tags or internal reasoning steps."
    formatted_messages.append({"role": "system", "content": enhanced_system_prompt})

    for msg in messages:
        formatted_messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })

    payload = {
        "model": model,
        "messages": formatted_messages,
        "temperature": 0.3,
        "max_tokens": 1400 if not is_chatbot else 1024,
        "stream": True
    }

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(GROQ_ENDPOINT, json=payload, headers=headers, stream=True, timeout=30)
        if resp.status_code == 200:
            yielded_tokens = False
            for line in resp.iter_lines():
                if line:
                    line_str = line.decode("utf-8").strip()
                    if line_str.startswith("data: "):
                        data_str = line_str[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta_content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if delta_content:
                                cleaned = delta_content.replace("<think>", "").replace("</think>", "")
                                if cleaned:
                                    yielded_tokens = True
                                    yield cleaned
                        except Exception:
                            continue
            if yielded_tokens:
                return
        elif resp.status_code == 401:
            yield "⚠️ **Invalid Groq API Key**: Please check your Groq API key in **Settings** or your `.env` file."
            return

        elif resp.status_code == 429:
            yield "⚠️ **Groq Rate Limit Exceeded**: Please wait a few seconds or try a smaller model like `llama-3.1-8b-instant`."
            return
        else:
            err_body = resp.text[:200]
            yield f"⚠️ **Groq API Error ({resp.status_code})**: {err_body}"
            return

    except requests.exceptions.Timeout:
        yield "⚠️ **Groq Request Timeout**: The Groq API took too long to respond. Please try again."
        return
    except Exception as e:
        yield f"⚠️ **Groq Connection Failure**: {str(e)}"
        return

    yield "Hello! How can I assist you with your project today?"
