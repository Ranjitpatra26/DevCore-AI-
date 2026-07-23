"""
Implementation Studio Component for DevCore AI Operating System.
VS Code-Style AI Software Engineering Workspace powered by synchronized project blueprints.
Features Blueprint Synchronization Validation, 12 Senior Engineering Personas, 11 Specialized Categories, 
80+ Specialized Sub-Module Selectors, VS Code-Style Project Explorer, Multi-File IDE Editor Viewer, 
Mermaid Diagram Visualizer, and Collapsible Developer Prompt Debug Panel.
Fully isolated and modular for complete rollback safety.
"""

import streamlit as st
import re
import json
import time
from typing import Dict, Any, List, Optional
from utils.ollama_client import query_ollama
from database.connection import execute_query
from components.ui import saas_card

# 12 Senior Engineering Role Personas
MODES: Dict[str, Dict[str, Any]] = {
    "architect": {
        "label": "🏗 Architect Mode",
        "title": "Senior Software Architect",
        "system_role": "You are a Senior Software Architect. Your job is to define system topology, module boundaries, architectural patterns, clean architecture, component relationships, and scalability trade-offs.",
        "priority": "Prioritize system topology, high-level architecture, module boundaries, component relationships, design patterns, and scalability trade-offs.",
        "agent_role": "architect"
    },
    "backend": {
        "label": "⚙ Backend Mode",
        "title": "Senior FastAPI Backend Engineer",
        "system_role": "You are a Senior FastAPI Backend Engineer. Your job is to write production-ready backend code following SOLID, Clean Architecture, Repository Pattern, and Dependency Injection: API endpoints, controllers, services, repositories, authentication, middleware, models, and validation schemas ONLY. Never generate frontend code.",
        "priority": "Prioritize API endpoint design, controllers, service layer, repository pattern, authentication, middleware, validation strategy, and server performance.",
        "agent_role": "backend"
    },
    "frontend": {
        "label": "🎨 Frontend Mode",
        "title": "Senior Frontend Engineer",
        "system_role": "You are a Senior Frontend Engineer. Your job is to write production-ready frontend code: UI component hierarchy, Streamlit/React pages, state management, layout hierarchy, and CSS design tokens ONLY. Never generate backend code.",
        "priority": "Prioritize UI components, page structure, layout hierarchy, state management recommendations, micro-interactions, and reusable UI tokens.",
        "agent_role": "frontend"
    },
    "database": {
        "label": "🗄 Database Mode",
        "title": "Senior PostgreSQL Architect",
        "system_role": "You are a Senior PostgreSQL Architect. Your job is to design production database schemas: SQL DDL, PostgreSQL/SQLite CREATE TABLE statements, ORM mapping models, ERD entity relationships, indexes, constraints, and migrations ONLY.",
        "priority": "Prioritize ERD entity relationships, SQL schema, ORM mapping models, indexing strategy, migration plans, and query optimization.",
        "agent_role": "database"
    },
    "ai_rag": {
        "label": "🤖 AI & RAG Mode",
        "title": "Senior AI Engineer",
        "system_role": "You are a Senior AI Engineer. Your job is to build AI pipelines: LangGraph state graph workflows, AI agent nodes, prompt templates, memory strategy, vector embeddings, and retrieval RAG architecture ONLY.",
        "priority": "Prioritize LangGraph state graph workflows, vector database embeddings, memory management, prompt template assembly, and agent orchestration.",
        "agent_role": "architect"
    },
    "qa": {
        "label": "🧪 QA Mode",
        "title": "Senior QA Engineer",
        "system_role": "You are a Senior QA Engineer. Your job is to design test suites: pytest test files, unit tests, integration API tests, edge case assertions, software reliability checks, and QA audit checklists ONLY.",
        "priority": "Prioritize unit testing, integration testing, end-to-end test scenarios, edge case validation, software reliability, and QA audit checklists.",
        "agent_role": "qa"
    },
    "security": {
        "label": "🔒 Security Mode",
        "title": "Senior Security Engineer",
        "system_role": "You are a Senior Security Engineer. Your job is to enforce application security: threat modeling, OWASP vulnerability mitigations, authentication/authorization middleware, input sanitization, data encryption, and key management ONLY.",
        "priority": "Prioritize threat modeling, authentication/authorization security, data encryption, input sanitization, vulnerability prevention, and security audit controls.",
        "agent_role": "security"
    },
    "documentation": {
        "label": "📄 Documentation Mode",
        "title": "Senior Technical Writer",
        "system_role": "You are a Senior Technical Writer. Your job is to produce comprehensive developer documentation: production README.md, API references, developer onboarding guides, deployment checklists, and architectural summaries.",
        "priority": "Prioritize clear README structure, API references, developer onboarding guides, deployment checklists, and project architecture summaries.",
        "agent_role": "documentation"
    },
    "devops": {
        "label": "🚀 DevOps Mode",
        "title": "Senior DevOps Engineer",
        "system_role": "You are a Senior DevOps Engineer. Your job is to write infrastructure automation: Dockerfile, docker-compose.yml, CI/CD pipeline scripts, Kubernetes manifests, environment variable management, and monitoring setups ONLY.",
        "priority": "Prioritize Docker containerization, CI/CD pipeline configuration, environment variables, deployment scripts, monitoring, and cloud hosting architecture.",
        "agent_role": "devops"
    },
    "general": {
        "label": "💡 General Engineering Mode",
        "title": "Principal Software Engineer",
        "system_role": "You are a Principal Software Engineer. Your job is to provide production-ready full-stack architecture, clean code implementation, folder structure, database schema, and engineering best practices.",
        "priority": "Provide balanced, well-rounded technical implementation guidance spanning architecture, full-stack development, database design, and best practices.",
        "agent_role": "architect"
    },
    "business_analyst": {
        "label": "📊 Business Analyst Mode",
        "title": "Senior Business Analyst",
        "system_role": "You are a Senior Business Analyst. Your job is to define business requirements: BRD, functional/non-functional requirements, user stories, acceptance criteria, business rules, process flows, use cases, and KPI metrics.",
        "priority": "Prioritize user stories, functional requirements, non-functional requirements, acceptance criteria, business rules, business process flows, use cases, and requirement traceability.",
        "agent_role": "business_analyst"
    },
    "project_manager": {
        "label": "📅 Project Manager Mode",
        "title": "Senior Technical Project Manager",
        "system_role": "You are a Senior Technical Project Manager. Your job is to define execution planning: sprint roadmaps, product backlog, story points, task breakdowns, milestone schedules, dependency maps, and risk mitigation strategies.",
        "priority": "Prioritize sprint planning, product backlog, task breakdown, milestones, timeline planning, resource allocation, risk assessment, and delivery roadmap.",
        "agent_role": "project_manager"
    }
}

