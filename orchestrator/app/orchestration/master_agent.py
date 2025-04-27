# app/orchestration/master_agent.py

import logging
from typing import Tuple

from app.orchestration.dispatcher import AGENT_REGISTRY

logger = logging.getLogger(__name__)

class MasterAgent:
    def __init__(self):
        # you could load an LLM here for classification later
        pass

    def classify_intent(self, text: str) -> str:
        """
        Decide which agent should handle this text.
        Returns the agent key (must exist in AGENT_REGISTRY), 
        or 'help' for fallback.
        """
        lower = text.lower()
        # example keyword rules
        if any(k in lower for k in ["sovereignty", "case", "statute", "law", "precedent"]):
            return "case_law_scholar"
        if "memo" in lower or "draft" in lower:
            return "memo_drafter"
        if any(k in lower for k in ["remind", "schedule", "date", "time"]):
            return "n8n_scheduler"
        return "help"

    def parse(self, text: str) -> Tuple[str, str]:
        """
        Returns (agent_key, query).
        For now, query is the full text minus any command words.
        """
        agent_key = self.classify_intent(text)
        return agent_key, text

    async def run(self, update: dict) -> str:
        """
        Top-level entrypoint: given the Telegram update, route to the
        correct agent and return its response text.
        """
        msg = update.get("message", {})
        text = msg.get("text", "")
        chat = msg.get("chat", {}).get("id")

        agent_key, query = self.parse(text)
        agent = AGENT_REGISTRY.get(agent_key)
        if not agent:
            return "Sorry, I don't know how to help with that yet. Try rephrasing."

        logger.info(f"MasterAgent routing to '{agent_key}' for query: {query!r}")
        # assume each agent.run can be async or sync
        result = agent.run(query)
        if callable(getattr(result, "__await__", None)):
            # it's a coroutine
            result = await result
        return result
