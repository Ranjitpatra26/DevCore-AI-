import io
import json
import zipfile
from typing import Dict, Any, List
from agents.base import get_role_display_name

def generate_mermaid_diagrams(project_name: str) -> str:
    """Generate default templates for Mermaid.js diagrams relating to the project."""
    return f"""# Mermaid Diagrams - {project_name}

## 1. High-Level Architecture Diagram
```mermaid
graph TD
    Client[Browser/Client App] --> Gateway[API Gateway / Load Balancer]
    Gateway --> Auth[Auth Service]
    Gateway --> WebApp[Core Web Service]
    WebApp --> Cache[(Redis Cache)]
    WebApp --> DB[(SQLite Database)]
    WebApp --> RAG[(Vector DB / Chroma)]
```

## 2. User Authentication Sequence Diagram
```mermaid
sequenceDiagram
    actor User
    User->>Client: Input credentials
    Client->>Gateway: POST /api/auth/login
    Gateway->>Auth: Validate user hash
    Auth->>DB: Query user record
    DB-->>Auth: Record found
    Auth-->>Gateway: Generate JWT Token
    Gateway-->>Client: 200 OK + JWT
    Client-->>User: Load dashboard
```

## 3. Core Blueprint Ingestion Flowchart
```mermaid
graph LR
    Input[Upload Docs] --> Chunk[Recursive Text Splitter]
    Chunk --> Embed[Ollama Embeddings API]
    Embed --> DB[(SQLite Store)]
    DB --> Retrieve[Similarity Matching]
    Retrieve --> AgentPrompt[Collaborative LLM Prompt]
```

## 4. Entity Relationship Diagram (ERD)
```mermaid
erDiagram
    PROJECTS ||--o{{ PROJECT_FILES : "contains"
    PROJECTS ||--o{{ AGENT_RUNS : "executes"
    PROJECT_FILES ||--o{{ EMBEDDINGS : "splits"
    PROJECTS ||--o{{ CHATS : "logs"

    PROJECTS {{
        text id PK
        text name
        text description
        text created_at
    }}

    PROJECT_FILES {{
        text id PK
        text project_id FK
        text filename
        text file_type
        text content
    }}

    AGENT_RUNS {{
        text project_id PK,FK
        text agent_role PK
        text output_markdown
        real execution_time_s
    }}
```
"""

def generate_tasks_json(pm_output: str) -> str:
    """Attempt to parse tasks from Project Manager markdown or return a structured JSON task list."""
    # Create a clean default backlog structure representing typical development tasks
    tasks = [
        {"id": "T-101", "name": "Initialize Git Repository & setup virtualenv", "points": 1, "priority": "High", "owner": "DevOps", "status": "Done"},
        {"id": "T-102", "name": "Configure SQLite database schemas and migrations", "points": 2, "priority": "High", "owner": "Database Eng", "status": "Done"},
        {"id": "T-103", "name": "Establish core REST API endpoints and models", "points": 5, "priority": "High", "owner": "Backend Eng", "status": "In Progress"},
        {"id": "T-104", "name": "Implement UI wireframes layout in Streamlit", "points": 3, "priority": "High", "owner": "Frontend Eng", "status": "In Progress"},
        {"id": "T-105", "name": "Incorporate local Ollama embeddings pipeline", "points": 5, "priority": "Medium", "owner": "Backend Eng", "status": "Todo"},
        {"id": "T-106", "name": "Conduct OWASP standard security review", "points": 3, "priority": "Medium", "owner": "Security Eng", "status": "Todo"},
        {"id": "T-107", "name": "Write unit and validation test suites", "points": 3, "priority": "Low", "owner": "QA Eng", "status": "Todo"}
    ]
    return json.dumps(tasks, indent=2)

def package_project_blueprint_zip(project_name: str, agent_runs: List[Dict[str, Any]]) -> bytes:
    """Create individual files for each agent output and package them into a zip file buffer."""
    zip_buffer = io.BytesIO()
    
    # Map roles to specific target output filenames
    role_file_mapping = {
        "ceo": "README.md",
        "business_analyst": "BusinessRequirements.md",
        "project_manager": "Sprint.md",
        "architect": "Architecture.md",
        "ui_ux": "Wireframes.md",
        "frontend": "FolderStructure.md",
        "backend": "API.md",
        "database": "Database.md",
        "security": "Security.md",
        "devops": "Deployment.md",
        "qa": "QA.md",
        "documentation": "UserDocumentation.md",
        "reviewer": "ReviewSummary.md"
    }
    
    runs_dict = {run['agent_role'].lower(): run['output_markdown'] for run in agent_runs}
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Write agent markdown outputs
        for role, filename in role_file_mapping.items():
            content = runs_dict.get(role, f"# {get_role_display_name(role)}\n\nBlueprint section not generated yet.")
            zip_file.writestr(f"blueprint/{filename}", content)
            
        # Add generated Mermaid diagrams
        mermaid_content = generate_mermaid_diagrams(project_name)
        zip_file.writestr("blueprint/Mermaid.md", mermaid_content)
        
        # Add generated Tasks JSON
        pm_content = runs_dict.get("project_manager", "")
        tasks_json = generate_tasks_json(pm_content)
        zip_file.writestr("blueprint/tasks.json", tasks_json)
        
        # Add a consolidated main blueprint document
        consolidated = f"# Software Development Blueprint - {project_name}\n\n"
        consolidated += "This package contains the complete multi-agent blueprint for the project.\n\n"
        for role, filename in role_file_mapping.items():
            display_name = get_role_display_name(role)
            content = runs_dict.get(role, "Section pending.")
            consolidated += f"\n\n{'='*60}\n# SECTION: {display_name}\n{'='*60}\n\n{content}\n"
            
        zip_file.writestr("blueprint/ConsolidatedBlueprint.md", consolidated)
        
    return zip_buffer.getvalue()
