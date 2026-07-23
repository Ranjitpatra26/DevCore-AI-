import time
from typing import Dict, Any, List
from database.connection import execute_update, execute_query
from agents.prompts import SYSTEM_PROMPTS
from utils.ollama_client import query_ollama, get_ollama_config
from utils.config import AGENT_BLUEPRINT_MAX_TOKENS
from rag.vector_store import query_project_vector_store

def get_role_display_name(role: str) -> str:
    """Map the system key role name to user friendly capitalized label."""
    mapping = {
        "ceo": "CEO",
        "business_analyst": "Business Analyst",
        "project_manager": "Project Manager",
        "architect": "Software Architect",
        "ui_ux": "UI UX Designer",
        "frontend": "Frontend Engineer",
        "backend": "Backend Engineer",
        "database": "Database Engineer",
        "security": "Security Engineer",
        "devops": "DevOps Engineer",
        "qa": "QA Engineer",
        "documentation": "Documentation Engineer",
        "reviewer": "Reviewer Agent"
    }
    return mapping.get(role.lower(), role.capitalize())

def get_complexity_directives(difficulty: str = "Intermediate", budget: str = "Medium", timeline: str = "3 months") -> str:
    """Generate adaptive blueprint instructions based on Implementation Complexity, Budget, and Delivery Schedule."""
    diff_lower = str(difficulty).lower()
    budget_lower = str(budget).lower()
    timeline_lower = str(timeline).lower()

    if "beginner" in diff_lower:
        complexity_guide = (
            "COMPLEXITY ADAPTATION (BEGINNER TIER):\n"
            "- Target Audience: Beginners, students, and early-stage developers.\n"
            "- Tone & Style: Educational, clear, encouraging, and easy to follow. Explain key concepts step-by-step with clear code comments.\n"
            "- Architectural Pattern: Simple Monolithic or Single-Service architecture. Minimal boilerplate; avoid unnecessary microservices or complex Kubernetes setups.\n"
            "- Database & Code: Straightforward relational schema, simple queries, clear variable naming, and easy-to-run local setup commands."
        )
    elif "intermediate" in diff_lower:
        complexity_guide = (
            "COMPLEXITY ADAPTATION (INTERMEDIATE TIER):\n"
            "- Target Audience: Professional software engineers and mid-level developers.\n"
            "- Tone & Style: Standard professional engineering rigor.\n"
            "- Architectural Pattern: Clean MVC / Layered architecture, REST APIs, Redis caching, ORM data models, and standard Docker setup."
        )
    elif "advanced" in diff_lower:
        complexity_guide = (
            "COMPLEXITY ADAPTATION (ADVANCED TIER):\n"
            "- Target Audience: Senior software architects and technical leads.\n"
            "- Tone & Style: Deep technical specifications, rigorous architectural patterns, and production trade-offs.\n"
            "- Architectural Pattern: Distributed services, worker queues (Celery/Kafka), JWT/OAuth2 RBAC authorization, automated CI/CD workflows, and comprehensive pytest coverage."
        )
    else:  # Enterprise Scale
        complexity_guide = (
            "COMPLEXITY ADAPTATION (ENTERPRISE SCALE TIER):\n"
            "- Target Audience: Principal Enterprise Architects, CTOs, and Security Compliance Officers.\n"
            "- Tone & Style: Enterprise-grade architectural rigor, compliance standards, high availability, and zero-trust security.\n"
            "- Architectural Pattern: Multi-region microservices, Event-Driven Kafka architecture, Zero-Trust RBAC, HIPAA/SOC2/GDPR compliance controls, Kubernetes Helm charts, blue-green deployment pipelines, disaster recovery, and Grafana/Prometheus telemetry."
        )

    if "low" in budget_lower or "5k" in budget_lower:
        budget_guide = "BUDGET ADAPTATION: Cost-optimized single-server/VPS or serverless infrastructure. Utilize open-source tools and lean resource allocation."
    elif "high" in budget_lower or "50k" in budget_lower or "150k" in budget_lower:
        budget_guide = "BUDGET ADAPTATION: Multi-zone HA cloud infrastructure (AWS/GCP), dedicated databases, managed caching, and staging environments."
    else:
        budget_guide = "BUDGET ADAPTATION: Standard cloud managed services (AWS ECS/App Runner, managed Postgres), commercial API integrations."

    if "1 month" in timeline_lower or "mvp" in timeline_lower:
        schedule_guide = "SCHEDULE ADAPTATION (1 MONTH MVP): Rapid MVP execution roadmap. Focus strictly on P0 core features, 2 quick Sprints, lean backlog, and immediate market delivery."
    elif "6 month" in timeline_lower:
        schedule_guide = "SCHEDULE ADAPTATION (6 MONTHS): 8 Sprints, full feature set, comprehensive security audit, load testing, and detailed documentation."
    elif "12 month" in timeline_lower or "platform" in timeline_lower:
        schedule_guide = "SCHEDULE ADAPTATION (12 MONTHS / ENTERPRISE PLATFORM): Multi-quarter roadmap (Q1-Q4), 16+ Sprints, continuous deployment, and enterprise rollout phases."
    else:
        schedule_guide = "SCHEDULE ADAPTATION (3 MONTHS): 4 Sprints, complete feature set, standard QA test suite, and deployment checklist."

    return f"{complexity_guide}\n\n{budget_guide}\n\n{schedule_guide}"

