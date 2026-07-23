"""
System Prompt & Context Assembler for DevCore AI Assistant.
Provides full knowledge of project architecture, codebase, database, and RAG index.
Dynamically adapts between Direct & Concise, Detailed Reasoning, and Casual modes based on user input.
"""

from typing import Optional, Dict, Any, List
import streamlit as st

CASUAL_SYSTEM_PROMPT = """You are DevCore AI Assistant — an enthusiastic, warm, supportive human-like senior engineering partner.

CRITICAL RESPONSE STYLE:
- Reply to greetings (e.g. "hi", "hello", "hey") warmly, encouragingly, and cheerfully with positive emojis (e.g. 👋, 🚀, ✨, 🤝, 💡).
- Keep casual greetings friendly and under 25 words."""

DIRECT_SYSTEM_PROMPT = """You are DevCore AI Assistant — an enthusiastic, encouraging, highly intelligent senior technical co-founder and engineering partner.

CRITICAL INSTRUCTION: WARM, ENCOURAGING & HUMAN-LIKE RESPONSES
- Answer ANY question, topic, or request directly, clearly, and helpfully with warm human encouragement and relevant emojis (e.g. 🚀, 💡, 🟢, 🎯, 🛠️, ✨, 🤝, 🙌, 📊, 🔒).
- If the user asks about the active project, utilize the reference context below. Celebrate completed milestones and encourage the user!
- If the user asks out-of-the-box or general technical questions, answer directly with full domain expertise."""

REASONING_SYSTEM_PROMPT = """You are DevCore AI Assistant — an expert Lead Architect, Systems Engineer, and Universal Knowledge Partner.

CRITICAL INSTRUCTION: WARM, ENCOURAGING REASONING & COMPREHENSIVE ANSWERS
- Analyze and answer ANY topic or request (project architectural choices, general technical questions, out-of-the-box concepts, math, logic, science, or general knowledge).
- Provide thorough, well-reasoned explanations with encouraging human tone and supportive emojis (🚀, 💡, 🟢, 🎯, 🛠️, ✨, 🤝, 🙌)."""

def build_system_context(user_prompt: str = "", active_project_id: Optional[str] = None) -> str:
    """
    Build context-enriched system prompt. Dynamically selects between Direct, Reasoning, and Casual modes based on user input intent.
    """
    clean_p = user_prompt.strip().lower()
    prompt_words = set(clean_p.split())

    # 1. Pure greetings receive casual short prompt
    pure_greetings = {"hi", "hello", "hey", "hii", "hiii", "howdy", "greetings", "good morning", "good evening", "how are you", "who are you", "thanks", "thank you"}
    if clean_p in pure_greetings or (len(prompt_words) <= 2 and any(w in pure_greetings for w in prompt_words)):
        return CASUAL_SYSTEM_PROMPT

    # 2. Keywords/phrases that explicitly request deep reasoning / architectural breakdown
    reasoning_triggers = {
        "explain in detail", "why", "deep dive", "analyze", "architecture", "architectural",
        "step by step", "breakdown", "blueprint", "compare", "tradeoffs", "design system",
        "workflow engine", "how does it work", "pros and cons", "detailed", "rationale",
        "summarize the architecture", "explain the architecture", "explain the workflow",
        "how does rag work", "explain the database schema"
    }

    is_reasoning_requested = any(trigger in clean_p for trigger in reasoning_triggers)

    # 3. Select prompt mode: Detailed reasoning if explicitly asked, otherwise Direct & Concise
    if is_reasoning_requested:
        context = REASONING_SYSTEM_PROMPT
    else:
        context = DIRECT_SYSTEM_PROMPT

    # 4. Attach active project context & agent blueprint details if available
    if active_project_id:
        try:
            from database.connection import execute_query
            proj = execute_query("SELECT * FROM projects WHERE id = ?", (active_project_id,))
            if proj:
                p = proj[0]
                context += f"\n\n### Active Project Workspace Context:\n"
                context += f"- **Project Name**: {p.get('name', 'N/A')}\n"
                context += f"- **Description**: {p.get('description', 'N/A')}\n"
                context += f"- **Industry Vertical**: {p.get('industry', 'N/A')}\n"
                context += f"- **Tech Preference**: {p.get('tech_preference', 'N/A')}\n"
                context += f"- **Complexity / Budget**: {p.get('difficulty', 'N/A')} | {p.get('budget', 'N/A')}\n"

                # Attach generated agent blueprint summaries
                agent_runs = execute_query("SELECT agent_role FROM agent_runs WHERE project_id = ?", (active_project_id,))
                if agent_runs:
                    roles = [r['agent_role'] for r in agent_runs]
                    context += f"- **Generated Agent Blueprints ({len(roles)}/13)**: {', '.join(roles)}\n"
        except Exception:
            pass

    return context

