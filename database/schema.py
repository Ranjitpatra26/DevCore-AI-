import os
import sqlite3
from database.connection import get_connection
from utils.config import load_env_file

def init_db():
    """Create all database tables and populate default configurations if not existing."""
    load_env_file()
    conn = get_connection()
    cursor = conn.cursor()

    # Create Projects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        industry TEXT,
        tech_preference TEXT,
        budget TEXT,
        timeline TEXT,
        difficulty TEXT,
        model_used TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # Create Project Files Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_files (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        content TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    )""")

    # Create Agent Runs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_runs (
        project_id TEXT NOT NULL,
        agent_role TEXT NOT NULL,
        output_markdown TEXT,
        execution_time_s REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (project_id, agent_role),
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    )""")

    # Create Chats Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id TEXT NOT NULL,
        agent_role TEXT NOT NULL,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    )""")

    # Create Settings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )""")

    # Create Embeddings Table for RAG
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS embeddings (
        id TEXT PRIMARY KEY,
        file_id TEXT NOT NULL,
        chunk_text TEXT NOT NULL,
        embedding_vector_json TEXT NOT NULL,
        FOREIGN KEY (file_id) REFERENCES project_files(id) ON DELETE CASCADE
    )""")

    # Seed Default Settings from Environment (.env) or Safe Defaults
    default_settings = [
        ("ollama_url", os.getenv("OLLAMA_URL", "http://localhost:11434")),
        ("ollama_model", "qwen3.5:9b"),
        ("temperature", "0.2"),
        ("top_p", "0.9"),
        ("max_tokens", "4096"),
        ("theme", "light"),
        ("execution_provider", "ollama"),
        ("chatbot_provider", "groq"),
        ("groq_api_key", os.getenv("GROQ_API_KEY", "")),
        ("groq_api_key_studio", os.getenv("GROQ_API_KEY_STUDIO", os.getenv("GROQ_API_KEY", ""))),
        ("groq_api_key_chatbot", os.getenv("GROQ_API_KEY_CHATBOT", os.getenv("GROQ_API_KEY", ""))),
        ("groq_api_key_consultation", os.getenv("GROQ_API_KEY_CONSULTATION", os.getenv("GROQ_API_KEY", ""))),
        ("groq_model", "llama-3.3-70b-versatile")
    ]
    for key, value in default_settings:
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))


    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
