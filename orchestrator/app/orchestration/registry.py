# orchestrator/app/orchestration/registry.py

from app.agents.case_law_scholar.case_law_agent import CaseLawScholarAgent
from app.agents.memo_drafter.memo_agent import MemoDrafterAgent


def build_registry(llm_client):
    """
    Constructs the agent registry, injecting the shared LLM client.

    Returns:
        dict: Mapping of agent_key -> agent_instance
    """
    return {
        # Routes research/legal queries
        "case_law_scholar": CaseLawScholarAgent(llm_client),
        # Drafts memos
        "memo_drafter": MemoDrafterAgent(llm_client),
        # Placeholder for n8n-based workflows
        # "n8n_scheduler": N8nSchedulerAgent(llm_client),   # your n8n‐based workflows
        # Fallback/help handler
        #  "help":             HelpAgent(),              # “I don’t know” fallback
        #),
    }
