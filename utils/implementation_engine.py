"""
Implementation Engine Module for DevCore AI Operating System.
Provides Code-First Implementation Generator (80% Code, 20% Explanation).
"""

import time
import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from utils.blueprint_context import load_blueprint_context
from utils.prompt_builder import build_implementation_prompt, STRICT_SYSTEM_PROMPT
from utils.telemetry import telemetry, response_cache
from utils.ollama_client import sanitize_and_eliminate_placeholders, query_ollama

logger = logging.getLogger("ai_software_company.implementation_engine")

def validate_generation_request(
    project_id: str,
    ctx: Dict[str, Any],
    active_mode: Optional[Dict[str, Any]],
    cat_data: Optional[Dict[str, Any]],
    active_module_name: Optional[str]
) -> Tuple[bool, Optional[str]]:
    """Prerequisites validation prior to calling LLM generator."""
    if not project_id or not str(project_id).strip():
        return False, "Validation Error: No active project selected."

    if not ctx or not isinstance(ctx, dict):
        return False, "Validation Error: Project blueprint context could not be loaded."

    if not ctx.get("is_grounded", False):
        return False, "Validation Error: Blueprint Synchronization Incomplete. Please run Agent Blueprint generation first."

    if not active_mode or not isinstance(active_mode, dict) or not active_mode.get("label"):
        return False, "Validation Error: No valid Engineering Mode persona selected."

    if not cat_data or not isinstance(cat_data, dict) or not cat_data.get("name"):
        return False, "Validation Error: No valid Implementation Category selected."

    if not active_module_name or not str(active_module_name).strip():
        return False, "Validation Error: No valid Target Module selected."

    return True, None

def calculate_smart_token_budget(cat_key: str = "", user_input: str = "", difficulty: str = "") -> int:
    """Smartly calculate token budget based on category complexity, project difficulty, and custom instruction scope."""
    cat_lower = str(cat_key).lower()
    input_lower = str(user_input).lower()
    diff_lower = str(difficulty).lower()

    if "beginner" in diff_lower:
        return 4096  # Lean, educational, easy-to-read code snippets for beginners

    # Heavy multi-file & architectural categories get 8192 tokens for deep, complete code generation
    heavy_categories = {"backend", "frontend", "database", "ai_rag", "devops", "architecture", "project_structure", "ui_components", "sql_schema", "pytest_suite"}
    heavy_keywords = {"full", "complete", "exhaustive", "all", "enterprise", "multi", "entire", "production", "system", "code", "file"}

    if cat_lower in heavy_categories or any(kw in input_lower for kw in heavy_keywords) or "enterprise" in diff_lower or "advanced" in diff_lower:
        return 8192
    return 6144