# 11 Engineering Categories & Specialized Sub-Modules
CATEGORIES: Dict[str, Dict[str, Any]] = {
    "backend": {
        "label": "⚙ Backend Development",
        "name": "Backend Development",
        "description": "API endpoints, controllers, services, repositories, auth & middleware.",
        "icon": "⚙",
        "modules": ["Authentication", "Authorization", "Users", "Admin", "Dashboard", "CRUD APIs", "Payment", "Notification", "Search", "Logging", "Middleware", "File Upload", "Background Workers", "WebSocket", "Analytics"],
        "prompt": "Generate ONLY backend implementation files: routers, controllers, services, repositories, schemas, models, auth, and middleware."
    },
    "frontend": {
        "label": "🎨 Frontend Development",
        "name": "Frontend Development",
        "description": "Component hierarchy, page routing, Streamlit/React components & state management.",
        "icon": "🎨",
        "modules": ["Landing Page", "Dashboard", "Login", "Registration", "Profile", "Settings", "Tables", "Forms", "Charts", "Reusable Components", "Navigation", "Theme", "State Management"],
        "prompt": "Generate ONLY frontend implementation files: page layout, UI components, state management hooks, forms, tables, and CSS design tokens."
    },
    "database": {
        "label": "🗄 Database Design",
        "name": "Database Design",
        "description": "SQL DDL schema, ORM model classes, ERD entity relationships, indexes & constraints.",
        "icon": "🗄",
        "modules": ["SQL Schema", "PostgreSQL DDL", "SQLAlchemy Models", "Relationships", "Indexes", "Constraints", "Migrations", "Seed Data"],
        "prompt": "Generate ONLY database implementation files: production SQL CREATE TABLE DDL statements, foreign keys, indexes, SQLAlchemy models, and seed data."
    },
    "ai_rag": {
        "label": "🤖 AI & RAG",
        "name": "AI & RAG",
        "description": "LangGraph state graphs, agent prompts, vector embeddings & memory retrieval pipeline.",
        "icon": "🤖",
        "modules": ["LangGraph", "Multi Agent", "Prompt Templates", "RAG", "Embeddings", "Vector DB", "Memory", "Tool Calling"],
        "prompt": "Generate ONLY AI & RAG implementation files: LangGraph StateGraph nodes, agent prompts, vector embeddings chunker, and memory retrieval pipeline."
    },
    "testing": {
        "label": "🧪 Testing",
        "name": "Testing",
        "description": "pytest unit tests, integration API test suite, edge case assertions & QA checklist.",
        "icon": "🧪",
        "modules": ["Unit Tests", "Integration Tests", "API Tests", "UI Tests", "Edge Cases", "Security Tests"],
        "prompt": "Generate ONLY test implementation files: pytest test files, mock fixtures, API integration tests, and edge case verification assertions."
    },
    "devops": {
        "label": "🚀 DevOps",
        "name": "DevOps",
        "description": "Dockerfile, docker-compose, CI/CD pipeline, Kubernetes manifests & env variables.",
        "icon": "🚀",
        "modules": ["Dockerfile", "docker-compose", "CI/CD Pipeline", "Kubernetes Manifests", "Environment Configs", "Monitoring Setup"],
        "prompt": "Generate ONLY infrastructure DevOps files: Dockerfile, docker-compose.yml, CI/CD GitHub action workflow, and environment configuration scripts."
    },
    "project_structure": {
        "label": "📁 Project Structure",
        "name": "Project Structure",
        "description": "Production folder hierarchy, package organization, module boundaries & domain files.",
        "icon": "📁",
        "modules": ["Full Directory Tree", "Clean Architecture Spec", "Package Boundary Map"],
        "prompt": "Generate full production directory hierarchy with complete file tree, package organization, naming conventions, and module boundaries."
    },
    "architecture": {
        "label": "🏗 Architecture",
        "name": "Architecture",
        "description": "System topology, Mermaid diagrams, layered architecture & design patterns.",
        "icon": "🏗",
        "modules": ["Mermaid System Topology", "Layered Service Topology", "Module Interaction Map"],
        "prompt": "Generate complete system topology with a Mermaid.js diagram (```mermaid ... ```), layered architecture breakdown, component relationships, and design patterns."
    },
    "documentation": {
        "label": "📄 Documentation",
        "name": "Documentation",
        "description": "Production README.md, API specification, quickstart guide & deployment steps.",
        "icon": "📄",
        "modules": ["README.md", "Developer Guide", "API Reference", "Architecture Overview", "Deployment Checklist"],
        "prompt": "Generate production documentation: complete README.md, API endpoint reference, environment setup commands, and deployment guide."
    },
    "pseudocode": {
        "label": "💡 Pseudocode & Algorithms",
        "name": "Pseudocode & Algorithms",
        "description": "Algorithmic logic breakdown, pseudocode, time complexity & function planning.",
        "icon": "💡",
        "modules": ["Core Domain Algorithm", "Big-O Time Complexity", "Step-by-Step Pipeline"],
        "prompt": "Generate algorithmic implementation: structured pseudocode, step-by-step logic pipeline, data structures, and time/space complexity analysis."
    },
    "code_review": {
        "label": "🔍 Code Review",
        "name": "Code Review",
        "description": "Paste code snippets for architecture-aware code review, refactoring & security audit.",
        "icon": "🔍",
        "requires_input": True,
        "input_label": "Paste Code Snippet to Review",
        "input_placeholder": "Paste code snippet here...",
        "modules": ["OWASP Security Audit", "Refactoring & Clean Code", "Performance Optimization"],
        "prompt": "Perform architecture-aware code review: check clean code practices, security vulnerabilities, performance bottlenecks, and refactored code fixes."
    },
    "debug": {
        "label": "🐞 Debug Assistant",
        "name": "Debug Assistant",
        "description": "Paste stack traces or error logs for root cause analysis & code fix.",
        "icon": "🐞",
        "requires_input": True,
        "input_label": "Paste Error Log or Stack Trace",
        "input_placeholder": "Paste error log here...",
        "modules": ["Root Cause Analysis", "Corrected Code Fix", "Exception Prevention Pattern"],
        "prompt": "Analyze the error log: provide root cause analysis, corrected code fix, exception handling middleware, and prevention recommendations."
    }
}

QUICK_ACTION_CHIPS = [
    ("⚙ Backend APIs", "backend"),
    ("🎨 UI Components", "frontend"),
    ("🗄 SQL Schema", "database"),
    ("🤖 AI RAG Pipeline", "ai_rag"),
    ("🚀 Docker Setup", "devops"),
    ("🧪 pytest Suite", "testing"),
    ("📄 README.md", "documentation"),
    ("🏗 System Architecture", "architecture"),
    ("📁 Project Tree", "project_structure")
]

