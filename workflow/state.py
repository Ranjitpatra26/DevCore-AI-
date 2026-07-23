from typing import TypedDict, Dict, Any, List

class ProjectState(TypedDict):
    """The shared state dictionary maintained by the multi-agent graph pipeline."""
    project_id: str
    project_name: str
    description: str
    industry: str
    tech_preference: str
    budget: str
    timeline: str
    difficulty: str
    agent_outputs: Dict[str, str]
    current_agent: str
    logs: List[str]
    status: str