def execute_implementation_module(*args, **kwargs) -> Dict[str, Any]:
    """
    Code-First Implementation Generator for Implementation Studio.
    Smartly calculates dynamic token budget (4096 to 6144 tokens), enforces blueprint context synchronization, and cleans output.
    """
    t0 = time.time()
    
    project_id = kwargs.get("project_id", "")
    active_mode = kwargs.get("active_mode", {})
    cat_data = kwargs.get("cat_data", {})
    active_module_name = kwargs.get("active_module_name", "")
    user_input = kwargs.get("user_input", "")
    project_details = kwargs.get("project_details")
    runs_map = kwargs.get("runs_map")
    ollama_query_fn = kwargs.get("ollama_query_fn")
    ctx = kwargs.get("ctx")

    # Positional arg mapping flexibility
    if args:
        if isinstance(args[0], str) and not project_id:
            project_id = args[0]
            if len(args) > 1 and isinstance(args[1], dict): active_mode = args[1]
            if len(args) > 2 and isinstance(args[2], dict): cat_data = args[2]
            if len(args) > 3 and isinstance(args[3], str): active_module_name = args[3]
            if len(args) > 4 and isinstance(args[4], str): user_input = args[4]
            if len(args) > 5 and isinstance(args[5], dict): project_details = args[5]
            if len(args) > 6 and isinstance(args[6], dict): runs_map = args[6]
        elif isinstance(args[0], dict) and not active_mode:
            active_mode = args[0]
            if len(args) > 1 and isinstance(args[1], dict): cat_data = args[1]
            if len(args) > 2 and isinstance(args[2], str): active_module_name = args[2]
            if len(args) > 3 and isinstance(args[3], dict): ctx = args[3]
            if len(args) > 4 and isinstance(args[4], str): user_input = args[4]

    if not ctx:
        ctx = load_blueprint_context(project_id, project_details, runs_map)

    is_valid, err_msg = validate_generation_request(project_id, ctx, active_mode, cat_data, active_module_name)
    if not is_valid:
        logger.error(err_msg)
        return {"success": False, "error": err_msg, "guidance_text": "", "context": ctx}

    prompts = build_implementation_prompt(
        active_mode=active_mode,
        cat_data=cat_data,
        active_module_name=active_module_name,
        ctx=ctx,
        user_input=user_input
    )

    proj_name = ctx.get("name", "Synchronized Project") if isinstance(ctx, dict) else "Synchronized Project"
    query_fn = ollama_query_fn or query_ollama
    
    # Smartly calculate token budget based on scope, category complexity, and difficulty tier
    cat_key = cat_data.get("name", "").lower().replace(" ", "_") if isinstance(cat_data, dict) else ""
    proj_diff = ctx.get("difficulty", "Intermediate") if isinstance(ctx, dict) else "Intermediate"
    smart_tokens = calculate_smart_token_budget(cat_key=cat_key, user_input=user_input, difficulty=proj_diff)

    try:
        raw_output = query_fn(
            system_prompt=prompts["system_prompt"],
            user_prompt=prompts["user_prompt"],
            agent_role=active_mode.get("agent_role", "backend") if isinstance(active_mode, dict) else "backend",
            is_consultation=False,
            project_name=proj_name,
            override_max_tokens=smart_tokens
        )

        cleaned_text = sanitize_and_eliminate_placeholders(raw_output, proj_name)
        t1 = time.time()
        latency_s = round(t1 - t0, 2)
        
        telemetry.record_request(
            latency_s=latency_s,
            prompt_chars=len(prompts["system_prompt"]) + len(prompts["user_prompt"]),
            response_chars=len(cleaned_text),
            from_cache=False
        )

        logger.info(f"Generated implementation for '{active_module_name}' in {latency_s}s")
        return {
            "success": True,
            "error": None,
            "guidance_text": cleaned_text,
            "context": ctx,
            "exec_time": latency_s
        }
    except Exception as e:
        logger.error(f"Implementation execution error for '{active_module_name}': {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "guidance_text": f"### Error Generating Implementation\n{str(e)}",
            "context": ctx,
            "exec_time": round(time.time() - t0, 2)
        }

def generate_project_manifest(
    project_id: str,
    active_mode: Dict[str, Any],
    cat_data: Dict[str, Any],
    active_module_name: str,
    project_details: Optional[Dict[str, Any]] = None,
    runs_map: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Optional manifest helper."""
    ctx = load_blueprint_context(project_id, project_details, runs_map)
    cat_name = cat_data.get("name", "Backend").lower()
    if "backend" in cat_name or "ai" in cat_name:
        manifest_files = [
            {"path": f"backend/{active_module_name.lower()}/router.py", "filename": "router.py", "folder": f"backend/{active_module_name.lower()}", "lang": "python"},
            {"path": f"backend/{active_module_name.lower()}/service.py", "filename": "service.py", "folder": f"backend/{active_module_name.lower()}", "lang": "python"},
            {"path": f"backend/{active_module_name.lower()}/repository.py", "filename": "repository.py", "folder": f"backend/{active_module_name.lower()}", "lang": "python"},
            {"path": f"backend/{active_module_name.lower()}/models.py", "filename": "models.py", "folder": f"backend/{active_module_name.lower()}", "lang": "python"},
            {"path": f"backend/{active_module_name.lower()}/schemas.py", "filename": "schemas.py", "folder": f"backend/{active_module_name.lower()}", "lang": "python"},
            {"path": "README.md", "filename": "README.md", "folder": "root", "lang": "markdown"}
        ]
    else:
        manifest_files = [
            {"path": f"src/{active_module_name.lower()}_module.py", "filename": f"{active_module_name.lower()}_module.py", "folder": "src", "lang": "python"},
            {"path": "README.md", "filename": "README.md", "folder": "root", "lang": "markdown"}
        ]
    return {"success": True, "manifest": manifest_files}

def generate_single_file(
    project_id: str,
    target_file_path: str,
    active_mode: Dict[str, Any],
    cat_data: Dict[str, Any],
    active_module_name: str,
    project_details: Optional[Dict[str, Any]] = None,
    runs_map: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Single file generator helper."""
    res = execute_implementation_module(project_id, active_mode, cat_data, active_module_name, f"Generate file {target_file_path}", project_details, runs_map)
    return {"success": res["success"], "file_path": target_file_path, "code": res["guidance_text"]}
