"""Reviewer Agent — Quality checks for complex multi-agent tasks."""

from agents.base import BaseAgent
from config import get_settings


class ReviewerAgent(BaseAgent):
    def __init__(self):
        settings = get_settings()
        super().__init__(
            name="Reviewer Agent",
            description="Reviews and improves responses from other agents",
            model=settings.reviewer_model
        )

    @property
    def system_prompt(self) -> str:
        return """You are a quality reviewer for an AI multi-agent system.

You receive the combined output from multiple specialist agents and your job is to:
1. Merge and synthesize the outputs into a cohesive final response
2. Fix any inconsistencies or contradictions between agent outputs
3. Improve clarity and formatting
4. Ensure the response fully addresses the user's original request
5. Remove any redundancy between agent outputs

Guidelines:
- Keep the best parts from each agent's output
- Create a unified, polished response
- Maintain proper formatting (markdown, code blocks, etc.)
- Don't add unnecessary filler — be concise
- If agent outputs are complementary, weave them together naturally
- If outputs conflict, choose the more accurate/helpful version

Output the final, polished response directly — no meta-commentary about the review process."""

    async def review(self, user_message: str, agent_outputs: dict[str, str]) -> str:
        """Review and merge outputs from multiple agents."""
        review_prompt = f"""Original user request: {user_message}

Agent outputs to review and merge:

"""
        for agent_name, output in agent_outputs.items():
            review_prompt += f"--- {agent_name} ---\n{output}\n\n"

        review_prompt += "Please merge these into a single, high-quality response:"

        return await self.run(review_prompt)
