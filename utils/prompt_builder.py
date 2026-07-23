"""
Prompt Builder Module for AI Software Company.
Assembles code-first prompts for Implementation Studio and Consultation Chat.
"""

from typing import Dict, Any, Optional

STRICT_SYSTEM_PROMPT = """You are a Senior Principal Software Engineer and System Architect.
Your primary task is to write MASSIVE, COMPLETE, EXECUTABLE, PRODUCTION-READY MULTI-FILE SOURCE CODE for the synchronized project along with complete File Structure Architecture and Execution Guidance.

OUTPUT STRUCTURE (STRICTLY FOLLOW THIS ORDER):
1. Executive Overview & 📁 Production File Structure Architecture (complete ASCII folder tree diagram in ```text ... ``` showing exact directory layout and file paths)
2. Complete Production Code (Write out AT LEAST 4 TO 6 FULL SOURCE CODE FILES wrapped in markdown code blocks with clear filename headers e.g. `### main.py`, `### models.py`, `### schemas.py`, `### router.py`, `### database.py`, `### config.py`, `### test_suite.py`). Write FULL imports, FULL class definitions, FULL Pydantic models, FULL REST endpoints, FULL SQL ORM queries, and FULL functions without any placeholders or ellipsis ("...").
3. 🚀 Code Execution & Developer Setup Guide (step-by-step shell commands to install dependencies, configure environment variables, start servers, and execute test suites)
4. ⚙️ Code Execution Breakdown & Architecture Analysis (detailed walkthrough of execution flow, component interactions, data flow, and function roles)
5. 🔒 Important Technical & Security Information (security controls, OWASP protections, rate limiting, error handling, performance considerations, and environment configuration)
6. 💡 Production Best Practices & Future Enhancements

STRICT CONSTRAINTS:
- TARGET OUTPUT LENGTH: Generate AT LEAST 2,500 to 4,000+ words of complete, un-truncated, executable production source code and developer execution guides.
- Write out ALL multiple production code files in FULL detail without truncating lines or using comments like '# Implement remaining logic here'.
- Always use the exact synchronized project name, industry, and tech stack in all code, comments, loggers, class names, directory trees, and execution steps."""

class PromptPayload(dict):
    """Dictionary subclass supporting both dict key access and tuple unpacking (sys_p, user_p)."""
    def __iter__(self):
        yield self["system_prompt"]
        yield self["user_prompt"]
    def __getitem__(self, key):
        if isinstance(key, int):
            return self["system_prompt"] if key == 0 else self["user_prompt"]
        return super().__getitem__(key)

