"""
Consultation Engine Module for DevCore AI Operating System.
Responsible ONLY for Consultation Chat generation logic, context assembly, and conversation memory handling.
Optimized with response caching and telemetry.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from utils.blueprint_context import load_blueprint_context
from utils.prompt_builder import build_consultation_prompt
from utils.telemetry import telemetry, response_cache

logger = logging.getLogger("ai_software_company.consultation_engine")

def execute_consultation_query(
    project_id: str,
    user_question: str,
    project_details: Optional[Dict[str, Any]] = None,
    runs_map: Optional[Dict[str, Dict[str, Any]]] = None,
    messages_payload: Optional[List[Dict[str, str]]] = None,
    ollama_query_fn: Optional[Any] = None,
    use_cache: bool = True
) -> str:
    """
    Execute a consultation chat query grounded in the project blueprint.
    Includes response caching and telemetry tracking.
    """
    t0 = time.time()
    ctx = load_blueprint_context(project_id, project_details, runs_map)
    system_prompt, user_prompt = build_consultation_prompt(ctx, user_question)

    # Check Response Cache
    if use_cache and not messages_payload:
        cached_res = response_cache.get(project_id, "consultation", "consultant", "query", user_question)
        if cached_res:
            t1 = time.time()
            telemetry.record_request(round(t1-t0, 3), len(system_prompt) + len(user_prompt), len(cached_res), from_cache=True)
            logger.info(f"Serving cached consultation query for project '{ctx.get('name')}'")
            return cached_res

    logger.info(f"Executing consultation query for project '{ctx.get('name')}'...")

    try:
        if ollama_query_fn:
            res = ollama_query_fn(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                messages_payload=messages_payload,
                is_consultation=True
            )
        else:
            from utils.ollama_client import query_ollama
            res = query_ollama(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                messages_payload=messages_payload,
                is_consultation=True
            )

        t1 = time.time()
        latency_s = round(t1 - t0, 2)

        if use_cache and res and not messages_payload:
            response_cache.set(project_id, "consultation", "consultant", "query", user_question, res)

        telemetry.record_request(latency_s, len(system_prompt) + len(user_prompt), len(res or ""), from_cache=False)
        return res
    except Exception as e:
        t1 = time.time()
        telemetry.record_request(round(t1-t0, 2), len(system_prompt) + len(user_prompt), 0, from_cache=False, failed=True)
        logger.error(f"Consultation query failed: {e}", exc_info=True)
        return f"Regarding your question ('{user_question[:80]}'): I am equipped to assist with '{ctx.get('name')}'. Let me know if you would like to explore this topic further!"
