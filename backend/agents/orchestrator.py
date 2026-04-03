"""Orchestrator — Coordinates agents with parallel execution and streaming."""

import asyncio
import json
from typing import AsyncGenerator
from agents.planner import plan_task
from agents.coder import CodingAgent
from agents.writer import WriterAgent
from agents.researcher import ResearchAgent
from agents.reviewer import ReviewerAgent
from services.cache import cache


# Pre-initialize agents (singleton pattern for connection reuse)
AGENTS = {
    "coder": CodingAgent(),
    "writer": WriterAgent(),
    "researcher": ResearchAgent(),
}
reviewer = ReviewerAgent()


async def process_message(
    user_message: str,
    context: list[dict] | None = None,
    use_cache: bool = True
) -> AsyncGenerator[str, None]:
    """
    Main orchestration pipeline:
    1. Check cache
    2. Plan (fast routing)
    3. Execute agents (parallel if multiple)
    4. Optional review
    5. Stream results

    Yields SSE-formatted events.
    """

    # --- Step 0: Check cache ---
    if use_cache:
        context_str = json.dumps(context[-5:]) if context else ""
        cached = cache.get(user_message, context_str)
        if cached:
            yield _sse_event("agent_status", {
                "agents": ["cache"],
                "status": "complete",
                "plan": "Retrieved from cache"
            })
            yield _sse_event("token", {"content": cached, "agent": "cache"})
            yield _sse_event("done", {"cached": True})
            return

    # --- Step 1: Plan (fast, <500ms) ---
    yield _sse_event("agent_status", {
        "agents": ["planner"],
        "status": "planning",
        "plan": "Analyzing your request..."
    })

    plan = await plan_task(user_message)
    selected_agents = plan["agents"]
    needs_review = plan["needs_review"]

    yield _sse_event("agent_status", {
        "agents": selected_agents,
        "status": "executing",
        "plan": plan["plan"],
        "needs_review": needs_review
    })

    # --- Step 2: Execute agents ---
    if len(selected_agents) == 1:
        # Single agent: stream directly for lowest latency
        agent = AGENTS[selected_agents[0]]
        full_response = ""

        async for token in agent.run_stream(user_message, context):
            full_response += token
            yield _sse_event("token", {
                "content": token,
                "agent": selected_agents[0]
            })

        # Cache the result
        if use_cache:
            context_str = json.dumps(context[-5:]) if context else ""
            cache.set(user_message, full_response, context_str)

        yield _sse_event("done", {"agents_used": selected_agents})

    else:
        # Multiple agents: run in parallel, then merge
        yield _sse_event("agent_status", {
            "agents": selected_agents,
            "status": "parallel_execution",
            "plan": f"Running {len(selected_agents)} agents in parallel..."
        })

        # Execute all agents concurrently
        tasks = {}
        for agent_name in selected_agents:
            if agent_name in AGENTS:
                tasks[agent_name] = AGENTS[agent_name].run(user_message, context)

        results = {}
        completed = await asyncio.gather(
            *[tasks[name] for name in tasks],
            return_exceptions=True
        )

        for name, result in zip(tasks.keys(), completed):
            if isinstance(result, Exception):
                results[name] = f"[Agent error: {str(result)}]"
            else:
                results[name] = result

        # --- Step 3: Optional review ---
        if needs_review and len(results) > 1:
            yield _sse_event("agent_status", {
                "agents": ["reviewer"],
                "status": "reviewing",
                "plan": "Reviewing and merging results..."
            })

            final_response = ""
            # Stream the reviewer's merged output
            review_prompt = f"Original request: {user_message}\n\nAgent outputs:\n"
            for name, output in results.items():
                review_prompt += f"\n--- {name} ---\n{output}\n"
            review_prompt += "\nMerge these into a single polished response:"

            async for token in reviewer.run_stream(review_prompt):
                final_response += token
                yield _sse_event("token", {
                    "content": token,
                    "agent": "reviewer"
                })
        else:
            # No review needed: concatenate with section headers
            final_response = ""
            for name, output in results.items():
                agent_display = AGENTS[name].name if name in AGENTS else name
                section = f"\n\n## {agent_display}\n\n{output}"
                final_response += section

            # Stream the concatenated result
            # Send in chunks for a natural streaming feel
            chunk_size = 5
            for i in range(0, len(final_response), chunk_size):
                chunk = final_response[i:i + chunk_size]
                yield _sse_event("token", {
                    "content": chunk,
                    "agent": "multi"
                })
                await asyncio.sleep(0.01)  # Small delay for streaming effect

        # Cache
        if use_cache:
            context_str = json.dumps(context[-5:]) if context else ""
            cache.set(user_message, final_response, context_str)

        yield _sse_event("done", {"agents_used": selected_agents, "reviewed": needs_review})


def _sse_event(event_type: str, data: dict) -> str:
    """Format a Server-Sent Event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
