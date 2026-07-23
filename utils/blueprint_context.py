"""
Blueprint Context Module for DevCore AI Operating System.
Responsible ONLY for loading, extracting, and assembling structured project blueprint context.
Optimized with in-memory caching and structured logging.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from database.connection import execute_query

logger = logging.getLogger("ai_software_company.blueprint_context")

# Context cache store to avoid redundant SQLite queries during a session
_CONTEXT_CACHE: Dict[str, Dict[str, Any]] = {}

def load_blueprint_context(
    project_id: str,
    project_details: Optional[Dict[str, Any]] = None,
    runs_map: Optional[Dict[str, Dict[str, Any]]] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Extract and assemble grounded source-of-truth project blueprint context.
    
    Returns a structured context dictionary containing metadata, tech stack,
    and agent outputs for all engineering roles.
    """
    if use_cache and project_id and project_id in _CONTEXT_CACHE:
        cached = _CONTEXT_CACHE[project_id]
        if time.time() - cached.get("_cached_at", 0) < 300:  # 5-min TTL
            logger.debug(f"Blueprint context cache HIT for project {project_id}")
            return cached["data"]

    t0 = time.time()
    details = project_details if isinstance(project_details, dict) else {}
    runs_dict = runs_map if isinstance(runs_map, dict) else {}

    # If project_details is empty, attempt to fetch from SQLite
    if not details and project_id:
        try:
            rows = execute_query(
                "SELECT id, name, description, industry, tech_preference, timeline, budget, difficulty FROM projects WHERE id = ?",
                (project_id,)
            )
            if rows:
                details = dict(rows[0])
        except Exception as e:
            logger.warning(f"Failed to load project details for {project_id}: {e}")

    # If runs_map is empty, attempt to fetch agent runs from SQLite
    if not runs_dict and project_id:
        try:
            run_rows = execute_query(
                "SELECT agent_role, output_markdown FROM agent_runs WHERE project_id = ?",
                (project_id,)
            )
            runs_dict = {row['agent_role']: dict(row) for row in run_rows if row.get('agent_role')}
        except Exception as e:
            logger.warning(f"Failed to load agent runs for {project_id}: {e}")

    def get_role_output(role: str) -> str:
        run_data = runs_dict.get(role)
        if isinstance(run_data, dict):
            out = run_data.get('output_markdown')
            return str(out) if out is not None else ""
        return ""

    proj_name = details.get('name', '')
    has_valid_name = bool(proj_name and str(proj_name).strip() and str(proj_name) != "N/A")

    arch_summary = get_role_output('architect')
    backend_summary = get_role_output('backend')
    db_summary = get_role_output('database')
    fe_summary = get_role_output('frontend')
    ba_summary = get_role_output('business_analyst')
    pm_summary = get_role_output('project_manager')
    sec_summary = get_role_output('security')
    qa_summary = get_role_output('qa')
    devops_summary = get_role_output('devops')

    is_grounded = bool(has_valid_name and (arch_summary or backend_summary or db_summary or fe_summary or runs_dict or details))

    result_ctx = {
        "project_id": project_id,
        "name": proj_name if has_valid_name else "Custom Software Application",
        "industry": details.get('industry', 'Technology & SaaS'),
        "tech_preference": details.get('tech_preference', 'Modern Full-Stack Architecture'),
        "description": details.get('description', 'A digital application platform.'),
        "timeline": details.get('timeline', '3 months'),
        "budget": details.get('budget', 'Medium'),
        "difficulty": details.get('difficulty', 'Intermediate'),
        "is_grounded": is_grounded,
        "summaries": {
            "architect": arch_summary[:1500],
            "backend": backend_summary[:1200],
            "database": db_summary[:1200],
            "frontend": fe_summary[:1200],
            "business_analyst": ba_summary[:1000],
            "project_manager": pm_summary[:1000],
            "security": sec_summary[:1000],
            "qa": qa_summary[:1000],
            "devops": devops_summary[:1000]
        }
    }

    if project_id:
        _CONTEXT_CACHE[project_id] = {
            "data": result_ctx,
            "_cached_at": time.time()
        }

    t1 = time.time()
    logger.info(f"Loaded blueprint context for project '{proj_name}' in {round(t1-t0, 3)}s (is_grounded={is_grounded})")
    return result_ctx

def invalidate_blueprint_cache(project_id: str):
    """Clear cached context for a specific project when its blueprint is updated."""
    if project_id in _CONTEXT_CACHE:
        del _CONTEXT_CACHE[project_id]
        logger.info(f"Invalidated blueprint cache for project {project_id}")