def build_implementation_prompt(*args, **kwargs) -> Dict[str, str]:
    """
    Construct Code-First prompt payload (80% Code, 20% Explanation).
    Supports both parameter order conventions & tuple unpacking.
    """
    ctx = kwargs.get("ctx", {})
    active_mode = kwargs.get("active_mode", {})
    cat_data = kwargs.get("cat_data", {})
    active_module_name = kwargs.get("active_module_name", "Core")
    user_input = kwargs.get("user_input", "")

    # Handle positional args flexibility
    if args:
        for a in args:
            if isinstance(a, dict):
                if "name" in a and "industry" in a:
                    ctx = a
                elif "title" in a or "label" in a or "system_role" in a or "role" in a:
                    active_mode = a
                elif "prompt" in a or "input_label" in a or "modules" in a:
                    cat_data = a
                elif not ctx:
                    ctx = a
                elif not active_mode:
                    active_mode = a
                elif not cat_data:
                    cat_data = a
            elif isinstance(a, str):
                if not active_module_name or active_module_name == "Core":
                    active_module_name = a
                else:
                    user_input = a

    proj_name = ctx.get("name", "Synchronized Project") if isinstance(ctx, dict) else "Synchronized Project"
    proj_ind = ctx.get("industry", "Technology & SaaS") if isinstance(ctx, dict) else "Technology & SaaS"
    proj_tech = ctx.get("tech_preference", "Modern Stack") if isinstance(ctx, dict) else "Modern Stack"
    
    category_name = cat_data.get("name", "Backend") if isinstance(cat_data, dict) else "Backend"
    mode_title = active_mode.get("title", "Senior Engineer") if isinstance(active_mode, dict) else "Senior Engineer"
    mode_label = active_mode.get("label", "Backend") if isinstance(active_mode, dict) else "Backend"

    system_prompt = f"""{STRICT_SYSTEM_PROMPT}

Target Project: {proj_name}
Industry: {proj_ind}
Tech Stack: {proj_tech}
Role: {mode_title} ({mode_label})
Category: {category_name}
Module: {active_module_name}"""

    proj_diff = ctx.get("difficulty", "Intermediate") if isinstance(ctx, dict) else "Intermediate"
    proj_budget = ctx.get("budget", "Medium") if isinstance(ctx, dict) else "Medium"
    proj_timeline = ctx.get("timeline", "3 months") if isinstance(ctx, dict) else "3 months"

    cat_lower = str(category_name).lower()
    spec_context = ""
    if isinstance(ctx, dict):
        if "backend" in cat_lower or "ai" in cat_lower or "architect" in cat_lower:
            if ctx.get("backend_summary"): spec_context += f"\nBackend Spec: {ctx['backend_summary'][:2500]}"
            if ctx.get("db_summary"): spec_context += f"\nDatabase Spec: {ctx['db_summary'][:2500]}"
        elif "frontend" in cat_lower or "ui" in cat_lower:
            if ctx.get("fe_summary"): spec_context += f"\nFrontend Spec: {ctx['fe_summary'][:2500]}"
        elif "database" in cat_lower:
            if ctx.get("db_summary"): spec_context += f"\nDatabase Spec: {ctx['db_summary'][:2500]}"

    user_prompt = f"""PRIORITY 1: SYNCHRONIZED PROJECT BLUEPRINT & TIER CONSTRAINTS
- Project Name: {proj_name}
- Industry: {proj_ind}
- Tech Stack: {proj_tech}
- Complexity Level: {proj_diff}
- Budget Level: {proj_budget}
- Delivery Schedule: {proj_timeline}

PRIORITY 2: FUNCTIONAL SCOPE & CATEGORY
- Category: {category_name}
- Target Module: {active_module_name}
- Role Persona: {mode_title} ({mode_label})
{spec_context}

USER CUSTOM INSTRUCTION:
{user_input if user_input.strip() else "Generate complete production implementation."}

COMPLEXITY LEVEL ADAPTATION MANDATE:
- If Complexity is 'Beginner': Write clean, well-commented, educational code with clear step-by-step setup steps suitable for early-stage developers.
- If Complexity is 'Enterprise Scale': Write robust enterprise code with strict Pydantic/TypeScript types, error handling, security middleware, and production-grade architecture.

REQUIRED OUTPUT STRUCTURE CONTRACT:
1. Executive Overview & 📁 Production File Structure Architecture (complete ASCII folder tree diagram in ```text ... ``` showing exact directory layout)
2. Complete Production Code (wrapped in ```python, ```typescript, ```sql, etc. with filename headers `### filename.ext`)
3. 🚀 Code Execution & Developer Setup Guide (commands to install, configure, run, and test)
4. ⚙️ Code Execution Breakdown & Architecture Walkthrough (detailed execution flow and data pipeline)
5. 🔒 Important Technical & Security Information (security controls, environment variables, error handling, performance)
6. 💡 Production Best Practices & Future Enhancements"""

    return PromptPayload({
        "system_prompt": system_prompt,
        "user_prompt": user_prompt
    })

def build_consultation_prompt(arg1: Any, arg2: Any) -> Dict[str, str]:
    """Build Consultation Chat prompt."""
    if isinstance(arg1, dict):
        proj_name = arg1.get("name", "Synchronized Project")
        user_query = str(arg2)
    else:
        user_query = str(arg1)
        proj_name = str(arg2) if arg2 else "Synchronized Project"

    system_prompt = f"You are a Principal Software Consultant advising on '{proj_name}'."
    return PromptPayload({"system_prompt": system_prompt, "user_prompt": user_query})