def run_agent(project_id: str, agent_role: str, state: Dict[str, Any]) -> str:
    """Execute a single agent's node in the planning pipeline and store results in SQLite."""
    start_time = time.time()
    
    # 1. Retrieve system prompt for the role
    system_prompt = SYSTEM_PROMPTS.get(agent_role.lower(), "You are a helpful software engineer.")
    
    # 2. Gather RAG context matching the agent's role responsibility
    rag_query = f"{get_role_display_name(agent_role)} features requirements tech stack database deployment security QA"
    rag_matches = query_project_vector_store(project_id, rag_query, top_k=5)
    rag_context_str = ""
    if rag_matches:
        rag_context_str = "\n--- RELEVANT SRS / SPECIFICATION CONTEXT ---\n"
        for idx, match in enumerate(rag_matches):
            rag_context_str += f"[{idx+1}] Source: {match['filename']}\n{match['text']}\n\n"
            
    # 3. Assemble inputs from preceding agents
    # Fetch all existing agent runs from database for this project
    previous_runs = execute_query(
        "SELECT agent_role, output_markdown FROM agent_runs WHERE project_id = ? AND agent_role != ?",
        (project_id, agent_role)
    )
    
    previous_context = ""
    if previous_runs:
        previous_context = "\n--- COMPREHENSIVE BLUEPRINTS FROM PRECEDING AGENTS ---\n"
        for run in previous_runs:
            role_name = get_role_display_name(run['agent_role'])
            raw_text = run.get('output_markdown', '') or ""
            # Include up to 2500 characters per preceding agent for maximum context depth
            output_snippet = raw_text[:2500] + ("\n... [Extended Blueprint Context]" if len(raw_text) > 2500 else "")
            previous_context += f"### {role_name} Blueprint Summary:\n{output_snippet}\n\n"

    complexity_directives = get_complexity_directives(
        difficulty=state.get('difficulty', 'Intermediate'),
        budget=state.get('budget', 'Medium'),
        timeline=state.get('timeline', '3 months')
    )
            
    # 4. Construct final user prompt with dynamic complexity conditioning
    user_prompt = f"""PROJECT DETAILS & TIER CONSTRAINTS:
Project Name: {state.get('project_name', 'Unnamed Project')}
Description: {state.get('description', '')}
Industry: {state.get('industry', 'General')}
Tech Stack Preference: {state.get('tech_preference', 'None')}
Implementation Complexity: {state.get('difficulty', 'Intermediate')}
Budget Level: {state.get('budget', 'Medium')}
Delivery Schedule: {state.get('timeline', '3 months')}

{complexity_directives}

{rag_context_str}
{previous_context}

INSTRUCTIONS FOR MAXIMUM DEPTH BLUEPRINT OUTPUT:
You are performing your role as: {get_role_display_name(agent_role)}.
Begin your document with an inspiring, encouraging engineering lead note highlighting why this software project is designed for high success.
Write an EXHAUSTIVE, production-grade, highly detailed, deep markdown blueprint section EXCLUSIVELY for your role as defined in your system prompt.
Target output length: Generate AT LEAST 1,300 to 2,000 words per node of exhaustive, un-truncated, production-grade technical specification. Expand every single section with complete code snippets, explicit schemas, full tables, and step-by-step guides.
Do NOT use placeholders, ellipsis ("..."), or abbreviated summaries. Utilize your full 8,192 token capacity to provide worthy, high-value, and production-ready technical content.
"""
    
    # 5. Query Ollama with validation and automatic fallback recovery
    output_markdown = query_ollama(
        system_prompt,
        user_prompt,
        agent_role=agent_role,
        override_max_tokens=AGENT_BLUEPRINT_MAX_TOKENS
    )
    if not output_markdown or not output_markdown.strip():
        from utils.ollama_client import generate_simulated_response
        output_markdown = generate_simulated_response(system_prompt, user_prompt, agent_role=agent_role)
        
    # 6. Calculate execution time
    elapsed_time = round(time.time() - start_time, 2)
    
    # 7. Persist to SQLite
    execute_update(
        """
        INSERT INTO agent_runs (project_id, agent_role, output_markdown, execution_time_s, timestamp)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(project_id, agent_role) DO UPDATE SET
            output_markdown=excluded.output_markdown,
            execution_time_s=excluded.execution_time_s,
            timestamp=CURRENT_TIMESTAMP
        """,
        (project_id, agent_role, output_markdown, elapsed_time)
    )
    
    # 8. Record an audit log entry in SQLite chats table as a system notification
    log_msg = f"Completed analysis in {elapsed_time}s."
    execute_update(
        "INSERT INTO chats (project_id, agent_role, sender, message) VALUES (?, ?, ?, ?)",
        (project_id, agent_role, "system", log_msg)
    )
    
    return output_markdown
