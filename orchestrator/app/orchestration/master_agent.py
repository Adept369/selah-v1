# orchestrator/app/orchestration/master_agent.py

import logging
from typing import Tuple

from app.orchestration.registry import build_registry

logger = logging.getLogger(__name__)

class MasterAgent:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.registry = build_registry(llm_client)

    def classify_intent(self, text: str) -> str:
        lower = text.lower()
        if any(k in lower for k in ["sovereignty", "case", "statute", "law", "precedent"]):
            return "case_law_scholar"
        if "memo" in lower or "draft" in lower:
            return "memo_drafter"
        if any(k in lower for k in ["remind", "schedule", "date", "time"]):
            return "n8n_scheduler"
        return "help"

    def parse(self, text: str) -> Tuple[str, str]:
        agent_key = self.classify_intent(text)
        return agent_key, text

    async def run(self, update: dict) -> str:
        msg = update.get("message", {})
        text = msg.get("text", "")
        if not text:
            return "Please send a text message."

        agent_key, query = self.parse(text)
        agent = self.registry.get(agent_key)
        if not agent:
            return "Sorry, I don't know how to help with that yet."

        logger.info(f"MasterAgent routing to '{agent_key}' for: {query!r}")
        result = agent.run(query)
        if hasattr(result, "__await__"):
            result = await result
        return result
