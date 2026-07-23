"""
Centralized Configuration Module for DevCore AI Operating System.
Provides production tuning parameters, timeouts, retry limits, and model selection.
"""

import os
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Dict, Any


# Root workspace directory and .env file location
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

def load_env_file() -> Dict[str, str]:
    """Load environment variables from .env file and Streamlit secrets into os.environ."""
    env_vars = {}
    if ENV_PATH.exists():
        try:
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip("'\"")
                    env_vars[key] = value
                    os.environ[key] = value
        except Exception:
            pass

    # Read from Streamlit Cloud secrets if available
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for k, v in st.secrets.items():
                if isinstance(v, str) and v.strip():
                    os.environ[k] = v.strip()
                    env_vars[k] = v.strip()
    except Exception:
        pass

    return env_vars

def update_env_file(key_values: Dict[str, str]) -> bool:
    """Update or append key-value pairs in the .env file and refresh os.environ."""
    try:
        existing_lines = []
        if ENV_PATH.exists():
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                existing_lines = f.readlines()

        updated_keys = set()
        new_lines = []

        for line in existing_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                key, _ = stripped.split("=", 1)
                key = key.strip()
                if key in key_values:
                    val = key_values[key]
                    new_lines.append(f"{key}={val}\n")
                    updated_keys.add(key)
                    os.environ[key] = val
                    continue
            new_lines.append(line)

        # Append any remaining new keys
        for key, val in key_values.items():
            if key not in updated_keys:
                new_lines.append(f"{key}={val}\n")
                os.environ[key] = val

        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    except Exception:
        return False

# Initialize .env on module load
load_env_file()

# Connection & Timeout Defaults (Calibrated for 35s per node parallel synthesis)
OLLAMA_DEFAULT_URL = os.getenv("OLLAMA_URL") or os.getenv("OLLAMA_HOST") or "http://localhost:11434"

DEFAULT_CONNECT_TIMEOUT = 5.0
DEFAULT_REQUEST_TIMEOUT = 360  # 6-minute max timeout for uncapped 15k+ word local LLM generation
IMPLEMENTATION_REQUEST_TIMEOUT = 480  # 8-minute max limit for deep multi-file source code generation
CONSULTATION_REQUEST_TIMEOUT = 60
MAX_RETRIES = 1  # Fast recovery

# Model Defaults
PRIMARY_MODEL = "qwen3.5:9b"
FALLBACK_MODEL = "qwen3.5:9b"
DEFAULT_MODEL = PRIMARY_MODEL

# Model Generation Parameters
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TOP_P = 0.85
DEFAULT_MAX_TOKENS = 8192  # Expanded 8K deep token capacity per agent
AGENT_BLUEPRINT_MAX_TOKENS = 8192  # Deep 8K capacity for uncapped local laptop VRAM power
IMPLEMENTATION_MAX_TOKENS = 8192  # Deep 8K capacity for Implementation Studio code generation
GROQ_BLUEPRINT_MAX_TOKENS = 1400  # Compact, high-value 1.4K token budget for Groq Cloud API (stays safely under 14.4k TPM)
CONSULTATION_SHORT_TOKENS = 1024
CONSULTATION_LONG_TOKENS = 4096

# Cache Parameters
RESPONSE_CACHE_MAXSIZE = 128
CONTEXT_CACHE_TTL_SECONDS = 300

def ensure_ollama_server_online(url: str = OLLAMA_DEFAULT_URL) -> bool:
    """
    Check if Ollama server is active.
    If offline, automatically launch local `ollama serve` process in the background.
    Returns True if online / successfully connected, False otherwise.
    """
    target = url.rstrip('/')
    urls_to_try = [target]
    if "localhost" in target:
        urls_to_try.append(target.replace("localhost", "127.0.0.1"))
    elif "127.0.0.1" in target:
        urls_to_try.append(target.replace("127.0.0.1", "localhost"))

    # 1. Test existing connection
    for u in urls_to_try:
        try:
            req = urllib.request.Request(f"{u}/api/tags", headers={"User-Agent": "DevCore-AI/1.0"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass

    # 2. Server offline: attempt background spawn of `ollama serve`
    ollama_bin = shutil.which("ollama")
    if not ollama_bin and os.name == "nt":
        default_win_path = r"C:\Users\RANJIT PATRA\AppData\Local\Programs\Ollama\ollama.exe"
        if os.path.exists(default_win_path):
            ollama_bin = default_win_path

    if ollama_bin:
        try:
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
            subprocess.Popen(
                [ollama_bin, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags
            )
            # Give server up to 3 seconds to spin up
            for _ in range(6):
                time.sleep(0.5)
                for u in urls_to_try:
                    try:
                        req = urllib.request.Request(f"{u}/api/tags", headers={"User-Agent": "DevCore-AI/1.0"})
                        with urllib.request.urlopen(req, timeout=1.0) as resp:
                            if resp.status == 200:
                                return True
                    except Exception:
                        pass
        except Exception:
            pass

    return False

def get_generation_config(override_dict: Dict[str, Any] = None) -> Dict[str, Any]:
    """Return consolidated model generation settings with SQLite settings sync and optional overrides."""
    url = OLLAMA_DEFAULT_URL
    model = DEFAULT_MODEL
    temp = DEFAULT_TEMPERATURE
    top_p = DEFAULT_TOP_P
    max_tokens = DEFAULT_MAX_TOKENS

    try:
        from database.connection import execute_query
        url_row = execute_query("SELECT value FROM settings WHERE key = 'ollama_url'")
        model_row = execute_query("SELECT value FROM settings WHERE key = 'ollama_model'")
        temp_row = execute_query("SELECT value FROM settings WHERE key = 'temperature'")
        top_p_row = execute_query("SELECT value FROM settings WHERE key = 'top_p'")
        max_tokens_row = execute_query("SELECT value FROM settings WHERE key = 'max_tokens'")

        if url_row and url_row[0]['value']:
            url = url_row[0]['value'].strip()
        if model_row and model_row[0]['value']:
            model = model_row[0]['value'].strip()
        if temp_row and temp_row[0]['value']:
            temp = float(temp_row[0]['value'])
        if top_p_row and top_p_row[0]['value']:
            top_p = float(top_p_row[0]['value'])
        if max_tokens_row and max_tokens_row[0]['value']:
            max_tokens = int(max_tokens_row[0]['value'])
    except Exception:
        pass

    base = {
        "url": url,
        "model": model,
        "fallback_model": FALLBACK_MODEL,
        "temperature": temp,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "connect_timeout": DEFAULT_CONNECT_TIMEOUT,
        "request_timeout": DEFAULT_REQUEST_TIMEOUT,
        "max_retries": MAX_RETRIES
    }
    if override_dict and isinstance(override_dict, dict):
        base.update(override_dict)
    return base

def get_execution_provider() -> str:
    """Retrieve active execution engine provider ('ollama' or 'groq') from SQLite database settings or env."""
    try:
        from database.connection import execute_query
        rows = execute_query("SELECT value FROM settings WHERE key = 'execution_provider'")
        if rows and rows[0]['value'] in ['ollama', 'groq']:
            return rows[0]['value']
    except Exception:
        pass
    return os.getenv("EXECUTION_PROVIDER", "ollama")