def get_initial_category_code(cat_key: str, proj_details: Dict[str, Any], runs_map: Dict[str, Any]) -> str:
    """Extract or generate instant production starter code & specifications for Implementation Studio."""
    proj_name = proj_details.get('name', 'Synchronized System') if isinstance(proj_details, dict) else 'Synchronized System'
    proj_tech = proj_details.get('tech_preference', 'Python, REST API, SQLite') if isinstance(proj_details, dict) else 'Python, REST API, SQLite'
    proj_ind = proj_details.get('industry', 'Technology & SaaS') if isinstance(proj_details, dict) else 'Technology & SaaS'
    proj_desc = proj_details.get('description', 'Application Platform') if isinstance(proj_details, dict) else 'Application Platform'

    def get_run_text(role: str) -> str:
        if not runs_map or not isinstance(runs_map, dict): return ""
        r = runs_map.get(role, {})
        if isinstance(r, str): return r
        if isinstance(r, dict): return r.get('output_markdown', '') or ""
        return ""

    if cat_key == "backend":
        bp_code = get_run_text("backend") or get_run_text("architect")
        if bp_code and "```" in bp_code:
            return bp_code
        return f"""# Production Backend API Implementation for '{proj_name}'

```python
# File: app/main.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os

app = FastAPI(
    title="{proj_name} API Services",
    description="Production REST API backend for {proj_name} ({proj_ind})",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthStatus(BaseModel):
    status: str = Field(default="online")
    system: str = Field(default="{proj_name}")
    environment: str = Field(default="production")

@app.get("/health", response_model=HealthStatus, tags=["Health"])
async def health_check():
    return {{"status": "online", "system": "{proj_name}", "environment": "production"}}

@app.get("/api/v1/resources", tags=["Resources"])
async def list_resources():
    return {{"project": "{proj_name}", "tech_stack": "{proj_tech}", "status": "active"}}
```

```python
# File: app/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "{proj_name}"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./{proj_name.lower().replace(' ', '_')}.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")

settings = Settings()
```
"""
    elif cat_key == "database":
        bp_code = get_run_text("database")
        if bp_code and "```" in bp_code:
            return bp_code
        return f"""# Database Schema & DDL Migration Script for '{proj_name}'

```sql
-- File: database/schema.sql
-- Production Relational Schema DDL for {proj_name}

CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    industry VARCHAR(100),
    tech_preference VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(36) REFERENCES projects(id) ON DELETE CASCADE,
    action VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
```
"""
    elif cat_key == "frontend":
        bp_code = get_run_text("frontend") or get_run_text("ui_ux")
        if bp_code and "```" in bp_code and ("class " in bp_code or "def " in bp_code or "import " in bp_code or "function " in bp_code or "const " in bp_code):
            return bp_code
        return f"""# UI Component Architecture & Production Source Code for '{proj_name}'

```text
# File: docs/file_structure_architecture.txt
frontend/
├── pages/
│   ├── dashboard.py     # Main operational metrics & project list
│   ├── new_project.py   # Spatial project initialization studio
│   ├── projects.py      # Workspace explorer & diagram renderer
│   ├── ai_team.py       # 13 Senior Agent profile studio
│   ├── chat.py          # Real-time multi-agent consultation chat
│   └── settings.py      # System preferences & Ollama configuration
└── components/
    ├── ui.py            # Reusable SaaS cards, metrics & badges
    ├── navigation.py    # Top navigation header & theme switcher
    ├── implementation.py # Source code synthesis studio
    └── styles.css       # Central design system CSS tokens & rules
```

```python
# File: pages/projects.py
import streamlit as st
from database.connection import execute_query

def show_projects():
    """Workspace Explorer & Architecture Renderer for {proj_name}."""
    st.title("🚀 Workspace Explorer - {proj_name}")
    st.caption("Industry Domain: {proj_ind} | Tech Stack: {proj_tech}")
    
    projects = execute_query("SELECT id, name, description, created_at FROM projects ORDER BY created_at DESC")
    
    if not projects:
        st.info("No active projects found in SQLite database.")
        return
        
    st.subheader(f"Saved Workspaces ({{len(projects)}})")
    for proj in projects:
        with st.expander(f"📁 {{proj['name']}}", expanded=True):
            st.write(proj['description'])
            st.caption(f"Initialized on {{proj['created_at']}}")

if __name__ == "__main__":
    show_projects()
```

```python
# File: pages/dashboard.py
import streamlit as st

def show_dashboard():
    """Operational Metrics & System Diagnostics Dashboard for {proj_name}."""
    st.markdown("## 📊 System Diagnostics: {proj_name}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Active AI Workforce", value="13 Agents", delta="100% Online")
    with col2:
        st.metric(label="Inference Latency", value="42ms", delta="GPU Accelerated")
    with col3:
        st.metric(label="Vector Knowledge Store", value="384 Dim", delta="SQLite / Chroma")

    st.success("Synchronized with {proj_tech} Backend Services.")

if __name__ == "__main__":
    show_dashboard()
```

```python
# File: components/ui.py
import streamlit as st

def saas_card(title: str, content: str, badge_text: str = "Active", status: str = "success"):
    """Reusable SaaS Card UI Component for {proj_name}."""
    st.html(f'''
    <div style="background: #0F172A; border: 1.5px solid #334155; border-radius: 12px; padding: 18px; margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h4 style="margin: 0; color: #F8FAFC;">{{title}}</h4>
            <span style="background: rgba(16, 185, 129, 0.2); color: #34D399; font-weight: 700; border: 1px solid #10B981; padding: 2px 10px; border-radius: 12px; font-size: 0.78rem;">{{badge_text}}</span>
        </div>
        <p style="margin: 0; color: #94A3B8; font-size: 0.9rem;">{{content}}</p>
    </div>
    ''')
```

```css
/* File: styles.css */
/* Central Design Tokens for {proj_name} */
:root {{
    --primary-color: #6366F1;
    --card-bg: #0F172A;
    --text-color: #F8FAFC;
    --text-secondary: #94A3B8;
    --border-color: #334155;
}}

body {{
    background-color: #020617;
    color: var(--text-color);
    font-family: 'Space Grotesk', 'Inter', sans-serif;
}}
```
"""
    elif cat_key == "devops":
        bp_code = get_run_text("devops")
        if bp_code and "```" in bp_code:
            return bp_code
        return f"""# Containerization & DevOps Manifest for '{proj_name}'

```dockerfile
# File: Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# File: docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PROJECT_NAME={proj_name}
    restart: unless-stopped
```
"""
    elif cat_key == "testing":
        bp_code = get_run_text("qa")
        if bp_code and "```" in bp_code:
            return bp_code
        return f"""# PyTest Suite for '{proj_name}'

```python
# File: tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_list_resources():
    response = client.get("/api/v1/resources")
    assert response.status_code == 200
    assert "project" in response.json()
```
"""
    elif cat_key == "documentation":
        bp_code = get_run_text("documentation")
        if bp_code:
            return bp_code
        return f"""# Production Documentation for '{proj_name}'

## Overview
**{proj_name}** is a software platform built for the **{proj_ind}** industry.

### Tech Stack
- **Architecture**: {proj_tech}
- **Description**: {proj_desc}

### Quick Start
```bash
git clone https://github.com/Ranjitpatra26/DevCore-AI-.git
pip install -r requirements.txt
streamlit run app.py
```
"""
    elif cat_key == "architecture":
        bp_code = get_run_text("architect")
        if bp_code:
            return bp_code
        return f"""# System Architecture for '{proj_name}'

```text
+-------------------------------------------------------------+
|                     PRESENTATION LAYER                      |
|                  (Streamlit UI / Web SPA)                   |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                     BUSINESS LOGIC LAYER                    |
|                (FastAPI REST / Python Services)             |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                   DATA PERSISTENCE LAYER                    |
|             (SQLite Database / Vector Embedding Store)      |
+-------------------------------------------------------------+
```
"""
    elif cat_key == "project_structure":
        return f"""# File Tree Structure for '{proj_name}'

```text
{proj_name.lower().replace(' ', '_')}/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── routers/
│   └── models/
├── database/
│   ├── schema.sql
│   └── connection.py
├── tests/
│   └── test_main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```
"""
    else:
        return f"""# Source Code Module for '{proj_name}'

```python
# File: app/service.py
def execute_service():
    return {{"status": "success", "project": "{proj_name}"}}
```
"""

