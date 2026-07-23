import time
import logging
from typing import Dict, Any, List, Callable, Optional
from langgraph.graph import StateGraph, END
from workflow.state import ProjectState
from agents.base import run_agent, get_role_display_name
from database.connection import execute_update

logger = logging.getLogger("ai_software_company")

# Helper to create graph nodes
def create_agent_node(role: str) -> Callable[[ProjectState], ProjectState]:
    """Generates a node executor for a specific agent role."""
    def agent_node(state: ProjectState) -> ProjectState:
        project_id = state["project_id"]
        # Inform logs
        logger.info(f"Starting execution node for: {role}")
        
        # Run agent logic and retrieve markdown blueprint
        output = run_agent(project_id, role, state)
        
        # Update shared state
        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}
        state["agent_outputs"][role] = output
        state["current_agent"] = role
        
        step_log = f"Agent {get_role_display_name(role)} generated blueprint successfully."
        if "logs" not in state or state["logs"] is None:
            state["logs"] = []
        state["logs"].append(step_log)
        
        # Log to project database as a system log
        execute_update(
            "INSERT INTO chats (project_id, agent_role, sender, message) VALUES (?, ?, ?, ?)",
            (project_id, role, "system", step_log)
        )
        return state
    return agent_node

def build_workflow_graph() -> StateGraph:
    """Wires up the 13 collaborating agents in the StateGraph sequence."""
    workflow = StateGraph(ProjectState)
    
    # 1. Define nodes
    roles = [
        "ceo", "business_analyst", "project_manager", "architect", "ui_ux",
        "frontend", "backend", "database", "security", "devops", "qa",
        "documentation", "reviewer"
    ]
    
    for role in roles:
        workflow.add_node(role, create_agent_node(role))
        
    # 2. Define edges
    workflow.set_entry_point("ceo")
    
    # Build linear dependency chain
    for i in range(len(roles) - 1):
        workflow.add_edge(roles[i], roles[i+1])
        
    workflow.add_edge("reviewer", END)
    
    return workflow.compile()

# Compile the graph
compiled_graph = build_workflow_graph()

import concurrent.futures
import threading

try:
    from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
except Exception:
    add_script_run_ctx = None
    get_script_run_ctx = None

def run_project_planning(
    project_id: str,
    project_name: str,
    description: str,
    industry: str,
    tech_preference: str,
    budget: str,
    timeline: str,
    difficulty: str,
    progress_callback: Optional[Callable[[str, int, str], None]] = None
) -> Dict[str, Any]:
    """Execute the 13-agent workflow graph in parallel multi-stage phases for high-velocity synthesis."""
    try:
        from utils.ollama_client import reset_ollama_status
        reset_ollama_status()
    except Exception:
        pass
    
    initial_state: ProjectState = {
        "project_id": project_id,
        "project_name": project_name,
        "description": description,
        "industry": industry,
        "tech_preference": tech_preference,
        "budget": budget,
        "timeline": timeline,
        "difficulty": difficulty,
        "agent_outputs": {},
        "current_agent": "idle",
        "logs": ["Planning initialized."],
        "status": "running"
    }
    
    # Capture main Streamlit execution context for thread workers
    script_ctx = get_script_run_ctx() if get_script_run_ctx else None
    
    # 4 Parallel Execution Stages for maximum speed & logical dependency flow
    stages = [
        ["ceo", "business_analyst", "project_manager"],
        ["architect", "ui_ux", "database", "security"],
        ["frontend", "backend", "devops", "qa"],
        ["documentation", "reviewer"]
    ]
    
    all_roles = [r for stage in stages for r in stage]
    total_roles = len(all_roles)
    completed_count = 0
    state_lock = threading.Lock()
    
    state = initial_state
    
    for stage_idx, stage_roles in enumerate(stages):
        def run_single_role(role: str):
            nonlocal completed_count, state
            if script_ctx and add_script_run_ctx:
                try:
                    add_script_run_ctx(threading.current_thread(), script_ctx)
                except Exception:
                    pass

            if progress_callback:
                try:
                    progress_callback(role, int((completed_count / total_roles) * 100), f"Synthesizing {get_role_display_name(role)} spec...")
                except Exception:
                    pass
                
            node_func = create_agent_node(role)
            with state_lock:
                current_state_snapshot = dict(state)
                
            try:
                updated_state = node_func(current_state_snapshot)
            except Exception as e:
                logger.error(f"Error executing agent node '{role}': {e}")
                updated_state = {}
            
            with state_lock:
                if "agent_outputs" not in state or state["agent_outputs"] is None:
                    state["agent_outputs"] = {}
                if isinstance(updated_state, dict) and "agent_outputs" in updated_state and updated_state["agent_outputs"]:
                    state["agent_outputs"].update(updated_state["agent_outputs"])
                if isinstance(updated_state, dict) and "logs" in updated_state and updated_state["logs"]:
                    for log in updated_state["logs"]:
                        if log not in state["logs"]:
                            state["logs"].append(log)
                completed_count += 1
                
            if progress_callback:
                try:
                    progress_callback(role, int((completed_count / total_roles) * 100), f"Completed {get_role_display_name(role)} section.")
                except Exception:
                    pass

        # Run stage roles concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(stage_roles)) as executor:
            futures = [executor.submit(run_single_role, role) for role in stage_roles]
            concurrent.futures.wait(futures)
            
    # Set status to completed and update DB
    execute_update("UPDATE projects SET model_used = ? WHERE id = ?", ("qwen3.5:9b", project_id))
    
    return state
