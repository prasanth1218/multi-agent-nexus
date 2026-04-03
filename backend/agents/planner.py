"""Planner Agent — Fast task classification and agent routing."""

import json
from services.llm import chat_completion
from config import get_settings


PLANNER_SYSTEM_PROMPT = """You are a fast task planner for an AI multi-agent system.  
Your ONLY job is to analyze the user's request and decide which specialist agent(s) should handle it.

Available agents:
- "coder": For code generation, debugging, programming questions, technical implementation
- "writer": For content creation, essays, summaries, creative writing, explanations
- "researcher": For factual questions, analysis, comparisons, data-driven answers

Rules:
1. Choose the MINIMUM number of agents needed (usually just 1)
2. Only use multiple agents if the task clearly requires different skills
3. Set needs_review=true ONLY for complex multi-step tasks
4. Be fast — this is a routing decision, not a deep analysis

Respond in STRICT JSON format only:
{"agents": ["agent_name"], "needs_review": false, "plan": "brief one-line plan"}

Examples:
- "Write a Python function" → {"agents": ["coder"], "needs_review": false, "plan": "Generate Python function"}
- "Write a blog post about AI" → {"agents": ["writer"], "needs_review": false, "plan": "Create blog post about AI"}
- "Build a landing page with compelling copy" → {"agents": ["coder", "writer"], "needs_review": true, "plan": "Generate HTML/CSS and write marketing copy"}
- "What is quantum computing?" → {"agents": ["researcher"], "needs_review": false, "plan": "Explain quantum computing"}
"""


async def plan_task(user_message: str) -> dict:
    """Classify the task and select agents. Uses fast model for low latency."""
    settings = get_settings()

    messages = [
        {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    try:
        response = await chat_completion(
            messages,
            model=settings.planner_model,
            temperature=0.1,  # Low temperature for consistent routing
            max_tokens=150,   # Short response = fast
        )

        # Parse the JSON response
        # Handle potential markdown code blocks in response
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
            cleaned = cleaned.rsplit("```", 1)[0] if "```" in cleaned else cleaned
            cleaned = cleaned.strip()

        result = json.loads(cleaned)

        # Validate and sanitize
        valid_agents = {"coder", "writer", "researcher"}
        result["agents"] = [a for a in result.get("agents", []) if a in valid_agents]
        if not result["agents"]:
            result["agents"] = ["researcher"]  # Default fallback
        result["needs_review"] = result.get("needs_review", False)
        result["plan"] = result.get("plan", "Processing your request")

        return result

    except (json.JSONDecodeError, KeyError, Exception):
        # Fallback: if planner fails, use researcher agent
        return {
            "agents": ["researcher"],
            "needs_review": False,
            "plan": "Processing your request"
        }