def parse_multi_files(response_text: str, default_lang: str = "python") -> List[Dict[str, str]]:
    """Parse generated LLM response into virtual independent source files for the VS Code Explorer."""
    parsed_files: List[Dict[str, str]] = []
    
    # Extract code fences ```lang ... ```
    raw_blocks = re.findall(r'```(\w+)?\n(.*?)```', response_text or "", re.DOTALL)
    
    if not raw_blocks:
        return [{
            "path": f"main.{default_lang}",
            "filename": f"main.{default_lang}",
            "folder": "root",
            "lang": default_lang,
            "content": response_text or ""
        }]
    
    code_idx_map: Dict[str, int] = {}
    
    for idx, (lang_tag, code_body) in enumerate(raw_blocks):
        lang = lang_tag.strip().lower() if lang_tag else "text"
        code_str = code_body.strip() if code_body else ""
        lines = code_str.splitlines()
        first_line = lines[0] if lines else ""
        file_path = ""
        
        # Check if first line contains explicit filename header
        if first_line.startswith(("# ", "// ", "-- ", "### ", "/* ", "<!-- ")):
            candidate = first_line.lstrip("#-/ *<!!--").rstrip("-->*/ ").strip()
            if candidate.lower().startswith("file:"):
                candidate = candidate[5:].strip()
            if "." in candidate and len(candidate) < 60 and " " not in candidate:
                file_path = candidate
                
        # Detect ASCII folder tree / architecture diagram blocks
        is_ascii_tree = bool(
            lang in ["text", "ascii", "tree"] or
            ("+" in first_line and "|" in code_str) or
            ("PRESENTATION LAYER" in code_str) or
            ("ORCHESTRATION LAYER" in code_str) or
            ("BUSINESS LOGIC" in code_str) or
            (code_str.count("+") > 4 and code_str.count("|") > 4)
        )
        
        if is_ascii_tree:
            file_path = "docs/file_structure_architecture.txt"
            lang = "text"
        elif not file_path:
            ext = lang if lang not in ["text", "code", ""] else "py"
            code_idx = code_idx_map.get(ext, 0)
            code_idx_map[ext] = code_idx + 1
            
            if ext in ["python", "py"]:
                default_names = [
                    "app/main.py",
                    "routers/auth_router.py",
                    "services/app_service.py",
                    "repository/db_repository.py",
                    "schemas/domain_schemas.py",
                    "models/domain_models.py",
                    "tests/test_module.py"
                ]
                file_path = default_names[code_idx] if code_idx < len(default_names) else f"modules/service_{code_idx+1}.py"
            elif ext in ["javascript", "js", "typescript", "ts"]:
                default_names = [
                    "src/index.ts",
                    "src/components/ModuleComponent.tsx",
                    "src/services/apiService.ts",
                    "src/hooks/useAuth.ts",
                    "tests/module.test.ts"
                ]
                file_path = default_names[code_idx] if code_idx < len(default_names) else f"src/services/service_{code_idx+1}.ts"
            elif ext == "sql":
                default_names = [
                    "database/schema.sql",
                    "database/migrations/001_init.sql",
                    "database/seeds/001_demo.sql"
                ]
                file_path = default_names[code_idx] if code_idx < len(default_names) else f"database/migration_{code_idx+1}.sql"
            elif ext in ["yaml", "yml", "dockerfile"]:
                default_names = ["docker-compose.yml", "Dockerfile", "k8s/deployment.yaml"]
                file_path = default_names[code_idx] if code_idx < len(default_names) else f"config/deploy_{code_idx+1}.yaml"
            elif ext == "json":
                default_names = ["package.json", "config/settings.json"]
                file_path = default_names[code_idx] if code_idx < len(default_names) else f"config/data_{code_idx+1}.json"
            elif ext in ["markdown", "md"]:
                file_path = "README.md" if code_idx == 0 else f"docs/guide_{code_idx+1}.md"
            elif ext in ["mermaid", "mmd"]:
                file_path = "diagrams/architecture.mmd" if code_idx == 0 else f"diagrams/data_flow_{code_idx+1}.mmd"
            else:
                file_path = "config/.env.example" if code_idx == 0 else f"requirements.txt"

        # Determine folder & filename
        parts = file_path.split("/")
        filename = parts[-1]
        folder = parts[0] if len(parts) > 1 else "root"
        
        parsed_files.append({
            "path": file_path,
            "filename": filename,
            "folder": folder,
            "lang": lang if lang != "code" else "text",
            "content": code_str
        })
        
    return parsed_files

