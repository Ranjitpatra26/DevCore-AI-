# Section 8: Implementation (DevCore AI)

## 8.1 Technical Overview & Workflow
The implementation of **DevCore AI** follows a decoupled multi-layer architecture. The end-to-end execution flow consists of 4 main phases:

1. **Input & RAG Ingestion:** The user submits project specifications (industry, tech stack, timeline, complexity). Any uploaded SRS documents (PDF/TXT) are chunked using an overlapping sliding window and indexed into SQLite as vector embeddings.
2. **Sequential Multi-Agent Execution:** 13 specialized AI agents run sequentially. Each agent receives project details, RAG context, and the accumulated outputs of all previous agents (**Context Chain**).
3. **Dual AI Inference Engine:** Queries are routed dynamically to **Groq Cloud API** (LLaMA 3.3 70B) for maximum speed or **Ollama** (Qwen 3.5 9B) for offline privacy.
4. **Code Generation & Persistence:** Generated markdown blueprints and runnable source code are saved atomically into an **SQLite relational database**.

---

## 8.2 Key Implementation Modules & Core Code Chunks

### 1. Sequential Context Chain & Agent Execution
**File:** [`agents/base.py`](file:///c:/Users/RANJIT%20PATRA/OneDrive/Attachments/project%202%20multi%20ai/agents/base.py)  
**Key Concept:** Each agent reads the outputs of prior agents from SQLite to ensure section-to-section consistency without contradictions.

```python
# Sequential Context Assembly & LLM Execution
previous_runs = execute_query(
    "SELECT agent_role, output_markdown FROM agent_runs WHERE project_id = ? AND agent_role != ?",
    (project_id, agent_role)
)
previous_context = "".join([f"### {r['agent_role']}:\n{r['output_markdown'][:2500]}\n\n" for r in previous_runs])

user_prompt = f"{project_details}\n{complexity_directives}\n{rag_context}\n{previous_context}"
output_markdown = query_ollama(system_prompt, user_prompt, agent_role=agent_role)

# Save result into SQLite with atomic upsert
execute_update(
    "INSERT INTO agent_runs (project_id, agent_role, output_markdown) VALUES (?, ?, ?) "
    "ON CONFLICT(project_id, agent_role) DO UPDATE SET output_markdown=excluded.output_markdown",
    (project_id, agent_role, output_markdown)
)
```

---

### 2. Dual AI Inference Engine (Groq Cloud / Local Ollama Routing)
**File:** [`utils/ollama_client.py`](file:///c:/Users/RANJIT%20PATRA/OneDrive/Attachments/project%202%20multi%20ai/utils/ollama_client.py)  
**Key Concept:** Automatically resolves active API keys from SQLite settings and routes queries to Groq Cloud API, falling back gracefully if offline.

```python
# Groq Cloud API Routing with Automatic Key Resolution
def query_groq_api_fallback(system_prompt: str, user_prompt: str) -> Optional[str]:
    g_rows = execute_query("SELECT value FROM settings WHERE key = 'groq_api_key_blueprint'")
    groq_key = g_rows[0]['value'] if g_rows else os.getenv("GROQ_API_KEY")
    
    if groq_key:
        from components.chatbot.groq_client import stream_groq_response
        chunks = stream_groq_response(messages=[{"role": "user", "content": user_prompt}], 
                                     api_key=groq_key, model="llama-3.3-70b-versatile", system_prompt=system_prompt)
        return sanitize_and_eliminate_placeholders("".join(chunks))
    return None
```

---

### 3. RAG Document Chunking Algorithm
**File:** [`rag/vector_store.py`](file:///c:/Users/RANJIT%20PATRA/OneDrive/Attachments/project%202%20multi%20ai/rag/vector_store.py)  
**Key Concept:** Splits large SRS files into 1,000-character chunks with a 200-character overlap while preserving sentence boundaries (`. `, `\n`).

```python
# Sliding Window Chunking with Boundary Protection
def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    chunks, start = [], 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        for sep in ['\n\n', '\n', '. ']: # Retroactive boundary search
            idx = text.rfind(sep, start + chunk_size // 2, end)
            if idx != -1: end = idx + len(sep); break
        chunks.append(text[start:end].strip())
        start = end - chunk_overlap if (end - chunk_overlap) > start else end
    return [c for c in chunks if c]
```

---

### 4. Implementation Studio Code Synthesis
**File:** [`utils/implementation_engine.py`](file:///c:/Users/RANJIT%20PATRA/OneDrive/Attachments/project%202%20multi%20ai/utils/implementation_engine.py)  
**Key Concept:** Validates context grounding and sets an expanded token budget (8,192 tokens) to output complete source code without truncation.

```python
# Pre-generation Validation & Smart Token Budget Allocation
def validate_generation_request(project_id: str, ctx: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    if not project_id: return False, "Error: No project selected."
    if not ctx.get("is_grounded"): return False, "Error: Run agent blueprints first."
    return True, None

def calculate_smart_token_budget() -> int:
    return 8192 # Max capacity for deep multi-file code generation
```

---

## 8.3 Relational SQLite Schema Architecture

| Table | Primary Key | Purpose |
| :--- | :--- | :--- |
| `projects` | `id` | Stores project specs, industry, stack preferences, timeline & tier. |
| `agent_runs` | `(project_id, agent_role)` | Stores generated markdown blueprint output for each of the 13 agents. |
| `embeddings` | `id` | Stores vector chunk embeddings for uploaded RAG documents. |
| `chats` | `id` | Logs floating chatbot conversations and pipeline execution events. |
| `settings` | `key` | Persists API keys, model parameters, and UI themes across sessions. |
