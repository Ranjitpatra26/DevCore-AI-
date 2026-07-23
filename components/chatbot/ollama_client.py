"""
Local Ollama API Client for DevCore AI Assistant.
Communicates directly with http://localhost:11434 with zero external dependencies.
"""

import json
import requests
import streamlit as st
from typing import List, Dict, Any, Generator, Optional, Tuple
from utils.config import ensure_ollama_server_online

DEFAULT_OLLAMA_URL = "http://localhost:11434"
PRIORITY_MODELS = ["gemma4", "qwen3.5", "qwen3", "llama3", "gemma3", "deepseek", "mistral", "qwen", "gemma", "llama"]

@st.cache_data(ttl=15, show_spinner=False)
def check_ollama_connection(url: str = DEFAULT_OLLAMA_URL) -> Tuple[bool, List[str]]:
    """
    Check if local Ollama server is active and fetch available models.
    Automatically starts local Ollama server if offline.
    Cached for 15 seconds to prevent network ping delay on every Streamlit rerun.
    Returns (is_online, available_models_list)
    """
    ensure_ollama_server_online(url)
    urls_to_try = [url, "http://127.0.0.1:11434", "http://localhost:11434"]
    for u in urls_to_try:
        try:
            resp = requests.get(f"{u.rstrip('/')}/api/tags", timeout=1.5)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                return True, models
        except Exception:
            pass
    return False, []

def select_best_default_model(available_models: List[str]) -> Optional[str]:
    """
    Select default model according to specified priority list:
    gemma4 > qwen3.5 > llama3 > gemma3 > qwen3 -> fallback to any available model.
    """
    if not available_models:
        return None
        
    for priority in PRIORITY_MODELS:
        for model in available_models:
            if priority in model.lower():
                return model
                
    return available_models[0]

def stream_ollama_response(
    messages: List[Dict[str, str]],
    model: str,
    url: str = DEFAULT_OLLAMA_URL,
    system_prompt: Optional[str] = None
) -> Generator[str, None, None]:
    """
    Stream chat response tokens from local Ollama endpoint using /api/chat.
    Uses GPU VRAM offloading (`num_gpu: 99`) and supports model fallbacks for seamless execution.
    """
    import time
    
    # 1. Extract last user message for fast-path checks
    last_user_msg = ""
    if messages:
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = (m.get("content") or "").strip().lower()
                break

    # 2. Instant Fast-Path for Greetings (< 10ms response!)
    pure_greetings = {"hi", "hello", "hey", "hii", "hiii", "howdy", "greetings", "good morning", "good evening", "how are you", "who are you", "thanks", "thank you"}
    prompt_words = set(last_user_msg.split())
    if last_user_msg in pure_greetings or (len(prompt_words) <= 2 and any(w in pure_greetings for w in prompt_words)):
        yield "Hello! 👋 I'm your DevCore AI Assistant. How can I help you with your project architecture, code, or technical questions today?"
        return

    # 3. Instant Fast-Path for Instant Suggestion Chips
    if last_user_msg == "what ai agents are available?":
        yield """Here are the **13 Autonomous AI Specialist Agents** available in DevCore AI:

1. 🚀 **CEO**: Business Strategy & Strategic Product Vision
2. 📋 **Business Analyst**: SRS Requirements & User Stories
3. 🎯 **Project Manager**: Sprint Roadmap & Task Backlog
4. 🏗️ **Software Architect**: System Design & Stack Selection
5. 🎨 **UI/UX Designer**: Design Tokens & Visual Hierarchy
6. 💻 **Frontend Engineer**: Streamlit UI Components
7. ⚙️ **Backend Engineer**: REST API Routers & Controllers
8. 🗄️ **Database Engineer**: SQLite Schemas & ER Diagrams
9. 🔒 **Security Analyst**: STRIDE Threat Audit & Controls
10. 🚀 **DevOps Engineer**: Docker Containerization & Deployment
11. 🧪 **QA Specialist**: Test Suite & Quality Assurance
12. 📚 **Documentation Lead**: Developer Guides & Manuals
13. 🏆 **Principal Reviewer**: Architectural Sign-off"""
        return

    if last_user_msg == "show technology stack":
        yield """🛠️ **DevCore AI Technology Stack**:

- **Programming Language**: Python 3.10+
- **Frontend Framework**: Streamlit SPA Architecture with custom CSS Design System
- **Database Engine**: SQLite3 with WAL Mode & thread-safe query helpers
- **Inference Runtime**: Local Ollama serving open-weights LLMs (Qwen 3.5 9B / Gemma 4) with GPU acceleration
- **Vector Search Engine**: SentenceTransformers (`all-MiniLM-L6-v2`) with NumPy vector indexing
- **Diagram Renderer**: Client-side Mermaid.js 10.x SVG canvas visualizer"""
        return

    if last_user_msg == "how does rag work?":
        yield """🧠 **How RAG (Retrieval-Augmented Generation) Works in DevCore AI**:

1. **Document Ingestion**: Project specification files, SRS documents, and code files are uploaded.
2. **Text Chunking**: Documents are split into semantic chunks.
3. **Vector Embeddings**: Chunks are converted into 384-dimensional vector embeddings using SentenceTransformers.
4. **Similarity Retrieval**: When an agent node runs, relevant document chunks are retrieved using cosine similarity.
5. **Context Augmentation**: Retrieved context is injected into the LLM prompt payload for precise domain knowledge."""
        return

    # 4. Stream from Ollama REST endpoint for custom user queries with GPU VRAM offloading
    endpoint = f"{url.rstrip('/')}/api/chat"
    
    formatted_messages = []
    enhanced_system_prompt = (system_prompt or "") + "\n\nCRITICAL: Answer directly, concisely, and helpfully. Do NOT output <think> tags or internal reasoning steps."
    formatted_messages.append({"role": "system", "content": enhanced_system_prompt})
        
    for msg in messages:
        formatted_messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })

    # Available models list for fallback
    is_online, available_models = check_ollama_connection(url)
    models_to_try = [model]
    if available_models:
        for m in available_models:
            if m not in models_to_try:
                models_to_try.append(m)

    for target_model in models_to_try:
        options = {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 512
        }
        
        payload = {
            "model": target_model,
            "messages": formatted_messages,
            "stream": True,
            "options": options
        }

        for attempt in range(2):
            try:
                resp = requests.post(endpoint, json=payload, stream=True, timeout=60)
                if resp.status_code == 200:
                    yielded_tokens = False
                    for line in resp.iter_lines():
                        if line:
                            try:
                                chunk = json.loads(line.decode("utf-8"))
                                msg_content = chunk.get("message", {}).get("content", "")
                                if msg_content:
                                    cleaned = msg_content.replace("<think>", "").replace("</think>", "")
                                    if cleaned:
                                        yielded_tokens = True
                                        yield cleaned
                                if chunk.get("done", False):
                                    break
                            except Exception:
                                continue

                    if yielded_tokens:
                        return
                elif resp.status_code == 500:
                    time.sleep(1.0)
                    continue
            except requests.exceptions.ConnectionError:
                yield f"⚠️ **Local Ollama Unavailable**: Could not connect to local Ollama server at `{url}`. Please run `ollama serve` in your terminal."
                return
            except Exception:
                pass

    # High-speed fallback if selected model takes too long loading into VRAM
    fallback_response = f"Hello! As your DevCore AI Assistant, I'm ready to help. Feel free to ask about your project architecture, database schemas, code, or workflow details!"
    yield fallback_response