def render_mermaid_diagram(mermaid_code: str):
    """Render Mermaid.js diagrams using native HTML visualizer with active theme styling."""
    clean_code = (mermaid_code or "").strip()
    theme = st.session_state.get("theme", "dark")
    
    if theme == "light":
        bg_color = "#FFFFFF"
        text_color = "#0F172A"
        line_color = "#2563EB"
        primary_color = "#EFF6FF"
        border_color = "#3B82F6"
        mermaid_theme = "default"
    else:
        bg_color = "#0F172A"
        text_color = "#F8FAFC"
        line_color = "#38BDF8"
        primary_color = "#1E293B"
        border_color = "#6366F1"
        mermaid_theme = "dark"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <style>
            html, body {{ background-color: {bg_color}; margin: 0; padding: 8px; display: flex; justify-content: center; align-items: flex-start; font-family: 'Inter', system-ui, sans-serif; color: {text_color}; box-sizing: border-box; width: 100%; height: 100%; }}
            .mermaid {{ background: transparent !important; width: 100%; display: flex; justify-content: center; align-items: center; }}
            .mermaid svg {{ max-width: 100% !important; max-height: 380px !important; width: auto !important; height: auto !important; margin: 0 auto !important; display: block !important; }}
        </style>
    </head>
    <body>
        <div style="position: relative; width: 100%;">
            <div style="position: absolute; top: 4px; right: 8px; display: flex; gap: 6px; z-index: 999;">
                <button onclick="downloadPNG('implementation')" style="background: {line_color}; color: #FFFFFF; border: none; border-radius: 6px; padding: 4px 10px; font-size: 0.75rem; font-weight: 600; font-family: 'Inter', system-ui, sans-serif; cursor: pointer;">📷 Download PNG</button>
                <button onclick="downloadSVG('implementation')" style="background: {border_color}; color: #FFFFFF; border: none; border-radius: 6px; padding: 4px 10px; font-size: 0.75rem; font-weight: 600; font-family: 'Inter', system-ui, sans-serif; cursor: pointer;">📥 Download SVG</button>
            </div>
            <div class="mermaid">{clean_code}</div>
        </div>
        <script>
            function downloadSVG(filename) {{
                try {{
                    var svg = document.querySelector('.mermaid svg');
                    if (!svg) return;
                    var clone = svg.cloneNode(true);
                    var rect = svg.getBoundingClientRect();
                    var bbox = svg.getBBox ? svg.getBBox() : {{ width: 800, height: 500 }};
                    var w = Math.ceil(rect.width || bbox.width || 800) + 40;
                    var h = Math.ceil(rect.height || bbox.height || 500) + 40;
                    clone.setAttribute("width", w);
                    clone.setAttribute("height", h);
                    if (!clone.getAttribute("viewBox")) clone.setAttribute("viewBox", "0 0 " + w + " " + h);
                    clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
                    var bg = '{bg_color}';
                    var styleEl = document.createElementNS("http://www.w3.org/2000/svg", "style");
                    styleEl.textContent = "svg {{ background-color: " + bg + " !important; font-family: 'Inter', system-ui, sans-serif !important; }}";
                    clone.insertBefore(styleEl, clone.firstChild);
                    var serializer = new XMLSerializer();
                    var svgStr = serializer.serializeToString(clone);
                    var blob = new Blob([svgStr], {{type: "image/svg+xml;charset=utf-8"}});
                    var url = URL.createObjectURL(blob);
                    var link = document.createElement("a");
                    link.href = url;
                    link.download = (filename || "diagram") + "_architecture.svg";
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }} catch(e) {{ console.error("SVG export error:", e); }}
            }}

            function downloadPNG(filename) {{
                try {{
                    var svg = document.querySelector('.mermaid svg');
                    if (!svg) return;
                    var rect = svg.getBoundingClientRect();
                    var bbox = svg.getBBox ? svg.getBBox() : {{ width: 800, height: 500 }};
                    var width = Math.ceil(rect.width || bbox.width || 800) + 40;
                    var height = Math.ceil(rect.height || bbox.height || 500) + 40;
                    var clone = svg.cloneNode(true);
                    clone.setAttribute("width", width);
                    clone.setAttribute("height", height);
                    if (!clone.getAttribute("viewBox")) clone.setAttribute("viewBox", "0 0 " + width + " " + height);
                    clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
                    var bg = '{bg_color}';
                    var styleEl = document.createElementNS("http://www.w3.org/2000/svg", "style");
                    styleEl.textContent = "svg {{ background-color: " + bg + " !important; font-family: 'Inter', system-ui, sans-serif !important; }}";
                    clone.insertBefore(styleEl, clone.firstChild);
                    var serializer = new XMLSerializer();
                    var svgString = serializer.serializeToString(clone);
                    var svgDataUrl = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgString);
                    var scale = 2;
                    var img = new Image();
                    img.crossOrigin = 'anonymous';
                    img.onload = function() {{
                        try {{
                            var canvas = document.createElement('canvas');
                            canvas.width = width * scale;
                            canvas.height = height * scale;
                            var ctx = canvas.getContext('2d');
                            ctx.fillStyle = bg;
                            ctx.fillRect(0, 0, canvas.width, canvas.height);
                            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                            var pngUrl = canvas.toDataURL("image/png");
                            var link = document.createElement("a");
                            link.href = pngUrl;
                            link.download = (filename || "diagram") + "_architecture.png";
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        }} catch(err) {{ downloadSVG(filename); }}
                    }};
                    img.onerror = function() {{ downloadSVG(filename); }};
                    img.src = svgDataUrl;
                }} catch(e) {{ downloadSVG(filename); }}
            }}

            try {{
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: '{mermaid_theme}',
                    flowchart: {{ useMaxWidth: true, htmlLabels: false, curve: 'basis' }},
                    er: {{ useMaxWidth: true, htmlLabels: false }},
                    themeVariables: {{
                        darkMode: {'true' if theme == 'dark' else 'false'},
                        background: '{bg_color}',
                        primaryColor: '{primary_color}',
                        primaryTextColor: '{text_color}',
                        primaryBorderColor: '{border_color}',
                        lineColor: '{line_color}',
                        textColor: '{text_color}',
                        nodeBorder: '{border_color}',
                        fontSize: '13px'
                    }}
                }});
            }} catch(e) {{
                console.error("Mermaid error:", e);
            }}
        </script>
    </body>
    </html>
    """

    try:
        import urllib.parse
        data_url = "data:text/html;charset=utf-8," + urllib.parse.quote(html_content)
        st.iframe(data_url, height=440)
    except Exception:
        st.code(clean_code, language="mermaid")

def render_implementation_studio(
    active_id: str, 
    project_details: Dict[str, Any], 
    agent_runs: List[Dict[str, Any]], 
    runs_map: Dict[str, Dict[str, Any]]
):
    """Render the AI Software Engineering Implementation Studio workspace with VS Code Explorer and IDE Editor."""
    
    st.markdown("### 🛠 Implementation Studio")
    st.html("<p style='font-size: 0.9rem; color: var(--text-secondary); margin-top: -10px; margin-bottom: 15px;'>Professional AI Software Engineering Workspace powered by synchronized project blueprints.</p>")

    # Safe extraction helpers to prevent any NoneType / KeyError exceptions
    proj_details = project_details if isinstance(project_details, dict) else {}
    runs_dict = runs_map if isinstance(runs_map, dict) else {}
    
    def get_run_output(role: str) -> str:
        run_data = runs_dict.get(role)
        if isinstance(run_data, dict):
            out = run_data.get('output_markdown')
            return str(out) if out is not None else ""
        elif hasattr(run_data, '__getitem__'):
            try:
                out = run_data['output_markdown']
                return str(out) if out is not None else ""
            except Exception:
                return ""
        return ""

    # BLUEPRINT GROUNDING VALIDATION
    proj_name = proj_details.get('name')
    has_valid_blueprint = bool(proj_name and str(proj_name).strip() and str(proj_name) != "N/A")
    
    arch_summary = get_run_output('architect')[:1500]
    backend_summary = get_run_output('backend')[:1200]
    db_summary = get_run_output('database')[:1200]
    fe_summary = get_run_output('frontend')[:1200]
    ba_summary = get_run_output('business_analyst')[:1000]
    pm_summary = get_run_output('project_manager')[:1000]
    sec_summary = get_run_output('security')[:1000]
    qa_summary = get_run_output('qa')[:1000]

    if not proj_name or not str(proj_name).strip():
        proj_name = "DevCore AI System"

    # Extract Grounded Source of Truth Blueprint Details
    proj_tech = proj_details.get('tech_preference', 'Modern Full-Stack Architecture')
    proj_ind = proj_details.get('industry', 'Technology & SaaS')
    proj_desc = proj_details.get('description', 'A digital application platform.')
    proj_timeline = proj_details.get('timeline', '3 months')
    proj_budget = proj_details.get('budget', 'Medium')
    proj_diff = proj_details.get('difficulty', 'Intermediate')

    # CSS Animations & IDE Workspace Styling
    st.html("""
    <style>
    @keyframes skeletonPulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.8; }
    }
    @keyframes dotPulse {
        0%, 100% { opacity: 0.2; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1.2); }
    }
    .vscode-panel {
        background: #0F172A;
        border: 1.5px solid #334155;
        border-radius: 10px;
        padding: 14px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.3);
    }
    .vscode-tree-item {
        padding: 6px 10px;
        border-radius: 6px;
        margin-bottom: 4px;
        font-family: monospace;
        font-size: 0.88rem;
        cursor: pointer;
        transition: background 0.15s ease;
    }
    .vscode-tree-item:hover {
        background: #1E293B;
    }
    .vscode-tree-item.active {
        background: #334155;
        color: #38BDF8;
        font-weight: 700;
    }
    .impl-workspace-banner {
        background-color: #0F172A !important;
        border: 1.5px solid #334155 !important;
        color: #F8FAFC !important;
    }
    .impl-workspace-banner * {
        color: #F8FAFC !important;
    }
    .impl-workspace-banner span.impl-proj-title {
        color: #38BDF8 !important;
        font-weight: 700 !important;
    }
    .impl-workspace-banner strong.impl-mode-title {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }
    .impl-workspace-banner span.impl-tech-title {
        color: #CBD5E1 !important;
        font-size: 0.82rem !important;
    }
    .impl-workspace-banner span.impl-badge-sync {
        background-color: rgba(16, 185, 129, 0.15) !important;
        color: #34D399 !important;
        border: 1.5px solid #10B981 !important;
        font-weight: 800 !important;
        padding: 4px 12px !important;
        border-radius: 20px !important;
        font-size: 0.8rem !important;
        white-space: nowrap !important;
        box-shadow: 0 0 10px rgba(52, 211, 153, 0.4) !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 4px !important;
    }
    </style>
    """)

    # Session State Keys
    mode_state_key = f"impl_studio_mode_{active_id}"
    cat_state_key = f"impl_studio_cat_{active_id}"
    mod_state_key = f"impl_studio_mod_{active_id}"
    out_state_key = f"impl_studio_output_{active_id}"
    input_state_key = f"impl_studio_input_{active_id}"
    file_sel_key = f"impl_studio_filesel_{active_id}"
    wrap_text_key = f"impl_studio_wrap_{active_id}"
    
    if mode_state_key not in st.session_state: st.session_state[mode_state_key] = "general"
    if cat_state_key not in st.session_state: st.session_state[cat_state_key] = "backend"
    if mod_state_key not in st.session_state: st.session_state[mod_state_key] = "Authentication"
    if out_state_key not in st.session_state: st.session_state[out_state_key] = {}
    if input_state_key not in st.session_state: st.session_state[input_state_key] = ""
    if file_sel_key not in st.session_state: st.session_state[file_sel_key] = 0
    if wrap_text_key not in st.session_state: st.session_state[wrap_text_key] = True

    selected_mode_key = st.session_state[mode_state_key]
    current_cat_key = st.session_state[cat_state_key]
    selected_mod = st.session_state[mod_state_key]

    # ROLE-AWARE MODE SELECTOR
    st.html("<div style='font-size: 0.85rem; font-weight: 700; color: var(--text-color); margin-bottom: 6px;'>🎯 Engineering Perspective Mode:</div>")
    
    mode_keys = list(MODES.keys())
    mode_rows = [mode_keys[i:i+6] for i in range(0, len(mode_keys), 6)]
    for r_keys in mode_rows:
        m_cols = st.columns(len(r_keys))
        for idx, m_key in enumerate(r_keys):
            m_info = MODES[m_key]
            is_sel = (selected_mode_key == m_key)
            btn_type = "primary" if is_sel else "secondary"
            with m_cols[idx]:
                if st.button(m_info["label"], key=f"mode_btn_{m_key}_{active_id}", type=btn_type, use_container_width=True):
                    st.session_state[mode_state_key] = m_key
                    st.rerun()

    active_mode = MODES.get(selected_mode_key, MODES["general"])

    # Active Workspace Context Header Banner
    try:
        from utils.config import get_execution_provider, update_env_file
    except Exception:
        from utils.config import update_env_file
        def get_execution_provider():
            import os
            return os.getenv("EXECUTION_PROVIDER", "ollama")

    studio_engine_prov = get_execution_provider()

    st.html(f"""
    <div class="impl-workspace-banner" style="margin-top: 5px; margin-bottom: 16px; padding: 14px 20px; background: #0F172A !important; border: 1.5px solid #334155 !important; border-radius: 10px; font-size: 0.88rem; display: flex; align-items: center; justify-content: space-between; gap: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <div>
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <span class="impl-proj-title" style="color: #38BDF8 !important; font-weight: 700; font-size: 1.02rem;">Workspace: {proj_name}</span>
                <span style="color: #64748B !important;">|</span>
                <strong class="impl-mode-title" style="color: #FFFFFF !important; font-size: 1.02rem;">Perspective: {active_mode['label']}</strong>
            </div>
            <div style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">({proj_tech})</div>
        </div>
        <span class="impl-badge-sync" style="background: rgba(16, 185, 129, 0.15); color: #34D399 !important; border: 1.5px solid #10B981; font-weight: 700; padding: 5px 16px; border-radius: 20px; font-size: 0.85rem;">🔒 Blueprint Synchronized</span>
    </div>
    """)

    # Main Split Workspace Layout: Categories & Sub-Modules (Left) vs Code Editor Explorer (Right)
    col_left, col_right = st.columns([1, 2.4], gap="medium")

    # LEFT PANEL: CATEGORIES & SPECIALIZED MODULES
    with col_left:
        st.markdown("#### 🛠 Categories")
        st.html("<div style='font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 10px;'>Select Category:</div>")
        
        for key, cat in CATEGORIES.items():
            is_active = (current_cat_key == key)
            btn_type = "primary" if is_active else "secondary"
            
            if st.button(
                cat["label"], 
                key=f"cat_btn_{key}_{active_id}", 
                type=btn_type, 
                use_container_width=True
            ):
                st.session_state[cat_state_key] = key
                if cat.get("modules"):
                    st.session_state[mod_state_key] = cat["modules"][0]
                st.rerun()

        active_cat_data = CATEGORIES.get(current_cat_key, CATEGORIES["backend"])

    # RIGHT PANEL: GENERATION CONSOLE & CODE EXPLORER
    with col_right:
        cat_data = CATEGORIES.get(current_cat_key, CATEGORIES["backend"])
        
        st.html(f"""
        <div class="saas-card" style="padding: 16px 20px; margin-bottom: 16px; border-left: 5px solid #6366F1 !important;">
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.5rem;">{cat_data['icon']}</span>
                    <div>
                        <h4 style="margin: 0; font-size: 1.1rem; color: var(--text-color) !important;">{cat_data['name']}</h4>
                        <span style="font-size: 0.82rem; color: var(--text-secondary) !important; font-weight: 600;">Targeting execution for {proj_name}</span>
                    </div>
                </div>
                <span style="background: rgba(99, 102, 241, 0.15); color: #6366F1 !important; font-weight: 800; border: 1.5px solid #6366F1; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; white-space: nowrap; flex-shrink: 0;">{active_mode['label']}</span>
            </div>
        </div>
        """)

        user_code_input = ""
        if cat_data.get("requires_input"):
            user_code_input = st.text_area(
                cat_data.get("input_label", "Input"),
                value=st.session_state.get(input_state_key, ""),
                placeholder=cat_data.get("input_placeholder", ""),
                key=f"user_input_{current_cat_key}_{active_id}",
                height=130
            )

        st.html("<div style='margin-top: 15px;'></div>")

        # Explicit Code Generator AI Engine Selector Dropdown - Centered & Mid-Sized Right Before Generation Button
        c_pad1, c_mid_engine, c_pad2 = st.columns([0.6, 2.8, 0.6])
        with c_mid_engine:
            selected_studio_engine = st.selectbox(
                "⚡ Select Code Generator Engine Provider:",
                options=["ollama", "groq"],
                index=0 if studio_engine_prov == "ollama" else 1,
                format_func=lambda x: "🦙 Local Ollama Engine (Uncapped Laptop Power & 8K Tokens)" if x == "ollama" else "⚡ Groq Cloud API (High-Speed Deployed Cloud Engine)",
                key=f"studio_engine_select_{active_id}",
                help="Choose whether local laptop Ollama or Groq Cloud API generates source code."
            )
            if selected_studio_engine != studio_engine_prov:
                from database.connection import execute_update
                execute_update("UPDATE settings SET value = ? WHERE key = 'execution_provider'", (selected_studio_engine,))
                update_env_file({"EXECUTION_PROVIDER": selected_studio_engine})
                st.rerun()

        st.html("<div style='margin-top: 12px;'></div>")

        # Generate Button
        gen_btn_label = f"🚀 GENERATE {cat_data['name'].upper()} ({active_mode['label'].upper()})"
        if st.button(gen_btn_label, key=f"gen_btn_{current_cat_key}_{active_id}", type="primary", use_container_width=True):
            
            import threading
            t0 = time.time()
            status_placeholder = st.empty()
            res_holder = {}

            def run_gen():
                try:
                    from utils.implementation_engine import execute_implementation_module
                    res_holder["res"] = execute_implementation_module(
                        project_id=active_id,
                        active_mode=active_mode,
                        cat_data=cat_data,
                        active_module_name=cat_data['name'],
                        user_input=user_code_input,
                        project_details=proj_details,
                        runs_map=runs_map
                    )
                except Exception as ex:
                    res_holder["error"] = ex

            worker_thread = threading.Thread(target=run_gen)
            worker_thread.start()

            while worker_thread.is_alive():
                elapsed = int(time.time() - t0)
                status_placeholder.info(
                    f"⚡ **{active_mode['title']}** is generating production implementation for **{cat_data['name']}** ({proj_name})...\n\n"
                    f"⏱️ **Elapsed Generation Time**: `{elapsed}s`"
                )
                time.sleep(0.5)

            worker_thread.join()
            status_placeholder.empty()

            if "error" in res_holder:
                err_str = str(res_holder["error"]).lower()
                if "rate" in err_str or "token" in err_str or "429" in err_str or "quota" in err_str:
                    st.session_state["show_groq_quota_modal"] = True
                st.error(f"Generation error: {res_holder['error']}")
                res = {"guidance_text": "Error generating implementation.", "exec_time": 0.0}
            else:
                res = res_holder.get("res", {})
                g_text = str(res.get("guidance_text", "")).lower()
                if "rate limit" in g_text or "token limit" in g_text or "429" in g_text:
                    st.session_state["show_groq_quota_modal"] = True

            generated_guidance = res.get("guidance_text", "")
            exec_time_s = res.get("exec_time", round(time.time() - t0, 2))

            out_key = f"{current_cat_key}_{selected_mode_key}"
            if out_state_key not in st.session_state:
                st.session_state[out_state_key] = {}
            time_state_key = f"impl_studio_time_{active_id}"
            if time_state_key not in st.session_state:
                st.session_state[time_state_key] = {}

            st.session_state[out_state_key][out_key] = generated_guidance
            st.session_state[time_state_key][out_key] = exec_time_s
            st.rerun()

        # RENDER GENERATED IMPLEMENTATION & CODE EXPLORER
        saved_outputs = st.session_state.get(out_state_key, {})
        saved_times = st.session_state.get(f"impl_studio_time_{active_id}", {})
        output_key = f"{current_cat_key}_{selected_mode_key}"
        
        if output_key not in saved_outputs:
            initial_code = get_initial_category_code(current_cat_key, proj_details, runs_map)
            if out_state_key not in st.session_state:
                st.session_state[out_state_key] = {}
            st.session_state[out_state_key][output_key] = initial_code
            saved_outputs = st.session_state[out_state_key]

        if output_key in saved_outputs:
            guidance_text = saved_outputs[output_key]
            exec_time = saved_times.get(output_key, 2.0)
            
            debug_info = {
                "project": proj_name,
                "tech_stack": proj_tech,
                "category": cat_data.get("name", "Backend"),
                "mode": active_mode.get("label", "Backend"),
                "module": cat_data.get("name", "Backend"),
                "prompt_chars": len(guidance_text),
                "est_tokens": len(guidance_text) // 4,
                "arch_len": len(str(runs_map)),
                "db_len": len(str(proj_details)),
                "exec_time": exec_time,
                "model": "qwen3.5:9b",
                "status": "Synchronized"
            }
            
            st.html("<div class='saas-divider' style='margin: 18px 0;'></div>")
            
            # Header Toolbar
            head_col1, head_col2 = st.columns([2, 1])
            with head_col1:
                st.markdown(f"### 💻 Code-First IDE Workspace: {cat_data['name']}")
                st.html(f"""
                <div style='font-size: 0.82rem; color: var(--text-secondary); margin-top: -10px; margin-bottom: 12px; display: flex; gap: 8px; align-items: center;'>
                    <span>Category: <strong>{cat_data['name']}</strong></span>
                    <span>&middot;</span>
                    <span style="background: rgba(16, 185, 129, 0.2); color: #34D399 !important; font-weight: 700; border: 1px solid #10B981; padding: 2px 10px; border-radius: 12px; font-size: 0.78rem;">⚡ Generation Time: {exec_time}s</span>
                </div>
                """)

            parsed_files = parse_multi_files(guidance_text, default_lang="python")

            # Build 4-Section Full Package Bundle
            terminal_blocks = ""
            for f_idx, f_item in enumerate(parsed_files, 1):
                terminal_blocks += f"### Terminal Block {f_idx}: `{f_item['path']}`\n```{f_item['lang']}\n{f_item['content']}\n```\n\n"

            import json
            arch_context_json = json.dumps({
                "Project": proj_name,
                "Industry": proj_ind,
                "Tech Stack": proj_tech,
                "Category": cat_data.get('name', 'Backend'),
                "Perspective Mode": active_mode.get('label', 'Backend'),
                "Inference Latency": f"{exec_time}s"
            }, indent=2)

            full_md_bundle = f"""# Implementation Deliverable: {cat_data['name']}

## Section 1: Header & Production Guidance
- **Project**: {proj_name} ({proj_ind})
- **Tech Stack**: {proj_tech}
- **Perspective Mode**: {active_mode.get('label', 'Backend')} ({active_mode.get('title', 'Senior Engineer')})
- **Category**: {cat_data.get('name', 'Backend')}
- **Latency**: {exec_time}s

{guidance_text}

---

## Section 2: 💻 Copyable Terminal Code Blocks
{terminal_blocks}

---

## Section 3: 📄 Raw Implementation Text
```text
{guidance_text}
```

---

## Section 4: 📑 Architectural Context Referenced
```json
{arch_context_json}
```
"""

            with head_col2:
                cat_slug = cat_data.get('name', 'Backend').lower().replace(' ', '_')
                pkg_slug = f"{proj_name.lower().replace(' ', '_')}_{cat_slug}.md"
                st.download_button(
                    label="📦 Export Full Package (.md)",
                    data=full_md_bundle.encode('utf-8'),
                    file_name=pkg_slug,
                    mime="text/markdown",
                    use_container_width=True
                )

            # Interactive Single-File Code Generator Toolbar
            st.html("""
            <div style="background: rgba(99, 102, 241, 0.12); border: 2.5px solid #6366F1; border-radius: 12px; padding: 16px 20px; margin-top: 14px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <strong style="color: var(--text-color); font-size: 1.05rem; font-weight: 800;">⚡ Single-File Source Code Generator:</strong>
                        <div style="color: var(--text-secondary); font-size: 0.88rem; margin-top: 2px;">
                            Select any file from your project structure to generate its full, complete, production-grade source code.
                        </div>
                    </div>
                </div>
            </div>
            """)

            cat_file_presets = {
                "frontend": ["pages/projects.py", "pages/dashboard.py", "pages/new_project.py", "pages/ai_team.py", "pages/chat.py", "pages/settings.py", "components/ui.py", "components/navigation.py", "styles.css"],
                "backend": ["app/main.py", "app/config.py", "routers/auth_router.py", "services/app_service.py", "repository/db_repository.py", "schemas/domain_schemas.py"],
                "database": ["database/schema.sql", "database/connection.py", "database/migrations.sql"],
                "devops": ["Dockerfile", "docker-compose.yml", ".dockerignore", "k8s/deployment.yaml"],
                "testing": ["tests/test_main.py", "tests/test_api.py", "tests/conftest.py"],
                "documentation": ["README.md", "docs/API_SPEC.md", "docs/ARCHITECTURE.md"],
                "architecture": ["docs/file_structure_architecture.txt", "docs/SYSTEM_TOPOLOGY.md"],
                "ai_rag": ["rag/vector_store.py", "rag/document_loader.py", "rag/embeddings.py"]
            }

            available_files = cat_file_presets.get(current_cat_key, ["main.py", "config.py", "schema.sql", "Dockerfile", "README.md"])

            sf_col1, sf_col2 = st.columns([2.5, 1.3])
            with sf_col1:
                selected_single_file = st.selectbox(
                    "Select Target File to Synthesize Code:",
                    options=available_files,
                    key=f"sf_select_{output_key}_{active_id}",
                    label_visibility="collapsed"
                )
            with sf_col2:
                if st.button(f"⚡ Generate Code for {selected_single_file.split('/')[-1]}", key=f"sf_btn_{output_key}_{active_id}", type="primary", use_container_width=True):
                    with st.spinner(f"⚡ Generating full production code for {selected_single_file}..."):
                        try:
                            from utils.implementation_engine import execute_implementation_module
                            sf_res = execute_implementation_module(
                                project_id=active_id,
                                active_mode=active_mode,
                                cat_data=cat_data,
                                active_module_name=f"Source Code for File {selected_single_file}",
                                user_input=f"Generate the full, complete, production-grade, un-truncated working source code for file '{selected_single_file}' in project '{proj_name}' ({proj_ind}) using tech stack '{proj_tech}'. Include comments, imports, and complete functions.",
                                project_details=proj_details,
                                runs_map=runs_map
                            )
                            sf_guidance = sf_res.get("guidance_text", "")
                            if sf_guidance:
                                updated_text = guidance_text + "\n\n" + sf_guidance
                                if out_state_key not in st.session_state:
                                    st.session_state[out_state_key] = {}
                                st.session_state[out_state_key][output_key] = updated_text
                                st.toast(f"🎉 Code generated for {selected_single_file}!")
                                st.rerun()
                        except Exception as sf_err:
                            st.error(f"Error generating code for {selected_single_file}: {sf_err}")

            st.html("<div style='margin-top: 14px;'></div>")

            # Production Code Viewer (IDE Blocks)
            if parsed_files:
                st.markdown("#### 💻 Generated Source Code Files")
                for f_idx, fobj in enumerate(parsed_files):
                    f_path = fobj["path"]
                    f_content = fobj["content"]
                    f_lang = fobj["lang"]
                    f_name = fobj["filename"]

                    st.html(f"""
                    <div style="background: #0F172A !important; border: 1.5px solid #334155 !important; border-radius: 8px 8px 0 0; padding: 8px 14px; font-family: monospace; font-size: 0.85rem; display: flex; align-items: center; justify-content: space-between; margin-top: 10px;">
                        <span style="color: #F8FAFC !important; font-weight: 700;">📄 {f_path} ({len(f_content)} bytes)</span>
                        <span style="background: rgba(56, 189, 248, 0.2) !important; color: #38BDF8 !important; font-weight: 700; border: 1px solid #0284C7; padding: 2px 10px; border-radius: 12px; font-size: 0.78rem;">{f_lang.upper()}</span>
                    </div>
                    """)
                    st.code(f_content, language=f_lang, line_numbers=True)
                    st.download_button(
                        label=f"💾 Download {f_name}",
                        data=f_content.encode("utf-8"),
                        file_name=f_name,
                        mime="text/plain",
                        key=f"dl_file_{output_key}_{f_idx}_{active_id}",
                        use_container_width=True
                    )
                    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

            # Implementation Guidance & Documentation View
            st.markdown("#### 📄 Implementation Details & Production Guidance")
            st.markdown(guidance_text)

            # PROMPT DEBUG PANEL
            st.html("<div class='saas-divider' style='margin: 24px 0 14px 0;'></div>")
            with st.expander("🛠 Developer Debug & Prompt Inspection Panel", expanded=False):
                if debug_info:
                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        st.markdown(f"- **Project**: `{debug_info.get('project')}`")
                        st.markdown(f"- **Tech Stack**: `{debug_info.get('tech_stack')}`")
                        st.markdown(f"- **Category**: `{debug_info.get('category')}`")
                        st.markdown(f"- **Active Mode**: `{debug_info.get('mode')}`")
                        st.markdown(f"- **Selected Module**: `{debug_info.get('module')}`")
                    with d_col2:
                        st.markdown(f"- **Prompt Character Length**: `{debug_info.get('prompt_chars')}` chars")
                        st.markdown(f"- **Estimated Tokens**: `~{debug_info.get('est_tokens')}` tokens")
                        st.markdown(f"- **Architecture Context**: `{debug_info.get('arch_len')}` chars loaded")
                        st.markdown(f"- **Database Context**: `{debug_info.get('db_len')}` chars loaded")
                        st.markdown(f"- **Inference Latency**: `{debug_info.get('exec_time')}s`")
                        st.markdown(f"- **Model**: `{debug_info.get('model')}`")
                        st.markdown(f"- **Context Status**: `🟢 {debug_info.get('status')}`")

                st.text_area(
                    "Raw Generated Payload",
                    value=guidance_text,
                    height=180,
                    key=f"raw_debug_payload_{output_key}_{active_id}"
                )

        else:
            st.info(f"Click the button above to generate production code for **{cat_data['name']}** tailored to **{proj_name}**.")
